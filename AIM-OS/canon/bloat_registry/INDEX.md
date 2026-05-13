# Bloat Registry

> **Purpose:** Document identified bloat with justification for why it's classified as such.
> **Rule:** Nothing is deleted. This registry explains what SHOULD be cleaned up eventually.

---

## Duplicate Directories

| Directory A | Directory B | Size | Verdict |
|------------|------------|------|---------|
| `audit/` (580K, 61 files) | `audits/` (788K, 42 files) | 1.4MB total | Both consolidated into `canon/audits/`. Originals redundant. |
| `schema/` (8K, 1 file) | `schemas/` (8K, 1 file) | 16K total | Two dirs for one file each. Consolidate. |
| `test_data_priority1/` | `test_data_priority1_format/` | 84K total | Three dirs with identical structure. Keep one. |
| `test_data_priority1/` | `test_data_priority1_linkage/` | (see above) | (see above) |
| `Documentation/` (544MB) | `Documentation_Consolidated/` (813MB) | 1.4GB total | MASSIVE duplication. 7,209 files between them. Documentation_Consolidated is the organized version. |

## Dead/Empty Directories

| Directory | Size | Files | Why Dead |
|-----------|------|-------|---------|
| `echo-forge-loop/` | 4K | 0 | Empty directory |
| `tmp/` | 8K | 0 | Empty temp directory |
| `__pycache__/` | 448K | 1 | Python cache — should be gitignored |
| `diagnostics/` | 52K | 1 | Single diagnostic file |
| `forcing_test_flip/` | 16K | 3 | Test flip files — likely stale |
| `evidence/` | 12K | 1 | Single evidence file — underutilized |

## Superseded Files

| File | Size | Superseded By |
|------|------|--------------|
| `lucid_mcp_server.py.bak` | 567KB | `lucid_mcp_server.py` (current version) |
| `README_CONTENT_PLAN.md` | 22KB | Actual README.md |
| `README_REORGANIZATION_PLAN.md` | 9KB | This canon reorganization |
| `dummy` | 130B | Nothing — test file |
| `mcp_err.log` / `mcp_out.log` | 56KB | Runtime logs — should be gitignored |
| `mesh_visualization.html` | 30KB | 3D visualization — not AIM-OS related |

## Oversized Directories

| Directory | Size | Files | Issue |
|-----------|------|-------|-------|
| `Documentation/` | 544MB | 5,607 | Includes .docx files, appexamples, _agent_sandbox. Too large for canon — reference only. |
| `Documentation_Consolidated/` | 813MB | 1,602 | 13 numbered categories. Organized but massive. Reference only. |
| `knowledge_architecture/` | 189MB | 37,352 | Largest content dir. Historical gold mine but mostly session indexes and atlas data. Summary only for canon. |
| `ide_orchestration/` | 22MB | 1,458 | IDE chains and panel inventories. Historical. |

## Total Bloat Estimate

| Category | Size | Files |
|----------|------|-------|
| Duplicates | ~1.4GB | ~7,250 |
| Dead/empty | ~500K | ~5 |
| Superseded files | ~600K | ~6 |
| Oversized (reference only) | ~1.6GB | ~46,000 |
| **Total** | **~3GB** | **~53,000** |

> **53,000 files / 3GB are bloat** — that's ~83% of AIM-OS-GIT's 63,786 files.
> The actual valuable, active content is roughly **11,000 files / 100MB**.
