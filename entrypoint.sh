#!/bin/bash

echo Collectstatic
python manage.py collectstatic --noinput

echo Compressor
python manage.py compress --extension=.haml --force

echo Starting gunicorn
gunicorn --timeout 90 --workers 3 --bind unix:/rapidpro/rapidpro.sock temba.wsgi:application &

echo Starting celery worker
celery worker -A temba -B -Q celery,handler,flows,msgs --autoscale 8,1 -n rapidpro.celery -l info &

echo Starting nginx
service nginx start
