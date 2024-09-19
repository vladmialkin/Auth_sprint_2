from http import HTTPStatus
import uuid
from http import HTTPStatus
import pytest

from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_elastic_film_by_id(generate_es_data_for_movies_index, es_write_data, make_get_request,
                                  del_all_redis_keys):
    films = await generate_es_data_for_movies_index(films_number=10)

    await del_all_redis_keys()
    await es_write_data(test_settings.movies_index_name, films)

    film_id = films[0]['id']

    resp = await make_get_request(f'/api/v1/films/{film_id}')
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.OK
    assert body['id'] == film_id

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_elastic_get_all_films(generate_es_data_for_movies_index, es_write_data, make_get_request,
                                     del_all_redis_keys):
    films_number = 5

    data = await generate_es_data_for_movies_index(films_number)

    await del_all_redis_keys()
    await es_write_data(test_settings.movies_index_name, data)

    resp = await make_get_request(f'/api/v1/films/')
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.OK
    assert len(body['items']) == films_number

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_redis_film_by_id(del_all_redis_keys, redis_write_data, del_es_index, make_get_request,
                                generate_redis_data):
    await del_es_index(test_settings.movies_index_name)
    await del_all_redis_keys()

    films = await generate_redis_data('film', 15)

    keys = [key for key in films.keys()]
    film_info = films[keys[0]]
    film_id = film_info['id']

    await redis_write_data(films)

    resp = await make_get_request(f'/api/v1/films/{film_id}')
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.OK
    assert body['id'] == film_id

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_redis_all_films(del_all_redis_keys, redis_write_data, del_es_index, make_get_request,
                               generate_redis_data):
    await del_es_index(test_settings.movies_index_name)
    await del_all_redis_keys()

    films_number = 15

    films = await generate_redis_data('film', films_number)

    await redis_write_data(films)

    resp = await make_get_request(f'/api/v1/films/')
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.OK
    assert len(body["items"]) == films_number

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_elastic_fake_film_by_id(del_all_redis_keys, es_write_data, del_es_index, make_get_request,
                                       generate_es_data_for_movies_index):
    await del_es_index(test_settings.movies_index_name)
    await del_all_redis_keys()

    films = await generate_es_data_for_movies_index(1)

    fake_film_id = uuid.uuid4()

    await es_write_data(test_settings.movies_index_name, films)

    resp = await make_get_request(f'/api/v1/films/{fake_film_id}')
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.NOT_FOUND
    assert body['detail'] == 'film not found'

    await del_all_redis_keys()
