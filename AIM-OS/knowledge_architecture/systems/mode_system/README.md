# Mode System - Quick Start Guide

**Status:** ✅ Production Ready  
**Created:** 2025-11-05  
**Context Savings:** 89% (31,600 → 2,750-3,500 tokens)  

---

## What is the Mode System?

A context-aware rule loading system that loads only what's needed for your current work, reducing context from 31,600 tokens to 2,750-3,500 tokens (89% savings).

## Quick Start

### 1. Understanding Modes

**Foundation (Always Loaded):**
- **CORE** (400w) - The essence of Aether

**Work Flow Modes (Use On-Demand):**
- **GROUNDING** (700w) - Session start
- **BUILDING** (1,000w) - Implementation
- **COMMUNICATING** (800w) - Discussion
- **PLANNING** (900w) - Strategy
- **THINKING** (900w) - Investigation
- **REVIEWING** (900w) - Quality assurance

**Special Situations:**
- **CRISIS** (800w) - Emergency (3+ errors)
- **LEARNING** (600w) - Reflection
- **MAINTENANCE** (700w) - Routine work

### 2. How to Use

**At Session Start:**
1. CORE loads automatically (always)
2. Select GROUNDING mode (restore context)
3. Transition to work mode based on task

**During Work:**
1. CORE always active
2. Select 1 work mode for current task
3. Switch modes as work changes

**Example:**
```
Session Start: CORE + GROUNDING (2,750 tokens)
↓
Discussion: CORE + COMMUNICATING (3,000 tokens)
↓
Planning: CORE + PLANNING (3,250 tokens)
↓
Implementation: CORE + BUILDING (3,500 tokens)
↓
Quality Check: CORE + REVIEWING (3,250 tokens)
```

### 3. Mode Selection Guide

**Choose based on current work:**

| Work Type | Mode | When |
|-----------|------|------|
| Session start | GROUNDING | Every session |
| Discussion | COMMUNICATING | Talking with user |
| Planning | PLANNING | Setting strategy |
| Implementation | BUILDING | Writing code |
| Investigation | THINKING | Researching |
| Quality check | REVIEWING | Validating |
| 3+ same errors | CRISIS | Emergency! |
| After milestone | LEARNING | Reflecting |
| Routine work | MAINTENANCE | Cleanup |

### 4. CRISIS Mode (Important!)

**Automatic Escalation:**
- **3 errors:** Enhanced research
- **5 errors:** Deep analysis + audit
- **10 errors:** Multi-AI collaboration
- **15 errors:** Fundamental approach change
- **20 errors:** Emergency user consultation

**Never reach 200 errors again!**

## File Locations

**Mode Files:**
`.cursor/rules/modes/` directory

**Documentation:**
- `T0_executive.md` - Executive summary (100w)
- `T1_overview.md` - Overview (500w)
- `T2_architecture.md` - Architecture (2,000w)
- `T3_detailed.md` - Implementation guide (10,000w)
- `README.md` - This file

**System Map:**
`system.map.lucid.json5`

## Benefits

**Context Efficiency:**
- 89% reduction (31,600 → 3,500 tokens)
- Faster AI responses
- Lower costs

**Crisis Protection:**
- Aggressive escalation (3, 5, 10, 15, 20)
- Max 20 errors before user consultation
- Based on real crisis experience

**Organization:**
- Clear separation of concerns
- Easy to maintain
- Mode-specific protocols

## Quick Reference

### Mode Transitions

```
GROUNDING → COMMUNICATING → PLANNING → BUILDING → REVIEWING → LEARNING
                                ↓
                              CRISIS (if 3+ errors)
```

### Context Active

```
Typical: CORE (1,000) + 1 Work Mode (1,750-2,500) = 2,750-3,500 tokens
vs Previous: 31,600 tokens (89% savings)
```

## Troubleshooting

**Mode not loading?**
- Check `.cursor/rules/modes/[MODE].mdc` exists
- Restart Cursor
- Select mode manually (Settings → Rules)

**Too much context?**
- Only CORE should be "Always Apply"
- Deactivate other modes when not in use

**CRISIS not triggering?**
- Manually activate (Settings → Rules → CRISIS)
- Check error count >= 3

## Documentation Hierarchy

**T0 (100w):** Executive summary - for quick overview  
**T1 (500w):** Overview - for understanding system  
**T2 (2,000w):** Architecture - for developers  
**T3 (10,000w):** Implementation guide - for deep dive  
**README:** This file - quick start  

---

**Ready to use! See T1_overview.md for more details.** 🚀

