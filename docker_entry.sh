#!/usr/bin/env bash
if [ "$MIGRATE" = "1" ]; then
    python3 manage.py db migrate
    python3 manage.py db upgrade
fi

if [ "$MIGRATE" = "2" ]; then
    python3 manage.py recreate_db
fi


python3 manage.py runserver -h 0.0.0.0 -p 5000
#gunicorn -b 0.0.0.0:5000 -w 9 wsgi:app
