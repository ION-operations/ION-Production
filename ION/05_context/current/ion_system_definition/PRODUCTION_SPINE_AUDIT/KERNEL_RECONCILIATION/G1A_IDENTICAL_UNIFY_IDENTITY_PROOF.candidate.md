# G1-A — Identical-Unify Identity Proof + Coupling Finding (candidate)

```
schema_id:    ion.production_spine.g1a_identity_proof.v0_1_candidate
packet:       PCKT-G1-IDENTICAL-UNIFY-NAMESPACE-MERGE-SCAFFOLD-20260617 (investigation phase)
generated_at: 2026-06-17T04:20:00Z (approx)
generated_by: Opus (ION North Star / IONOLOGIST mount, lead orchestrator) — direct on-disk evidence
posture:      candidate_only; READ-ONLY investigation; no source edits made
```

## Why this exists

Operator gated G1-A as a **split**: apply the provably-safe identical-unify now, hold the namespace scaffold (the live `kernel/__init__.py` edit) for candidate-diffs-first review. Before applying anything, a read-only investigation tested that premise. **It corrected it:** the collapse is *coupled* to the scaffold and cannot land independently. What is safe to bank now is the **identity proof**; the scaffold must come **first**, then the collapse is behavior-neutral.

## Proof 1 — byte-identity of the 3 IDENTICAL controls (full sha256, monolith == ion_core)

| Control | sha256 (both trees) |
|---------|---------------------|
| `ion_ai_movement_gate` | `06a4eb9e099d0ab6b7b1c04563d3a867113e91060a3ce71e7bcbc6fcbe356161` |
| `ion_codex_work_request_target_binding` | `21d98c067132b55aad67961da5bd8e3f9929ab02de77676116834a35b5a5c9c6` |
| `ion_template_action_gate` | `bb1d1868db945a6fbb40e1c2d61dae3df341603129b77ca54026df563707a634` |

Both copies hash-match exactly ⇒ collapsing them is provably **behavior-neutral** once imports resolve.

## Proof 2 — the 6 DIVERGED controls (monolith != ion_core), confirms the matrix

`ion_agent_cwd_boundary`, `ion_carrier_mount_receipt`, `ion_context_proof_gate`, `ion_operator_artifact_hygiene_check`, `ion_path_authority`, `ion_workspace_root_registry` — all have differing sha256 between the trees. (3 identical + 6 diverged = the 9 shared control true-names; independently re-confirms `KERNEL_CONTROL_DIFF_MATRIX`.)

## Finding — the collapse is COUPLED to the scaffold (premise correction)

Each of the 3 identical `ion_core` modules is **referenced inside `ion_core`** and **pinned in canon**:

| Identical control | Referenced by (kept ion_core surfaces) | Canon registry pin |
|-------------------|----------------------------------------|--------------------|
| `ion_ai_movement_gate` | `ion_vnext_readiness_lock.py` (src) + control test | yes |
| `ion_codex_work_request_target_binding` | `ion_vnext_readiness_lock.py` (src) + control test | yes |
| `ion_template_action_gate` | `ion_vnext_boot_dogfood_smoke.py` (src), `ion_vnext_readiness_lock.py` (src), README + control test | yes |

`ion_vnext_readiness_lock` and `ion_vnext_boot_dogfood_smoke` are exactly the **M87-M102 harnesses we are KEEPING in `ion_core`.** Deleting the 3 identical modules **before** the namespace scaffold resolves `kernel.*` across both trees would break those kept harnesses, the 176-test control suite, and registry resolution. **The collapse therefore cannot precede the scaffold.**

## Corrected ordering for G1-A (replaces the literal split)

1. **G1-A1 — identity proof (THIS doc): DONE, bankable now.** Zero risk; no source change.
2. **G1-A2 — namespace scaffold (candidate-diffs-first, gated):** add `pkgutil.extend_path` to monolith `kernel/__init__.py` + define unified `PYTHONPATH` (monolith-first). This is the live-import-root edit the operator wanted reviewed. Proven via a temp-dir dry run (ion_core 176 tests + import-resolution + monolith smoke) before any real edit.
3. **G1-A3 — collapse the 3 duplicates (after scaffold lands):** behavior-neutral by Proof 1; removes the duplicate `ion_core` copies once imports resolve from the monolith.

> Open empirical question the G1-A2 dry run must answer honestly: with **monolith-first** resolution, `ion_core`'s tests for the **6 diverged** controls would resolve against the *monolith* versions. If any ion_core diverged-control test asserts ion_core-specific behavior, the scaffold may not be green-neutral until G1-B (diverged reconciliation). The dry run reports this rather than assuming it.

## Non-claims

Candidate; read-only; no source edited. Identity is proven; the collapse is *justified* but *not executed*. Scaffold + diverged handling remain gated, diffs-first, and nemesis-auditable.
