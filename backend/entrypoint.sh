#!/bin/sh

set -e

echo "Waiting for PostgreSQL..."

until python -c "
import psycopg2
import os
from urllib.parse import urlparse

database_url = os.getenv('DATABASE_URL')
parsed = urlparse(database_url)

conn = psycopg2.connect(
    dbname=parsed.path[1:],
    user=parsed.username,
    password=parsed.password,
    host=parsed.hostname,
    port=parsed.port,
)
conn.close()
"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is ready."

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"