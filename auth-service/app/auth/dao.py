from datetime import datetime, timezone
from sqlalchemy import select, update
from app.core.base_dao import BaseDAO
from app.auth.models import RefreshToken

class RefreshTokenDAO(BaseDAO):
    model = RefreshToken

    async def find_by_hash(self, token_hash: str) -> RefreshToken | None:
        q = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        r = await self.session.execute(q)
        return r.scalar_one_or_none()

    async def revoke(self, token_hash: str) -> None:
        q = (
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await self.session.execute(q)