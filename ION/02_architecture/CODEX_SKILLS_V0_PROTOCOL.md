# Codex Skills v0 Protocol

Status: candidate
Date: 2026-05-15
Packet: PCKT-ION-CODEX-SKILLS-V0

## Purpose

Codex skills are the ergonomic layer over ION carrier surfaces. They teach a
Codex carrier when and how to use ION context, templates, branch capsules,
memory recall, workbench tools, hooks, receipts, and next-packet routing.

Skills do not create a parallel operating system. They map Codex-native behavior
back into normal ION operations.

## Governing Law

```text
CARRIER_FEATURES_MUST_MAP_TO_ION_OPS
```

Every Codex skill must serve at least one ION operation:

- context_load
- situation_route
- bounded_execution
- receipt_preservation
- domain_capsule_update
- drift_repair
- next_packet_compile

If a skill does none of these, it is carrier noise.

## Skill Set v0

ion-orchestration:
  Maps operator intent to ION route, package, template, receipt, and next packet.

ion-context-scout:
  Finds branch context, parent inheritance, lazy materialization posture,
  receipts, and route-deeper evidence before work starts.

ion-memory-curator:
  Treats Codex native memory as carrier recall. Writes through ad-hoc
  contribution lanes, observes generated memory, and reconciles against ION
  truth.

ion-workbench:
  Uses Project Workbench context/file-slice/patch-preview surfaces for bounded
  repo work, preview/rollback posture, and receipt-backed diagnostics.

ion-hook-engineer:
  Designs and audits Codex hook wiring through the shared carrier-sync adapter.
  Keeps hooks quiet/fail-soft unless a real blocker is hit.

## Authority Rule

Skills may never grant:

- accepted state
- production authority
- live execution authority
- secrets authority
- git push authority
- destructive authority
- authority outside the active ION root
- permission to edit generated Codex memory before contribution lanes are tried

Templates, validation, receipts, and operator/settlement gates remain the proof
contracts.

## Skill Flow

```text
operator intent
-> skill selection
-> active root proof
-> context mount
-> branch/memory/workbench/hook route
-> template gate
-> bounded work or response
-> validation/proof
-> receipt
-> next packet
```

## Relationship To Recent Candidate Pillars

C-117 Codex Carrier Sync Layer:
  Hook events and carrier features route into ION operations. Skills explain
  when to use those routes.

C-118 Lazy Branch Context Materialization:
  Folder context appears where work happens. `ion-context-scout` is the front
  door for inspecting and proposing that context.

C-119 Codex Memory Curator:
  Memory is managed recall, not authority. `ion-memory-curator` is the front
  door for contribution and verification.

C-120 Branch Leader Lazy Context Integration:
  Action/MCP branch leaders can describe paths and safe routes. Skills tell the
  carrier which branch leader surface is relevant.

## Installation Posture

This packet stages repo-local skill drafts under:

```text
ION/05_context/current/codex_skills_v0/skills/
```

The globally installed Codex skills under `/home/sev/.codex/skills/` are not
modified by this packet.

## Acceptance Posture

Candidate only. No production authority, no live execution authority, no secrets
authority, no push, and no accepted-state claim.
