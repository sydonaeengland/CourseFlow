#!/bin/sh
set -e

echo "Waiting for MySQL..."
until mysql -h "$DB_HOST" -P "${DB_PORT:-3306}" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SELECT 1" > /dev/null 2>&1; do
  sleep 2
done

echo "Running schema..."
mysql -h "$DB_HOST" -P "${DB_PORT:-3306}" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < /app/create_db.sql

echo "Checking if data exists..."
COUNT=$(mysql -h "$DB_HOST" -P "${DB_PORT:-3306}" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -sN -e "SELECT COUNT(*) FROM users;")
if [ "$COUNT" -eq "0" ]; then
  echo "Populating data..."
  mysql -h "$DB_HOST" -P "${DB_PORT:-3306}" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < /app/populate_db.sql
else
  echo "Data already exists, skipping populate."
fi

echo "Starting app..."
exec gunicorn --bind "0.0.0.0:${PORT:-5000}" --workers 4 app:app
