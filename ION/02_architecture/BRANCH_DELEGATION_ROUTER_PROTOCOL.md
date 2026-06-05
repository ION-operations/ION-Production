# ION Branch Delegation Router Protocol v0.1

## Purpose

The Branch Delegation Router Protocol turns a folder or file reference into an ION-routable specialist request.

The operator should be able to stand in the folder where the issue is present, launch Codex, and say something like:

```text
Ask the browser-extension branch and the kernel branch what context I need before changing this queue behavior.
```

or:

```text
Use ION/09_integrations/browser_extension and ION/04_packages/kernel as delegate branches for this patch plan.
```

The agent should not need a long prompt. The path references themselves are routing handles. ION resolves the paths to branch context nodes, mounts local and parent context capsules, selects the nearest specialist projection, and either invokes an allowed delegate surface or emits a blocked/candidate delegation request with a receipt fragment.

## Relationship to existing protocols

This protocol extends:

- `README_BRANCH_CONTEXT_PROTOCOL`: the folder is the context branch.
- `CODEX_BRANCH_SPECIALIST_PROTOCOL`: current directory activates the local Codex specialist.
- `CHAT_AS_RECEIPT_OUTPUT_CONTRACT`: every claimed delegation must expose evidence, non-actions, and missing proof.
- `ION_BROWSER_EXTENSION_TAG_CONTRACT`: branch/delegation tags drive UI chips, queue filters, and proof badges.

## Core law

```yaml
branch_delegation_router_law:
  folder_or_file_reference: routable_context_handle
  readme: natural_ai_entry_surface
  agents_md: codex_native_projection
  ion_context_capsule: machine_operating_contract
  delegate_call: not_claimed_without_tool_or_receipt_proof
  returned_summary: candidate_until_receipted_and_accepted
  tags: visibility_not_authority
```

## Delegation surfaces

ION should support several increasingly strong surfaces. The protocol chooses the strongest allowed surface with current proof.

```yaml
delegation_surfaces:
  local_context_compile:
    meaning: read target branch README, AGENTS, capsule, child index, receipts, and tests
    authority: read_only
    proof_required:
      - files_read
      - context_refs
  codex_subagent:
    meaning: spawn specialized Codex subagent scoped to target branch
    authority: read_only_by_default
    proof_required:
      - subagent_invocation_id_or_cli_transcript
      - branch_delegate_return
  codex_mcp:
    meaning: call Codex or other tools through MCP surface
    authority: per_mcp_tool_policy
    proof_required:
      - mcp_tool_call_receipt
      - returned_context_refs
  ion_agent_queue:
    meaning: enqueue bounded ION agent invocation packet
    authority: bounded_by_gateway_policy
    proof_required:
      - invocation_id
      - queue_receipt
      - settlement_or_blocker
  browser_queue:
    meaning: enqueue a typed prompt/work packet for browser-carrier execution
    authority: browser_carrier_policy
    proof_required:
      - queue_packet_id
      - browser_queue_receipt
  manual_receipt_packet:
    meaning: no live call available; emit candidate request and blocker
    authority: none
    proof_required:
      - missing_proof_list
```

## Routing algorithm

```yaml
branch_delegation_algorithm:
  - parse_operator_text_for_folder_file_or_branch_refs
  - resolve_paths_relative_to_repo_root_and_current_branch
  - reject_absolute_external_or_path_traversal_targets
  - locate_nearest_branch_context_node_for_each_target
  - mount_target_readme_agents_capsule_parent_chain_and_receipts
  - classify_delegate_intent:
      - route_only
      - ask_for_context
      - review_plan
      - patch_plan
      - run_tests
  - select_delegate_surface:
      prefer:
        - local_context_compile
        - codex_subagent_when_available_and_allowed
        - mcp_or_ion_agent_when_explicitly_allowed
      degrade_to: manual_receipt_packet
  - emit_branch_delegation_request
  - invoke_only_if_authority_and_surface_proof_exist
  - collect_branch_delegate_return
  - merge_returns_into_steward_summary
  - emit_ion_receipt_fragment_with_calls_and_missing_proof
```

## Minimal request shape

```yaml
ion_branch_delegation_request:
  schema_id: ion.branch_delegation_request.v0_1
  status: candidate
  objective: "<operator objective>"
  current_branch: "<cwd or branch node>"
  targets:
    - ref: ION/09_integrations/browser_extension
      kind: directory
      nearest_branch_node: ION/09_integrations/browser_extension
      context_files:
        - README.md
        - AGENTS.md
        - ION_CONTEXT_CAPSULE.yaml
  requested_delegate_mode: ask_for_context
  allowed_surfaces:
    - local_context_compile
    - codex_subagent
  authority:
    production_authority: false
    live_execution_authority: false
    write_authority: none
  proof_required:
    - files_read
    - delegate_return
    - receipt_fragment
```

## Return shape

```yaml
ion_branch_delegate_return:
  schema_id: ion.branch_delegate_return.v0_1
  branch: ION/09_integrations/browser_extension
  status: answered|blocked|deferred|failed
  context_refs:
    - README.md
    - AGENTS.md
    - ION_CONTEXT_CAPSULE.yaml
  summary: "<what this branch knows>"
  recommendations:
    - "<bounded recommendation>"
  blockers:
    - "<missing proof or needed file>"
  authority_boundary:
    production_authority: false
    live_execution_authority: false
  receipt_fragment:
    tool_calls: []
    did_not_do: []
    missing_proof: []
```

## Codex-specific behavior

When running in Codex CLI, the branch specialist should:

1. Treat referenced repo paths as possible branch delegates.
2. Resolve each target using the branch capsule mesh.
3. Prefer reading the target branch context before broad search.
4. Use Codex subagents only if the session supports subagent workflows and the operator/task allows it.
5. Use MCP tools only when configured, relevant, and authority-safe.
6. Emit a candidate delegation request instead of pretending a delegate was called.
7. Never claim a subagent, MCP, browser queue, or ION agent invocation without a receipt, invocation ID, transcript, or tool result.

## ION automation behavior

ION automation may implement this protocol through:

- `ion_context_compile` to assemble target branch context.
- `ion_agent_invoke` to ask a bounded specialist.
- `ion_agent_result` or settlement receipts to collect proof.
- `ion_queue_operator_message` or browser queue tools when the browser carrier is the correct surface.

A failed or unavailable automation is not an error in the protocol. It simply degrades the request to a candidate packet with `missing_proof`.

## Tags

```yaml
reserved_branch_delegation_tags:
  - route:branch-delegation
  - carrier:codex-cli
  - carrier:mcp
  - carrier:ion-agent
  - carrier:browser-queue
  - phase:delegate-request
  - phase:delegate-return
  - state:candidate
  - state:blocked
  - proof:context-compiled
  - proof:delegate-called
  - proof:missing
  - authority:read-only
  - authority:approval-required
  - authority:no-production
  - authority:no-live
```

Tags make routing and UI visible. They do not grant authority, accepted state, approval, or receipt status.

## Maturity levels

```yaml
branch_delegation_maturity:
  D0: folder_refs_are_plain_text
  D1: folder_refs_resolve_to_branch_context_nodes
  D2: branch_delegation_request_packets_exist
  D3: Codex can use branch subagents or skills with receipt returns
  D4: ION automations can compile context and enqueue bounded delegates
  D5: branch delegate returns are merged by Steward with proof
  D6: browser extension badges receipt/delegation YAML and queue packets
```

## Safety and proof boundaries

- A branch delegate can recommend, summarize, or block.
- A branch delegate cannot grant production/live authority.
- A tag cannot prove a call occurred.
- A generated request is not an invocation.
- A subagent summary is not accepted state.
- A return without cited context files must degrade.
- Cross-branch writes require explicit authority and normal patch receipts.
