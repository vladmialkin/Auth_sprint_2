from typing import Literal

from pydantic import BaseModel, Field


class PersonFilmwork(BaseModel):
    table_name: Literal["person_film_work"] = Field(..., exclude=True)

    id: str
    film_work_id: str
    person_id: str
    role: str
    created_at: str
