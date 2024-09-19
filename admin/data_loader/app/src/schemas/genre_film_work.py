from typing import Literal

from pydantic import BaseModel, Field


class GenreFilmwork(BaseModel):
    table_name: Literal["genre_film_work"] = Field(..., exclude=True)

    id: str
    film_work_id: str
    genre_id: str
    created_at: str
