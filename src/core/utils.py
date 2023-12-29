from __future__ import annotations

import functools
from typing import Optional, Any, Callable
from copy import deepcopy
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

from src.core.users.models import User


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
    return role in [role.name for role in user.roles]


def allow_superuser(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapped(*args, **kwargs) -> Any:
        for key, value in kwargs.items():
            if isinstance(value, User):
                if value.is_superuser:
                    return
        return await func(*args, **kwargs)

    return wrapped
