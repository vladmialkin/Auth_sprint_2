import logging
from functools import lru_cache

import backoff
from elasticsearch import AsyncElasticsearch, ConnectionError, NotFoundError
from fastapi import Depends
from pydantic import ValidationError
from redis import ConnectionError as RedisConError
from redis.asyncio import Redis

from ..core.config import settings
from ..db.elastic import get_elastic
from ..db.redis import get_redis
from ..models.models import Person

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index = 'persons'
        self.log = logging.getLogger('main')

    async def get_by_id(self, person_id: str) -> Person | None:
        person = await self._person_from_cache(person_id)

        if not person:
            person = await self._get_from_elastic_by_id(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def get_all_persons(self) -> list[Person] | None:
        persons = await self._all_persons_from_cache()

        if not persons:
            persons = await self._get_from_elastic_all_persons()
            if not persons:
                return None
            await self._put_all_persons_to_cache(persons)

        return persons

    async def get_by_search(self, search_text) -> list[Person] | None:
        persons = await self._all_person_from_cache_by_search(search_text)

        if not persons:
            persons = await self._get_from_elastic_by_search(search_text)
            if not persons:
                return None
            await self._put_all_persons_to_cache(persons)

        return persons

    @backoff.on_exception(backoff.expo, ConnectionError, max_tries=settings.MAX_TRIES)
    async def _get_from_elastic_by_id(self, person_id: str) -> Person | None:
        try:
            response = await self.elastic.get(index="persons", id=person_id)
            self.log.info(f'elastic: 1')
        except NotFoundError:
            self.log.info(f'elastic: 0')
            return None
        return Person(**response["_source"])

    @backoff.on_exception(backoff.expo, ConnectionError, max_tries=settings.MAX_TRIES)
    async def _get_from_elastic_all_persons(self) -> list[Person] | None:
        try:
            response = await self.elastic.search(index="persons", size=1000, body={
                "query": {
                    "match_all": {}
                }
            })
            persons_list = [Person(**hit["_source"]) for hit in response['hits']['hits']]
            self.log.info(f'elastic: {len(persons_list)}')
        except NotFoundError:
            self.log.info(f'elastic: 0')
            return None
        return persons_list

    @backoff.on_exception(backoff.expo, ConnectionError, max_tries=settings.MAX_TRIES)
    async def _get_from_elastic_by_search(self, search_text) -> list[Person] | None:
        try:
            docs = await self.elastic.search(index=self.index, size=1000, query={
                "match": {
                    "full_name": {
                        "query": search_text,
                        "fuzziness": "auto"
                    }
                }
            })
            persons_list = [Person(**dict_['_source']) for dict_ in docs['hits']['hits']]
            self.log.info(f'elastic: {len(persons_list)}')
        except NotFoundError:
            return None
        return persons_list

    @backoff.on_exception(backoff.expo, ConnectionError, max_tries=settings.MAX_TRIES)
    async def _person_from_cache(self, person_id: str) -> Person | None:
        data = await self.redis.get(f"person:{person_id}")
        if not data:
            self.log.info(f"redis: 0")
            return None

        person = Person.parse_raw(data)
        self.log.info(f"redis: {len(data)}")
        return person

    @backoff.on_exception(backoff.expo, RedisConError, max_tries=settings.MAX_TRIES)
    async def _all_persons_from_cache(self):
        keys = await self.redis.keys('person:*')
        self.log.info(f'redis keys: {len(keys)}')

        if not keys:
            return None

        data = await self.redis.mget(keys)

        persons = [Person.parse_raw(item) for item in data if item is not None]
        self.log.info(f"redis: get {len(persons)} persons")
        return persons if persons else None

    @backoff.on_exception(backoff.expo, RedisConError, max_tries=settings.MAX_TRIES)
    async def _all_person_from_cache_by_search(self, search_text: str):
        keys = await self.redis.keys(f"person:*")
        self.log.info(f'redis_keys: {len(keys)}')

        if not keys:
            return None

        data = await self.redis.mget(keys)
        self.log.info(f'redis data: {len(data)}')

        person_list = []
        for item in data:
            if item is not None:
                try:
                    person = Person.parse_raw(item)
                    if search_text in person.full_name:
                        person_list.append(person)
                except ValidationError as e:
                    self.log.error(f'Ошибка при парсинге персон из данных: {item}. Ошибка: {e}')
        self.log.info(f'redis: get {len(person_list)} person')
        return person_list

    @backoff.on_exception(backoff.expo, RedisConError, max_tries=settings.MAX_TRIES)
    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(f"person:{person.id}", person.json(), FILM_CACHE_EXPIRE_IN_SECONDS)
        self.log.info(f'set 1 person to redis')

    @backoff.on_exception(backoff.expo, RedisConError, max_tries=settings.MAX_TRIES)
    async def _put_all_persons_to_cache(self, persons: list[Person]):
        data = {f"person:{person.id}": person.json() for person in persons}
        await self.redis.mset(data)
        self.log.info(f'set {len(data)} persons to redis')


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
