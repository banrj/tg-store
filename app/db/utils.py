import datetime

import boto3

from app.db import config as db_config, keys_structure
from app.settings import settings
from app.core.log_config import logger


def connect_ydb():
    YANDEX_DB_URL = settings.YC_DATABASE_URL
    YANDEX_SERVICE_ACCOUNT_KEY_ID = settings.YC_SERVICE_ACCOUNT_KEY_ID
    YANDEX_SERVICE_ACCOUNT_SECRET_KEY = settings.YC_SERVICE_ACCOUNT_SECRET_KEY

    dynamodb = boto3.client(
        'dynamodb',
        endpoint_url=YANDEX_DB_URL,
        region_name='us-east-1',
        aws_access_key_id=YANDEX_SERVICE_ACCOUNT_KEY_ID,
        aws_secret_access_key=YANDEX_SERVICE_ACCOUNT_SECRET_KEY
    )

    return dynamodb


def connect_table(table_name: str):
    start_time = datetime.datetime.now()
    YANDEX_DB_URL = settings.YC_DATABASE_URL
    YANDEX_SERVICE_ACCOUNT_KEY_ID = settings.YC_SERVICE_ACCOUNT_KEY_ID
    YANDEX_SERVICE_ACCOUNT_SECRET_KEY = settings.YC_SERVICE_ACCOUNT_SECRET_KEY

    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=YANDEX_DB_URL,
        region_name='us-east-1',
        aws_access_key_id=YANDEX_SERVICE_ACCOUNT_KEY_ID,
        aws_secret_access_key=YANDEX_SERVICE_ACCOUNT_SECRET_KEY
    )
    table = dynamodb.Table(table_name)
    logger.debug(f'DynamoDB connection duration: {datetime.datetime.now() - start_time}', extra={'user': '-'})

    return table


def create_table(
    dynamodb_client,
    table_name,
    attribute_definitions,
    key_schema,
    provisioned_throughput
):
    response = dynamodb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=attribute_definitions,
        KeySchema=key_schema,
        ProvisionedThroughput=provisioned_throughput
    )

    # Wait for the table to be created
    table_waiter = dynamodb_client.get_waiter('table_exists')
    table_waiter.wait(TableName=table_name)

    # Check if the table creation was successful
    if response['TableDescription']['TableStatus'] == 'ACTIVE':
        print(f'Table {table_name} created successfully.')
    else:
        print(f'Table {table_name} creation failed.')


def get_gen_table():
    return connect_table(db_config.general_table.format(mode=settings.TABLE_SUFFIX))


def get_tokens_table():
    return connect_table(db_config.tokens_table.format(mode=settings.TABLE_SUFFIX))


class SetupTablesConnection:
    # def __init__(self):
    #     pass

    def __call__(self):
        self.general_table = connect_table(db_config.general_table.format(mode=settings.TABLE_SUFFIX))
        self.tokens_table = connect_table(db_config.tokens_table.format(mode=settings.TABLE_SUFFIX))

        return self


def init_local_db_test_table(table_suffix: str):
    GENERAL_TABLE_NAME = db_config.general_table.format(mode=table_suffix)
    TOKENS_TABLE_NAME = db_config.tokens_table.format(mode=table_suffix)
    dynamodb = connect_ydb()

    attribute_definitions = [
        {
            'AttributeName': keys_structure.db_table_partkey,
            'AttributeType': 'S'
        },
        {
            'AttributeName': keys_structure.db_table_sortkey,
            'AttributeType': 'S'
        }
    ]
    key_schema = [
        {
            'AttributeName': keys_structure.db_table_partkey,
            'KeyType': 'HASH'
        },
        {
            'AttributeName': keys_structure.db_table_sortkey,
            'KeyType': 'RANGE'
        }
    ]

    provisioned_throughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }

    response = dynamodb.list_tables()

    # Retrieve the table names from the response
    table_names = response['TableNames']

    if GENERAL_TABLE_NAME not in table_names:
        create_table(
            dynamodb_client=dynamodb,
            table_name=GENERAL_TABLE_NAME,
            attribute_definitions=attribute_definitions,
            key_schema=key_schema,
            provisioned_throughput=provisioned_throughput
        )
    else:
        print(f'{GENERAL_TABLE_NAME} already exists')

    if TOKENS_TABLE_NAME not in table_names:
        create_table(
            dynamodb_client=dynamodb,
            table_name=TOKENS_TABLE_NAME,
            attribute_definitions=attribute_definitions,
            key_schema=key_schema,
            provisioned_throughput=provisioned_throughput
        )
    else:
        print(f'{TOKENS_TABLE_NAME} already exists')


def replace_dict_key(item, orig_key, new_key):
    if orig_key in item:
        if new_key not in item:
            item[new_key] = item[orig_key]
        del item[orig_key]


def substitute_keys_to_db(item):
    replace_dict_key(item, 'id', 'id_')
    replace_dict_key(item, 'name', 'name_')
    replace_dict_key(item, 'uuid', 'uuid_')


def substitute_keys_from_db(item):
    item.pop('partkey', None)
    item.pop('sortkey', None)
    replace_dict_key(item, 'id_', 'id')
    replace_dict_key(item, 'name_', 'name')
    replace_dict_key(item, 'uuid_', 'uuid')


def substitute_keys(dict4process: dict, base_keys: dict, opt_dict: dict = None):
    all_keys = base_keys | (opt_dict if opt_dict else {})
    for key, val in all_keys.items():
        if val:
            replace_dict_key(dict4process, key, val)
        elif key in dict4process.keys():
            dict4process.pop(key, None)


def substitute_records(records4process: list[dict], base_keys: dict, opt_dict: dict = None):
    for i, _ in enumerate(records4process):
        substitute_keys(
            dict4process=records4process[i],
            base_keys=base_keys,
            opt_dict=opt_dict
        )
