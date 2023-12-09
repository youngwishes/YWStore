from pydantic_settings import BaseSettings
import secrets
from pydantic import Field
from pathlib import Path
from typing import Union


class YStoreBaseSettings(BaseSettings):
    PROJECT_NAME: str = "YStore"
    API_VERSION_INT: int = 1
    BASE_API_PREFIX: str = f"/api/v{API_VERSION_INT}"
    BASE_DIR: str = str(Path().absolute())

    class ConfigDict:
        extra = "allow"
        env_file = ".env"
        case_sensitive = True


class PGSettings(YStoreBaseSettings):
    POSTGRES_DB: str = Field("YStore", title="Postgres DB name")
    POSTGRES_USER: str = Field("YStore", title="Postgres DB user")
    POSTGRES_PASSWORD: str = Field("YStore", title="Postgres DB password")
    POSTGRES_HOST: str = Field("ystore-postgres", title="Postgres DB host")
    POSTGRES_PORT: int = Field(5432, title="Postgres port")
    POSTGRES_DRIVER: str = "postgresql+asyncpg"

    @property
    def sqlalchemy_db_uri(self) -> str:
        return f"{self.POSTGRES_DRIVER}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"


class YStoreSettings(YStoreBaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60
    SQL_ECHO: bool = True
    DEBUG: bool = Field(True)
    postgres: PGSettings = PGSettings()


def get_settings(db_only=False) -> Union[PGSettings, YStoreSettings]:
    return PGSettings() if db_only else YStoreSettings()
