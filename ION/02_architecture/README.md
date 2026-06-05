# ION Architecture

This directory contains protocols, contracts, boundary documents, carrier laws,
and architecture decision surfaces.

## Read First

- `README_BRANCH_CONTEXT_PROTOCOL.md`
- `ION_MOUNT_CONTRACT.md`
- `ION_GITHUB_DATA_PLANE_PROTOCOL.md`
- `ION_GITHUB_WORK_DAEMON_PROTOCOL.md`
- `ION_FULL_CARRIER_MCP_PARITY_PROTOCOL.md`
- `ION_BROWSER_CARRIER_RUNTIME_PROTOCOL.md`
- `ION_CHATOPS_YAML_ACTION_PROTOCOL.md`
- `CODEX_CLI_CARRIER_PROTOCOL.md`

## How To Use This Directory

- Treat protocols as owner surfaces, not loose notes.
- Prefer extending an existing protocol before creating a new authority lane.
- If a protocol is draft/proposed, keep language honest about non-production
  status and missing runtime proof.
- Pair implementation changes with registry, template, test, or receipt updates
  when those owners exist.

## Public Collaboration Boundary

Public architecture work may discuss design, tool surfaces, packet flow, and
tests. It must not publish secrets, private infrastructure, or production
credentials.


## Branch Context Note

`README_BRANCH_CONTEXT_PROTOCOL.md` is the candidate ION-wide law for making README files and `ION_CONTEXT_CAPSULE.yaml` files the natural branch-native context entrypoints for humans, generic AI, carriers, and agents.

## Receipts / History

Architecture claims remain candidate unless backed by the relevant protocol status, test output, settlement note, or receipt. Missing proof must degrade to blocker or candidate receipt fragment.
