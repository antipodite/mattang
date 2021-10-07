# syntax=docker/dockerfile:1

FROM debian:bullseye

WORKDIR /mattang

RUN apt update
RUN apt install -y python3-pip \
                   python3-cartopy \
                   python3-matplotlib \
                   python3-numpy \
                   python3-pandas \
                   python3-scipy

COPY cartopy_feature_download.py .

RUN python3 cartopy_feature_download.py --no-warn physical

COPY . .
