from typing import TypedDict, Literal, Any


class YFunctionEvent(TypedDict):
    httpMethod: Literal['POST', 'GET', 'HEAD', 'OPTION', 'DELETE', 'PUT', 'PATCH']
    headers: dict
    url: str
    params: dict[str, Any]
    multiValueHeaders: dict
    queryStringParameters: dict
    multiValueQueryStringParameters: dict
    requestContext: dict
    body: str | bytes
    isBase64Encoded: bool


class YFunctionResponse(TypedDict):
    statusCode: int
    headers: dict
    body: str | bytes
    isBase64Encoded: bool
