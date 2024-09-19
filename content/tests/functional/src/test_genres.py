from http import HTTPStatus
import uuid
from http import HTTPStatus
import pytest

from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_genre_by_id(generate_es_data_for_movies_index, es_write_data, make_get_request, del_all_redis_keys):
    films = await generate_es_data_for_movies_index(films_number=10)

    await del_all_redis_keys()
    await es_write_data(test_settings.movies_index_name, films)

    genre_id = films[0]['genres'][0]['id']

    resp = await make_get_request(f'/api/v1/genres/{genre_id}')
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.OK
    assert body['id'] == genre_id

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_get_all_genres(generate_es_data_for_movies_index, es_write_data, make_get_request, del_all_redis_keys):
    films_number = 5

    data = await generate_es_data_for_movies_index(films_number)

    await del_all_redis_keys()
    await es_write_data(test_settings.movies_index_name, data)

    resp = await make_get_request(f'/api/v1/genres/')
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.OK
    assert len(body['items']) == films_number

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_redis_genre_by_id(del_all_redis_keys, redis_write_data, del_es_index, make_get_request,
                                 generate_redis_data):
    await del_es_index(test_settings.movies_index_name)
    await del_all_redis_keys()

    genres = await generate_redis_data('genre', 1)

    keys = [key for key in genres.keys()]
    genre_info = genres[keys[0]]
    genre_id = genre_info['id']

    await redis_write_data(genres)

    resp = await make_get_request(f'/api/v1/genres/{genre_id}')
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.OK
    assert body['items'][0]['genres']['id'] == genre_id

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_elastic_fake_genre_by_id(del_all_redis_keys, es_write_data, del_es_index, make_get_request,
                                        generate_es_data_for_movies_index):
    await del_es_index(test_settings.movies_index_name)
    await del_all_redis_keys()

    films = await generate_es_data_for_movies_index(1)

    fake_genre_id = uuid.uuid4()

    await es_write_data(test_settings.movies_index_name, films)

    resp = await make_get_request(f'/api/v1/genres/{fake_genre_id}')
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.NOT_FOUND
    assert body['detail'] == 'genre not found'

    await del_all_redis_keys()
