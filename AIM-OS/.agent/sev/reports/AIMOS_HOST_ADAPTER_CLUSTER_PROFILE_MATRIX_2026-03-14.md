# AIMOS Host Adapter Cluster Profile Matrix - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_09_2026-03-14`
Status: evidence-only host-adapter profile matrix

## Surface Matrix

| Surface | Host or runtime shape | Main technologies | Local file and subsystem scale | Major visible capabilities | Best-known intended role from docs and manifests | Direct evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `packages/antigravity-extension/` | VS Code or Cursor extension with an always-on activity-bar webview that activates on startup | TypeScript, VS Code extension API, webview provider, local file reads, HTTP bridge polling | `src/` contains `13` files across `2` subdirectories; major subsystems are `providers/consoleView.ts` plus services for MCP, bridge monitoring, mission control, genome reads, IDE automation, and model clients | Refreshable console view, message send/store-memory prompts, ghost bridge health and message polling, mission-control roster/timeline snapshot, MCP-backed system health and memory pulse | Antigravity-specific live console for MCP metrics, ghost bridge status, agent comms, and system health | `package.json` description and activation events; commands in `src/extension.ts`; bridge polling in `src/services/bridgeMonitor.ts`; repo-root MCP and `mcp_memory` assumptions in `src/services/mcpClient.ts`; roster/timeline reads in `src/services/missionControl.ts` |
| `cursor-addon/` | Cursor-focused extension that opens dashboard webviews in the editor area and starts a local HTTP command server | TypeScript, VS Code extension API, webviews, Node HTTP server, spawned MCP subprocess, message-routing utilities | `src/` contains `40` files across `10` subdirectories; visible subsystems include `mcp/`, `messaging/`, `memory/`, `crossModel/`, `models/`, `agent/`, and dashboard/webview providers | Dashboard panel, MCP process initialization, cross-model controls, memory store/retrieve flows, model selection, plan and confidence commands, local HTTP command server, agent monitoring hooks | Cursor host adapter and automation bridge into the AIM-OS MCP tool plane | `package.json` description and commands; manager wiring in `src/extension.ts`; HTTP control surface in `src/commandServer.ts`; workspace-root `lucid_mcp_server.py` spawn path in `src/mcp/mcpClient.ts` |
| `packages/lucid_core_console/` | VS Code or Cursor extension centered on a dedicated console view backed by a daemon client and mutation hooks | TypeScript, VS Code extension API, webview view provider, WebSocket daemon client, timeline logging, file-event hooks | `src/` contains `9` files across `1` subdirectory; major subsystems are console provider, daemon client, file hooks, phone remote, voice interface, and timeline logger | Console panel, daemon communication, voice input, phone pairing, mutation approval or force-edit actions, timeline logging, file-system hook registration | Aether command interface and supervised control surface with human approval gates, voice I/O, phone remote, and audit logging | `package.json` description and commands; subsystem wiring in `src/extension.ts`; hard-gate behavior in `src/fileHooks.ts`; operator-facing role statements in `README.md` |

## Net Local Reading

1. `packages/antigravity-extension/` is the lightest always-on monitoring surface in this cluster.
2. `cursor-addon/` is the deepest Cursor-native integration surface and the broadest automation bridge.
3. `packages/lucid_core_console/` is the most explicit supervised command console with mutation-control and audit semantics.
