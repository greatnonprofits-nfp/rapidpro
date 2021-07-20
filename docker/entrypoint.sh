#!/bin/bash
set -e

case $1 in
    app)
        python3.6 manage.py compress --extension=.haml --force
        python3.6 docker/clear-compressor-cache.py
        python3.6 manage.py migrate --noinput
        envsubst '${NGINX_COURIER_URL} ${NGINX_MAILROOM_URL}' < docker/nginx.conf > /etc/nginx/sites-enabled/nginx.conf
        /usr/local/bin/supervisord -n -c docker/supervisor-app.conf
    ;;
    celery)
        python3.6 docker/clear-compressor-cache.py
        python3.6 manage.py migrate --noinput
        /usr/local/bin/supervisord -n -c docker/supervisor-celery.conf
    ;;

esac

exec "$@"