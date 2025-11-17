from pydantic import BaseModel, Field
from fastapi import Query
from typing import Optional

DEFAULT_PAGE = 1
DEFAULT_SIZE = 50
MAX_SIZE = 200

class PageParams(BaseModel):
    page: int = Field(DEFAULT_PAGE, ge=1)
    size: int = Field(DEFAULT_SIZE, ge=1, le=MAX_SIZE)

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        return self.size

def get_pagination(
    page: int = Query(DEFAULT_PAGE, ge=1),
    size: int = Query(DEFAULT_SIZE, ge=1, le=MAX_SIZE),
) -> PageParams:
    return PageParams(page=page, size=size)
