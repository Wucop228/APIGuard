from sqlalchemy.ext.asyncio import AsyncSession

from app.spec.dao import SpecDAO, SpecResultDAO
from app.spec.models import Spec
from app.spec.enums import SpecStatus
from app.spec.validator import parse_raw_content, validate_openapi, SpecValidationError
from app.spec.parser import parse_openapi
from app.broker.publisher import publish_task
from app.broker.constants import ROUTING_KEY_ANALYZE, ROUTING_KEY_GENERATE, ROUTING_KEY_REVIEW


class SpecServiceError(Exception):
    pass


class SpecService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.dao = SpecDAO(session)

    async def upload(self, user_id: str, raw_content: str) -> Spec:
        try:
            spec_dict = parse_raw_content(raw_content)
        except SpecValidationError as e:
            raise SpecServiceError(str(e))

        try:
            validate_openapi(spec_dict)
        except SpecValidationError as e:
            raise SpecServiceError(str(e))

        parsed_data = parse_openapi(spec_dict)

        spec = await self.dao.add(
            user_id=user_id,
            original_content=raw_content,
            parsed_data=parsed_data,
            status=SpecStatus.ANALYZING,
        )

        await publish_task(
            routing_key=ROUTING_KEY_ANALYZE,
            payload={
                "spec_id": spec.id,
                "parsed_data": parsed_data,
            },
        )

        return spec

    async def handle_callback(
        self,
        spec_id: str,
        agent_type: str,
        status: str,
        content: dict | None = None,
        error: str | None = None,
    ) -> None:
        spec = await self.dao.find_one_or_none(id=spec_id)
        if not spec:
            raise SpecServiceError("Спецификация не найдена")

        if status == "failed":
            await self.dao.update_by_filter(
                Spec.id == spec_id,
                status=SpecStatus.FAILED,
                error_message=error or "Unknown error",
            )
            print(f"Спецификация {spec_id}: {agent_type} ошибка {error}")
            return

        if status == "completed" and content is not None:
            result_dao = SpecResultDAO(self.session)
            await result_dao.add(
                spec_id=spec_id,
                agent_type=agent_type,
                content=content,
            )

            if agent_type == "analyzer":
                await self.dao.update_by_filter(
                    Spec.id == spec_id,
                    status=SpecStatus.GENERATING,
                )

                await publish_task(
                    routing_key=ROUTING_KEY_GENERATE,
                    payload={
                        "spec_id": spec_id,
                        "analysis": content,
                    },
                )
                print(f"Спецификация {spec_id}: analyzer выполнил => отправил в generator")

            elif agent_type == "generator":
                await self.dao.update_by_filter(
                    Spec.id == spec_id,
                    status=SpecStatus.REVIEWING,
                )

                analysis_result = await result_dao.find_one_or_none(
                    spec_id=spec_id,
                    agent_type="analyzer",
                )

                await publish_task(
                    routing_key=ROUTING_KEY_REVIEW,
                    payload={
                        "spec_id": spec_id,
                        "analysis": analysis_result.content if analysis_result else {},
                        "generated_tests": content,
                    },
                )
                print(f"Спецификация {spec_id}: generator выполнил => отправил в reviewer")

            elif agent_type == "reviewer":
                await self.dao.update_by_filter(
                    Spec.id == spec_id,
                    status=SpecStatus.DONE,
                )
                print(f"Спецификация {spec_id}: reviewer выполнил")

    async def get_status(self, spec_id: str, user_id: str) -> Spec:
        spec = await self.dao.find_one_or_none(id=spec_id)

        if not spec:
            raise SpecServiceError("Спецификация не найдена")

        if spec.user_id != user_id:
            raise SpecServiceError("Нет доступа к этой спецификации")

        return spec

    async def get_results(self, spec_id: str, user_id: str) -> Spec:
        spec = await self.dao.find_by_id_with_results(spec_id)

        if not spec:
            raise SpecServiceError("Спецификация не найдена")

        if spec.user_id != user_id:
            raise SpecServiceError("Нет доступа к этой спецификации")

        return spec

    async def get_user_specs(self, user_id: str) -> list[Spec]:
        return await self.dao.find_all(user_id=user_id)