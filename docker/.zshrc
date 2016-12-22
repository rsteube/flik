PS1=$'%{\e[0;36m%}flik-console %{\e[0m%}'

zstyle ':completion:*' menu select
fpath=($(flik completion) $fpath)
autoload -U compinit && compinit
