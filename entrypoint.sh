#!/bin/sh

echo "===Collect static files==="
python manage.py collectstatic --noinput


echo "===Apply database migrations==="
python manage.py migrate


echo "===Starting server==="
gunicorn stihtok.wsgi --bind 0.0.0.0:8000