import psycopg2


try:
    connection = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="postgres",
        host="postgres",
        port="5432",
    )
    cursor = connection.cursor()
except psycopg2.Error as e:
    print(f"Не удалось подключиться к БД. Ошибка: {e}")
else:
    print("Подключение установлено!")


try:
    cursor.execute("""create table users (
                   id serial primary key,
                   name varchar(255) not null,
                   password varchar(255) not null,
                   email varchar(255) not null unique,
                   is_confirm_email boolean default false
                   );""")
    connection.commit()
except psycopg2.Error as e:
    print(f"Не удалось создать таблицу users. Ошибка: {e}")
else:
    print("Таблица users успешно создана!")


try:
    cursor.execute("""create table products (
                   id serial primary key,
                   title varchar(255) not null,
                   price integer not null,
                   description varchar(10000),
                   article varchar(255) not null unique,
                   purchase smallint not null check(purchase >= 0 and purchase <= 2),
                   user_id integer not null
                   );""")
    connection.commit()
except psycopg2.Error as e:
    print(f"Не удалось создать таблицу products. Ошибка: {e}")
else:
    print("Таблица products успешно создана!")
finally:
    cursor.close()
    connection.close()
