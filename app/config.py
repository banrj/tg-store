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

    VERSION: str = 0
    USE_WEBHOOK: bool = True


match os.getenv('MODE'):
    case 'CICD':
        settings = Settings()  # в этом случае переменные окружения настроены в workflow
        print(f'{settings=}')
    case _:
        settings = Settings(_env_file=('.env', '../.env'))
        print(settings)

LOGGER_LEVEL = logging.DEBUG
