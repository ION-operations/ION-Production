#!/usr/bin/env bash
# Health-gated opener for local JOC cockpit on 127.0.0.1:8765 (candidate-only).
set -euo pipefail

COCKPIT_URL="http://127.0.0.1:8765/cockpit#system"
HEALTH_URL="http://127.0.0.1:8765/health"
TIMEOUT_S="${ION_COCKPIT_OPEN_TIMEOUT_S:-2}"

notify() {
    if command -v notify-send >/dev/null 2>&1; then
        notify-send "ION JOC Cockpit" "$1"
    else
        printf '%s\n' "$1" >&2
    fi
}

if ! curl -fsS --max-time "$TIMEOUT_S" "$HEALTH_URL" >/dev/null 2>&1; then
    notify "Preview not healthy on :8765. Enable ion-mcp-preview.service (user) first."
    exit 1
fi

if command -v xdg-open >/dev/null 2>&1; then
    exec xdg-open "$COCKPIT_URL"
fi

if command -v gio >/dev/null 2>&1; then
    exec gio open "$COCKPIT_URL"
fi

notify "No xdg-open or gio available to open the cockpit URL."
exit 1
