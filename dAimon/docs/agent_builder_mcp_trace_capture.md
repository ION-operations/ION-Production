# Agent Builder / MongoDB MCP Trace Capture

This is the remaining live proof gate after the current MongoDB + Gemini API
vertical slice.

## Required Proof

Attach a trace export or screenshot-transcribed JSON at:

```text
sample_outputs/agent_builder_mcp_trace.json
```

The trace must show:

- Agent Builder or Gemini agent execution.
- A `find_continuity_objects` tool call or MongoDB MCP tool call.
- MongoDB MCP tool usage such as aggregate, find, or vector search.
- A read-only retrieval filter containing `INHERITABLE_AFTER_RECEIPT`.
- An accepted-state gate such as `settled_accept_sample`, `ACCEPTED`, or `RECEIPT_CLEARED`.
- Returned object IDs matching the live inheritance bundle.
- Receipt IDs or proof hashes cited with returned objects.

## Validation

```bash
python scripts/deploy_cloud_run.py --confirm-deploy --allow-unauthenticated
python scripts/check_cloud_run_live.py --url "$ION_CLOUD_RUN_URL"
python scripts/validate_agent_builder_mcp_trace.py
python scripts/validate_agent_builder_mcp_trace.py --require-live-trace
python scripts/generate_demo_evidence_package.py
```

Without a live trace artifact, the validator stays honest and reports:

```text
local_harness_or_pending_live_trace
```

With a valid live trace artifact, the claim upgrades to:

```text
proven_live_agent_builder_mcp
```

## Boundary

The existing live vertical slice proves MongoDB-backed candidate records,
accepted-only retrieval, and Gemini API handoff. It does not claim complete
Agent Builder deployment until this trace is attached and validated.

## Cloud Run Tool Surface

The deploy target exposes two live read-only proof endpoints:

- `POST /query-governed-state-live` with operationId `find_continuity_objects`
- `GET /live-vertical-slice-evidence/{session_id}`

`find_continuity_objects` is the Agent Builder-facing tool name. Its response
must keep the accepted-only filter visible:

```json
{
  "inheritance_status": "INHERITABLE_AFTER_RECEIPT",
  "acceptance_status_allowlist": [
    "settled_accept_sample",
    "ACCEPTED",
    "RECEIPT_CLEARED",
    "receipt_cleared"
  ]
}
```

`MONGODB_URI` should be mounted into Cloud Run through Secret Manager. Do not
paste the URI into the OpenAPI contract, dashboard artifacts, or trace JSON.
