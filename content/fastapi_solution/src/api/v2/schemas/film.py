from pydantic import Field

from ...v2.schemas.base import BaseSchema


class FilmSchema(BaseSchema):
    id: str = Field(..., title="UUID", description="Идентификатор фильма")
    title: str = Field(..., title="Название", description="Название фильма")
    imdb_rating: float | None = Field(
        None, title="Рейтинг", description="Рейтинг фильма"
    )
