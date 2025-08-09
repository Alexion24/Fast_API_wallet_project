#!/bin/bash
set -e

echo "Waiting for database..."
until pg_isready -h db -U postgres; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

if [ "$1" = "test" ]; then
    echo "Setting up test database..."

    PGPASSWORD=postgres psql -h db -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'test_wallet'" | grep -q 1 && \
    PGPASSWORD=postgres psql -h db -U postgres -c "DROP DATABASE test_wallet"

    PGPASSWORD=postgres psql -h db -U postgres -c "CREATE DATABASE test_wallet"

    echo "Running tests..."
    python -m pytest -v backend/tests/
elif [ "$1" = "app" ]; then
    echo "Running migrations..."
    alembic upgrade head

    echo "Starting application..."
    exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
else
    echo "Unknown command: $1"
    exit 1
fi
