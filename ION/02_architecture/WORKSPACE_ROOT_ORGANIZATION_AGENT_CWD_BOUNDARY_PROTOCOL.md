# Workspace Root Organization and Agent CWD Boundary Protocol

Status: candidate protocol

Authority: candidate architecture and local kernel projection only. This protocol does not grant production authority, live execution authority, accepted-state authority, Git push, deploy, deletion, service restart, export materialization, secret access, or vault content read.

## Purpose

ION agents are not safe merely because a terminal was opened from the correct folder. A carrier can start from the active ION root and still write into the wrong folder through stale paths, parent-relative paths, old root names, copied package scripts, or sibling project ambiguity.

Every AI movement that can write files must preserve three separate cwd facts:

- `control_plane_cwd`: where ION queue, receipts, reports, context packages, and runner state are prepared.
- `worker_launch_cwd`: where the worker process is launched.
- `target_command_cwd`: where project-local commands must run.

For active ION control work, all three normally resolve to `/home/sev/ION - Production/ION_Developement`.

For sibling or external project work, `control_plane_cwd` remains the active ION root, while `worker_launch_cwd` and `target_command_cwd` must resolve to the target project root, such as:

- `/home/sev/ION - Production/browser_extension/ion_chatops_bridge`
- `/home/sev/ION - Production/ION_GPT`
- `/home/sev/ION - Production/dAimon`
- `/home/sev/ION - Production/mcp`

Export movements are special: the worker launches from the active source root and writes only to the approved export root through the export gate.

## Root Organization Rule

The parent workspace `/home/sev/ION - Production` is the estate root, not the default project root. The active ION control root is `/home/sev/ION - Production/ION_Developement`. Sibling roots are governed project or projection roots. A worker must not create a new top-level sibling folder as a side effect of path confusion.

Canonical current roots are projected from `ION_WORKSPACE_MANIFEST.yaml` through `ion_workspace_root_registry.py`.

## Required Agent CWD Boundary

Each queued or invoked movement should carry:

```json
{
  "schema_id": "ion.agent_cwd_boundary.v1",
  "control_plane_cwd": "/home/sev/ION - Production/ION_Developement",
  "worker_launch_cwd": "<target project root or active root>",
  "target_command_cwd": "<target project root or active root>",
  "target_project_root": "<declared target project root>",
  "target_root_id": "<registry root id>",
  "target_root_class": "<registry root class>",
  "accepted": true
}
```

The boundary is not a substitute for path authority. It is the cwd layer that prevents a worker from using the active ION root as the accidental project terminal for browser extension, ION_GPT, dAimon, MCP, or other sibling movement.

## Blocking Conditions

The agent cwd boundary must block:

- missing `target_project_root`;
- target root under a blocked alias such as `quarantine` when canonical root is `quarentine`;
- unknown top-level workspace folders such as old `ION_CODEX` clones;
- forbidden external roots outside the governed workspace;
- missing target project root on disk;
- target content root outside target project root;
- sibling or external movement whose worker launch cwd points back to the active ION root;
- active ION movement whose worker launch cwd points outside the active ION root.

## Queue Runner Integration

The Codex queue runner remains a control-plane process rooted in the active ION checkout. It prepares run packets and receipts under:

```text
ION/05_context/current/chatgpt_connector/
```

Before a worker is allowed to start, the queue runner must project the agent cwd boundary into:

- the AI movement preflight root envelope;
- the worker spawn contract;
- the prompt;
- the run packet;
- the worker context awareness receipt.

For future live worker starts, the Codex subprocess must use `worker_launch_cwd` rather than blindly inheriting the active ION root.

## Operator Answer

When asked whether ION agents are called from their folder terminal, the accurate answer is:

```text
They must be called with a recorded cwd boundary, not just from an assumed terminal folder.
The control plane may start in the active ION root, but sibling project agents must carry and use the target project root as worker_launch_cwd and target_command_cwd.
```

## Validation Surface

Candidate validation should prove:

- active ION work launches from active root;
- browser extension movement launches from browser extension project root;
- ION_GPT movement launches from `ION_GPT`;
- dAimon movement launches from `dAimon`;
- export movement remains source-root launched with export-root artifacts;
- unknown parallel top-level roots are blocked;
- worker awareness receipts preserve cwd boundary fields.

## Recommended Next Packet

`WORKSPACE_ROOT_ORGANIZATION_AGENT_CWD_BOUNDARY_UI_AND_QUEUE_WARNING_PROJECTION`
