import asyncio
from http import HTTPStatus
import pytest

from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_elastic_film_title_search(make_get_request, es_write_data, generate_es_data_for_movies_index,
                                         del_all_redis_keys):
    await del_all_redis_keys()

    films = await generate_es_data_for_movies_index(100)
    film_title = films[0]['title']

    await es_write_data(test_settings.movies_index_name, films)

    query_data = {'title_search': film_title}
    resp = await make_get_request(f'/api/v1/films/search/', query_data)
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.OK
    assert body['items'][0]['title'] == film_title

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_elastic_person_name_search(make_get_request, es_write_data, generate_es_data_for_persons_index,
                                          del_all_redis_keys):
    await del_all_redis_keys()

    persons = await generate_es_data_for_persons_index(10)
    person_name = persons[0]['full_name']

    await es_write_data(test_settings.persons_index_name, persons)

    query_data = {'name_search': person_name}
    resp = await make_get_request(f'/api/v1/persons/search/', query_data)
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.OK
    assert body['items'][0]['full_name'] == person_name

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_redis_film_search(del_es_index, make_get_request, del_all_redis_keys, redis_write_data,
                                 generate_redis_data):
    await del_es_index(test_settings.movies_index_name)
    await del_all_redis_keys()

    films = await generate_redis_data('film', 20)

    keys = [key for key in films.keys()]
    film_info = films[keys[0]]
    film_title = film_info['title']

    await redis_write_data(films)

    query_data = {'title_search': film_title}
    resp = await make_get_request(f'/api/v1/films/search/', query_data)
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.OK
    assert body['items'][0]['title'] == film_title

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_redis_person_search(del_all_redis_keys, redis_write_data, del_es_index, make_get_request,
                                   generate_redis_data):
    await del_es_index(test_settings.persons_index_name)
    await del_all_redis_keys()

    persons = await generate_redis_data('person', 20)

    keys = [key for key in persons.keys()]
    person_info = persons[keys[0]]
    person_name = person_info['full_name']

    await redis_write_data(persons)

    query_data = {'name_search': person_name}
    resp = await make_get_request(f'/api/v1/persons/search/', query_data)
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.OK
    assert body['items'][0]['full_name'] == person_name

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_elastic_fake_film_title_search(make_get_request, es_write_data, generate_es_data_for_movies_index,
                                              del_all_redis_keys):
    await del_all_redis_keys()

    films = await generate_es_data_for_movies_index(15)

    fake_film_title = 'Fake title'

    await es_write_data(test_settings.movies_index_name, films)

    query_data = {'title_search': fake_film_title}
    resp = await make_get_request(f'/api/v1/films/search/', query_data)
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.NOT_FOUND
    assert body['detail'] == 'film not found'

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_elastic_fake_person_name_search(make_get_request, es_write_data, generate_es_data_for_persons_index,
                                               del_all_redis_keys):
    await del_all_redis_keys()

    persons = await generate_es_data_for_persons_index(10)

    fake_person_name = 'Fake name'

    await es_write_data(test_settings.persons_index_name, persons)

    query_data = {'name_search': fake_person_name}
    resp = await make_get_request(f'/api/v1/persons/search/', query_data)
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.NOT_FOUND
    assert body['detail'] == 'person not found'

    await del_all_redis_keys()
