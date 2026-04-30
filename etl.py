import csv
from datetime import date

from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models import Book, ReadLog
from app.crud import create_book_and_log
from app.schemas import BookAndLogCreate

EXPECTED_COLUMNS = [
    "title",
    "author",
    "genre",
    "page_count",
    "rating",
    "read_month",
    "read_year",
]


def load_books_from_csv(file_path: str):
    db = SessionLocal()

    with open(file_path, mode="r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)

        actual_columns = csv_reader.fieldnames
        if not all(column in actual_columns for column in EXPECTED_COLUMNS):
            missing_columns = [
                column for column in EXPECTED_COLUMNS if column not in actual_columns
            ]
            raise ValueError(
                f"CSV file is missing the following required columns: {', '.join(missing_columns)}"
            )

        success_count = 0
        skipped_count = 0

        for row in enumerate(csv_reader, start=2):
            try:
                book_and_log_data = BookAndLogCreate(
                    title=row["title"],
                    author=row["author"],
                    genre=row["genre"],
                    page_count=int(row["page_count"]),
                    rating=int(row["rating"]),
                    read_month=int(row["read_month"]),
                    read_year=int(row["read_year"]),
                )

                create_book_and_log(db, book_and_log_data)
                success_count += 1

            except IntegrityError:

                db.rollback()
                print(f"Row {row[0]} skipped: Book '{row['title']}' by {row['author']} already exists.")
                skipped_count += 1

            except Exception as e:
                db.rollback()
                print(f"Row {row[0]} skipped due to error: {e}")
                skipped_count += 1

        print(f"Finished processing CSV file: {success_count} rows added, {skipped_count} rows skipped.")
     
    db.close()

if __name__ == "__main__":
    load_books_from_csv("okuma_listesi.csv")