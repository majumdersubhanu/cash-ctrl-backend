#!/bin/sh
set -e

echo "Waiting for database..."

while ! pg_isready -h db -U cashctrl_user -d cashctrl; do
  sleep 1
done

echo "Database is ready!"

if [ "$1" = "gunicorn" ]; then
  echo "Applying migrations..."
  python manage.py migrate --noinput

  echo "Collecting static files..."
  python manage.py collectstatic --noinput
fi

exec "$@"
