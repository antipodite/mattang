# syntax=docker/dockerfile:1

FROM debian:bullseye

WORKDIR /mattang

COPY requirements.txt requirements.txt

RUN apt update
RUN apt install -y python3-pip python3-cartopy
RUN pip install -r requirements.txt

COPY . .
