from pydantic import BaseModel


class BaseRole(BaseModel):
    name: str

    class ConfigDict:
        from_attributes = True


class RoleIn(BaseRole):
    ...


class RoleOut(BaseRole):
    id: int
