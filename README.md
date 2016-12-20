# flik[WIP]

[![Build Status](https://travis-ci.org/rsteube/flik.svg?branch=master)](https://travis-ci.org/rsteube/flik)

blue ant cli client

![demo](demo.gif)

## Install

```sh
pip2 install --user git+https://github.com/rsteube/flik
# needs ~/.local/bin in $PATH
```

```sh
#~/.zshrc
#
#zstyle ':completion:*' menu select
fpath=($(flik completion) $fpath)
autoload -U compinit && compinit
```

## Demo

```sh
docker-compose run flik
flik# flik login
flik# flik sync
flik# flik list
```
