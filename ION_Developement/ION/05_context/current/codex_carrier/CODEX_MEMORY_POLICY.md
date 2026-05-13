# Codex Carrier Memory Policy

Status: active policy for the Codex carrier domain.

Codex memories and raw context may orient and diagnose local work. They are not accepted ION state.

Rules:

- Do not export or print raw `~/.codex` memory/session contents without explicit review.
- Preserve raw context value through local-private snapshots and public-safe manifests, not raw commits.
- Memory summaries may be cited as orientation only.
- Diagnostic excerpts must be redacted, packet-bound, and proof-gated before settlement.
- Durable claims require branch capsule, receipt, proof, or settlement evidence.
- Secret-like content is path/type only unless the operator explicitly authorizes a redacted audit.
- Branch capsule governs current work; settlement governs accepted inheritance.

Authority:

```json
{
  "branch_capsule_governs_current_work": true,
  "codex_memory_role": "bounded_diagnostic_continuity",
  "memory_may_accept_state": false,
  "memory_may_orient": true,
  "raw_context_content_committable_by_default": false,
  "raw_context_drive_mirror_allowed_by_default": false,
  "raw_context_manifest_committable": true,
  "raw_context_may_accept_state": false,
  "raw_context_may_diagnose": true,
  "raw_context_private_storage": ".ion_private/codex_raw_context/<agent_tag>/<session_id>/",
  "raw_context_sync_lane": "manifest_only_by_default",
  "raw_memory_export": "forbidden_without_explicit_review",
  "receipt_or_settlement_required_for_durable_claims": true,
  "schema_id": "ion.codex_carrier_memory_policy.v2",
  "secrets_redaction_required": true
}
```
