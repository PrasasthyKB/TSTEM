FROM python:3.10

COPY ./src/ /src/

WORKDIR /src

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD gunicorn --worker-class gevent --workers 8 --bind 0.0.0.0:5000 wsgi:app --max-requests 10000 --timeout 5 --keep-alive 5 --log-level info
