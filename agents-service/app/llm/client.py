from openai import AsyncOpenAI

from app.core.config import settings

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            base_url=settings.NVIDIA_BASE_URL,
            api_key=settings.NVIDIA_API_KEY,
            timeout=180.0,
        )
    return _client


async def call_llm(model: str, system_prompt: str, user_prompt: str) -> str:
    client = _get_client()

    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=settings.LLM_TEMPERATURE,
        top_p=0.95,
        max_tokens=settings.LLM_MAX_TOKENS,
    )

    return completion.choices[0].message.content