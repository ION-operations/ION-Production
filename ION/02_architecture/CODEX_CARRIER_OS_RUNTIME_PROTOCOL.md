# Codex Carrier OS Runtime Protocol

Status: active candidate protocol
Authority: Codex carrier operating substrate projection only
Accepted-state authority: false
Production authority: false
Live execution authority: false

## Purpose

The Codex Carrier OS is the repo-local operating substrate that lets Codex CLI/App power ION work without becoming ION authority.

It composes:

```text
Codex carrier domain registry
Codex agents/domains
Codex sessions
branch capsules
raw-context diagnostic lane
runtime event ledger
cockpit source map
Git/stage/commit proposal law
MCP/Action Gateway projections
Google Drive/context mirror policy
```

## Core boundary

```text
Codex executes local work.
ION governs state transition.
Cockpit makes the operating surface legible.
Receipts and settlement decide inheritance.
```

Codex native sessions, memories, app surfaces, and tool output are valuable carrier continuity. They are not accepted ION state by themselves.

## Runtime loop

```text
operator_intent
-> work_packet
-> context_package
-> carrier_mount_receipt
-> codex_session_registration
-> branch_capsule_binding
-> local_codex_execution
-> raw_context_manifest_optional
-> proof_bearing_return
-> runtime_event_emission
-> cockpit_projection
-> proof_gate
-> settlement_request
-> Steward/operator decision
-> receipt
-> next_context_inheritance
```

## Control planes

The source map at:

```text
ION/05_context/current/codex_carrier/CODEX_CARRIER_OS_SOURCE_MAP.json
```

must project these planes:

```text
codex_carrier_domain
codex_sessions
codex_agents
raw_context_diagnostics
runtime_event_bus
cockpit_projection
context_mirror
slash_commands
```

Each plane is candidate/projection state unless accepted through ION gates.

## Native Codex bindings

Codex native capabilities bind to ION as follows:

| Codex capability | ION binding | Authority |
|---|---|---|
| sessions/resume | `CODEX_SESSION_REGISTRY` + branch capsule | orientation only until receipt |
| memories | memory policy + raw-context lane | diagnostic continuity only |
| `AGENTS.md` | carrier instructions + mount contract | role context, not state |
| `config.toml` | sanitized local-PC audit | configuration evidence only |
| hooks | mount/scope/proof guardrails | guardrail, not acceptance |
| slash commands | deterministic command registry | wrapper, not authority |
| subagents | child branch capsules | candidate subbranch only |
| MCP | read-only/dry-run transport | socket, not law |
| app-server / remote-control | service map + approval gate | unauthorized by default |
| Git review | stage/commit proposal evidence | proposal, not merge |

## Google Drive / context mirror law

Drive may carry a curated context mirror.

Drive must not become:

```text
active working tree
runtime source of truth
raw Codex context store
secret store
Git metadata substitute
accepted ION state authority
```

The policy lives at:

```text
ION/05_context/current/codex_carrier/CODEX_CONTEXT_MIRROR_POLICY.json
```

Any GPT/PRO mount from Drive needs freshness proof and a mount receipt.

## Slash-command law

Slash commands are deterministic wrappers. They may improve operator speed, but they do not bypass confirmation, proof, receipt, or settlement.

Default commands:

```text
/ion-mount
/ion-identity
/ion-packet
/ion-branch
/ion-sync
/ion-proof
/ion-git-plan
/ion-receipt
/ion-settlement
/ion-handoff
```

## Non-claims

This protocol does not grant:

```text
accepted-state authority
production authority
live execution authority
secrets authority
browser control authority
GitHub push authority
Drive runtime authority
```
