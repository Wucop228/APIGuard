from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from jose import jwt, JWTError

from app.core.config import settings

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.user_id = None

        token = request.cookies.get("access_token")
        if token:
            try:
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                    options={
                        "verify_signature": True,
                        "verify_exp": True,
                        "require": ["exp", "sub"],
                    },
                )
                request.state.user_id = payload.get("sub")
            except JWTError:
                pass

        response = await call_next(request)
        return response