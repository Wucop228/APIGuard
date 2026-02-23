import httpx

from app.core.config import settings

http_client: httpx.AsyncClient | None = None


async def init_http_client() -> None:
    global http_client
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0),
    )


async def close_http_client() -> None:
    global http_client
    if http_client:
        await http_client.aclose()
        http_client = None


async def send_result(
    spec_id: str,
    agent_type: str,
    status: str,
    content: dict | None = None,
    error: str | None = None,
) -> None:
    if http_client is None:
        raise RuntimeError("HTTP client не инициализирован")

    url = f"{settings.orchestrator_callback_url}/{spec_id}/callback"

    payload = {
        "agent_type": agent_type,
        "status": status,
    }
    if content is not None:
        payload["content"] = content
    if error is not None:
        payload["error"] = error

    try:
        response = await http_client.post(url, json=payload)
        response.raise_for_status()
        print(f"Результат агента успешно отправлен: spec_id={spec_id}, status={status}")
    except httpx.HTTPError as e:
        print(f"Результат агента упал с ошибкой: spec_id={spec_id}, error={e}")
        raise