from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, status, Query, Path

from ...repository.elasticsearch import ESRepository
from ...repository.redis import RedisRepository
from ...service.film import FilmService
from ..deps import ESConnection, RedisConnection, UserData
from ..v2.schemas.film import FilmSchema

router = APIRouter(dependencies=[UserData])


@router.get(
    "",
    summary="Список фильмов",
    description="Список фильмов с пагинацией, фильтрацией по жанрам и сортировкой по названию или рейтингу",
    response_description="Информация по фильмам",
)
async def get_all(
        es_conn: ESConnection,
        redis_conn: RedisConnection,
        page_size: Annotated[int, Query(description='Количество элементов страницы', ge=1)] = 1,
        page_number: Annotated[int, Query(description='Номер страницы', ge=1)] = 10,
        sort: Annotated[
            Literal["imdb_rating", "creation_date"],
            Query(description="Указывает поле для сортировки фильмов.", )
        ] = "imdb_rating",
        genre: str | None = Query(
            None,
            title="Жанр",
            description="Фильтрует фильмы по жанру."
        ),
) -> list[FilmSchema]:
    """
    Получить список фильмов с возможностью фильтрации и сортировки.
    Возвращает пагинированный список фильмов.
    - **es_conn**: Подключение к Elastic
    - **redis_conn**: Подключение к Redis
    - **page_size**: Количество элементов на странице
    - **page_number**: Номер мтраницы
    - **sort**: Сортировка
    - **genre**: Жанр
    """
    service = FilmService(
        storage=ESRepository(es_conn),
        cache=RedisRepository(redis_conn, 60 * 5),
    )
    return await service.get_all(sort, genre, page_size, page_number)


@router.get(
    "/search",
    response_model=list[FilmSchema],
    summary="Полнотекстовый поиск по фильмам",
    description="Поиск по фильмам",
    response_description="Информация по фильмам",
)
async def search(
        es_conn: ESConnection,
        redis_conn: RedisConnection,
        page_size: Annotated[int, Query(description='Количество элементов страницы', ge=1)] = 1,
        page_number: Annotated[int, Query(description='Номер страницы', ge=1)] = 10,
        title: str = Query(
            None,
            title="Заголовок фильма для поиска",
            description="Заголовок фильма для поиска"
        ),
) -> list[FilmSchema]:
    """
    Возвращает пагинированный список фильмов по заданному названию.
    - **es_conn**: Подключение к Elastic
    - **redis_conn**: Подключение к Redis
    - **page_size**: Количество элементов на странице
    - **page_number**: Номер мтраницы
    - **title**: Заголовок фильма для поиска
    """
    service = FilmService(
        storage=ESRepository(es_conn),
        cache=RedisRepository(redis_conn, 60 * 5),
    )
    return await service.search(title, page_size, page_number)


@router.get(
    "/{film_id}",
    response_model=FilmSchema,
    summary="Поиск фильма по id",
    description="Получение информации по id",
    response_description="Полная информация по фильму",
)
async def details(
        es_conn: ESConnection,
        redis_conn: RedisConnection,
        film_id: str = Path(
            ...,
            title="Идентификатор фильма",
            description="Уникальный идентификатор фильма для получения его деталей.",
        ),
) -> FilmSchema:
    service = FilmService(
        storage=ESRepository(es_conn),
        cache=RedisRepository(redis_conn, 60 * 5),
    )
    """
    Получить полную информацию о фильме по его идентификатору.

    - **film_id**: Уникальный идентификатор фильма (обязательный параметр пути).
    - **film_service**: Сервис для получения данных о фильмах (зависимость).

    Возвращает полную информацию о фильме в случае успеха,
    """
    film = await service.get(key=film_id)

    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Film not found"
        )

    return film
