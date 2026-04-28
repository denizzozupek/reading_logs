import csv
from datetime import date
from app.database import SessionLocal
from app.models import Book, ReadLog

csv_file = "okuma_listesi.csv"

with SessionLocal() as s:
    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            page_count = int(row["page_count"])
            read_year = int(row["read_year"])
            month = int(row["month"])
            read_date = date(read_year, month, 1)

            new_book = Book(
                title=row["title"],
                author=row["author"],
                genre=row["genre"],
                page_count=page_count,
            )

            new_log = ReadLog(
                status="okundu",
                rating=int(row["rating"]),
                read_date=read_date,
                read_pages=page_count,
            )

            new_book.logs.append(new_log)
            s.add(new_book)
    s.commit()
    print("Veriler başarıyla eklendi.")
