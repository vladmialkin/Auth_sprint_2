from typing import Optional

from pydantic import BaseModel, Field


class FilmRequest(BaseModel):
    id: str = Field(..., title="UUID", description="Идентификатор фильма")
    title: str = Field(..., title="Название", description="Название фильма")
    imdb_rating: Optional[float] = Field(
        None, title="Рейтинг", description="Рейтинг фильма"
    )
    creation_date: Optional[str] = Field(
        None, title="Дата создания", description="Дата выпуска фильма"
    )
    genres: list[dict[str, Optional[str]]] = Field(
        ..., title="Жанры", description="Список жанров фильма"
    )
    description: Optional[str] = Field(
        None, title="Описание", description="Описание фильма"
    )
    file_path: Optional[dict] = Field(
        None, title="Путь к файлу", description="Путь к файлу фильма"
    )
    directors_names: list[str] = Field(
        ..., title="Имена режиссеров", description="Список имен режиссеров"
    )
    actors_names: list[str] = Field(
        ..., title="Имена актеров", description="Список имен актеров"
    )
    writers_names: list[str] = Field(
        ..., title="Имена сценаристов", description="Список имен сценаристов"
    )
    directors: list[dict[str, str]] = Field(
        ..., title="Режиссеры", description="Список режиссеров с дополнениями"
    )
    actors: list[dict[str, str]] = Field(
        ..., title="Актеры", description="Список актеров с дополнениями"
    )
    writers: list[dict[str, str]] = Field(
        ..., title="Сценаристы", description="Список сценаристов с дополнениями"
    )


# Полная информация о фильме
class FilmFullResponse(BaseModel):
    id: str = Field(..., title="UUID", description="Идентификатор фильма")
    title: str = Field(..., title="Название", description="Название фильма")
    imdb_rating: Optional[float] = Field(
        None, title="Рейтинг", description="Рейтинг фильма"
    )
    creation_date: Optional[str] = Field(
        None, title="Дата создания", description="Дата выпуска фильма"
    )
    genres: list[dict[str, Optional[str]]] = Field(
        ..., title="Жанры", description="Список жанров фильма"
    )
    description: Optional[str] = Field(
        None, title="Описание", description="Описание фильма"
    )
    directors: list[dict[str, str]] = Field(
        ..., title="Режиссеры", description="Список режиссеров"
    )
    actors: list[dict[str, str]] = Field(
        ..., title="Актеры", description="Список актеров"
    )
    writers: list[dict[str, str]] = Field(
        ..., title="Сценаристы", description="Список сценаристов"
    )


# Ответ с основной информацией о фильме
class FilmResponse(BaseModel):
    id: str = Field(..., title="UUID", description="Идентификатор фильма")
    title: str = Field(..., title="Название", description="Название фильма")
    imdb_rating: Optional[float] = Field(
        None, title="Рейтинг", description="Рейтинг фильма"
    )


# Модель для жанра
class Genre(BaseModel):
    id: str = Field(..., title="UUID", description="Идентификатор жанра")
    name: str = Field(..., title="Имя", description="Название жанра")
    description: Optional[str] = Field(
        None, title="Описание", description="Описание жанра"
    )


# Модель для личности (персоны)
class Person(BaseModel):
    id: str = Field(..., title="UUID", description="Идентификатор персоны")
    full_name: str = Field(..., title="Полное имя", description="Полное имя персоны")
    films: list[dict] = Field(
        ..., title="Фильмы", description="Список фильмов, в которых участвовала персона"
    )
