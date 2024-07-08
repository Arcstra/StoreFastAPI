from pydantic import BaseModel, EmailStr
from typing import Optional


class User(BaseModel):
    name: Optional[str]
    password: str
    email: EmailStr


class LoginForm(BaseModel):
    password: str
    email: EmailStr


class Product(BaseModel):
    title: str
    price: int
    description: Optional[str] = ""
    article: str
    purchase: int # 0 - ничего, 1 - купля, 2 - продажа


class GetProductForm(BaseModel):
    article: Optional[str]
    user_id: Optional[int]
