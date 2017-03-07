# flik

[![Build Status](https://travis-ci.org/rsteube/flik.svg?branch=master)](https://travis-ci.org/rsteube/flik)

Blue Ant CLI client.

![demo](demo.gif)

## Install

```sh
pip2 install --user git+https://github.com/rsteube/flik@v0.9
# needs ~/.local/bin in $PATH
```

```sh
#~/.zshrc
#
#zstyle ':completion:*' menu select
fpath=($(flik completion) $fpath)
autoload -U compinit && compinit
```

### Windows

- install [Babun]
- update cygwin `$HOME/.babun/update.bat` (https://github.com/babun/babun/issues/720)
- start [Babun] and enter:

```bash
curl -sSL https://bootstrap.pypa.io/get-pip.py | python
pip2 install git+https://github.com/rsteube/flik
sed -i '1ifpath=($(flik completion) $fpath)\' ~/.zshrc
```
- restart [Babun]

## Demo

```sh
docker-compose run flik
flik# flik login
flik# flik sync
flik# flik list
```

[Babun]:https://babun.github.io/
