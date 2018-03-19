# flik

[![Build Status](https://travis-ci.org/rsteube/flik.svg?branch=master)](https://travis-ci.org/rsteube/flik)

**flik** is a command line client for [Proventis Blue Ant](https://www.proventis.net/de/). It provides basic time tracking functionalities using dynamic [zsh command completion](https://github.com/zsh-users/zsh-completions/blob/master/zsh-completions-howto.org).

![demo](demo.svg)

## Install

Install using [pip](https://pip.pypa.io/en/stable/):
```sh
pip install git+https://github.com/rsteube/flik
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
fpath+=($(flik completion))
autoload -U compinit && compinit
```

### Windows

- install [Babun]
- update cygwin `$HOME/.babun/update.bat` (https://github.com/babun/babun/issues/720)
- start [Babun] and enter:

```bash
curl -sSL https://bootstrap.pypa.io/get-pip.py | python
pip install git+https://github.com/rsteube/flik
sed -i '1ifpath+=($(flik completion))\' ~/.zshrc
```
- restart [Babun]

## First use

- `flik login` (config stored in `~/.config/flik/config.yml` and password using the available [keyring](https://github.com/jaraco/keyring/))
- `flik sync` (updates cache in `~/.local/share/flik`)

## Limiting/blacklisting completion options
In case that you have more _projects_, _tasks_ or _activities_ assigned than you need for time tracking you can simply remove the corresponding entries from the cache files in `~/.local/share/flik`. Note that you have to redo this step after updating the cache using `flik sync`.

## Demo

```sh
docker-compose run flik
flik# flik login
flik# flik sync
flik# flik list
```

[Babun]:https://babun.github.io/
