from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

http_client: httpx.AsyncClient | None = None

def get_http_client() -> httpx.AsyncClient:
    if http_client is None:
        raise RuntimeError("HTTP client не инициализирован")
    return http_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client

    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(
            connect=5.0,
            read=30.0,
            write=10.0,
            pool=5.0,
        ),
        limits=httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20,
        ),
        follow_redirects=False,
    )

    yield

    await http_client.aclose()
    http_client = None