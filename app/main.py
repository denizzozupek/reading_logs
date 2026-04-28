from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from typing import Annotated

from app import schemas
from app.database import SessionLocal
from app.schemas import BookAndLogCreate, LogResponse, BookResponse
from app import crud

app = FastAPI(title="Reading Logs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AnnotatedDate = Annotated[date | None, Query(description="Filter by date (YYYY-MM-DD)")]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/readinglogs/", response_model=LogResponse)
def add_reading_log(data: BookAndLogCreate, db: Session = Depends(get_db)):
    new_log = crud.create_book_and_log(db, data)
    return new_log


@app.delete("/readinglogs/{log_id}")
def delete_reading_log(log_id: int, db: Session = Depends(get_db)):
    success = crud.delete_book_log(db, log_id)
    if success:
        return {"message": f"Log with id {log_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Log not found")


@app.get("/readinglogs/", response_model=list[LogResponse])
def get_all_logs(db: Session = Depends(get_db)):
    return crud.get_all_logs(db)


@app.get("/readinglogs/{log_id}", response_model=LogResponse)
def get_log_by_id(log_id: int, db: Session = Depends(get_db)):
    log = crud.get_log_with_id(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log


@app.get("/books/", response_model=list[BookResponse])
def get_all_books(db: Session = Depends(get_db)):
    return crud.get_all_books(db)


@app.get("/books/{book_id}", response_model=BookResponse)
def get_book_by_id(book_id: int, db: Session = Depends(get_db)):
    book = crud.get_book_with_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.get("/stats/total-pages/", response_model=schemas.TotalPagesResponse)
def get_total_read_pages_endpoint(
    db: Session = Depends(get_db),
    start_date: AnnotatedDate = None,
    end_date: AnnotatedDate = None,
):
    total_pages = crud.get_total_read_pages(
        db, start_date=start_date, end_date=end_date
    )
    return {"total_pages": total_pages}


@app.get("/stats/total-books/", response_model=schemas.TotalBooksResponse)
def get_total_books_endpoint(
    db: Session = Depends(get_db),
    start_date: AnnotatedDate = None,
    end_date: AnnotatedDate = None,
):
    total_books = crud.get_total_books_read(
        db, start_date=start_date, end_date=end_date
    )
    return {"total_books": total_books}


@app.get(
    "/stats/total-books-by-genre/", response_model=list[schemas.GenreCountResponse]
)
def get_total_books_by_genre_endpoint(
    db: Session = Depends(get_db),
    start_date: AnnotatedDate = None,
    end_date: AnnotatedDate = None,
):
    return crud.get_total_books_read_by_genre(
        db, start_date=start_date, end_date=end_date
    )


@app.get(
    "/stats/total-books-by-author/", response_model=list[schemas.AuthorCountResponse]
)
def get_total_books_read_by_author_endpoint(
    db: Session = Depends(get_db),
    start_date: AnnotatedDate = None,
    end_date: AnnotatedDate = None,
):
    return crud.get_total_books_read_by_author(
        db, start_date=start_date, end_date=end_date
    )


@app.get(
    "/stats/average-rating-by-genre/",
    response_model=list[schemas.RatingAverageForGenreResponse],
)
def get_rating_average_by_genre_endpoint(db: Session = Depends(get_db)):
    return crud.get_rating_average_by_genre(db)


@app.get(
    "/stats/average-rating-by-author/",
    response_model=list[schemas.RatingAverageForAuthorResponse],
)
def get_rating_average_by_author_endpoint(db: Session = Depends(get_db)):
    return crud.get_rating_average_by_author(db)


@app.get(
    "/stats/monthly-reading-stats",
    response_model=list[schemas.MonthlyReadingStatsResponse],
)
def get_monthly_reading_stats_endpoint(
    db: Session = Depends(get_db),
    year: Annotated[int | None, Query(description="Filter by year (e.g. 2024)")] = None,
):
    return crud.monthly_reading_stats(db, year=year)
