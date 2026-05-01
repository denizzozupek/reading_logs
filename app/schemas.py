from pydantic import BaseModel, Field
from datetime import date

from enum import Enum


class ReadingStatus(str, Enum):
    OKUNDU = "okundu"
    OKUNUYOR = "okunuyor"
    YARIM_KALDI = "yarım_kaldı"


class BookAndLogCreate(BaseModel):
    title: str
    author: str
    genre: str
    page_count: int = Field(gt=0)

    rating: int = Field(ge=1, le=10)
    read_month: int = Field(ge=1, le=12)
    read_year: int = Field(ge=2000, le=date.today().year)


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None
    page_count: int | None = None


class LogUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=10)
    read_month: int | None = Field(default=None, ge=1, le=12)
    read_year: int | None = Field(default=None, ge=2000, le=date.today().year)


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    page_count: int

    model_config = {
        "from_attributes": True
    }  # This allows Pydantic to create a BookResponse from an ORM model instance


class LogResponse(BaseModel):
    id: int
    book_id: int
    read_date: date
    rating: int
    status: str
    read_pages: int

    book: BookResponse | None = None

    model_config = {
        "from_attributes": True
    }  # This allows Pydantic to create a LogResponse from an ORM model instance


class TotalPagesResponse(BaseModel):
    total_pages: int


class TotalBooksResponse(BaseModel):
    total_books: int


class GenreCountResponse(BaseModel):
    genre: str
    count: int


class AuthorCountResponse(BaseModel):
    author: str
    count: int


class RatingAverageForGenreResponse(BaseModel):
    genre: str
    average_rating: float


class RatingAverageForAuthorResponse(BaseModel):
    author: str
    average_rating: float


class MonthlyReadingStatsResponse(BaseModel):
    month: int
    count: int
    total_pages: int


class BookPageAverageResponse(BaseModel):
    average_pages: float
