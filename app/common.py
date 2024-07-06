import contextlib
import typing as t

import fastapi
import httpx
from aiogram import Dispatcher as BotDispatcher


def tg_app(req: fastapi.Request) -> BotDispatcher:
    return req.app.state.tg_app


@contextlib.asynccontextmanager
async def get_async_httpx_client(**kwargs) -> httpx.AsyncClient:
    if kwargs.get('timeout') is None:
        kwargs['timeout'] = float(60)
    async with httpx.AsyncClient(**kwargs) as session:
        yield session


TelegramApp = t.Annotated[BotDispatcher, fastapi.Depends(tg_app)]
