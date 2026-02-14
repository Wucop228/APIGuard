from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.http_client import get_http_client

router = APIRouter(prefix="/auth", tags=["auth"])


async def _proxy_to_auth(
    request: Request,
    path: str,
    method: str = "POST",
) -> Response:
    client = get_http_client()
    url = f"{settings.AUTH_SERVICE_URL}{path}"

    headers = {
        "Content-Type": "application/json",
    }

    request_id = getattr(request.state, "request_id", None)
    if request_id:
        headers["X-Request-ID"] = request_id

    cookies = dict(request.cookies)

    body = await request.body()

    try:
        upstream_response = await client.request(
            method=method,
            url=url,
            content=body if body else None,
            headers=headers,
            cookies=cookies,
        )
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={"detail": f"Auth-service недоступен: {str(e)}"},
        )

    response = Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        media_type="application/json",
    )

    for key, value in upstream_response.headers.multi_items():
        if key.lower() == "set-cookie":
            response.headers.append("set-cookie", value)

    return response


@router.post("/register")
async def register(request: Request):
    return await _proxy_to_auth(request, "/user/register")


@router.post("/login")
async def login(request: Request):
    return await _proxy_to_auth(request, "/auth/login")


@router.post("/logout")
async def logout(request: Request):
    return await _proxy_to_auth(request, "/auth/logout")


@router.post("/refresh")
async def refresh(request: Request):
    return await _proxy_to_auth(request, "/auth/refresh")


@router.get("/me")
async def me(request: Request):
    return await _proxy_to_auth(request, "/auth/me", method="GET")