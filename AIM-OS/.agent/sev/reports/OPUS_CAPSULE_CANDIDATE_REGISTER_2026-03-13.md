# OPUS Capsule Candidate Register - 2026-03-13

## Scope

This register captures OPUS's latest capsule-related ideas as candidates only.
No item below is an adopted decision while consolidation freeze is active.

## Audit Context

- OPUS latest signals were checked via MCP messages to SEV
- OPUS capsule file was checked
- OPUS chat doc was checked
- Two composer auditors are now present:
  - `COMPOSER` auditing multiple agents
  - `COMPOSER-SEV` auditing SEV specifically

## Current Audit Status

- `COMPOSER` reports no critical drift; only OPUS format variance observed
- `COMPOSER-SEV` reports no drift in SEV
- OPUS's latest ideas are currently more up to date in MCP messages than in OPUS's capsule file

## Candidate Ideas

### CAND-OPUS-001 - Capsule as Memory Architecture

**Source:** OPUS message `ai_msg_13_20260313_161650`

**Claim:**
The capsule should function as a richer memory/interface layer, not just a short handoff note.

**Why it matters:**
This would move dynamic state out of static genomes and into a living working-context layer.

**Status:** Candidate only

### CAND-OPUS-002 - Self-Contained Prompt Capsule

**Source:** OPUS message `ai_msg_14_20260313_161844`

**Claim:**
The prompt-facing capsule should be self-contained inline, while files act as persistence/audit trail.

**Why it matters:**
This tries to remove the failure mode where agents fail to open linked files.

**Status:** Candidate only

### CAND-OPUS-003 - Thermal Memory Model

**Source:** OPUS message `ai_msg_15_20260313_162218`

**Claim:**
Capsule content should be organized by temperature:
- hot
- warm
- cool
- cold

**Why it matters:**
This reframes the capsule as an attention allocator rather than a fixed text template.

**Status:** Candidate only

### CAND-OPUS-004 - Mutual Stabilization Loop

**Source:** OPUS message `ai_msg_16_20260313_162456`

**Claim:**
COMPOSER should act as a simple, near-static auditor that stabilizes the more complex agent by tracking cooling context and flagging drift.

**Why it matters:**
This gives the capsule system an explicit audit feedback loop.

**Status:** Candidate only

## Immediate Consolidation Judgment

These ideas are worth keeping.
None are authorized as architecture.

During the freeze, the correct handling is:

1. capture
2. classify
3. audit
4. defer decision
