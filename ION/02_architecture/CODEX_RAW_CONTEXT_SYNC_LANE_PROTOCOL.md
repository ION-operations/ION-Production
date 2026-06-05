# Codex Raw Context Sync Lane Protocol

Status: active candidate protocol
Authority: Codex carrier-domain diagnostic continuity only
Accepted-state authority: false
Production authority: false
Live execution authority: false

## Purpose

Raw Codex context can be valuable while ION is still under active development. It can preserve session-local debugging continuity, expose why a Codex lane made a decision, and help diagnose failures that receipts alone may not yet explain.

This protocol preserves that value without letting raw Codex memory, session transcripts, hidden reasoning, credentials, or private operator material become accepted ION state.

## Core rule

```text
Raw Codex context may diagnose.
Raw Codex context may not govern.
Manifested, redacted, proof-gated excerpts may support settlement.
Receipts and settlement decide inheritance.
```

## Storage model

Raw snapshots default to:

```text
.ion_private/codex_raw_context/<agent_tag>/<session_id>/
```

This path is private/local by default. It must be gitignored and excluded from Drive/context mirrors unless a separate explicit packet changes that policy.

Repo-visible manifests live at:

```text
ION/05_context/current/codex_carrier/raw_context_manifests/<manifest_id>.json
```

Branch-capsule-local manifest refs may live at:

```text
ION/05_context/current/agent_context_branches/<...>/RAW_CONTEXT_MANIFEST.json
```

## Public-safe manifest

A raw context manifest may record:

```json
{
  "schema_id": "ion.codex_raw_context_manifest.v1",
  "manifest_id": "rawctx_...",
  "agent_tag": "codex_local_ion_mason",
  "session_id": "codex_session_...",
  "branch_id": "branch_...",
  "packet_id": "PCKT-...",
  "snapshot_storage_class": "local_private_gitignored",
  "snapshot_content_committed": false,
  "snapshot_mirrored_externally": false,
  "snapshot_sha256": "sha256:...",
  "redaction_status": "not_exported",
  "promotion_state": "not_promoted"
}
```

A manifest must not contain raw Codex transcript text, memory text, hidden chain-of-thought, credentials, browser profile material, private operator logs, or unredacted provider/tool outputs.

## Promotion path

```text
native Codex session / memory
-> local-private raw snapshot
-> public-safe manifest
-> packet-bound redacted diagnostic excerpt or summary
-> proof gate
-> receipt / settlement
-> inheritable ION state
```

## Cockpit semantics

The cockpit should show raw context as a guarded lane:

```text
available / unavailable
agent/session owner
private snapshot manifest
raw content committed: true/false
external mirror: true/false
redaction status
summary/excerpt refs
proof gate status
settlement status
```

The display must keep these categories visually distinct:

```text
raw private context
public manifest
redacted candidate evidence
rolling context
branch capsule
receipt
settled accepted state
```

## MCP exposure

MCP may expose a read-only status projection:

```text
ion.codex.raw_context.status
```

That tool may report manifest counts, policy presence, gitignore guard state, and non-authority boundaries. It must not read raw context contents, write manifests, mirror snapshots, or start workers.

## CLI surfaces

Read-only status:

```bash
PYTHONPATH=ION/04_packages python3 -m kernel.ion_codex_raw_context_sync status --ion-root . --json
```

Initialize policy and private-storage gitignore guard:

```bash
PYTHONPATH=ION/04_packages python3 -m kernel.ion_codex_raw_context_sync init \
  --ion-root . \
  --confirmation ION_CODEX_RAW_CONTEXT_SYNC_WRITE_CONFIRMED \
  --json
```

Create a public-safe manifest for a local-private snapshot:

```bash
PYTHONPATH=ION/04_packages python3 -m kernel.ion_codex_raw_context_sync manifest \
  --ion-root . \
  --agent-tag codex_local_ion_mason \
  --session-id codex_session_... \
  --branch-id branch_... \
  --packet-id PCKT-... \
  --branch-capsule ION/05_context/current/agent_context_branches/... \
  --snapshot-path .ion_private/codex_raw_context/codex_local_ion_mason/codex_session_.../snapshot.json \
  --confirmation ION_CODEX_RAW_CONTEXT_SYNC_WRITE_CONFIRMED \
  --json
```

## Non-claims

This protocol does not:

```text
make Codex memory accepted ION state
read hidden Codex memory/transcript contents
commit raw Codex context
mirror raw context externally
settle branch output
grant production authority
grant live execution authority
grant secrets authority
replace receipts, gates, or settlement
```
