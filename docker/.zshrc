PS1=$'%{\e[0;36m%}flik-console %{\e[0m%}'

zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|=*' 'l:|=* r:|=*'

fpath=($(flik completion) $fpath)
autoload -U compinit && compinit
