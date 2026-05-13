#!/bin/bash
# ═══════════════════════════════════════════════════════
# MCP Fallback Server — Auto-Start Setup Script
# ═══════════════════════════════════════════════════════
#
# Installs the MCP HTTP fallback server as a systemd user service
# so it always runs and auto-restarts on failure.
#
# Usage:
#   bash scripts/setup_mcp_autostart.sh
#
# To uninstall:
#   systemctl --user stop aimos-mcp-fallback
#   systemctl --user disable aimos-mcp-fallback
#   rm ~/.config/systemd/user/aimos-mcp-fallback.service
#   systemctl --user daemon-reload

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SERVICE_FILE="$SCRIPT_DIR/aimos-mcp-fallback.service"
USER_SERVICE_DIR="$HOME/.config/systemd/user"

echo "═══════════════════════════════════════════"
echo "  AIM-OS MCP Fallback — Auto-Start Setup"
echo "═══════════════════════════════════════════"

# Detect Python
if [ -f "$REPO_ROOT/.venv/bin/python" ]; then
    MCP_PYTHON="$REPO_ROOT/.venv/bin/python"
elif command -v python3 &>/dev/null; then
    MCP_PYTHON="$(which python3)"
else
    echo "❌ No Python found. Please create a venv at $REPO_ROOT/.venv"
    exit 1
fi

echo "  Repo root:  $REPO_ROOT"
echo "  Python:     $MCP_PYTHON"
echo "  Service:    $SERVICE_FILE"

# Create user systemd dir
mkdir -p "$USER_SERVICE_DIR"

# Generate service file with correct paths
cat > "$USER_SERVICE_DIR/aimos-mcp-fallback.service" <<EOF
[Unit]
Description=AIM-OS MCP HTTP Fallback Server
After=network.target

[Service]
Type=simple
Environment=AIMOS_ROOT=$REPO_ROOT
Environment=MCP_PYTHON=$MCP_PYTHON
WorkingDirectory=$REPO_ROOT
ExecStart=$MCP_PYTHON $REPO_ROOT/scripts/mcp_http_fallback_server.py --port 5001 --host 127.0.0.1
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

echo ""
echo "  📋 Service file written to: $USER_SERVICE_DIR/aimos-mcp-fallback.service"

# Reload, enable, start
systemctl --user daemon-reload
systemctl --user enable aimos-mcp-fallback
systemctl --user start aimos-mcp-fallback

echo ""
echo "  ✅ MCP fallback server started and enabled"
echo ""
echo "  Commands:"
echo "    Status:   systemctl --user status aimos-mcp-fallback"
echo "    Logs:     journalctl --user -u aimos-mcp-fallback -f"
echo "    Stop:     systemctl --user stop aimos-mcp-fallback"
echo "    Restart:  systemctl --user restart aimos-mcp-fallback"
echo ""

# Quick health check
sleep 1
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001/health | grep -q "200"; then
    echo "  🟢 Fallback server is responding on port 5001"
else
    echo "  🟡 Server starting up... (may take a moment for first-time init)"
fi
