#!/bin/sh
set -e

if [ "$SKIP_DB_WAIT" != "True" ] && [ "$SKIP_DB_WAIT" != "true" ]; then
  echo "Waiting for database..."
  HOST="${DB_HOST:-db}"
  USER="${DB_USER:-cashctrl_user}"
  NAME="${DB_NAME:-cashctrl}"
  while ! pg_isready -h "$HOST" -U "$USER" -d "$NAME"; do
    sleep 1
  done
  echo "Database is ready!"
fi

if [ "$1" = "gunicorn" ]; then
  echo "Applying migrations..."
  python manage.py migrate --noinput

  echo "Collecting static files..."
  python manage.py collectstatic --noinput
fi

exec "$@"
