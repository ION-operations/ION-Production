# dAimon Full Orchestration Plan

This document turns the dAimon concept into the build, management, testing, and release structure for the repository. The machine-readable source of truth lives in `orchestration/*.json`; this document explains how those contracts are used.

## Product Thesis

dAimon treats AI output as a candidate transition, not trusted state.

The core loop is:

```text
import -> classify -> route -> settle -> receipt -> inherit
```

The product is not another memory layer. Memory stores what was said or produced. dAimon governs what future agents may rely on. The contest build is a vertical slice of that trust layer: messy AI work enters, governed objects are classified, settlement decides what is accepted, receipts cite proof, and only receipt-cleared context becomes inheritable.

## Proof Boundary

The contest build may claim:

```text
dAimon demonstrates a local and MongoDB-backed vertical slice of governed inheritance.
```

The contest build must not claim:

```text
production readiness
legal compliance certification
complete Google integration until live proof exists
complete MongoDB MCP integration until live proof exists
fully autonomous governance
that every receipt makes a claim objectively true
that human review is unnecessary
```

When in doubt, the system should preserve the larger product vision but label unproven items as roadmap.

## Layer Model

The product has four repo-visible layer records in `orchestration/product_layers.json`.

### Continuity Substrate

Question answered:

```text
What may the next AI session inherit?
```

Responsibilities:

- Import transcripts, tool returns, documents, code outputs, and demo assets as witness material.
- Classify witness material into continuity objects.
- Route objects into settlement queues.
- Decide accepted, rejected, deferred, caveated, or review-required status.
- Issue receipts.
- Export accepted-only inheritance bundles.

Current proof:

- Local sample demo.
- Local MCP visibility trace.
- MongoDB candidate seed proof.
- MongoDB-backed trace artifact.

Next work:

- Add a small API or dashboard surface.
- Make MongoDB the default contest backing store when credentials are present.
- Add receipt drill-down for each inherited object.

### Generative Governance Engine

Question answered:

```text
What kind of governed intelligence does this problem require?
```

Responsibilities:

- Convert an objective into domains, roles, context packages, proof obligations, and settlement paths.
- Generate work packets for carriers such as Gemini, Codex CLI, local scripts, MongoDB MCP, or human review.
- Detect when a domain is too broad and needs fission.
- Route work by capability, authority, context, proof, and side effects.

Current proof:

- Machine-readable domain and template registries.
- Orchestration validator.

Next work:

- Implement objective-to-domain cartography.
- Generate bounded work packets from accepted receipts.
- Add fission recommendations based on route and receipt history.

### Enterprise Trust Layer

Question answered:

```text
How can an enterprise prove what its AI work relied on?
```

Responsibilities:

- Preserve every meaningful AI action as a receipt-bearing graph event.
- Trace inherited context to settlement decisions.
- Preserve rejected and deferred material as witness.
- Separate technical auditability from compliance claims.

Current proof:

- Receipt registry.
- Test matrix.
- Non-claim boundary in README and docs.

Next work:

- Add graph query API over MongoDB continuity data.
- Add audit export for receipt chains.
- Add enterprise role and authority policies.

### Contest Vertical Slice

Question answered:

```text
Can the trust primitive be demonstrated end to end inside the hackathon boundary?
```

Required demo behavior:

- Messy work enters as candidate material.
- Objects are classified.
- Settlement decides what may inherit.
- Receipts justify accepted state.
- MCP visibility trace returns accepted objects only.
- Excluded objects remain visible as witness.
- A next-session bundle is generated.
- The demo video itself is governed by claim receipts.

## Domain Model

Domains are governed graph regions. Each domain has:

- Context objects.
- Role ownership.
- Templates.
- Proof obligations.
- Authority ceiling.
- Settlement rules.
- Neighbor routes.
- Fission triggers.

The active domains are:

- `continuity_substrate`
- `generative_governance`
- `capability_routing`
- `mcp_visibility`
- `enterprise_trust`
- `cloud_runtime`
- `demo_video_agent`
- `product_ops`

The model should avoid giant prompt-stuffed domains. When one domain accumulates unrelated templates, diverging proof obligations, noisy context packages, or repeated ownership confusion, it should split and preserve lineage.

## Graph Model

dAimon should model meaningful work as a graph.

Node types:

```text
source_bundle
continuity_object
settlement_queue_item
receipt
inheritance_bundle
work_packet
domain
role
template
validation_result
artifact
future_task
```

Edge types:

```text
relies_on
produced_by
settled_by
inherits_from
routes_to
blocks
validates
supersedes
conflicts_with
```

The first implementation can store the graph as JSON documents in MongoDB collections. The important behavior is traceability, not the specific database engine. Later, materialized graph views or a graph database can be added if audit queries require it.

## Template Law

Templates define governed action types. They do not need private chain-of-thought. They require public, checkable action records.

The core templates are:

- `import_witness_bundle`
- `classify_continuity_objects`
- `route_objective`
- `settle_outputs`
- `issue_receipt`
- `resolve_inheritance`
- `mcp_visibility_trace`

Additional contest templates cover capability routing, Google Cloud deployment, Gemini or Agent Builder handoff, demo claim audit, and release packaging.

Every template must state:

- Required context.
- Inputs.
- Outputs.
- Proof obligations.
- Authority ceiling.
- State mutation rule.
- Settlement path.
- Validation method.

## Receipt Rules

A receipt is not a log line. A receipt must answer:

- What was attempted?
- What context was used?
- What proof was available?
- What authority was exercised?
- What changed?
- What was rejected or deferred?
- What may future work inherit?

Required receipt fields are listed in `orchestration/receipt_registry.json`.

Inheritance rules:

- `accepted`: may inherit when receipt-cited and in scope.
- `accepted_with_caveats`: may inherit only with caveats preserved.
- `rejected`: may appear as witness but not trusted context.
- `deferred`: may appear as pending work but not accepted fact.
- `needs_human_review`: blocked until review settles.
- `needs_more_proof`: blocked until proof is supplied and settled.
- `merged`: inherit through the merged target object.
- `archived_as_witness`: inspectable but not trusted.

## Partner Adapter Fabric

MongoDB remains the primary contest proof substrate. The wider product should
show that dAimon has a general partner adapter law:

```text
Every partner becomes a governed context surface.
dAimon decides what future AI work may inherit from it.
```

The partner registry lives in `orchestration/partner_adapter_registry.json`.
It defines MongoDB as the live proof lane and Arize, Elastic, Fivetran, and
GitLab as planned expansion lanes:

- MongoDB: continuity state, receipts, settlement queues, inheritance bundles,
  and MCP trace evidence.
- Arize: observability and evaluation over model, tool, retrieval, and custom
  logic traces.
- Elastic: evidence search across receipts, artifacts, claims, logs, and
  rejected branches.
- Fivetran: enterprise ingestion metadata, freshness, lineage, and connector
  sync state.
- GitLab: SDLC governance across issues, merge requests, CI, security scans,
  approvals, and deployment evidence.

None of the planned partner lanes may be presented as live integrations until
the corresponding adapter has a trace, validation artifact, receipt, and
dashboard proof.

## Build Roadmap

Roadmap phases live in `orchestration/build_roadmap.json`.

### P0: Standalone Repo and Local Continuity Bridge

Status: complete.

Proof:

- dAimon exists as an independent repo.
- Local demo and local trace exist.
- Scaffold validation passes.

### P1: MongoDB Atlas Candidate State and Visibility Proof

Status: complete for seed proof.

Proof:

- Atlas ping succeeds with local credentials.
- Candidate objects, queue items, receipts, and sessions can be seeded.
- MongoDB-backed trace returns accepted-only objects with excluded witness.

### P2: Orchestration Contract Layer

Status: active.

Proof target:

- All orchestration registries exist and validate.
- The repo can explain its own governance structure.
- The plan is executable phase by phase.

### P3: Dashboard and Review Surface

Status: planned.

Proof target:

- A user can inspect queue, receipts, trace, and inheritance bundle.
- UI distinguishes trusted inherited context from excluded witness.

### P4: Google Cloud Runtime

Status: planned.

Proof target:

- The vertical slice runs on Google infrastructure.
- Health and trace endpoints respond.
- Deployment facts are receipted.

### P5: Gemini or Agent Builder Governed Handoff

Status: planned.

Proof target:

- Gemini-era carrier receives only receipt-cleared context.
- Carrier output returns as candidate transition.
- Settlement decides what may inherit.

### P6: Self-Demonstrating Contest Package

Status: planned.

Proof target:

- The demo video and submission package are governed outputs.
- Every claim is proven, local-only, live, roadmap, or non-claim.

## Testing Strategy

Testing groups live in `orchestration/test_matrix.json`.

Required local gates:

```bash
python scripts/validate_orchestration_plan.py
python scripts/validate_scaffold.py
python scripts/validate_mcp_trace_harness.py
python scripts/validate_mongodb_contract.py
python -m py_compile ion_kernel/*.py scripts/*.py
```

Live MongoDB gate:

```bash
python scripts/check_mongodb_live_readiness.py
python scripts/seed_mongodb_candidate_sample.py
python scripts/validate_mongodb_contract.py
```

Google Cloud gate:

```bash
gcloud run services describe <service>
curl -fsS <service-url>/health
curl -fsS <service-url>/trace
```

Gemini or Agent Builder gate:

```text
Send receipt-cleared context to carrier.
Capture carrier return as candidate output.
Settle return.
Issue receipt.
```

Demo claim gate:

```text
Inventory claims.
Map claims to artifacts.
Mark local-only, live, roadmap, or non-claim.
Remove unsupported claims.
```

## Management Cadence

Management cadence lives in `orchestration/management_cadence.json`.

Session start:

- Read the README, this plan, and active roadmap phase.
- Check git status.
- Identify the active domain route.
- Name the proof target before editing.

Daily build loop:

- Pick the highest-value blocker.
- Build the smallest proof-producing increment.
- Run the matching validation group.
- Update docs or sample outputs when behavior changes.
- Commit with proof-oriented message.

Settlement review:

- Identify candidate outputs.
- Check template proof obligations.
- Decide settlement status.
- Issue receipt.
- Update inheritance only from accepted receipt-backed objects.

Release candidate:

- Run local validation.
- Run live integration validation for every live claim.
- Run demo claim audit.
- Record known gaps and non-claims.

## Google Infrastructure Plan

The Google path should be built in two layers.

First, deploy a small dAimon runtime to Google Cloud Run or an equivalent Google-hosted surface. It should expose:

- `/health`
- `/trace`
- `/bundle`
- `/receipts/<id>` if time permits

Second, add Gemini or Agent Builder handoff:

- Build accepted-only inheritance payload.
- Send payload to carrier with objective and return schema.
- Store carrier return as candidate output.
- Settle carrier return.
- Issue receipt.

The claim boundary matters. A Cloud Run health check proves hosting. It does not prove full Agent Builder integration. A Gemini handoff proves carrier exchange. It does not prove autonomous governance or output correctness.

## MongoDB Plan

MongoDB is the contest persistence and visibility surface.

Initial collections:

- `<prefix>continuity_objects`
- `<prefix>settlement_queue`
- `<prefix>receipts`
- `<prefix>sessions`

Near-term additions:

- `<prefix>domains`
- `<prefix>templates`
- `<prefix>routes`
- `<prefix>validation_runs`
- `<prefix>claim_audits`

MongoDB trace behavior must show:

- Objects considered.
- Objects returned.
- Objects excluded.
- Receipt citations.
- Whether accepted state changed.
- Whether external mutation occurred.

Only receipt-cleared objects should be inheritable.

## Dashboard Plan

The dashboard should be a dense operational surface, not a landing page.

Primary views:

- Queue: candidate objects and required settlement action.
- Receipts: accepted, rejected, deferred, caveated decisions.
- Trace: considered, returned, excluded, and cited objects.
- Bundle: next-session context package.
- Roadmap: phase status and validation gates.
- Claims: demo claims and proof status.

Important UI rule:

```text
The first screen should show the governed work surface, not marketing copy.
```

## Release and GitHub Plan

Repo posture:

- Keep dAimon independent from ION.
- Keep raw credentials out of commits.
- Use GitHub Secrets for CI and live workflows.
- Keep workflow template in docs until the token has workflow scope.

Release candidate checklist:

- `git status --short` inspected.
- Local validation passed.
- Orchestration validation passed.
- Live integration proof refreshed for any live claim.
- Secret pattern scan performed.
- README and docs reflect current proof boundary.
- Demo claim audit completed.

## Backlog

Highest-value next build items:

1. Minimal dashboard/API surface over existing local and MongoDB artifacts.
2. Google Cloud Run runtime path.
3. Accepted-only Gemini or Agent Builder handoff.
4. Receipt graph query endpoint.
5. Demo claim audit artifact generator.
6. Domain cartography from objective to work packets.
7. Domain fission recommendation logic.

## Custom GPT Expansion

The ION custom GPT expansion plan adds the product modules that connect this
repository back to the broader ION operating substrate and forward to a public
custom GPT/local PC workflow.

Canonical expansion doc:

- `docs/custom_gpt_expansion_plan.md`

New governed domains:

- `ion_product_boundary`
- `technology_fabric`
- `portable_continuation`
- `voice_local_work`
- `security_red_team`
- `project_identity_collaboration`

New proof themes:

- dAimon is the productized trust surface; ION is the deep law and engine.
- Adapters normalize many technologies into object, capability, authority, proof, receipt, and inheritance rules.
- Work should survive the carrier through portable continuation.
- Voice is an intent source, not authority; high-risk voice-derived actions need confirmation.
- Security and red-team tests belong in containment lanes with synthetic secrets and receipts.
- Project identity starts with a first contact package; collaboration is scoped by capability tokens.

## Final Demo Narrative

Opening:

```text
AI agents are getting powerful, but they still have a trust problem.
They generate useful work, but future agents often inherit that work without knowing what was proven, what was rejected, or what was merely suggested.
dAimon fixes that.
```

Demo sequence:

1. Messy work enters.
2. dAimon classifies candidate objects.
3. Settlement decides what is inheritable.
4. Receipts are generated.
5. MCP visibility trace returns only accepted objects.
6. Excluded objects remain visible as witness.
7. Gemini-era next session receives receipt-cleared continuity.
8. The demo package itself is shown as governed output.

Closing:

```text
The model generates. dAimon decides what future models may trust.
```
