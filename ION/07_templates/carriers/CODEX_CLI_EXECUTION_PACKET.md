# Codex CLI Execution Packet

## Carrier

- carrier_id: `CODEX_CLI_CARRIER`
- host_family: `codex_cli`
- starting_level: `L1_TOOL_ASSISTED`
- bounded_execution_level: `L2_BOUNDED_EXECUTION`
- production_authority: `false`
- live_execution_authority: `false`

## Shell Root Proof

- shell_root:
- `pyproject.toml` present:
- `ION/REPO_AUTHORITY.md` present:

## Active ION Packet

- active_work_packet:
- active_turn_packet:
- active_spawn_plan:
- chatgpt_connector_codex_work_request:
- operator_message:
- objective:

## Required Context Reads

- `ION/REPO_AUTHORITY.md`
- `ION/docs/setup/ION_CURRENT_OPERATING_PACKET_V119.md`
- `ION/02_architecture/CODEX_CLI_CARRIER_PROTOCOL.md`
- `ION/03_registry/codex_cli_carrier_profile.yaml`
- `ION/07_templates/carriers/CODEX_CLI_EXECUTION_PACKET.md`
- active packet/context package for the task
- files directly affected by the requested change

## Recommended Invocation Record

```text
codex_command:
prompt_path:
return_path:
event_log_path:
sandbox_mode:
approval_mode:
```

## High-Stakes Route Enforcement

When a Codex work packet is `red_alert`, `action_native_mount`,
`authority_security`, `gpt_builder`, `settlement`,
`branch_gateway_mount_equivalence`, or `operator_release_packaging`, the packet
must carry structured route fields before execution:

```yaml
work_class: red_alert
risk_level: red_alert
route_family: red_alert
idempotency_key: pckt-<stable-packet-id>
codex_model_override:
  selected_model: gpt-5.5
  selected_reasoning_effort: xhigh
  reason: <why frontier routing is required>
requested_model: gpt-5.5
requested_reasoning_effort: xhigh
model_override_reason: <same fallback reason>
```

The queue runner records a `route_enforcement_receipt` and rejects high-stakes
packets that rely only on prose model instructions.

## Required Return

```text
### CONTEXT PROOF
For every required context read, emit one block exactly like:

- path: ION/example/path.md
  sha256: <64 lowercase hex>
  line: L1
  excerpt: <short non-empty excerpt>

Rules:
- Use the literal labels `path:`, `sha256:`, `line:`, and `excerpt:` near every required path.
- Do not rely on table headers to provide `sha256`/`excerpt` labels.
- Do not use only `L1`; include `line:`.
- If the file is empty, use `eof: empty file` or `excerpt: <empty file>`.
- If a required read is impossible, report it under `### BLOCKERS`.
- Template structure and context proof are separate gates. A useful return with
  missing context evidence is preserved as candidate carrier evidence, but it is
  not accepted carrier intake or product state until the context proof gate
  passes.

### TEMPLATE ACTION PROOF
template_id: ion.template.patch_proposal.v1
action_id: codex_queue_runner_process_once
result: <implemented|designed|blocked>
touched_paths:
  - ION/...

For design-only/read-only work, `touched_paths` must still be non-empty. Use
the work request, run packet, context receipt, inspected source/status files, or
`no_touched_paths:` with an explicit reason if no repo path was touched.

### RESULT
<what changed>

### VALIDATION
- <tests/checks>

### WORKLOAD DIFF
- ION/...

### BLOCKERS
- none

### RECOMMENDED NEXT PACKET
<one packet>

### NON-CLAIMS
- No production authority claimed.
- No live execution authority claimed.
```

## Authority Boundaries

- State the mounted ION Codex carrier posture for the active root.
- STEWARD/RELAY/PERSONA authority requires role-phase proof.
- Do not run unbounded host mutation.
- Do not push to git or deploy without explicit human gate.
- Do not summarize unaccepted worker returns as current truth.
- Do not attach receipts to UI bubbles by recency.
