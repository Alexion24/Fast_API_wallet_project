#!/bin/bash
set -e

echo "Waiting for database..."
sleep 5

if [ "$1" = "test" ]; then
    echo "Setting up test database..."
    PGPASSWORD=postgres psql -h db -U postgres -c "DROP DATABASE IF EXISTS test_wallet"
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