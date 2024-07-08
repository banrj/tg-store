import contextlib
import typing as t
import httpx
from aiogram import Dispatcher, Bot
from fastapi import HTTPException, Request, Depends
from app.core.context import AppContext


def tg_dp() -> Dispatcher:
    context = AppContext()
    dp = context.get_dispatcher_tg()
    # if dp is None:
    #     raise HTTPException(status_code=500, detail="Telegram dp is not initialized")
    return dp
    # tgapp = getattr(req.app.state, 'tg_app', None)
    # return tgapp
    # return req.app.state.dispatcher_tg


def tg_bot() -> Bot:
    context = AppContext()
    bot = context.get_bot()
    # if bot is None:
    #     raise HTTPException(status_code=500, detail="Telegram bot is not initialized")
    return bot


@contextlib.asynccontextmanager
async def get_async_httpx_client(**kwargs) -> httpx.AsyncClient:
    if kwargs.get('timeout') is None:
        kwargs['timeout'] = float(60)
    async with httpx.AsyncClient(**kwargs) as session:
        yield session


BotDispatcher = t.Annotated[Dispatcher, Depends(tg_dp)]
TgBot = t.Annotated[Bot, Depends(tg_bot)]
