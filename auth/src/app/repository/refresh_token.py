from app.models import RefreshToken
from app.repository.base import SQLAlchemyRepository


class RefreshTokenRepository(SQLAlchemyRepository[RefreshToken]):
    pass


refresh_token_repository = RefreshTokenRepository(RefreshToken)
