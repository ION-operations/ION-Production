# PHASE0_MIXED_LANE_RECLAIM_MANIFEST

**Status:** `candidate` · **analysis-only** · **nothing moved** · **DW must not break**

**Audit agent:** Composer (ION North Star subagent)  
**Audit date:** 2026-06-17  
**Active root:** `/home/sev/ION - Production/ION_Developement`  
**Archive destination (reference only):** `/home/sev/ION - Production/ION_ARCHIVE/2026-06-17_exhaust_candidate/phase0_mixed_lanes/`

**Method:** per-lane `du`/`find`; KEEP reasons = `ACTIVE_*` / registry / manifest / projection / monolith constant / recency (`_recent_files` limit 8–20) / paired `*.schema*.json`; ARCHIVE candidates grep-checked against runtime surfaces (`ION/04_packages`, `ION/03_registry`, `ION/02_architecture`, `ION/REPO_AUTHORITY.md`, `ION_LIVING_ENCYCLOPEDIA_MANIFEST_V100.json`, `DOMAIN_WEAVER_PROJECTION.json`, `PROMOTION_*.json`). **Conservative:** when in doubt → KEEP.

**Sampling note:** `live_carrier_binding/snapshots/` (8,037 files) fully enumerated by script; other lanes sampled representative subdirs + top-level listing. Grep verdicts shown for ARCHIVE globs (representative basename where subtree is huge).

---

## Lane 1 — `domain_weaver/live_carrier_binding` (220M → ~8M keep)

**Structure:** 8,201 files; flat top-level JSON/MD + `proof_row_candidates/` (148K) + `proof_row_update_candidates/` (724K) + `snapshots/` (218M, 8,037 files in 2 subdirs). Newest activity: 2026-06-17 kernel-repair monitor/settlement snapshots.

### KEEP table

| Path (relative to `ION_Developement/`) | Reason | Size (approx) |
|---|---|---|
| `ION/05_context/current/domain_weaver/live_carrier_binding/ACTIVE_INVOKABLE_BINDING_*` (16 files: 8 JSON + 8 schema) | **ACTIVE_*** hard rule; kernel `DOMAIN_WEAVER_ACTIVE_INVOKABLE_BINDING_PROOF_ROWS_PATH`; projection `proof_row_path` | ~350K |
| All 103 filenames hard-coded under `DOMAIN_WEAVER_LIVE_CARRIER_BINDING_DIR` in `ion_domain_weaver.py` (L489–700+) | **Monolith-bound** queue ledgers, monitors, settlements, plans | ~1.5M |
| All 92 paths cited in `DOMAIN_WEAVER_PROJECTION.json` under `live_carrier_binding/` (includes 25 snapshot paths) | **Projection-bound** | (subset of above + snapshots) |
| Paired `*.schema.candidate.json` for every kept `*.candidate.json` | **Schema pairing rule** | included |
| Newest **20** files by mtime in lane (2026-06-12→17 kernel-repair snapshot pairs + `.latest.json` monitors) | **Observatory recency** (`ion_agent_observatory.py:679` `_recent_files(..., limit=8)` on lane root) | ~2M |
| `snapshots/EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_{FANIN_SETTLEMENT_RESULT,RETURN_MONITOR}/` **keep files only** = union(projection-cited 25, newest-20 snapshot files) | **Projection volatile_recompute_snapshot_path** + recency guard | ~2M |

**Monolith-bound file inventory (103):** all `*.candidate.json` / `*.latest.json` constants from `DOMAIN_WEAVER_LIVE_CARRIER_BINDING_DIR` in `ion_domain_weaver.py` — includes `LIVE_CARRIER_BINDING_PLAN`, `LIVE_RETURN_MONITOR`, `EXACT_ACTIVE_SPECIALIST_BINDING_*`, `CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_*`, `FISSION_REFLEX_*`, `WAVE2_*` queue ledgers, etc. (full list extractable via `rg 'DOMAIN_WEAVER_LIVE_CARRIER_BINDING_DIR' ION/04_packages/kernel/ion_domain_weaver.py`).

**Projection-cited snapshot paths (25, all KEEP):** under `snapshots/EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANIN_SETTLEMENT_RESULT/` and `..._RETURN_MONITOR/` with timestamps `20260603T032218Z` through `20260604T210853Z` (see `DOMAIN_WEAVER_PROJECTION.json` `snapshot_path` / `volatile_recompute_snapshot_path` fields).

### ARCHIVE table

| Path / glob | Grep verdict | Size (approx) |
|---|---|---|
| `ION/05_context/current/domain_weaver/live_carrier_binding/snapshots/**/*` **except** KEEP snapshot union above | **CLEAR** — no bind in `04_packages`/`03_registry`/`02_architecture`/`REPO_AUTHORITY` for individual snapshot files beyond projection list; sampling: `20260612T153506474893Z_exact_active_kernel_repair_fanin_settlement.json` → no runtime-surface match | **~212M** (7,996 files) |
| `ION/05_context/current/domain_weaver/live_carrier_binding/proof_row_candidates/**` | **CLEAR** — sampled `CONTEXT_VISUALIZATION_CARTOGRAPHER_EXACT_ACTIVE_BINDING_PROOF_ROW_SEED_20260603_ATTEMPT_001.candidate.json` | **~148K** |
| `ION/05_context/current/domain_weaver/live_carrier_binding/proof_row_update_candidates/**` | **CLEAR** — no runtime-surface basename match (sampled) | **~724K** |
| `ION/05_context/current/domain_weaver/live_carrier_binding/EXACT_ACTIVE_BINDING_EVIDENCE_REPAIR_MAP_20260603_ATTEMPT_001.{candidate.json,md}` | **CLEAR** | **~12K** |

**Lane reclaim estimate:** **~212M** (safe batch). **Highest-risk lane** — execute only with post-move DW projection/observatory verification.

---

## Lane 2 — `project_launcher` (172M)

**Structure:** `diagnostic_smoke_apps/` (126M, almost all `vite_react_r3f/node_modules`), `app_diagnostics/` (39M: events 20M, snapshots 19M), `screenshots/` (6.9M), `receipts/` (376K), `logs/` (64K), `state/` (12K).

### KEEP table

| Path | Reason | Size |
|---|---|---|
| `ION/05_context/current/project_launcher/` root structure | `ion_project_launcher.py` `PROJECT_LAUNCHER_DIR` | — |
| `state/**` | Durable launch state (`PROJECT_LAUNCHER_STATE_DIR`) | 12K |
| `receipts/**` (all 86 files) | Read by `ion_app_diagnostics_timeline._receipt_events`, `ion_project_preview_sessions` | 376K |
| `logs/**` | Launch logs dir | 64K |
| `screenshots/**` (all 31) | `project_launcher_screenshot_file()` | 6.9M |
| `app_diagnostics/**` | `ion_app_diagnostics_timeline.DIAGNOSTICS_ROOT` (events + snapshots actively read) | 39M |
| `diagnostic_smoke_apps/{README.md,network_trace,static_lifecycle,webgl_engine,vite_react_r3f/{package.json,package-lock.json,index.html,src}}` | `DIAGNOSTIC_SMOKE_APPS_DIR`; matrix spec `vite_react_r3f` | ~56K source |

### ARCHIVE table

| Path / glob | Grep verdict | Size |
|---|---|---|
| `ION/05_context/current/project_launcher/diagnostic_smoke_apps/vite_react_r3f/node_modules/**` | **CLEAR** on path `vite_react_r3f/node_modules` (no runtime-surface match); parent app dir **BOUND** | **~126M** |

**Operator gate:** `ion_project_launcher` sets `install_repair: True` for `vite_react_r3f` — node_modules is regenerable but matrix diagnostics will fail until `npm install` completes. **Recommend:** execute this slice only after confirming repair path in staging.

**Lane reclaim estimate:** **0M** (default conservative) · **~126M** (operator-gated node_modules slice).

---

## Lane 3 — `codex_carrier` (98M)

**Structure:** top-level registries/policies (~200K) + `commit_boundary/` (97M audit JSON) + small dirs.

### KEEP table

| Path | Reason | Size |
|---|---|---|
| All top-level `CODEX_*` registries, policies, `README.md`, `ROLLING_CONTEXT.template.md` | `ion_codex_carrier_os.py` `CODEX_CARRIER_DIR` primary refs; registry `agent_roster` continuity_home; `domain.codex_carrier_sync` context_roots | ~200K |
| `commit_boundary/**` (all 4 files) | **BOUND** — `ion_codex_commit_boundary_audit.OUTPUT_DIR`; `ion_codex_carrier_os.py` reads `CODEX_COMMIT_BOUNDARY_AUDIT.json` + `CODEX_SOURCE_BUNDLE_STAGE_REVIEW.json` | **97M** |
| `events/`, `sessions/`, `raw_context_manifests/`, `git_rollback/` | Carrier lane continuity surfaces (no exhaust grep) | ~50K |

### ARCHIVE table

| Path | Grep verdict | Size |
|---|---|---|
| `ION/05_context/current/codex_carrier/production_zip_prep_20260610T042913Z/**` | **CLEAR** — no runtime-surface match for `production_zip_prep_20260610` | **~33K** |

**Lane reclaim estimate:** **~0M** (commit_boundary is load-bearing despite size).

---

## Lane 4 — `codex_cli` (64M)

**Structure:** `identity/` (2857 session dirs, 43M), launch-variant probe dirs (Jun 10), `hooks/` (78K), `mount_guard/`, `operational_posture/`, top-level orchestration MD (49 files, 268K).

### KEEP table

| Path | Reason | Size |
|---|---|---|
| `latest_prompt.md`, `latest_return.md` | `codex_cli_carrier_profile.yaml` `recommended_prompt_path` / `recommended_return_path` | small |
| `mount_guard/CURRENT_CODEX_CARRIER_MOUNT.json` + dir | `ion_codex_mount_guard.DEFAULT_CURRENT_STATUS_PATH` | 8K |
| `operational_posture/CURRENT_ION_CODEX_OPERATIONAL_POSTURE.json` + dir | `ion_codex_operational_posture` current status path | 13K |
| `hooks/**` (esp. `hooks/runtime/**`) | `ion_codex_cli_launch_variant_probe.HOOK_RUNTIME_DIR` | 78K |
| `identity/<newest-20-session-dirs>/**` | `ion_codex_chat_identity.IDENTITY_ROOT`; cockpit reads session dirs | **~0.2M** |
| `sessions/` | Carrier session dir (small) | 5K |

### ARCHIVE table

| Path / glob | Grep verdict | Size |
|---|---|---|
| `ION/05_context/current/codex_cli/identity/*/` **except** newest 20 session dirs by mtime | **CLEAR** per-dir basename (root `codex_cli/identity` bound, not individual session UUIDs) | **~33M** (2,837 dirs) |
| `ION/05_context/current/codex_cli/launch_variant_*_20260610T*/**` (6 dirs) | **CLEAR** — probe uses `terminal_workers/codex_cli_launch_variant_forensics`, not these dirs | **~1.4M** |
| `ION/05_context/current/codex_cli/bugcrowd_100_agent_hook_proof/**` | **CLEAR** | **2.6M** |
| `ION/05_context/current/codex_cli/layout_proof/**` | **CLEAR** | **3.3M** |
| `ION/05_context/current/codex_cli/usage_limit_quarantine_20260610T0404Z/**` | **CLEAR** | **563K** |
| `ION/05_context/current/codex_cli/codex_carrier_transfer/**` | **CLEAR** (export lane deduped elsewhere) | **18K** |
| `ION/05_context/current/codex_cli/carrier_identity_timeline/**` | **CLEAR** | **37K** |
| `ION/05_context/current/codex_cli/CODEX_*_ORCHESTRATION_*.md` + `COCKPIT_*_2026060*.md` + similar top-level process MD (49 files) | **CLEAR** — not cited in registry/kernel paths (witness docs) | **268K** |

**Lane reclaim estimate:** **~41M**

---

## Lane 5 — `codex_capsule_chat` (28M)

**Structure:** `state.json` (6M), `response_runs/` (55 dirs, 17M), `raw_cli_runs/` (18 dirs, 3M), `archive_attachments/`, `ide_context_bridges/`, prune backup.

### KEEP table

| Path | Reason | Size |
|---|---|---|
| `state.json` | `ion_dual_codex_chat.STATE_PATH`; MCP `ion_codex_capsule_chat_status` | 6M |
| `archive_attachments/**` | `ion_runtime_service_control`, `ion_codex_conversation_archive`, registry `ion_action_mcp_branch_leader_registry.yaml` | 70K |
| `ide_context_bridges/**` | `ion_dual_codex_chat.IDE_CONTEXT_BRIDGES_DIR` | 71K |
| `raw_cli_runs/**` (all 18 dirs) | `RAW_CODEX_CLI_RUNS_DIR` (18 < recency threshold) | 3M |
| `response_runs/<newest-24-dirs>/**` | `build_codex_chat_response_run_surface(..., limit=24)` | **~14M** |

### ARCHIVE table

| Path / glob | Grep verdict | Size |
|---|---|---|
| `ION/05_context/current/codex_capsule_chat/state.pre_playwright_smoke_prune_20260508T175403Z.json` | **CLEAR** | **767K** |
| `ION/05_context/current/codex_capsule_chat/response_runs/*/` **except** newest 24 dirs by mtime | **CLEAR** per-run dir (parent `response_runs/` bound, not individual run IDs) | **~3.1M** (35 dirs) |

**Lane reclaim estimate:** **~3.9M**

---

## Lane 6 — `domain_weaver/full_steam_push` (26M)

**Structure:** 26 dated `20260608_*` push candidate dirs (Jun 8, 2026); no ongoing writes.

### KEEP table

| Path | Reason |
|---|---|
| *(none — entire lane is process-exhaust)* | — |

### ARCHIVE table

| Path / glob | Grep verdict | Size |
|---|---|---|
| `ION/05_context/current/domain_weaver/full_steam_push/**` | **CLEAR** — zero matches in `04_packages`/`03_registry`/`02_architecture`/`REPO_AUTHORITY`/`DOMAIN_WEAVER_PROJECTION`/`ION_LIVING_ENCYCLOPEDIA_MANIFEST_V100` | **~22M** |

**Lane reclaim estimate:** **~22M** (lowest risk — move entire dir).

---

## Lane 7 — `portable_agent_domain_packages` (15M)

**Structure:** 19 `role_*__domain_*` dirs, each with exactly **one** timestamp stamp + `LATEST.json`.

### KEEP table

| Path | Reason | Size |
|---|---|---|
| `ION/05_context/current/portable_agent_domain_packages/**` (entire lane) | `ion_codex_agent_mount.PORTABLE_PACKAGE_ROOT`; registry `domain.ion_system_definition` cites embedded `role_ionologist__.../20260526T144122Z/.../source_refs/`; each `LATEST.json` is write target of export | **15M** |

### ARCHIVE table

| Path | Grep verdict | Size |
|---|---|---|
| *(none)* | All role packages are current-only (1 stamp each); archiving any package risks mount/export failure | **0** |

**Lane reclaim estimate:** **0M** — **do not touch**.

---

## Do NOT touch (hard load-bearing summary)

| Surface | Paths |
|---|---|
| **ACTIVE_*** | All `live_carrier_binding/ACTIVE_INVOKABLE_BINDING_*` (+ schemas) |
| **Monolith DW constants** | 103 `live_carrier_binding` filenames in `ion_domain_weaver.py` |
| **DOMAIN_WEAVER_PROJECTION.json** | 92 `live_carrier_binding` paths (incl. 25 snapshot paths, all `*.latest.json` monitors) |
| **Kernel observatory** | Newest ~20 files in `live_carrier_binding/`; `ACTIVE_INVOKABLE_BINDING_PROOF_ROWS` |
| **Codex carrier OS** | `codex_carrier/commit_boundary/*.json` (97M), all top-level `CODEX_*` registries |
| **Codex CLI carrier profile** | `codex_cli/latest_prompt.md`, `latest_return.md`, `mount_guard/`, `operational_posture/`, `hooks/runtime/` |
| **Codex capsule chat** | `state.json`, `archive_attachments/`, `raw_cli_runs/`, newest 24 `response_runs/` |
| **Project launcher runtime** | `state/`, `receipts/`, `logs/`, `screenshots/`, `app_diagnostics/`, smoke app **source** (not node_modules) |
| **Portable packages** | Entire `portable_agent_domain_packages/` tree |
| **Registry continuity** | `agent_roster_registry.yaml` → `codex_carrier/`; `codex_cli_carrier_profile.yaml` → `codex_cli/` paths |

---

## Reclaimable totals

| Lane | Conservative reclaim | Notes |
|---|---|---|
| `live_carrier_binding` | **~212M** | Highest risk — snapshot bulk |
| `full_steam_push` | **~22M** | Lowest risk — move whole dir |
| `codex_cli` | **~41M** | Identity session pruning |
| `codex_capsule_chat` | **~4M** | Old response runs + prune backup |
| `project_launcher` | **0M** (default) / **~126M** (gated) | node_modules only |
| `codex_carrier` | **~0M** | commit_boundary load-bearing |
| `portable_agent_domain_packages` | **0M** | Do not touch |
| **Grand total (conservative)** | **~279M (~0.27 GB)** | Excludes gated node_modules |
| **Grand total (incl. gated node_modules)** | **~405M (~0.40 GB)** | Operator-confirmed only |

---

## Execution batch list

Archive root variable for commands (run from `ION_Developement/`):

```bash
ARCH="/home/sev/ION - Production/ION_ARCHIVE/2026-06-17_exhaust_candidate/phase0_mixed_lanes"
mkdir -p "$ARCH"
```

**Execute in order; re-guard with `rg` before each batch; run DW smoke after batches 1 and 2.**

### Batch 1 — `full_steam_push` (low risk)

```bash
mv ION/05_context/current/domain_weaver/full_steam_push \
   "$ARCH/domain_weaver/full_steam_push"
```

### Batch 2 — `live_carrier_binding` snapshot exhaust (highest risk)

```bash
# 2a — stage entire snapshots tree
mv ION/05_context/current/domain_weaver/live_carrier_binding/snapshots \
   "$ARCH/domain_weaver/live_carrier_binding/snapshots_EXHAUST_20260617"

# 2b — recreate snapshot subdirs
mkdir -p ION/05_context/current/domain_weaver/live_carrier_binding/snapshots/EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANIN_SETTLEMENT_RESULT
mkdir -p ION/05_context/current/domain_weaver/live_carrier_binding/snapshots/EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_RETURN_MONITOR

# 2c — restore KEEP snapshots (projection-cited 25 + newest-20 union; use precomputed list)
# North Star: run PRODUCTION_SPINE_AUDIT/scripts/lcb_snapshot_keep_restore.sh (to be generated at execute time from DOMAIN_WEAVER_PROJECTION.json + find -mtime) OR move back manually from staging.

# 2d — small CLEAR top-level + proof_row dirs
mv ION/05_context/current/domain_weaver/live_carrier_binding/proof_row_candidates \
   "$ARCH/domain_weaver/live_carrier_binding/proof_row_candidates"
mv ION/05_context/current/domain_weaver/live_carrier_binding/proof_row_update_candidates \
   "$ARCH/domain_weaver/live_carrier_binding/proof_row_update_candidates"
mv ION/05_context/current/domain_weaver/live_carrier_binding/EXACT_ACTIVE_BINDING_EVIDENCE_REPAIR_MAP_20260603_ATTEMPT_001.candidate.json \
   "$ARCH/domain_weaver/live_carrier_binding/"
mv ION/05_context/current/domain_weaver/live_carrier_binding/EXACT_ACTIVE_BINDING_EVIDENCE_REPAIR_MAP_20260603_ATTEMPT_001.md \
   "$ARCH/domain_weaver/live_carrier_binding/"
```

**Snapshot restore helper (run between 2b and 2d):**

```bash
KEEP_LIST="$ARCH/domain_weaver/live_carrier_binding/SNAPSHOT_KEEP_MANIFEST_20260617.txt"
# Build KEEP_LIST = projection-cited snapshot paths ∪ newest-20 snapshot paths (see audit method §Lane 1)
while IFS= read -r rel; do
  src="$ARCH/domain_weaver/live_carrier_binding/snapshots_EXHAUST_20260617/${rel#*snapshots/}"
  dst="ION/05_context/current/domain_weaver/live_carrier_binding/snapshots/${rel#*snapshots/}"
  [ -f "$src" ] && mkdir -p "$(dirname "$dst")" && mv "$src" "$dst"
done < "$KEEP_LIST"
```

### Batch 3 — `codex_cli` exhaust

```bash
mv ION/05_context/current/codex_cli/launch_variant_agents_isolation_20260610T0338Z "$ARCH/codex_cli/"
mv ION/05_context/current/codex_cli/launch_variant_config_agents_combo_20260610T0339Z "$ARCH/codex_cli/"
mv ION/05_context/current/codex_cli/launch_variant_config_isolation_20260610T0337Z "$ARCH/codex_cli/"
mv ION/05_context/current/codex_cli/launch_variant_empty_target_20260610T0336Z "$ARCH/codex_cli/"
mv ION/05_context/current/codex_cli/launch_variant_full_mount_content_20260610T0340Z "$ARCH/codex_cli/"
mv ION/05_context/current/codex_cli/launch_variant_topfile_isolation_20260610T0341Z "$ARCH/codex_cli/"
mv ION/05_context/current/codex_cli/bugcrowd_100_agent_hook_proof "$ARCH/codex_cli/"
mv ION/05_context/current/codex_cli/layout_proof "$ARCH/codex_cli/"
mv ION/05_context/current/codex_cli/usage_limit_quarantine_20260610T0404Z "$ARCH/codex_cli/"
mv ION/05_context/current/codex_cli/codex_carrier_transfer "$ARCH/codex_cli/"
mv ION/05_context/current/codex_cli/carrier_identity_timeline "$ARCH/codex_cli/"

# Identity: stage all, restore newest 20
mv ION/05_context/current/codex_cli/identity "$ARCH/codex_cli/identity_EXHAUST_20260617"
mkdir -p ION/05_context/current/codex_cli/identity
# restore newest 20 session dirs by mtime from staging → identity/

# Top-level orchestration MD (witness)
mkdir -p "$ARCH/codex_cli/orchestration_md"
mv ION/05_context/current/codex_cli/CODEX_*_ORCHESTRATION_*.md "$ARCH/codex_cli/orchestration_md/" 2>/dev/null || true
mv ION/05_context/current/codex_cli/COCKPIT_*_2026060*.md "$ARCH/codex_cli/orchestration_md/" 2>/dev/null || true
```

### Batch 4 — `codex_capsule_chat` exhaust

```bash
mv ION/05_context/current/codex_capsule_chat/state.pre_playwright_smoke_prune_20260508T175403Z.json \
   "$ARCH/codex_capsule_chat/"
# Move response_runs dirs older than newest 24 (per-dir mv from sorted find output)
```

### Batch 5 — `codex_carrier` minor

```bash
mv ION/05_context/current/codex_carrier/production_zip_prep_20260610T042913Z "$ARCH/codex_carrier/"
```

### Batch 6 — `project_launcher` (OPERATOR-GATED — skip unless install_repair confirmed)

```bash
mv ION/05_context/current/project_launcher/diagnostic_smoke_apps/vite_react_r3f/node_modules \
   "$ARCH/project_launcher/vite_react_r3f_node_modules"
```

### Post-batch verification (required)

```bash
cd ION_Developement
python -m pytest ION/04_packages/kernel/tests/test_resolve_context_scope*.py -q  # if present
# DW observatory / projection refresh readback on live_carrier_binding ACTIVE_* + .latest.json
# Codex carrier OS status still resolves commit_boundary refs
```

---

## Non-claims

- This manifest does **not** ratify archive moves; North Star must re-guard immediately before each batch.
- Snapshot KEEP union size (~41 files) is an **estimate**; exact list must be materialized at execute time from `DOMAIN_WEAVER_PROJECTION.json` + `find -type f -printf '%T@ %p\n' | sort -rn | head -20`.
- `ION_LIVING_ENCYCLOPEDIA_MANIFEST_V100.json` had **no direct path citations** for these seven lanes (grep empty); binds are via kernel + `DOMAIN_WEAVER_PROJECTION.json` + registry instead.
- `project_launcher/diagnostic_smoke_apps/vite_react_r3f/node_modules` reclaim assumes `install_repair` works; not verified in this audit run.
- Sizes are `du`/stat estimates (2026-06-17); margin ±5%.
- Reversible: all operations are `mv` to `ION_ARCHIVE/...` (no deletes).

---

## Risk summary (for North Star)

| Lane | Risk | Recommendation |
|---|---|---|
| `live_carrier_binding` | **HIGH** | Execute batch 2 alone; verify DW projection + observatory before continuing |
| `project_launcher` | **MEDIUM** (node_modules only) | Skip batch 6 unless operator approves repair path |
| `codex_carrier` | **LOW** (near-zero reclaim) | Keep commit_boundary; optional batch 5 only |
| `portable_agent_domain_packages` | **HIGH if touched** | **Do not archive** |
| `full_steam_push` | **LOW** | Safe first batch |
| `codex_cli` / `codex_capsule_chat` | **LOW–MEDIUM** | Batches 3–4 after DW check |
