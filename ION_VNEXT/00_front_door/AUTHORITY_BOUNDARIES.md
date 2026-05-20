# Authority Boundaries

Status: M33 candidate authority guide

ION_VNEXT is a candidate rebuild surface. It is not accepted state by default
and does not replace the production root front door.

## Hard Rules

- No accepted-state claim without validation and receipt.
- No migration without source-pool audit.
- No movement without path-policy fit.
- No runtime/current-state JSON copy.
- No private, secret, credential, session, vault, or `.env` material.
- No source-pool bulk copy.
- No production deploy, service restart, GPT Builder change, Action mutation, or
  MCP mutation from this front-door packet.
- No legacy root-shim edits in M33.

## Evidence Classes

Legacy roots are evidence until promoted:

- `ION_Developement` is kernel/current-state source evidence.
- `ION_GPT` is Custom GPT product evidence.
- `dAimon` is product evidence.
- `browser_extension`, `mcp`, `Cursor`, `.github`, local daemon, and systemd
  surfaces are carrier evidence.
- `Needs_Routed` is work/inbox evidence.
- Archives and ZIP witnesses remain historical evidence until promoted.
- `ION_VAULT_LOCAL`, `.env*`, credentials, sessions, and private auth files are
  private material and must not be read, printed, packaged, or promoted.

## Receipt Rule

A useful document, test pass, model answer, or copied file is still candidate
material until the packet records what changed, why it was allowed, what proof
ran, and which receipt future workers inherit.

## Front-Door Limit

This front door orients work inside `ION_VNEXT`. It does not authorize changes
outside `ION_VNEXT`, and it does not modify root `README.md`, `AGENTS.md`,
`START_HERE_FOR_ANY_AGENT.md`, or `ION_WORKSPACE_MANIFEST.yaml`.
