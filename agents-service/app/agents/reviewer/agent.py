from app.agents.base import BaseAgent
from app.agents.reviewer.prompts import SYSTEM_PROMPT, build_user_prompt
from app.agents.reviewer.schemas import ReviewResult
from app.core.config import settings
from app.llm.client import call_llm
from app.llm.parser import extract_json

MAX_RETRIES = 3


class ReviewerAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "ReviewerAgent"

    async def execute(self, payload: dict) -> dict:
        analysis = payload.get("analysis")
        generated_tests = payload.get("generated_tests")

        if not analysis:
            raise ValueError("нет 'analysis' в payload")
        if not generated_tests:
            raise ValueError("нет 'generated_tests' в payload")

        spec_id = payload.get("spec_id", "unknown")
        print(f"{self.name} начал делать ревью для spec_id={spec_id}")

        user_prompt = build_user_prompt(analysis, generated_tests)
        last_error: Exception | None = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(f"{self.name} LLM попытка {attempt}/{MAX_RETRIES}")

                raw_response = await call_llm(
                    model=settings.REVIEWER_MODEL,
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                )

                parsed = extract_json(raw_response)
                result = ReviewResult.model_validate(parsed)

                print(
                    f"{self.name} сделал: score={result.overall_score}/10, "
                    f"{result.total_issues} ошибок найдено"
                )

                return result.model_dump(mode="json")

            except Exception as e:
                last_error = e
                print(f"{self.name} попытка {attempt} выдала ошибку: {e}")

        raise RuntimeError(
            f"{self.name} все {MAX_RETRIES} попытки выдали ошибку. Последняя ошибка: {last_error}"
        )