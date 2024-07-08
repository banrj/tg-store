import aioboto3
import pydantic
import types_aiobotocore_dynamodb as aiodyno_types
from contextlib import asynccontextmanager
from app.config import settings

from app.core.log_config import logger


async def dynamodb_connection(
    endpoint_url: pydantic.HttpUrl = settings.YC_DATABASE_URL,
    access_key: str = settings.YC_SERVICE_ACCOUNT_KEY_ID,
    secret_key: str = settings.YC_SERVICE_ACCOUNT_SECRET_KEY,
) -> [tuple[aiodyno_types.DynamoDBServiceResource, aiodyno_types.DynamoDBClient]]:
    session = aioboto3.Session()

    setup_data = {
        "service_name": 'dynamodb',
        "region_name": 'ru-central1',
        "aws_access_key_id": access_key,
        "aws_secret_access_key": secret_key,
        "endpoint_url": endpoint_url,
    }

    async with session.resource(**setup_data) as dyno_resource, session.client(**setup_data) as dyno_client:
        return dyno_resource, dyno_client


class DynamoConnection:
    def __init__(
        self,
        dyno_client: aiodyno_types.DynamoDBClient,
        dyno_resource: aiodyno_types.DynamoDBServiceResource,
        *,
        default_table: str = settings.TABLE_SUFFIX,
    ) -> None:
        self._client = dyno_client
        self._resource = dyno_resource
        self._default_table = default_table

    async def table(self, table_name: str | None = None):
        logger.debug(f'Запрашиваемая таблица: {table_name}')
        if table_name is None:
            table_name = self._default_table
        try:
            table_list = await self._client.list_tables()
            table_names = table_list.get('TableNames', [])
            logger.info(f"Доступные таблицы: {table_names}")
            response = await self._client.describe_table(TableName=table_name)
            logger.info(f"Таблица '{table_name}' существует: {response}")
        except Exception as e:
            logger.error(f"Ошибка при проверке таблицы '{table_name}': {e}")
            raise
