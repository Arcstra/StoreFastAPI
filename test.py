import requests as rq


TOKEN = "123456"

name = "Ilya"
password = "12345678"
email = "Ilya@mail.ru"


def test_register_201():
    data = {
        "name": name,
        "password": password,
        "email": email,
    }

    try:
        res = rq.post("http://localhost:8000/register", json=data)
    except Exception as e:
        print(f"Error: {e}")
        assert 1 == 0

    assert res.status_code == 201


def test_register_403():
    data = {
        "name": name,
        "password": password,
        "email": email,
    }

    try:
        res = rq.post("http://localhost:8000/register", json=data)
    except Exception as e:
        print(f"Error: {e}")
        assert 1 == 0

    assert res.status_code == 403


def test_login_202():
    data = {
        "password": password,
        "email": email,
    }

    try:
        res = rq.post("http://localhost:8000/login", json=data)
    except Exception as e:
        print(f"Error: {e}")
        assert 1 == 0

    global TOKEN
    TOKEN = res.headers["x-token"]
    assert res.status_code == 202


title = "car"
price = 4_000_000
article = "CAR01"
purchase = 2


def test_to_sell_201():
    data = {
        "title": title,
        "price": price,
        "article": article,
        "purchase": purchase,
    }
    headers = {
        "x-token": TOKEN,
    }

    try:
        res = rq.post("http://localhost:8000/purchase", json=data, headers=headers)
    except Exception as e:
        print(f"Error: {e}")
        assert 1 == 0

    assert res.status_code == 201


def test_all_purchase_200():
    headers = {
        "x-token": TOKEN,
    }

    try:
        res = rq.get("http://localhost:8000/allpurchase", headers=headers)
    except Exception as e:
        print(f"Error: {e}")
        assert 1 == 0

    assert res.status_code == 200


def test_article_purchase_200():
    params = {
        "article": article,
    }
    headers = {
        "x-token": TOKEN,
    }

    try:
        res = rq.get("http://localhost:8000/articlepurchase", params=params, headers=headers)
    except Exception as e:
        print(f"Error: {e}")
        assert 1 == 0

    assert res.status_code == 200


def test_my_purchase_200():
    headers = {
        "x-token": TOKEN,
    }

    try:
        res = rq.get("http://localhost:8000/mypurchase", headers=headers)
    except Exception as e:
        print(f"Error: {e}")
        assert 1 == 0

    assert res.status_code == 200
