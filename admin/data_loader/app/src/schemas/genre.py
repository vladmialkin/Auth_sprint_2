from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, Field


class Genre(BaseModel):
    table_name: Literal["genre"] = Field(..., exclude=True)

    id: str
    name: str
    description: Annotated[str, BeforeValidator(lambda v: v if v else "")]
    created_at: str
    updated_at: str
