#!/bin/bash
# points Espanso's config dir at ../Espanso/.espanso (symlink), an existing config dir is kept as a backup; safe to run again
set -euo pipefail
cd "$(dirname "$0")/../Espanso/.espanso"

target=$(espanso path config 2>/dev/null || echo "$HOME/.config/espanso")

if [ -L "$target" ]; then
    rm "$target"
elif [ -e "$target" ]; then
    backup="$target.bak-$(date +%Y%m%d-%H%M%S)"
    mv "$target" "$backup"
    echo "Old config moved to $backup"
    # config/ is per machine (gitignored), take over the existing one
    if [ ! -e config ] && [ -d "$backup/config" ]; then
        cp -r "$backup/config" config
        echo "config/ copied from $backup"
    fi
fi

mkdir -p "$(dirname "$target")"
ln -s "$PWD" "$target"
echo "$target -> $PWD"

espanso restart 2>/dev/null || true
