# ION Content Root

This directory is the canonical ION content root for this repository.

Use the repository root for commands that depend on `pyproject.toml`. Use this
directory for code and document navigation.

## ION Branch Context Entry

This directory is now a candidate ION branch context node. Before substantive
work inside `ION/`, read:

1. `README.md`
2. `ION_CONTEXT_CAPSULE.yaml`
3. `REPO_AUTHORITY.md`
4. the relevant child branch README/capsule

The capsule is the local machine-readable operating contract. The README is the
human/generic-AI projection. Neither grants production authority, live execution
authority, or accepted state by itself.


## Authority

Read `ION/REPO_AUTHORITY.md` first. It defines the current root, shell-root
distinction, mount order, active carrier lanes, and what is canonical here.

Important starting points:

- `ION/REPO_AUTHORITY.md`
- `ION/02_architecture/ION_MOUNT_CONTRACT.md`
- `ION/docs/setup/ION_CURRENT_OPERATING_PACKET_V119.md`
- `ION/01_doctrine/CANONICAL_WORKFLOW.md`
- `ION/07_templates/README.md`

## Public Orientation Docs

For the public conceptual spine, start here:

- `ION/docs/ION_FUNDAMENTALS.md`
- `ION/docs/ION_CONTINUITY_SUBSTRATE_EXPLAINER.md`
- `ION/docs/ION_DOMAIN_GRAPH_AND_FISSION.md`
- `ION/docs/ION_PARALLEL_SETTLEMENT.md`
- `ION/docs/ION_PROJECT_INGESTION.md`

## Directory Map

```text
00_BOOTSTRAP      startup and historical bootstrap material
01_doctrine       doctrine floor and workflow law
02_architecture   protocols, carrier law, integration architecture
03_registry       profiles, policies, capabilities, tool registries
04_agents         role/carrier agent surfaces
04_packages       Python kernel implementation
05_context        current context, queues, receipts, runtime evidence
06_intelligence   reports, audits, research, orchestration evidence
07_templates      packet, proof, receipt, carrier, and action templates
08_ui             cockpit and UI surfaces
09_integrations   MCP, browser extension, local daemon, Cursor integrations
docs              setup guides, consolidation reports, public guides
examples          examples and smoke inputs
tests             pytest suite
```

## Carrier And Integration Entry Points

- Public docs index:
  `ION/docs/README.md`
- Domain graph and fission:
  `ION/docs/ION_DOMAIN_GRAPH_AND_FISSION.md`
- Project ingestion:
  `ION/docs/ION_PROJECT_INGESTION.md`
- Parallel settlement:
  `ION/docs/ION_PARALLEL_SETTLEMENT.md`
- Codex CLI carrier:
  `ION/docs/setup/CODEX_CLI_ION_DOGFOOD_SETUP_V125.md`
- ChatGPT Browser MCP connector:
  `ION/docs/setup/CHATGPT_BROWSER_MCP_CONNECTOR_SETUP_V120.md`
- ChatOps browser carrier runtime:
  `ION/09_integrations/browser_extension/ion_chatops_bridge/README.md`
- Local ChatOps daemon:
  `ION/09_integrations/local_daemon/ion_chatops_bridge/README.md`
- MCP integration:
  `ION/09_integrations/mcp/README.md`

## Common Commands

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ION/04_packages python3 -S -m kernel.ion_status --ion-root . --json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ION/04_packages PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest ION/tests -q
```
