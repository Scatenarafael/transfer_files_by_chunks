#!/bin/bash

cd /app/

export TERM=dumb
export DJANGO_SETTINGS_MODULE=core.settings


python3 manage.py makemigrations || true
# python manage.py runserver #"0.0.0.0:${APP_PORT}"
python3 manage.py migrate || true

python3 manage.py createsuperuser --no-input || true



# photondam_env/bin/gunicorn -c gunicorn.conf.py --worker-tmp-dir /dev/shm photonfuelAPI.wsgi:application --bind "0.0.0.0:${APP_PORT}" --reload
# # /opt/venv/bin/gunicorn --worker-tmp-dir /dev/shm photonfuelAPI.wsgi:application --bind "0.0.0.0:${APP_PORT}" --reload

python manage.py collectstatic --no-input
# celery -A core worker --loglevel=info --detach

gunicorn -c gunicorn_conf.py core.wsgi:application --reload