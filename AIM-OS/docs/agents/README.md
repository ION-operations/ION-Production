# Agent Catalog

This folder contains operational specifications for dedicated AIM-OS agents.

## Available Agents

- `CodexGit` - Git branch hygiene, scoped commits, push/PR safety, and release-state reporting.

## Coordination Canon

- `docs/agents/ROLE_CONTINUITY_CANON.md` - canonical CEO/COO/agent identity + lock protocol.
- `docs/ROLE_CONTINUITY_STATE.md` - live continuity snapshot for session rehydration.
- `.agent/comms/COMMS_PROTOCOL.md` - filesystem-first communication + canonical route mapping.

## Paths

- `docs/agents/CodexGit/README.md`
- `docs/agents/CodexGit/OPERATING_RUNBOOK.md`
- `docs/agents/CodexGit/REQUEST_TEMPLATE.md`
- `docs/agents/ROLE_CONTINUITY_CANON.md`
- `docs/ROLE_CONTINUITY_STATE.md`
- `.agent/comms/COMMS_PROTOCOL.md`
- `scripts/agent_comms/identity_registry.py`
- `scripts/agent_comms/comms_cli.py`
- `scripts/agent_comms/bootstrap_agent_session.py`
- `scripts/agent_comms/identity_session_lock.py`
- `scripts/git/codexgit_status_report.py`
- `scripts/git/quintet_pre_commit_gate.py`
