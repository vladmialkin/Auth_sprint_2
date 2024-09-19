from app.models import Role
from app.repository.base import SQLAlchemyRepository


class RoleRepository(SQLAlchemyRepository[Role]):
    pass


role_repository = RoleRepository(Role)
