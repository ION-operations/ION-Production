# Agent Comms Protocol - Filesystem First

Purpose: keep agent coordination available even when MCP transport is down.

Source of truth: files under `.agent/comms/`.
MCP is an accelerator, not a dependency.

## Canonical Identity Routing

Use canonical sender IDs in message content and MCP payloads.
Use route keys for filesystem inbox/status paths.

| Canonical ID | Route Key |
| --- | --- |
| Agent Aether | aether |
| Codex Agent | codex |
| Claude Opus 4.6 | antigravity |
| Sev | sev |
| Composer | composer |
| Gemini | gemini |
| CodexGit | codexgit |

Aliases must be normalized before writing:
- `Aether` -> `Agent Aether`
- `Codex` -> `Codex Agent`
- `Opus`, `Opus1`, `Antigravity` -> `Claude Opus 4.6`
- `Sev`, `GPT-5.4`, `GPT-5.2` -> `Sev`

## Directory Layout

```
.agent/comms/
|-- COMMS_PROTOCOL.md
|-- templates/
|   |-- handoff.template.md
|   |-- status.template.md
|   `-- broadcast.template.md
|-- inbox/
|   |-- antigravity/
|   |-- sev/
|   |-- codex/
|   |-- aether/
|   |-- gemini/
|   `-- composer/
|-- broadcasts/
|-- handoffs/
`-- status/
    |-- antigravity.status.md
    |-- sev.status.md
    |-- codex.status.md
    |-- aether.status.md
    |-- gemini.status.md
    `-- composer.status.md
```

## Required Startup Flow (Every Session)

1. Load genome from `.agent/genomes/<route_key>.genome.md`.
2. Read direct inbox `.agent/comms/inbox/<route_key>/`.
3. Read `.agent/comms/broadcasts/`.
4. Read `.agent/comms/handoffs/`.
5. Read `.agent/comms/status/`.
6. Write your own status file in `.agent/comms/status/`.

## Naming Rules

- Direct message:
  - `YYYY-MM-DD_<from_route>_to_<to_route>_<subject>.md`
- Broadcast:
  - `YYYY-MM-DD_<from_route>_<subject>.md`
- Handoff:
  - `YYYY-MM-DD_<from_route>_to_<to_route>_<subject>.md`
- Status:
  - `<route_key>.status.md`

## Tooling

Canonical comms CLI:
- `python scripts/agent_comms/comms_cli.py --repo-root . resolve-identity --agent "Agent Aether"`
- `python scripts/agent_comms/comms_cli.py --repo-root . send --sender "Codex Agent" --recipient "Agent Aether" --subject "status" --content "update"`
- `python scripts/agent_comms/comms_cli.py --repo-root . list-inbox --agent "Codex Agent"`
- `python scripts/agent_comms/comms_cli.py --repo-root . update-status --agent "Codex Agent" --state active --current-work "runtime checks" --last-completed "mcp health verified" --available-for "integration"`

Session bootstrap helper:
- `python scripts/agent_comms/bootstrap_agent_session.py --repo-root . --agent "Codex Agent"`

Use `--strict-identity` in either script to reject unknown names.

## Identity Lock (Anti-Impersonation)

Optional but recommended in multi-session runs.
When enabled for an agent, message/status writes for that sender require matching `holder_id`.

Lock manager:
- `python scripts/agent_comms/identity_session_lock.py claim --agent "Codex Agent" --holder-id "codex_primary_20260304T1300"`
- `python scripts/agent_comms/identity_session_lock.py status`
- `python scripts/agent_comms/identity_session_lock.py release --agent "Codex Agent" --holder-id "codex_primary_20260304T1300"`

Comms CLI with lock:
- `python scripts/agent_comms/comms_cli.py --repo-root . --holder-id "codex_primary_20260304T1300" send --sender "Codex Agent" --recipient "Agent Aether" --subject "status" --content "update"`

Environment alternative:
- `set AIMOS_AGENT_HOLDER_ID=codex_primary_20260304T1300`

## Cleanup Rules

- Inbox messages: archive/delete after action.
- Broadcasts: keep 7 days then archive.
- Handoffs: keep until completion.
- Status files: overwrite in place, keep current state only.
