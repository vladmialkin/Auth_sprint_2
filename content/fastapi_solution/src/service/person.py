from typing import Any, Coroutine

from elasticsearch.exceptions import NotFoundError

from ..models.models import Person
from ..repository.elasticsearch import ESRepository
from ..repository.redis import RedisRepository
from .base import Service


class PersonService(Service[Person]):
    def __init__(self, storage: ESRepository, cache: RedisRepository) -> None:
        self._storage = storage
        self._cache = cache

    async def get(self, key: str) -> Coroutine[Any, Any, Person]:
        person = await self._cache.get(slug="person/get", key=key)

        if not person:
            person = await self._storage.get(index="person", key="key")
            await self._cache.add(slug="person/get", value=person, key=key)

        return person

    async def get_all(self) -> Coroutine[Any, Any, list[Person]]:
        query: dict[str, Any] = {"query": {"bool": {"must": []}}}
        persons = await self._cache.get(slug="person/get_all")

        if not persons:
            query["query"]["bool"]["must"].append({"match_all": {}})
            persons = await self._storage.list(index="person")

            await self._cache.add(slug="person/get_all", value=persons)

        return [Person(**hit["_source"]) for hit in persons["hits"]["hits"]]

    async def search(
        self,
        limit: int,
        offset: int,
        name: str | None = None,
        role: str | None = None,
        film_title: str | None = None,
    ) -> Coroutine[Any, Any, list[Person]]:
        query: dict[str, Any] = {"query": {"bool": {"must": []}}}

        query["from"] = (offset - 1) * limit
        query["size"] = limit

        if name:
            query["query"]["bool"]["must"].append({"match": {"full_name": name}})
        if role:
            query["query"]["bool"]["must"].append(
                {"nested": {"path": "films", "query": {"match": {"films.roles": role}}}}
            )
        if film_title:
            query["query"]["bool"]["must"].append(
                {
                    "nested": {
                        "path": "films",
                        "query": {"match": {"films.title": film_title}},
                    }
                }
            )

        persons = await self._cache.get(
            slug="person/search",
            limit=limit,
            offset=offset,
            name=name,
            role=role,
            film_title=film_title,
        )

        if not persons:
            try:
                persons = await self._storage.get_all(index="person", query=query)
            except NotFoundError:
                persons = {"hits": {"hits": []}}

            await self._cache.add(
                slug="person/search",
                value=persons,
                limit=limit,
                offset=offset,
                name=name,
                role=role,
                film_title=film_title,
            )

        return [Person(**hit["_source"]) for hit in persons["hits"]["hits"]]
