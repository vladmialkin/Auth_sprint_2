from app.models import UserRole
from app.repository.base import SQLAlchemyRepository


class UserRoleRepository(SQLAlchemyRepository[UserRole]):
    pass


user_role_repository = UserRoleRepository(UserRole)
