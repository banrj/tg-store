async def put_item(
    table,
    partkey: str,
    sortkey: str,
    item_payload: dict,
    condition_expression: str | None = None
):
    item_payload_dropna = {key: value for key, value in item_payload.items() if value is not None}
    if not condition_expression:
        response = await table.put_item(
            Item={
                'partkey': partkey,
                'sortkey': sortkey,
                **item_payload_dropna
            }
        )
    else:
        response = await table.put_item(
            Item={
                'partkey': partkey,
                'sortkey': sortkey,
                **item_payload_dropna
            },
            ConditionExpression=condition_expression
        )
    return response


async def get_item(
    table,
    partkey: str,
    sortkey: str
):
    response = await table.get_item(
        Key={
            'partkey': partkey,
            'sortkey': sortkey
        }
    )

    return response


async def query(table, **query_args):

    response = await table.query(**query_args)
    return response


async def update_item(table, Key, UpdateExpression, ExpressionAttributeNames ,ExpressionAttributeValues):

    response = await table.update_item(
        Key=Key,
        UpdateExpression=UpdateExpression,
        ExpressionAttributeNames=ExpressionAttributeNames,
        ExpressionAttributeValues=ExpressionAttributeValues,
        ReturnValues='ALL_NEW'
    )

    return response


async def delete_item(
    table_connection,
    partkey: str,
    sortkey: str
):
    async with table_connection as table_conn:
        response = await table_conn.delete_item(Key={'partkey': partkey, 'sortkey': sortkey})

    return response


async def scan(table_connection):
    async with table_connection as table_conn:
        response = await table_conn.scan()

    return response
