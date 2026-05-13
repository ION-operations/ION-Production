# Repository layout (blueprint)

Top-level layout follows **AIM-OS-GIT** conventions so scripts, imports, and docs keep valid relative paths.

## Layer 0 — Meta (this project only)

| Path | Role |
|------|------|
| `project_blueprint/` | Human blueprint; safe to extend; not required at runtime. |
| `AIM_ION_OVERVIEW.md` | Short pointer at repo root. |

## Layer 1 — Operational spine (code + entrypoints)

| Path | Role |
|------|------|
| `lucid_mcp_server.py` | Primary MCP tool surface (monolith entrypoint). |
| `packages/` | Libraries and apps (JOC, BAS, CMC, HHNI, VIF, …). |
| `scripts/` | Launchers, bridges, audits, MCP transport helpers. |
| `IDE/` | Tauri / context mapper seam (Lane A). |
| `pyproject.toml`, `requirements.txt`, `Makefile` | Python/tooling contracts. |

## Layer 2 — Coordination and truth

| Path | Role |
|------|------|
| `PROJECT_TRUTH/` | Evidence pack: canonical system index, operational spine, doc index. |
| `canon/` | Doctrine and audits (e.g. `canon/audits/system_audits/AUDIT_01_SYSTEM_MAP.md`). |
| `docs/` | Active governance and runbooks (smaller hub vs full `Documentation/`). |
| `.agent/` | Genomes, comms, agent protocol files. |

## Layer 3 — Documentation corpora

| Path | Role |
|------|------|
| `Documentation/` | Working documentation library. |
| `Documentation_Consolidated/` | Numbered consolidation (research papers, archive, architecture, …). |

## Layer 4 — Knowledge architecture

| Path | Role |
|------|------|
| `knowledge_architecture/` | Systems, applications, validation, AETHER memory (sizes vary vs FRESH). |

## Layer 5 — Data and persistence (copy-specific)

| Path | Role |
|------|------|
| `data/` | Databases, MCP mirrors, system maps (see `05_DATA_MEMORY_AND_GIT.md`). |
| `mcp_memory/` | MCP memory index surface. |
| `mcp_ai_messages.json`, `mcp_timeline_entries.json` | Root message/timeline stores (if present). |

## Layer 6 — Supporting / optional roots

Examples: `ideas/`, `north_star_project/`, `archive/`, `benchmarks/`, `deployment/`, `examples/`, `codex_workspace/`, `cursor-addon/`, `daemon_rag_system/`, `context_capsule_wire_and_mapper_v1/`, `ide_orchestration/`, `organized_root_files/`, `projects/`, `tests/`, `Testing/`.

Use **`SOURCE_OF_TRUTH.yaml`** and **`PROJECT_TRUTH/`** before trusting ad-hoc folder names alone.

## Intentionally empty after copy (regenerate)

- Any `**/node_modules/` — run `npm install` / `npm ci` per package (e.g. `packages/joc`, `packages/browser-automation-service`).
- No root `.venv/` — create Python venv from `requirements.txt` / `pyproject.toml` as needed.
