from app.agents.base import BaseAgent
from app.agents.generator.prompts import SYSTEM_PROMPT, build_user_prompt
from app.agents.generator.schemas import GenerationResult
from app.core.config import settings
from app.llm.client import call_llm
from app.llm.parser import extract_json

MAX_RETRIES = 3


class GeneratorAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "GeneratorAgent"

    async def execute(self, payload: dict) -> dict:
        analysis = payload.get("analysis")
        if not analysis:
            raise ValueError("Нет 'analysis' в payload")

        spec_id = payload.get("spec_id", "unknown")
        print(f"{self.name} начал анализировать для spec_id={spec_id}")

        user_prompt = build_user_prompt(analysis)
        last_error: Exception | None = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(f"{self.name} LLM попытка {attempt}/{MAX_RETRIES}")

                raw_response = await call_llm(
                    model=settings.GENERATOR_MODEL,
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                )

                parsed = extract_json(raw_response)
                result = GenerationResult.model_validate(parsed)

                print(
                    f"{self.name} сделал: {result.total_tests} количество сгенерированных файлов с тестами"
                )

                return result.model_dump(mode="json")

            except Exception as e:
                last_error = e
                print(f"{self.name} попытка {attempt} выдала ошибку: {e}")

        raise RuntimeError(
            f"{self.name} все {MAX_RETRIES} попытки выдали ошибку. Последняя ошибка: {last_error}"
        )