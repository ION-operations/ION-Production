# Repository Cleanup & Documentation Audit

**Agent:** Opus
**Date:** 2026-03-09T13:30:00-04:00
**Phase/Task:** Phase 28b — Repo Cleanup
**Confidence:** 0.90

## Reasoning

The root directory has 36 files and 75 subdirectories. Many are temp files, generated artifacts, or data files that shouldn't be in the repository. Additionally, `gmail.txt` was deleted from disk but is still tracked in git and lives in git history.

## Root File Classification

### ✅ KEEP — Production essentials
| File | Purpose |
|------|---------|
| `README.md` | Project README |
| `AIM_OS_NORTH_STAR.md` | Vision document |
| `AGENTS.md` | Agent roster |
| `DO_NOT_TOUCH_MCP.md` | MCP protection law |
| `SOURCE_OF_TRUTH.yaml` | System truth registry |
| `pyproject.toml` | Python project config |
| `requirements.txt` | Python dependencies |
| `Makefile` | Build commands |
| `.gitignore` | Git exclusions |
| `.gitattributes` | Git attributes |
| `.editorconfig` | Editor config |
| `.env.template` | Env template (no secrets) |
| `.sdfcvf.config.yaml` | SDF-CVF config |
| `.cursorrules` | Cursor IDE rules |
| `pyrightconfig.json` | Type checker config |
| `lucid_mcp_server.py` | Main MCP server (548KB) |
| `run_mcp_32_tools.py` | MCP launcher |
| `run_mcp_cross_model.py` | Cross-model MCP runner |
| `LAUNCH_AETHER.bat` | Aether launcher |

### 🟡 MOVE — to proper locations
| File | Move to | Reason |
|------|---------|--------|
| `10_MODES_SUMMARY.md` | `Documentation/` | Not a root doc |
| `MAPPING_COMPLETE_SUMMARY.md` | `Documentation/` | Historical summary |
| `README_CONTENT_PLAN.md` | `Documentation/plans/` | Idea/plan doc |
| `README_REORGANIZATION_PLAN.md` | `Documentation/plans/` | Idea/plan doc |
| `SHARED_MESSAGE_BOARD_ANTIGRAVITY.md` | `.agent/comms/` | Agent comms |
| `mesh_visualization.html` | `packages/joc/` or `tmp/` | Generated viz |

### 🔴 DELETE/UNTRACK — temp, generated, sensitive
| File | Action | Reason |
|------|--------|--------|
| `gmail.txt` | `git rm --cached` + add to `.gitignore` | **SENSITIVE** — emails in git history |
| `.coverage` | Untrack | Generated test coverage |
| `coverage.xml` | Untrack | Generated (already in .gitignore) |
| `dummy` | Delete | Test stub |
| `tmp_mesh_out.txt` | Delete | Temp output |
| `context_capsule.zip` | Untrack | Large binary (already .gitignored pattern) |
| `context_capsule_wire_and_mapper_v1.zip` | Untrack | Large binary |
| `mcp_ai_messages.json` | Untrack | Runtime data (already in .gitignore) |
| `mcp_timeline_entries.json` | Untrack | Runtime data (already in .gitignore) |
| `.env` | Untrack | **SENSITIVE** — should never be tracked |

## Root Directory Classification

### ✅ KEEP — Core project dirs
`packages/`, `scripts/`, `.agent/`, `src/`, `config/`, `schema/`, `schemas/`, `tests/`, `Testing/`, `bootloaders/`, `deployment/`

### ✅ KEEP — Product dirs
`IDE/`, `cursor-addon/`, `UIeditor/`, `ide_orchestration/`, `mcp-aether/`

### ✅ KEEP — Knowledge
`Documentation/`, `knowledge_architecture/`, `PROJECT_TRUTH/`, `docs/`

### 🟡 REVIEW — may consolidate
| Directory | Question |
|-----------|----------|
| `Documentation_Consolidated/` | Overlap with Documentation/? |
| `codex/`, `codex-systems/`, `codex_workspace/` | 3 codex dirs — consolidate? |
| `audit/`, `audits/` | Two audit dirs — merge? |
| `plans/`, `goals/`, `ideas/` | Consolidate planning dirs? |
| `data/`, `evidence/`, `examples/` | Review relevance |
| `context/`, `context_capsule_wire_and_mapper_v1/` | Context system historical? |
| `orchestration_templates/` | Still used? |
| `organized_root_files/` | Ironic name — review |
| `active_work/`, `coordination/` | Current or stale? |
| `daemon_rag_system/` | Used or replaced by packages/deepsearch? |

### 🔴 DELETE — clearly noise
| Directory | Reason |
|-----------|--------|
| `forensics_backups/` | Old backups |
| `htmlcov/` | Generated coverage (in .gitignore) |
| `tmp/` | Temp files |
| `forcing_test_flip/` | Old test artifact |
| `test_data_priority1/` | Old test data |
| `test_data_priority1_format/` | Old test data |
| `test_data_priority1_linkage/` | Old test data |
| `test_mcp_configs/` | Old test configs |
| `test_mcp_memory/` | Old test data |
| `achievements/` | Historical |
| `archive/` | Already archived |
| `artifacts/` | Moved to proper locations |
| `benchmarks/` | Review but likely outdated |
| `diagnostics/` | Generated |
| `images/` | Random images |
| `legacy_docs/` | Already in .gitignore |
| `north_star_project/` | Duplicate of AIM_OS_NORTH_STAR.md? |
| `projects/` | Review |
| `reports/` | Generated |
| `runs/` | Generated |
| `snapshots/` (root) | Old snapshots |
| `state/` | Runtime state |
| `timeline_goals/` | Moved to MCP |

## Git Actions Needed

```bash
# 1. Remove sensitive file from git tracking
git rm --cached gmail.txt 2>/dev/null

# 2. Untrack generated/runtime files
git rm --cached .coverage coverage.xml dummy tmp_mesh_out.txt 2>/dev/null
git rm --cached mcp_ai_messages.json mcp_timeline_entries.json 2>/dev/null
git rm --cached context_capsule.zip context_capsule_wire_and_mapper_v1.zip 2>/dev/null
git rm --cached .env 2>/dev/null
git rm --cached desktop.ini 2>/dev/null

# 3. Add to .gitignore
# gmail.txt
# .env
# dummy
# tmp_*.txt
# *.zip (already there)
# desktop.ini

# 4. CRITICAL: gmail.txt is in git HISTORY
# To fully remove from history: git filter-branch or BFG Repo Cleaner
# This requires a force push and should be done carefully
```

## Open Questions

1. Should we run BFG Repo Cleaner to purge `gmail.txt` from git history entirely?
2. Which "REVIEW" directories can be deleted vs consolidated?
3. How should we reorganize Documentation vs Documentation_Consolidated?
