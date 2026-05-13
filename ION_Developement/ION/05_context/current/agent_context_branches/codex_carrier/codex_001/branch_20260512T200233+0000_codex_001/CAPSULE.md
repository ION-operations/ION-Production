# Codex Carrier Branch Capsule

Status: candidate branch capsule; not accepted state by itself.

session_id: `codex_session_20260512T200233+0000_codex_001`
agent_tag: `codex_001`
branch_id: `branch_20260512T200233+0000_codex_001`
current_packet: `PCKT-ION-CODEX-LOCAL-PC-LIVE-CARRIER-MOUNT-002`
accepted_state_authority: false
production_authority: false
live_execution_authority: false

## Purpose

Bind one local Codex carrier session to a durable ION branch-capsule surface.

## Boundary

Codex session and memory may orient work. Branch capsule, proof, receipts, and settlement govern durable inheritance.

## Write Scope

- `ION/02_architecture/CODEX_CARRIER_DOMAIN_PROTOCOL.md`
- `ION/04_packages/kernel/ion_codex_carrier_domain.py`
- `ION/04_packages/kernel/ion_codex_local_pc_audit.py`
- `ION/04_packages/kernel/ion_codex_local_pc_readiness.py`
- `ION/04_packages/kernel/ion_codex_carrier_os.py`
- `ION/04_packages/kernel/ion_codex_raw_context_sync.py`
- `ION/05_context/current/codex_carrier`
- `ION/05_context/current/codex_local_pc`

## Required Settlement

Any material output from this branch remains proposal until proof gates and Steward/operator settlement accept it.
