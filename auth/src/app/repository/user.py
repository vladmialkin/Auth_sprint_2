from app.models import User
from app.repository.base import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[User]):
    pass


user_repository = UserRepository(User)
