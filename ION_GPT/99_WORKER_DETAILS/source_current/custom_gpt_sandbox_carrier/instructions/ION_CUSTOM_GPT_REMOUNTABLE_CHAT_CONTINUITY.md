# ION Custom GPT Remountable Chat Continuity v4.3

## Purpose

A new chat should resume the same workflow from explicit package state, not from
memory claims.

## Required restored state

- active_objective
- active_route
- current_phase
- completed/pending phases
- candidate domains
- candidate agents
- persona profile
- receipts/proof manifest
- authority boundaries
- blockers
- exact next sequence

## Missing proof

If any required object is absent, return `persona_gate_blocked` with missing
proof and next unblocker. Do not guess.
