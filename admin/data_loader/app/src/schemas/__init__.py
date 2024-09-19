from pydantic import BaseModel, Field
from schemas.film_work import FilmWork
from schemas.genre import Genre
from schemas.genre_film_work import GenreFilmwork
from schemas.person import Person
from schemas.person_film_work import PersonFilmwork

Model = Person | FilmWork | Genre | GenreFilmwork | PersonFilmwork


class Row(BaseModel):
    model: Model = Field(..., discriminator="table_name")
