from pydantic import BaseModel, Field
from datetime import date

class BookAndLogCreate(BaseModel):
    title: str
    author: str
    genre: str
    page_count: int = Field(gt=0)

    rating: int = Field(ge=1, le=10)
    read_month: int = Field(ge=1, le=12)
    read_year: int = Field(ge=2000, le=date.today().year)


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    page_count: int

    model_config = {"from_attributes": True} # This allows Pydantic to create a BookResponse from an ORM model instance

class LogResponse(BaseModel):
    id: int
    book_id: int
    read_date: date
    rating: int
    status: str
    read_pages: int

    book: BookResponse | None = None

    model_config = {"from_attributes": True} # This allows Pydantic to create a LogResponse from an ORM model instance

class TotalPagesResponse(BaseModel):
    total_pages: int

class TotalBooksResponse(BaseModel):
    total_books: int

