import logging
import os

from pydantic_settings import (
    BaseSettings,
)


class Settings(BaseSettings):
    YC_DATABASE_URL: str
    YC_SERVICE_ACCOUNT_KEY_ID: str
    YC_SERVICE_ACCOUNT_SECRET_KEY: str

    PORT: int = 8001

    TABLE_SUFFIX: str

    TG_KEY: str

    VERSION: str = 'dev'

    USE_WEBHOOK: bool = False
    WEBHOOK: str


match os.getenv('MODE'):
    case 'CICD':
        settings = Settings()  # в этом случае переменные окружения настроены в workflow
    case _:
        settings = Settings(_env_file=('.env', '../.env'))

LOGGER_LEVEL = logging.DEBUG

