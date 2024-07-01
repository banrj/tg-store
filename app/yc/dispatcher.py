import base64
import re

import asgi_lifespan
import fastapi
import httpx

from app.yc.common import get_async_httpx_client
from app.yc.types import YFunctionEvent
from app.core.log_config import dispatcher_loger


def _is_binary(response) -> bool:
    if not response.headers.get("content-type"):
        return False

    content_type = response.headers["content-type"]
    return any(
        re.match(re_, content_type) for re_ in (
            r"image/.*",
            r"video/.*",
            r"audio/.*",
            r".*zip",
            r".*pdf",
        )
    )


def _patch_function_response(response: httpx.Response):
    dispatcher_loger.debug(response.__dict__)

    is_binary_ = _is_binary(response)
    if is_binary_:
        body = base64.b64encode(response.content).decode("utf-8")
    else:
        body = response.content.decode()
    return {
        "statusCode": response.status_code,
        "headers": dict(response.headers),
        "body": body,
        "isBase64Encoded": is_binary_,
    }


def _patch_base64_body(event: YFunctionEvent):
    if not event["body"]:
        pass
    elif event["isBase64Encoded"]:
        event["body"] = base64.b64decode(event["body"])
    else:
        event["body"] = event["body"].encode()


class Dispatcher:

    def __init__(self, asgi_app: fastapi.FastAPI):
        self.asgi_app = asgi_app

    async def _invoke_app(self, event: YFunctionEvent):
        dispatcher_loger.debug(event)

        host_url = event["headers"].get("Host", "https://raw-function.net")
        if not host_url.startswith("http"):
            host_url = f"https://{host_url}"
        _patch_base64_body(event)

        async with asgi_lifespan.LifespanManager(
            self.asgi_app,
            startup_timeout=float(60),
            shutdown_timeout=float(60)
        ) as lifespan_manager:
            async with get_async_httpx_client(
                app=lifespan_manager.app,
                base_url=host_url
            ) as asgi_app_client:
                request = asgi_app_client.build_request(
                    method=event["httpMethod"],
                    url=event["url"],
                    headers=event["headers"],
                    params=event["multiValueQueryStringParameters"],
                    content=event["body"],
                )
                asgi_app_response = await asgi_app_client.send(request)
                return asgi_app_response

    async def __call__(self, event: YFunctionEvent, ctx):
        dispatcher_loger.info(f"DISPATCHER STARTUP")

        if not event:
            return {
                "statusCode": 500,
                "body": "got empty event",
            }
        response = await self._invoke_app(event)

        dispatcher_loger.info(f"DISPATCHER SHUTDOWN")
        return _patch_function_response(response)
