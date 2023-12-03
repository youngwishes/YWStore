from __future__ import annotations
from typing import TYPE_CHECKING
from src.core.config import get_settings
from sqlalchemy import URL

if TYPE_CHECKING:
    from src.core.config import PGSettings


settings: PGSettings = get_settings(db_only=True)

TEST_DB_NAME: str = "test_db"

SQLALCHEMY_DATABASE_TEST_URI: URL = URL.create(
    drivername=settings.POSTGRES_DRIVER,
    host=settings.POSTGRES_HOST,
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    port=settings.POSTGRES_PORT,
    database=TEST_DB_NAME,
)

HOST_URL: str = "http://0.0.0.0:8000/"

TEST_USER_EMAIL: str = "test@example.com"
TEST_USER_FIRST_NAME: str = "test_first_name"
TEST_USER_LAST_NAME: str = "test_user_last_name"
TEST_USER_MIDDLE_NAME: str = "test_user_middle_name"
TEST_USER_PASSWORD: str = "test_user_password"
