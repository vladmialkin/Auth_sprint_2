from fastapi import APIRouter, HTTPException, status, Path

from ...repository.elasticsearch import ESRepository
from ...repository.redis import RedisRepository
from ...service.genre import GenreService
from ..deps import ESConnection, RedisConnection, UserData
from ..v2.schemas.genre import GenreSchema

router = APIRouter(dependencies=[UserData])


@router.get(
    "/{genre_id}",
    response_model=GenreSchema,
    summary="Поиск жанра по id",
    description="Получение информации по id",
    response_description="Полная информация по жанру",
)
async def details(
        es_conn: ESConnection,
        redis_conn: RedisConnection,
        genre_id: str = Path(
            ...,
            title="Идентификатор жанров",
            description="Уникальный идентификатор жанра для получения его деталей.",
        ),
) -> GenreSchema:
    """
    Получить информацию о жанре по его идентификатору.

    - **genre_id**: Уникальный идентификатор жанра (обязательный параметр пути).

    Возвращает полную информацию о жанре в случае успеха,
    """
    service = GenreService(
        storage=ESRepository(es_conn),
        cache=RedisRepository(redis_conn, ttl=60 * 5),
    )

    genre = await service.get(key=genre_id)

    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found"
        )

    return genre


@router.get(
    "",
    summary="Список жанров",
    description="Список жанров с пагинацией",
    response_description="Информация по жанрам",
)
async def get_all(
        es_conn: ESConnection,
        redis_conn: RedisConnection
) -> list[GenreSchema]:
    """
    Получить список всех жанров.
    Возвращает пагинированный список жанров.
    """
    service = GenreService(
        storage=ESRepository(es_conn),
        cache=RedisRepository(redis_conn, ttl=60 * 5),
    )

    return await service.get_all()
