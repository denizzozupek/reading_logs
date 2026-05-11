#!/bin/bash

echo "PostgreSQL bekleniyor..."
while ! pg_isready -h $PGHOST -p 5432 > /dev/null 2>&1; do
  sleep 1
done

echo "PostgreSQL hazır, migration çalışıyor..."
alembic upgrade head

echo "Uygulama başlatılıyor..."
uvicorn app.main:app --host 0.0.0.0 --port 8000