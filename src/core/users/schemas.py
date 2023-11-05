from pydantic import BaseModel, Field
from datetime import datetime


class UserBase(BaseModel):
    first_name: str = Field(..., max_length=128, title="Имя")
    last_name: str = Field(..., max_length=128, title="Фамилия")
    username: str = Field(..., max_length=128, min_length=4, title="Имя пользователя")
    email: str = Field(..., max_length=320, title="Электронная почта")
    phone_number: str = Field(..., max_length=16, title="Номер телефона")
    password: str = Field(..., max_length=128, title="Пароль")


class UserIn(UserBase):
    pass


class UserOut(UserBase):
    id: int
    joined_date: datetime

    class ConfigDict:
        from_attributes = True
