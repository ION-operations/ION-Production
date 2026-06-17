# G2-A — Durable Harvest Capture: APPLY GATE (exit test + state)

```
schema_id:  ion.production_spine.g2a_apply_gate.v0_1_candidate
packet:     PCKT-G2-DURABLE-HARVEST-CAPTURE-AT-INTAKE-20260617
status:     APPLIED to working tree (uncommitted; commit HELD per operator) — verified
posture:    candidate_only (no accepted-state / production / live-worker authority)
provenance: G2_DURABLE_FANIN_PLAN.candidate.md §1; G2A_DRYRUN.candidate.md (5/5 /tmp green);
            orchestrator apply + verification 2026-06-17
```

## What this gate proves

The settlement-time durable harvest mechanism is wired into the live carrier-intake path as a **purely additive, fail-soft** side-effect: a settled lane's return body is copied (hash-verified, idempotent) into the git-tracked `DURABLE_FANIN/` surface **before** the volatile `codex_queue_runs/` body is pruned — without changing acceptance, reconciliation, or fan-in behavior.

## What was applied (working tree)

- **NEW module** `ION/04_packages/kernel/ion_durable_fanin.py` (~130 lines): `durable_fanin_harvest_lane_body(root, request, body_text, *, harvest_source)` — fail-soft entrypoint (top-level try/except, never raises) wrapping an impl that validates the 9 dynamic-swarm sections, computes full-file sha256, writes `DURABLE_FANIN/lanes/LANE{NN}_{SLUG}_GAP_RETURN.candidate.md`, upserts `DURABLE_FANIN/MANIFEST.candidate.json`, is idempotent on `(request_id, objective_sha256)`+hash, and supersedes on hash mismatch. Returns additive-only work-request metadata (`durable_harvest_*`, `intake_accepted=true`, `semantically_settled=false`).
- **Hook 1 — connector** `ion_chatgpt_browser_mcp_connector_contract.py` (in `_evaluate_task_return_packet`, after the accepted-status `_write_json` ~:5095): guarded `if accepted and text.strip():` block, lazy import, full `try/except: pass` outer guard. Applies returned metadata to `request_payload` and re-writes it.
- **Hook 2 — queue runner** `ion_codex_queue_runner.py` (inside the `if accepted:` finalization block, before `_write_run_packet` ~:8543): reads the on-disk `task_return_body_path` via `_read_rel_text_if_exists`, harvests, applies metadata to `request`. Full `try/except: pass` outer guard.

Footprint: 1 new module + ~22 added lines in each of the 2 (already pre-dirty) hook files. **Engine `ion_domain_weaver.py` untouched.**

## Verification (real repo, 2026-06-17)

| Check | Result |
|-------|--------|
| Import sanity (new module + connector + runner import cleanly as `kernel.*`) | **PASS** (`IMPORT_OK`) |
| Live harvest smoke (temp root, committed LANE08 fixture): fresh harvest writes body + manifest (ordinal 8) + `intake_accepted/semantically_settled` honesty fields | **PASS** |
| Idempotent re-harvest (identical body → `idempotent_skip`) | **PASS** |
| Missing-section reject (no write) | **PASS** |
| Fail-soft (induced internal error → `harvested=false`, no raise) | **PASS** |
| Merged 176-control suite (G1 gate; must stay green) | **PASS** (176/176) |
| Real `DURABLE_FANIN/` surface unpolluted by smoke (temp root only) | **PASS** |

### Command

```bash
cd "/home/sev/ION - Production/ION_Developement"
PYTHONPATH="ION/04_packages:ION_VNEXT/02_kernel/ion_core/src" python3 /tmp/g2a_apply_verify.py   # IMPORT_OK + SMOKE_OK
PYTHONPATH="ION/04_packages:ION_VNEXT/02_kernel/ion_core/src" python3 -m pytest ION_VNEXT/02_kernel/ion_core/tests/control -q   # 176 passed
```

## Path correctness (durable surface = the committed surface)

`_resolve_connector_root` returns the dir holding `pyproject.toml` + `ION/REPO_AUTHORITY.md` (the `ION_Developement` root); `CONNECTOR_STATE_DIR = ION/05_context/current/chatgpt_connector` and on-disk `codex_work_requests` confirm it. So `root / DURABLE_FANIN_REL` resolves to `ION/05_context/current/ion_system_definition/PRODUCTION_SPINE_AUDIT/DURABLE_FANIN` — the surface committed in `ddfdb219`. Bodies harvested at runtime are durable in git (commit-as-they-land, per operator).

## Honest scope (what G2-A does / does NOT do)

- **Does:** durably capture settled bodies that carry the locked dynamic-swarm header (`lane_id (ordinal N)` / `request_id` / `objective_sha256`) + 9 sections — i.e. the formatted vNext lane re-drives (the cohort G2-B will re-drive for lanes 1–5).
- **Does NOT yet:** capture arbitrary raw live returns that lack that header — those fail-soft to a no-op. Deriving lane identity from the work-request payload + a section resolver is **G2-B** (broaden coverage). No reconciliation/fan-in change (G2-C/D) and no honesty/nemesis behavior change (G2-E/F) here.

## Holds + reversibility

- **COMMIT HELD** (operator go required; git law). Revert = `rm ION/04_packages/kernel/ion_durable_fanin.py` + delete the two `# G2-A` guarded blocks from the connector and runner.
- Not pushed.

## Next (gated)

G2-B (migrate 10 legacy `VNEXT_LANE_HARVEST/` bodies + manifest backfill + back-harvest lanes 1–5 + broaden capture coverage) → G2-C (reconciliation durable fields, additive) → G2-D (fan-in durable read path, additive) → G2-E (nemesis gate, behavior-change) → G2-F (reconciliation honesty, flag-guarded) → G2-G (exit harness).
