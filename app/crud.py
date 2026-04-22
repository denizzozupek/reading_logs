from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from datetime import date
from models import Book, ReadLog
from app.schemas import BookAndLogCreate


def create_book_and_log(db: Session, data: BookAndLogCreate):
    # Check if the book already exists in the database
    query = select(Book).where(Book.title == data.title, Book.author == data.author)
    db_book = db.execute(query).scalar_one_or_none()

    # If the book doesn't exist, create a new one
    if not db_book:

        db_book = Book(
            title=data.title,
            author=data.author,
            genre=data.genre,
            page_count=data.page_count,
        )
        db.add(db_book)
        db.commit()
        db.refresh(db_book)

    # Turn the read_month and read_year into a date object (using the first day of the month)
    read_month = data.read_month
    read_year = data.read_year if data.read_year else date.today().year
    read_date = date(read_year, read_month, 1)

    # Create a new ReadLog entry for the book
    new_log = ReadLog(
        book_id=db_book.id,
        read_date=read_date,
        rating=data.rating,
        status="okundu",
        read_pages=db_book.page_count,
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return new_log

def delete_book_log(db: Session, log_id: int):
    db_log = db.query(ReadLog).filter(ReadLog.id == log_id).first()
    if db_log:
        db.delete(db_log)
        db.commit()
        return True
    return False

def get_all_logs(db: Session):
    return db.query(ReadLog).options(selectinload(ReadLog.book)).all()