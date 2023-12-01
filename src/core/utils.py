from __future__ import annotations
from typing import Optional, Any
from copy import deepcopy
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo


def make_field_partial(field: FieldInfo, default: Any = None) -> (Any, FieldInfo):
    new = deepcopy(field)
    new.default = default
    new.annotation = Optional[field.annotation]
    return new.annotation, new


def optional(cls: type[BaseModel]) -> type[BaseModel]:
    fields_in_partial_mode = {
        field: make_field_partial(info) for field, info in cls.model_fields.items()
    }
    return create_model(
        cls.__name__,
        __base__=cls,
        __module__=cls.__module__,
        **fields_in_partial_mode,
    )
