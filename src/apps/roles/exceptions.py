from fastapi.exceptions import HTTPException


class AdminRequiredError(HTTPException):
    """Необходимо обладать правами администратора компании."""


class RoleNotExists(HTTPException):
    """Пользователь не относится к указанной роли."""
