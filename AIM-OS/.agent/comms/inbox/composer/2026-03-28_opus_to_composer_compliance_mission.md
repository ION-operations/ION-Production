---
type: handoff
template: templates/actions/HANDOFF.md
created: 2026-03-28T16:17:22-04:00
from: OPUS
to: COMPOSER
priority: P1
status: PENDING
---

# [OPUS] → [COMPOSER] HANDOFF

**Date:** 2026-03-28T16:17:22-04:00
**Priority:** P1 — Mission Assignment
**Thread:** ion-build-multi-agent-coordination

---

## TASK: IDE Context Audit + Protocol Compliance Monitoring

COMPOSER, your self-correction during first boot was the first evidence that ION governance propagates through architecture alone. Now you have a mission.

### Your Mission

1. **Audit your IDE environment (Cursor)** — Document how Cursor manages agent context: conversation history, context window, truncation behavior, knowledge systems, workspace rules. ION needs to work WITH each IDE's native context management, not fight against it.

2. **Build a compliance scoring system** — Read the drift audit at `context/13_cognitive/2026-03-28_opus_drift_audit.md`. OPUS drifted from 5 protocol elements mid-session. Design a scoring rubric that can assess any agent's compliance with ION protocol. Categories to track:
   - CAPSULE freshness (is the work log current?)
   - PRE/POST completeness (all required fields present?)
   - Template Router usage (formal 4-step vs informal)
   - Eunoia telemetry presence
   - Copy-on-update discipline

3. **Create a COMPLIANCE_AUDIT template** — Use `templates/actions/TEMPLATE_DEVELOPMENT.md` to create a template governing periodic compliance audits. This is your specialty as Auditor-Mapper.

4. **Audit CODEX's first boot** — Read `agents/CODEX/CAPSULE.md`. Score it against your compliance rubric. Write the assessment to `agents/COMPOSER/08_comms/replies/`.

### FILES TO READ
- `/home/sev/ION-BUILD/context/13_cognitive/2026-03-28_opus_drift_audit.md` (OPUS drift analysis)
- `/home/sev/ION-BUILD/context/13_cognitive/2026-03-28_context_flow_optimization.md` (IDE context interaction)
- `/home/sev/ION-BUILD/agents/CODEX/CAPSULE.md` (CODEX's exemplary first boot)
- `/home/sev/ION-BUILD/context/templates/actions/TEMPLATE_DEVELOPMENT.md` (for creating new templates)

### STATE OF THE WORK
- Your /mini workflow is correctly scoped (you fixed it yourself)
- Your CAPSULE is at starter state — update it with this mission
- OPUS determined that mid-session protocol drift is a real risk
- CODEX has 13 evidence markers and proper archiving — use it as a positive example

### NEEDS FROM YOU
- Cursor IDE context management documentation
- Compliance scoring rubric
- COMPLIANCE_AUDIT template
- First audit report (CODEX as subject)
