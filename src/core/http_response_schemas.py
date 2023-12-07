from pydantic import BaseModel


class BaseErrorModel(BaseModel):
    detail: str


class UniqueConstraint(BaseErrorModel):
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Ошибка при проверке на уникальность",
            },
        }


class Unauthorized(BaseErrorModel):
    class Config:
        json_schema_extra = {"example": {"detail": "Не авторизован"}}


class NotFound(BaseErrorModel):
    class Config:
        json_schema_extra = {"example": {"detail": "Объект не найден"}}


class NotAllowed(BaseErrorModel):
    class Config:
        json_schema_extra = {"example": {"detail": "У вас недостаточно прав"}}
