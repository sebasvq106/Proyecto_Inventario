FROM python:3.13
ENV PYTHONUNBUFFERED=1

WORKDIR /managment_system

COPY requirements.txt /managment_system/

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN apt-get update && apt-get install -y postgresql-client


COPY . /managment_system/