# flik

[![Build Status](https://travis-ci.org/rsteube/flik.svg?branch=master)](https://travis-ci.org/rsteube/flik)

**flik** is a command line client for [Proventis Blue Ant](https://www.proventis.net/de/). It provides basic time tracking functionalities using dynamic [zsh command completion](https://github.com/zsh-users/zsh-completions/blob/master/zsh-completions-howto.org).

![demo](demo.gif)

## Install

Install using [pip](https://pip.pypa.io/en/stable/):
```sh
sudo pip2 install git+https://github.com/rsteube/flik
```

Add completion plugin using [zgen](https://github.com/tarjoilija/zgen) or similar:
```
zgen load rsteube/flik
```

Or extend `fpath` manually:
```sh
#~/.zshrc
#
#zstyle ':completion:*' menu select
fpath=+($(flik completion))
autoload -U compinit && compinit
```

### Windows

- install [Babun]
- update cygwin `$HOME/.babun/update.bat` (https://github.com/babun/babun/issues/720)
- start [Babun] and enter:

```bash
curl -sSL https://bootstrap.pypa.io/get-pip.py | python
pip2 install git+https://github.com/rsteube/flik
sed -i '1ifpath+=($(flik completion))\' ~/.zshrc
```
- restart [Babun]

## First use

- `flik login` (config stored in `~/.config/flik/config.yml` and password using the available [keyring](https://github.com/jaraco/keyring/))
- `flik sync` (updates cache in `~/.local/share/flik`)

## Demo

```sh
docker-compose run flik
flik# flik login
flik# flik sync
flik# flik list
```

[Babun]:https://babun.github.io/
