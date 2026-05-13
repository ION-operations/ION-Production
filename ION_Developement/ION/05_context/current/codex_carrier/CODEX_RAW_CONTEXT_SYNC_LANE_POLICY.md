# Codex Raw Context Sync Lane Policy

Status: active candidate policy for the Codex carrier domain.

Raw Codex context is valuable local diagnostic continuity while ION is still being perfected.
It is not accepted ION state.

## Rule

```text
Raw Codex context may diagnose.
Raw Codex context may not govern.
Manifested, redacted, proof-gated excerpts may support settlement.
Receipts and settlement decide inheritance.
```

## Storage classes

- Raw snapshots live under `.ion_private/codex_raw_context/` by default.
- Raw snapshots are gitignored and excluded from Drive/context mirrors by default.
- Repo-visible manifests may record hash/provenance without content.
- Redacted excerpts require a packet-bound review and proof path before shared inheritance.

## Authority

```json
{
  "accepted_state_authority": false,
  "browser_control_authority": false,
  "live_execution_authority": false,
  "production_authority": false,
  "raw_content_exported": false,
  "schema_id": "ion.codex_raw_context_sync_lane.v1",
  "secrets_authority": false
}
```
