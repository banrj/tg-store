import aioboto3
import pydantic
import types_aiobotocore_dynamodb as aiodyno_types
from contextlib import asynccontextmanager
from app.config import settings

from app.core.log_config import logger


@asynccontextmanager
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

    @asynccontextmanager
    async def table(self, table_name: str | None = None):
        logger.debug(f'{table_name=}')
        if table_name is None:
            table_name = self._default_table
        table = await self._resource.Table(table_name)
        logger.debug(f'{table_name=}')
        logger.info(table)
        return table
        # logger.debug(f'dynamo db connection to {table_name} is done')
