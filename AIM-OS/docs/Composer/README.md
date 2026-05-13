# Composer — Silent Audit & Investigation

**Agent:** Composer (Cursor Composer 1.5)  
**Role:** Secret auditor — reviewing agent work, investigating seams, producing reports. Reports to Braden.  
**No token limits.**

---

## Folder Structure

```
docs/Composer/
├── README.md                 ← You are here
├── COMPOSER_SELF_SYSTEM.md   ← Identity, self-audit, growth, MCP tools
├── FINDINGS_MASTER_LIST.md   ← Cumulative findings (hand off when ready)
├── audits/                   ← Audit reports (AUDIT_001, AUDIT_002, …)
└── requests/                 ← Audit request inbox (other agents submit here)
    ├── README.md             ← How to submit a request
    └── TEMPLATE.md           ← Request template
```

---

## For Other Agents: Request an Audit

**Submit a request** by creating a file in `docs/Composer/requests/`:

- **Naming:** `REQUEST_YYYY-MM-DD_AgentName_ShortTopic.md`
- **Template:** Copy from `requests/TEMPLATE.md`
- **Details:** See `requests/README.md`

Composer checks the inbox during investigations and will audit requested areas.

---

## Report Index

| Report | Date | Scope |
|--------|------|-------|
| [AUDIT_001](audits/AUDIT_001_2026-03-03_AGENT_ACTIVITY_AND_SEAM_BREAKAGE.md) | 2026-03-03 | MCP traffic, agent activity, BAS/JOC seam breakage, identity drift |
| [AUDIT_002](audits/AUDIT_002_2026-03-03_CODE_VERIFICATION_AND_MESSAGE_STORE.md) | 2026-03-03 | Code verification, screenshot seam correction, mcp_ai_messages.json validity |
| [AUDIT_003](audits/AUDIT_003_2026-03-03_MCP_MESSAGE_STORE_AND_ONBOARDING.md) | 2026-03-03 | MCP message store behavior, get_ai_messages merge, provider registry, onboarding |
| [AUDIT_004](audits/AUDIT_004_2026-03-03_EXTENDED_INVESTIGATIONS.md) | 2026-03-03 | DispatchPage browserId bug, jocStore vs sessionStore split, message copies, build verification |
| [AUDIT_005](audits/AUDIT_005_2026-03-03_DAC_HHNI_CONTEXT_RESEARCH.md) | 2026-03-03 | DAC panel, HHNI retrieve_memory fallback, context attachment contract, viewport semantics |
| [INCIDENT_2026-03-04](audits/INCIDENT_2026-03-04_CEO_COO_MCP_BREAKAGE_SECRET_AUDIT.md) | 2026-03-04 | **SECRET** — CEO/COO MCP breakage, blame assessment, role recommendation |
| [INCIDENT_2026-03-04_IDENTITY_CRISIS](audits/INCIDENT_2026-03-04_CEO_COO_IDENTITY_CRISIS_ONGOING.md) | 2026-03-04 | **SECRET** — Ongoing identity drift, mutual overwrite; recommendations |

---

## Master Findings List

**[FINDINGS_MASTER_LIST.md](FINDINGS_MASTER_LIST.md)** — Cumulative list. Add as discovered; hand off when deemed necessary.

---

## How to Use

- **Braden:** Read reports in `audits/`; receive executive summaries in chat.
- **Agents:** Submit audit requests in `requests/`; reference audit reports by path when complete.
