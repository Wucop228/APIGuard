from app.agents.base import BaseAgent
from app.agents.analyzer.prompts import SYSTEM_PROMPT, build_user_prompt
from app.agents.analyzer.schemas import AnalysisResult
from app.core.config import settings
from app.llm.client import call_llm
from app.llm.parser import extract_json

MAX_RETRIES = 3


class AnalyzerAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "AnalyzerAgent"

    async def execute(self, payload: dict) -> dict:
        parsed_data = payload.get("parsed_data")
        if not parsed_data:
            raise ValueError("Нет 'parsed_data' в payload")

        spec_id = payload.get("spec_id", "unknown")
        print(f"{self.name} начал анализировать для spec_id={spec_id}")

        user_prompt = build_user_prompt(parsed_data)
        last_error: Exception | None = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(f"{self.name} LLM попытка {attempt}/{MAX_RETRIES}")

                raw_response = await call_llm(
                    model=settings.ANALYZER_MODEL,
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                )

                parsed = extract_json(raw_response)
                analysis = AnalysisResult.model_validate(parsed)

                print(
                    f"{self.name} сделал: {analysis.total_endpoints} эндпоинтов, "
                    f"{analysis.total_scenarios} сценариев"
                )

                return analysis.model_dump(mode="json")

            except Exception as e:
                last_error = e
                print(f"{self.name} попытка {attempt} выдала ошибку: {e}")

        raise RuntimeError(
            f"{self.name} все {MAX_RETRIES} попытки выдали ошибки. Последняя ошибка: {last_error}"
        )