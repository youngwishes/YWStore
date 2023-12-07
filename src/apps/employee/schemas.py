from pydantic import BaseModel, Field
from src.core.utils import optional
from src.core.users.schemas import UserRead


class BaseEmployee(BaseModel):
    telegram: str | None = Field(..., title="Ник в телеграм")
    vk: str | None = Field(..., title="Ссылка на ВК")
    phone_number: str | None = Field(..., title="Контактный номер телефона")
    extra_data: str | None = Field(..., title="Дополнительная информация о сотруднике")
    is_active: bool

    class ConfigDict:
        from_attributes = True


class EmployeeIn(BaseEmployee):
    company_id: int
    user_id: int


class EmployeeOut(BaseEmployee):
    user: UserRead


@optional
class EmployeeOptional(BaseEmployee):
    ...
