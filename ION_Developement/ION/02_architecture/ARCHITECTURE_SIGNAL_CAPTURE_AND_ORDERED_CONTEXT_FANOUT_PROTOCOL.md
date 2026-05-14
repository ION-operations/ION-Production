---
type: architecture_protocol
authority: A3_CANDIDATE
created: 2026-05-13T00:00:00-04:00
status: CANDIDATE
purpose: Preserve important operator-identified system patterns as durable candidate architecture and define ION-wide ordered context fan-out baton inheritance.
connections:
  - ION/02_architecture/BOUNDED_PARALLELISM_AND_SETTLEMENT_PROTOCOL.md
  - ION/02_architecture/FAN_IN_MERGE_REVIEW_SETTLEMENT_PROTOCOL.md
  - ION/02_architecture/BOUNDED_MULTI_AGENT_ALLOCATOR_PROTOCOL.md
  - ION/02_architecture/CONTEXT_GRAPH_SUBSTRATE_PROTOCOL.md
  - ION/02_architecture/AGENT_GRAPH_CUSTODIAN_AND_SUBSPECIALIST_FANOUT_PROTOCOL.md
  - ION/02_architecture/ACTIVATION_SUMMARY_HANDOFF_CAPSULE_MATERIALIZATION_PROTOCOL.md
  - ION/02_architecture/HANDOFF_CAPSULE_EXECUTOR_ENTRY_REHEARSAL_PROTOCOL.md
---

# Architecture Signal Capture and Ordered Context Fan-Out Protocol

## Posture

This is ION-wide candidate architecture law. It is not limited to the Custom GPT
carrier and it does not claim accepted ION state, production authority, live
execution authority, or secrets authority.

Custom GPT, Codex CLI, ChatGPT Browser, MCP Actions, local project workbench
workers, browser-extension companions, and future carriers may each expose their
own projection of this law. Those projections inherit this ION-wide contract;
they do not replace it.

## ARCHITECTURE_SIGNAL_CAPTURE_LAW

When the operator introduces or clarifies an important system behavior, ION must
create or update a durable candidate object before the idea can be considered
handled.

The object may be:

- candidate architecture note
- route requirement
- protocol draft
- schema
- template
- test obligation
- receipt
- continuity export entry
- unresolved design obligation

The carrier must not rely on chat memory alone.

The signal must be assigned a route/version, included in the next applicable
diff, package, or continuity export, and carried forward until it is implemented,
deferred, or rejected with reason.

## Ordered Context Fan-Out / Sequential Baton

Ordered context fan-out is the ION-wide rule for sequential branch inheritance.
It applies when sections, domains, files, projects, agents, or worker branches
must be analyzed in a dependency order.

Minimum baton inheritance:

- Agent A analyzes section A and emits a dense baton.
- Agent B receives Agent A's dense baton before analyzing section B.
- Agent C receives the Agent A plus Agent B baton set before analyzing section C.
- Any later branch receives the accumulated baton set required by its dependency
  order before starting analysis.
- If a downstream branch discovers that upstream assumptions must reopen, it
  emits an upstream reopen alert rather than silently continuing.
- Fan-in settlement treats branch return metadata as settlement input, not
  disposable transcript residue.

This is not ordinary parallel fan-out. It is ordered fan-out with inheritance.
The parent scope may still schedule work across carriers, but a downstream
carrier cannot lawfully analyze its section until the required upstream baton is
mounted.

## Alias Mapping

The exact historical name is not authoritative. Prior source may use any of
these terms:

- relay packet
- context baton
- handoff capsule
- forward alert
- downstream alert
- upstream reopen alert
- branch return metadata
- fan-in settlement input

When prior source uses those terms for this behavior, route it into this
protocol rather than creating a disconnected duplicate system.

## Candidate Object Fields

Architecture signal objects must preserve:

- `signal_id`
- `captured_at_utc`
- `source`
- `raw_summary`
- `normalized_requirement`
- `aliases`
- `related_existing_protocols`
- `product_version_target`
- `status`
- `continuity_export_required: true`
- `tests_required: true`
- `accepted_state_claim: false`
- `route`
- `continuity_export_refs`

Allowed `source` values:

- `operator_chat`
- `mounted_doc`
- `codex_return`
- `artifact`

Allowed `status` values:

- `candidate_unimplemented`
- `candidate_implemented`
- `deferred`
- `rejected_with_reason`

## Continuity Export Law

Continuity export must include unresolved architecture signals that affect the
next route, diff, package, or workbench lane.

For the ordered fan-out case, the export must preserve enough information for a
new chat or carrier to recover:

- the operator remark or mounted artifact summary,
- the normalized product requirement,
- the alias map,
- the related protocols,
- the current implementation status,
- the required test obligation,
- and the next route or package target.

If the current packet cannot implement the signal, it must carry the unresolved
obligation forward rather than dropping it.

## Test Obligation

A user remark like:

```text
Agent B needs Agent A's findings before reading section B
```

must produce a durable architecture signal, route it into ordered context
fan-out, and appear in a continuity export or context package so a new chat can
recover it.

## Relation To Current Dirty-Tree Work

The recovered dirty-tree audit is candidate operational evidence. It confirms
that current work is mixed across duplicate-audit hardening, project workbench
source, runtime/evidence residue, Codex context state, ION_GPT package residue,
Needs_Routed candidates, and one stale package-builder hazard.

That audit must not be broad-staged as source truth. It should route into the
next scoped packet or commit-boundary review, with runtime and evidence paths
excluded unless explicitly selected as proof artifacts.

## Non-Claims

- No accepted ION state is claimed.
- No production authority is claimed.
- No live execution authority is claimed.
- No Git stage, commit, push, or settlement is performed by this protocol.
- No raw private Codex memory, session content, credential, or runtime secret is
  promoted by this protocol.
