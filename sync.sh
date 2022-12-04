#!/usr/bin/env bash

set -euo pipefail
trap "echo -e '\e[1;31mScript failed: see failed command above\e[0m'" ERR

wget --no-verbose -O _fzf https://raw.githubusercontent.com/junegunn/fzf/master/shell/completion.zsh
wget --no-verbose -O _zoxide https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/contrib/completions/_zoxide
wget --no-verbose -O _bat https://raw.githubusercontent.com/sharkdp/bat/master/assets/completions/bat.zsh.in
