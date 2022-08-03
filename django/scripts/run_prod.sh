#!/bin/bash -xe


wait-for-it $DJANGO_DB_HOST:$DJANGO_DB_PORT
gunicorn mapswipe.wsgi:application --bind 0.0.0.0:80 --access-logfile '-' --error-logfile '-'
