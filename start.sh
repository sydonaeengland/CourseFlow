#!/bin/sh

echo "Starting gunicorn..."
gunicorn --bind "0.0.0.0:${PORT:-5000}" --workers 4 app:app &
GUNICORN_PID=$!

echo "DB_HOST=$DB_HOST DB_PORT=$DB_PORT DB_USER=$DB_USER DB_NAME=$DB_NAME"
echo "Waiting for MySQL..."
until mysql -h "$DB_HOST" -P "${DB_PORT:-3306}" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SELECT 1" 2>&1; do
  echo "MySQL not ready, retrying..."
  sleep 3
done

echo "Running schema..."
mysql -h "$DB_HOST" -P "${DB_PORT:-3306}" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < /app/create_db.sql

COUNT=$(mysql -h "$DB_HOST" -P "${DB_PORT:-3306}" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -sN -e "SELECT COUNT(*) FROM users;")
if [ "$COUNT" -eq "0" ]; then
  echo "Populating data..."
  mysql -h "$DB_HOST" -P "${DB_PORT:-3306}" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < /app/populate_db.sql
  echo "Done."
fi

wait $GUNICORN_PID
