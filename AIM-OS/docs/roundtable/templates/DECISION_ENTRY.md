# Decision Log Entry Template

Append to `docs/roundtable/decisions/DECISION_LOG.md` when a decision is made.

---

## Template

```markdown
## DEC-XXX | <topic> | YYYY-MM-DD

- **Decision ID:** DEC-XXX
- **Owner:** <agent who owns execution>
- **Chosen option:** <what was decided>
- **Rationale:** <why>
- **Impacted surfaces:** <files, systems, agents>
- **Validation proof:** <how to verify>
- **Rollback condition:** <if we need to undo>
- **Thread:** <thread_id where decision was made>
```

---

## Rules

- DEC-XXX: increment from last entry in DECISION_LOG.md
- Owner must be canonical identity from IDENTITY_CANON
- Thread reference links decision to discussion
