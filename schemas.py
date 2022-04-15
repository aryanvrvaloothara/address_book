from typing import Optional

from pydantic import BaseModel


class Address(BaseModel):
    name: str = None
    house_name: str = None
    place: str = None
    post_office: str = None
    pin_code: str = None
    latitude: str = None
    longitude: str = None

    class Config:
        orm_mode = True


class User(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        orm_mode = True


class ReadUser(User):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str]


class UserLogin(BaseModel):
    email: str
    password: str
