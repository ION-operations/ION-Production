```
lane_id: ion_vnext_kernel_core (ordinal 8)
request_id: codex_req_domain_weaver_dynamic_swarm_08_domain_ion_vnext_kernel_core_20260602_attempt_001
objective_sha256: cabc5120e9be509ee7534e43ec4a455105b7d16a6e2c6513bfd3e3bd93882597
source_target: ION_VNEXT/02_kernel/ion_core
produced_by: Composer carrier (role.mason) — fresh durable re-drive after run-exhaust pruning
produced_at: 2026-06-17T03:41:11Z
write_posture: candidate_only
```

### CONTEXT PROOF

**Shell root proof (VERIFIED):** commands run from `/home/sev/ION - Production/ION_Developement`. Present on disk: `pyproject.toml` (shell root, `ion-kernel` package → `ION/04_packages`), `ION/REPO_AUTHORITY.md`, and target `ION_VNEXT/02_kernel/ion_core/pyproject.toml` (`ion-kernel-vnext-control` → `src/kernel`).

**Paths read (one-line note each):**

| Path | Note |
| --- | --- |
| `ION_VNEXT/02_kernel/ion_core/README.md` | Long-form ION orientation; **stale** — points executable center at `ION/04_packages/kernel/`, not this package |
| `ION_VNEXT/02_kernel/ion_core/REPO_AUTHORITY.md` | Copied monolith authority doc; describes `ION/` content root absent from `ion_core` shell |
| `ION_VNEXT/02_kernel/ion_core/pyproject.toml` | vNext control package: `testpaths = ["tests/control"]`, zero deps, Python ≥3.11 |
| `ION_VNEXT/02_kernel/ion_core/ION_CONTEXT_CAPSULE.shell_root.yaml` | Branch capsule for repo root; references `ION/` child domain not present under `ion_core` |
| `ION_VNEXT/02_kernel/ion_core/ION_CONTEXT_CAPSULE.content_root.yaml` | Capsule for `path: ION` subtree — **unresolvable** from `ion_core` shell (no `ION/` dir) |
| `ION_VNEXT/02_kernel/ion_core/src/kernel/__init__.py` | Package docstring only; no re-exports |
| `ION_VNEXT/02_kernel/ion_core/src/kernel/*.py` (30 modules) | Dependency-closed vNext control surfaces M35–M102 |
| `ION_VNEXT/02_kernel/ion_core/tests/control/*.py` (29 files) | Control tests; hardcode operator workspace paths |
| `ION_VNEXT/00_front_door/AI_START_HERE.md` | M103C front door; control-test invocation from `../02_kernel/ion_core` |
| `ION_VNEXT/00_front_door/AUTHORITY_BOUNDARIES.md` | M102 authority ceiling; all execution gates closed |
| `ION_VNEXT/01_canon/QUALITY_STANDARD.yaml` | Production-quality bar (candidate) |
| `ION_VNEXT/01_canon/CONTROL_SURFACE_REGISTRY.yaml` | 29 controls mapped to `02_kernel/ion_core/src/kernel/*` |
| `ION_VNEXT/01_canon/DOMAIN_WEAVE_READ_FIRST_BINDING.yaml` | M103B read-first binding; `can_continue_locally: false` |
| `ION/04_packages/kernel/ion_domain_weaver.py` (~L8273–8393) | `_domain_weaver_vnext_productization_lanes`; lane 8 spec + guard |
| `ION/tests/test_kernel_ion_agent_control_plane.py` (~L5880–6040) | Dynamic-swarm / vNext productization lane assertions |
| `ION/05_context/current/chatgpt_connector/codex_work_requests/codex_req_domain_weaver_dynamic_swarm_08_domain_ion_vnext_kernel_core_20260602_attempt_001.json` | Original work request; status `RETURN_RECORDED_PROOF_ACCEPTED`; body paths point to pruned run dir |
| `ION/05_context/current/domain_weaver/swarm_evolution/DYNAMIC_SWARM_OPERATION_PLAN.candidate.json` | Lane 8 ordinal/path/required_context match engine spec |

**Lane builder currentness (VERIFIED):** `_domain_weaver_vnext_productization_lanes` guard at L8379 requires `target_path.exists()` and non-empty `required_context`. All four required_context files exist; lane would be emitted with ordinal 8.

### TEMPLATE ACTION PROOF

**Import attempt (from `ION_VNEXT/02_kernel/ion_core`):**

```bash
cd "/home/sev/ION - Production/ION_Developement/ION_VNEXT/02_kernel/ion_core"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -c "
import sys
import kernel
from kernel import ion_path_authority, ion_context_proof_gate, ion_template_action_gate
print('import kernel: OK')
print('kernel.__file__:', kernel.__file__)
print('sample imports: OK', ion_path_authority.__name__, ion_context_proof_gate.__name__)
"
```

**Key output (VERIFIED):**

```text
python: 3.13.11 | packaged by Anaconda, Inc. | ...
import kernel: OK
kernel.__file__: .../ION_VNEXT/02_kernel/ion_core/src/kernel/__init__.py
sample imports: OK kernel.ion_path_authority kernel.ion_context_proof_gate
```

**Import without PYTHONPATH / editable install (VERIFIED failure — reported as gap, not fixed):**

```bash
cd ".../ION_VNEXT/02_kernel/ion_core"
env -u PYTHONPATH python3 -c "import kernel"
```

```text
ModuleNotFoundError: No module named 'kernel'
```

**Pytest invocation (matches `AI_START_HERE.md` + `pyproject.toml`):**

```bash
cd "/home/sev/ION - Production/ION_Developement/ION_VNEXT/02_kernel/ion_core"
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -p no:cacheprovider tests/control -v
```

**Key output (VERIFIED):**

```text
collected 176 items
...
============================= 176 passed in 0.75s ==============================
```

**Namespace collision check (VERIFIED):** with `PYTHONPATH=ION/04_packages` (shell-root convention), `import kernel` resolves to `ION/04_packages/kernel/`, **not** `ion_core/src/kernel`. The two trees share the `kernel` package name but are separate on disk.

### VALIDATION

| Check | Result | Evidence |
| --- | --- | --- |
| `import kernel` (with `PYTHONPATH=src`) | **PASS** | Resolves to `ion_core/src/kernel/__init__.py` |
| Sample submodule imports | **PASS** | `ion_path_authority`, `ion_context_proof_gate`, `ion_template_action_gate` |
| `import kernel` without PYTHONPATH / install | **FAIL** | `ModuleNotFoundError` |
| `tests/control` pytest | **PASS** | **176 passed**, 0 failed, 0 skipped, 0 errors, 0.75s |
| Main shell `pyproject.toml` includes `ion_core` tests | **NOT RUN / absent** | `testpaths = ["ION/tests"]` only — `ion_core` suite isolated |
| Editable install of `ion-kernel-vnext-control` | **NOT ATTEMPTED** | Forbidden in this review posture (`pip install` blocked) |
| Prior lane-8 run body on disk | **MISSING** | `codex_queue_runs/codex_run_2026-06-02T192719Z0000_*_kernel_core_*` — **0 files** (run-exhaust pruned); task_return JSONs retain gate receipts + pointer to missing `task_return_body.md` |

**Module inventory (VERIFIED):** 30 `src/kernel/*.py` modules (~528 KB total); 29 test files; `CONTROL_SURFACE_REGISTRY.yaml` lists 29 controls with matching `source_module` paths — **1:1 alignment**.

**Skipped tests:** none observed.

### LANE CURRENTNESS REVIEW

**Verdict: PARTIALLY CURRENT — on-disk target matches engine lane spec; orientation/docs/runtime binding are stale.**

**Current (VERIFIED):**

- Target path `ION_VNEXT/02_kernel/ion_core` exists with full control package.
- All four `required_context` paths from `_domain_weaver_vnext_productization_lanes` and `DYNAMIC_SWARM_OPERATION_PLAN.candidate.json` exist.
- `CONTROL_SURFACE_REGISTRY.yaml` source modules match actual files; control tests pass.
- Work request JSON still records `RETURN_RECORDED_PROOF_ACCEPTED` with matching `objective_sha256`.
- Lane ordinal 8, `domain_id: domain.ion_vnext_kernel_core`, `required_output: production_spec_kernel_test_and_import_gap_return` unchanged in engine + projection artifacts.

**Stale or missing (VERIFIED / INFERENCE):**

| Item | Status |
| --- | --- |
| Gap-return **body** from 2026-06-02 runs | **MISSING** — only ~1200-char previews in task_return metadata; `codex_queue_runs/` dirs empty |
| `README.md` / `REPO_AUTHORITY.md` under `ion_core` | **STALE** — describe monolith layout (`ION/04_packages/kernel/`, `ION/tests/`) as executable center |
| `ION_CONTEXT_CAPSULE.shell_root.yaml` `child_domains: [ion_core]` + content capsule `path: ION` | **STALE / broken locally** — no `ION/` subtree under `ion_core` shell (`test -d ION` → MISSING) |
| Live runtime kernel | **DIVERGENT** — `ION/04_packages/kernel/` is what Codex/carrier code imports at shell root; not `ion_core` |
| Overlapping modules (`ion_path_authority`, `ion_context_proof_gate`, …) | **DIVERGENT** — `diff` confirms vNext copies differ from monolith (307 vs 287 lines for `ion_path_authority`; 138 vs 180 for `ion_context_proof_gate`) |
| Durable harvest surface for lane bodies | **MISSING until this artifact** — `PRODUCTION_SPINE_AUDIT/VNEXT_LANE_HARVEST/` did not exist pre-write |

**INFERENCE (unverified):** whether the 2026-06-02 accepted return's test counts matched today's 176/176 — original body unavailable for diff.

### PRODUCTION SPEC GAP REVIEW

Ranked by production-cutover impact (candidate assessment):

1. **Dual `kernel` namespace / no runtime binding (CRITICAL)**  
   Live carriers, Codex sync, cycle runner, and MCP surfaces import `kernel.*` from `ION/04_packages` (shell `pyproject.toml`). vNext controls in `ion_core` are canon-registered but **not wired** into live runtime. Parallel implementations have **diverged** on shared true names. Production cutover requires an explicit reconciliation or re-export strategy — not present today.

2. **Packaging / install posture incomplete (HIGH)**  
   `ion-kernel-vnext-control` requires manual `PYTHONPATH=src` or unverified editable install. Shell-root `ion-kernel` package does not include vNext controls. No CI path runs `ion_core/tests/control` from root pytest. `REPO_AUTHORITY.md` inside `ion_core` claims editable-install proof for the **monolith**, not this package.

3. **Authority / orientation docs misaligned with disk (HIGH)**  
   `README.md`, `REPO_AUTHORITY.md`, and branch capsules describe an `ION/` content tree and monolith CLI (`ion_status`, `ion_cycle_runner`, …) that are **not** in the `ion_core` package (30 control modules only; no `ion_status` in vNext tree). Misleading for carriers mounting through lane required_context.

4. **Production authority chain open at M102 (HIGH — by design, still a gap)**  
   `AUTHORITY_BOUNDARIES.md` and `CONTROL_SURFACE_REGISTRY.yaml` record M102 decision draft ready; **no gates closed**, `production_execution_authority_not_set` remains. vNext kernel proves candidate controls, not production authority.

5. **Domain Weaver integration substrate not closed (MEDIUM)**  
   `DOMAIN_WEAVE_READ_FIRST_BINDING.yaml`: `m103b_impact_result.can_continue_locally: false`; steward contacts required before cross-domain mutations. DW lane 7 (`ion_vnext_domain_weaver_integration`) is the natural successor seam; kernel lane does not integrate DW MVP tools into `ion_core`.

6. **Test portability / environment coupling (MEDIUM)**  
   Control tests hardcode absolute paths (`/home/sev/ION - Production/...`). Pass locally but fail portability bar in `QUALITY_STANDARD.yaml` ("not dependent on memory of this chat" / dogfoodable on any Codex host without path surgery).

7. **Harvest durability gap (MEDIUM — addressed by this write)**  
   Accepted swarm returns stored bodies under volatile `codex_queue_runs/`; pruning evaporated lane knowledge. Discipline now needs extension to remaining 7 vNext lanes + fanin/nemesis.

8. **Optional live MCP / Supabase proof deferred (LOW for kernel core, tracked)**  
   `ion_vnext_optional_live_mcp_supabase_smoke_proof` tests pass as local harness; live observation explicitly deferred per M93 canon.

### DOMAIN WEAVER EVOLUTION REVIEW

**Engine alignment (VERIFIED):** Lane 8 is a first-class entry in `_domain_weaver_vnext_productization_lanes` with `candidate_only: True`, `worker_start_authority: False`, `accepted_state_authority: False`. Dynamic swarm plan primary mission: `ion_vnext_production_spec_with_production_grade_domain_weaver_integration`. `test_kernel_ion_agent_control_plane.py` asserts `vnext_productization_lane_count > 0` and lane topology classes.

**Divergence (VERIFIED):**

- **Live execution path:** Domain Weaver monolith (`ION/04_packages/kernel/ion_domain_weaver.py`, ~49K lines) orchestrates lanes; it references `ION_VNEXT/02_kernel/ion_core` as a **review target**, not as imported control modules.
- **Control surface registry vs runtime:** Canon declares vNext modules authoritative for 29 controls; runtime gate strings in monolith (e.g. `kernel.ion_context_proof_gate` in `ion_cycle_runner.py`) resolve to **monolith copies**, not `ion_core` copies.
- **Settlement posture:** 2026-06-02 proof-accepted status on the work request reflects **gate/receipt acceptance**, not production promotion of `ion_core` into the live kernel package.
- **Adaptive topology:** Lane sizing from queue-governor evidence is engine-side; `ion_core` itself contains no DW topology logic — correct for a control-surface lane, but means kernel evolution depends on lane 7 integration work.

**INFERENCE:** Until monolith↔vNext reconciliation lands, Domain Weaver "production-grade integration" remains **plan-level** for kernel core despite local test green.

### BLOCKERS

**Explicit blockers to production cutover / accepted-state move:**

1. **No reconciled single kernel authority** — dual `kernel` trees with diverged implementations; live runtime bound to monolith.
2. **`production_execution_authority_not_set`** — M102 closes no gates; operator authority decision not recorded.
3. **Pruned lane-8 return bodies** — historical evidence incomplete on disk (mitigated by this durable re-drive, not by retroactive recovery).
4. **`DOMAIN_WEAVE_READ_FIRST_BINDING` steward gate** — `can_continue_locally: false` for cross-domain promotion using DW guidance.
5. **No verified editable-install / CI path for `ion-kernel-vnext-control`** — import requires explicit PYTHONPATH today.

**Not blockers for continued candidate review work:** local 176/176 control tests; lane builder inclusion; required_context readability.

### RECOMMENDED NEXT PACKET

**Single most valuable next bounded packet:**

**`PCKT-VNEXT-KERNEL-MONOLITH-RECONCILIATION-AND-RUNTIME-BINDING-20260617`**

**Objective:** Produce a candidate reconciliation plan + proof harness that (a) diffs all 29 shared control true names between `ion_core/src/kernel` and `ION/04_packages/kernel`, (b) selects one authoritative implementation per control with nemesis-reviewed rationale, (c) defines the minimal re-export/shim or promotion path so live carrier imports and `CONTROL_SURFACE_REGISTRY.yaml` agree, (d) rebases `ion_core` README/REPO_AUTHORITY/capsules to describe the vNext package truthfully, and (e) adds a root-level pytest marker or job that runs `ion_core/tests/control` without manual `cd`.

**Role:** `role.mason` + `role.nemesis` review.

**Authority ceiling:** candidate plan + read-only diff artifacts only in first pass; **no source edits** until operator approves reconciliation strategy.

**Evidence that would gate any source edit / promotion:**

- Nemesis-signed diff matrix for all 29 controls with no silent behavior regression.
- Unified pytest: monolith suite + `ion_core/tests/control` green from documented install path (`pip install -e ION_VNEXT/02_kernel/ion_core` or approved shim).
- Updated `REPO_AUTHORITY.md` / capsules matching on-disk layout (VERIFIED by context-proof gate).
- Steward receipt landing reconciliation decision in `ION/05_context/current/` (not chat).
- Explicit operator approval before any live worker start, git push, or production authority claim.

**Follow-on lane (after reconciliation plan):** drive **lane 7** (`ion_vnext_domain_weaver_integration`) with the same durable harvest discipline.

### ION OPERATIONAL POSTURE

This artifact is **candidate-only**. It records read-only inspection, import attempts, and pytest evidence. It does **not** ratify production state, close cutover gates, start live workers, or authorize source edits.

**Before any real change, separate proof packets and explicit authority would be required for:**

| Action | Required authority |
| --- | --- |
| Source edit (reconciliation, README fix, shims) | Operator-approved bounded packet + steward integration |
| Live worker / Codex queue start | DW approval governor + `worker_start_authority` |
| Accepted-state / production cutover | M102+ operator decision record; `production_execution_authority` proof |
| Service restart / MCP mutation / Supabase write | Front-door hard stops per `AUTHORITY_BOUNDARIES.md` |
| Secret access | Explicit vault packet — never from this lane |
| Git push | Operator approval per M97A scope |
| Deletion / archive of runtime artifacts | Steward + source-pool audit |

**Carrier posture:** `role.mason` bounded review worker; one write to durable harvest path only. Synthesis is not settlement. Prior `RETURN_RECORDED_PROOF_ACCEPTED` on the 2026-06-02 request remains a **gate receipt**, not a substitute for this regained body or for production promotion.
