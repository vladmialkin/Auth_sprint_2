#!/bin/bash

python3 manage.py migrate &&
python3 manage.py compilemessages -l en -l ru &&
python3 manage.py collectstatic --noinput &&
gunicorn -w 3 config.wsgi:application --bind 0.0.0.0:8000
