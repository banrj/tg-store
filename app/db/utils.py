import aioboto3
import datetime

from app.config import settings
from app.core.log_config import logger


async def connect_ydb():
    YC_DATABASE_URL = settings.YC_DATABASE_URL
    YC_SERVICE_ACCOUNT_KEY_ID = settings.YC_SERVICE_ACCOUNT_KEY_ID
    YC_SERVICE_ACCOUNT_SECRET_KEY = settings.YC_SERVICE_ACCOUNT_SECRET_KEY
    session = aioboto3.Session()
    async with session.client(
        'dynamodb',
        endpoint_url=YC_DATABASE_URL,
        region_name='us-east-1',
        aws_access_key_id=YC_SERVICE_ACCOUNT_KEY_ID,
        aws_secret_access_key=YC_SERVICE_ACCOUNT_SECRET_KEY
    ) as dynamodb:
        return dynamodb


async def connect_table(table_name: str):
    start_time = datetime.datetime.now()
    YC_DATABASE_URL = settings.YC_DATABASE_URL
    YC_SERVICE_ACCOUNT_KEY_ID = settings.YC_SERVICE_ACCOUNT_KEY_ID
    YC_SERVICE_ACCOUNT_SECRET_KEY = settings.YC_SERVICE_ACCOUNT_SECRET_KEY

    session = aioboto3.Session()
    async with session.resource(
        'dynamodb',
        endpoint_url=YC_DATABASE_URL,
        region_name='us-east-1',
        aws_access_key_id=YC_SERVICE_ACCOUNT_KEY_ID,
        aws_secret_access_key=YC_SERVICE_ACCOUNT_SECRET_KEY
    ) as dynamodb:
        table = await dynamodb.Table(table_name)
        logger.debug(f'DynamoDB connection duration: {datetime.datetime.now() - start_time}', extra={'user': '-'})
        return table


async def create_table(
    dynamodb_client,
    table_name,
    attribute_definitions,
    key_schema,
    provisioned_throughput
):
    response = await dynamodb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=attribute_definitions,
        KeySchema=key_schema,
        ProvisionedThroughput=provisioned_throughput
    )

    # Wait for the table to be created
    table_waiter = dynamodb_client.get_waiter('table_exists')
    await table_waiter.wait(TableName=table_name)

    # Check if the table creation was successful
    if response['TableDescription']['TableStatus'] == 'ACTIVE':
        print(f'Table {table_name} created successfully.')
    else:
        print(f'Table {table_name} creation failed.')


async def drop_general_table():
    TABLE_NAME = settings.TABLE_SUFFIX
    table = await connect_table(TABLE_NAME)
    scan = await table.scan()
    async with table.batch_writer() as batch:
        for item in scan['Items']:
            await batch.delete_item(Key={'partkey': item['partkey'], 'sortkey': item['sortkey']})


class SetupTableConnection:
    def __init__(self):
        self.table = None

    async def __call__(self):
        table_name =settings.TABLE_SUFFIX
        table = await connect_table(table_name)
        self.table = table
        return table


async def init_local_db_test_table(table_suffix: str):
    GENERAL_TABLE_NAME = mode=table_suffix
    dynamodb = await connect_ydb()

    attribute_definitions = [
        {
            'AttributeName': 'partkey',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'sortkey',
            'AttributeType': 'S'
        }
    ]
    key_schema = [
        {
            'AttributeName': 'partkey',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'sortkey',
            'KeyType': 'RANGE'
        }
    ]

    provisioned_throughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }

    response = await dynamodb.list_tables()

    # Retrieve the table names from the response
    table_names = response['TableNames']

    if GENERAL_TABLE_NAME not in table_names:
        await create_table(
            dynamodb_client=dynamodb,
            table_name=GENERAL_TABLE_NAME,
            attribute_definitions=attribute_definitions,
            key_schema=key_schema,
            provisioned_throughput=provisioned_throughput
        )
    else:
        print(f'{GENERAL_TABLE_NAME} already exists')
