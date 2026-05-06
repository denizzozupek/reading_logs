from app import crud
from app import schemas
import pytest


@pytest.fixture
def test_book_and_log_data():
    book = schemas.BookAndLogCreate(
        title="Lord of the Rings",
        author="J.R.R. Tolkien",
        genre="Fantasy",
        page_count=400,
        rating=10,
        read_month=5,
        read_year=2025,
    )

    return book


def test_invalid_date_format(client):
    response = client.get(
        "/stats/total-pages/",
        params={"start_date": "invalid-date", "end_date": "2026-01-01"},
    )

    assert response.status_code == 422


def test_add_reading_log(client, test_book_and_log_data):

    response = client.post("/readinglogs/", json=test_book_and_log_data.model_dump())
    assert response.status_code in (200, 201)

    data = response.json()
    assert data["book"]["title"] == test_book_and_log_data.title
    assert data["book"]["author"] == test_book_and_log_data.author
    assert data["rating"] == test_book_and_log_data.rating
    assert data["status"] == "okundu"
    assert data["read_pages"] == test_book_and_log_data.page_count
    assert "id" in data
    assert "read_date" in data


def test_delete_log_success(db_session, client, test_book_and_log_data):
    created_log = crud.create_book_and_log(db_session, test_book_and_log_data)

    assert created_log.id is not None

    response = client.delete(f"/readinglogs/{created_log.id}")

    assert response.status_code == 200

    assert response.json() == {
        "message": f"Log with id {created_log.id} deleted successfully"
    }


def test_delete_log_failed(client):
    log_id = 999
    response = client.delete(f"/readinglogs/{log_id}")

    assert response.status_code == 404


def test_get_all_books(client):
    response = client.get("/books/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_log_by_id(db_session, client, test_book_and_log_data):
    created_log = crud.create_book_and_log(db_session, test_book_and_log_data)

    assert created_log.id is not None

    response = client.get(f"/readinglogs/{created_log.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_log.id


def test_get_log_by_id_not_found(client):
    log_id = 999
    response = client.get(f"/readinglogs/{log_id}")
    assert response.status_code == 404


def test_get_book_by_id(db_session, client, test_book_and_log_data):
    created_log = crud.create_book_and_log(db_session, test_book_and_log_data)
    book_id = created_log.book_id

    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id


def test_get_book_by_id_not_found(client):
    book_id = 999
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 404


def test_get_total_read_pages(db_session, client, test_book_and_log_data):
    created_log = crud.create_book_and_log(db_session, test_book_and_log_data)
    total_pages = created_log.book.page_count

    start_date = "2025-01-01"
    end_date = "2026-01-01"

    response = client.get(
        "/stats/total-pages/", params={"start_date": start_date, "end_date": end_date}
    )

    assert response.status_code == 200
    assert response.json() == {"total_pages": total_pages}


def test_get_total_books_endpoint(db_session, client, test_book_and_log_data):
    created_log = crud.create_book_and_log(db_session, test_book_and_log_data)
    book2 = schemas.BookAndLogCreate(
        title="Hobbit",
        author="J. R. R. Tolkien",
        genre="Fantastik",
        page_count=300,
        rating=9,
        read_month=6,
        read_year=2024,
    )

    created_log2 = crud.create_book_and_log(db_session, book2)

    start_date = "2025-01-01"
    end_date = "2026-01-01"

    response = client.get(
        "/stats/total-books/", params={"start_date": start_date, "end_date": end_date}
    )
    assert response.status_code == 200

    assert response.json() == {"total_books": 1}


def test_get_total_books_by_genre(db_session, client, test_book_and_log_data):
    created_log = crud.create_book_and_log(db_session, test_book_and_log_data)
    start_date = "2025-01-01"
    end_date = "2026-01-01"

    response = client.get(
        "/stats/total-books-by-genre/",
        params={"start_date": start_date, "end_date": end_date},
    )
    assert response.status_code == 200

    assert response.json() == [{"genre": "Fantasy", "count": 1}]


def test_get_total_books_by_author(db_session, client, test_book_and_log_data):
    created_log = crud.create_book_and_log(db_session, test_book_and_log_data)

    book2 = schemas.BookAndLogCreate(
        title="Hobbit",
        author="J.R.R. Tolkien",
        genre="Fantastik",
        page_count=300,
        rating=9,
        read_month=6,
        read_year=2025,
    )

    book3 = schemas.BookAndLogCreate(
        title="1984",
        author="George Orwell",
        genre="Dystopian",
        page_count=350,
        rating=8,
        read_month=7,
        read_year=2025,
    )

    created_log2 = crud.create_book_and_log(db_session, book2)
    created_log3 = crud.create_book_and_log(db_session, book3)

    start_date = "2025-01-01"
    end_date = "2026-01-01"

    response = client.get(
        "/stats/total-books-by-author/",
        params={"start_date": start_date, "end_date": end_date},
    )
    assert response.status_code == 200

    assert response.json() == [{"author": "J.R.R. Tolkien", "count": 2}]


def test_get_rating_average_by_genre(db_session, client, test_book_and_log_data):
    created_log = crud.create_book_and_log(db_session, test_book_and_log_data)

    book2 = schemas.BookAndLogCreate(
        title="Hobbit",
        author="J.R.R. Tolkien",
        genre="Fantasy",
        page_count=300,
        rating=9,
        read_month=6,
        read_year=2025,
    )

    book3 = schemas.BookAndLogCreate(
        title="1984",
        author="George Orwell",
        genre="Dystopian",
        page_count=350,
        rating=8,
        read_month=7,
        read_year=2025,
    )

    created_log2 = crud.create_book_and_log(db_session, book2)
    created_log3 = crud.create_book_and_log(db_session, book3)

    response = client.get("/stats/average-rating-by-genre/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    
    result_dict = {item["genre"]: item["average_rating"] for item in data}
    assert result_dict == {
        "Dystopian": 8.0,
        "Fantasy": 9.5,
    }

def test_get_rating_average_by_author(db_session, client, test_book_and_log_data):
    created_log = crud.create_book_and_log(db_session, test_book_and_log_data)

    book2 = schemas.BookAndLogCreate(
        title="Hobbit",
        author="J.R.R. Tolkien",
        genre="Fantasy",
        page_count=300,
        rating=9,
        read_month=6,
        read_year=2025,
    )

    book3 = schemas.BookAndLogCreate(
        title="1984",
        author="George Orwell",
        genre="Dystopian",
        page_count=350,
        rating=8,
        read_month=7,
        read_year=2025,
    )

    created_log2 = crud.create_book_and_log(db_session, book2)
    created_log3 = crud.create_book_and_log(db_session, book3)

    response = client.get("/stats/average-rating-by-author/")
    assert response.status_code == 200

    assert response.json() == [
        {"author": "J.R.R. Tolkien", "average_rating": 9.5},
    ]

