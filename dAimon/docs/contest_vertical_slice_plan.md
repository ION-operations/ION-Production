# Contest Vertical Slice Plan

The contest slice must prove one complete behavior:

```text
Only receipt-cleared AI work becomes inheritable future context.
```

## Minimum Demo

1. Import messy AI work as witness.
2. Classify it into governed objects.
3. Route objects into settlement.
4. Accept some objects and reject or defer others.
5. Issue receipts.
6. Produce a visibility trace.
7. Export an inheritance bundle containing accepted objects only.
8. Show excluded witness and receipt citations.

## Minimum Screens

- Settlement queue.
- Receipt detail.
- Visibility trace.
- Inheritance bundle.
- Roadmap and non-claims.

## Minimum Commands

```bash
python scripts/run_local_demo.py
python scripts/run_mcp_trace_harness.py
python scripts/validate_mcp_trace_harness.py
python scripts/validate_orchestration_plan.py
python scripts/validate_scaffold.py
```

## Live MongoDB Claim

The live MongoDB claim requires:

```bash
python scripts/check_mongodb_live_readiness.py
python scripts/seed_mongodb_candidate_sample.py
python scripts/validate_mongodb_contract.py
```

Artifacts:

- `sample_outputs/mongodb_live_readiness.json`
- `sample_outputs/mongodb_candidate_seed_summary.json`
- `sample_outputs/mongodb_candidate_seed_mcp_trace.json`

Claim wording:

```text
dAimon demonstrates MongoDB-backed candidate state and accepted-only visibility trace behavior for the contest slice.
```

Do not claim:

```text
Complete production MongoDB MCP integration.
```

## Live Google Claim

The live Google claim requires:

- Google-hosted runtime.
- Health check proof.
- Trace endpoint proof.
- Deployment receipt.

Claim wording after proof:

```text
dAimon runs a contest vertical slice on Google infrastructure.
```

Do not claim:

```text
Production deployment hardening.
Complete enterprise Google integration.
```

## Gemini or Agent Builder Claim

The carrier handoff claim requires:

- Receipt-cleared context payload.
- Gemini or Agent Builder request.
- Carrier output captured as candidate.
- Settlement receipt.

Claim wording after proof:

```text
dAimon can hand receipt-cleared context to a Gemini-era carrier and settle the returned output before inheritance.
```

Do not claim:

```text
Carrier output is automatically trusted.
Fully autonomous governance is complete.
```

Live Gemini API proof command:

```bash
python scripts/run_gemini_handoff_demo.py
python scripts/run_live_vertical_slice.py --confirm-live-run
```

Artifacts:

- `sample_outputs/gemini_handoff_context_bundle.json`
- `sample_outputs/gemini_handoff_request.json`
- `sample_outputs/gemini_handoff_response.json`
- `sample_outputs/gemini_candidate_output.json`
- `sample_outputs/gemini_handoff_summary.json`
- `sample_outputs/live_vertical_slice_summary.json`
- `sample_outputs/live_vertical_slice_mcp_trace.json`

## Agent Builder / MongoDB MCP Claim

The live Agent Builder MCP claim is separate from the Gemini API handoff claim.
It requires:

```bash
python scripts/validate_agent_builder_mcp_trace.py --require-live-trace
```

with a captured trace at:

```text
sample_outputs/agent_builder_mcp_trace_raw.json
```

Until that artifact exists, claim wording must stay:

```text
dAimon has proven the live MongoDB + Gemini API vertical slice and has a bounded
Agent Builder / MongoDB MCP validation gate ready for trace attachment.
```
