# dAimon — Governed Inheritance for Gemini-era Agents

Candidate contest implementation for the Google Cloud Rapid Agent Hackathon.


## Public name

**dAimon** is the hackathon-facing project name.  
**ION Continuity Bridge** remains the underlying protocol/scaffold name.

Judge-facing line:

```text
Gemini can generate useful work. dAimon decides what becomes trusted future context.
```

First principle:

```text
AI output is not state. AI output is a candidate transition.
```

## What this scaffold demonstrates

dAimon, built on ION Continuity Bridge, turns imported AI work into governed continuity objects:

```text
import witness material
→ classify continuity objects
→ build settlement queue
→ issue receipt candidate
→ resolve inheritance bundle
→ route new objectives through capability graph
→ retrieve only governed state for the next session
```

## Active stack target

```text
Gemini + Google Cloud Agent Builder
→ Cloud Run FastAPI ION kernel
→ MongoDB Atlas persistence
→ MongoDB MCP visibility trace
→ governed inheritance bundle
```

Local sample mode uses only files in this repository and does not call any external service.

## Orchestration layer

The build plan is now repo-owned instead of chat-owned. The active orchestration
contracts live in `orchestration/`:

- `product_layers.json`: continuity substrate, generative governance engine, enterprise trust layer, and contest slice
- `domain_registry.json`: governed domains, proof obligations, authority ceilings, settlement rules, and fission triggers
- `template_registry.json`: action law for import, classify, route, settle, receipt, inherit, trace, deploy, handoff, and demo audit
- `receipt_registry.json`: receipt fields, settlement decisions, and inheritance rules
- `build_roadmap.json`: phase-by-phase build plan from local proof to Google/Gemini/demo package
- `test_matrix.json`: local, live MongoDB, Google Cloud, Agent Builder, security, and demo validation gates
- `management_cadence.json`: session, daily build, settlement, integration, and release operating loops

Detailed planning docs:

- `docs/full_orchestration_plan.md`
- `docs/contest_vertical_slice_plan.md`
- `docs/self_demonstrating_video_agent.md`
- `docs/custom_gpt_expansion_plan.md`
- `docs/ui_canon_product_plan.md`
- `docs/partner_ecosystem_expansion.md`
- `docs/custom_gpt_action_connection.md`
- `docs/gitlab_connection_readiness.md`

UI planning now follows the local UI canon bundle at
`/home/sev/ION - Production/_ui_canon_bundle`. The dAimon product surface should
evolve from the current proof dashboard into a compact DXL trust console with
visual instruments for settlement, receipts, inheritance, MCP traces, routes,
claims, and domain cartography.

Validate the orchestration contracts:

```bash
python scripts/validate_orchestration_plan.py
python scripts/generate_connector_expansion_plan.py
```

## Partner adapter posture

MongoDB is the primary live proof substrate for the contest. Arize, Elastic,
Fivetran, and GitLab are modeled as partner adapter expansion lanes in
`orchestration/partner_adapter_registry.json`.

The product claim is not that every partner integration is live today. The claim
is that dAimon can treat enterprise systems as governed context surfaces and
control what future agents may inherit from them.

## New in v1.0

The scaffold adds a candidate `/route` endpoint and capability graph dashboard trace.

`/route` accepts an objective and returns:

- ION domain
- agent role
- capability path
- authority ceiling
- proof obligations
- trace steps
- non-claims
- candidate-state boundary

Routes do not call tools and do not mutate state.

## Run local demos

```bash
python scripts/run_local_demo.py
python scripts/run_mcp_trace_harness.py
python scripts/run_adapter_contract_demo.py
python scripts/run_route_demo.py
python scripts/validate_mcp_trace_harness.py
python scripts/validate_mongodb_contract.py
python scripts/validate_orchestration_plan.py
python scripts/validate_scaffold.py
```

Expected local boundary:

```json
{
  "accepted_state_changed": false,
  "external_mutation_attempted": false
}
```

## API endpoints

- `GET /health`
- `POST /import`
- `GET /settlement-queue/{session_id}`
- `POST /settle`
- `POST /receipt/{session_id}`
- `GET /inheritance/{session_id}`
- `POST /query-governed-state`
- `POST /query-governed-state-live`
- `GET /live-vertical-slice-evidence/{session_id}`
- `GET /capability-graph`
- `POST /route`
- `POST /mcp-visibility-trace`

## RAH-011A local MCP trace harness

`scripts/run_mcp_trace_harness.py` writes:

- `sample_outputs/mcp_visibility_trace.json`
- `sample_outputs/mcp_trace_dashboard_trace.json`

The trace includes the accepted-only MongoDB query shape, a read-only MCP
aggregate envelope, returned continuity object IDs, receipt/proof citations,
and an exclusion report for rejected, deferred, proof-debt, and witness-only
objects. It remains a local harness until a live Agent Builder/MongoDB MCP trace
is attached.

When credentials are ready, use `docs/credential_handoff.md` as the MongoDB and
Google Cloud handoff checklist.

Live MongoDB checks are separate from local validation:

```bash
python scripts/check_mongodb_live_readiness.py
python scripts/seed_mongodb_candidate_sample.py --confirm-candidate-write
python scripts/run_gemini_handoff_demo.py
python scripts/run_live_vertical_slice.py --confirm-live-run
python scripts/validate_agent_builder_mcp_trace.py
python scripts/generate_demo_evidence_package.py
```

The seed command writes candidate demo records to MongoDB Atlas. It does not
change accepted ION production state.

The live vertical slice command writes candidate demo records to MongoDB, reads
only receipt-cleared inherited objects back, sends that bounded bundle to
Gemini, and captures Gemini's answer as candidate output with its own receipt.
Gemini output is not automatically trusted.

Cloud Run and Agent Builder / MongoDB MCP are separate proof gates. Deploy the
read-only kernel endpoint and capture health/evidence first:

```bash
python scripts/deploy_cloud_run.py --confirm-deploy --allow-unauthenticated
python scripts/check_cloud_run_live.py --url "$ION_CLOUD_RUN_URL"
```

Then attach a live Agent Builder trace export at
`sample_outputs/agent_builder_mcp_trace.json`, then run:

```bash
python scripts/validate_agent_builder_mcp_trace.py --require-live-trace
python scripts/generate_demo_evidence_package.py
```

Named user / tester access is a separate readiness gate from runtime proof. To
verify whether specific Google accounts can invoke the shared surfaces, run:

```bash
python scripts/check_google_user_access_readiness.py --target-user user@example.com
```

This writes `sample_outputs/google_user_access_readiness.json` and does not
grant IAM or mutate cloud state.

## GitHub Actions

`docs/github_actions_validate_template.yml` contains the intended validation
workflow. Copy it to `.github/workflows/validate.yml` after the GitHub token
used for this repository has `workflow` scope.

## State boundary

Imported material starts as witness. Model output is candidate. Future work inherits only receipt-cleared continuity objects.

## Current non-claims

dAimon does not yet claim production readiness, legal compliance certification,
complete Google integration, complete production MongoDB MCP integration, fully
autonomous governance, or that human review is unnecessary. Live claims should be
made only after their matching validation gate in `orchestration/test_matrix.json`
has proof.
