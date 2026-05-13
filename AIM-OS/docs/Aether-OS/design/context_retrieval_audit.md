# AIM-OS Phase 0 Audit Report

**Generated:** 2026-03-11  
**Source:** Automated inventory scan of `/home/sev/AIM-OS-GIT`

---

## Executive Summary

| Metric | Count |
|--------|-------|
| Total files | ~52,000 |
| Total directories | ~4,950 |
| Top-level directories | 60 |
| Python files | 1,281 |
| Python lines | 408,617 |
| Markdown docs | 10,598 |
| Packages | 67 |
| Packages with tests | 35 |
| Packages with README | 39 |
| Packages with `__init__.py` | 43 |
| `_TAGGED` duplicate files | 115 |
| Repo size (excl .git) | 1.7 GB |

> [!CAUTION]
> 10,598 markdown files vs 1,281 Python files = **8.3:1 docs-to-code ratio**. The documentation IS the mess.

---

## Directory Classification

### CORE (Actual Code)
| Directory | Files | Size |
|-----------|-------|------|
| `packages/` | 1,791 | 24.2 MB |
| `scripts/` | 290 | 3.0 MB |
| `src/` | (small) | |
| `config/` | (small) | |
| `lucid_mcp_server.py` (root) | 1 file | 559 KB |

### DOCS (4 overlapping doc directories — **1.5 GB combined**)
| Directory | Files | Size |
|-----------|-------|------|
| `Documentation_Consolidated/` | 1,602 | **808 MB** |
| `Documentation/` | 5,607 | **530 MB** |
| `knowledge_architecture/` | 5,622 | 173 MB |
| `docs/` | 229 | 2.8 MB |
| `legacy_docs/` | 76 | 1.4 MB |

### DATA (Runtime artifacts mixed with code)
| Directory | Files |
|-----------|-------|
| `mcp_memory/` | 128 |
| `data/` | 40 |
| `snapshots/` | 25 |
| `backups/` | 33 |
| `forensics_backups/` | 259 |
| `test_mcp_memory/` | 18 |
| `mcp_ai_messages.json` (root) | 265 KB |
| `mcp_timeline_entries.json` (root) | 11 KB |

### APPS / EXPERIMENTS
| Directory | Files | Size |
|-----------|-------|------|
| `ide_orchestration/` | 1,458 | 18 MB |
| `cursor-addon/` | 687 | 4.7 MB |
| `echo-forge-loop/` | (app) | |
| `daemon_rag_system/` | 52 | |
| `codex-systems/` | 124 | |
| `codex_workspace/` | (workspace) | |
| `north_star_project/` | 265 | |
| `context_capsule_wire_and_mapper_v1/` | 60 | |
| `mcp-aether/` | (app) | |
| `IDE/`, `UIeditor/`, `ui/` | 49 + 35 + small | |

### TESTS (3 separate test directories)
| Directory | Files |
|-----------|-------|
| `Testing/` | 529 |
| `tests/` | 14 |
| `benchmarks/` | (some) |
| `test_data_priority1*/` | 3 dirs |
| `test_mcp_configs/` | (some) |

### META / PLANNING
| Directory | Files |
|-----------|-------|
| `coordination/` | 201 |
| `active_work/` | (workspace) |
| `goals/` | 37 |
| `plans/` | (planning) |
| `ideas/` | 74 |
| `projects/` | (project tracking) |
| `PROJECT_TRUTH/` | (source of truth) |
| `evidence/` | (evidence files) |
| `deployment/` | (deploy docs) |
| `diagnostics/` | (diag tools) |
| `orchestration_templates/` | (templates) |
| `archive/` | 264 |
| `organized_root_files/` | 33 |

### DUPLICATE / REDUNDANT PAIRS
| Pair | Files (A) | Files (B) |
|------|-----------|-----------|
| `audit/` vs `audits/` | 61 | 42 |
| `schema/` vs `schemas/` | 1 | 1 |
| `Testing/` vs `tests/` | 529 | 14 |

---

## Package Overlap Groups

> [!WARNING]
> 8 groups of packages with overlapping names/purposes. These need consolidation decisions.

### consciousness_* (5 packages)
- `consciousness_analyzer/`
- `consciousness_creativity_engine/`
- `consciousness_error_learning/`
- `consciousness_learning_engine/`
- `consciousness_optimization_detector/`

### mcp_* (4 packages)
- `mcp_data_integration/`
- `mcp_debugging_system/`
- `mcp_rag_proxy/`
- `mcp_server/`

### lucid_* (4 packages)
- `lucid_core_console/`
- `lucid_document_editor/`
- `lucid_mcp_server/`
- `lucid_orchestrator/`

### prompt* (2 packages)
- `prompt_chain_executor/`
- `prompt_chains/`

### quaternion_* (2 packages)
- `quaternion_kernel/`
- `quaternion_math/`

### router* (2 packages)
- `router/`
- `router_api_server/`

### apoe* (2 packages)
- `apoe/`
- `apoe_runner/`

### joc* (2 packages)
- `joc/`
- `joc-tournament/`

---

## Packages Missing `__init__.py` (25 of 67)

These are either not proper Python packages, or were never properly initialized:

```
advanced_monaco_editor, aimos_mobile_app, aimos-sdk,
autonomous_protocol, browser-automation-service, context_bootloader,
ide_chat_app, igodn, jarvis_injector, joc, joc-tournament,
lucid_core_console, lucid_document_editor, lucid_orchestrator,
lumin_snap_system, mcp_debugging_system, mcp_rag_proxy,
meta_reasoning, plix, prompt_chains, quaternion_kernel,
safety_systems, shared, timeline_context_system
```

---

## Package Complexity Leaders

| Package | Classes | AIM-OS Deps | Status |
|---------|---------|-------------|--------|
| `apoe` | 116 | 33 | Core system, heavily connected |
| `timeline_context_system` | 98 | 4 | Core system, many subsystems |
| `vif` | 78 | 28 | Core system, heavily connected |
| `cmc_service` | 67 | 10 | Core memory system |
| `sdfcvf` | 47 | 18 | Core verification system |
| `hhni` | 47 | 13 | Core retrieval system |
| `mcp_data_integration` | 37 | 0 | Island — zero AIM-OS deps |
| `autonomous_research_dream` | 31 | 1 | Lightly connected |
| `nl_tags` | 21 | 9 | Connected |
| `cas` | 20 | 1 | Lightly connected |
| `seg` | 15 | 19 | Heavily connected |

---

## Immediate Safe Actions (No-Risk)

These can be done now without any analysis:

1. **Merge duplicate dirs:** `audit/` + `audits/`, `schema/` + `schemas/`, `Testing/` + `tests/`
2. **Move data files out of root:** `mcp_ai_messages.json`, `mcp_timeline_entries.json` → `data/`
3. **Move root `.md` files:** `10_MODES_SUMMARY.md`, `MAPPING_COMPLETE_SUMMARY.md`, etc. → `docs/`
4. **Remove `__pycache__/`** from root and all packages
5. **Delete `tmp/`** contents if stale

---

## Next Steps

1. **Phase 1.1:** Deep audit each of the 67 packages — what each actually does, what's active vs dead
2. **Phase 1.2:** Audit `lucid_mcp_server.py` (559 KB) — tool count, working vs broken, dead code
3. **Phase 1.3:** Audit the 10.6K markdown files — determine authoritative docs vs drift
4. **Multi-agent brief:** Draft missions for Gemini CLI / Codex agents to parallelize Phase 1
