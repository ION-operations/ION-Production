---
atlas_package: system
system_slug: multics
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Architecture

## Structural overview

- **Supervisor / user modes** with hardware-enforced protection rings for privileged operations (`HISTORICAL`, `paper-organick-1972-multics`).  
- **Segmented virtual memory** model tying protection to segments (`HISTORICAL`, `paper-saltzer-1974-protection`).  
- **Unified treatment of memory and persistent information** in the research design (single-level store concepts — `HISTORICAL`; exact mechanism phrasing must track Organick/Saltzer wording in ledger `mc-003`).

## Control vs data plane

- **Supervisor** mediated privileged resources and enforced policy (`HISTORICAL`).  
- **User programs** accessed objects via controlled capabilities/ACL semantics as described in protection literature (`HISTORICAL` — do not collapse to modern “capabilities OS” without matching definitions).

## Evidence gaps

- Internal module decomposition varies by era and site; **UNKNOWN** for micro-modular map without a cited diagram revision.
