from abc import ABC, abstractmethod
from typing import Any, Coroutine


class Repository(ABC):
    @abstractmethod
    async def get(self, *args, **kwargs) -> Coroutine[Any, Any, Any]:
        """Получить объект по ключу"""

        raise NotImplementedError

    @abstractmethod
    async def add(self, *args, **kwargs) -> Coroutine[Any, Any, None]:
        """Добавить объект"""

        raise NotImplementedError

    @abstractmethod
    async def get_all(self, *args, **kwargs) -> Coroutine[Any, Any, list[Any]]:
        """Получить список объектов"""

        raise NotImplementedError


class InMemoryRepository(ABC):
    @classmethod
    def _compute_key(cls, **kwargs) -> str:
        """Сгенерировать ключ для хранилища"""
        return f"".join(f"{key}={value}" for key, value in sorted(kwargs.items()))

    @abstractmethod
    async def get(self, slug: str, *args, **kwargs) -> Coroutine[Any, Any, Any]:
        """Получить объект по ключу"""

        raise NotImplementedError

    @abstractmethod
    async def add(self, slug: str, *args, **kwargs) -> Coroutine[Any, Any, None]:
        """Добавить объект"""

        raise NotImplementedError
