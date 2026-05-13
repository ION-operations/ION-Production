# AIMOS Host Adapter Cluster Best-At Map - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_09_2026-03-14`
Status: evidence-only comparative answer map

## Best-At Answers

| Surface | What it appears best at locally | Where it seems narrower than siblings | Unique value preserved locally | Direct evidence |
| --- | --- | --- | --- | --- |
| `packages/antigravity-extension/` | Best at serving as a lightweight always-on host dashboard for live MCP health, ghost bridge status, agent comms, and mission snapshot visibility | Narrower than `cursor-addon/` in automation depth, host-command breadth, and Cursor-specific control; narrower than `packages/lucid_core_console/` in explicit approval and mutation-governance features | Preserves the clearest combined view of ghost bridge state plus local roster, timeline, and memory-backed system health in one extension surface | `package.json` describes live metrics, ghost bridge status, agent comms, and system health; `src/extension.ts` activates on startup and registers dashboard commands; `src/services/bridgeMonitor.ts` polls and messages the ghost bridge; `src/services/missionControl.ts` aggregates genomes, status files, messages, and atom counts |
| `cursor-addon/` | Best at acting as the deepest Cursor-native automation and MCP control bridge in the visible local organism | Narrower than `packages/lucid_core_console/` in hard-gated file supervision and dedicated console discipline; narrower than `packages/antigravity-extension/` in explicit ghost-bridge and mission-roster monitoring | Preserves the local command-server and Cursor-state control path that lets external or adjacent surfaces drive Cursor through HTTP while still tying back to the MCP server | `src/extension.ts` wires dashboard, cross-model, memory, plan, and confidence commands; `src/commandServer.ts` exposes `localhost:5001` endpoints for health, Cursor state, logs, problems, and MCP actions; `src/mcp/mcpClient.ts` spawns workspace-root `lucid_mcp_server.py` |
| `packages/lucid_core_console/` | Best at providing a supervised command console where human approval, mutation control, voice input, phone remote, and timeline audit stay in the center of the interaction model | Narrower than `cursor-addon/` in broad host automation and command-surface breadth; narrower than `packages/antigravity-extension/` in ambient bridge monitoring and agent-roster summarization | Preserves the strongest file-governance and operator-supervision semantics in this cluster, including explicit approve, force-edit, and cancel handling around detected mutations | `README.md` frames the surface as Aether's command interface with hard gates, voice I/O, phone remote, and timeline logging; `src/extension.ts` registers console, voice, phone, approve, and force-edit flows; `src/fileHooks.ts` detects file events and routes approval decisions through the daemon |

## Net Comparative Answer

1. `packages/antigravity-extension/` appears best at lightweight live monitoring and bridge-aware comms.
2. `cursor-addon/` appears best at deep Cursor integration and local automation bridging.
3. `packages/lucid_core_console/` appears best at supervised command execution and mutation governance.

The map stays comparative. It does not rank one host surface as the canon winner.
