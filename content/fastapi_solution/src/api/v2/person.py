from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Query, Path

from ...repository.elasticsearch import ESRepository
from ...repository.redis import RedisRepository
from ...service.person import PersonService
from ..deps import ESConnection, RedisConnection
from ..v2.schemas.person import PersonSchema

router = APIRouter()


@router.get(
    "/search",
    summary='Полнотекстовый поиск по персонам',
    description='Поиск по персонам',
    response_description='Информация по персоне'
)
async def search(
        es_conn: ESConnection,
        redis_conn: RedisConnection,
        name: str | None = Query(
            None, title="Имя для поиска",
            description="Имя персоны для полнотекстового поиска."
        ),
        role: str | None = Query(
            None, title="Роль для поиска",
            description="Роль персоны для полнотекстового поиска."
        ),
        film_title: str | None = Query(
            None, title="Имя фильма для поиска",
            description="Имя фильма для полнотекстового поиска."
        ),
        page_size: Annotated[int, Query(description='Количество элементов страницы', ge=1)] = 1,
        page_number: Annotated[int, Query(description='Номер страницы', ge=1)] = 10,
) -> list[PersonSchema]:
    """
    Поиск персоны по имени.
    Возвращает пагинированный список персон по заданному имени.
    """
    service = PersonService(
        ESRepository(es_conn=es_conn),
        RedisRepository(redis_conn=redis_conn, ttl=60 * 5),  # 5 minutes
    )

    return await service.search(page_size, page_number, name=name, role=role, film_title=film_title)


@router.get(
    "/{person_id}",
    response_model=PersonSchema,
    summary="Поиск персоны по id",
    description="Получение информации по id",
    response_description="Полная информация по персоне",
)
async def details(
        es_conn: ESConnection,
        redis_conn: RedisConnection,
        person_id: str = Path(
            ...,
            title="Идентификатор персоны",
            description="Уникальный идентификатор персоны для получения его деталей.",
        ),
) -> PersonSchema:
    """
    Получить информацию о персоне по ее идентификатору.

    - **person_id**: Уникальный идентификатор персоны (обязательный параметр пути).

    Возвращает информацию о персоне в случае успеха,
    """
    service = PersonService(
        ESRepository(es_conn=es_conn),
        RedisRepository(redis_conn=redis_conn, ttl=60 * 5),  # 5 minutes
    )

    person = await service.get(key=person_id)

    if not person:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Person not found")

    return person


@router.get(
    "",
    summary="Список персон",
    description="Список персон с пагинацией",
    response_description="Информация по персонам",
)
async def get_all(
        es_conn: ESConnection,
        redis_conn: RedisConnection
) -> list[PersonSchema]:
    """
    Получить список персон с возможностью сортировки по ролям.
    Возвращает пагинированный список персон.
    """
    service = PersonService(
        ESRepository(es_conn=es_conn),
        RedisRepository(redis_conn=redis_conn, ttl=60 * 5),  # 5 minutes
    )

    return await service.get_all()
