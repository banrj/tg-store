import contextlib
import typing as t
import httpx
from aiogram import Dispatcher as BotDispatcher
from fastapi import HTTPException, Request, Depends


def tg_app(req: Request) -> BotDispatcher:
    # tgapp = getattr(req.app.state, 'tg_app', None)
    # if tgapp is None:
    #     raise HTTPException(status_code=500, detail="Telegram app is not initialized")
    # return tgapp
    return BotDispatcher()


@contextlib.asynccontextmanager
async def get_async_httpx_client(**kwargs) -> httpx.AsyncClient:
    if kwargs.get('timeout') is None:
        kwargs['timeout'] = float(60)
    async with httpx.AsyncClient(**kwargs) as session:
        yield session


TelegramApp = t.Annotated[BotDispatcher, Depends(tg_app)]
