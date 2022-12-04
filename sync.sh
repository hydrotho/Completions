#!/usr/bin/env bash

set -euo pipefail
trap "echo -e '\e[1;31mScript failed: see failed command above\e[0m'" ERR

wget --no-verbose -O _fzf https://raw.githubusercontent.com/junegunn/fzf/master/shell/completion.zsh
wget --no-verbose -O _zoxide https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/contrib/completions/_zoxide
wget --no-verbose -O _bat https://raw.githubusercontent.com/sharkdp/bat/master/assets/completions/bat.zsh.in
wget --no-verbose -O _fd https://raw.githubusercontent.com/sharkdp/fd/master/contrib/completion/_fd
TMPDIR=$(mktemp -d) || exit 1
TAG=$(curl -s https://api.github.com/repos/Peltoche/lsd/releases/latest | jq -r ".tag_name")
LSD=lsd-$TAG-x86_64-unknown-linux-musl
wget --no-verbose -P "$TMPDIR" "https://github.com/Peltoche/lsd/releases/download/$TAG/$LSD.tar.gz"
tar -xzf "$TMPDIR/$LSD.tar.gz" -C "$TMPDIR"
cp "$TMPDIR/$LSD/autocomplete/_lsd" .
rm -rf "$TMPDIR"
unset LSD
unset TAG
unset TMPDIR
wget --no-verbose -O _rg https://raw.githubusercontent.com/BurntSushi/ripgrep/master/complete/_rg
