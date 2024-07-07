import contextlib
import typing as t
import httpx
from aiogram import Dispatcher, Bot
from fastapi import HTTPException, Request, Depends
from app.core.context import AppContext


def tg_dp() -> Dispatcher:
    context = AppContext()
    dp = context.get_dispatcher_tg()
    return dp
    # tgapp = getattr(req.app.state, 'tg_app', None)
    # if tgapp is None:
    #     raise HTTPException(status_code=500, detail="Telegram app is not initialized")
    # return tgapp
    # return req.app.state.dispatcher_tg


def tg_bot() -> Bot:
    context = AppContext()
    bot = context.get_bot()
    return bot


@contextlib.asynccontextmanager
async def get_async_httpx_client(**kwargs) -> httpx.AsyncClient:
    if kwargs.get('timeout') is None:
        kwargs['timeout'] = float(60)
    async with httpx.AsyncClient(**kwargs) as session:
        yield session


BotDispatcher = t.Annotated[Dispatcher, Depends(tg_dp)]
TgBot = t.Annotated[Bot, Depends(tg_bot)]
