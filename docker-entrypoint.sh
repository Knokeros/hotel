#!/usr/bin/env sh
set -e

poetry run python manage.py migrate --noinput
exec poetry run python manage.py runserver 0.0.0.0:8000
