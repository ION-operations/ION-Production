# Codex CLI Resume Adapter Protocol v0.1

Status: candidate local protocol
True name: `codex_d1_codex_resume_adapter`
Carrier: `codex`
Lane: `D`
Production authority: false
Live execution authority: false
Accepted state claim: false

## Core Law

```text
NATIVE CODEX RESUME IS NOT ION CONTINUITY BY ITSELF
```

Codex CLI can resume native interactive or exec sessions by explicit session id
or by `--last`. ION must treat that native session as a carrier continuity
surface, not accepted ION state. A lawful ION resume requires a manifest binding
the native session id to true name, rank, context packages, status, root
identity, leases, and receipts.

This adapter does not run `codex resume`. It only creates session manifests,
lawful-resume decisions, bounded resume prompts, and receipts.

## Observed Local CLI Surface

Local help inspected for this packet showed:

- `codex resume [SESSION_ID] [PROMPT]`
- `codex resume --last`
- `codex exec resume [SESSION_ID] [PROMPT]`
- `codex exec resume --last`

Both resume surfaces can select the most recent session with `--last`. That is
a blind latest-session resume and is blocked by this protocol unless a manifest
explicitly allows it. The candidate default requires an explicit session id.

## Manifest Binding

A Codex resume manifest must bind:

- `codex_session_id`
- `worker_true_name`
- true-name binding status and expiry
- rank vector and rank signature
- status verdict
- cwd and ION root identity with hashes
- context package refs and file hashes
- active Worker Shift lease evidence
- transcript reference classified as witness only
- authority boundary with production/live/accepted/secrets/deploy/push false

Manifest holder:

```text
ION/05_context/current/codex_cli/sessions/
```

Implementation:

```text
ION/04_packages/kernel/ion_codex_resume_adapter.py
```

Template:

```text
ION/07_templates/carriers/CODEX_CLI_RESUME_PACKET.md
```

## Lawful Resume Gate

The adapter blocks resume when any of these are true:

- no explicit session id is supplied while explicit id is required;
- blind `--last` resume is requested under the default policy;
- requested session id does not match the manifest;
- true name is expired or inactive;
- required Worker Shift write lease is missing for a write resume;
- rank signature differs from the manifest unexpectedly;
- cwd or ION root differs from the manifest;
- status verdict is blocked, degraded, unknown, or outside the ready set;
- context package hash drift is detected and not approved;
- requested resume authority includes production or live authority.

Ready status verdicts for this candidate adapter are:

```text
ION_STATUS_READY
ION_STATUS_PARTIAL
ION_STATUS_SINGLE_CARRIER_READY
ION_CODEX_SOLO_CONTEXT_READY
```

## Transcript Classification

Codex native transcript files are witness material. They may help a carrier
remember what happened, but they do not replace:

- ION manifests;
- Worker Shift sign-on, lease, or sign-off receipts;
- rank gates;
- context package hashes;
- settlement receipts.

The adapter must mark transcripts as:

```text
transcript_witness_not_state
```

## Fork and Side Routes

A fork or side route from a resumed session creates a candidate child true name.
It does not create accepted state and cannot settle itself. Any child route must
return evidence through normal Worker Shift and settlement lanes.

## Authority Boundary

This protocol grants no production authority, live execution authority,
accepted-state authority, secret access, deployment authority, GitHub push
authority, or vault access.
