from fastapi import FastAPI

from app.core.http_client import lifespan
from app.middleware.auth import AuthMiddleware
from app.middleware.request_id import RequestIdMiddleware
from app.routers import auth, health, spec

app = FastAPI(lifespan=lifespan)


app.add_middleware(AuthMiddleware)
app.add_middleware(RequestIdMiddleware)


app.include_router(auth.router)
app.include_router(health.router)
app.include_router(spec.router)