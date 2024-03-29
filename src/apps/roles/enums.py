from enum import Enum


class CompanyRoles(str, Enum):
    """Возможные роли внутри компании."""

    ADMIN = "Администратор"
    PRODUCT_MANAGER = "Продуктовый менеджер"
    TECH_SUPPORT = "Техническая поддержка"
    MODERATOR = "Модератор"

    @classmethod
    def list(cls) -> list[str]:
        return [role for role in cls]
