# AIM-OS-GIT Domain Map — Complete Directory Classification

> **Phase:** G1 Survey & Classify
> **Date:** 2026-03-24
> **Scope:** All 67 top-level directories + 31 root files in AIM-OS-GIT
> **Rule:** COPY into canon/, never delete originals

---

## Classification Key

| Code | Meaning | Canon Action |
|------|---------|-------------|
| **CORE** | Essential active system | Copy to canon/systems/ or canon/doctrine/ |
| **REORG** | Valuable but needs reorganization | Copy relevant parts to appropriate canon/ section |
| **ARCHIVE** | Historical value, not active | Copy summary to canon/history/ |
| **BLOAT** | Duplicate, dead, or superseded | Log in canon/bloat_registry/ |
| **IGNORE** | Not relevant to AIM-OS mission | Skip (per Braden directive) |

---

## Directory Classifications

### CORE — Essential Active Systems

| Dir | Size | Files | Classification | Canon Target | Summary |
|-----|------|-------|---------------|-------------|---------|
| `.agent/` | — | ~50 | CORE | canon/agents/ | Agent ecosystem: genomes, bootloader, comms, capsules, status files. THE control plane. |
| `packages/` | 44MB | 11,493 | CORE | canon/systems/ | All 8 AIM-OS packages (CMC, HHNI, SEG, VIF, APOE, CAS, TCS) + JOC + 60+ more. Primary codebase. |
| `docs/` | 4.6MB | 282 | CORE | canon/doctrine/ + canon/systems/ | Aether-OS constitution, atlas, kernel, interface + ION audits + orchestration docs. |
| `config/` | 24K | 4 | CORE | canon/builds/ | Configuration files for the system. |
| `data/` | 12MB | 40 | CORE | canon/systems/ion/ | Data directory (ions should live here). |
| `src/` | 112K | 8 | CORE | canon/systems/ | Source modules. |
| `canon/` | 148K | 2 | CORE | (IS canon/) | The canon directory itself (already created). |

### REORG — Valuable, Needs Organization

| Dir | Size | Files | Classification | Canon Target | Summary |
|-----|------|-------|---------------|-------------|---------|
| `scripts/` | 4.2MB | 310 | REORG | canon/builds/ + canon/systems/ | Agent comms, AI engine, MCP bridge, assembly scripts. Mix of active and legacy. |
| `tests/` | 248K | 32 | REORG | canon/builds/ | Test suite for ion/packages. |
| `Testing/` | 529K | 529 | REORG | canon/builds/ | Additional test infrastructure. |
| `analysis/` | 4.2MB | 66 | REORG | canon/audits/ | System analysis: architecture, complexity metrics, core maps. |
| `coordination/` | 2.1MB | 201 | REORG | canon/history/ | 2025-10-21 dated coordination docs, agent syncs. Historical. |
| `goals/` | 268K | 37 | REORG | canon/north_star/ | Goal tracking, plans, master plan index. |
| `plans/` | 180K | 12 | REORG | canon/north_star/ | Strategic plans. |
| `ideas/` | 752K | 74 | REORG | canon/history/ | Ideas index, brainstorming docs. |
| `active_work/` | 100K | 12 | REORG | canon/doctrine/ | Move ledger, org docs, plans, summaries. Current work tracking. |
| `north_star_project/` | 6.1MB | 265 | REORG | canon/north_star/ | Chapters, agents, chains, codex analysis. The north star book project. |
| `PROJECT_TRUTH/` | 88K | 9 | REORG | canon/doctrine/ | Canonical system index, canonical doc index. Truth anchors. |
| `mcp_memory/` | 2.5MB | 175 | REORG | canon/systems/mcp/ | MCP memory store files. Active runtime data. |
| `snapshots/` | 888K | 25 | REORG | canon/history/ | System state snapshots. |
| `evidence/` | 12K | 1 | REORG | canon/audits/ | Evidence tracking (single file). |
| `deployment/` | 24K | 4 | REORG | canon/builds/ | Deployment configs. |
| `examples/` | 12K | 1 | REORG | canon/systems/ | Example files. |
| `runs/` | 40K | 5 | REORG | canon/builds/ | Run outputs. |
| `ui/` | 68K | 4 | REORG | canon/apps/ | UI components. |
| `benchmarks/` | 12MB | 9 | REORG | canon/builds/ | Benchmark data and results. |
| `organized_root_files/` | 340K | 33 | REORG | (distribute) | Previously organized root files — check for useful content. |

### ARCHIVE — Historical Value

| Dir | Size | Files | Classification | Canon Target | Summary |
|-----|------|-------|---------------|-------------|---------|
| `archive/` | 7.1MB | 499 | ARCHIVE | canon/history/ | Mixed archive: achievements, announcements, old analyses, scripts. |
| `knowledge_architecture/` | 189MB | 37,352 | ARCHIVE | canon/history/knowledge_architecture/ | MASSIVE knowledge corpus. 130+ session indexes, atlas indexes, future plans. Historical gold mine but huge. |
| `legacy_docs/` | 1.4MB | 76 | ARCHIVE | canon/history/ | Explicitly marked legacy. |
| `backups/` | 924K | 35 | ARCHIVE | canon/history/ | Backup files. |
| `cursor-addon/` | 6.3MB | 687 | ARCHIVE | canon/apps/ (summary only) | Cursor IDE addon — aether analysis, architecture, UI directives. Historical cursor work. |
| `ide_orchestration/` | 22MB | 1,458 | ARCHIVE | canon/history/ | IDE orchestration chains, panel inventories. Historical. |
| `codex-systems/` | 2.0MB | 124 | ARCHIVE | canon/history/ | 3D systems: animation, audio, camera, geometry. Codex-era work. |
| `codex_workspace/` | 108K | 10 | ARCHIVE | canon/history/ | Codex agent workspace. |
| `daemon_rag_system/` | 1.1MB | 52 | ARCHIVE | canon/systems/ (summary only) | RAG system prototype: ah_protocol, context analysis engine. |
| `context_capsule_wire_and_mapper_v1/` | 1.2MB | 60 | ARCHIVE | canon/systems/ (summary only) | Early capsule system v1. Historical precursor to current capsule. |
| `context/` | 40K | 8 | ARCHIVE | canon/history/ | Early context management files. |

### BLOAT — Duplicate or Dead

| Dir | Size | Files | Classification | Canon Target | Issue |
|-----|------|-------|---------------|-------------|-------|
| `Documentation/` | 544MB | 5,607 | BLOAT | canon/bloat_registry/ | **MASSIVE.** Superseded by Documentation_Consolidated. Contains .docx, scattered .md, appexamples. |
| `Documentation_Consolidated/` | 813MB | 1,602 | BLOAT | canon/bloat_registry/ | Even larger consolidated version. 13 numbered categories. Useful index but too large to copy. Reference only. |
| `audit/` | 580K | 61 | BLOAT | canon/bloat_registry/ | **Duplicate of `audits/`** — different contents but overlapping purpose. |
| `audits/` | 788K | 42 | BLOAT | canon/bloat_registry/ | **Duplicate of `audit/`** — consolidate both into canon/audits/. |
| `schema/` | 8K | 1 | BLOAT | canon/bloat_registry/ | **Duplicate of `schemas/`** — single file. |
| `schemas/` | 8K | 1 | BLOAT | canon/bloat_registry/ | **Duplicate of `schema/`** — single file. |
| `test_data_priority1/` | 28K | 4 | BLOAT | canon/bloat_registry/ | **Triplicate** with format and linkage variants. |
| `test_data_priority1_format/` | 28K | 4 | BLOAT | canon/bloat_registry/ | **Triplicate.** |
| `test_data_priority1_linkage/` | 28K | 4 | BLOAT | canon/bloat_registry/ | **Triplicate.** |
| `test_mcp_configs/` | 20K | 4 | BLOAT | canon/bloat_registry/ | MCP test configs — likely stale. |
| `test_mcp_memory/` | 168K | 18 | BLOAT | canon/bloat_registry/ | MCP test memory files — likely stale. |
| `__pycache__/` | 448K | 1 | BLOAT | canon/bloat_registry/ | Python cache — should be gitignored. |
| `tmp/` | 8K | 0 | BLOAT | canon/bloat_registry/ | Empty temp dir. |
| `diagnostics/` | 52K | 1 | BLOAT | canon/bloat_registry/ | Single diagnostic file. |
| `forcing_test_flip/` | 16K | 3 | BLOAT | canon/bloat_registry/ | Test flip files. |
| `artifacts/` | 80K | 5 | BLOAT | canon/bloat_registry/ | Stale artifacts — assess content. |

### IGNORE — Per Braden Directive

| Dir | Size | Files | Classification | Notes |
|-----|------|-------|---------------|-------|
| `forensics_backups/` | 4MB | 259 | IGNORE | 3D projects (shadertoy, volumetric clouds). Braden: "ignore the apps folder with those 3d projects" |
| `echo-forge-loop/` | 4K | 0 | IGNORE | Empty directory. |
| `images/` | 380K | 1 | IGNORE | Single image file. |

### SPECIAL — Require Individual Handling

| Dir | Size | Files | Classification | Notes |
|-----|------|-------|----------------|-------|
| `.gemini/` | — | — | SPECIAL | Gemini IDE config. Don't touch. |
| `.claude/` | — | — | SPECIAL | Claude config. Don't touch. |
| `.vscode/` | — | — | SPECIAL | VS Code config. Don't touch. |
| `.github/` | — | — | SPECIAL | GitHub config. Don't touch. |
| `.git/` | — | — | SPECIAL | Git repo. Don't touch. |
| `IDE/` | 1.7MB | 49 | SPECIAL | IDE extension source: context_mapper_lab, wire_proof, extensions. Assess value vs cursor-addon. |
| `UIeditor/` | 524K | 35 | SPECIAL | UI editor component. Assess if active or legacy. |
| `mcp-aether/` | 52K | 3 | SPECIAL | MCP-Aether bridge. Small but potentially important. |
| `orchestration_templates/` | 104K | 6 | SPECIAL | Agent orchestration templates. May belong in canon/agents/. |
| `projects/` | 52K | 3 | SPECIAL | Project definitions. Small. |
| `bootloaders/` | 12K | 2 | SPECIAL | Bootloader files (may overlap with .agent/BOOTLOADER.md). |

---

## Root Files Classification

| File | Size | Classification | Canon Target |
|------|------|---------------|-------------|
| `AIM_OS_NORTH_STAR.md` | 27KB | REORG | canon/north_star/ (basis for v3) |
| `AGENTS.md` | 5KB | CORE | canon/agents/ |
| `README.md` | 10KB | CORE | canon/ (root readme) |
| `SOURCE_OF_TRUTH.yaml` | 20KB | CORE | canon/doctrine/ |
| `PACKAGE_MANIFEST.md` | 3KB | CORE | canon/builds/ |
| `pyproject.toml` | 5KB | CORE | canon/builds/ |
| `requirements.txt` | 1.2KB | CORE | canon/builds/ |
| `Makefile` | 3KB | CORE | canon/builds/ |
| `lucid_mcp_server.py` | 571KB | CORE | canon/systems/mcp/ (reference only — too large) |
| `README_CONTENT_PLAN.md` | 22KB | BLOAT | canon/bloat_registry/ |
| `README_REORGANIZATION_PLAN.md` | 9KB | BLOAT | canon/bloat_registry/ |
| `10_MODES_SUMMARY.md` | 3KB | REORG | canon/doctrine/ |
| `MAPPING_COMPLETE_SUMMARY.md` | 4KB | REORG | canon/doctrine/ |
| `DO_NOT_TOUCH_MCP.md` | 1KB | CORE | canon/systems/mcp/ |
| `.sdfcvf.config.yaml` | 11KB | CORE | canon/systems/vif/ |
| `lucid_mcp_server.py.bak` | 567KB | BLOAT | canon/bloat_registry/ |
| `mcp_tester.py` | 1KB | REORG | canon/systems/mcp/ |
| `mcp_ai_messages.json` | 7KB | REORG | canon/systems/mcp/ (runtime data) |
| `mcp_timeline_entries.json` | 11KB | REORG | canon/systems/mcp/ (runtime data) |
| `mcp_err.log` / `mcp_out.log` | 56KB | BLOAT | canon/bloat_registry/ (logs) |
| `mesh_visualization.html` | 30KB | IGNORE | 3D visualization file |
| `dummy` | 130B | BLOAT | canon/bloat_registry/ |
| `run_mcp_*.py` | 2KB | REORG | canon/systems/mcp/ |
| `pyrightconfig.json` | 385B | SPECIAL | IDE config — don't touch |
| `.cursorrules` | 770B | SPECIAL | IDE config — don't touch |
| `.editorconfig` | 260B | SPECIAL | IDE config — don't touch |
| `.gitignore` | 3KB | SPECIAL | Git config — don't touch |
| `.gitattributes` | 394B | SPECIAL | Git config — don't touch |
| `LAUNCH_AETHER.bat` | 289B | REORG | canon/builds/ |

---

## Summary Statistics

| Category | Dirs | Files | Size | % of Total |
|----------|------|-------|------|-----------|
| **CORE** | 7 | ~11,879 | ~61MB | 18.6% |
| **REORG** | 21 | ~1,281 | ~34MB | 2.0% |
| **ARCHIVE** | 11 | ~40,441 | ~233MB | 63.3% |
| **BLOAT** | 16 | ~7,750 | ~1.4GB | 12.1% |
| **IGNORE** | 3 | ~260 | ~4.4MB | 0.4% |
| **SPECIAL** | 9 | ~100 | ~2.5MB | 0.2% |

> **Key Insight:** 63% of files are ARCHIVE (historical but mostly `knowledge_architecture/` at 37K files). 12% are BLOAT (mostly `Documentation/` and `Documentation_Consolidated/` at 1.4GB combined). Only ~19% are CORE active systems.

---

## High-Priority Copy Queue (Phase G2)

1. `docs/Aether-OS/*.md` → canon/constitution/ + canon/doctrine/
2. `.agent/` key files → canon/agents/
3. `SOURCE_OF_TRUTH.yaml` → canon/doctrine/
4. `PROJECT_TRUTH/` → canon/doctrine/
5. `AIM_OS_NORTH_STAR.md` → canon/north_star/ (as basis for v3)
6. `packages/` → canon/systems/ (summaries, not full code)
7. `audit/` + `audits/` → canon/audits/ (merged)
8. `analysis/` → canon/audits/
9. `goals/` + `plans/` → canon/north_star/
10. `scripts/` key files → canon/builds/

---

*Classification complete. 67 directories + 31 root files categorized.*
*Ready for Phase G2: Copy & Organize.*
