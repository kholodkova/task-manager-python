#!/bin/sh
# Практическая работа № 3: вторая база tasks_test для автотестов.
# Postgres выполняет скрипты из /docker-entrypoint-initdb.d только при первом
# создании тома с данными.
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  -c "CREATE DATABASE tasks_test OWNER $POSTGRES_USER;"
