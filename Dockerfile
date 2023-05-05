FROM python:3.11.2-alpine

RUN mkdir /app
COPY requirements.txt /app
COPY manage.py /app/
COPY api /app/api
COPY stihtok /app/stihtok

WORKDIR /app
RUN pip install -r requirements.txt
