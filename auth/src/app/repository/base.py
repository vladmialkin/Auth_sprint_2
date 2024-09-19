from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

T = TypeVar("T", bound=Base)


class SQLAlchemyRepository[T]:
    def __init__(self, model: type[T]) -> None:
        self._model = model

    async def exists(self, session: AsyncSession, **attrs) -> bool:
        query = select(self._model).filter_by(**attrs)

        return (await session.execute(query)).scalars().first() is not None

    async def get(
        self, session: AsyncSession, options: Any | None = None, **attrs
    ) -> T | None:
        query = select(self._model).filter_by(**attrs)

        if options is not None:
            if isinstance(options, list):
                for option in options:
                    query = query.options(option)
            else:
                query = query.options(options)

        return (await session.execute(query)).scalars().first()

    async def filter(
        self, session: AsyncSession, options: Any | None = None, **attrs
    ) -> list[T]:
        query = select(self._model).filter_by(**attrs)

        if options is not None:
            if isinstance(options, list):
                for option in options:
                    query = query.options(option)
            else:
                query = query.options(options)

        return (await session.execute(query)).scalars().all()

    async def create(
        self, session: AsyncSession, data: dict[str, Any], commit: bool = True
    ) -> T:
        obj = self._model(**data)
        session.add(obj)
        await session.flush()

        if commit:
            await session.commit()

        return obj

    async def update(
        self,
        session: AsyncSession,
        obj: T,
        data: dict[str, Any],
        commit: bool = True,
    ) -> T:
        for key, value in data.items():
            setattr(obj, key, value)
        await session.flush()

        if commit:
            await session.commit()

        return obj

    async def delete(
        self, session: AsyncSession, obj: T, commit: bool = True
    ) -> None:
        await session.delete(obj)
        await session.flush()

        if commit:
            await session.commit()
