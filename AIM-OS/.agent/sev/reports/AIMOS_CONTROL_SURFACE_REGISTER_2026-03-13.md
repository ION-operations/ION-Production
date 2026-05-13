# AIM-OS Control Surface Register

Work package: `CONSOLIDATION_WORK_PACKAGE_04_2026-03-13`

This register records surfaces that currently claim authority over agent behavior, canon precedence, or continuity handling.

## Primary Control Surfaces

| Path | Declared role or owner | Target agent, habitat, or system | Surface mode | Current authority claim |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | Workspace identity router and universal rule layer | SEV, CODEX, COMPOSER host routing | static | Declares itself the canonical identity router for this workspace, sets chat-doc destinations, MCP-first rule, capsule pilot, and decision freeze. |
| `.agent/STARTUP.md` | Mandatory startup protocol | All agents | static | Claims no work may begin before identity, genome, doctrine, inbox, broadcasts, status, and announcement steps are completed. |
| `.agent/COMMS_DOCTRINE.md` | Braden / COMMAND via OPUS | All agent responses and chain of command | static | Declares mandatory callsign headers, message formats, rules of engagement, and session startup protocol. |
| `.agent/CONTEXT_CAPSULE_PROTOCOL.md` | Capsule pilot spec | All agents using capsules | static | Defines the capsule header, required fields, invariants, storage path, and freeze interaction. |
| `.agent/comms/COMMS_CANONICAL.md` | Canonical comms flow | Inbox, broadcasts, roundtable, MCP check/post flow | static | Claims to be the one canonical comms flow for where agents check and post. |
| `.agent/comms/COMMS_PROTOCOL.md` | Filesystem-first comms protocol | Filesystem routes, status files, identity routing, lock rules | static | Claims files under `.agent/comms/` are the source of truth and MCP is an accelerator rather than a dependency. |
| `docs/MCP_RUNBOOK.md` | MCP launch and transport runbook | Codex, Cursor, JOC, ChatGPT transport startup | static | Claims launch canon for HTTP fallback, stdio, SSE, health checks, and recovery commands. |
| `.agent/SEV_NORTH_STAR.md` | SEV | SEV in Codex desktop lane | static | Declares itself the canonical self-reference for SEV in the Codex desktop lane. |
| `.agent/OPUS_NORTH_STAR.md` | OPUS | OPUS operating lane | static | Declares itself OPUS's operational truth and says to read it first every session. |
| `.agent/genomes/codex/cursor_codex_instructions.md` | SEV / OPUS packetized Codex lane | CODEX in Cursor | static | Defines the CODEX role, mission, capsule rules, MCP-first requirement, and reporting chain for the Cursor host lane. |
| `.agent/genomes/composer/cursor_composer_instructions.md` | OPUS packetized Composer lane | COMPOSER in Cursor | static | Defines COMPOSER as a drift auditor with read-only audit scope and capsule-driven oversight. |
| `.agent/genomes/composer/sev_auditor_instructions.md` | OPUS packetized secondary Composer lane | COMPOSER-SEV second Cursor Composer instance | static | Defines COMPOSER-SEV as a dedicated SEV auditor with its own chat and capsule outputs. |
| `.agent/genomes/sev/codex_ide_instructions.md` | SEV lane instruction file | SEV in Codex IDE | static | Provides the SEV-specific Codex IDE control surface for the executive lane. |
| `.agent/genomes/antigravity.genome.md` | Antigravity / OPUS genome | OPUS in Antigravity IDE | static | Declares OPUS identity, MCP-first rule, chat-doc redirect, and operating correction vectors in the Antigravity lane. |

## Session-Bound Control Surfaces

| Path | Declared role or owner | Target agent, habitat, or system | Surface mode | Current authority claim |
| --- | --- | --- | --- | --- |
| `.agent/comms/capsules/{codex,sev,opus,composer,composer-sev}/2026-03-13.md` | Per-agent capsule writer | Current turn mission/now/must-not/next state | session-bound | Capsules are explicitly treated as control surfaces that should reveal drift when they conflict with chat or mission law. |
| `.agent/comms/status/*.status.md` | Per-agent status writer | Multi-agent overwrite prevention and current availability | session-bound | Status files are part of startup and coordination rules; other agents are told to check them before overwriting shared files. |
| `.agent/comms/chat/{codex,sev,opus,composer,composer-sev}/2026-03-13.md` | Per-agent response sink | Where substantive responses are written | session-bound | Multiple instruction surfaces route operational responses into dated chat docs instead of IDE chat. |
| `.agent/genomes/{codex,sev,opus}/context/current_priorities.md` plus `.agent/genomes/opus/context/open_questions.md` | Per-agent context state | Agent-local continuity state | dynamic | These files act as current-state continuity hints for some lanes, but not all lanes have an equivalent surface. |

## Adjacent Surfaces Not Counted As Primary Control

| Path | Why it is adjacent rather than primary control | Continuity or audit use |
| --- | --- | --- |
| `.agent/sev/reports/CONSOLIDATION_FINDINGS_BOARD_02_2026-03-13.md` | Descriptive synthesis rather than direct behavior control | Sets evidence priority and identifies control-layer ambiguity as the next audit target. |
| `.agent/comms/chat/*` historical entries | Durable trail of what agents said and did | Useful for continuity and audit, but older entries do not automatically outrank current instructions. |
| `.agent/sev/reports/*` generally | Evidence artifacts and audit outputs | These inform later review, but they are not themselves the startup or identity router. |

## Notes

- Control is currently distributed across root docs, `.agent` canon docs, per-lane genomes/instructions, and session-bound surfaces.
- The same actor can have more than one control surface family at once, especially SEV, OPUS, and CODEX.
