from abc import ABC, abstractmethod
from typing import Coroutine


class Service[T](ABC):
    _storage = None
    _cache = None

    @abstractmethod
    async def get(self, key: str) -> Coroutine[None, None, T]:
        """Получить объект по ключу."""
