from app.core.base_dao import BaseDAO
from app.auth.models import RefreshToken

class RefreshTokenDAO(BaseDAO):
    model = RefreshToken