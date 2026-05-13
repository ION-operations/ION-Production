# PALISADE Mission Packet - Doctrine Drift Map - 2026-03-06

**Status:** Active candidate mission packet  
**Mission owner:** Sev  
**Assigned specialist:** PALISADE  
**Recommended host:** Composer 1.5  
**Mission class:** Audit / canon drift mapping  
**Output location:** `.agent/sev/reports/PALISADE_DOCTRINE_DRIFT_MAP_2026-03-06.md`

---

## 1. Mission ID + Intent

**Mission ID:** `PALISADE-001-doctrine-drift-map`

**Mission objective:** Produce one evidence-backed doctrine drift map that compares local `.agent` truth, roundtable canon, context capsules, and active audit docs so Sev can decide the first canon cleanup queue.

---

## 2. Northstar Mapping

This advances the AIM-OS north star indirectly but critically by reducing truth drift in the operating system that humans and agents depend on to work coherently.

This packet supports:
- bounded truth instead of folklore
- faster agent onboarding and retrieval
- safer delegation and fewer duplicate decisions
- cleaner future canon promotion for local Sev doctrine

---

## 3. Read This First

1. `context/00_operational_definition.md`
2. `context/01_current_truth.md`
3. `context/02_canonical_map.md`
4. `.agent/sev/FIRST_WORKFORCE_DEPLOYMENT_PACKET_2026-03-06.md`
5. `.agent/sev/candidate_genomes/palisade.genome.md`
6. `docs/AIM_OS_PRIME_CANON_INDEX_V1.md`
7. `docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md`
8. `docs/AUDIT_01_SYSTEM_MAP.md`
9. `docs/AUDIT_02_CAPABILITY_MATRIX.md`
10. `docs/roundtable/IDENTITY_CANON.md`
11. `docs/roundtable/decisions/DECISION_LOG.md`

---

## 4. Scope Boundaries

## 4.1 In scope

- `.agent/STARTUP.md`
- `.agent/COMMS_DOCTRINE.md`
- `.agent/comms/COMMS_CANONICAL.md`
- `.agent/comms/COMMS_PROTOCOL.md`
- `.agent/genomes/*.genome.md`
- `.agent/sev/*`
- `context/00_operational_definition.md`
- `context/01_current_truth.md`
- `context/02_canonical_map.md`
- `context/03_tonight_plan.md`
- `docs/AIM_OS_PRIME_CANON_INDEX_V1.md`
- `docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md`
- `docs/AUDIT_01_SYSTEM_MAP.md`
- `docs/AUDIT_02_CAPABILITY_MATRIX.md`
- `docs/roundtable/START_HERE.md`
- `docs/roundtable/IDENTITY_CANON.md`
- `docs/roundtable/INDEX.md`
- `docs/roundtable/decisions/DECISION_LOG.md`
- older role/governance docs only when they directly conflict with the files above

## 4.2 Out of scope

- changing runtime code
- restarting services or changing MCP processes
- rewriting global roundtable canon directly
- editing `packages/*` implementation files
- promoting any candidate genome into official identity routing
- resolving disputes by assertion instead of evidence

---

## 5. Implementation Expectations

### Allowed behavior

- read broadly inside the scoped doctrine surfaces
- compare claims across files
- identify conflicts, stale assumptions, duplicate authorities, and deprecation candidates
- recommend a cleanup order
- create one local report in `.agent/sev/reports/`

### Forbidden behavior

- mutating global canon files as part of this packet
- collapsing "local active doctrine" and "global canon" into the same status
- treating historical docs as current authority without explicit decision references
- making runtime-health claims without citing live truth sources already present in scoped current-truth docs

---

## 6. Required Deliverable

Create:
- `.agent/sev/reports/PALISADE_DOCTRINE_DRIFT_MAP_2026-03-06.md`

Required sections:

1. **Executive summary**
   - 5-10 concise findings
2. **Authority map**
   - which docs currently behave as canonical
   - which docs are local-active only
   - which docs are historical/conflicting
3. **Conflict table**
   - file A
   - file B
   - topic
   - conflict description
   - recommended status (`canon`, `local`, `historical`, `deprecated candidate`, `needs adjudication`)
4. **Cleanup queue**
   - ordered list of highest-value cleanup actions
5. **Risks**
   - what should not be changed casually
6. **Verification notes**
   - what was actually read

Preferred style:
- evidence-first
- short, high-signal tables
- no broad philosophy

---

## 7. Validation Requirements

Validation for this packet means:
- every major finding cites at least one concrete file path
- every conflict distinguishes evidence from inference
- no source outside scope is treated as authoritative without explanation
- the report is usable by Sev for immediate cleanup prioritization

No build/test run is required.

---

## 8. Reporting Format

Every meaningful update from PALISADE should use:

### A. What changed
- exact files read or report sections completed

### B. Assumptions
- any assumptions about authority or document freshness

### C. Merge impact
- local-only, no runtime impact

### D. Drift check
- confirm no canon was silently rewritten

### E. Validation result
- report completeness and evidence quality

### F. Next move
- immediate next reading or synthesis step

### G. Deliverable summary
- What
- Where
- How to verify

---

## 9. Escalation Triggers

Escalate back to Sev if:
- a conflict cannot be classified without a new governance decision
- a file appears to be simultaneously canonical and explicitly rejected
- the packet suggests edits to shared/global canon rather than a local report
- runtime/process actions appear necessary to complete the analysis

---

## 10. Definition of Done

Mission is done when:
- the drift-map report exists at the specified path
- the report contains a usable conflict table and cleanup queue
- Sev can use it to decide the first canon cleanup packet without redoing the whole comparison

---

*Candidate mission packet. Evidence first, no silent canon rewrites.*
