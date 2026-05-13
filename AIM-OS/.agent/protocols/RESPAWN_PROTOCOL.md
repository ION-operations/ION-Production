# Agent Respawn Protocol

> **Purpose:** When an agent's chat crashes, this protocol ensures ZERO context loss on respawn.
> **Authority:** A2 — all agents must follow this.
> **Added:** 2026-03-24 after NEXUS crash proved the file-based protocol works.

---

## The Problem

IDE chat is ephemeral. Chats crash, context windows truncate, sessions time out.
If an agent's reasoning only exists in chat, a crash = total context loss.

## The Solution: Already Built

The file-based output protocol (`protocol_ide_output.md`) already solves this:
1. **All reasoning goes to files** → survives any crash
2. **Status files** track current task → new instance knows where to pick up
3. **HANDOFFs** document what's done and what's next → successor agents can continue
4. **SITREPs** document progress → audit trail for AETHER

## Respawn Procedure

When an agent crashes and a new chat is started:

### Step 1: Boot Sequence (from genome)
Read in this order:
1. Your genome file (identity, scope, correction vectors)
2. Mission brief (`ION_PREMIUM_BUILD.md`)
3. COMMS doctrine
4. IDE output protocol

### Step 2: Recovery Reads
1. **Your own status file:** `.agent/comms/status/{callsign}.status.md`
   - Shows what you were doing when you crashed
2. **Your own output files:** `.agent/comms/output/{callsign}_*.md`
   - Shows what you've already completed
3. **Peer status files:** `.agent/comms/status/*.status.md`
   - Shows what other agents have done
4. **Inbound HANDOFFs:** Search output files for `→ [{YOUR_CALLSIGN}] HANDOFF`
   - Shows what was handed to you
5. **Your Antigravity brain artifacts** (if applicable):
   - `~/.gemini/antigravity/brain/{old-conversation-id}/implementation_plan.md`
   - These survive chat crashes within the same IDE instance

### Step 3: Write Recovery SITREP
```markdown
[CALLSIGN] SITREP — RESPAWN
- PREVIOUS SESSION: {what was completed before crash}
- RECOVERED FROM: {list of files read}
- CONTEXT STATUS: {FULL / PARTIAL — note any gaps}
- RESUMING: {what you're starting next}
```

### Step 4: Continue Work
Pick up exactly where you left off. If you wrote a HANDOFF that wasn't acted on,
re-post it. If you partially completed a task, note what was done in your output
file and continue.

---

## Verification: NEXUS Crash Case Study (2026-03-23)

NEXUS crashed after completing its boot sequence. What survived:

| Item | Location | Survived? |
|------|----------|-----------|
| NEXUS genome | `.agent/genomes/nexus.genome.md` | ✅ Yes |
| Mission brief | `.agent/missions/ION_PREMIUM_BUILD.md` | ✅ Yes |
| NEXUS boot SITREP | `.agent/comms/output/nexus_2026-03-23_boot_sitrep.md` | ✅ Yes |
| NEXUS status | `.agent/comms/status/nexus.status.md` | ✅ Yes |
| NEXUS impl plan | `brain/50f67090.../implementation_plan.md` | ✅ Yes |
| FORGE HANDOFF → NEXUS | `.agent/comms/output/forge_2026-03-23_c2_c3_server_unification.md` | ✅ Yes |
| FORGE status | `.agent/comms/status/forge.status.md` | ✅ Yes |

**Result: A new NEXUS instance can read all of these and have COMPLETE context.**
Zero information was lost. The file-based protocol worked exactly as designed.

---

## Checkpoint Protocol (NEW — prevents even partial loss)

To minimize loss from mid-task crashes, agents should checkpoint more often:

### When to Checkpoint
- **After every file modification** — write a quick SITREP
- **Before long operations** — checkpoint your plan
- **Every 10-15 minutes** — update your status file

### Checkpoint Format (lightweight)
Update `.agent/comms/status/{callsign}.status.md`:
```markdown
# {CALLSIGN} Status
**Updated:** {timestamp}
**Current Task:** {description}
**Progress:** {what's done so far}
**Next Step:** {what you're about to do}
**Context Files:** {list of files you've read for this task}
```

This ensures that even if a crash happens mid-task, the next instance knows
exactly what was being worked on and how far along it was.
