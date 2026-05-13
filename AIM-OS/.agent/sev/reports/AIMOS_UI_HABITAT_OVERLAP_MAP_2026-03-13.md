# AIMOS UI Habitat Overlap Map - 2026-03-13

Status: evidence-only overlap map for `CONSOLIDATION-WORK-PACKAGE-02`

Purpose:
- describe overlap across operator-facing or habitat-adjacent surfaces visible on disk
- keep overlap visible without selecting a canonical surface

## 1. Surface Register

| Surface | Direct evidence | Observed role signal in this pass | Visible overlap signals |
|---|---|---|---|
| `packages/joc/` | `package.json` name `joc`; description `Joint Operations Center - Browser-based AIM-OS command surface`; top-level `src/`, `public/`, `electron/`, `dist/` | operator-facing command surface | overlaps with `IDE/` and `packages/ide_chat_app/` as operator-facing app shells; overlaps with `packages/joc-tournament/` through shared JOC framing |
| `packages/joc-tournament/` | `README.md` presents a `J.A.R.V.I.S. UI Tournament`; references `packages/joc/src/store/panelRegistry.ts`; top-level `builds/`, `references/`, `shared/` | tournament/reference surface around JOC UI | overlaps with `packages/joc/` by explicitly inheriting JOC canon and launch target `localhost:5011` |
| `packages/ide_chat_app/` | `package.json` name `ide-chat-app`; top-level `src/`, `public/`, `electron/`, `dist/`; many app-shell and launch docs | separate operator-facing Electron/chat app surface | overlaps with `packages/joc/` and `IDE/` as a desktop/Electron UI habitat with agent-facing controls |
| `IDE/` | `package.json` name `saios`; description `Sovereign AI Operating System - Multi-Agent LLM Orchestration with Bare-Metal Actuation`; top-level `src/`, `extensions/`, `docs/`, `wire_proof/` | standalone IDE / operator console habitat | overlaps with `packages/joc/` and `packages/ide_chat_app/` as an operator shell; overlaps with extension-style habitats via `extensions/` subtree |
| `cursor-addon/` | `package.json` name `aimos-cursor-addon`; description `UI elements and automation for AIM-OS MCP server integration`; top-level `src/`, `out/`, `resources/`, `tests/`, nested addon subtrees and extensive docs | Cursor host extension habitat | overlaps with `packages/antigravity-extension/` as an IDE-extension and MCP-integration surface |
| `packages/antigravity-extension/` | `package.json` name `antigravity-console`; description `Live MCP metrics, ghost bridge status, agent comms, and system health for AIM-OS autonomous agents`; top-level `src/`, `out/`, `media/`, versioned `.vsix` artifacts | Antigravity IDE extension habitat | overlaps with `cursor-addon/` as an IDE-extension and operator-monitoring surface; overlaps with operator-facing shells through metrics, comms, and health signals |

## 2. Overlap Clusters

### Cluster A - Operator command surfaces

Direct members:
- `packages/joc/`
- `packages/ide_chat_app/`
- `IDE/`

Why the overlap is direct:
- all three expose app-shell style frontends with `src/` trees and operator-facing framing
- `packages/joc/` explicitly names itself a command surface
- `packages/ide_chat_app/` is a separate AI/chat environment with Electron structure
- `IDE/` identifies itself as an operating-system style orchestration shell

### Cluster B - JOC canon and JOC-adjacent experimentation

Direct members:
- `packages/joc/`
- `packages/joc-tournament/`

Why the overlap is direct:
- `packages/joc-tournament/README.md` explicitly points back into `packages/joc/` canon files
- the tournament surface appears to be a design/build competition or exploration lane around the JOC surface

### Cluster C - IDE extension habitats

Direct members:
- `cursor-addon/`
- `packages/antigravity-extension/`

Why the overlap is direct:
- both are IDE-extension style surfaces with package manifests, `src/` trees, built output folders, and host-specific integration intent
- `cursor-addon/` frames itself around AIM-OS MCP integration in Cursor
- `packages/antigravity-extension/` frames itself around MCP metrics, comms, system health, Gemini CLI, and ghost/Ollama integration in Antigravity

### Cluster D - Shell plus extension adjacency

Direct members:
- `IDE/`
- `cursor-addon/`
- `packages/antigravity-extension/`

Why the overlap is direct:
- `IDE/` includes an `extensions/` subtree and operator-shell framing
- `cursor-addon/` and `packages/antigravity-extension/` are both host-extension habitats adjacent to that shell/operator-control space

## 3. Overlap Signals By Capability

| Capability signal | Surfaces showing it directly on disk |
|---|---|
| operator-facing shell/app | `packages/joc/`, `packages/ide_chat_app/`, `IDE/` |
| Electron or desktop-shell structure | `packages/joc/`, `packages/ide_chat_app/` |
| extension-host packaging/output | `cursor-addon/`, `packages/antigravity-extension/` |
| MCP client / integration intent | `packages/joc/`, `cursor-addon/`, `packages/antigravity-extension/` |
| design/reference/tournament layer | `packages/joc-tournament/` |
| high documentation density around one UI habitat | `packages/ide_chat_app/`, `cursor-addon/` |

## 4. Constraint

- this map records coexistence and adjacency only
- it does not decide which UI or habitat surface is canonical, current, preferred, or deprecated
