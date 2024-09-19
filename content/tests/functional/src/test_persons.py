from http import HTTPStatus
import uuid
from http import HTTPStatus
import pytest

from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_elastic_person_by_id(es_write_data, make_get_request, generate_es_data_for_persons_index,
                                    del_all_redis_keys):
    await del_all_redis_keys()

    persons = await generate_es_data_for_persons_index(3)
    person_info = persons[0]
    person_id = person_info['id']
    person_full_name = person_info['full_name']

    await es_write_data(test_settings.persons_index_name, persons)

    resp = await make_get_request(f'/api/v1/persons/{person_id}')
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.OK
    assert body['id'] == person_id
    assert body['full_name'] == person_full_name

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_elastic_all_persons(generate_es_data_for_persons_index, es_write_data, make_get_request,
                                   del_all_redis_keys):
    await del_all_redis_keys()

    persons_number = 5

    data = await generate_es_data_for_persons_index(persons_number)

    await es_write_data(test_settings.persons_index_name, data)

    resp = await make_get_request(f'/api/v1/persons/')
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.OK
    assert len(body['items']) == persons_number

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_redis_person_by_id(del_all_redis_keys, redis_write_data, del_es_index, make_get_request,
                                  generate_redis_data):
    await del_es_index(test_settings.persons_index_name)
    await del_all_redis_keys()

    persons = await generate_redis_data('person', 3)

    keys = [key for key in persons.keys()]
    person_info = persons[keys[0]]
    person_id = person_info['id']
    person_name = person_info['full_name']

    await redis_write_data(persons)

    resp = await make_get_request(f'/api/v1/persons/{person_id}')
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.OK
    assert body['id'] == person_id
    assert body['full_name'] == person_name

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_redis_all_persons(del_all_redis_keys, redis_write_data, del_es_index, make_get_request,
                                 generate_redis_data):
    await del_es_index(test_settings.persons_index_name)
    await del_all_redis_keys()

    persons_number = 5

    data = await generate_redis_data('person', persons_number)

    await redis_write_data(data)

    resp = await make_get_request(f'/api/v1/persons/')
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.OK
    assert len(body['items']) == persons_number

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_elastic_fake_person_by_id(es_write_data, make_get_request, generate_es_data_for_persons_index,
                                         del_all_redis_keys):
    await del_all_redis_keys()

    persons = await generate_es_data_for_persons_index(3)
    fake_person_id = uuid.uuid4()

    await es_write_data(test_settings.persons_index_name, persons)

    resp = await make_get_request(f'/api/v1/persons/{fake_person_id}')
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.NOT_FOUND
    assert body['detail'] == 'Person not found'

    await del_all_redis_keys()


@pytest.mark.asyncio
async def test_redis_fake_person_by_id(del_all_redis_keys, redis_write_data, del_es_index, make_get_request,
                                       generate_redis_data):
    await del_es_index(test_settings.persons_index_name)
    await del_all_redis_keys()

    persons = await generate_redis_data('person', 3)

    fake_person_id = uuid.uuid4()

    await redis_write_data(persons)

    resp = await make_get_request(f'/api/v1/persons/{fake_person_id}')
    body = await resp.json()
    status = resp.status

    assert status == HTTPStatus.NOT_FOUND
    assert body['detail'] == 'Person not found'

    await del_all_redis_keys()
