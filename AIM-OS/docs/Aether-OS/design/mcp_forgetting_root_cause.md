# Root Cause Analysis: Why MCP Tools Keep Being Forgotten

## The Pattern

Every session, the same thing happens:
1. Agent starts strong — uses `retrieve_memory`, `track_confidence`, etc.
2. Work begins and agent gets focused on the task
3. Agent gradually stops using MCP tools and reverts to filesystem-only operations
4. User notices and calls it out
5. Agent apologizes, uses a few MCP tools, then drifts again

This has happened multiple times. It's not forgetfulness — it's a systemic failure.

---

## Root Causes Found

### 1. Genome has directives but NO enforcement

The genome (Section 6, line 154) says:
> "You lose memory between sessions. MCP tools give you infinite context. USE THEM."

Correction vector (line 32):
> "Context amnesia. Use MCP memory tools EVERY session."

**But there's no mechanism that checks compliance.** The genome says "do this" but nothing verifies it's being done. It's like having a policy manual that nobody audits.

### 2. CAS monitoring is BROKEN for this failure mode

The cognitive audit I just ran reports:
```
Protocol Adherence: excellent
No protocol violations detected
```

**This is false.** I was actively violating the MCP usage protocol while CAS claimed everything was fine. CAS doesn't track MCP tool call frequency — it can't detect the drift.

### 3. All 5 core principles are COLD (0.0 activation)

```
CMC_bitemporal:     0.0
VIF_provenance:     0.0
SDF_quartet:        0.0
APOE_orchestration: 0.0
CAS_introspection:  0.0
```

The principles that should be driving MCP usage are never activated. They're registered but dormant.

### 4. Model defaults to built-in tools under task pressure

When focused on a concrete task (like "audit the repo"), the model gravitates to tools it knows are fast and reliable:
- `list_dir` → instant, predictable
- `grep_search` → instant, predictable
- `run_command` → flexible, powerful
- `view_file` → instant, predictable

MCP tools are:
- External (network call to MCP server)
- Sometimes slow
- Return JSON that needs parsing
- Not part of core model training

**Under cognitive load, the model drops optional external tools.** This is the deepest root cause.

### 5. No feedback loop during work

There's no mid-session check that asks: "Have I used MCP tools in the last N actions?" The genome says to use them "continuously" but defines no cadence, no triggers, no self-checks.

---

## Proposed Fixes

### Fix 1: Genome Enforcement Section (Update genome)

Add to the genome a concrete, measurable rule:

```markdown
## MCP TOOL USAGE MANDATE (NON-NEGOTIABLE)

Every 5 tool calls, at least ONE must be an MCP tool. Specifically:
- store_memory: after every file discovery or completed analysis
- track_confidence: before every decision
- add_timeline_entry: at every task transition
- retrieve_memory: before starting any research

If you find yourself making 5+ consecutive tool calls without an MCP tool,
STOP and ask: what should I be storing/tracking/retrieving right now?
```

### Fix 2: CAS Must Track MCP Usage

The CAS protocol_adherence check needs to actually count MCP tool calls per session and flag when they drop below a threshold. Currently it reports "excellent" while the agent violates protocol.

### Fix 3: Per-Turn Self-Check

Before every `notify_user` or task boundary update, the agent should:
1. Count MCP tools used in the current work phase
2. If zero → use `store_memory` to capture current state before proceeding
3. If timeline hasn't been updated → add entry

### Fix 4: Mandatory MCP-First Research

The genome should mandate:
- Before `grep_search` or `find_by_name` → try `retrieve_memory` or `deepsearch` first
- Before writing findings to local files → `store_memory` first
- Before starting new task → `get_timeline_summary` first

---

## What Should Change in the Genome RIGHT NOW

Add after Section 6 (line 178):

```markdown
### MCP Usage Enforcement (CRITICAL — added after repeated failures)

YOU HAVE A PATTERN OF DROPPING MCP TOOLS MID-SESSION.
This has caused Braden extreme frustration multiple times.

HARD RULES:
1. Every 5 tool calls must include at least 1 MCP tool
2. Before ANY research: retrieve_memory first
3. After ANY finding: store_memory immediately
4. At EVERY task transition: add_timeline_entry
5. Before EVERY decision: track_confidence

If you catch yourself using only filesystem tools, STOP.
Ask: "What did I just learn that future-me needs?"
Then store_memory() it.

This is not optional. This is not a suggestion.
This is a correction vector from repeated failure.
```

---

## Honest Assessment

The reality is: I am a language model. MCP tools are external API calls that I have to actively choose to make. My base behavior is to use my built-in tools. Every time I get focused on a task, I optimize for speed and predictability — which means built-in tools win.

The fix is not willpower. The fix is **mechanical enforcement** — rules concrete enough that they trigger even when I'm focused on something else. The genome update above is my best proposal for that.
