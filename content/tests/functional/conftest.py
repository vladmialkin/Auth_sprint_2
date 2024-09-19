import asyncio
import json
import uuid
from datetime import datetime
from random import randint, choice

import pytest_asyncio
from faker import Faker
from aiohttp import ClientSession, ClientResponse
from aiohttp.web_exceptions import HTTPNotFound
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from redis.asyncio import Redis

from .settings import test_settings

fake = Faker()

genres = ['Action', 'Adventure', 'Drama', 'Romance', 'Thriller', 'Comedy', 'Documentary', 'Mystery', 'Fantasy']
roles = ['actor', 'director', 'writer']


async def generate_films_info(films_number: int) -> list[dict]:
    bulk_query: list[dict] = []

    films = [
        {
            'id': str(uuid.uuid4()),
            'title': fake.sentence(nb_words=randint(1, 5)),
            'imdb_rating': randint(1, 10),
            'creation_date': str(datetime.now()),
            'genres': [{'id': str(uuid.uuid4()), 'name': choice(genres), 'description': None}],
            'description': None,
            'file_path': None,
            'directors': [],
            'actors': [
                {'id': str(uuid.uuid4()), 'name': fake.name()},
                {'id': str(uuid.uuid4()), 'name': fake.name()}
            ],
            'writers': [
                {'id': str(uuid.uuid4()), 'name': fake.name()},
                {'id': str(uuid.uuid4()), 'name': fake.name()}
            ],
        } for _ in range(films_number)
    ]

    for film in films:
        dict_ = {
            'actors_names': [dict_['name'] for dict_ in film['actors']] if film['actors'] is not None else [],
            'writers_names': [dict_['name'] for dict_ in film['writers']] if film['writers'] is not None else [],
            'directors_names': [dict_['name'] for dict_ in film['directors']] if film['directors'] is not None else []
        }
        dict_.update(film)
        bulk_query.append(dict_)

    return bulk_query


async def generate_persons_info(persons_number: int) -> list[dict]:
    persons = [
        {
            'id': str(uuid.uuid4()),
            'full_name': fake.name(),
            'films': [
                {'id': str(uuid.uuid4()), 'roles': [choice(roles)]},
                {'id': str(uuid.uuid4()), 'roles': [choice(roles)]}
            ]
        } for _ in range(persons_number)
    ]
    return persons


async def generate_genres_info() -> list[dict]:
    genres_list = [
        {
            'id': str(uuid.uuid4()),
            'name': genre,
            'description': fake.text(100)
        } for genre in genres
    ]
    return genres_list


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def es_client():
    es_client = AsyncElasticsearch(hosts=f'http://{test_settings.es_host}:{test_settings.es_port}',
                                   verify_certs=False)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(scope='session')
async def redis_client():
    redis_client = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    yield redis_client
    await redis_client.aclose()


@pytest_asyncio.fixture(scope='session')
async def aiohttp_client():
    session = ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture()
async def del_all_redis_keys(redis_client):
    async def inner(key_name: str = '*:*') -> None:
        keys = [key async for key in redis_client.scan_iter(key_name)]

        if not len(keys) == 0:
            await redis_client.delete(*keys)

    return inner


@pytest_asyncio.fixture()
async def del_es_index(es_client):
    async def inner(index_name: str) -> None:
        if await es_client.indices.exists(index=index_name):
            await es_client.indices.delete(index=index_name)
    return inner


@pytest_asyncio.fixture()
async def generate_es_data_for_movies_index():
    async def inner(films_number: int) -> list[dict]:
        bulk_query: list[dict] = []

        films = await generate_films_info(films_number)

        for film in films:
            dict_ = {
                '_index': test_settings.movies_index_name,
                '_id': film['id']
            }
            dict_.update(film)
            bulk_query.append(dict_)

        return bulk_query

    return inner


@pytest_asyncio.fixture()
async def del_es_index(es_client):
    async def inner(index_name: str) -> None:
        if await es_client.indices.exists(index=index_name):
            await es_client.indices.delete(index=index_name)

    return inner


@pytest_asyncio.fixture()
async def generate_es_data_for_persons_index():
    async def inner(persons_number: int) -> list[dict]:
        bulk_query: list[dict] = []

        persons = await generate_persons_info(persons_number)

        for person in persons:
            dict_ = {
                '_index': test_settings.persons_index_name,
                '_id': person['id']
            }
            dict_.update(person)
            bulk_query.append(dict_)

        return bulk_query

    return inner


@pytest_asyncio.fixture()
async def generate_redis_data():
    async def inner(key_prefix: str, items_number: int) -> dict[str, dict]:
        switcher = {
            'film': generate_films_info,
            'person': generate_persons_info,
            'genre': generate_genres_info
        }
        generate_info_func = switcher.get(key_prefix, None)

        data: list[dict] = await generate_info_func(items_number)
        dict_ = {f'{key_prefix}:{dict_["id"]}': dict_ for dict_ in data}

        return dict_

    return inner


@pytest_asyncio.fixture()
async def es_write_data(es_client):
    async def inner(index_name: str, data: list[dict]):
        if await es_client.indices.exists(index=index_name):
            await es_client.indices.delete(index=index_name)
        await es_client.indices.create(index=index_name)

        updated, errors = await async_bulk(client=es_client, actions=data, refresh='wait_for')

        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


@pytest_asyncio.fixture()
async def redis_write_data(redis_client):
    async def inner(data: dict[str, dict]) -> None:
        data = {k: json.dumps(v) for k, v in data.items()}

        if len(data) == 1:
            key, value = data.popitem()
            await redis_client.set(key, value)
        else:
            await redis_client.mset(data)

    return inner


@pytest_asyncio.fixture()
async def make_get_request(aiohttp_client):
    async def inner(url: str, params: dict = None) -> ClientResponse:
        url = test_settings.service_url + url
        response = None

        try:
            response = await aiohttp_client.get(url, params=params)
            status = response.status
            if status == HTTPNotFound.status_code:
                print(f'Status: {status} Not Found')
        except OSError as e:
            print(f'Cannot connect to host {e}')

        return response

    return inner
