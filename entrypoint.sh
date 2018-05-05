#!/bin/sh
cd /justdoist
pip install uwsgi
python manage.py makemigrations main
python manage.py migrate
python manage.py collectstatic
cd main && python fill_db.py
exec "$@"
