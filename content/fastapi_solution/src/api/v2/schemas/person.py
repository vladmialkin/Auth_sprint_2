from ...v2.schemas.base import BaseSchema


class PersonFilmSchema(BaseSchema):
    id: str
    roles: list[str]


class PersonSchema(BaseSchema):
    id: str
    full_name: str
    films: list[PersonFilmSchema]
