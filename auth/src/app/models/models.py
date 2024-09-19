from datetime import datetime
from uuid import UUID as PY_UUID

from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTableUUID,
    SQLAlchemyBaseUserTableUUID,
)
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, mapper_registry
from app.models.constance import (
    NAME_STR_LEN,
    REFRESH_TOKEN_STR_LEN,
    USER_AGENT_STR_LEN,
)

user_role = Table(
    "userrole",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True),
)


class UserRole:
    pass


mapper_registry.map_imperatively(UserRole, user_role)


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary=user_role, back_populates="users"
    )
    sessions: Mapped[list["Session"]] = relationship(
        "Session", back_populates="user"
    )

    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )

    def __str__(self) -> str:
        return f"User ({self.id}) {self.email}"


class Role(Base):
    name: Mapped[UUID] = mapped_column(String(NAME_STR_LEN), unique=True)

    users: Mapped[list[User]] = relationship(
        "User", secondary=user_role, back_populates="roles"
    )

    def __str__(self) -> str:
        return f"Role ({self.id}) {self.name}"


class RefreshToken(Base):
    token: Mapped[str] = mapped_column(
        String(REFRESH_TOKEN_STR_LEN), unique=True
    )
    expiration_date: Mapped[datetime] = mapped_column(DateTime(timezone=False))

    session: Mapped["Session"] = relationship(
        "Session", back_populates="refresh_token"
    )

    def __str__(self) -> str:
        return f"RefreshToken ({self.id}) {self.token[:6]}"


class Session(Base):
    user_id: Mapped[PY_UUID] = mapped_column(ForeignKey("user.id"))
    refresh_token_id: Mapped[PY_UUID] = mapped_column(
        ForeignKey("refreshtoken.id")
    )
    user_agent: Mapped[str | None] = mapped_column(String(USER_AGENT_STR_LEN))

    user: Mapped[User] = relationship("User", back_populates="sessions")
    refresh_token: Mapped[RefreshToken] = relationship(
        "RefreshToken", back_populates="session"
    )

    def __str__(self) -> str:
        return f"Session ({self.id}) of user {self.user_id}"
