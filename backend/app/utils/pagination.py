from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


def paginate(query_result: list, total: int, page: int, page_size: int):
    return {"items": query_result, "total": total, "page": page, "page_size": page_size}
