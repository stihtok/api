FROM python:3.11.2-alpine

COPY requirements.txt /
COPY entrypoint.sh /

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && pip install -r /requirements.txt \
    && apk del --no-cache .build-deps \
    && apk --no-cache add libpq \
    && mkdir /app

COPY manage.py /app/
COPY api /app/api
COPY stihtok /app/stihtok

WORKDIR /app

CMD ["/entrypoint.sh"]