# syntax=docker/dockerfile:1

FROM fedora:latest

WORKDIR /mattang

COPY requirements.txt requirements.txt

RUN dnf install -y python-pip python-cartopy
RUN pip install -r requirements.txt
RUN touch /langdata

COPY . .
