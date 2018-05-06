#!/bin/sh
cd /justdoist
sleep 5
python manage.py makemigrations main
python manage.py migrate
if [ -d "static" ]; then
    rm -rf static
fi
python manage.py collectstatic
cd main && python fill_db.py
exec "$@"
