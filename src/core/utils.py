from __future__ import annotations
from typing import Optional, Any
from copy import deepcopy
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo
from src.apps.users.models import User
from src.core.config import get_settings

settings = get_settings()


def make_field_partial(field: FieldInfo, default: Any = None) -> (Any, FieldInfo):
    new = deepcopy(field)
    new.default = default
    new.annotation = Optional[field.annotation]
    return new.annotation, new


def optional(cls: type[BaseModel]) -> type[BaseModel]:
    """
    !! Сделает схему опциональной, например если нужно реализовать PATCH-запрос
    >>> class RequiredSchema:
    >>>       required_field: str

    >>> @optional
    >>> class OptionalSchema(RequiredSchema):
            ...
    """
    fields_in_partial_mode = {
        field: make_field_partial(info) for field, info in cls.model_fields.items()
    }
    return create_model(
        cls.__name__,
        __base__=cls,
        __module__=cls.__module__,
        **fields_in_partial_mode,
    )


async def is_member(user: User, role: str) -> bool:
    return role in user.roles_set
