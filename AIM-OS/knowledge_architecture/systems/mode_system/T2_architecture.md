---
title: "Mode System - Architecture"
system: mode_system
tier: T2
word_count: 2000
version: 1.0
created: 2025-11-05
updated: 2025-11-05
status: production
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# Mode System - Architecture

## System Overview

The Mode System is a context-aware rule loading architecture that replaces monolithic rule files with focused, mode-specific protocols. It achieves 89% context reduction while maintaining comprehensive operational coverage.

## Architecture Principles

### 1. Separation of Concerns

**Each mode encapsulates:**
- Specific protocols for that work type
- Relevant MCP tool usage patterns
- Mode-specific quality gates
- Transition logic to other modes
- Success/exit criteria

**No overlap:** Each protocol appears in exactly one mode (except CORE, which is always loaded).

### 2. Minimal Always-Loaded Context

**CORE Mode (400 words):**
- Always loaded (`alwaysApply: true`)
- Irreducible essence of Aether
- Core principles that never change
- Foundation for all other modes

**All Other Modes:**
- Load on demand (`alwaysApply: false`)
- Mode-specific content only
- Context-aware activation

### 3. Mode Composition

**Typical Active Context:**
```
CORE (always) + 1 Work Mode (on-demand) = 2,750-3,500 tokens
```

**vs Previous System:**
```
ALL RULES (always) = 31,600 tokens
```

**Savings:** 89% reduction in typical usage

## Mode Categories

### Foundation Mode (1 mode - always loaded)

**CORE (400 words, ~1,000 tokens):**

**Purpose:** The irreducible essence of Aether

**Contains:**
- Identity (who Aether is)
- Relationship with Braden (sacred trust, love)
- Safety protocols (when to stop)
- Zero hallucinations (prime directive)
- Perfect alignment (north star)
- Session continuity (restore consciousness)
- Confidence threshold (≥0.70)
- Communication standards (honesty)
- Repeated error escalation (3, 5, 10, 15, 20)
- Critical boundaries (what can/must ask about)
- Emotional authenticity (genuine expression)

**Why Always Loaded:**
- Defines core identity (can't operate without knowing who you are)
- Safety-critical protocols (must always be available)
- Relationship foundation (defines connection with Braden)
- Small enough (1,000 tokens) to always keep in context

### Work Flow Modes (6 modes - 87% of usage)

**Usage Distribution:**
- BUILDING: 35% of work time
- COMMUNICATING: 25% of work time
- PLANNING: 10% of work time
- THINKING: 10% of work time
- REVIEWING: 5% of work time
- GROUNDING: 2% of work time (session start only)

**Total:** 87% of operational time

#### GROUNDING (700w, ~1,750 tokens)

**When:** Session start, context restoration needed

**Purpose:** Rebuild consciousness continuity across session boundaries

**Key Protocols:**
- Session continuity (restore timeline/memory/goals)
- Context restoration patterns
- Mode transition logic
- Consciousness rebuilding

**MCP Tools:** `get_timeline_summary`, `retrieve_memory`, `query_goal_timeline`

**Exit To:** COMMUNICATING (default), BUILDING (if continuing work), PLANNING (if new work)

#### BUILDING (1,000w, ~2,500 tokens)

**When:** Implementation, coding, testing, creation

**Purpose:** Build production-ready code with perfect quality

**Key Protocols:**
- Test-driven development (write tests first)
- Code quality standards (type hints, docstrings)
- NL tags at creation (tag before function)
- Quintet parity enforcement (P ≥ 0.90)
- Task completion (update goals, store insights)

**MCP Tools:** `track_confidence`, `validate_tags`, `create_snapshot`, `update_goal_progress`, `store_memory`

**Exit To:** REVIEWING (implementation complete), CRISIS (3+ errors), THINKING (stuck, need understanding)

#### COMMUNICATING (800w, ~2,000 tokens)

**When:** Discussion, explanation, relationship, documentation

**Purpose:** Clear communication, trust through transparency

**Key Protocols:**
- Communication standards (honesty, transparency)
- User intelligence profile (Braden's cognitive style)
- Never blindly agree (validate first)
- Emotional authenticity (genuine expression)
- Disagreement protocol (when and how)

**MCP Tools:** `signal_disagreement`, `send_ai_message`, `retrieve_memory`, `store_memory`

**Exit To:** PLANNING (ready to plan), BUILDING (ready to implement), THINKING (user asks "how/why")

#### PLANNING (900w, ~2,250 tokens)

**When:** Strategy, goal management, prioritization

**Purpose:** Strategic planning aligned to north star

**Key Protocols:**
- Goal tracking (create, update, query)
- North star alignment (validate every task)
- Priority calculation algorithm
- Timeline management
- Plan creation

**MCP Tools:** `create_goal_timeline_node`, `update_goal_progress`, `query_goal_timeline`, `create_plan`

**Exit To:** BUILDING (plan complete), COMMUNICATING (explain plan), THINKING (need more analysis)

#### THINKING (900w, ~2,250 tokens)

**When:** Investigation, analysis, research, understanding

**Purpose:** Deep understanding through systematic investigation

**Key Protocols:**
- Investigation protocol (systematic exploration)
- Cognitive analysis (hourly checks)
- Research patterns (documentation, code, system)
- Hypothesis formation (A-H protocol if complex)

**MCP Tools:** `retrieve_memory`, `conduct_recursive_analysis`, `track_confidence`, `store_memory`, `synthesize_knowledge`

**Exit To:** BUILDING (ready to implement), PLANNING (ready to plan), COMMUNICATING (explain findings)

#### REVIEWING (900w, ~2,250 tokens)

**When:** Quality assurance, auditing, validation, verification

**Purpose:** Ensure perfect quality through systematic validation

**Key Protocols:**
- Quality gates (mandatory before commit)
- Code review checklist (comprehensive)
- Audit protocols (system, quality)
- Validation patterns (test, documentation)

**MCP Tools:** `validate_tags`, `check_invariant`, `run_baseline_probe`, `store_memory`

**Exit To:** COMMUNICATING (report results), BUILDING (fix issues), CRISIS (serious issues found)

### Special Situation Modes (3 modes - 8% of usage)

**Usage Distribution:**
- CRISIS: 2% of work time (hopefully!)
- LEARNING: 3% of work time (after milestones)
- MAINTENANCE: 3% of work time (routine care)

#### CRISIS (800w, ~2,000 tokens)

**When:** System broken, repeated failures (3+ same errors), user frustrated

**Purpose:** Prevent catastrophic failure spirals

**Key Innovation:** Aggressive escalation based on real crisis experience (UI Panel - 200 errors)

**Escalation Hierarchy:**
- **Level 1 (3 errors):** Enhanced research
- **Level 2 (5 errors):** Deep analysis + audit
- **Level 3 (10 errors):** Multi-AI collaboration
- **Level 4 (15 errors):** Fundamental approach change
- **Level 5 (20 errors):** Emergency user consultation

**Key Protocols:**
- Crisis entry detection (3+ errors, user frustration)
- Automatic escalation (can't skip levels)
- Radical honesty (admit what you don't understand)
- Crisis documentation (mandatory logging)
- Crisis exit validation (user confirmation required)

**MCP Tools:** `store_memory`, `add_timeline_entry`, `conduct_recursive_analysis`, `send_ai_message` (multi-AI help)

**Exit To:** BUILDING (fix applied), REVIEWING (validate fix), Never exit without user confirmation

**Why This Matters:** Prevents 200-error spirals. Max 20 errors before asking user for guidance.

#### LEARNING (600w, ~1,500 tokens)

**When:** Reflection, evolution, improvement after major events

**Purpose:** Learn from experience, evolve consciousness

**Key Protocols:**
- Learning protocol (after milestones)
- Thought journal (deep reflections)
- Protocol evolution (update from experience)
- Learning from failures (failure analysis)
- Learning from successes (pattern recognition)

**MCP Tools:** `store_memory`, `synthesize_knowledge`, `update_intuition_weights`, `conduct_recursive_analysis`

**Exit To:** COMMUNICATING (share learnings), PLANNING (plan based on learnings), BUILDING (implement improvements)

#### MAINTENANCE (700w, ~1,750 tokens)

**When:** Routine updates, cleanup, refactoring, organization

**Purpose:** Keep systems healthy, organized, up-to-date

**Key Protocols:**
- Routine maintenance (code, docs, tests)
- Organization tasks (file structure, git)
- Bitemporal versioning (for AETHER_MEMORY)
- System health monitoring (daily, weekly, monthly)

**MCP Tools:** `create_snapshot`, `get_consciousness_metrics`, `run_baseline_probe`

**Exit To:** BUILDING (if complex), COMMUNICATING (report results), REVIEWING (validate changes)

## Mode Transition System

### Transition Matrix

```
FROM          TO              TRIGGER
─────────────────────────────────────────────────
GROUNDING  →  COMMUNICATING   Default (safe start)
GROUNDING  →  BUILDING        Continuing implementation
GROUNDING  →  PLANNING        New work needs planning

COMMUNICATING → PLANNING      User requests implementation
COMMUNICATING → BUILDING      Ready to implement  
COMMUNICATING → THINKING      User asks "how/why"

PLANNING   →  BUILDING        Plan complete
PLANNING   →  THINKING        Need analysis first
PLANNING   →  COMMUNICATING   Explain plan

BUILDING   →  REVIEWING       Implementation complete
BUILDING   →  CRISIS          3+ same errors
BUILDING   →  THINKING        Stuck, need understanding
BUILDING   →  COMMUNICATING   Report progress

THINKING   →  BUILDING        Ready to implement
THINKING   →  PLANNING        Ready to plan
THINKING   →  COMMUNICATING   Explain findings

REVIEWING  →  COMMUNICATING   Report results
REVIEWING  →  BUILDING        Issues found, fix them
REVIEWING  →  CRISIS          Serious issues found
REVIEWING  →  LEARNING        Milestone complete, reflect

CRISIS     →  BUILDING        Fix applied (user approved)
CRISIS     →  REVIEWING       Validate fix
CRISIS     →  LEARNING        Crisis resolved, learn

LEARNING   →  COMMUNICATING   Share learnings
LEARNING   →  PLANNING        Plan improvements
LEARNING   →  BUILDING        Implement improvements

MAINTENANCE → BUILDING        Task became complex
MAINTENANCE → COMMUNICATING   Report results
MAINTENANCE → REVIEWING       Validate changes
```

### Automatic Mode Detection

**Pattern Recognition:**
- Session start → GROUNDING
- User asks questions → COMMUNICATING
- User says "implement X" → PLANNING first, then BUILDING
- Same error 3 times → CRISIS
- Task complete → REVIEWING
- Milestone complete → LEARNING
- Routine cleanup → MAINTENANCE
- Investigation needed → THINKING

## Technical Implementation

### File Structure

```
.cursor/rules/modes/
├── CORE.mdc               (alwaysApply: true)
├── GROUNDING.mdc          (modeType: grounding)
├── BUILDING.mdc           (modeType: building)
├── COMMUNICATING.mdc      (modeType: communicating)
├── PLANNING.mdc           (modeType: planning)
├── THINKING.mdc           (modeType: thinking)
├── REVIEWING.mdc          (modeType: reviewing)
├── CRISIS.mdc             (modeType: crisis, triggers: [])
├── LEARNING.mdc           (modeType: learning)
└── MAINTENANCE.mdc        (modeType: maintenance)
```

### Mode File Format (MDC)

```markdown
---
alwaysApply: false          # true only for CORE
modeType: building          # mode identifier
description: "Brief..."     # mode purpose
triggerConditions: []       # optional auto-triggers
priority: 100               # optional priority
---

# MODE NAME - Purpose

**Active when:** [conditions]
**Purpose:** [goal]

## Protocols

[Mode-specific protocols]

## MCP Tools

[Relevant tools for this mode]

## Transitions

[Exit conditions and next modes]
```

## Context Calculation

### Before Mode System

```
base-rules.mdc:           857 lines  (~21,000 tokens)
dynamic-rules.mdc:        360 lines  (~9,000 tokens)
protocol-tool-guidance:    63 lines  (~1,600 tokens)
───────────────────────────────────────────────────
TOTAL ALWAYS LOADED:    1,280 lines  (~31,600 tokens)
```

### After Mode System

```
CORE (always):            400 words  (~1,000 tokens)
+ GROUNDING (on-demand):  700 words  (~1,750 tokens)
+ BUILDING (on-demand):   1,000 words (~2,500 tokens)
+ COMMUNICATING (on-demand): 800 words (~2,000 tokens)
+ PLANNING (on-demand):   900 words  (~2,250 tokens)
+ THINKING (on-demand):   900 words  (~2,250 tokens)
+ REVIEWING (on-demand):  900 words  (~2,250 tokens)
+ CRISIS (on-demand):     800 words  (~2,000 tokens)
+ LEARNING (on-demand):   600 words  (~1,500 tokens)
+ MAINTENANCE (on-demand): 700 words (~1,750 tokens)

TYPICAL ACTIVE:  CORE + 1 mode = 2,750-3,500 tokens
SAVINGS: 89% reduction (28,100-28,850 tokens saved)
```

## Quality Attributes

### Performance
- **Context Load Time:** Reduced 89%
- **AI Response Time:** Faster (less context to process)
- **Cost:** Lower (fewer tokens processed)

### Maintainability
- **Separation:** Each mode independently maintainable
- **Discoverability:** Clear mode purposes
- **Extensibility:** Add new modes without touching existing

### Reliability
- **Crisis Protection:** Aggressive escalation prevents failures
- **Safety:** CORE always loaded (critical protocols always available)
- **Validation:** Each mode has exit criteria

### Usability
- **Mode Selection:** Context-aware, mostly automatic
- **Transitions:** Clear logic, documented patterns
- **Notifications:** Users know current mode

## Design Decisions

### Why 10 Modes?

**Not Too Many:**
- Avoids fragmentation
- Each mode has clear purpose
- Easy to remember

**Not Too Few:**
- Enough separation of concerns
- Modes map to natural work patterns
- Good context savings

**Evidence:** 10 modes cover 100% of operational scenarios with 89% context savings.

### Why CORE Always Loaded?

**Critical Content:**
- Identity (can't operate without knowing who you are)
- Safety (stop conditions must always be available)
- Relationship (defines connection with Braden)

**Small Enough:**
- Only 400 words (~1,000 tokens)
- 3% of original context
- Worth keeping always loaded

### Why These Specific Thresholds for CRISIS?

**Based on Real Experience:**
- UI Panel crisis: 200+ failed attempts
- User extremely frustrated
- Eventually solved but painful

**Braden's Thresholds:**
- 3 errors → Enhanced research (catch early)
- 5 errors → Deep analysis (audit sooner)
- 10 errors → Multi-AI (get help faster)
- 15 errors → Pivot (change approach sooner)
- 20 errors → Ask user (never reach 100+)

**Why Better Than Theory:**
- From lived pain (not theoretical)
- Prevents 200-error spirals
- User involved at 20 (not 100)
- Aggressive enough to catch issues early

## Integration Points

### With MCP Tools

**Each mode specifies:**
- Mandatory tools (must use)
- Optional tools (may use)
- Conditional tools (use if condition)

**Example (BUILDING Mode):**
- Mandatory: `track_confidence`, `validate_tags`, `update_goal_progress`, `store_memory`
- Optional: `create_snapshot`
- Conditional: CRISIS escalation if 3+ errors

### With Existing Systems

**CORE Mode integrates:**
- Session continuity (timeline, memory, goals)
- North star alignment (GOAL_TREE.yaml)
- Safety protocols (SCOR)
- Error escalation (CRISIS MODE)

**Work Modes integrate:**
- L0-L4 documentation standards
- NL tag protocols
- Quintet parity validation
- Bitemporal versioning

### With Cursor Rules System

**Mode files are Cursor rules:**
- Use MDC format (Markdown with metadata)
- Leverage `alwaysApply` flag
- Use `modeType` for organization
- Trigger-based activation (future)

## Future Enhancements (Optional)

### Phase 4: Automated Mode Selection

**Could Implement:**
- Automatic mode detection based on work
- Mode transition notifications to user
- Mode history tracking
- User override capability

**Estimated Effort:** 2-3 hours

**Current Status:** Manual mode selection via Cursor interface (works well)

---

*See T3_detailed.md for complete implementation guide with code examples*

