#!/bin/sh
cd /justdoist
pip install uwsgi
python manage.py makemigrations main
python manage.py migrate
exec "$@"