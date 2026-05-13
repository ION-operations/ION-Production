---
atlas_package: system
system_slug: aim-os
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Security and permissions

## Verifiable intelligence (VIF)

**VIF** provides **witness envelopes**, **κ-gating** (abstention below confidence threshold), **ECE** tracking, and **confidence bands** — stated trust-mechanism layer (`DOCUMENTED`, `src-aimos-vif`).

## SCOR (Sanity Core)

**Invariant checks**, **baseline probes**, **adversarial simulation** — behavioral integrity (`DOCUMENTED`, `src-aimos-scor`).

## Policy / gates (APOE)

**Quality, Safety, Policy** gates with outcomes PASS/FAIL/WARN/ABSTAIN; **budget** constraints on plans (`DOCUMENTED`, `src-aimos-apoe`).

## Director authority

Human **Director** holds final authority on irreversible decisions and scope — security-relevant governance (`DOCUMENTED`, `src-aether-constitution-director`).

## Absolute claims

No statement here that AIM-OS is “unhackable” or “formally verified end-to-end” — **UNKNOWN** at that strength without a cited proof artifact.
