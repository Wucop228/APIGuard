from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.base_dao import BaseDAO
from app.spec.models import Spec, SpecResult


class SpecDAO(BaseDAO):
    model = Spec

    async def find_by_id_with_results(self, spec_id: str) -> Spec | None:
        query = (
            select(Spec)
            .options(selectinload(Spec.results))
            .where(Spec.id == spec_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class SpecResultDAO(BaseDAO):
    model = SpecResult