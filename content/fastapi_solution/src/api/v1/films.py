import logging
from http import HTTPStatus
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi_pagination import Page, paginate

from ...services.film_service import FilmService, get_film_service
from ...models.models import FilmFullResponse, FilmResponse

router = APIRouter()

log = logging.getLogger("main")


@router.get(
    "/{film_id}",
    response_model=FilmFullResponse,
    summary="Поиск фильма по id",
    description="Получение информации по id",
    response_description="Полная информация по фильму",
)
async def film_details(
        film_id: str = Path(
            ...,
            title="Идентификатор фильма",
            description="Уникальный идентификатор фильма для получения его деталей.",
        ),
        film_service: FilmService = Depends(get_film_service),
) -> FilmFullResponse:
    """
    Получить полную информацию о фильме по его идентификатору.

    - **film_id**: Уникальный идентификатор фильма (обязательный параметр пути).
    - **film_service**: Сервис для получения данных о фильмах (зависимость).

    Возвращает полную информацию о фильме в случае успеха,
    иначе вызывает HTTPException с кодом 404, если фильм не найден.
    """
    log.info(f"Получение информации по фильму с id: {film_id} ...")
    film = await film_service.get_by_id(film_id)

    if not film:
        log.info(f"Фильм с id: {film_id} не найден.")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    log.info(f"Информация по фильму с id: {film_id} получена.")
    return FilmFullResponse(
        id=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        creation_date=film.creation_date,
        genres=film.genres,
        actors=film.actors,
        directors=film.directors,
        writers=film.writers,
    )


@router.get(
    "",
    summary="Список фильмов",
    description="Список фильмов с пагинацией, фильтрацией по жанрам и сортировкой по названию или рейтингу",
    response_description="Информация по фильмам",
)
async def films(
        film_service: FilmService = Depends(get_film_service),
        rating: Optional[float] = Query(
            None,
            title="Минимальный рейтинг",
            description="Фильтрует фильмы по минимальному рейтингу.",
        ),
        genre: Optional[str] = Query(
            None, title="Жанр", description="Фильтрует фильмы по жанру."
        ),
        creation_date: Optional[str] = Query(
            None, title="Дата создания", description="Фильтрует фильмы по дате создания."
        ),
        sort_by: Optional[Literal["imdb_rating", "creation_date"]] = Query(
            None,
            title="Поле сортировки",
            description="Указывает поле для сортировки фильмов.",
        ),
) -> Page[FilmResponse]:
    """
    Получить список фильмов с возможностью фильтрации и сортировки.

    - **film_service**: Сервис для получения данных о фильмах (зависимость).
    - **rating**: Минимальный рейтинг для фильтрации фильмов (необязательный параметр).
    - **genre**: Жанр для фильтрации фильмов (необязательный параметр).
    - **creation_date**: Дата создания для фильтрации фильмов (необязательный параметр).
    - **sort_by**: Поле для сортировки списка фильмов (необязательный параметр,
      может быть 'imdb_rating' или 'creation_date').

    Возвращает пагинированный список фильмов.
    В случае, если фильмы не найдены, вызывает HTTPException с кодом 404.
    """
    films_list = await film_service.get_all_films()

    if not films_list:
        log.info("Фильмы не найдены.")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    # Фильтрация по рейтингу.
    if rating is not None:
        films_list = [film for film in films_list if film.imdb_rating >= rating]

    # Фильтрация по жанру.
    if genre is not None:
        films_list = [
            film
            for film in films_list
            if genre in [genre["name"] for genre in film.genres]
        ]

    # Фильтрация по дате создания.
    if creation_date is not None:
        films_list = [
            film for film in films_list if film.creation_date >= creation_date
        ]

    # Сортировка по рейтингу или дате создания.
    if sort_by is not None:
        films_list = sorted(films_list, key=lambda f: f.imdb_rating, reverse=True)

    log.info(f"Получено {len(films_list)} фильмов.")
    return paginate(films_list)


@router.get(
    "/search/{title_search}",
    summary="Полнотекстовый поиск по фильмам",
    description="Поиск по фильмам",
    response_description="Информация по фильмам",
)
async def film_search(
        title_search: str = Path(
            ...,
            title="Название для поиска",
            description="Название фильма для полнотекстового поиска.",
        ),
        film_service: FilmService = Depends(get_film_service),
) -> Page[FilmResponse]:
    """
    Поиск фильмов по названию.

    - **title_search**: Название фильма для поиска (обязательный параметр пути).
    - **film_service**: Сервис для получения данных о фильмах (зависимость).

    Возвращает пагинированный список фильмов по заданному названию.
    """
    log.info(f'Поиск фильмов по названию "{title_search}" ...')
    films_list = await film_service.get_by_search(title_search)

    if not films_list:
        log.info(f'Фильмы с названием "{title_search}" не найдены.')
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    log.info(f"Получено {len(films_list)} фильмов с названием {title_search}.")
    return paginate(films_list)
