```yaml
packet_id: PCKT-VNEXT-KERNEL-MONOLITH-RECONCILIATION-AND-RUNTIME-BINDING-20260617
produced_by: Composer carrier (role.mason)
produced_at: 2026-06-17T04:05:58Z
write_posture: candidate_only
nemesis_posture: reconciliation_gated_on_operator_approval_and_nemesis_review_before_any_source_edit
source_inputs:
  - ION/05_context/current/ion_system_definition/PRODUCTION_SPINE_AUDIT/KERNEL_RECONCILIATION/KERNEL_CONTROL_DIFF_MATRIX.candidate.md
  - ION_VNEXT/01_canon/CONTROL_SURFACE_REGISTRY.yaml
  - ION/05_context/current/ion_system_definition/PRODUCTION_SPINE_AUDIT/VNEXT_LANE_HARVEST/LANE08_ION_VNEXT_KERNEL_CORE_GAP_RETURN.candidate.md
shell_root: /home/sev/ION - Production/ION_Developement
```

# Kernel Reconciliation Plan (Candidate) — Gap G1 Dual-`kernel` Tree Seam

## Executive summary

**VERIFIED:** ION has two on-disk Python packages both named `kernel`. Live runtime (`pyproject.toml`, Codex mounts, carrier imports) resolves `kernel.*` to `ION/04_packages/kernel/` (~463 modules). Canon registers 29 controls under `ION_VNEXT/02_kernel/ion_core/src/kernel/`; that tree is dependency-closed (30 modules, 176 control tests green) but **not** wired into live PYTHONPATH. Overlap classification: **3 IDENTICAL / 6 DIVERGED / 20 ONLY_IN_VNEXT / 0 ONLY_IN_MONOLITH** (diff matrix, 2026-06-17).

**INFERENCE:** Reconciliation is a **binding + namespace** problem, not a rewrite. The monolith must remain the authoritative home for live-enforced controls; `ion_core` retains cutover harnesses until M102 cutover-binding packets wire them into runtime.

---

## 1. Namespace-resolution decision

### Recommendation: **Monolith-primary namespace merge** (variant of “monolith absorbs `ion_core` controls”; not “`ion_core` becomes the package”)

| Option | Verdict |
|--------|---------|
| **Monolith absorbs `ion_core` controls** | **SELECTED** — authoritative on-disk home for all live-enforced controls + promoted primitives |
| `ion_core` becomes the package; monolith re-exports | **REJECTED** — ~463 monolith modules, hundreds of live importers, June 2026 operational fixes already on monolith |
| Shared third `kernel` package both consume | **REJECTED as primary** — high migration cost; **ADOPTED as mechanism** via `pkgutil.extend_path` namespace merge |

### Rationale

1. **VERIFIED live binding:** Root `pyproject.toml` sets `where = ["ION/04_packages"]`, `pythonpath = ["ION/04_packages"]`. Codex agent mounts set `PYTHONPATH` to `ION/04_packages`. Monolith modules (`ion_codex_queue_runner`, `ion_chatgpt_browser_mcp_connector_contract`, `ion_carrier_task_return`, `ion_mcp_local_bridge`, etc.) already import overlapping controls from the monolith copy.

2. **VERIFIED scale asymmetry:** Monolith kernel ≈ 361K lines / 463 files vs `ion_core` 30 control modules. Moving authority to `ion_core` would require re-homing the entire runtime graph — disproportionate risk for G1.

3. **VERIFIED complementary supersets:** `ion_core` is a **control superset** (20 modules absent from monolith). Six shared modules **diverged** with monolith carrying June 2026 fixes (Codex agent mount allowance, stricter context-proof evidence, expanded export hygiene). vNext-only `vnext_*` modules (M87–M102) are cutover harnesses, not live movement gates.

4. **Namespace merge solves collision without duplicate true-names:** Both trees use package name `kernel`. A shim alone cannot fix ambiguity when both paths are on PYTHONPATH. **Mechanism:** add `pkgutil.extend_path(__path__, __name__)` to monolith `kernel/__init__.py`; configure unified PYTHONPATH as `ION/04_packages` + `ION_VNEXT/02_kernel/ion_core/src` (monolith first). Shared controls exist **only** in monolith; `vnext_*` harness modules exist **only** in `ion_core`. No duplicate basenames on disk after reconciliation.

5. **State migration implications:**

| Surface | Current | Post-reconciliation (candidate) |
|---------|---------|----------------------------------|
| Root `pyproject.toml` | `pythonpath = ["ION/04_packages"]` | Add second path + documented unified test invocation; optional `pip install -e` both packages |
| `ion_core/pyproject.toml` | `pythonpath = ["src"]` only | `pythonpath = ["../../ION/04_packages", "src"]` for control tests |
| Codex mount `PYTHONPATH` | `.../ION/04_packages` | Extend with `ion_core/src` **only** if a live carrier must invoke `kernel.ion_vnext_*` CLI; default mounts unchanged until cutover packet |
| `CONTROL_SURFACE_REGISTRY.yaml` `source_module` | All cite `02_kernel/ion_core/src/kernel/*` | Dual-path or monolith-primary paths with `runtime_binding` field (Packet G1-D) |
| `ion_core/src/kernel/` duplicates | 13 shared modules copied | **Removed** after promote; only 16 `vnext_*` + `__init__.py` remain |

**INFERENCE:** This is the smallest diff that achieves single-module resolution per true-name while preserving isolated cutover harness development in `ion_core`.

---

## 2. Per-control decision table

Legend — **class:** `IDENTICAL` | `DIVERGED` | `ONLY_IN_VNEXT` (subclass `PROMOTE` = live primitive | `KEEP` = cutover harness). **Authority:** monolith = `ION/04_packages/kernel/` | vNext = `ION_VNEXT/02_kernel/ion_core/src/kernel/`.

| control | class | authoritative source | binding mechanism | rationale | risk | exit test |
|---------|-------|----------------------|-------------------|-----------|------|-----------|
| `ai_movement_gate` | IDENTICAL | monolith | Single file in monolith; delete `ion_core` duplicate; namespace merge | `diff -q` clean; live `ion_codex_queue_runner` imports monolith | LOW | `diff -q` both paths absent (only monolith file); `pytest ION/tests` + `ion_core/tests/control/test_kernel_ion_ai_movement_gate.py` green under unified PYTHONPATH |
| `codex_work_request_target_binding` | IDENTICAL | monolith | Same as above | Identical; bound to Codex dispatch path | LOW | Same pattern; control test file green |
| `template_action_gate` | IDENTICAL | monolith | Same as above | Identical; widespread monolith carrier imports | LOW | Same pattern; control test file green |
| `path_authority` | DIVERGED | monolith | Promote monolith → delete `ion_core` copy; **port** `discover_workspace_manifest()` into monolith as optional API (env + upward marker) while keeping `DEFAULT_WORKSPACE_MANIFEST = resolve_repo_root(...)` as live default | Monolith: `resolve_repo_root` anchor, policy-gated `require_artifacts_outside_active_repo`; vNext: always-reject artifact-in-active-repo, upward discovery only. Live worker shift + path gates use monolith | **HIGH** — manifest resolution + artifact policy fork | (1) `load_workspace_authority(manifest_path=explicit)` identical roots vs manifest YAML. (2) `decide_path_authority(..., purpose="artifact")` inside active repo: blocked when policy true. (3) `discover_workspace_manifest()` from `ION_Developement` returns `ION_WORKSPACE_MANIFEST.yaml`. (4) Monolith `test_kernel_ion_path_authority` if present + `ion_core` control tests green |
| `workspace_root_registry` | DIVERGED | monolith | Promote monolith copy (uses `DEFAULT_WORKSPACE_MANIFEST`); delete `ion_core` duplicate | Coupled to `path_authority` manifest fork; monolith import chain matches live registry consumers | **HIGH** — cascades from path_authority | `build_workspace_root_registry()` without explicit manifest matches monolith-default manifest; classify canonical paths for `ION/`, export root, `Needs_Routed` sibling — `ion_core/tests/control/test_kernel_ion_workspace_root_registry.py` green |
| `agent_cwd_boundary` | DIVERGED | monolith | Promote monolith → delete `ion_core` copy | Monolith adds `CODEX_AGENT_MOUNT_MANIFEST`, `_codex_agent_mount_allowance()`, return fields `codex_agent_mount`, `active_root_subdir_worker_launch_allowed`; `ion_codex_queue_runner` depends on monolith | **HIGH** — Codex mount launches blocked if wrong copy | Fixture envelope with generated mount under active root: `build_agent_cwd_boundary` returns `active_root_subdir_worker_launch_allowed=True` when manifest+AGENTS.md+config valid; invalid mount adds blockers. `ion_core` control tests green |
| `context_proof_gate` | DIVERGED | monolith | Promote monolith → delete `ion_core` copy | Monolith: `has_machine_read_evidence()`, pipe-table regex, multi-position path scan; MCP connector imports public `has_machine_read_evidence` from monolith | **HIGH** — false ACCEPT/REJECT on carrier returns | (1) Pipe-table proof with real excerpt → ACCEPT. (2) Path mention without excerpt → REJECT `missing_read_evidence_near_path`. (3) `has_machine_read_evidence` matches `_has_machine_read_evidence` on golden windows. MCP connector contract tests green |
| `carrier_mount_receipt` | DIVERGED | monolith | Promote monolith → delete `ion_core` copy | Docstring/non_claims wording only (“private internal reasoning text” vs “hidden chain-of-thought”); gate logic identical | LOW | `diff` shows only comment/docstring hunks; `ion_carrier_mount_receipt` control tests green; no finding-code changes |
| `operator_artifact_hygiene_check` | DIVERGED | monolith | Promote monolith → delete `ion_core` copy | Monolith: stricter **exact** path parts (`.cache`, `cache`, `ion_vault_local`, `sessions`, `shell_snapshots`, `vault`); clears fragment list. vNext used substring fragments (weaker for `cache` vs `.cache`) | **MEDIUM** — operator export surface leak | Tree containing `.cache/` or `sessions/` under operator kit → hygiene BLOCKED; clean OPERATOR_FINAL tree → PASS. `ion_codex_carrier_transfer_package` integration path unchanged |
| `receipt_core` | ONLY_IN_VNEXT / PROMOTE | monolith (after copy) | Copy module into monolith; keep `ion_core` re-export or delete after namespace merge exposes monolith module | `dogfood_required_controls` requires before receipt-backed claims; **no** monolith `rg` hits today; vNext-only receipt primitive (`ion.vnext.receipt_core.v1`) | MEDIUM — new surface, no live callers yet | Module importable as `kernel.ion_receipt_core` from `PYTHONPATH=ION/04_packages`; `build_receipt_record` + `classify_receipt_record` control tests green; authority flags remain false |
| `context_package_core` | ONLY_IN_VNEXT / PROMOTE | monolith (after copy) | Copy into monolith | Required before domain context binding per registry; bounded record builders only | MEDIUM | Import + control tests green; no runtime queue coupling |
| `source_pool_audit_core` | ONLY_IN_VNEXT / PROMOTE | monolith (after copy) | Copy into monolith | Required for source-pool promotion review; classification without FS scan | MEDIUM | Import + control tests green |
| `promotion_plan_core` | ONLY_IN_VNEXT / PROMOTE | monolith (after copy) | Copy into monolith | Required before release/operator upload per registry | MEDIUM | Import + control tests green |
| `vnext_boot_dogfood_smoke` | ONLY_IN_VNEXT / KEEP | vNext (`ion_core`) | Primary home `ion_core`; accessible via namespace merge only | M87 harness; proves fresh carrier boot smoke — not a live movement gate | LOW | Stays in `ion_core`; 176-suite subset green; not required on `PYTHONPATH=ION/04_packages` alone until cutover |
| `vnext_readiness_lock` | ONLY_IN_VNEXT / KEEP | vNext | Same | M88 review lock; depends on `ion_receipt_core` — **INFERENCE:** after promote, harness imports receipt from merged namespace | LOW | Control tests green with unified PYTHONPATH |
| `vnext_cutover_gap_closure_plan` | ONLY_IN_VNEXT / KEEP | vNext | Same | M89 blocker map harness | LOW | Control tests green |
| `vnext_release_rollback_dryrun` | ONLY_IN_VNEXT / KEEP | vNext | Same | M90 dry-run evidence harness | LOW | Control tests green |
| `vnext_operator_readiness_review_packet` | ONLY_IN_VNEXT / KEEP | vNext | Same | M91 operator review packet builder | LOW | Control tests green |
| `vnext_production_cutover_packet_draft` | ONLY_IN_VNEXT / KEEP | vNext | Same | M92 non-executable cutover draft | LOW | Control tests green |
| `vnext_optional_live_mcp_supabase_smoke_proof` | ONLY_IN_VNEXT / KEEP | vNext | Same | M93 local MCP listener proof; live Supabase deferred | LOW | Control tests green |
| `vnext_cutover_remaining_gates_review` | ONLY_IN_VNEXT / KEEP | vNext | Same | M94 gates review harness | LOW | Control tests green |
| `vnext_validated_release_bundle_candidate` | ONLY_IN_VNEXT / KEEP | vNext | Same | M95 bundle candidate harness | LOW | Control tests green |
| `vnext_rollback_package_candidate` | ONLY_IN_VNEXT / KEEP | vNext | Same | M96 rollback package harness | LOW | Control tests green |
| `vnext_operator_production_approval_review` | ONLY_IN_VNEXT / KEEP | vNext | Same | M97 approval review template | LOW | Control tests green |
| `vnext_executable_cutover_packet_review` | ONLY_IN_VNEXT / KEEP | vNext | Same | M98 executable packet review | LOW | Control tests green |
| `vnext_production_execution_authority_review` | ONLY_IN_VNEXT / KEEP | vNext | Same | M99 authority review | LOW | Control tests green |
| `vnext_cutover_execution_rehearsal_dryrun` | ONLY_IN_VNEXT / KEEP | vNext | Same | M100 rehearsal dry-run | LOW | Control tests green |
| `vnext_production_authority_transition_precheck` | ONLY_IN_VNEXT / KEEP | vNext | Same | M101 precheck harness | LOW | Control tests green |
| `vnext_production_authority_decision_packet_draft` | ONLY_IN_VNEXT / KEEP | vNext | Same | M102 decision draft; authority not set by design | LOW | Control tests green |

### Per-class counts (verified classification + plan subclass)

| bucket | count | plan action |
|--------|-------|-------------|
| IDENTICAL | **3** | Unify to monolith single file; remove `ion_core` duplicates |
| DIVERGED | **6** | Promote monolith; preserve vNext-only APIs where tests/doctrine require (`discover_workspace_manifest`) |
| ONLY_IN_VNEXT — **PROMOTE** | **4** | Copy primitives into monolith |
| ONLY_IN_VNEXT — **KEEP** | **16** | Retain in `ion_core`; namespace merge for import |
| ONLY_IN_MONOLITH | **0** | — |

---

## 3. Diverged controls — behavioral diff summary

### `path_authority` (VERIFIED)

| aspect | vNext (`ion_core`) | monolith (authoritative) |
|--------|-------------------|--------------------------|
| Default manifest | `Path("ION_WORKSPACE_MANIFEST.yaml")` cwd-relative | `resolve_repo_root(__file__) / "ION_WORKSPACE_MANIFEST.yaml"` |
| Discovery | `discover_workspace_manifest()` — env `ION_WORKSPACE_MANIFEST` + upward walk | **Removed**; explicit `manifest_path` or default only |
| Artifact in active repo | Always `REASON_ARTIFACT_INSIDE_ACTIVE_REPO` | Blocked only if `path_policy.require_artifacts_outside_active_repo` (default **true**) |
| Preserve from non-chosen | Port `discover_workspace_manifest` into monolith as optional API | — |

### `workspace_root_registry` (VERIFIED)

| aspect | vNext | monolith |
|--------|-------|----------|
| Default manifest resolution | `discover_workspace_manifest()` when `manifest_path` omitted | `DEFAULT_WORKSPACE_MANIFEST` from monolith `path_authority` |
| Public API | Same symbols | Same symbols |
| Coupling | Follows vNext discovery | Follows monolith repo-root default |

### `agent_cwd_boundary` (VERIFIED)

| aspect | vNext | monolith |
|--------|-------|----------|
| Codex mount | No mount allowance logic | `_codex_agent_mount_allowance()` validates generated mount (manifest JSON, `AGENTS.md`, `.codex/config.toml`) |
| Return envelope | No `codex_agent_mount` / `active_root_subdir_worker_launch_allowed` | Adds both fields |
| LOC | 247 | 311 |

### `context_proof_gate` (VERIFIED)

| aspect | vNext | monolith |
|--------|-------|----------|
| Read evidence | Single `path.find`; token substring check | All match positions; `has_machine_read_evidence()` public API |
| Pipe tables | Not validated structurally | `_has_pipe_table_read_evidence` with cell/excerpt rules |
| Live importers | — | `ion_chatgpt_browser_mcp_connector_contract` imports `has_machine_read_evidence` |

### `operator_artifact_hygiene_check` (VERIFIED)

| aspect | vNext | monolith |
|--------|-------|----------|
| Forbidden paths | 3 exact parts + 4 substring fragments | 9 exact parts + empty fragments |
| Effect | `cache` fragment blocks broader; misses exact `.cache`, `sessions`, etc. | Exact-part blocking for cache/session/vault paths |

### `carrier_mount_receipt` (VERIFIED)

| aspect | vNext | monolith |
|--------|-------|----------|
| Behavior | Identical gate logic | Identical gate logic |
| Diff | Docstring “hidden chain-of-thought” | Docstring “private internal reasoning text” |

---

## 4. Exit-test harness design

### 4.1 Unified pytest (VERIFIED target state)

**Documented invocation (candidate — not executed in this packet):**

```bash
cd "/home/sev/ION - Production/ION_Developement"
export PYTHONPATH="ION/04_packages:ION_VNEXT/02_kernel/ion_core/src"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python3 -m pytest -p no:cacheprovider ION/tests tests/control \
  --pyargs kernel 2>/dev/null; \
python3 -m pytest -p no:cacheprovider ION/tests -q; \
cd ION_VNEXT/02_kernel/ion_core && python3 -m pytest -p no:cacheprovider tests/control -q
```

**INFERENCE:** Root `pyproject.toml` should add a marker job `pytest -m kernel_reconciliation` or script `ION/scripts/run_kernel_reconciliation_tests.sh` documenting the above.

| harness | pass criterion |
|---------|----------------|
| Monolith suite | `ION/tests` green (existing kernel tests) |
| Control suite | `ion_core/tests/control` — **176 passed** (baseline VERIFIED 2026-06-17) |
| Combined | Both exit 0 from one documented path without manual `cd` |

### 4.2 Import-resolution test (new — candidate)

Add `ION_VNEXT/02_kernel/ion_core/tests/control/test_kernel_import_resolution.py` (or `ION/tests/test_kernel_control_surface_resolution.py`):

For each of 29 controls in `CONTROL_SURFACE_REGISTRY.yaml`:

1. `importlib.import_module("kernel." + module_basename)` succeeds under unified PYTHONPATH.
2. `module.__file__` resolves to **exactly one** absolute path.
3. Shared controls (13) → path under `ION/04_packages/kernel/`.
4. `vnext_*` controls (16) → path under `ion_core/src/kernel/`.
5. Promoted primitives (4) → path under `ION/04_packages/kernel/` post Packet G1-C.

### 4.3 Per-diverged behavior-equivalence tests (new — candidate)

| control | golden fixtures |
|---------|-----------------|
| `path_authority` | Manifest load roots; artifact inside active repo; `discover_workspace_manifest` optional |
| `workspace_root_registry` | Root classification matrix |
| `agent_cwd_boundary` | Valid/invalid Codex agent mount fixtures |
| `context_proof_gate` | ACCEPT pipe-table; REJECT bare path mention; public API parity |
| `operator_artifact_hygiene_check` | Kit with `.cache/`, `sessions/` → BLOCK |
| `carrier_mount_receipt` | Docstring-only — snapshot gate output hash unchanged |

### 4.4 Registry-alignment check (new — candidate)

Script `ION/scripts/check_control_surface_registry_alignment.py`:

1. Parse `CONTROL_SURFACE_REGISTRY.yaml` `controls.*.source_module`.
2. Map true-name → expected on-disk path per reconciliation table.
3. Fail if file missing, duplicate basename in both trees, or `source_module` disagrees with `runtime_binding` policy post cutover.
4. Emit candidate receipt JSON to `ION/05_context/current/signals/`.

### 4.5 Namespace-merge smoke (new — candidate)

```bash
PYTHONPATH="ION/04_packages:ION_VNEXT/02_kernel/ion_core/src" python3 -c "
import kernel.ion_path_authority as pa
import kernel.ion_vnext_readiness_lock as rl
assert '04_packages' in pa.__file__
assert 'ion_core' in rl.__file__
"
```

---

## 5. Sequenced gated bounded packets

Each packet: **candidate edit → nemesis diff review → operator gate → execute**. No skip.

| seq | packet id | scope | dependencies | gate evidence |
|-----|-----------|-------|--------------|---------------|
| **G1-0** | `PCKT-G1-RECONCILIATION-PLAN-20260617` | This plan + diff matrix | Lane 8 harvest | Operator read + nemesis audit (**this artifact**) |
| **G1-A** | `PCKT-G1-IDENTICAL-UNIFY-NAMESPACE-MERGE-SCAFFOLD-20260617` | (1) Add `pkgutil.extend_path` to monolith `kernel/__init__.py`. (2) Remove 3 duplicate modules from `ion_core` (identical only). (3) Update `ion_core/pyproject.toml` pythonpath. (4) Add import-resolution + namespace smoke tests (read-only stubs OK). (5) Document unified pytest script. **No diverged edits.** | G1-0 approved | 3 identical `diff -q` absent from `ion_core`; namespace smoke passes; 176 control tests green |
| **G1-B** | `PCKT-G1-DIVERGED-PROMOTE-MONOLITH-20260617` | Promote 6 diverged monolith modules; delete `ion_core` copies; port `discover_workspace_manifest` into monolith; add behavior-equivalence tests | G1-A green | 6 diverged exit tests green; MCP/carrier importers unchanged; monolith + control pytest green |
| **G1-C** | `PCKT-G1-PRIMITIVES-PROMOTE-20260617` | Copy 4 primitives into monolith; wire **candidate** imports in steward/receipt surfaces (no production claim) | G1-B green | 4 modules in monolith; import-resolution test; control tests green |
| **G1-D** | `PCKT-G1-REGISTRY-RUNTIME-BINDING-20260617` | Update `CONTROL_SURFACE_REGISTRY.yaml` with `runtime_source_module` (monolith paths) + retain `canon_source_module`; root `pyproject.toml` test job; rebase `ion_core` README/capsules | G1-C green | Registry-alignment script exit 0; unified pytest from one script; context-proof gate on updated docs |
| **G1-E** | `PCKT-G1-CUTOVER-HARNESS-BINDING-20260617` (optional, post-M102) | Thin live invocation path for `vnext_*` from carriers if operator requests | G1-D + M102 decision | Explicit operator authority; not part of Wave A minimum |

**FIRST bounded packet to execute after this plan:** **G1-A** (`PCKT-G1-IDENTICAL-UNIFY-NAMESPACE-MERGE-SCAFFOLD-20260617`).

---

## 6. Risks and mitigations

| risk | severity | mitigation |
|------|----------|------------|
| `path_authority` manifest fork breaks carrier mounts | CRITICAL | Monolith default unchanged; `discover_workspace_manifest` ported as optional; explicit manifest in envelopes |
| `context_proof_gate` regression on MCP returns | CRITICAL | Golden ACCEPT/REJECT fixtures; run `ion_chatgpt_browser_mcp_connector_contract` tests in G1-B gate |
| `agent_cwd_boundary` blocks valid Codex launches | HIGH | Mount allowance fixtures from live `codex_agent_mounts`; queue runner integration test |
| Namespace merge import shadowing | HIGH | Monolith first on PYTHONPATH; delete duplicates; import-resolution test |
| `ion_core` tests hardcode `/home/sev/ION - Production` | MEDIUM | Portability packet (G5); not G1 blocker |
| Registry still cites vNext paths after partial reconcile | MEDIUM | G1-D registry script is exit gate |
| Promoting primitives without callers | LOW | Copy only; wire imports in bounded steward packet |

---

## 7. Explicit non-claims

- **No** production authority, live execution authority, or accepted-state claim.
- **No** M102 gate closure or `production_execution_authority` assignment.
- **No** ratification of `CONTROL_SURFACE_REGISTRY.yaml` — alignment check is candidate only.
- **No** claim that unified pytest has been run in this packet — baseline 176/176 is **VERIFIED** from lane 8 harvest on vNext-only PYTHONPATH, not post-reconciliation state.
- **No** `pip install`, venv, worker start, git push, or service restart.
- Synthesis is not settlement. Nemesis audit required before any source edit.

---

## 8. Evidence ledger

| claim | status |
|-------|--------|
| 29 controls; 3/6/20/0 split | **VERIFIED** — diff matrix |
| Live runtime binds monolith | **VERIFIED** — pyproject, Codex mounts, importer grep |
| 176 control tests pass (pre-reconcile) | **VERIFIED** — lane 8 harvest |
| Monolith absorbs + namespace merge is lowest-risk | **INFERENCE** — scale + live binding |
| 4 promote + 16 keep for ONLY_IN_VNEXT | **VERIFIED** per-module review (primitives lack FS coupling; `vnext_*` are M87–M102 harnesses) |
| `discover_workspace_manifest` should be ported to monolith | **INFERENCE** — registry `manifest_topology_blocker_status: resolved_by_marker_discovery` + control test imports |
