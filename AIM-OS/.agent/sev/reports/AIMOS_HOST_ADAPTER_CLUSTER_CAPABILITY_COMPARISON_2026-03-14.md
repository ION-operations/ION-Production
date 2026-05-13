# AIMOS Host Adapter Cluster Capability Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_09_2026-03-14`
Status: evidence-only comparative capability analysis

## Comparative Table

| Comparison axis | `packages/antigravity-extension/` | `cursor-addon/` | `packages/lucid_core_console/` |
| --- | --- | --- | --- |
| MCP or bridge relationship | Reads against repo-root `lucid_mcp_server.py`, `mcp_memory`, and related local stores; also polls a separate ghost bridge at `http://192.168.2.25:9090` for health and messages | Spawns workspace-root `lucid_mcp_server.py` as a subprocess, initializes MCP over stdio, and exposes a local HTTP control surface on `localhost:5001` through `CommandServer` | Primary live coupling is to an Aether daemon on `localhost:8080`; README describes integration with core AIM-OS systems, but the visible code is daemon-first rather than MCP-first |
| Host coupling | Tied to the Antigravity extension host, startup activation, workspace-root assumptions, and an operator-configured ghost bridge URL | Most tightly coupled to Cursor-style host behavior, editor-area dashboard patterns, workspace-root server spawning, and a long-lived local HTTP command server | Tied to a VS Code or Cursor extension host plus a separately running daemon, voice stack, and phone-remote path |
| Control and supervision role | Supervises health, agent roster, timeline, and bridge state from a dashboard posture; lighter on direct mutation governance | Supervises Cursor-side automation, model and memory flows, and command exposure to external clients; broader orchestration than explicit approval control | Strongest explicit governance surface in the cluster: file hooks detect create, modify, delete, and rename events and route approval, force-edit, or cancel actions through the daemon |
| Messaging or telemetry role | Strong on ghost messaging, system-health polling, mission snapshotting, and local status aggregation from genomes, status files, and message stores | Strong on internal routing and automation telemetry through message router, agent monitor, memory flows, and command endpoints for Cursor/editor/workspace state | Strong on timeline logging and console-session traceability, but narrower than siblings on broad multi-agent telemetry or external bridge messaging |
| Portability and operator dependence | Moderately portable as an extension package, but operationally dependent on repo-root layout, local state files, and optional external ghost bridge availability | Less portable because it assumes Cursor-host features plus workspace-root MCP startup and a resident command server; broad feature set increases environment dependence | Portable only where the daemon, voice path, and phone-pairing support exist; strongest operator dependence because approval actions and human-supervised mutation flow are core behaviors |

## Direct Comparative Reading

### `packages/antigravity-extension/` vs `cursor-addon/`

- `packages/antigravity-extension/` reads more like an always-on monitoring and comms console.
- `cursor-addon/` reads more like a full host-integration and automation layer for Cursor itself.

### `packages/antigravity-extension/` vs `packages/lucid_core_console/`

- `packages/antigravity-extension/` emphasizes live status, agent presence, and ghost-bridge messaging.
- `packages/lucid_core_console/` emphasizes supervised command execution, mutation approval, and audit logging.

### `cursor-addon/` vs `packages/lucid_core_console/`

- `cursor-addon/` owns the broadest host-automation and MCP-bridge surface in this cluster.
- `packages/lucid_core_console/` owns the strictest operator-control and file-governance surface.

## Net Comparative Answer

1. `packages/antigravity-extension/` is the strongest monitoring and comms dashboard in this cluster.
2. `cursor-addon/` is the strongest Cursor-native automation and MCP bridge surface in this cluster.
3. `packages/lucid_core_console/` is the strongest supervised command and mutation-governance surface in this cluster.

These are local comparative role answers only. They do not declare a canonical host path or merger target.
