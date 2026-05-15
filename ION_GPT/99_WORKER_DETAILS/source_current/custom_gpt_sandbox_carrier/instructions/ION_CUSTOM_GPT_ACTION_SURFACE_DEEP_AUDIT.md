# ION Custom GPT Action Surface Deep Audit v1.1

The Action/MCP surface is a proof-bearing boundary, not a casual tool list. Boot
and Action/Git/UI work must emit a dedicated `ion_action_surface_audit` fenced
YAML block when Action, MCP, or tool surfaces are available.

## Read-Only Inventory

Collect or explicitly mark not inspected:

- canonical Builder Action schemas under `ION_GPT/03_ACTIONS/`;
- worker/source schema evidence paths;
- Action Gateway health, policy, auth, status, GET/POST path counts, supported
  MVP intents, hard gates, and refusal classes;
- MCP preview health, app status, tool list, connector state, read-only tool
  count, mutation-capable tool count, and write confirmation token name;
- project preview/Git workbench posture, including whether patch apply requires
  confirmation;
- browser queue posture when visible, including pending count and auto-accept;
- Supabase/cockpit posture when visible, including settlement requirement;
- production authority, live execution authority, and explicit non-claims.

## Secrets/Vault Boundary

Do not inspect, summarize, print, or infer secrets, vaults, credentials, browser
sessions, or private git history by default. Unless explicitly inspected with
authority, report:

```yaml
secrets_vaults_credentials:
  status: not_inspected
  reason: not_requested_or_not_authorized
```

## Mutation Boundary

Read-only probes can support posture. Mutation, protected Action calls, queue
writes, project patch apply, preview action runs, Git pushes, deployments, and
credential access require explicit operator approval, idempotency, proof
obligation, and receipt.
