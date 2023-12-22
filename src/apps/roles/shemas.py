from pydantic import BaseModel


class BaseRole(BaseModel):
    name: str


class RoleIn(BaseRole):
    ...


class RoleOut(BaseRole):
    id: int
