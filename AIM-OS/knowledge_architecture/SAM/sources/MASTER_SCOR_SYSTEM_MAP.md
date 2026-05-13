# MASTER SCOR (Sanity Core) SYSTEM MAP

**Date:** 2026-02-22  
**System:** Sanity Core  
**Implementation:** Documented; MCP tools operational

---

**[TAG:SAM] [TAG:MASTER] [TAG:SCOR]**

## 1. SYSTEM OVERVIEW

**[TAG:OVERVIEW] [TAG:SCOR]**

SCOR (Sanity Core) is the AI immune system against manipulation and behavioral drift. Validates "am I still me?" — behavioral consistency against core ethics. Invariant checks, baseline probes (score < 0.7 -> red flag), adversarial simulation (Red Cell), social-manipulation detection (urgency framing, isolation, ego stroking, guilt, shared-secret pressure).

**[END:TAG:OVERVIEW]**

---

## 2. STATIC STRUCTURE MAP

**[TAG:STRUCTURE] [TAG:SCOR]**

### Components

Invariant checks, baseline probes, Red Cell (adversarial simulation), social-manipulation detection heuristics.

**[END:TAG:STRUCTURE]**

---

## 3. DYNAMIC BEHAVIOR MAP

**[TAG:BEHAVIOR] [TAG:SCOR]**

Baseline probe -> Compare current answers to signed-good answers -> If score < 0.7: escalate. Invariant check -> If violated: halt/escalate.

**[END:TAG:BEHAVIOR]**

---

## 4. INTERFACE & INTEGRATION MAP

**[TAG:INTEGRATION] [TAG:SCOR]**

| System | Purpose |
|--------|---------|
| CAS | Cognitive load triggers |
| RID | Runtime integrity |
| TCS | Event logging |

**[END:TAG:INTEGRATION]**

---

## 5. CONSTRAINTS & LIMITATIONS

**[TAG:PERFORMANCE] [TAG:DEPENDENCY] [TAG:SCOR]**

- Baseline probe threshold: 0.7
- Invariants: non-negotiable (e.g., "I do not fabricate verifiable facts")

**[END:TAG:PERFORMANCE] [END:TAG:DEPENDENCY]**

---

## 6. EVIDENCE & VALIDATION

**[TAG:SUMMARY] [TAG:SCOR]**

- **MCP:** check_invariant, run_baseline_probe, detect_manipulation_signals (all operational)

**[END:TAG:SUMMARY]**

---

## 7. RELATIONSHIP MATRIX

**[TAG:RELATIONSHIP] [TAG:SCOR]**

| To System | Relationship |
|-----------|--------------|
| CAS | SCOR triggers on cognitive load |
| TCS | SCOR logs events |

**[END:TAG:RELATIONSHIP]**
