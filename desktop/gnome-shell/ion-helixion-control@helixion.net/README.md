# ION Startup Connections GNOME Control

This GNOME Shell 42 extension exposes every currently configured ION
connection that starts with the user login and draws from this PC:

- **Helixion**: `ion-mcp-preview.service` on `127.0.0.1:8765` plus the
  `ion-browser` tunnel for `ion.helixion.net`.
- **GPT Actions**: `ion-action-gateway.service` on `127.0.0.1:8777` plus the
  `ion-actions` tunnel for `ion-actions.helixion.net`.
- **ChatOps**: `ion-chatops.service` on `127.0.0.1:8767`; local only.

Each switch is independent and persistent. ON enables and starts only that
group. OFF stops the tunnel before its local origin (where applicable), then
disables the group so it remains off at the next login.

Health checks validate exact unit identity, MainPID/process ownership,
loopback-only listeners, process counts, and the expected local/public ION
health contracts. One process per named tunnel is expected; the two distinct
Cloudflare tunnels are not duplicates.

The helper accepts only `status`, compatibility aliases `on`/`off` for
Helixion, and fixed group actions such as `actions-on` and `chatops-off`. It
never accepts arbitrary units, ports, URLs, or shell commands. Mutation
receipts are written under:

```text
~/.local/state/ion-helixion-control/receipts/
```

Disabled optional units such as `ion-cockpit-app.service` and
`ion-cosmos-preview.service` are outside this connection panel. Rollback is
non-destructive: disable the extension with
`gnome-extensions disable ion-helixion-control@helixion.net`.

## JOC cockpit desktop launcher (candidate)

- **`.desktop` entry:** `desktop/gnome-shell/share/applications/ion-joc-cockpit.desktop`
- **Health-gated opener:** `desktop/gnome-shell/share/ion-open-joc-cockpit.sh`
- **Install:** `desktop/gnome-shell/install-ion-joc-cockpit-desktop.sh`
- **Panel menu:** opens `http://127.0.0.1:8765/cockpit#system` only when Helixion
  health is `healthy` (same gate as the `.desktop` launcher).
