FROM python:2-alpine

ADD . /src

RUN cd /src \
 && python setup.py install \
 && rm -rf /src

