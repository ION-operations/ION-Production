# ION Production Workspace

**ION Production** is the governed workspace for ION, dAimon, WisdomNET, ATLAS, AIM-OS lineage, browser-carrier tooling, Custom GPT Actions, MCP surfaces, and local operating infrastructure.

This repository is not just an app repo. It is the source-truth workspace for a local-first AI operating system project.

```text
AI output is not accepted state.
A useful answer is not accepted state.
A patch is not accepted state.
State changes require context, authority, proof, validation, receipt, and settlement.
```

## Current source-truth root

```text
/home/sev/ION - Production
```

This root is now the main monorepo and GitHub source-truth surface.

Canonical remote:

```text
https://github.com/ION-operations/ION-Production
```

Do not use `/home/sev` as the project Git root.

## What this workspace contains

| Path | Role |
|---|---|
| `ION_Developement/` | Active ION kernel, protocols, context, tests, Supabase migrations, cockpit surfaces, and setup docs. |
| `ION_GPT/` | Custom GPT packages and canonical Action Gateway OpenAPI schema. |
| `browser_extension/` | Browser carrier extension for ChatGPT/ION UI, queue, docs/packages, and page automation surfaces. |
| `mcp/` | MCP preview/action/connector surfaces for ChatGPT browser integration. |
| `local_daemon/` | Local daemon bridge surfaces. |
| `systemd/` | User-service templates for local ION services. |
| `product_packager/` | Packaging/export tooling. |
| `Cursor/` | Cursor extension and SDK surfaces. |
| `dAimon/` | dAimon agent/application project for governed inheritance, Gemini-era agents, and continuity bridge experiments. |
| `AIM-OS/` | AIM-OS lineage and adjacent architecture corpus. |
| `ATLAS/` | Systems ATLAS reference library for external systems, platforms, and lineage comparison. |
| `wisdomNET/` | WisdomNET workspace family for memory/context/intelligence evolution. |
| `Needs_Routed/` | Operator staging lane for incoming diffs, workpackets, bundles, and material needing routing. |
| `quarentine/` | Archive witness lane. Not active source by default. |
| `ION_VAULT_LOCAL/` | Local-only ignored vault for secrets and credential notes. |

The workspace manifest is:

```text
ION_WORKSPACE_MANIFEST.yaml
```

Agent entrypoint:

```text
START_HERE_FOR_ANY_AGENT.md
```

## Core projects

### ION

ION is the continuity substrate and governance law for AI work. It defines how AI outputs become candidate state transitions, how work packets are bounded, how context is mounted, how authority is declared, how proof is returned, and how state is settled.

Start here:

```text
ION_Developement/README.md
ION_Developement/ION/REPO_AUTHORITY.md
ION_Developement/ION/01_doctrine/
ION_Developement/ION/02_architecture/
ION_Developement/ION/04_packages/kernel/
ION_Developement/ION/05_context/current/
```

### dAimon

dAimon is the governed inheritance agent/application lane. It applies ION continuity principles to Gemini-era agents, Google/Cloud surfaces, MongoDB/Atlas traces, capability routing, inheritance bundles, and trust/settlement proofs.

Start here:

```text
dAimon/README.md
dAimon/orchestration/
dAimon/docs/
dAimon/ion_kernel/
```

### WisdomNET

WisdomNET is the memory/context/intelligence lineage for durable knowledge, retrieval, and continuity evolution. In this workspace it should become a first-class project family with its own README, manifest, indexes, and ION integration map.

Current status:

```text
workspace_family_candidate
```

Next expected docs:

```text
wisdomNET/README.md
wisdomNET/WISDOMNET_MANIFEST.yaml
wisdomNET/docs/
```

### ATLAS

ATLAS is the Systems ATLAS reference library. It provides evidence-grounded comparative packages for external systems, platforms, protocols, and operating-system lineages that ION can learn from without copying wholesale.

Start here:

```text
ATLAS/README.md
ATLAS/_meta/
ATLAS/systems/
ATLAS/comparative/
```

### AIM-OS

AIM-OS is an adjacent/lineage architecture corpus and prototype surface. It is preserved in the monorepo as a major reference and possible source of components, concepts, and lessons for ION, dAimon, WisdomNET, and JOC evolution.

Start here:

```text
AIM-OS/README.md
AIM-OS/.agent/
AIM-OS/Documentation/
```

## Operating surfaces

### Custom GPT Action Gateway

Canonical full schema:

```text
ION_GPT/custom_gpt_action_gateway/openapi.yaml
```

Release domain tooling:

```text
ION_Developement/ION/04_packages/kernel/ion_action_schema_release.py
ION_Developement/ION/02_architecture/ION_CUSTOM_GPT_ACTION_RELEASE_DOMAIN_PROTOCOL_V0_1.md
```

Hard rule:

```text
Do not install schema fragments into GPT Builder.
Install only the canonical full schema after release-domain validation.
```

### Supabase operating mirror

Supabase migrations, adapter, and docs live under:

```text
ION_Developement/supabase/
ION_Developement/ION/04_packages/kernel/ion_supabase_event_mirror.py
ION_Developement/ION/docs/setup/ION_SUPABASE_EVENT_MIRROR.md
```

Supabase is an operational mirror, not source truth.

### Browser extension

```text
browser_extension/ion_chatops_bridge/
```

This is the browser carrier surface for ChatGPT/ION panels, queues, docs/packages, DOM perception, and operator controls.

### MCP and local services

```text
mcp/
systemd/user/
local_daemon/
```

Known local port truth:

```text
8765 = ION MCP preview
8777 = ION Action Gateway
8788 = ION local cockpit
8795 = dAimon Gemini websocket bridge
```

## Local vault and secrets

Local-only vault:

```text
ION_VAULT_LOCAL/
```

This folder is ignored by Git. Do not commit it. Do not print secret values. Agents may report only whether required values are present or missing.

Tracked setup doc:

```text
ION_Developement/ION/docs/setup/ION_LOCAL_SECRET_VAULT.md
```

## Quarantine

```text
quarentine/
```

Quarantine is an archive witness lane, not active source. Raw contents are ignored by default. Only the README/index are tracked unless a specific artifact is promoted by a bounded packet.

## Validation quick commands

From the workspace root:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=ION_Developement/ION/04_packages \
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python3 -m pytest -q \
  ION_Developement/ION/tests/test_kernel_ion_workspace_paths.py \
  ION_Developement/ION/tests/test_kernel_ion_action_schema_release.py
```

Validate the canonical Custom GPT Action schema:

```bash
PYTHONPATH=ION_Developement/ION/04_packages \
python3 -m kernel.ion_action_schema_release validate \
  --ion-root ION_Developement \
  --json
```

Expected schema posture:

```text
operation_count: 25
schema_sha256: 9ee5e43885e85607ae51a0efccd72d780ba57635074bc6b01a2f81dff8ae72ba
```

## Development rules

- Do not treat AI output as accepted state.
- Do not push without operator approval.
- Do not touch GPT Builder without a validated Action release package.
- Do not print or commit secrets.
- Do not delete quarantine evidence without explicit approval.
- Do not restart services unless requested.
- Do not run broad queue workers casually.
- Keep source, candidate evidence, runtime evidence, and accepted state distinct.

## Current status

The workspace was converted into a monorepo on 2026-05-13.

The first monorepo commits established:

```text
workspace shell
active ION development tree
promoted integration roots
dAimon source
knowledge/application corpora
quarantine index
post-migration action schema path hardening
```

The root repo is now the source-truth container for the ION Production workspace.
