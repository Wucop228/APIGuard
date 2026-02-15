from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.broker.connection import connect_broker, disconnect_broker
from app.api.spec import router as spec_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_broker()
    yield
    await disconnect_broker()


app = FastAPI(lifespan=lifespan)

app.include_router(spec_router)