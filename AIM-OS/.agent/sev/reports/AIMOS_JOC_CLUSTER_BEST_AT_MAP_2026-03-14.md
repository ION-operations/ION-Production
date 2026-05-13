# AIMOS JOC Cluster Best-At Map - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_07_2026-03-14`
Status: evidence-only comparative answer map

## Best-At Answers

| Surface | What it appears best at locally | Where it seems narrower than siblings | Unique value preserved locally | Direct evidence |
| --- | --- | --- | --- | --- |
| `packages/joc/` | Best at acting as the broadest mission-control runtime surface for AIM-OS operations | Narrower than `packages/ide_chat_app/` in chat-heavy experimentation and narrower than `packages/joc-tournament/` in design-heritage coverage | Preserves the richest operational page map in this cluster: dispatch, session, diagnostics, vault, infrastructure, compute, oracle, and synthesizer flows in one runtime app | `26` page files; `11` services; `8` stores; `docs/AUDIT_01_SYSTEM_MAP.md` identifies it as the JOC app; `package.json` describes it as the browser-based command surface |
| `IDE/` | Best at being a lightweight desktop operations wrapper for live service state, vault controls, console input, and SEER access | Narrower than `packages/joc/` and `packages/ide_chat_app/` in source depth and application breadth; narrower than `packages/joc-tournament/` in comparative design history | Preserves a compact Tauri-hosted operator shell with six explicit tabs and direct local service-monitor semantics around MCP, BAS, vault, and SEER | `IDE/src/main.js` implements dashboard, services, agents, console, vault, and SEER tabs; `index.html` exposes six tab targets; `package.json` is Tauri-only |
| `packages/ide_chat_app/` | Best at combining AI chat, agent-management, orchestration, telemetry, and development-environment experimentation in one dense UI surface | Narrower than `packages/joc/` in explicit dispatch/session/cockpit framing and narrower than `packages/joc-tournament/` in preserved heritage/build comparison | Preserves the densest UI and service layer in the cluster, including large component and service counts plus an Electron/Cursor-aware MCP integration path | `143` component files; `29` services; onboarding docs describe MainDashboard, drawers, bottom bar, chat/chains/tools/timeline tabs, and MCP calls through `mcpApi.ts` |
| `packages/joc-tournament/` | Best at preserving comparative JOC design heritage and multi-agent build experimentation | Narrower than the other three as a live operator runtime, since it is not the main cockpit shell | Preserves the design laws, competitor builds, prototype lineage, and build arena that let the team compare multiple command-surface directions directly | `README.md` frames the tournament purpose; `HERITAGE_INDEX.md` organizes laws, prototypes, and references; `builds/` contains `8` build lanes tied back to the JOC canon |

## Net Comparative Answer

1. `packages/joc/` appears best at the actual operations-cockpit runtime.
2. `IDE/` appears best at compact desktop service supervision and control.
3. `packages/ide_chat_app/` appears best at chat-rich, telemetry-rich AI development workflow.
4. `packages/joc-tournament/` appears best at preserving and testing alternative JOC directions.

These are role answers from the visible local tree. They do not declare a canon winner or reduce any surface to discard status.
