from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.http_client import get_http_client

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok", "service": "gateway"}


@router.get("/health/details")
async def health_details():
    client = get_http_client()
    services = {}

    try:
        resp = await client.get(f"{settings.AUTH_SERVICE_URL}/docs", timeout=3.0)
        services["auth"] = {
            "status": "ok" if resp.status_code < 500 else "degraded",
            "url": settings.AUTH_SERVICE_URL,
            "http_code": resp.status_code,
        }
    except Exception as e:
        services["auth"] = {
            "status": "unavailable",
            "url": settings.AUTH_SERVICE_URL,
            "error": str(e),
        }

    all_ok = all(s["status"] == "ok" for s in services.values())

    return JSONResponse(
        status_code=200 if all_ok else 503,
        content={
            "gateway": "ok",
            "services": services,
        },
    )