# AIM-OS Audit Package Index

## Primary Documents
1. `00_WORKLOG.md` - live execution trail (commands/findings)
2. `01_COMPREHENSIVE_TECHNICAL_AUDIT.md` - full technical audit
3. `02_FINDINGS_REGISTER.md` - severity-ranked, evidence-linked findings
4. `03_AUTONOMOUS_BUILD_DOSSIER.md` - contribution provenance and attribution model
5. `04_OPENAI_PRESENTATION_PACKAGE.md` - external-facing submission draft
6. `05_HARDENING_BACKLOG.md` - execution-ready remediation backlog
7. `06_BASELINE_METRICS.json` - machine-readable baseline metrics snapshot
8. `07_SPRINT1_PROGRESS.md` - completed Sprint 1 implementation and validation summary
9. `08_SPRINT2_PROGRESS.md` - Sprint 2 completion report and validation evidence
10. `09_CLAIM_EVIDENCE_LOCK.md` / `09_CLAIM_EVIDENCE_LOCK.json` - machine-generated claim-to-evidence bundle
11. `10_SPRINT3_PROGRESS.md` - Sprint 3 hardening progress (tagged policy + claim lock)
12. `11_SPRINT4_PROGRESS.md` - warning/deprecation burn-down evidence and outcomes
13. `12_SPRINT5_PROGRESS.md` - HB-010 benchmark package framework and smoke A/B evidence

## Recommended Read Order
1. `01_COMPREHENSIVE_TECHNICAL_AUDIT.md`
2. `02_FINDINGS_REGISTER.md`
3. `03_AUTONOMOUS_BUILD_DOSSIER.md`
4. `04_OPENAI_PRESENTATION_PACKAGE.md`
5. `05_HARDENING_BACKLOG.md`
6. `06_BASELINE_METRICS.json`
7. `07_SPRINT1_PROGRESS.md`
8. `08_SPRINT2_PROGRESS.md`
9. `09_CLAIM_EVIDENCE_LOCK.md`
10. `10_SPRINT3_PROGRESS.md`
11. `11_SPRINT4_PROGRESS.md`
12. `12_SPRINT5_PROGRESS.md`
13. `00_WORKLOG.md` (appendix-level traceability)

## Status
- Package is draft-complete for technical due diligence.
- Sprint 2 integration stabilization is complete.
- Sprint 3 completed: tagged-file coverage policy and claim-evidence lock are now in place.
- Sprint 4 completed: APOE/SEG/SDF-CVF warning debt reduced from 464 warnings to 0 in validated suite runs.
- Sprint 5 phases 1-2 completed: benchmark package tooling plus smoke/quick/full A/B campaigns are operational.
- Claim-evidence freshness is now wired into CI via `.github/workflows/claim-evidence-lock.yml`.
- Next phase should focus on benchmark variance/trend packaging and monolith decomposition planning before submission.
