# Reading Logs API

A personal book tracking REST API. Manage the books you've read, your ratings, and your reading statistics.

🔗 **Live Demo:** https://reading-logs.onrender.com/docs

---

## Tech Stack

- **FastAPI** — REST API
- **PostgreSQL** — Veritabanı
- **SQLAlchemy** — ORM
- **Alembic** — Migration yönetimi
- **Docker & Docker Compose** — Containerization
- **Render** — Deployment

---

## Features

- Add, update, and delete books and reading logs
- Reading statistics by genre, author, and month
- Filter by date range and rating
- Page count and rating average calculations

---

## Getting Started

### Requirements

- Docker
- Docker Compose

### Run Locally

```bash
git clone https://github.com/denizzozupek/reading_logs.git
cd reading_logs
cp .env.example .env  # fill in the values
docker compose up --build
```

API will be available at `http://localhost:8000/docs`

---

## Environment Variables

Copy `.env.example` and fill in the values:

```
DATABASE_URL=postgresql+psycopg2://user:password@db:5432/dbname
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/readinglogs/` | Add a book and reading log |
| GET | `/readinglogs/{id}` | Get a reading log |
| DELETE | `/readinglogs/{id}` | Delete a reading log |
| GET | `/books/` | List all books |
| GET | `/books/{id}` | Get a book |
| PATCH | `/update/update-book-stats/{id}` | Update book info |
| PATCH | `/update/update-log-stats/{id}` | Update reading log |
| GET | `/stats/total-pages/` | Total pages read |
| GET | `/stats/total-books/` | Total books read |
| GET | `/stats/total-books-by-genre/` | Books read by genre |
| GET | `/stats/total-books-by-author/` | Books read by author |
| GET | `/stats/average-rating-by-genre/` | Average rating by genre |
| GET | `/stats/average-rating-by-author/` | Average rating by author |
| GET | `/stats/monthly-reading-stats` | Monthly reading statistics |
| GET | `/stats/books-pages-average/` | Average page count |
| GET | `/stats/readinglogs/` | All reading logs (with filters) |

For full endpoint documentation and parameters: https://reading-logs.onrender.com/docs
