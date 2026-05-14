---
name: ion-branch-delegate
description: Resolve ION folder/file references into branch delegation requests, context compiles, or bounded specialist calls with receipts.
---

# ION Branch Delegate Skill

Use this skill when the task mentions another folder, branch, file, package, context capsule, agent, template, queue, browser extension, kernel module, or registry area that may need specialist context.

## Inputs

- Operator objective.
- Current working directory.
- Referenced repo paths or inferred branch targets.
- Available surfaces: local context, Codex subagent, MCP, ION agent queue, browser queue.

## Procedure

1. Extract branch/file references.
2. Resolve each path under the repo root.
3. Locate the nearest branch node by looking for:
   - `README.md`
   - `AGENTS.md`
   - `ION_CONTEXT_CAPSULE.yaml`
   - `BRANCH_CHILD_INDEX.yaml`
4. Read local and parent branch guidance before broad search.
5. Emit or use `ion.branch_delegation_request.v0_1`.
6. If a real delegate call is available, pass the target branch, objective, context refs, and authority boundary.
7. Require the delegate to return `ion.branch_delegate_return.v0_1`.
8. If no real call is available, say so and return a blocked/candidate receipt fragment.

## Output

Return a compact receipt-bearing summary. Never state that a delegate was invoked unless there is proof.
