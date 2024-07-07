import datetime
import re
import httpx
from base64 import b64decode, b64encode

from fastapi import FastAPI

from app.main import create_app as create_fastapi_app
from app.core.log_config import logger
from app.tg.create_app import initialize_components, shutdown


def body_to_bytes(event):
    if not event["body"]:
        pass
    elif event["isBase64Encoded"]:
        event["body"] = b64decode(event["body"])
    else:
        event["body"] = event["body"].encode()


async def call_app(application: FastAPI, event) -> httpx.Response:
    logger.info('-----CALL APP-----')
    host_url = event["headers"].get("Host", "https://raw-function.net")
    if not host_url.startswith("http"):
        host_url = f"https://{host_url}"
    body_to_bytes(event)

    async with httpx.AsyncClient(app=application, base_url=host_url) as client:
        request = client.build_request(
            method=event["httpMethod"],
            url=event["url"],
            headers=event["headers"],
            params=event["queryStringParameters"],
            content=event["body"],
        )
        response = await client.send(request)
        return response


def is_binary(response):
    if not response.headers.get("content-type"):
        return False

    content_type = response.headers["content-type"]
    return any(
        re_.match(content_type) for re_ in (
            re.compile(r"image/.*"),
            re.compile(r"video/.*"),
            re.compile(r"audio/.*"),
            re.compile(r".*zip"),
            re.compile(r".*pdf"),
        )
    )


def patch_response(response: httpx.Response):
    """
    returns Http response in the format of
    {
     'status code': 200,
     'body': body - string or base64-string in case of binary content,
     'headers': {}
    }
    """
    is_binary_ = is_binary(response)
    if is_binary_:
        body = b64encode(response.content).decode("utf-8")
    else:
        body = response.content.decode()
    return {
        "statusCode": response.status_code,
        "headers": dict(response.headers),
        "body": body,
        "isBase64Encoded": is_binary_,
    }


async def handle(event, _):
    logger.info(f"APPLICATION STARTUP {datetime.datetime.now()}", extra={'user': 'handler'})
    logger.debug(f'{event=}', extra={'user': 'handler'})
    fastapi_app = create_fastapi_app()
    try:
        state_dict = {key: str(value) for key, value in fastapi_app.state.__dict__.items()}
        logger.info(f"Check in Handle State: {state_dict}")
        if not hasattr(fastapi_app.state, "bot"):
            logger.info("Start Initialized")
            await initialize_components(fastapi_app)
        else:
            logger.info("Components already initialized")

    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        return {
            "statusCode": 500,
            "body": "Error during initialization",
        }
    if not event:
        return {
            "statusCode": 500,
            "body": "got empty event",
        }
    if 'event_metadata' in event:
        logger.info('event_metadata in handle')
        return {
            "statusCode": 200,
            "body": "event_metadata",
        }
    response = await call_app(fastapi_app, event)
    await shutdown(fastapi_app)
    logger.info(f"APPLICATION SHUTDOWN {datetime.datetime.now()}", extra={'user': 'handler'})
    return patch_response(response)