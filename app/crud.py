from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func
from datetime import date
from app.models import Book, ReadLog
from app.schemas import BookAndLogCreate, BookUpdate, LogUpdate


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
        db.flush()  # Flush to get the book ID for the log entry before committing (if we commit here, we won't be able to roll back the book creation if the log creation fails)

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


def _date_filter(query, start_date: date | None = None, end_date: date | None = None):
    if start_date:
        normalized_start_date = date(start_date.year, start_date.month, 1)
        query = query.where(ReadLog.read_date >= normalized_start_date)
    if end_date:
        query = query.where(ReadLog.read_date <= end_date)
    return query


def delete_book_log(db: Session, log_id: int):
    db_log = db.query(ReadLog).filter(ReadLog.id == log_id).first()
    if db_log:
        db.delete(db_log)
        db.commit()
        return True
    return False


def update_book(db: Session, book_id: int, update_data: BookUpdate):

    db_book = db.get(Book, book_id)

    if not db_book:
        return None

    update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)

    for key, value in update_dict.items():
        setattr(db_book, key, value)

    db.commit()
    db.refresh(db_book)
    return db_book


def update_log(db: Session, log_id: int, update_data: LogUpdate):

    db_log = db.get(ReadLog, log_id)

    if not db_log:
        return None

    update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)

    read_month = update_dict.pop("read_month", db_log.read_date.month)
    read_year = update_dict.pop("read_year", db_log.read_date.year)

    if "read_month" in update_data.model_fields_set or "read_year" in update_data.model_fields_set:
        db_log.read_date = date(read_year, read_month, 1)

    for key, value in update_dict.items():
        setattr(db_log, key, value)

    db.commit()
    db.refresh(db_log)
    return db_log


def get_all_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    sort_by: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    rating_filter: int | None = None,
):
    query = (
        select(ReadLog)
        .join(Book)
        .options(selectinload(ReadLog.book))
        .where(ReadLog.status == "okundu")
    )
    query = _date_filter(query, start_date, end_date)

    if rating_filter is not None:
        query = query.where(ReadLog.rating == rating_filter)

    if sort_by is not None:

        if sort_by == "pages":
            query = query.order_by(ReadLog.read_pages.desc())

        else:
            query = query.order_by(ReadLog.read_date.desc())

    query = query.offset(skip)

    if limit is not None:
        query = query.limit(limit)

    return db.execute(query).scalars().all()


def get_books_pages_average(db: Session):
    query = (
        select(func.avg(Book.page_count))
        .join(ReadLog)
        .where(ReadLog.status == "okundu")
        .where(Book.genre.notin_(["Çizgi Roman", "Manga"]))
    )
    average_pages = db.execute(query).scalar()
    return round(average_pages, 1) if average_pages else 0.0


def get_total_read_pages(
    db: Session, start_date: date | None = None, end_date: date | None = None
):
    query = select(func.sum(ReadLog.read_pages)).where(ReadLog.status == "okundu")
    query = _date_filter(query, start_date, end_date)
    total_pages = db.execute(query).scalar()
    return total_pages if total_pages else 0


def get_total_books_read(
    db: Session, start_date: date | None = None, end_date: date | None = None
):
    query = select(func.count(ReadLog.id)).where(ReadLog.status == "okundu")
    query = _date_filter(query, start_date, end_date)

    total_books = db.execute(query).scalar()
    return total_books


def get_total_books_read_by_genre(
    db: Session, start_date: date | None = None, end_date: date | None = None
):
    query = (
        select(Book.genre, func.count(ReadLog.id))
        .join(ReadLog)
        .where(ReadLog.status == "okundu")
    )

    query = _date_filter(query, start_date, end_date)

    query = query.group_by(Book.genre).order_by(func.count(ReadLog.id).desc())

    results = db.execute(query).all()
    return [{"genre": genre, "count": count} for genre, count in results]


def get_total_books_read_by_author(
    db: Session, start_date: date | None = None, end_date: date | None = None
):
    query = (
        select(Book.author, func.count(ReadLog.id))
        .join(ReadLog)
        .where(ReadLog.status == "okundu")
    )
    query = _date_filter(query, start_date, end_date)

    query = (
        query.group_by(Book.author)
        .having(func.count(ReadLog.id) > 1)
        .order_by(func.count(ReadLog.id).desc())
    )

    results = db.execute(query).all()
    return [{"author": author, "count": count} for author, count in results]


def get_all_books(db: Session):
    query = select(Book).order_by(Book.title)
    return db.execute(query).scalars().all()


def get_rating_average_by_genre(db: Session):
    query = select(Book.genre, func.avg(ReadLog.rating))
    query = query.join(ReadLog).where(ReadLog.status == "okundu").group_by(Book.genre)
    results = db.execute(query).all()
    return [
        {"genre": genre, "average_rating": round(avg_rating, 1)}
        for genre, avg_rating in results
    ]


def get_rating_average_by_author(db: Session):
    query = (
        select(Book.author, func.avg(ReadLog.rating))
        .join(ReadLog)
        .where(ReadLog.status == "okundu")
        .group_by(Book.author)
        .having(func.count(ReadLog.id) > 1)
    )
    results = db.execute(query).all()
    return [
        {"author": author, "average_rating": round(avg_rating, 1)}
        for author, avg_rating in results
    ]


def get_book_with_id(db: Session, book_id: int):
    query = select(Book).where(Book.id == book_id)
    return db.execute(query).scalar_one_or_none()


def get_log_with_id(db: Session, log_id: int):
    query = select(ReadLog).where(ReadLog.id == log_id)
    log = db.execute(query).scalar_one_or_none()
    return log


def monthly_reading_stats(db: Session, year: int | None = None):
    query = (
        select(
            func.date_part("month", ReadLog.read_date).label("month"),
            func.count(ReadLog.id),
            func.sum(ReadLog.read_pages),
        )
        .where(ReadLog.status == "okundu")
        .group_by(func.date_part("month", ReadLog.read_date))
        .order_by(func.date_part("month", ReadLog.read_date))
    )

    if year is not None:
        query = query.where(func.date_part("year", ReadLog.read_date) == year)
    results = db.execute(query).all()
    return [
        {
            "month": int(month),
            "count": count,
            "total_pages": int(total_pages) if total_pages else 0,
        }
        for month, count, total_pages in results
    ]
