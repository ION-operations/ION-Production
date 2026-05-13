# ION Custom GPT Sandbox Carrier Package

This package lane prepares the Custom GPT knowledge bundle used when ChatGPT is acting as an ION sandbox carrier.

It is not the GPT Builder Action schema release lane. Action schema releases are governed separately by the Custom GPT Action Release domain.

## Canonical posture

- The Custom GPT is a sandbox carrier, not total ION.
- Uploaded or extracted ION repo files are evidence and context, not accepted state by themselves.
- Every boot should emit human-readable prose and machine-readable boot blocks.
- Actions are optional live tools and must be treated as degraded until the canonical full Action Gateway schema and bearer auth are proven in a fresh GPT session.
- Supabase remains an operational mirror, not source truth.

## Important paths

- Main instructions: `instructions/ION_CUSTOM_GPT_MAIN_INSTRUCTIONS_8000.md`
- Boot sequence: `instructions/ION_CUSTOM_GPT_BOOT_SEQUENCE.md`
- Machine blocks: `instructions/ION_CUSTOM_GPT_OUTPUT_MACHINE_BLOCKS.md`
- Action posture: `actions/ACTION_SURFACE_POSTURE.md`
- Knowledge index: `indexes/ION_CUSTOM_GPT_KNOWLEDGE_INDEX.yaml`
- Route index: `indexes/ION_CUSTOM_GPT_ROUTE_INDEX.yaml`
- Agent/domain index: `indexes/ION_CUSTOM_GPT_AGENT_DOMAIN_INDEX.yaml`
- Builder: `ION_Developement/ION/04_packages/kernel/ion_custom_gpt_sandbox_package.py`

## Build

From the workspace root:

```bash
PYTHONPATH=ION_Developement/ION/04_packages python3 -m kernel.ion_custom_gpt_sandbox_package --workspace-root . --json
```

The zip output is written under `ION_EXPORTS_LOCAL/`, which is intentionally ignored by git.

## Internal package structure

The carrier is not driven by instructions alone. It mounts:

- `context/ION_CUSTOM_GPT_SANDBOX_CARRIER_CONTEXT_PACKAGE.yaml`
- `routes/BOOT_TO_PERSONA_ROUTE.yaml`
- `workflows/ION_CUSTOM_GPT_INTERNAL_WORKFLOW.md`
- `templates/ION_CUSTOM_GPT_BOOT_PERSONA_RESPONSE.template.md`

These files make boot route into persona response naturally without dumping internal role machinery into chat.
