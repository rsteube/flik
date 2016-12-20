FROM python:2-alpine

RUN echo http://dl-3.alpinelinux.org/alpine/edge/community \
      >> /etc/apk/repositories \
 && apk add --no-cache zsh \
                       asciinema

ADD . /src

RUN cd /src \
 && python setup.py install \
 && rm -rf /src

RUN echo -e "\
zstyle ':completion:*' menu select\n\
fpath=(\$(flik completion) \$fpath)\n\
autoload -U compinit && compinit"\
 > /root/.zshrc

CMD zsh

