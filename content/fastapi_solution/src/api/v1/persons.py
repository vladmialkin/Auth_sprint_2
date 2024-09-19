import logging
from http import HTTPStatus
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi_pagination import Page, paginate

from ...models.models import Person
from ...services.person_service import PersonService, get_person_service

router = APIRouter()

log = logging.getLogger("main")


@router.get(
    "/{person_id}",
    response_model=Person,
    summary="Поиск персоны по id",
    description="Получение информации по id",
    response_description="Полная информация по персоне",
)
async def person_details(
    person_id: str = Path(
        ...,
        title="Идентификатор персоны",
        description="Уникальный идентификатор персоны для получения его деталей.",
    ),
    person_service: PersonService = Depends(get_person_service),
) -> Person:
    """
    Получить информацию о персоне по ее идентификатору.

    - **person_id**: Уникальный идентификатор персоны (обязательный параметр пути).
    - **person_service**: Сервис для получения данных о персонах (зависимость).

    Возвращает информацию о персоне в случае успеха,
    иначе вызывает HTTPException с кодом 404, если персона не найдена.
    """
    log.info(f"Получение информации по персоне с id: {person_id} ...")
    person = await person_service.get_by_id(person_id)

    if not person:
        log.info(f"Персона с id: {person_id} не найдена.")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")

    log.info(f"Информация по персоне с id: {person_id} получена.")
    return person


@router.get(
    "",
    summary="Список персон",
    description="Список персон с пагинацией",
    response_description="Информация по персонам",
)
async def persons(
    person_service: PersonService = Depends(get_person_service),
    sort_by: Optional[Literal["writer", "director", "actor"]] = Query(
        None, title="Деятельность", description="Фильтрует персон по виду деятельности."
    ),
) -> Page[Person]:
    """
    Получить список персон с возможностью сортировки по ролям.

    - **sort_by**: Указывает, по какому роли сортировать список персон. Может принимать значения:
      - 'writer': Фильтровать по сценаристам.
      - 'director': Фильтровать по режиссерам.
      - 'actor': Фильтровать по актерам (необязательный параметр).

    Возвращает пагинированный список персон.
    В случае отсутствия персон вызывает HTTPException с кодом 404.
    """
    log.info("Получение персон ...")
    persons_list = await person_service.get_all_persons()

    if not persons_list:
        log.info(f"Персон не найдено.")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Persons not found"
        )

    if sort_by is not None:
        # получение только тек персон, роли которых совпадают с выбранным
        persons_list = [
            person
            for person in persons_list
            if any(role == sort_by for film in person.films for role in film["roles"])
        ]

    log.info(f"Получено {len(persons_list)} персон.")
    return paginate(persons_list)


@router.get(
    '/search/',
    summary='Полнотекстовый поиск по персонам',
    description='Поиск по персонам',
    response_description='Информация по персоне'
)
async def person_search(
        person_service: PersonService = Depends(get_person_service),
        name_search: str = Query(
            None, title="Название для поиска",
            description="Имя персоны для полнотекстового поиска."
        )
) -> Page[Person]:
    """
    Поиск персоны по имени.

    - **name_search**: Имя персоны для поиска (обязательный параметр пути).
    - **person_service**: Сервис для получения данных о персоне (зависимость).

    Возвращает пагинированный список персон по заданному имени.
    """
    log.info(f'Поиск персон по имени "{name_search}" ...')
    persons_list = await person_service.get_by_search(name_search)

    if not persons_list:
        log.info(f'Персоны с именем "{name_search}" не найдены.')
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    log.info(f'Получено {len(persons_list)} персон с именем {name_search}.')
    return paginate(persons_list)
