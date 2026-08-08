#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
APPS_DIR="$DATA_HOME/applications"
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
LAUNCHER_SRC="$SCRIPT_DIR/share/ion-open-joc-cockpit.sh"
DESKTOP_SRC="$SCRIPT_DIR/share/applications/ion-joc-cockpit.desktop"
LAUNCHER_DEST="$BIN_DIR/ion-open-joc-cockpit"
DESKTOP_DEST="$APPS_DIR/ion-joc-cockpit.desktop"

install -d -m 0755 "$APPS_DIR" "$BIN_DIR"
install -m 0755 "$LAUNCHER_SRC" "$LAUNCHER_DEST"

sed "s|REPO_ROOT/desktop/gnome-shell/share/ion-open-joc-cockpit.sh|$LAUNCHER_DEST|g" \
    "$DESKTOP_SRC" >"$DESKTOP_DEST"
chmod 0644 "$DESKTOP_DEST"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPS_DIR" >/dev/null 2>&1 || true
fi

printf 'Installed %s and %s\n' "$DESKTOP_DEST" "$LAUNCHER_DEST"
