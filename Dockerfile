FROM python:3.8-alpine
RUN apk update
RUN apk add curl sudo build-base unixodbc-dev unixodbc freetds-dev && pip install pyodbc

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt