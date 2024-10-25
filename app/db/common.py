import typing
import datetime

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from app.db import utils as db_utils
from app.core.log_config import logger
from app.dto.exceptions import common as exceptions_common


to_db_basic_keys = {
    'name': "name_",
    'id': "id_",
    'uuid': "uuid_"
}

to_ui_basic_keys = {
    'name_': "name",
    'id_': "id",
    'uuid_': "uuid",
    'partkey': None,
    'sortkey': None,
}

def make_pk_sk_private(item):
    item["_partkey"] = item.pop("partkey")
    item["_sortkey"] = item.pop("sortkey")
    return item


def update_db_record(update_request, table_connection=db_utils.get_gen_table):
    return table_connection().update_item(**update_request)["Attributes"]


def get_db_item(partkey: str, sortkey: str, table_connection=db_utils.get_gen_table) -> dict:
    result = table_connection().get_item(
        Key={
            'partkey': partkey,
            'sortkey': sortkey
        }
    )

    if result.__contains__('Item'):
        return result['Item']
    else:
        logger.error(f"get_db_item ::: record partkey={partkey} sortkey={sortkey} not found")
        return {}


def delete_db_item(partkey, sortkey, check_condition=False, table_connection=db_utils.get_gen_table):
    item = {
        'Key': {'partkey': partkey, 'sortkey': sortkey},
        'ConditionExpression': 'partkey = :partkey and sortkey=:sortkey',
        'ExpressionAttributeValues': {':partkey': partkey, ':sortkey': sortkey}
    }
    if not check_condition:
        item.pop('ConditionExpression')
        item.pop('ExpressionAttributeValues')

    return table_connection().delete_item(
        **item
    )


def query_items_paged(key_condition_expression, filter_expression=None, projection_expression=None,
                      table_connection=db_utils.get_gen_table, index_name=None, expr_attr_names=None):
    """ This method shall be used whenever you think the query will
        return more than 1mb of data at once"""
    kwargs = {'KeyConditionExpression': key_condition_expression}
    if filter_expression:
        kwargs.update({'FilterExpression': filter_expression})

    if projection_expression:
        kwargs.update({'ProjectionExpression': projection_expression})

    if expr_attr_names:
        kwargs.update({'ExpressionAttributeNames': expr_attr_names})

    if index_name:
        kwargs.update({'IndexName': index_name})

    resp = table_connection().query(**kwargs)
    data = resp['Items']

    while 'LastEvaluatedKey' in resp:
        kwargs.update({'ExclusiveStartKey': resp['LastEvaluatedKey']})
        resp = table_connection().query(**kwargs)
        data.extend(resp['Items'])
    return data


def expression_preparation(*args, **kwargs):
    update_expression_values = 'set'
    expression_attribute_values = {}
    expression_attribute_names = {}
    for key in kwargs.keys():
        if key in args:
            update_expression_values += f" #{key}=:{key},"
            expression_attribute_values.update({
                f":{key}": kwargs[key]
            })
            expression_attribute_names.update({
                f"#{key}": key
            })
    return update_expression_values[:-1], expression_attribute_values, expression_attribute_names


def pydantic_db_update_helper(item, return_values='ALL_NEW') -> typing.Dict:
    body: dict = item.to_db()
    update_expression, values, names = expression_preparation(*body.keys(), **body)
    return dict(
        Key={
            'partkey': item._partkey,
            'sortkey': item._sortkey
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=values,
        ExpressionAttributeNames=names,
        ReturnValues=return_values
    )


def change_inactive_status(pk: str, sk: str, user_uuid: str, inactive: bool, return_values = 'ALL_NEW') -> dict:
    user_uuid = str(user_uuid)
    logger.info(f"change_inactive_status ::: partkey={pk}, sortkey={sk}")
    return db_utils.get_gen_table().update_item(
        Key={
            'partkey': pk,
            'sortkey': sk
        },
        UpdateExpression=f"set #inactive = :inactive_value, #user_uuid = :user_uuid_value, #date_update = :date_update_value",
        ExpressionAttributeValues={
            ':inactive_value': inactive,
            ':user_uuid_value': user_uuid,
            ':date_update_value': datetime.datetime.now().isoformat()
        },
        ExpressionAttributeNames={
            '#inactive': 'inactive', '#user_uuid': 'user_uuid', '#date_update': 'date_update'},
        ReturnValues=return_values
    ).get("Attributes", {})


def change_inactive_status_by_owner(pk: str, sk: str, user_uuid: str, inactive: bool, return_values = 'ALL_NEW') -> dict:
    user_uuid = str(user_uuid)
    try:
        logger.info(f"delete_shop_db_request ::: make inactive shop: partkey={pk}, sortkey={sk}")
        return db_utils.get_gen_table().update_item(
            Key={
                'partkey': pk,
                'sortkey': sk
            },
            UpdateExpression=f"set #inactive = :inactive_value, #user_uuid = :user_uuid_value, #date_update = :date_update_value",
            ExpressionAttributeValues={
                ':inactive_value': inactive,
                ':user_uuid_value': user_uuid,
                ':date_update_value': datetime.datetime.now().isoformat()
            },
            ExpressionAttributeNames={
                '#inactive': 'inactive', '#user_uuid': 'user_uuid', '#date_update': 'date_update'},
            ConditionExpression=(Attr("owner_uuid").eq(user_uuid)),
            ReturnValues=return_values
        ).get("Attributes", {})
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            raise exceptions_common.IncorrectOwner
        else:
            raise e