import pytest
from app import crud
from app.schemas import BookAndLogCreate, BookUpdate, LogUpdate
from app.models import Book, ReadLog


@pytest.fixture
def book_and_log_instance():
    book = BookAndLogCreate(
        title="Yüzüklerin Efendisi",
        author="J. R. R. Tolkien",
        genre="Fantastik",
        page_count=400,
        rating=10,
        read_month=6,
        read_year=2025,
    )


def test_create_book_and_log(db_session, book_and_log_instance):
    created_log = crud.create_book_and_log(db_session, book_and_log_instance)

    assert created_log.id is not None
    assert created_log.rating == book_and_log_instance.rating
    assert created_log.read_date.month == book_and_log_instance.read_month
    assert created_log.read_date.year == book_and_log_instance.read_year

    db_book = db_session.get(Book, created_log.book_id)

    assert db_book is not None
    assert db_book.title == book_and_log_instance.title
    assert db_book.author == book_and_log_instance.author
    assert db_book.genre == book_and_log_instance.genre
    assert db_book.page_count == book_and_log_instance.page_count


def test_create_book_and_log_for_existing_book(db_session, book_and_log_instance):
    created_log1 = crud.create_book_and_log(db_session, book_and_log_instance)
    created_log2 = crud.create_book_and_log(db_session, book_and_log_instance)

    assert created_log1.book_id == created_log2.book_id
    assert created_log1.id != created_log2.id

def test_delete_book_log(db_session, book_and_log_instance):
    created_log = crud.create_book_and_log(db_session, book_and_log_instance)

    result = crud.delete_book_log(db_session, created_log)
    assert result is True
    deleted_log = db_session.get(ReadLog.id, created_log.id)
    assert deleted_log is None


def test_delete_book_log_false(db_session):
    result = crud.delete_book_log(db_session, log_id=9999)

    assert result is False


def test_update_book(db_session, book_and_log_instance):
    created_book = crud.create_book_and_log(db_session, book_and_log_instance)

    update_data = BookUpdate(author="Tolkien")

    updated_book = crud.update_book(
        db_session, book_id=created_book.book_id, data=update_data
    )

    assert updated_book is not None
    assert updated_book.author == "Tolkien"
    assert updated_book.title == book_and_log_instance.title
    assert updated_book.genre == book_and_log_instance.genre


def test_update_book_none(db_session):
    update_data = BookUpdate(author="Tolkien")

    updated_book = crud.update_book(db_session, book_id=9999, data=update_data)
    assert updated_book is None


def test_update_log(db_session, book_and_log_instance):
    created_log = crud.create_book_and_log(db_session, book_and_log_instance)

    update_data = LogUpdate(rating=9)

    updated_log = crud.update_log(db_session, log_id=created_log.id, data=update_data)

    updated_log = crud.update_log(db_session, log_id=created_log.id, data=update_data)
    assert updated_log is not None
    assert updated_log.rating == 9
    assert updated_log.read_date == created_log.read_date


def test_update_log_none(db_session):

    update_data = LogUpdate(rating=9)

    updated_log = crud.update_log(db_session, log_id=9999, data=update_data)
    assert updated_log is None


def test_update_log_date(db_session, book_and_log_instance):

    book = book_and_log_instance

    created_log = crud.create_book_and_log(db_session, book)

    update_data = LogUpdate(read_month=7, read_year=2025)

    updated_log = crud.update_log(db_session, log_id=created_log.id, data=update_data)

    created_log = crud.create_book_and_log(db_session, book)
    update_data = LogUpdate(read_month=7, read_year=2025)
    updated_log = crud.update_log(db_session, log_id=created_log.id, data=update_data)
    assert updated_log is not None
    assert updated_log.read_date.month == 7
    assert updated_log.read_date.year == 2025


def test_get_all_logs(db_session, book_and_log_instance):
    book1 = book_and_log_instance
    book2 = BookAndLogCreate(
        title="Hobbit",
        author="J. R. R. Tolkien",
        genre="Fantastik",
        page_count=300,
        rating=9,
        read_month=7,
        read_year=2025,
    )

    crud.create_book_and_log(db_session, book1)
    crud.create_book_and_log(db_session, book2)

    logs = crud.get_all_logs(db_session)
    assert len(logs) == 2
    log_titles = [log.book.title for log in logs]
    assert "Yüzüklerin Efendisi" in log_titles
    assert "Hobbit" in log_titles


def test_get_all_logs_with_rating_filter(db_session, book_and_log_instance):
    book1 = book_and_log_instance
    book2 = BookAndLogCreate(
        title="Hobbit",
        author="J. R. R. Tolkien",
        genre="Fantastik",
        page_count=300,
        rating=9,
        read_month=7,
        read_year=2025,
    )

    crud.create_book_and_log(db_session, book1)
    crud.create_book_and_log(db_session, book2)

    logs = crud.get_all_logs(db_session, min_rating=10)
    assert len(logs) == 1
    assert logs[0].book.title == "Yüzüklerin Efendisi"

    crud.create_book_and_log(db_session, book1)

    logs = crud.get_all_logs(db_session, min_rating=10)
    assert len(logs) == 1
    assert logs[0].book.title == "Yüzüklerin Efendisi"

def test_get_all_logs_by_sorting(db_session, book_and_log_instance):
    book1 = book_and_log_instance
    book2 = BookAndLogCreate(
        title="Hobbit",
        author="J. R. R. Tolkien",
        genre="Fantastik",
        page_count=300,
        rating=9,
        read_month=7,
        read_year=2025,
    )

    crud.create_book_and_log(db_session, book1)
    crud.create_book_and_log(db_session, book2)

    logs = crud.get_all_logs(db_session, sort_by="rating")
    assert len(logs) == 2
    assert logs[0].rating >= logs[1].rating