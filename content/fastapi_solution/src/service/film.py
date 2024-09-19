from logging import getLogger
from typing import Any, Coroutine

from elasticsearch.exceptions import NotFoundError

from ..models.models import FilmRequest, Genre
from ..repository.elasticsearch import ESRepository
from ..repository.redis import RedisRepository
from ..service.base import Service

logger = getLogger(__name__)


class FilmService(Service[FilmRequest]):
    def __init__(self, storage: ESRepository, cache: RedisRepository) -> None:
        self._storage = storage
        self._cache = cache

    async def get(self, key: str) -> Coroutine[Any, Any, FilmRequest]:
        film = await self._cache.get(slug="film/get", key=key)

        if not film:
            film = await self._storage.get(index="film", key=key)
            await self._cache.add(slug="film/get", value=film, key=key)

        return film

    async def get_all(
        self,
        sort: str | None = None,
        genre: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Coroutine[Any, Any, list[FilmRequest]]:
        sort = self._assemble_sort_query(sort) if sort else None
        genre = await self._assemble_genre_query(genre) if genre else None
        films = await self._cache.get(
            slug="film/get_all", sort=sort, genre=genre, limit=limit, offset=offset
        )

        if films is None:
            doc = await self._storage.get_all(
                index="film",
                limit=limit,
                offset=offset,
                sort=sort,
                query=genre,
            )

            films = [FilmRequest(**hit["_source"]) for hit in doc["hits"]["hits"]]

            await self._cache.add(
                slug="film/get_all",
                value=films,
                sort=sort,
                genre=genre,
                limit=limit,
                offset=offset,
            )

        return films

    def _assemble_sort_query(self, sort: str) -> dict[str, Any]:
        if sort.startswith("-"):
            sort_key = sort[1:]
            order = "asc"
            mode = "min"
        else:
            sort_key = sort
            order = "desc"
            mode = "max"

        return {sort_key: {"order": order, "mode": mode}}

    async def _assemble_genre_query(
        self, genre: str
    ) -> Coroutine[Any, Any, dict[str, Any] | None]:
        genre = await self._storage.get(index="genres", key=genre)

        if not genre:
            return None

        genre_name = Genre(**genre["_source"]).name

        return {"bool": {"filter": {"term": {"genre": genre_name}}}}

    async def search(
        self, title: str, limit: int, offset: int
    ) -> Coroutine[Any, Any, list[FilmRequest]]:
        films = await self._cache.get(
            slug="film/search", title=title, limit=limit, offset=offset
        )

        if not films:
            try:
                films = await self._storage.get_all(
                    index="films",
                    query={"match": {"title": title}},
                    limit=limit,
                    offset=offset,
                )
            except NotFoundError:
                films = {"hits": {"hits": []}}

            await self._cache.add(
                slug="film/search", value=films, title=title, limit=limit, offset=offset
            )

        return [FilmRequest(**hit["_source"]) for hit in films["hits"]["hits"]]
