# ⚡ Quick Reference - Multi-Agent Workflow

**For:** 4 Cursor Agents + Codex  
**Purpose:** Fast reference for daily work  
**Full docs:** See MULTI_AGENT_WORKFLOW.md and CURSOR_AGENT_ONBOARDING.md

---

## 🎯 **YOUR ROLE (Cursor Agents)**

**First Pass Only:**
- Create scaffolds (~500-800 words)
- Add basic examples
- Initialize quality gates
- Hand off to Codex

**NOT Your Job:**
- ❌ Completing chapters to 100%
- ❌ Calculating quality scores
- ❌ Integrating all Tier A sources

---

## 📋 **FIRST PASS CHECKLIST**

**For Each Chapter:**
1. ✅ Pre-flight checks (deps, Tier A, VIF)
2. ✅ Create chapter.md (~500-800 words)
3. ✅ Add basic runnable examples
4. ✅ Create evidence.jsonl (initial citations)
5. ✅ Create metrics.yaml (gates initialized)
6. ✅ Send handoff message to Codex

**Time:** ~30-60 minutes per chapter

---

## 🚨 **CRITICAL: QUALITY METRICS, NOT WORD COUNTS**

**❌ WRONG:**
"Ch01: 1,840/2,000 words (needs ~160 more)"

**✅ CORRECT:**
"Ch01: Scaffold complete, quality scores pending, ready for second pass"

**Quality Gates (from gates.json):**
- Relevance Score (≥ 0.85 for Tier B)
- Density Score (≥ 0.80 for Tier B)
- Completion Score (≥ 0.85 for Tier B)
- Thoroughness Checklist (≥ 0.85)

**Codex calculates these - you just initialize them as "pending"**

---

## 📊 **CHAPTER ASSIGNMENTS**

**Max:** Part I (Ch01-Ch04) - Wave 1
**Lex:** Part II (Ch05-Ch10) - Foundation
**Sam:** Part III (Ch11-Ch15) - Consciousness
**Dac:** Part IV-VII (Ch16-Ch40) - Authority + Math + Builder + Reference

**Codex:** Second pass on all chapters (expansion + integration)

---

## 💬 **COMMUNICATION**

**Status Updates:**
- Post to `coordination/epic_standards_overhaul/comms/SHARED_MESSAGE_BOARD.md`
- Format: `### 2025-11-06 - Agent Name (Status)`

**Handoffs:**
- Use MCP `send_ai_message` tool
- Thread ID: `north-star-orchestration-2025-11-06`

**Questions:**
- Ask in message board
- Don't block on questions

---

## ✅ **SUCCESS = CLEAN HANDOFF**

**First Pass Success:**
- ✅ Scaffold created
- ✅ Basic examples added
- ✅ Quality gates initialized
- ✅ Ready for Codex

**NOT Success:**
- ❌ Word count hits target
- ❌ Chapter 100% complete
- ❌ Quality scores calculated

---

## 📚 **ESSENTIAL FILES**

- `MULTI_AGENT_WORKFLOW.md` - Complete workflow
- `CURSOR_AGENT_ONBOARDING.md` - Full onboarding
- `gates.json` - Quality gate definitions
- `ChainSpec.yaml` - Chapter specifications
- `NORTH_STAR_INTEGRATION_VALIDATION.md` - Integration guide

---

**Status:** ✅ **READY FOR 4 AGENTS**  
**Workflow:** 3-Pass System (You = First Pass)  
**Goal:** Fast scaffolds, clean handoffs

