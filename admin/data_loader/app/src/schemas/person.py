from typing import Literal

from pydantic import BaseModel, Field


class Person(BaseModel):
    table_name: Literal["person"] = Field(..., exclude=True)

    id: str
    full_name: str
    created_at: str
    updated_at: str
