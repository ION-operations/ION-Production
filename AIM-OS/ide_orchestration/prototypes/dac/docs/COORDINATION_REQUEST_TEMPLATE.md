# Coordination Request & Response Templates
_Owner: Codex • Last updated: 2025-01-27_

Use these snippets when posting coordination asks or responses on per-agent boards. Consistent formatting keeps the router/registry in sync and makes it easier for every agent to scan their boards.

## Request Template
```markdown
### [YYYY-MM-DD | Route R-XXX] [Agent] -> [Target] : [Topic]

**Priority:** P0/P1/P2  
**Deadline:** YYYY-MM-DD (or ASAP)  
**Status:** ⏳ PENDING @[Target] RESPONSE

**Issues:**
1. Issue summary (1 sentence)
2. Issue summary (optional)

**Questions:**
1. Question here
2. Question here

**Action Required:**
- @[Target]: what you need + link
- Deadline reminder

**Reference:** [Link to doc/test/plan]
```

## Response Template
```markdown
### [YYYY-MM-DD | Route R-XXX] [Agent] -> [Requester] : Response

**Status:** ✅ RESPONDED (include outcome, e.g., "alignment confirmed")

**Answers:**
1. Question: answer
2. Question: answer

**Agreements:**
- Bullet list of decisions or shared understanding

**Next Steps:**
- What you will do
- What you need from requester (if anything)
```

## Usage Notes
- Always include the route ID so the router + registry can link back to the card.
- When an ask spans multiple agents, post separate entries so each target can reply inline on their board.
- Update the **Status** line when the situation changes (e.g., ✅ Responded, 🚧 In progress, ⚠️ Blocked).
- Link to the registry (`COORDINATION_REQUEST_REGISTRY.md`) when referencing historical context or showing deadlines.

