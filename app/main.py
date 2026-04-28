from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from datetime import date

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


@app.get("/books/", response_model=list[BookResponse])
def get_all_books(db: Session = Depends(get_db)):
    return crud.get_all_books(db)


@app.get("/stats/total-pages/", response_model=schemas.TotalPagesResponse)
def get_total_read_pages_endpoint(
    db: Session = Depends(get_db),
    start_date: date | None = None,
    end_date: date | None = None,
):
    total_pages = crud.get_total_read_pages(
        db, start_date=start_date, end_date=end_date
    )
    return {"total_pages": total_pages}


@app.get("/stats/total-books/", response_model=schemas.TotalBooksResponse)
def get_total_books_endpoint(
    db: Session = Depends(get_db),
    start_date: date | None = None,
    end_date: date | None = None,
):
    total_books = crud.get_total_books_read(db, start_date=start_date, end_date=end_date)
    return {"total_books": total_books}


@app.get("/stats/total-books-by-genre/")
def get_total_books_by_genre_endpoint(
    db: Session = Depends(get_db),
    start_date: date | None = None,
    end_date: date | None = None,
):
    return crud.get_total_books_read_by_genre(
        db, start_date=start_date, end_date=end_date
    )


@app.get("/stats/total-books-by-author/")
def get_total_books_read_by_author_endpoint(
    db: Session = Depends(get_db),
    start_date: date | None = None,
    end_date: date | None = None,
):
    return crud.get_total_books_read_by_author(
        db, start_date=start_date, end_date=end_date
    )
