import logging
from datetime import datetime as dt
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
from ..models.models import FilmRequest

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index = "movies"
        self.log = logging.getLogger("main")

    async def get_by_id(self, film_id: str) -> FilmRequest | None:
        film = await self._film_from_cache(film_id)

        if not film:
            film = await self._get_from_elastic_by_id(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def get_all_films(self) -> list[FilmRequest] | None:
        films = await self._all_films_from_cache()

        if not films:
            films = await self._get_from_elastic_all_films()
            if not films:
                return None
            await self._put_all_films_to_cache(films)

        return films


    async def get_by_search(self, search_text) -> list[FilmRequest] | None:
        films = await self._get_from_elastic_by_search(search_text)

        if not films:
            films = await self._get_from_elastic_by_search(search_text)
            if not films:
                return None
            await self._put_all_films_to_cache(films)

        return films

    @backoff.on_exception(backoff.expo, ConnectionError, max_tries=settings.MAX_TRIES)
    async def _get_from_elastic_by_id(self, film_id: str) -> FilmRequest | None:
        try:
            doc = await self.elastic.get(index=self.index, id=film_id)
            self.log.info("elastic: 1")
        except NotFoundError:
            self.log.info("elastic: 0")
            return None
        return FilmRequest(**doc["_source"])

    @backoff.on_exception(backoff.expo, ConnectionError, max_tries=settings.MAX_TRIES)
    async def _get_from_elastic_all_films(self) -> list[FilmRequest] | None:
        try:
            docs = await self.elastic.search(
                index=self.index, size=1000, query={"match_all": {}}
            )
            movies_list = [
                FilmRequest(
                    id=dict_["_source"]["id"],
                    title=dict_["_source"]["title"],
                    imdb_rating=(
                        dict_["_source"]["imdb_rating"]
                        if dict_["_source"]["imdb_rating"] is not None
                        else 0
                    ),
                    creation_date=(
                        dict_["_source"]["creation_date"]
                        if dict_["_source"]["creation_date"] is not None
                        else str(dt.min)
                    ),
                    genres=dict_["_source"]["genres"],
                    description=dict_["_source"]["description"],
                    file_path=dict_["_source"]["file_path"],
                    directors_names=dict_["_source"]["directors_names"],
                    actors_names=dict_["_source"]["actors_names"],
                    writers_names=dict_["_source"]["writers_names"],
                    directors=dict_["_source"]["directors"],
                    actors=dict_["_source"]["actors"],
                    writers=dict_["_source"]["writers"],
                )
                for dict_ in docs["hits"]["hits"]
            ]
            self.log.info(f'elastic: {len(movies_list)}')
        except NotFoundError:
            self.log.info(f'elastic: 0')
            return None
        return movies_list

    @backoff.on_exception(backoff.expo, ConnectionError, max_tries=settings.MAX_TRIES)
    async def _get_from_elastic_by_search(
        self, search_text
    ) -> list[FilmRequest] | None:
        try:
            docs = await self.elastic.search(
                index=self.index,
                size=1000,
                query={"match": {"title": {"query": search_text, "fuzziness": "auto"}}},
            )
            movies_list = [
                FilmRequest(**dict_["_source"]) for dict_ in docs["hits"]["hits"]
            ]
        except NotFoundError:
            return None
        return movies_list

    @backoff.on_exception(backoff.expo, RedisConError, max_tries=settings.MAX_TRIES)
    async def _film_from_cache(self, film_id: str) -> FilmRequest | None:
        data = await self.redis.get(f"film:{film_id}")
        # self.log.info(f"redis: {data}")
        if not data:
            self.log.info("redis: 0")
            return None

        film = FilmRequest.parse_raw(data)
        self.log.info(f"redis: get {film.id} film")
        return film

    @backoff.on_exception(backoff.expo, RedisConError, max_tries=settings.MAX_TRIES)
    async def _all_films_from_cache(self):
        keys = await self.redis.keys(f"film:*")
        self.log.info(f'redis_keys: {len(keys)}')

        if not keys:
            self.log.info("redis: 0")
            return None

        data = await self.redis.mget(keys)

        films_list = []
        for item in data:
            if item is not None:
                try:
                    film = FilmRequest.parse_raw(item)
                    films_list.append(film)
                except ValidationError as e:
                    self.log.error(
                        f"Ошибка при парсинге фильмов из данных: {item}. Ошибка: {e}"
                    )
        self.log.info(f"redis: get {len(films_list)} films")
        return films_list

    @backoff.on_exception(backoff.expo, RedisConError, max_tries=settings.MAX_TRIES)
    async def _all_films_from_cache_by_search(self, search_text: str):
        keys = await self.redis.keys(f"film:*")
        self.log.info(f'redis_keys: {len(keys)}')

        if not keys:
            return None

        data = await self.redis.mget(keys)
        self.log.info(f'redis: {len(data)}')

        films_list = []
        for item in data:
            if item is not None:
                try:
                    film = FilmRequest.parse_raw(item)
                    if search_text in film.title:
                        films_list.append(film)
                except ValidationError as e:
                    self.log.error(f'Ошибка при парсинге фильмов из данных: {item}. Ошибка: {e}')
        self.log.info(f'redis: get {len(films_list)} films')
        return films_list

    @backoff.on_exception(backoff.expo, RedisConError, max_tries=settings.MAX_TRIES)
    async def _put_film_to_cache(self, film: FilmRequest):
        await self.redis.set(
            f"film:{film.id}", film.json(), FILM_CACHE_EXPIRE_IN_SECONDS
        )
        self.log.info(f'set 1 film to redis')

    @backoff.on_exception(backoff.expo, RedisConError, max_tries=settings.MAX_TRIES)
    async def _put_all_films_to_cache(self, films):
        data = {f"film:{film.id}": film.json() for film in films}
        await self.redis.mset(data)
        self.log.info(f'set {len(data)} films to redis')


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
