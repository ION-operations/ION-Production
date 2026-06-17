```yaml
packet_id: PCKT-VNEXT-KERNEL-MONOLITH-RECONCILIATION-AND-RUNTIME-BINDING-20260617
produced_by: Composer carrier (role.mason)
produced_at: 2026-06-17T03:58:52Z
write_posture: candidate_only
nemesis_posture: reconciliation_gated_on_operator_approval_and_nemesis_review_before_any_source_edit
shell_root: /home/sev/ION - Production/ION_Developement
registry_source: ION_VNEXT/01_canon/CONTROL_SURFACE_REGISTRY.yaml
vnext_tree: ION_VNEXT/02_kernel/ion_core/src/kernel
monolith_tree: ION/04_packages/kernel
controls_compared: 29
```

# Kernel Control Diff Matrix (Candidate)

## Scope and method

**VERIFIED:** `CONTROL_SURFACE_REGISTRY.yaml` registers **29 Python kernel controls** (`controls:` entries with `source_module` under `02_kernel/ion_core/src/kernel/`). Two additional registry entries (`approval_scope_correction`, `operational_mandate_and_joint_accountability`) point to markdown work packets, not kernel modules — excluded from this matrix.

**VERIFIED:** Comparison method per control: locate same basename in both trees; `diff -q` for identity; line counts via `wc -l`; substantive diff review for `DIVERGED` rows; public API scan via AST for top-level `def`/`class` names.

**VERIFIED:** Monolith kernel scale: **463** `.py` files, **361,242** total lines in `ION/04_packages/kernel/*.py` (top-level sum). vNext control package: **30** modules (29 controls + `__init__.py`).

**INFERENCE:** Monolith continued evolving through June 2026 on shared control names while vNext control modules largely stabilized around May 2026 — drift is expected on overlapping surfaces, not accidental duplication alone.

---

## Per-control matrix

| control | vnext module path | monolith module path | status | key diffs | vnext LOC | monolith LOC |
|---------|-------------------|----------------------|--------|-----------|-----------|--------------|
| path_authority | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_path_authority.py` | `ION/04_packages/kernel/ion_path_authority.py` | **DIVERGED** | Monolith: imports `resolve_repo_root` from `ion_workspace_paths`; `DEFAULT_WORKSPACE_MANIFEST` anchored to repo root; **removed** `discover_workspace_manifest()` upward marker search; artifact purpose gate reads `require_artifacts_outside_active_repo` policy (optional allow inside active repo). vNext retains env/upward discovery. Public API: vNext-only `discover_workspace_manifest`. | 307 | 287 |
| workspace_root_registry | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_workspace_root_registry.py` | `ION/04_packages/kernel/ion_workspace_root_registry.py` | **DIVERGED** | Import swap: vNext uses `discover_workspace_manifest`; monolith uses `DEFAULT_WORKSPACE_MANIFEST`. `build_workspace_root_registry` default manifest resolution aligned with path_authority fork. No new public symbols. | 466 | 466 |
| ai_movement_gate | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_ai_movement_gate.py` | `ION/04_packages/kernel/ion_ai_movement_gate.py` | **IDENTICAL** | `diff -q` clean. | 377 | 377 |
| codex_work_request_target_binding | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_codex_work_request_target_binding.py` | `ION/04_packages/kernel/ion_codex_work_request_target_binding.py` | **IDENTICAL** | `diff -q` clean. | 418 | 418 |
| agent_cwd_boundary | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_agent_cwd_boundary.py` | `ION/04_packages/kernel/ion_agent_cwd_boundary.py` | **DIVERGED** | Monolith adds `CODEX_AGENT_MOUNT_MANIFEST`, `_codex_agent_mount_allowance()` (validates generated Codex agent mount under active root: manifest, `AGENTS.md`, `.codex/config.toml`), extends `build_agent_cwd_boundary` return with `codex_agent_mount` and `active_root_subdir_worker_launch_allowed`. | 247 | 311 |
| context_proof_gate | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_context_proof_gate.py` | `ION/04_packages/kernel/ion_context_proof_gate.py` | **DIVERGED** | Monolith adds `_HEX64_RE`, `_LINE_MARKER_RE`, `_has_pipe_table_read_evidence`, `_has_machine_read_evidence`, public `has_machine_read_evidence()`; read-evidence check uses all path match positions and stricter pipe-table excerpt rules. | 138 | 180 |
| template_action_gate | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_template_action_gate.py` | `ION/04_packages/kernel/ion_template_action_gate.py` | **IDENTICAL** | `diff -q` clean. | 134 | 134 |
| carrier_mount_receipt | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_carrier_mount_receipt.py` | `ION/04_packages/kernel/ion_carrier_mount_receipt.py` | **DIVERGED** | Docstring/non_claims wording only (“hidden chain-of-thought” → “private internal reasoning text”). No behavioral diff observed in gate logic. | 518 | 518 |
| operator_artifact_hygiene_check | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_operator_artifact_hygiene_check.py` | `ION/04_packages/kernel/ion_operator_artifact_hygiene_check.py` | **DIVERGED** | Monolith expands `FORBIDDEN_EXACT_PARTS` (`.cache`, `cache`, `ion_vault_local`, `sessions`, `shell_snapshots`, `vault`) and clears `FORBIDDEN_PART_FRAGMENTS` (those moved to exact parts). Stricter operator-surface hygiene. | 334 | 336 |
| receipt_core | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_receipt_core.py` | — | **ONLY_IN_VNEXT** | No `ion_receipt_core` in monolith (`rg` zero hits). vNext-only receipt primitive builders/validators (`SCHEMA_ID ion.vnext.receipt_core.v1`). | 250 | 0 |
| context_package_core | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_context_package_core.py` | — | **ONLY_IN_VNEXT** | No monolith module. vNext-only bounded context-package record builders. | 241 | 0 |
| source_pool_audit_core | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_source_pool_audit_core.py` | — | **ONLY_IN_VNEXT** | No monolith module. vNext-only source-pool classification without filesystem scan. | 399 | 0 |
| promotion_plan_core | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_promotion_plan_core.py` | — | **ONLY_IN_VNEXT** | No monolith module. vNext-only typed promotion-plan builders. | 505 | 0 |
| vnext_boot_dogfood_smoke | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_boot_dogfood_smoke.py` | — | **ONLY_IN_VNEXT** | M87 harness; no monolith copy. | 329 | 0 |
| vnext_readiness_lock | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_readiness_lock.py` | — | **ONLY_IN_VNEXT** | M88 harness; no monolith copy. | 426 | 0 |
| vnext_cutover_gap_closure_plan | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_cutover_gap_closure_plan.py` | — | **ONLY_IN_VNEXT** | M89 harness; no monolith copy. | 395 | 0 |
| vnext_release_rollback_dryrun | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_release_rollback_dryrun.py` | — | **ONLY_IN_VNEXT** | M90 harness; no monolith copy. | 453 | 0 |
| vnext_operator_readiness_review_packet | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_operator_readiness_review_packet.py` | — | **ONLY_IN_VNEXT** | M91 harness; no monolith copy. | 427 | 0 |
| vnext_production_cutover_packet_draft | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_production_cutover_packet_draft.py` | — | **ONLY_IN_VNEXT** | M92 harness; no monolith copy. | 541 | 0 |
| vnext_optional_live_mcp_supabase_smoke_proof | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_optional_live_mcp_supabase_smoke_proof.py` | — | **ONLY_IN_VNEXT** | M93 harness; no monolith copy. | 547 | 0 |
| vnext_cutover_remaining_gates_review | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_cutover_remaining_gates_review.py` | — | **ONLY_IN_VNEXT** | M94 harness; no monolith copy. | 437 | 0 |
| vnext_validated_release_bundle_candidate | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_validated_release_bundle_candidate.py` | — | **ONLY_IN_VNEXT** | M95 harness; no monolith copy. | 453 | 0 |
| vnext_rollback_package_candidate | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_rollback_package_candidate.py` | — | **ONLY_IN_VNEXT** | M96 harness; no monolith copy. | 544 | 0 |
| vnext_operator_production_approval_review | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_operator_production_approval_review.py` | — | **ONLY_IN_VNEXT** | M97 harness; no monolith copy. | 494 | 0 |
| vnext_executable_cutover_packet_review | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_executable_cutover_packet_review.py` | — | **ONLY_IN_VNEXT** | M98 harness; no monolith copy. | 755 | 0 |
| vnext_production_execution_authority_review | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_production_execution_authority_review.py` | — | **ONLY_IN_VNEXT** | M99 harness; no monolith copy. | 610 | 0 |
| vnext_cutover_execution_rehearsal_dryrun | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_cutover_execution_rehearsal_dryrun.py` | — | **ONLY_IN_VNEXT** | M100 harness; no monolith copy. | 843 | 0 |
| vnext_production_authority_transition_precheck | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_production_authority_transition_precheck.py` | — | **ONLY_IN_VNEXT** | M101 harness; no monolith copy. | 628 | 0 |
| vnext_production_authority_decision_packet_draft | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_production_authority_decision_packet_draft.py` | — | **ONLY_IN_VNEXT** | M102 harness; no monolith copy. | 712 | 0 |

---

## Counts summary

| status | count |
|--------|-------|
| IDENTICAL | **3** |
| DIVERGED | **6** |
| ONLY_IN_VNEXT | **20** |
| ONLY_IN_MONOLITH | **0** |
| NOT_FOUND | **0** |

**Total controls compared:** 29

---

## Runtime binding (which tree is live)

### VERIFIED — install / test configuration

Root `pyproject.toml` (shell root):

```toml
[tool.setuptools.packages.find]
where = ["ION/04_packages"]
include = ["kernel*"]

[tool.pytest.ini_options]
pythonpath = ["ION/04_packages"]
```

`ion_core` is a **separate** package (`ion-kernel-vnext-control`) with `where = ["src"]` and `pythonpath = ["src"]` only in `ION_VNEXT/02_kernel/ion_core/pyproject.toml` — not referenced by root install.

### VERIFIED — `import kernel` resolution

```text
PYTHONPATH=ION/04_packages → kernel.__file__ = .../ION/04_packages/kernel/__init__.py
PYTHONPATH=ION_VNEXT/02_kernel/ion_core/src → kernel.__file__ = .../ion_core/src/kernel/__init__.py
```

### VERIFIED — carrier PYTHONPATH convention

Representative Codex agent mount config (`role_ionologist__domain_ion_system_definition/.codex/config.toml`):

```toml
env = { PYTHONPATH = ".../ION_Developement/ION/04_packages", ... }
```

Same pattern observed across multiple `ION/05_context/current/codex_agent_mounts/*/config.toml` mounts.

### VERIFIED — live monolith imports of registered controls (relative `from .ion_*`)

| control module | monolith importers (sample) |
|----------------|----------------------------|
| `ion_path_authority` | `ion_worker_shift_presence.py` (`from kernel.ion_path_authority import ...`) |
| `ion_agent_cwd_boundary` | `ion_codex_queue_runner.py` |
| `ion_ai_movement_gate` | `ion_codex_queue_runner.py` |
| `ion_context_proof_gate` | `ion_chatgpt_browser_mcp_connector_contract.py` (imports `has_machine_read_evidence`), `ion_carrier_task_return.py`, `ion_domain_weaver_round_table_return_lint.py`, `ion_cycle_runner.py` (string refs) |
| `ion_template_action_gate` | `ion_chatgpt_browser_mcp_connector_contract.py`, `ion_carrier_task_return.py`, `ion_autonomous_loop.py`, many carrier audit surfaces |
| `ion_carrier_mount_receipt` | `ion_mcp_local_bridge.py`, `ion_codex_solo_context.py` |
| `ion_operator_artifact_hygiene_check` | `ion_codex_carrier_transfer_package.py` |

### VERIFIED — vNext-only controls not imported by live monolith

`rg ion_receipt_core|ion_context_package_core|ion_promotion_plan_core|ion_source_pool_audit` under `ION/04_packages/kernel` → **no matches**.

`from kernel.` / `import kernel.` under `ION_VNEXT/` → confined to `ion_core/tests/control/*` (isolated test package).

### INFERENCE

Live runtime execution path (Codex queue, MCP connector, carrier task return, Domain Weaver monolith) resolves `kernel.*` to **`ION/04_packages/kernel`**. Canon registry paths under `02_kernel/ion_core/src/kernel/` describe **candidate authority documentation**, not the bound import surface for production carriers today.

---

## Recommended reconciliation strategy (candidate — not ratified)

**Gate:** Operator approval + nemesis review before any source edit, registry ratification, or PYTHONPATH change. This section is planning only.

### Group A — Live path / movement / proof gates (9 controls: 3 IDENTICAL + 6 DIVERGED shared modules)

| controls | recommended authority | approach |
|----------|----------------------|----------|
| `ai_movement_gate`, `codex_work_request_target_binding`, `template_action_gate` | Either (already identical) | **Sync bookkeeping only** — optional single-source copy to vNext or mark monolith as mirror; low risk. |
| `path_authority`, `workspace_root_registry` | **Monolith** for live runtime | **Promote-and-replace into vNext canon copy** after nemesis review of manifest discovery vs `resolve_repo_root` default — or merge `discover_workspace_manifest` back into monolith if upward discovery is still required doctrine. Minimal shim **not** advisable (behavioral fork on manifest resolution). |
| `agent_cwd_boundary`, `context_proof_gate`, `operator_artifact_hygiene_check` | **Monolith** | **Promote-and-replace vNext copies** to match monolith (Codex mount allowance, stricter proof evidence, expanded forbidden export paths). Live connectors already depend on monolith semantics (`has_machine_read_evidence`). |
| `carrier_mount_receipt` | **Monolith** (cosmetic) | **Trivial sync** of docstring/non_claims text; no shim needed. |

**Why monolith wins here:** VERIFIED live imports and June 2026 operational fixes (Codex agent mount, MCP proof gate, export hygiene) are already on the monolith tree.

### Group B — vNext core primitives (4 controls: ONLY_IN_VNEXT)

| controls | recommended authority | approach |
|----------|----------------------|----------|
| `receipt_core`, `context_package_core`, `source_pool_audit_core`, `promotion_plan_core` | **vNext (`ion_core`)** as canonical implementation | **Promote-and-copy into monolith** when live runtime must enforce receipt/context-package gates (registry `dogfood_required_controls` already require these before several claims). Re-export shim alone is insufficient until monolith callers exist — copy module files into `ION/04_packages/kernel/` then wire imports in steward/receipt surfaces. Until wired, registry truth and runtime truth remain split. |

### Group C — vNext cutover harness stack (16 controls: `vnext_*` ONLY_IN_VNEXT)

| controls | recommended authority | approach |
|----------|----------------------|----------|
| M87–M102 `vnext_*` modules | **vNext (`ion_core`)** | **Keep primary home in `ion_core`** for candidate cutover artifacts; **do not** bulk-copy into monolith pre-cutover. Optional thin monolith **re-export shim** (`from kernel.ion_vnext_readiness_lock import ...` after copy) only when a live carrier must invoke harness CLI from `PYTHONPATH=ION/04_packages`. Domain Weaver already references vNext paths as review targets, not imports. |

### Group D — Registry vs runtime binding

| item | recommendation |
|------|----------------|
| `CONTROL_SURFACE_REGISTRY.yaml` `source_module` paths | After Group A/B landing, **update registry** to dual-path or single authoritative path with receipt — today registry cites vNext paths while live tree is monolith (**VERIFIED mismatch**). |
| Root `pyproject.toml` | **INFERENCE:** eventual optional editable install of `ion_core` controls into monolith package or unified `kernel` namespace — requires packaging decision; not a shim-only fix. |
| Namespace collision | **VERIFIED:** both trees use package name `kernel` — reconciliation must pick one on-disk home per module true name to avoid PYTHONPATH ambiguity. |

### Minimal shim vs promote-and-replace summary

| situation | advise |
|-----------|--------|
| IDENTICAL modules | either tree; sync for hygiene |
| DIVERGED live gates | **promote-and-replace** (monolith → vNext canon copy, or vNext ← monolith for registry alignment) |
| ONLY_IN_VNEXT primitives needed live | **promote-and-copy** into monolith + import wiring |
| ONLY_IN_VNEXT cutover harnesses | **keep in vNext** until cutover binding packet; shim only for explicit cross-PYTHONPATH CLI invocation |

---

## Non-claims

- No production authority, live execution authority, or accepted-state claim from this artifact.
- Synthesis is candidate evidence for packet `PCKT-VNEXT-KERNEL-MONOLITH-RECONCILIATION-AND-RUNTIME-BINDING-20260617`; not ratification.
- Line counts and `diff` results are point-in-time on 2026-06-17 UTC.
