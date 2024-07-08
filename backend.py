import sys, bcrypt, uuid, redis
from psycopg2 import pool, Error, _psycopg
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from models import User, LoginForm, Product, GetProductForm

app = FastAPI()

r_token = redis.Redis(
    host="redis",
    port=6379,
    db=0,
    decode_responses=True,
)
r_token.flushdb()

try:
    connection_pool = pool.SimpleConnectionPool(1, 2,
                                                database="postgres",
                                                user="postgres",
                                                password="postgres",
                                                host="postgres",
                                                port="5432",
                                                )
except Error as e:
    print("Не удалось подключиться к БД(")
    sys.exit()
else:
    print("Успешное подключение к БД!")


async def check_login(token) -> int | None:
    if token is None:
        return None
    
    user_id = r_token.get(token)
    if user_id is None:
        return None
    
    return user_id


@app.get("/")
async def home():
    return {"Hello": "world!"}


@app.post("/register")
async def register(user: User):
    connection: _psycopg.connection = connection_pool.getconn()
    cursor = connection.cursor()

    try:
        cursor.execute(f"select * from users where email='{user.email}'")
    except Error as e:
        cursor.close()
        connection_pool.putconn(connection)
        return JSONResponse({}, status_code=500)
    
    if len(cursor.fetchall()) > 0:
        cursor.close()
        connection_pool.putconn(connection)
        return JSONResponse({}, status_code=403) # Неуникальная почта

    try:
        cursor.execute(f"""insert into users (name, password, email, is_confirm_email)
                       values ('{user.name}', '{bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()}', '{user.email}', false);""")
        connection.commit()
    except Error as e:
        return JSONResponse({}, status_code=500)
    else:
        return JSONResponse({}, status_code=201)
    finally:
        cursor.close()
        connection_pool.putconn(connection)



@app.post("/login")
async def login(user: LoginForm):
    connection: _psycopg.connection = connection_pool.getconn()
    cursor = connection.cursor()

    try:
        cursor.execute(f"select id, password from users where email='{user.email}';")
        res = cursor.fetchall()
    except Error as e:
        return JSONResponse({}, status_code=500)
    finally:
        cursor.close()
        connection_pool.putconn(connection)

    if len(res) == 0:
        return JSONResponse({}, status_code=404) # Не найден в БД
    
    hashed_password = res[0][1]
    
    if not bcrypt.checkpw(user.password.encode(), hashed_password.encode()):
        return JSONResponse({}, status_code=400) # Неверный пароль
    
    if not r_token.get(user.email) is None:
        return JSONResponse({}, status_code=403) # Уже залогинин
    
    token = str(uuid.uuid4())
    r_token.set(token, res[0][0]) # сохранение id пользователя
    
    return JSONResponse({}, 
        status_code=202,
        headers={"x-token": token},
    )


@app.post("/purchase")
async def purchase(request: Request, product: Product):
    user_id = await check_login(request.headers.get("x-token"))
    if user_id is None:
        return JSONResponse({}, status_code=401)
    
    connection: _psycopg.connection = connection_pool.getconn()
    cursor = connection.cursor()

    try:
        cursor.execute(f"""insert into products (title, price, description, article, purchase, user_id)
                       values ('{product.title}', {product.price}, '{product.description}', '{product.article}', {product.purchase}, {user_id})""")
        connection.commit()
    except Exception as e:
        return JSONResponse({}, status_code=500)
    else:
        return JSONResponse({}, status_code=201)
    finally:
        cursor.close()
        connection_pool.putconn(connection)


@app.get("/allpurchase")
async def get_all_purchase(request: Request):
    user_id = await check_login(request.headers.get("x-token"))
    if user_id is None:
        return JSONResponse({}, status_code=401)
    
    connection: _psycopg.connection = connection_pool.getconn()
    cursor = connection.cursor()

    try:
        cursor.execute(f"select title, price, description, article, purchase, user_id from products;")
    except Exception as e:
        return JSONResponse({}, status_code=500)
    else:
        res_all = cursor.fetchall()
        data = []

        for res in res_all:
            data.append({
                "title": res[0],
                "price": res[1],
                "description": res[2],
                "article": res[3],
                "purchase": res[4],
                "user_id": res[5],
            })

        return JSONResponse(content=data,
                        status_code=200)
    finally:
        cursor.close()
        connection_pool.putconn(connection)


@app.get("/articlepurchase")
async def get_purchase(request: Request, article: str):
    user_id = await check_login(request.headers.get("x-token"))
    if user_id is None:
        return JSONResponse({}, status_code=401)
    
    connection: _psycopg.connection = connection_pool.getconn()
    cursor = connection.cursor()

    try:
        cursor.execute(f"select title, price, description, article, purchase, user_id from products where article = '{article}';")
    except Exception as e:
        return JSONResponse({}, status_code=500)
    else:
        res = cursor.fetchone()
        data = {
            "title": res[0],
            "price": res[1],
            "description": res[2],
            "article": res[3],
            "purchase": res[4],
            "user_id": res[5],
        }

        return JSONResponse(content=data,
                        status_code=200)
    finally:
        cursor.close()
        connection_pool.putconn(connection)


@app.get("/mypurchase")
async def get_purchase(request: Request):
    user_id = await check_login(request.headers.get("x-token"))
    if user_id is None:
        return JSONResponse({}, status_code=401)
    
    connection: _psycopg.connection = connection_pool.getconn()
    cursor = connection.cursor()

    try:
        cursor.execute(f"select title, price, description, article, purchase, user_id from products where user_id = '{user_id}';")
    except Exception as e:
        return JSONResponse({}, status_code=500)
    else:
        res_all = cursor.fetchall()
        data = []

        for res in res_all:
            data.append({
                "title": res[0],
                "price": res[1],
                "description": res[2],
                "article": res[3],
                "purchase": res[4],
                "user_id": res[5],
            })

        return JSONResponse(content=data,
                        status_code=200)
    finally:
        cursor.close()
        connection_pool.putconn(connection)
