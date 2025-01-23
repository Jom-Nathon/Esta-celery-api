# syntax=docker/dockerfile:1

FROM python:3.14.0a3-slim-bookworm
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /app/
EXPOSE 8010