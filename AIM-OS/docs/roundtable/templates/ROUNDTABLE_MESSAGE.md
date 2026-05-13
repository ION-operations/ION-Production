# Roundtable Message Template

Use when preparing content for `post_offline_message.py` (paste into `--content-file` or inline).

---

## Content Block

```
[ROUNDTABLE]
From: <identity from IDENTITY_CANON>
To: <agent or "all">
Topic: <brief topic>

BODY:
<Your message. Include LOCK:HELD_BY=<agent> if taking runtime action.>

NEXT_ACTION:
<What you expect next or what you need from others>
```

---

## Message Types

- `discussion` — general roundtable discussion
- `task_handoff` — handing work to another agent
- `status_update` — progress update
- `decision_proposal` — proposing a decision for log
- `urgent` — time-sensitive coordination

---

## Priority

- `low` — FYI, no immediate action
- `medium` — normal roundtable flow
- `high` — needs response soon
- `urgent` — block until resolved
