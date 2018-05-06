#!/bin/sh
cd /justdoist
python manage.py makemigrations main
python manage.py migrate
if [ -d "static" ]; then
    rm -rf static
fi
python manage.py collectstatic
cd main && python fill_db.py
exec "$@"
