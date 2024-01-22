from pydantic_settings import BaseSettings
import secrets
from pydantic import Field
from pathlib import Path
from typing import Union


class YWStoreBaseSettings(BaseSettings):
    PROJECT_NAME: str = "YWStore"
    API_VERSION_INT: int = 1
    BASE_API_PREFIX: str = f"/api/v{API_VERSION_INT}"
    ABSOLUTE_BASE_DIR: Path = Path().absolute()
    BASE_MODULE_PATH: Path = Path("src", "apps")

    class ConfigDict:
        extra = "allow"
        env_file = ".env"
        case_sensitive = True


class PGSettings(YWStoreBaseSettings):
    POSTGRES_DB: str = Field("YWStore", title="Postgres DB name")
    POSTGRES_USER: str = Field("YWStore", title="Postgres DB user")
    POSTGRES_PASSWORD: str = Field("YWStore", title="Postgres DB password")
    POSTGRES_HOST: str = Field("ywstore-postgres", title="Postgres DB host")
    POSTGRES_PORT: int = Field(5432, title="Postgres port")
    POSTGRES_DRIVER: str = "postgresql+asyncpg"

    @property
    def sqlalchemy_db_uri(self) -> str:
        return f"{self.POSTGRES_DRIVER}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"


class RedisSettings(YWStoreBaseSettings):
    REDIS_HOST: str = Field("ywstore-redis", title="Redis host name")
    REDIS_PORT: int = Field(6379, title="Redis connection port")


class YWStoreSettings(YWStoreBaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60
    SQL_ECHO: bool = True
    DEBUG: bool = Field(True)
    postgres: PGSettings = PGSettings()
    redis: RedisSettings = RedisSettings()


def get_settings(db_only=False) -> Union[PGSettings, YWStoreSettings]:
    return PGSettings() if db_only else YWStoreSettings()
