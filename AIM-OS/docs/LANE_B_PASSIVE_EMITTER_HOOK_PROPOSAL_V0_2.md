# Lane B - Passive Emitter Hook Proposal v0.2

Status: Proposal only (no runtime wiring)  
Date: 2026-03-01  
Lane: B (Contextual Sync convergence)  

---

## Mission Scope

Define the first merge-ready **observational passive hook** that can later emit Shadow BCI records from live mapper flow behind a feature flag.

This document is intentionally:

- insertion-point precise
- fail-open by design
- off-by-default
- non-invasive to live behavior

This document is **not** the implementation.

---

## Constraints (Frozen Doctrine)

- Mapper remains deterministic truth plane.
- Daemon remains tool/memory/orchestration plane.
- Kernel remains supervision/routing/access plane.
- Contextual Sync remains additive superstrate.
- No hard sync gate.
- No live hook wiring in this phase.
- No edits to `kernel_planes`, `context_service`, mapper core internals, or `daemon_bridge`.

---

## 1) Candidate Hook Point Re-evaluation

## Candidate A - post-extraction

Location shape:

- immediately after `extractor.extract(...)` returns `ExtractedFile`

Data available:

- `path`, `imports`, `contracts`, `confidence`
- caller still has `source_text`
- **no** resolved dependency list yet

Assessment:

- Blast radius: low
- Observability quality: medium (missing dependency context)
- Coupling risk: low
- Complexity: low
- Extensibility: medium

Verdict:

- feasible, but not best first hook for useful L0 quality.

## Candidate B - post-resolution (recommended)

Location shape:

- immediately after local dependency resolution completes and before envelope is assembled/returned.

Data available:

- extracted file shape
- resolved dependency paths
- caller source text
- parse confidence

Assessment:

- Blast radius: low
- Observability quality: high for first passive slice (atoms + L0/L5)
- Coupling risk: low (orchestration boundary, not parser internals)
- Complexity: low-medium
- Extensibility: high

Verdict:

- **best first passive hook**.

## Candidate C - post-envelope assembly

Location shape:

- after envelope object/string is assembled

Data available:

- parse confidence and envelope-level fields
- may require unpacking to recover per-field adapter input

Assessment:

- Blast radius: low-medium
- Observability quality: medium
- Coupling risk: medium (ties hook to envelope representation changes)
- Complexity: medium
- Extensibility: medium

Verdict:

- safe later, not ideal first cut.

---

## 2) Exact Proposed Hook Location

Recommended insertion point (unambiguous statement):

> At the **post-resolution orchestration boundary**, immediately after local dependency resolution has produced a finalized dependency list and immediately before envelope assembly/return to caller.

Concrete code-shape anchors already present in project context:

- Current lab flow: `context_mapper_lab/src/main.rs` after `resolve_imports(...)`.
- Promoted orchestration shape: `docs/recent_work_for_gpt_context/phase2c_context_mapper/api.rs` after dependency path enrichment and before `SystemEnvelope::new(...)`.

This point is observational, has complete first-cut payload, and avoids parser/resolver internal mutation.

---

## 3) Hook Payload Contract

Payload emitted by hook (adapter input target):

```json
{
  "source_path": "string",
  "source_text": "string",
  "imports": ["string"],
  "contracts": [
    { "kind": "string", "name": "string", "signature": "string|null" }
  ],
  "parse_confidence": "High|Degraded|Fallback",
  "resolved_dependencies": ["string"],
  "observed_at": "ISO-8601 optional"
}
```

### Field availability at proposed hook

| Field | Availability at hook | Notes |
|---|---|---|
| `source_path` | direct | from extracted file path |
| `source_text` | direct/cheap | available at call boundary that already read file |
| `imports` | direct | from extracted output |
| `contracts` | direct | from extracted output |
| `parse_confidence` | direct | from extracted output |
| `resolved_dependencies` | direct | from resolver output; path stringify/normalize |
| `observed_at` | derived cheap | timestamp at hook invocation |

### Not available at hook (v0.2)

- trustworthy deep re-export certainty
- mature symbol usage truth beyond current placeholders
- contradiction/drift state from historical comparisons
- advisory sync-state engine outputs

---

## 4) Feature Flag Proposal

Flag:

- `AIMOS_SHADOW_BCI_PASSIVE_EMIT`

Default:

- `false` / off (if unset, empty, `"0"`, `"false"`)

Enable semantics:

- enabled only when explicitly set to `"1"` or `"true"` (case-insensitive)

Flag type:

- runtime environment flag for first slice

Why runtime env for first slice:

- smallest surface area
- no new config system required
- easy rollback (`unset` flag)
- easy local/CI toggling

---

## 5) Failure Behavior (Fail-Open Policy)

Core rule:

- shadow emission must never break mapper live success path.

If flag is disabled:

- no adapter/emitter execution
- no impact

If flag is enabled and emission succeeds:

- log debug/info event
- continue live path

If flag is enabled and emission fails:

- log warning with error summary
- drop shadow result
- continue live path unchanged
- no retries/backoff/circuit-breaker in v0.2

Surface policy:

- failures are **not** propagated to caller as mapper failure
- no user-facing error mutation in this first passive slice

---

## 6) Logging / Observability Posture (Minimal)

Recommended minimal events:

1. `shadow_emit_attempt` (debug)
   - fields: `source_path`, `contract_count`, `import_count`
2. `shadow_emit_success` (debug/info)
   - fields: `record_count`, `elapsed_ms`
3. `shadow_emit_failure` (warn)
   - fields: `source_path`, `error_class`, `error_message`

Operational posture:

- keep logs lightweight
- no new telemetry platform required
- enough detail to confirm hook behavior and troubleshoot failures

---

## 7) Blast Radius & Merge Risk Analysis

### Eventually touched (implementation phase, not this phase)

- one mapper orchestration boundary file (where extraction + resolution + envelope are coordinated)
- one small passive emission adapter/hook module (new file)
- optional tiny env flag utility helper

### Explicitly untouched

- extractor internals
- resolver internals
- envelope internals
- daemon bridge internals
- kernel routing planes
- context service seam

### Risk to live request behavior

- low, if implemented with:
  - off-by-default flag
  - fail-open policy
  - no return-path mutation

### Preconditions for safe implementation later

- adapter contract remains aligned to actual orchestration payload
- shadow emission is wrapped in non-propagating error boundary
- implementation adds no blocking synchronization behavior

---

## 8) Tiny Illustrative Pseudocode

```text
result = run_mapper_pipeline(target_path)
  extracted = extract(...)
  resolved = resolve(...)

if env_flag("AIMOS_SHADOW_BCI_PASSIVE_EMIT") == true:
    try:
        adapter_input = adapt({
            target_source,
            extracted_file: extracted,
            resolved_local_files: resolved,
            observed_at: now()
        })
        shadow_records = emit_shadow(adapter_input)
        log_debug("shadow_emit_success", record_count, elapsed_ms)
    except Exception as e:
        log_warn("shadow_emit_failure", source_path, error=e)
        # swallow error, continue

envelope = build_envelope(extracted, resolved, ...)
return envelope
```

---

## 9) Merge Classification

- **Safe now**
  - proposal docs and isolated planning artifacts
- **Safe later**
  - feature-flagged observational passive hook implementation at post-resolution boundary
- **Not safe yet**
  - hard sync gates
  - behavior-affecting routing changes
  - contradiction/drift enforcement in live path

---

## 10) Conclusion

The first passive hook should sit **post-resolution, pre-envelope assembly** at mapper orchestration boundary, guarded by `AIMOS_SHADOW_BCI_PASSIVE_EMIT` (default off), and run under strict fail-open semantics.

This keeps live behavior sovereign while enabling first observational Contextual Sync superstrate emissions when explicitly enabled later.
