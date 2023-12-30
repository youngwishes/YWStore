from __future__ import annotations
import os
from pathlib import Path
from typing import Optional, Any
from copy import deepcopy
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo
from importlib import import_module
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


def import_schema(schema_class_name: str) -> type[BaseModel]:
    schema_file_name = "schemas"
    exclude = ["__pycache__", "__init__.py"]
    for app_name in os.listdir(settings.BASE_MODULE_PATH):
        if app_name not in exclude:
            app_module_path = Path.joinpath(
                settings.BASE_MODULE_PATH,
                app_name,
                schema_file_name,
            )
            module_path = ".".join(str(app_module_path).split("/"))
            module = import_module(module_path)
            try:
                return getattr(module, schema_class_name)
            except AttributeError:
                ...
