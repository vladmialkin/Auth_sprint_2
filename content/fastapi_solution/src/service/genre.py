from typing import Any, Coroutine

from elasticsearch.exceptions import NotFoundError

from ..models.models import Genre
from ..repository.elasticsearch import ESRepository
from ..repository.redis import RedisRepository
from ..service.base import Service


class GenreService(Service[Genre]):
    def __init__(self, storage: ESRepository, cache: RedisRepository) -> None:
        self._storage = storage
        self._cache = cache

    async def get(self, key: str) -> Coroutine[Any, Any, Genre]:
        genre = await self._cache.get(slug="genre/get", key=key)

        if not genre:
            genre = await self._storage.get(index="genre", key="key")
            await self._cache.add(slug="genre/get", value=genre, key=key)

        return genre

    async def get_all(self) -> Coroutine[Any, Any, list[Genre]]:
        query: dict[str, Any] = {"query": {"bool": {"must": []}}}
        genres = await self._cache.get(slug="genre/get_all")

        if not genres:
            query["query"]["bool"]["must"].append({"match_all": {}})

            try:
                genres = await self._storage.get_all(index="genre")
            except NotFoundError:
                genres = {"hits": {"hits": []}}

            await self._cache.add(slug="genre/get_all", value=genres)

        return [Genre(**hit["_source"]) for hit in genres["hits"]["hits"]]
