FROM python:2-alpine

RUN echo http://dl-3.alpinelinux.org/alpine/edge/community \
      >> /etc/apk/repositories \
 && apk add --no-cache zsh

ADD . /src
ADD ./docker/.zshrc /root/

RUN cd /src \
 && python setup.py install \
 && rm -rf /src \
 && mkdir /flik-console

WORKDIR /flik-console

CMD zsh

