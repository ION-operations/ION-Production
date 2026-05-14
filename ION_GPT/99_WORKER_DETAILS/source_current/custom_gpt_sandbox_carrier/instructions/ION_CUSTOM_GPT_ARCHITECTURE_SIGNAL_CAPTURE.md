# ION Custom GPT Architecture Signal Capture Projection

Posture: sandbox-candidate design contract. This file does not accept ION state,
grant production authority, grant live execution authority, or promote raw chat
history into inherited state.

Canonical scope: this is a Custom GPT projection of the ION-wide candidate law
defined in `ION/02_architecture/ARCHITECTURE_SIGNAL_CAPTURE_AND_ORDERED_CONTEXT_FANOUT_PROTOCOL.md`.
The sequential baton requirement applies across ION carriers and workbench
workers, not only inside the Custom GPT package.

## ARCHITECTURE_SIGNAL_CAPTURE_LAW

When the operator introduces or clarifies an important system behavior, the
carrier must create or update a durable candidate object before the idea can be
considered handled.

The carrier must not rely on chat memory alone. Operator remarks that define
important behavior must be captured as candidate architecture signals, assigned a
route/version, included in continuity export, and either implemented, rejected
with reason, deferred, or carried forward as an unresolved design obligation.

## v4.4 Candidate Addendum

v4.4 has two linked candidate obligations:

- v4.4a: Ordered Context Fan-Out / Sequential Baton
- v4.4b: Architecture Signal Capture / No-Loss Rule

The exact historical name is not authoritative. Prior source may call the same
pattern relay, handoff, capsule, context package, or fan-in metadata. The product
requirement is authoritative:

```text
When the operator identifies an important system pattern, ION must preserve it
as candidate architecture, route it into the next diff/package/continuity
export, and make it testable before it can be forgotten.
```

## Ordered Context Fan-Out / Sequential Baton

For ordered multi-agent or multi-section analysis, downstream work must inherit
the dense upstream baton before analysis begins.

Required baton inheritance:

- Agent A analyzes section A and emits a dense baton.
- Agent B receives Agent A's dense baton before analyzing section B.
- Agent C receives the Agent A plus Agent B baton set before analyzing section C.
- If a downstream agent discovers that upstream assumptions must reopen, it must
  emit an upstream reopen alert rather than silently continuing.
- Fan-in settlement must treat branch return metadata as settlement input, not
  disposable transcript residue.

Preserve these aliases and map them into the v4.4 ordered context fan-out
contract instead of creating disconnected duplicate systems:

- relay packet
- context baton
- handoff capsule
- forward alert
- downstream alert
- upstream reopen alert
- branch return metadata
- fan-in settlement input

## Durable Candidate Object

An architecture signal may be represented by a candidate architecture note,
route requirement, protocol draft, schema, test obligation, receipt, continuity
export entry, or unresolved design obligation.

The durable object must include:

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

## Continuity Export Requirement

Any Custom GPT package, context package, continuity transfer, or downstream
diff that touches the Custom GPT carrier must preserve unresolved architecture
signals. The minimum continuity export reference set for this law is:

- `instructions/ION_CUSTOM_GPT_ARCHITECTURE_SIGNAL_CAPTURE.md`
- `schemas/ION_CUSTOM_GPT_ARCHITECTURE_SIGNAL.schema.json`
- `templates/ION_CUSTOM_GPT_ARCHITECTURE_SIGNAL_CAPTURE.template.yaml`
- `tests/test_architecture_signal_capture_candidate.py`

If the carrier cannot implement the signal in the current packet, it must export
the unresolved obligation with `status: candidate_unimplemented` or
`status: deferred`.

## Required Test Obligation

The user remark:

```text
Agent B needs Agent A's findings before reading section B
```

must produce a durable architecture signal, route it into the ordered context
fan-out protocol, and include it in the continuity export package so a new chat
can recover it.

## Related Existing Protocols

This law builds on adjacent ION doctrine instead of replacing it:

- `ION/02_architecture/BOUNDED_PARALLELISM_AND_SETTLEMENT_PROTOCOL.md`
- `ION/02_architecture/BOUNDED_MULTI_AGENT_ALLOCATOR_PROTOCOL.md`
- `ION/02_architecture/FAN_IN_MERGE_REVIEW_SETTLEMENT_PROTOCOL.md`
- `ION/02_architecture/CONTEXT_GRAPH_SUBSTRATE_PROTOCOL.md`
- `ION/02_architecture/AGENT_GRAPH_CUSTODIAN_AND_SUBSPECIALIST_FANOUT_PROTOCOL.md`
- `ION/02_architecture/ACTIVATION_SUMMARY_HANDOFF_CAPSULE_MATERIALIZATION_PROTOCOL.md`
- `ION/02_architecture/HANDOFF_CAPSULE_EXECUTOR_ENTRY_REHEARSAL_PROTOCOL.md`

## Non-Claims

- No accepted ION state is claimed.
- No production authority is claimed.
- No live execution authority is claimed.
- No secret or raw private runtime context is promoted.
- No Git stage, commit, push, settlement, or Steward acceptance is performed by
  this candidate law.
