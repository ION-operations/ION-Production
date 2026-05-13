# AIMOS JOC Cluster Surface Profile Matrix - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_07_2026-03-14`
Status: evidence-only comparative profile matrix

## Scope

This matrix compares the four required JOC-cluster surfaces directly:

- `packages/joc/`
- `IDE/`
- `packages/ide_chat_app/`
- `packages/joc-tournament/`

## Surface Matrix

| Surface | Primary host or runtime shape | Main technologies visible locally | Local code / file scale signals | Visible subsystems or major folders | Best-known intended role from docs and manifests |
| --- | --- | --- | --- | --- | --- |
| `packages/joc/` | Browser-first React/Vite app on port `5011`, with optional Electron shell via `electron/main.cjs` | React, Vite, Electron, Monaco, Zustand, TypeScript | `122` source files, `26` page files, `11` service files, `8` store files, `16` plan files | `src/pages`, `src/services`, `src/store`, `electron/`, `plans/`, `scripts/` | `package.json` calls it "Joint Operations Center — Browser-based AIM-OS command surface"; `docs/AUDIT_01_SYSTEM_MAP.md` records it as the JOC app and the main dispatch/session shell. |
| `IDE/` | Tauri desktop shell around local AIM-OS services | Tauri API, vanilla HTML/CSS/JS | `3` source files total, `6` visible tabs in `index.html`, `2` local docs | `src/`, `docs/`, `extensions/`, `wire_proof/` | `package.json` frames it as "Sovereign AI Operating System — Multi-Agent LLM Orchestration with Bare-Metal Actuation"; `src/main.js` implements tabs for dashboard, services, agents, console, vault, and SEER. |
| `packages/ide_chat_app/` | React/Vite/Electron application with environment-aware UI behavior between Electron and Cursor-extension contexts | React, Vite, Electron, Monaco, Zustand, Supabase, XYFlow, Tailwind | `222` source files, `143` component files, `29` service files, `7` Electron files, large launcher/doc set at package root | `src/components`, `src/services`, `src/store`, `src/contexts`, `electron/`, many launch/onboarding docs | `package.json` frames it as an AI consciousness development environment; onboarding docs describe a multi-tab dashboard with Agents, Chat, Chains, Tools, Timeline, drawers, bottom bar, and MCP integration over the extension command server. |
| `packages/joc-tournament/` | Comparative build and research corpus, not the main runtime shell | Markdown-heavy design corpus plus build directories for multiple agents | `8` build directories, `10305` files under `builds/`, `2` shared files, `2` reference files | `builds/`, `references/`, `shared/`, `README.md`, `HERITAGE_INDEX.md`, `RULES.md` | `README.md` frames it as "Everything you need to build the best AIM-OS command surface"; `HERITAGE_INDEX.md` positions it as the design-heritage and competitor index around the JOC canon. |

## Direct Notes

- `packages/joc/` is the broadest code-bearing JOC runtime surface in the local tree.
- `IDE/` is structurally much smaller than the other three surfaces, but its tabs and service map give it a distinct operator-shell role.
- `packages/ide_chat_app/` carries the densest local chat/dashboard/component footprint in this cluster.
- `packages/joc-tournament/` preserves comparative design work, laws, and competitor builds rather than acting as the main live cockpit.
