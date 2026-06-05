---
type: architecture_protocol
authority: A3_CANDIDATE
created: 2026-05-29T00:00:00-04:00
status: CANDIDATE
protocol_id: ion_connector_transport_and_lod_routing_protocol
purpose: Define connector transport boundaries and level-of-detail routing discipline for bounded ION read/write operations.
connections:
  - ION/02_architecture/ION_ACTION_MCP_BRANCH_LEADER_GATEWAY_PROTOCOL.md
  - ION/02_architecture/ION_CUSTOM_GPT_ACTION_GATEWAY_PROTOCOL.md
  - ION/02_architecture/ION_CHATGPT_BROWSER_HTTP_MCP_PREVIEW_PROTOCOL.md
  - ION/02_architecture/ION_FULL_CARRIER_MCP_PARITY_PROTOCOL.md
  - ION/04_packages/kernel/ion_codex_queue_runner.py
---

# ION Connector Transport and LOD Routing Protocol

## Purpose

This protocol defines how ION connectors carry requests without becoming
authority and how read/write work must be routed through an explicit level of
detail (LOD) ladder.

Transport is not authority.

## Transport Roles and Boundaries

### MCP (local)

MCP is local, branch-native, bounded read/write transport for project-local
operations under active root constraints.

### HTTP Action Gateway (public ingress)

HTTP Action Gateway is the public Custom GPT Action / REST / OpenAPI ingress and
policy membrane. It validates and routes; it does not grant production, live
execution, accepted-state, or secrets authority.

### Branch Gateway before raw tools

Branch Gateway must be used before raw flat tool selection. Route by owner and
branch context first; only then invoke a bounded tool path.

### Codex/local agents

Codex/local agents are the lawful lane for large-repo, multi-file, test/build,
and corpus-scale work that exceeds narrow connector calls.

### Mirror/visibility lanes

Supabase, Mongo, and browser queues are mirror/visibility/carrier lanes unless
explicitly reconciled with receipts proving parity with owner state.

## Read LOD Ladder

Choose the smallest lawful read level that can answer the question.

| Level | Name | Allowed Shape |
| --- | --- | --- |
| L0 | Existence / path / title | File exists, canonical path, top title only. |
| L1 | Branch/domain summary | Owner branch/domain purpose and route summary. |
| L2 | Index / route map | Registry/index listing, route map, manifest pointers. |
| L3 | Excerpts / search hits | Targeted excerpts and query hits with path anchors. |
| L4 | Bounded full file | Full single-file read where bounded and justified. |
| L5 | Sliced/chunked read | Explicit chunks for large files or long artifacts. |
| L6 | Delegated corpus inspection | Delegated multi-file/corpus inspection with receipts. |

## Write LOD Ladder

Choose the smallest reversible write level that can complete the task.

| Level | Name | Allowed Shape |
| --- | --- | --- |
| W0 | Decision / receipt | No file mutation; decision and proof receipt only. |
| W1 | Small candidate file | Add one small candidate file; no overwrite. |
| W2 | Targeted patch | Narrow patch to specific lines/files. |
| W3 | Bounded patch batch | Coordinated small patch set with shared intent. |
| W4 | Chunked artifact upload | Large artifact split into chunks with manifest/hashes. |
| W5 | Delegated implementation | Delegated multi-file implementation with bounded scope and receipts. |

## Confirmation and Idempotency

Any write at W1-W5 requires:

- explicit confirmation token: `ION_BOUNDED_WRITE_CONFIRMED`;
- stable idempotency key bound to objective and target path/scope;
- replay refusal or safe idempotent no-op behavior on duplicate keys;
- receipt proving requested scope, applied scope, and outcome.

## Direct Bounded Repo-Ingest Lane (Candidate)

The ChatGPT Browser MCP connector may perform direct bounded repo ingest without
routing every small mutation through an async Codex packet when all of the
following are true:

- target path is under an allowlisted ingest root;
- secret-like path fragments are absent (`.env`, `secret*`, `credential*`, `vault`);
- overwrite is denied by default (existing targets block and require lifecycle route);
- caller supplies `ION_BOUNDED_WRITE_CONFIRMED` for apply operations;
- idempotency key or deterministic fallback key is recorded;
- receipt includes SHA-256 and unified diff proof.

Current direct-ingest mapping:

- W1 create candidate file: `ion_file_put_text` with `preview_only=true` then apply.
- W2/W3 targeted patch/batch: `ion_bounded_patch_preview` then `ion_bounded_patch_apply`.
- W4 chunked artifact: `ion_artifact_upload_init/chunk/commit`.
- W5 multi-file or high-context tasks: queue through Codex work packet / agent invocation.

## Large Movement Rules

For large file or artifact movement (read or write):

- split data into deterministic chunks;
- emit per-chunk hash and overall manifest hash;
- include chunk order, byte ranges, and total byte count;
- require manifest-level verification before claiming completion.

## State and Drift Rules

Output is not state until accepted with proof.

Connector-visible payloads, queue projections, browser surfaces, or mirror
stores are provisional until reconciled with owner receipts and acceptance flow.

Drift guard:

- if mirror/queue/projection disagrees with owner receipt, owner receipt wins;
- flag drift immediately and block accepted-state claims;
- require explicit reconciliation receipt before continuing as if synchronized.

## Minimal Invariant

- Smallest lawful read.
- Smallest reversible write.
- Owner route before raw tool.
- Proof before state.
- Transport is not authority.
