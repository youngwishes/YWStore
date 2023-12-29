from fastapi.exceptions import HTTPException


class UniqueConstraintError(HTTPException):
    """Ограничение на уникальность объектов"""


class NotFoundError(HTTPException):
    """Страница/объект не найден-а"""


class IsOwnerError(HTTPException):
    """Нет доступа к объекту."""
