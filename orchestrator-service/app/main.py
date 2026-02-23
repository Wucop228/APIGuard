from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.broker.connection import connect_broker, disconnect_broker
from app.api.spec import router as spec_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_broker()
    yield
    await disconnect_broker()


app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def inject_user_id(request: Request, call_next):
    user_id = request.headers.get("X-User-ID")
    request.state.user_id = user_id
    return await call_next(request)

app.include_router(spec_router)