FROM greatnonprofits/ccl-base:0.2

RUN mkdir /rapidpro
WORKDIR /rapidpro
RUN pip install --upgrade pip virtualenv
RUN virtualenv env
RUN . env/bin/activate
ADD pip-freeze.txt /rapidpro/pip-freeze.txt

RUN pip install -r pip-freeze.txt --upgrade
RUN pip install -U requests[security]
ADD . /rapidpro
COPY docker.settings /rapidpro/temba/settings.py

RUN bower install --allow-root
RUN python manage.py collectstatic --noinput

RUN touch `echo $RANDOM`.txt

# nginx + gunicorn setup
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

RUN rm -f /etc/nginx/sites-enabled/default
RUN ln -sf /rapidpro/nginx /etc/nginx/sites-enabled/

RUN rm -f /rapidpro/temba/settings.pyc

EXPOSE 8000

COPY entrypoint.sh /

CMD ["/entrypoint.sh"]
