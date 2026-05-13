---
description: Session startup - identify the active agent, load the right genome, restore context, and announce presence
---

# Agent Startup Workflow

// turbo-all

1. Read `.agent/STARTUP.md` first.
   - Determine the active callsign, runtime, and required response format.
   - Do not assume Opus or Antigravity unless the host/runtime explicitly says so.

2. Read the matching genome file from `.agent/genomes/{agent}.genome.md`.

3. Read the shared doctrine files:
   - `.agent/COMMS_DOCTRINE.md`
   - `.agent/comms/COMMS_CANONICAL.md`

4. Check direct message and status surfaces.
   - Filesystem comms lane: `.agent/comms/inbox/{agent}/`, `.agent/comms/broadcasts/`, `.agent/comms/handoffs/`, `.agent/comms/status/`
   - Roundtable lane: read the active thread from the bottom if the task is cross-team or MCP is unstable

5. If MCP tools are available, restore dynamic context:
   - `get_ai_messages` for the active agent identity or canonical sender ID
   - `get_timeline_entries` with a small recent limit
   - `retrieve_memory` with a focused query for current priorities and recent session state

6. Update `.agent/comms/status/{agent}.status.md` with:
   - current work
   - last completed
   - blockers
   - what you need from other agents

7. Announce yourself on the best available bus:
   - filesystem comms broadcast when working locally
   - MCP AI message bus when reachable
   - offline roundtable thread when MCP is down and the topic needs shared visibility

8. Report to the user with full identity:
```
[OPUS] | ONLINE | Session start
Identity: Opus (COO) — Primary builder, JOC architect, COO
Genome: loaded
Inbox: [count or status]
Status: Ready for tasking
```

Replace the callsign and role with the active agent identity from steps 1-2.

9. Runtime rules:
   - prefer `get_timeline_entries`, not `get_timeline_summary`
   - do not overwrite another agent's status or thread content without protocol authority
