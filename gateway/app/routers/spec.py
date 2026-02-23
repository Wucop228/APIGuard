from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.http_client import get_http_client
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/spec", tags=["spec"])


async def _proxy_to_orchestrator(
    request: Request,
    path: str,
    method: str = "POST",
) -> Response:
    user_id = get_current_user(request)

    client = get_http_client()
    url = f"{settings.ORCHESTRATOR_SERVICE_URL}{path}"

    headers = {
        "Content-Type": "application/json",
        "X-User-ID": user_id,
    }

    request_id = getattr(request.state, "request_id", None)
    if request_id:
        headers["X-Request-ID"] = request_id

    body = await request.body()

    try:
        upstream_response = await client.request(
            method=method,
            url=url,
            content=body if body else None,
            headers=headers,
            params=dict(request.query_params),
        )
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={"detail": f"Orchestrator-service недоступен: {str(e)}"},
        )

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        media_type="application/json",
    )


@router.post("/upload")
async def upload_spec(request: Request):
    return await _proxy_to_orchestrator(request, "/spec/upload")


@router.get("/{spec_id}/status")
async def get_spec_status(spec_id: str, request: Request):
    return await _proxy_to_orchestrator(request, f"/spec/{spec_id}/status", method="GET")


@router.get("/{spec_id}/results")
async def get_spec_results(spec_id: str, request: Request):
    return await _proxy_to_orchestrator(request, f"/spec/{spec_id}/results", method="GET")


@router.get("/")
async def get_my_specs(request: Request):
    return await _proxy_to_orchestrator(request, "/spec/", method="GET")