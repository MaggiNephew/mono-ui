#!/usr/bin/env bash
# Copy the generated rice files (dist/rice) into your config.
#
#   gen/install-rice.sh            dry run: show what would change, change nothing
#   gen/install-rice.sh --apply    back up the current files, then copy
#
# Replaced in place (same format as today):
#   ~/.config/hypr/colors.lua, ~/.config/quickshell/colors.qml,
#   ~/.config/qt6ct/colors/mono-dark.conf, ~/.local/share/color-schemes/MonoBW.colors
# Added next to your configs (nothing uses them until you include them):
#   ~/.config/kitty/mono-colors.conf, ~/.config/foot/mono-colors.ini,
#   ~/.config/hypr/mono-look.lua, ~/.config/starship-mono-palette.toml
#
# Note: hypr/colors.lua and quickshell/colors.qml are written by matugen. If matugen
# regenerates them (e.g. on a wallpaper change), it will overwrite these copies.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
D="$ROOT/dist/rice"
CFG="${XDG_CONFIG_HOME:-$HOME/.config}"
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1

[[ -d "$D" ]] || { echo "dist/rice not found. Run: python3 gen/build.py rice" >&2; exit 1; }

pairs=(
  "$D/hypr/colors.lua|$CFG/hypr/colors.lua"
  "$D/quickshell/colors.qml|$CFG/quickshell/colors.qml"
  "$D/qt6ct/colors/mono-dark.conf|$CFG/qt6ct/colors/mono-dark.conf"
  "$D/color-schemes/MonoBW.colors|$DATA/color-schemes/MonoBW.colors"
  "$D/kitty/mono-colors.conf|$CFG/kitty/mono-colors.conf"
  "$D/foot/mono-colors.ini|$CFG/foot/mono-colors.ini"
  "$D/hypr/mono-look.lua|$CFG/hypr/mono-look.lua"
  "$D/starship/palette.toml|$CFG/starship-mono-palette.toml"
)

backup="$CFG/mono-ui-backup-$(date +%Y%m%d-%H%M%S)"
changed=0
for p in "${pairs[@]}"; do
  src="${p%%|*}"; dst="${p##*|}"
  if [[ -f "$dst" ]] && cmp -s "$src" "$dst"; then
    echo "  same     $dst"
    continue
  fi
  changed=$((changed + 1))
  if [[ -f "$dst" ]]; then
    echo "  changes  $dst"
    diff -u "$dst" "$src" | sed -n '3,40p' | sed 's/^/           /' || true
  else
    echo "  new      $dst"
  fi
  if (( APPLY )); then
    if [[ -f "$dst" ]]; then
      mkdir -p "$backup/$(dirname "${dst#$HOME/}")"
      cp -p "$dst" "$backup/${dst#$HOME/}"
    fi
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
  fi
done

if (( changed == 0 )); then
  echo "Nothing to do: your files already match the tokens."
elif (( APPLY )); then
  [[ -d "$backup" ]] && echo "Backed up the old files to $backup"
  echo "Done. Reload: hyprctl reload; restart quickshell; reopen Qt/KDE apps."
else
  echo "$changed file(s) would change. Run again with --apply to write them."
fi
