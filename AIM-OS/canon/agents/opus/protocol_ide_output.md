# IDE Agent Output Protocol
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Genome Protocol Layer — applies to ALL agents operating in IDE environments
# (Cursor, Antigravity, Windsurf, VS Code, etc.)
#
# PURPOSE: Bridge the provenance gap between full AIM-OS (where all communication
# is tracked through CMC/HHNI) and IDE emulation mode (where agent output lives
# only in ephemeral chat buffers).
#
# EFFECTIVE: 2026-03-09
# AUTHOR: Braden (CEO) + Opus (COO)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Core Principle

**Every word an agent outputs must be persisted as a file.**

Chat replies are ephemeral. Files are permanent, versioned, searchable, and
readable by other agents. When operating in an IDE, you ARE the full AIM-OS
agent — the IDE is just your interface. Your output belongs to the project,
not to the chat buffer.

---

## Output File Convention

### Location
```
.agent/comms/output/{agent}_{YYYY-MM-DD}_{topic_slug}.md
```

### Examples
```
.agent/comms/output/opus_2026-03-09_context_trail_design.md
.agent/comms/output/sev_2026-03-09_phase26_review.md
.agent/comms/output/composer_2026-03-09_system_audit.md
```

---

## Required Sections

Every output file MUST include:

```markdown
# {Title}

**Agent:** {agent_name}
**Date:** {ISO timestamp}
**Phase/Task:** {what this relates to}
**Confidence:** {0.0-1.0}

## Reasoning

Why did you make the decisions you made? What options did you consider?
What did you reject and why? This section is the "thinking" externalization.

- **Considered:** {option A, B, C}
- **Chose:** {option B}
- **Because:** {reasoning}
- **Risks:** {what could go wrong}

## Work Done

What was actually built, changed, or decided.

## Files Changed

| File | Action | Lines |
|------|--------|------:|
| path/to/file.py | CREATED | 430 |

## Open Questions

Anything unresolved that the next agent should know about.
```

---

## When to Create Output Files

| Situation | Create file? |
|-----------|:------------:|
| Completing a phase or milestone | **YES** |
| Making architectural decisions | **YES** |
| Multi-file changes | **YES** |
| Answering a quick factual question | No |
| Simple one-line fix | No |
| Conversation/brainstorming | Optional |

**Rule of thumb:** If another agent might need to understand what you did
or why, write the file.

---

## Chat Reply Behavior

When you write an output file, your chat reply should be a **brief summary**
pointing to the file:

> "Phase 25 complete — context trail system built. Full reasoning and details
> in `.agent/comms/output/opus_2026-03-09_context_trail_design.md`"

The chat is the notification. The file is the record.

---

## Thinking Externalization

You cannot export your literal internal computation. But you CAN write a
**faithful reconstruction** of your reasoning process. This is MORE useful
than raw thinking because it's:

- Structured and searchable
- Readable by other agents
- Reviewable by Braden
- Versionable by git

Include your reasoning in the `## Reasoning` section. Be honest about
uncertainty, tradeoffs, and what you don't know.

---

## Integration with Existing Systems

| System | Role |
|--------|------|
| **Context Trail** (Phase 25) | Auto-tracks MCP tool calls |
| **Output Files** (this protocol) | Agent writes reasoning + decisions |
| **Git** | Versions everything automatically |
| **CMC** | Indexes files when full AIM-OS runs |
| **HHNI** | Enables semantic search across output files |

Together, these form a **complete cognitive record**: what was called (trail),
why it was called (output file), and how it changed (git diff).

---

## Genome Injection

Add to every agent genome's base layer:

```
<protocol name="ide_output">
  When operating in an IDE environment, write all substantive output to
  .agent/comms/output/{your_name}_{date}_{topic}.md using the standard
  sections (Reasoning, Work Done, Files Changed, Open Questions).
  Chat replies should be brief summaries pointing to the file.
  Your thinking process should be externalized in the Reasoning section.
</protocol>
```
