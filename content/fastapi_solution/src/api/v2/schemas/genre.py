from pydantic import Field

from ...v2.schemas.base import BaseSchema


class GenreSchema(BaseSchema):
    id: str = Field(..., title="UUID", description="Идентификатор жанра")
    name: str = Field(..., title="Имя", description="Название жанра")
    description: str | None = Field(
        None, title="Описание", description="Описание жанра"
    )
