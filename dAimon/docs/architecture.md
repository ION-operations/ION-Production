# Architecture

```text
User / Operator
  ↓
Google Cloud Agent Builder / Gemini
  ↓ tool calls
ION Kernel on Cloud Run
  ↓
MongoDB MCP Server + MongoDB Atlas
  ↓
continuity_objects · settlement_queue · receipts · sessions
  ↓
Next Gemini session receives only receipt-cleared inheritance bundle
```

## What must be visible in the judged build

The judged build must show a real MongoDB MCP call for governed-state retrieval. Backend API writes can use a conventional MongoDB client, but the contest-required MCP integration must be visible in the agent path.

## Orchestration Layers

The repository now treats orchestration as a first-class product surface. The
machine-readable contracts in `orchestration/` define:

- Product layers and contest proof boundary.
- Governed domains as graph regions.
- Templates for import, classify, route, settle, receipt, inherit, trace, deploy, handoff, and demo claim audit.
- Receipt fields and inheritance status rules.
- Roadmap phases, validation gates, and management cadence.

The long-form operating plan is `docs/full_orchestration_plan.md`.

## Partner Ecosystem Expansion

MongoDB is the first live proof because it carries continuity objects, receipts,
settlement queues, and accepted-only inheritance traces. The other hackathon
partners are represented as governed adapter lanes, not as unsupported live
claims:

- Arize: observability and evaluation over model, retrieval, and tool traces.
- Elastic: evidence search across receipts, claims, logs, artifacts, and
  rejected branches.
- Fivetran: enterprise source ingestion into governed context lanes.
- GitLab: SDLC governance across issues, merge requests, CI, scans, approvals,
  and deploy evidence.

The architecture claim is:

```text
dAimon can connect to many enterprise systems and still know what future AI
work is allowed to trust.
```

The machine-readable partner plan is
`orchestration/partner_adapter_registry.json`; the long-form explanation is
`docs/partner_ecosystem_expansion.md`.
