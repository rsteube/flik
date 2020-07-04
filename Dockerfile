FROM python:3-slim

RUN apt-get update && apt-get install -y zsh python3-cryptography
RUN pip install keyring keyrings.alt

ADD ./docker/.zshrc /root/

ADD requirements.txt /
RUN pip install -r requirements.txt

ADD . /src
RUN cd /src \
 && python setup.py install

WORKDIR /flik-console

CMD zsh

