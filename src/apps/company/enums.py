from enum import IntEnum


class CompanyType(IntEnum):
    """
    1. Индивидуальный предприниматель
    2. Юридическое лицо
    """

    INDIVIDUAL = 1
    LLC = 2
