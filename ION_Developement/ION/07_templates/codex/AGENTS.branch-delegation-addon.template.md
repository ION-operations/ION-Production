# ION Branch Delegation Add-on for AGENTS.md

Use this add-on in any branch that should be able to ask neighboring ION branches for context.

## Path references are delegation handles

When the operator mentions a repo folder or file, treat it as a possible branch delegate target.

Examples:

```text
Ask ION/09_integrations/browser_extension what queue constraints matter here.
Use ION/04_packages/kernel and ION/03_registry to review this action schema.
Route this issue between the template branch and the browser-extension branch.
```

## Required behavior

1. Resolve every target path under the repo root.
2. Reject path traversal or external absolute paths.
3. Read the target branch `README.md`, `AGENTS.md`, and `ION_CONTEXT_CAPSULE.yaml` before broad search.
4. Build an `ion.branch_delegation_request.v0_1` candidate object.
5. Invoke a delegate only if the current Codex session/tooling actually supports the surface and authority permits it.
6. Prefer read-only delegation unless the operator has approved a bounded write.
7. Merge delegate returns into the local answer through a receipt fragment.

## Allowed delegation surfaces

- Local context compile.
- Codex subagent when available.
- MCP tool call when configured and relevant.
- ION agent queue when available and explicitly allowed.
- Browser queue when the browser carrier is the target.
- Candidate request packet when no live call is available.

## Hard boundary

Do not claim that a subagent, MCP tool, browser queue, or ION agent was called unless there is proof: invocation ID, queue receipt, transcript, tool result, or returned `ion_branch_delegate_return`.

Tags, README text, and AGENTS.md guidance never grant accepted state, production authority, or live execution authority.
