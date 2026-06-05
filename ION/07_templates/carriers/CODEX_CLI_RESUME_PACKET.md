# CODEX CLI RESUME PACKET

packet_id:
created_at:
true_name:
codex_session_id:
carrier: codex_cli
mission_movement: codex_resume_adapter
primary_domain: carrier.codex_cli

## Authority

production_authority: false
live_execution_authority: false
accepted_state_claim: false
secrets_authority: false
deploy_authority: false
github_push_authority: false

## Native CLI Surface Observed

```text
codex resume [SESSION_ID] [PROMPT]
codex resume --last
codex exec resume [SESSION_ID] [PROMPT]
codex exec resume --last
```

## Manifest Inputs

```yaml
codex_session_id:
worker_true_name:
transcript_ref:
cwd:
ion_root:
status_verdict:
rank_vector:
  rank_id:
  context_level:
  domain_scope:
  mutation_class:
  settlement_power:
context_package_refs:
  - ION/05_context/current/codex_solo/CAPSULE.md
worker_shift_leases:
  - lease_id:
    worker_id:
    mode:
    paths: []
    status:
required_lease_paths: []
```

## Default Resume Policy

```yaml
require_explicit_session_id: true
blind_last_resume_allowed: false
allow_context_hash_drift: false
actual_resume_execution_allowed: false
```

## Bounded Resume Prompt

```text
# ION Codex CLI Resume Packet

codex_session_id: <native Codex session id>
worker_true_name: <ION true name>
carrier: codex_cli
resume_scope: bounded_candidate_continuity
production_authority: false
live_execution_authority: false
accepted_state_claim: false
secrets_authority: false

Resume posture:
- Treat the native Codex transcript as witness evidence only.
- Use this manifest, Worker Shift leases, rank vector, status verdict, and context hashes as the ION resume gate.
- Do not claim accepted state, production authority, live execution authority, deployment authority, push authority, or secret access.
```

## Required Return Evidence

```yaml
manifest_path:
resume_decision:
receipt_path:
tests:
status_after_work:
worker_shift:
  sign_on:
  lease:
  sign_off:
settlement_recommendation: ACCEPT_CANDIDATE | REVISE | SPLIT | REJECT | QUARANTINE
```
