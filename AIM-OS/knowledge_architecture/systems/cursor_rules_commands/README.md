# Cursor Rules & Commands System

**Purpose:** Cursor 2.0's AI context management and workflow automation for AIM-OS  
**Status:** Production Ready ✅  
**Created:** 2025-11-05  
**Author:** Aether  

---

## Quick Start

### Understanding the System

**Read this first:**
- **T0 (100w):** `T0_executive.md` - Quick summary
- **T1 (500w):** `T1_overview.md` - Overview
- **T2 (2,000w):** `T2_architecture.md` - Architecture
- **T3 (10,000w):** `T3_detailed.md` - Implementation guide

### Using Rules

**Active Rules:**
- `base-rules.mdc` - Always applied (essential requirements)
- `dynamic-rules.mdc` - Agent requested (context-aware)

**Location:** `.cursor/rules/`

### Using Commands

**Try these commands in Cursor chat:**
- `/run-tests` - Run test suite
- `/create-t0-t4-docs` - Generate documentation
- `/fix-nl-tags` - Auto-tag code
- `/audit-system` - Comprehensive audit

**All commands:** `.cursor/commands/` (12 total)

---

## What This System Provides

### Rules (Persistent AI Context)

**4 Rule Types:**
1. **Always** - Loaded every conversation
2. **Auto-Attached** - Based on file patterns
3. **Agent Requested** - AI decides relevance
4. **Manual** - Explicit @mention only

**Benefits:**
- Consistent AI behavior
- Optimal token usage
- Context-aware guidance
- Quality enforcement

### Commands (Workflow Automation)

**12 Core Commands:**

**Documentation:**
- `/create-t0-t4-docs` - Generate T0-T4 stack
- `/update-super-index` - Update master index
- `/validate-docs` - Check documentation standards

**Development:**
- `/run-tests` - Execute test suite
- `/fix-nl-tags` - Auto-tag code
- `/code-review` - Quality review
- `/fix-linter` - Fix linter errors

**System:**
- `/audit-system` - Comprehensive audit
- `/create-system` - New system creation
- `/validate-quintet` - Check parity

**Memory:**
- `/create-decision-log` - Decision documentation
- `/create-thought-journal` - Reflection entry
- `/update-goal-tree` - Progress tracking

**Benefits:**
- One-touch complex workflows
- Standardized execution
- Time savings (50-95% per task)
- Quality consistency

---

## Documentation Hierarchy

```
systems/cursor_rules_commands/
├── README.md (this file)
├── T0_executive.md (100w summary)
├── T1_overview.md (500w overview)
├── T2_architecture.md (2,000w architecture)
├── T3_detailed.md (10,000w implementation)
└── system.map.lucid.json5 (system map)
```

---

## A-H Protocol Documentation

**Investigation following A-H protocol:**

```
knowledge_architecture/ah_protocol/cursor_rules_commands_investigation/
├── A_intent.md - Intent capture
├── B_hypothesis.md - Hypothesis formation
├── C_context.md - Context mapping
├── D_del.md - Deep expansion layer
├── E_cmm.md - Context mesh map
├── F_confidence.md - Confidence-gated mutation
├── G_implementation.md - Implementation
└── H_audit.md - Audit and memory
```

---

## Integration

**With AIM-OS Systems:**
- CMC - Storage for outputs
- HHNI - Knowledge retrieval
- VIF - Confidence tracking
- APOE - Workflow orchestration
- SDF-CVF - Quality enforcement

**With Scripts:**
- 83 automation scripts
- Direct integration via commands

**With MCP Tools:**
- 59 tools available
- Commands execute tools
- Rules guide tool usage

---

## Current Status

**Deployed:**
- ✅ 2 active rules (base, dynamic)
- ✅ 12 core commands
- ✅ Archive disabled
- ✅ T0-T3 documentation

**Metrics:**
- Token reduction: Est. 30-40%
- Time savings: Est. 50-95% per workflow
- Quality improvement: TBD (2 weeks)

**Confidence:** 0.95 (production-ready)

---

## Next Steps

1. **Create additional glob-based rules** (Python, TypeScript specific)
2. **Add specialized commands** (deployment, security, etc.)
3. **Monitor effectiveness** (2-4 weeks)
4. **Iterate based on usage** data

---

**Start with:** T0_executive.md → Progress to deeper levels as needed

**For implementation:** Read T3_detailed.md

**For questions:** Check T2_architecture.md first

