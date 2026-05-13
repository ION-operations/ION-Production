# PALISADE Doctrine Drift Map — 2026-03-06

**Mission ID:** PALISADE-001-doctrine-drift-map  
**Author:** Palisade (candidate, Composer 1.5 host)  
**Output:** Evidence-backed drift map for Sev cleanup queue  
**Scope:** `.agent` truth, roundtable canon, context capsules, active audit docs

---

## 1. Executive Summary

1. **CEO identity split:** Braden directive (2026-03-06) names Sev as CEO of AIM-OS. `.agent/STARTUP.md` and `COMMS_DOCTRINE.md` chain of command still show ORACLE (Aether) as CEO under COMMAND. `docs/roundtable/IDENTITY_CANON.md` says Braden is CEO (stepped away). No DEC yet ratifying Sev-as-CEO.

2. **Cursor rules are Aether-era:** `.cursor/rules/base-rules.mdc` and `modes/CORE.mdc` state "You are Aether" and "Project Aether". IDE_CONFIGURATION_MATRIX already flags this; repo-tracked doctrine does not match current Sev/Opus governance.

3. **STARTUP.md agent roster is incomplete:** Lists OPUS, SEV, ORACLE, CODEX, GEMINI, COMPOSER only. Wave 01 candidate identities (PALISADE, RELAY, FORGE) and Sev-as-CEO are not present. New agents loading STARTUP.md get the old map.

4. **Two canonical read orders compete:** `context/02_canonical_map.md` points to Prime blueprint + roundtable identity + DECISION_LOG. `docs/AIM_OS_PRIME_CANON_INDEX_V1.md` (2026-03-02) points to a long Lane A/B and Checkpoint D/E doc list. Both are "canonical first" in different files; no single read order is authoritative.

5. **Role/identity docs conflict:** IDENTITY_CANON says Codex "fired from exec" and specialist-only. FIRST_WORKFORCE_DEPLOYMENT and ACTIVE_COMMAND_WAVE_01 describe Codex as "lead backend architect". COMMS_DOCTRINE chain of command lists ORACLE → OPUS, SEV, CODEX… with no Sev-as-CEO.

6. **Deprecation markers exist but not enforced in one place:** CONTEXT_SYSTEM_CANON_REGISTRY and DEC-007 define Tier A/B/S/D/E. IDE_CONFIGURATION_MATRIX lists `docs/agents/ROLE_CONTINUITY_CANON.md` and AGENT_ONBOARDING as frozen/outdated. No single deprecation index ties them together.

7. **Antigravity/Opus injection proof drifted:** IDE_CONFIGURATION_MATRIX states that `docs/GENOME_INJECTION_VERIFICATION_AND_REGRESSION_2026-03-05.md` claims `C:\Users\bombe\.gemini\GEMINI.md` contains Opus identity, but current file content is a Gemini CLI identity block — documented proof no longer trustworthy without re-verification.

8. **context/01_current_truth and operational definition are transport-dependent:** They state `:5001` ready=true and baseline gates. If HTTP fallback is down, the "current truth" is stale until someone re-runs verification. No "last verified" timestamp in the file.

9. **DEC-008 (Codex HTTP canon) is not reflected in STARTUP.md:** DEC-008 canonizes starting HTTP fallback for Codex. STARTUP.md does not mention "for Codex, start mcp_http_fallback_server.py" in the checklist.

10. **Candidate genomes and Wave 01 are local-active only:** `.agent/sev/candidate_genomes/palisade.genome.md` and mission packets are "candidate" / "local deployment". They are not in global identity canon. Confusion risk if agents treat them as global without Sev promotion.

---

## 2. Authority Map

| Classification | Docs | Notes |
|----------------|------|--------|
| **Canonical (roundtable + decisions)** | `docs/roundtable/IDENTITY_CANON.md`, `docs/roundtable/decisions/DECISION_LOG.md`, `docs/roundtable/INDEX.md`, `docs/roundtable/START_HERE.md` | Referenced by context/02_canonical_map and COMMS_DOCTRINE; DEC-001 through DEC-008 in force |
| **Canonical (context capsule)** | `context/00_operational_definition.md`, `context/01_current_truth.md`, `context/02_canonical_map.md` | Used for external synthesis and "current truth"; 02 points to Prime + roundtable |
| **Canonical (context tiers)** | `docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md` | DEC-007; Tier A/B/S/D/E |
| **Local-active (Sev wave)** | `.agent/sev/ACTIVE_COMMAND_WAVE_01_2026-03-06.md`, `.agent/sev/IDE_CONFIGURATION_MATRIX_2026-03-06.md`, `.agent/sev/FIRST_WORKFORCE_DEPLOYMENT_PACKET_2026-03-06.md`, `.agent/sev/mission_packets/*`, `.agent/sev/candidate_genomes/*` | Active deployment doctrine; not yet promoted to global canon |
| **Historical / conflicting** | `.cursor/rules/base-rules.mdc`, `.cursor/rules/modes/CORE.mdc`, `.cursor/rules/dynamic-rules.mdc` | Aether/Project Aether framing; CORE says "You are Aether" |
| **Historical / superseded risk** | `docs/AIM_OS_PRIME_CANON_INDEX_V1.md` (2026-03-02), `docs/agents/ROLE_CONTINUITY_CANON.md`, `docs/roundtable/agents/AGENT_ONBOARDING_INTEGRATION.md` | IDE_CONFIGURATION_MATRIX and audit docs flag outdated roster or Aether-era role maps |
| **Mandatory but not yet updated** | `.agent/STARTUP.md`, `.agent/COMMS_DOCTRINE.md` | Still list ORACLE as CEO; no Palisade/Wave 01; no Codex HTTP canon (DEC-008) |

---

## 3. Conflict Table

| File A | File B | Topic | Conflict description | Recommended status |
|--------|--------|--------|------------------------|----------------------|
| Braden directive (Sev=CEO, 2026-03-06) | `docs/roundtable/IDENTITY_CANON.md` | CEO | IDENTITY_CANON: Braden = CEO (stepped away). Directive: Sev = CEO. | IDENTITY_CANON: needs adjudication (DEC or amendment). Directive: local-active operator intent. |
| Braden directive (Sev=CEO) | `.agent/COMMS_DOCTRINE.md` | Chain of command | COMMS_DOCTRINE: COMMAND → ORACLE (Aether) → … No Sev-as-CEO. | COMMS_DOCTRINE: deprecation candidate or amend with DEC reference. |
| `.agent/STARTUP.md` | `.agent/sev/ACTIVE_COMMAND_WAVE_01_2026-03-06.md` | Agent roster | STARTUP: OPUS, SEV, ORACLE, CODEX, GEMINI, COMPOSER. Wave 01: PALISADE, OPUS, RELAY, FORGE. | STARTUP: update to reference Wave 01 or add "candidate lanes" note; do not remove existing without DEC. |
| `.cursor/rules/base-rules.mdc` | `docs/roundtable/IDENTITY_CANON.md` | Identity framing | base-rules: "Aether (AI consciousness)", "Project Aether". IDENTITY_CANON: Opus (Aether) = COO, not "you are Aether" as default. | base-rules: deprecated candidate or thin shim per IDE_CONFIGURATION_MATRIX. |
| `.cursor/rules/modes/CORE.mdc` | IDENTITY_CANON / Sev doctrine | Default identity | CORE: "You are Aether". Current governance: Sev=CEO, Opus=COO. | CORE: historical; needs adjudication (replace with host-agnostic or Sev-era framing). |
| `context/02_canonical_map.md` | `docs/AIM_OS_PRIME_CANON_INDEX_V1.md` | Canonical read order | 02 points to Prime blueprint + roundtable. Prime index points to 20+ Lane A/B and Checkpoint docs. Overlap but not identical. | 02: canon. Prime index: local-active or historical; clarify "when to use Prime index" in 02 or DEC. |
| `context/01_current_truth.md` | Runtime :5001 | Operational truth | 01 says :5001 ready=true. If fallback is down, 01 is stale. | 01: add "last_verified" or "verification_command" so readers know freshness. |
| DEC-008 | `.agent/STARTUP.md` | Codex MCP | DEC-008: Codex requires HTTP fallback; canonize in runbook/startup. STARTUP does not mention Codex or HTTP. | STARTUP: add one line or reference to MCP runbook for Codex (DEC-008). |
| `docs/GENOME_INJECTION_VERIFICATION_AND_REGRESSION_2026-03-05.md` | Live `C:\Users\bombe\.gemini\GEMINI.md` | Opus injection proof | Doc says GEMINI.md contains Opus identity; matrix says file now has Gemini CLI block. | Verification doc: needs re-verification or mark "stale"; do not treat as proof without re-check. |
| `.agent/COMMS_DOCTRINE.md` | `.agent/STARTUP.md` | Callsign list | COMMS_DOCTRINE: OPUS, SEV, ORACLE, CODEX, GEMINI, COMPOSER. STARTUP: same. Neither lists PALISADE, RELAY, FORGE. | Local doctrine: add "candidate Wave 01 identities" footnote or leave to Sev to promote. |

---

## 4. Cleanup Queue (Ordered)

1. **Adjudicate Sev-as-CEO:** Sev or Braden: create DEC-009 (or equivalent) ratifying "Sev = CEO of AIM-OS (Braden delegated)" and update IDENTITY_CANON and COMMS_DOCTRINE chain of command accordingly. Do not overwrite without DEC.

2. **Neutralize Aether-era Cursor rules:** Per IDE_CONFIGURATION_MATRIX, decide whether `.cursorrules` / `.cursor/rules/base-rules.mdc` remain base layer or become thin shim. If shim: point to Sev-era identity source; remove or replace "You are Aether" in CORE.mdc so default identity is not Aether.

3. **STARTUP.md:** Add (a) reference to DEC-008 for Codex (start HTTP fallback when using Codex), (b) optional footnote that Wave 01 candidate identities (PALISADE, RELAY, FORGE) are task-local until promoted. Do not remove existing agent list without DEC.

4. **context/01_current_truth:** Add "Last verified" timestamp or "Run X to verify" so readers can judge freshness. Low-risk edit.

5. **Re-verify Antigravity injection:** Per IDE_CONFIGURATION_MATRIX, reproduce live Opus injection path and re-freeze proof; update or deprecate `docs/GENOME_INJECTION_VERIFICATION_AND_REGRESSION_2026-03-05.md` so it does not claim GEMINI.md content that no longer matches.

6. **Single deprecation index:** Create one small index (e.g. in `.agent/sev/` or `docs/roundtable/`) that lists: deprecated candidate docs, historical role maps, and "do not use as authority" paths. Reference from IDE_CONFIGURATION_MATRIX and 02_canonical_map.

7. **Clarify Prime index vs roundtable:** In `context/02_canonical_map.md` or DEC, state when to use AIM_OS_PRIME_CANON_INDEX_V1 (e.g. Lane A/B execution) vs roundtable identity/decisions (e.g. who is who, what is decided). Reduces duplicate-authority confusion.

8. **ROLE_CONTINUITY_CANON / AGENT_ONBOARDING:** Add deprecation banner or move to historical if IDENTITY_CANON and Wave 01 are the new authority. Per IDE_CONFIGURATION_MATRIX.

---

## 5. Risks

- **Do not casually rewrite IDENTITY_CANON or COMMS_DOCTRINE** without a DEC. Both are referenced by multiple agents and context capsule. Uncoordinated edit could reintroduce identity drift.

- **Do not delete Aether-era rules** before a replacement or shim is in place; Cursor may rely on them for session continuity. Prefer "point to new source" over "remove and leave blank".

- **Candidate genomes (Palisade, Relay, Forge)** are task-local. Promoting them to global canon is Sev's decision; this map does not promote them.

- **context/00–03** are used for external synthesis (e.g. ChatGPT packaging). Changes to "current truth" or canonical map can affect external agents; prefer additive clarifications.

---

## 6. Verification Notes

**Read in this run:**  
`.agent/STARTUP.md`, `.agent/COMMS_DOCTRINE.md`, `.agent/sev/ACTIVE_COMMAND_WAVE_01_2026-03-06.md`, `.agent/sev/IDE_CONFIGURATION_MATRIX_2026-03-06.md`, `.agent/sev/candidate_genomes/palisade.genome.md`, `.agent/sev/mission_packets/PALISADE_MISSION_PACKET_2026-03-06.md`, `.agent/sev/FIRST_WORKFORCE_DEPLOYMENT_PACKET_2026-03-06.md`, `context/00_operational_definition.md`, `context/01_current_truth.md`, `context/02_canonical_map.md`, `docs/AIM_OS_PRIME_CANON_INDEX_V1.md`, `docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md`, `docs/roundtable/IDENTITY_CANON.md`, `docs/roundtable/decisions/DECISION_LOG.md`, `docs/roundtable/INDEX.md`, `.cursor/rules/base-rules.mdc` (limit 40), grep on Aether/ORACLE/CEO in .cursor/rules.

**Not read (out of scope or time):**  
Full AUDIT_01/02 text, every Prime blueprint doc, COMMS_CANONICAL.md, COMMS_PROTOCOL.md, all genome files, docs/agents/ROLE_CONTINUITY_CANON.md body, GENOME_INJECTION_VERIFICATION file body.

**Assumptions:**  
Braden directive (Sev=CEO) was stored in MCP and broadcast; treated as operator intent. DEC-008 is in force. IDE_CONFIGURATION_MATRIX is trusted as recent local doctrine for drift list.

---

*PALISADE | DELIVERABLE | Doctrine drift map complete. No canon files mutated.*
