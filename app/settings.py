import logging
import os

from pydantic_settings import (
    BaseSettings,
)


class Settings(BaseSettings):
    YC_DATABASE_URL: str
    YC_PRODUCTS_BUCKET_NAME: str
    YC_SERVICE_BUCKET_NAME: str
    YC_PRODUCTS_BUCKET_URL_PREFIX: str = "https://storage.yandexcloud.net"  # не править
    YC_SERVICE_ACCOUNT_KEY_ID: str
    YC_SERVICE_ACCOUNT_SECRET_KEY: str

    PORT: int = 8000

    TABLE_SUFFIX: str

    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    # Ссылка на базовый редирект если с магазинами или шаблонами что-то не так
    DEFAULT_REDIRECT_URL: str = 'https://stl.im/'

    BACKUP_DELAY_IN_DAYS: int = 10
    APP_BOT_API_KEY: (
        str  # ключ для того чтобы бот загружал страницу магазина в приложении телеги
    )

    ADMIN_API_KEY: str

    # * Token expiration in MINUTES
    ACCESS_TOKEN_EXPIRATION: float = 60
    REFRESH_TOKEN_EXPIRATION: float = 43200
    ACCESS_TEMPLATE_TOKEN_EXPIRATION: float = 1440

    TG_SHA256_HASH_BOT_TOKEN: str

    # * Max telegram signed data expiration
    MIN_TG_AUTH_DATETIME: float = 1

    LOGGER_LEVEL: str = "DEBUG"

    SHOP_TRIAL_DAYS: int = 7


match os.getenv("MODE"):
    case "CICD":
        settings = Settings()  # в этом случае переменные окружения настроены в workflow
        print(f"{settings=}")
    case "TO_REAL_DEV":
        settings = Settings(_env_file=(".env", "../.env"))
    case "LOCAL_DEV":
        settings = Settings(
            _env_file=(".env.local-development", "../.env.local-development")
        )
        print(f"{settings=}")
    case "DEV":
        settings = Settings(_env_file=".env.dev")
        print(f"{settings=}")
    case "STAGE":
        pass
    case _:
        settings = Settings(_env_file=(".env.local-testing", "../.env.local-testing"))
        print(f"{settings=}")


LOGGER_LEVEL = logging.DEBUG
