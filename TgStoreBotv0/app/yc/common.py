from contextlib import asynccontextmanager
from httpx import AsyncClient


@asynccontextmanager
async def get_async_httpx_client(**kwargs) -> AsyncClient:
    if kwargs.get('timeout') is None:
        kwargs['timeout'] = float(60)
    async with AsyncClient(**kwargs) as session:
        yield session
