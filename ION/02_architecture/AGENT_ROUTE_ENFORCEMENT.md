# Agent Route Enforcement

Status: candidate local enforcement. No production authority, live execution
authority, or accepted-state claim.

## What Is Invoked

High-stakes Codex work enters through the existing queue owner:

```text
ion_request_codex_work_packet
-> ION/05_context/current/chatgpt_connector/codex_work_requests/
-> ion_codex_queue_runner.prepare_codex_queue_run
-> fixed Codex CLI carrier command
-> proof-gated task return intake
```

Agent broker work also compiles into the same Codex work-request shape. It is
not a separate hidden agent route.

## What Cannot Be Skipped

For these route classes, prose instructions are not enough:

```text
red_alert
action_native_mount
authority_security
gpt_builder
settlement
branch_gateway_mount_equivalence
operator_release_packaging
```

The request must include structured fields:

```yaml
work_class: red_alert
risk_level: red_alert
route_family: red_alert
idempotency_key: pckt-<stable-packet-id>
codex_model_override:
  selected_model: gpt-5.5
  selected_reasoning_effort: high
  reason: <why frontier routing is required>
requested_model: gpt-5.5
requested_reasoning_effort: high
model_override_reason: <same fallback reason>
```

`selected_reasoning_effort` may be `high` or `xhigh`. Any other high-stakes
model route is rejected before the worker run is prepared.

## Receipts

Every prepared run now carries:

```text
route_enforcement_receipt
codex_model_override_receipt
```

For high-stakes work, the route receipt marks
`model_override_receipt_required: true`. A high-stakes packet without the
structured model override is rejected instead of silently falling back to the
runner default.

## Operator Artifact Hygiene

`gpt_builder` and `operator_release_packaging` packets require the operator
artifact hygiene gate. The final operator output must be one clean surface:

```text
OPERATOR_FINAL/
```

or one final upload kit:

```text
ION_GPT_FINAL_OPERATOR_UPLOAD_KIT_<timestamp>/
```

Internal logs, hashes, task returns, fallback folders, and smoke material belong
outside the operator surface under reference-only material. The checker is:

```text
ION/04_packages/kernel/ion_operator_artifact_hygiene_check.py
```

## Boundary

This enforcement blocks bad route shape. It does not accept state, mutate GPT
Builder, push git, deploy, restart services, or grant secrets authority.
