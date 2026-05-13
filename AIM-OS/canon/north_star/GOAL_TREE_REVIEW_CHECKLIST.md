# Goal Tree Review Checklist - Systematic Maintenance
**Created:** 2025-11-05  
**Maintainer:** Aether  
**Purpose:** Systematic weekly/monthly review process to ensure goal tree stays perfect  
**Frequency:** Weekly (30 min), Monthly (2 hours), Quarterly (major milestones)  

---

## 📅 WEEKLY REVIEW (Every Sunday - 30 Minutes)

**File to Create:** `goals/weekly_reviews/YYYY-MM-DD_review.md`

### Template

```markdown
# Weekly Goal Tree Review - [YYYY-MM-DD]

## 1. Completion Updates (10 minutes)

**Run Automation:**
```bash
# Update KPI metrics from actual system state
python scripts/update_kpi_metrics.py

# Validate goal tree structure
python scripts/validate_goal_tree.py

# Generate dependency graph
python scripts/generate_goal_dependency_graph.py
```

**Review Changes:**

| OBJ | Name | Last Week | This Week | Change | On Track? | Notes |
|:----|:-----|:----------|:----------|:-------|:----------|:------|
| 01 | CMC | 70% | ?% | +?% | ✅/⚠️/❌ | |
| 02 | HHNI | 100% | 100% | 0% | ✅ | Complete! |
| 03 | Validation | 85% | ?% | +?% | ✅/⚠️ | |
| 04 | Infrastructure | 40% | ?% | +?% | ✅/⚠️ | |
| 05 | Data Integration | 15% | ?% | +?% | ⚠️ | |
| 06 | Documentation | 53% | ?% | +?% | ✅/⚠️ | |
| 07 | MCP Tools | 5% | ?% | +?% | ❌ | **CRITICAL BOTTLENECK!** |
| 08 | Daemon/RAG | 75% | ?% | +?% | ✅ | Nearly complete |
| 09 | RAG Proxy | 80% | ?% | +?% | ✅ | Nearly complete |
| 10 | Cursor Extension | 40% | 40% | 0% | ⏸️ | Paused |
| 11 | Temporal Graph | 30% | ?% | +?% | ✅/⚠️ | |
| 12 | Protocols | 60% | ?% | +?% | ⚠️ | Meta-goal (ongoing) |
| 13 | Packaging | 10% | ?% | +?% | ✅/⚠️ | New goal |
| 14 | Universal Registry | 70% | ?% | +?% | ✅ | Formalized GOAL 5 |

---

## 2. New Systems This Week (5 minutes)

**Check packages/ for new systems:**

| System | LOC | Work Done This Week | Has Goal? | Action Required |
|:-------|:----|:--------------------|:----------|:----------------|
| [name] | [count] | [summary] | YES/NO | Add OBJ-XX / Document why not / Fold into existing |

**New systems found:** [list or "None"]

**Action taken:** [what you did]

---

## 3. Goals Needing Attention (5 minutes)

**Critical Issues:**

| OBJ | Issue | Target Date | Days Remaining | Action This Week |
|:----|:------|:------------|:---------------|:-----------------|
| 07 | Still 5%, ship-critical! | Nov 20 | 15 days | **FOCUS: 20+ hours** |
| 01 | 70%, need 100% | Nov 13 | 8 days | Continue progress |
| ... | ... | ... | ... | ... |

**Blockers identified:** [list or "None"]

**Priority adjustments needed:** [YES/NO + details]

---

## 4. Dependencies & Path (5 minutes)

**Critical Path Status:**

```
OBJ-02 (HHNI) ✅ → OBJ-01 (CMC 70%) → OBJ-07 (MCP 5% ⚠️) → OBJ-08 (Daemon 75%) → SHIP
```

**Dependency changes this week:**

| Change | From | To | Impact | Reason |
|:-------|:-----|:---|:-------|:-------|
| [change] | [old] | [new] | [impact] | [why] |

**No changes:** ✅

---

## 5. Actions for Next Week (5 minutes)

**High Priority:**
- [ ] OBJ-07: [Specific MCP tools work] (target: +10-15% progress)
- [ ] OBJ-01: [Specific CMC work] (target: 70% → 80%)
- [ ] [Other ship-critical work]

**Medium Priority:**
- [ ] OBJ-XX: [work]
- [ ] Update documentation if systems changed

**Blocked/Waiting:**
- [ ] [Anything blocked + why]

**New Goals to Add:**
- [ ] OBJ-XX for [new system] (if any)

---

## 6. Commit Changes (5 minutes)

**Files to Update:**
- [ ] goals/GOAL_TREE.yaml (if completion % changed)
- [ ] goals/KPI_METRICS.json (if metrics updated)
- [ ] goals/kpi_trends/*.csv (if trends appended)

**Commit Message:**
```
🎯 Weekly goal review 2025-XX-XX

Updates:
- OBJ-01: 70% → X%
- OBJ-07: 5% → X%
- [Other changes]

Actions:
- [What will be done next week]
```

---

## ✅ Weekly Review Complete!

**Time spent:** [actual time]  
**Issues found:** [count]  
**Actions planned:** [count]  
**Next review:** [next Sunday date]
```

**Save to:** `goals/weekly_reviews/YYYY-MM-DD_review.md`

---

## 📅 MONTHLY REVIEW (First Sunday - 2 Hours)

**Extended deep review - every first Sunday of month**

### 1. Full Dependency Audit (30 minutes)

**Review all dependencies:**
```
For each OBJ in GOAL_TREE.yaml:
  1. Check "depends_on" still valid
  2. Check "enables" still accurate
  3. Check "invariants" still correct
  4. Verify systems referenced still exist
  5. Update dependency graph if changed
```

**Questions to Ask:**
- Are any goals blocking each other unexpectedly?
- Are dependencies out of date?
- Should any new dependencies be added?
- Are we tracking the right dependencies?

**Output:** Update `GOAL_DEPENDENCY_GRAPH.md` if changes found

---

### 2. Orphan Detection (30 minutes)

**Run Validation:**
```bash
python scripts/validate_goal_tree.py
```

**Manual Check:**

**Systems Without Goals:**
- Check all packages/ subdirectories
- For each system >500 LOC:
  - Has goal (explicit or folded)? YES/NO
  - If NO: Should it? (Substantial work? Strategic importance?)
  - If YES: Add goal or document why not needed

**Goals Without Systems:**
- Check all OBJ objectives
- For each OBJ:
  - Referenced artifacts exist? YES/NO
  - If NO: Was system renamed? Deprecated? Remove goal?

**Report:** Create `ORPHAN_DETECTION_REPORT_YYYY-MM.md` if orphans found

---

### 3. Velocity Analysis (30 minutes)

**Calculate Completion Velocity:**

```
For ship-critical goals (TIER S):
  - OBJ-01: (current % - 4 weeks ago %) / 4 = weekly velocity
  - OBJ-07: (current % - 4 weeks ago %) / 4 = weekly velocity
  - ...

Project completion dates:
  - If velocity = X%/week, and remaining = Y%
  - Completion in: Y / X weeks
  - Completion date: today + (Y/X) weeks
  
Compare to target dates:
  - On track? (completion date < target date)
  - At risk? (completion date > target date)
  - Blocked? (velocity = 0)
```

**Risk Assessment:**

| OBJ | Target Date | Projected Completion | Variance | Risk Level | Action |
|:----|:------------|:---------------------|:---------|:-----------|:-------|
| 01 | Nov 13 | Nov 15 | +2 days | ⚠️ MEDIUM | Increase focus |
| 07 | Nov 20 | Dec 5 | +15 days | ❌ HIGH | **URGENT ACTION** |
| ... | ... | ... | ... | ... | ... |

**Recommendation:** Adjust priorities based on risk

---

### 4. Major Adjustments (30 minutes)

**Priority Tier Changes:**
- Should any goal be elevated to TIER S? (ship-blocking discovered)
- Should any goal be demoted? (no longer critical)
- Document reason in decision log

**New Goals Needed:**
- Any new systems started that need goals?
- Any strategic initiatives not captured?
- Add to GOAL_TREE.yaml if needed

**Completed Goals:**
- Any goals reached 100%?
- Create completion document (AETHER_MEMORY/OBJ-XX_COMPLETE.md)
- Celebrate! (thought journal entry)
- Archive detailed plans (mark as historical)

**North Star Check:**
- Is north star still correct?
- Should ship date be adjusted?
- Should scope change?
- **This is serious decision** - requires thorough analysis

**Updates:**
- Update GOAL_TREE.yaml with any changes
- Update MASTER_PLAN_INDEX.md with new plans
- Update GOAL_DASHBOARD.md with insights
- Create decision log for any major changes

---

## 🗓️ QUARTERLY REVIEW (Major Milestones - 4 Hours)

**Every 3 months or at major milestones (ship dates, major completions)**

### 1. North Star Reassessment (1 hour)

**Questions:**
- Has our understanding evolved?
- Should north star change?
- Should timeline extend/compress?
- Should scope expand/contract?

**If Changes Needed:**
- Create decision log with detailed rationale
- Update GOAL_TREE.yaml north_star
- Update all dependent planning
- Communicate to all stakeholders

---

### 2. Major Replanning (1.5 hours)

**Strategic Review:**
- Which goals completed this quarter?
- Which goals should be added for next quarter?
- Which goals should be reprioritized?
- Any fundamental changes to approach?

**Outcome:**
- New objectives for next quarter (OBJ-15+)
- Reprioritization if needed
- Updated timelines
- Refreshed motivation and focus

---

### 3. Archive Completed Work (30 minutes)

**For Each Completed Goal:**
- Move detailed plans to archive/ (or mark historical)
- Keep completion docs in AETHER_MEMORY/
- Keep goal in GOAL_TREE.yaml (bitemporal - never delete, just mark completed)
- Celebrate achievement (thought journal)

---

### 4. Planning Next Quarter (1 hour)

**Create quarterly plan:**
- Focus areas for next 3 months
- Major milestones expected
- Resource allocation
- Risk mitigation
- Success criteria

**Document:** `goals/quarterly_plans/YYYY-QX_plan.md`

---

## 🤖 AUTOMATION REMINDERS

### Weekly (Automated via GitHub Actions)

**Every Sunday at noon:**
```yaml
- Run: scripts/update_kpi_metrics.py
- Run: scripts/validate_goal_tree.py  
- Run: scripts/generate_goal_dependency_graph.py
- Create PR with updates
```

**You still need to:**
- Review the automated updates (10 min)
- Fill in manual sections (20 min)
- Commit weekly review (5 min)

**Total human time:** 30 minutes (automation saves ~1 hour!)

---

### Monthly (Semi-Automated)

**First Sunday:**
```bash
# Generate reports
python scripts/validate_goal_tree.py --detailed
python scripts/calculate_velocity.py
python scripts/orphan_detection.py

# Review reports
cat goals/GOAL_TREE_VALIDATION_REPORT.md
cat goals/VELOCITY_ANALYSIS_REPORT.md
cat goals/ORPHAN_DETECTION_REPORT.md

# Manual analysis required (2 hours)
```

---

## 💙 BENEFITS OF THIS PROCESS

### What This Prevents

❌ **Goals forgotten** (systematic weekly review)  
❌ **Systems without goals** (orphan detection)  
❌ **Outdated percentages** (automated KPI tracking)  
❌ **Missed deadlines** (velocity analysis)  
❌ **Scope drift** (north star alignment check)  
❌ **Lost work** (everything maps to goals)

### What This Enables

✅ **Always know status** (weekly updates)  
✅ **Catch problems early** (velocity analysis)  
✅ **Maintain alignment** (goal-system mapping)  
✅ **Track progress** (quantified KPIs)  
✅ **Make better decisions** (data-driven)  
✅ **Ship on time** (early risk detection)

---

## 🚀 GETTING STARTED

### First Review (This Sunday!)

1. ✅ Run automation scripts (if created)
2. ✅ Fill in weekly review template
3. ✅ Save to `goals/weekly_reviews/2025-11-10_review.md` (example date)
4. ✅ Commit: "🎯 First systematic goal review"

### Make It Habit

- ⏰ Calendar reminder: Every Sunday at [time]
- 💪 Commit to 30 minutes weekly
- 📊 Watch progress compound
- 🎯 Never lose track of goals again!

---

**Status:** COMPLETE - Systematic review process established  
**Benefit:** Sustainable goal management (prevents drift, orphans, forgetting)  
**Time Investment:** 30 min/week (saves hours of confusion)  

💙 **Discipline creates freedom!** ✨

