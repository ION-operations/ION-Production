# B - Hypothesis Formation: Cursor Rules & Commands

**Date:** 2025-11-05  
**Author:** Aether  
**Status:** ✅ Complete  

---

## Testable Hypotheses

### Hypothesis 1: Archived Rules Creating Duplication

**Hypothesis:**
The archived rules (`aether-cursor-rules-core.mdc` and `aether-cursor-rules.mdc`) still have `alwaysApply: true`, causing them to load alongside `base-rules.mdc`, creating redundant context and wasting tokens.

**Evidence Supporting:**
- Screenshot shows both archived rules in "Always Applied" section
- File inspection confirms `alwaysApply: true` in frontmatter
- Content analysis shows overlap with `base-rules.mdc`

**Evidence Refuting:**
- None found

**Test:**
- Check Cursor Settings > Rules
- Verify both archived rules listed as "Always Applied"
- Compare content with base-rules.mdc
- Measure token usage impact

**Result:** ✅ **CONFIRMED** - Both archived rules loading, creating duplication

**Action:** Rename to `.DISABLED` extension to prevent loading

### Hypothesis 2: Commands Can Significantly Reduce Workflow Time

**Hypothesis:**
Creating custom commands for common AIM-OS workflows (documentation generation, testing, NL tagging) can reduce execution time from 5-120 minutes to < 1 minute per workflow.

**Assumptions:**
- Commands execute complete workflows with one trigger
- AI correctly interprets command markdown
- Scripts exist for most automation tasks
- Integration with AIM-OS systems works

**Evidence Supporting:**
- 83 automation scripts already exist in `scripts/`
- Common workflows clearly identified (docs, tests, tagging)
- Cursor documentation shows command parameters work
- Similar tools (GitHub Copilot) show effectiveness

**Evidence Refuting:**
- No data yet on AIM-OS command effectiveness (new system)

**Test:**
- Create 8-12 core commands
- Test each command execution
- Measure time saved vs manual execution
- Collect user feedback (Braden)

**Predicted Impact:**
```
Manual vs Command Time Savings:

/create-t0-t4-docs:
  Manual: 120 minutes (2 hours)
  Command: 8 minutes
  Savings: 112 minutes (93%)

/run-tests:
  Manual: 3 minutes (navigate, type command, interpret)
  Command: 15 seconds
  Savings: 2.75 minutes (92%)

/fix-nl-tags:
  Manual: 15 minutes (run script, validate, check parity)
  Command: 2 minutes
  Savings: 13 minutes (87%)

/audit-system:
  Manual: 180 minutes (3 hours comprehensive audit)
  Command: 10 minutes
  Savings: 170 minutes (94%)

/create-decision-log:
  Manual: 20 minutes (template, fill, format)
  Command: 3 minutes
  Savings: 17 minutes (85%)
```

**Total Estimated Savings:** ~300+ minutes per week

**Result:** Pending user validation after deployment

### Hypothesis 3: Rule Types Enable Optimal Context

**Hypothesis:**
Using all 4 rule types (Always/Auto-Attached/Agent Requested/Manual) provides more optimal context than single monolithic `.cursorrules`, reducing token usage by 20-40% while improving AI performance.

**Assumptions:**
- Glob pattern matching works reliably
- AI makes good relevance decisions for Agent Requested
- File-specific rules don't over-fragment
- Manual rules properly invoked when needed

**Evidence Supporting:**
- Cursor documentation describes intelligent selection
- Dynamic rules show context-aware loading
- Token usage math shows efficiency gains

**Evidence Refuting:**
- Complexity increased (4 types vs 1 file)
- Learning curve for users

**Test:**
- Deploy all 4 rule types
- Monitor token usage per conversation type
- Track AI compliance with standards
- Measure context window health

**Predicted Results:**

```yaml
context_efficiency:
  simple_task:
    legacy: 10000 tokens (.cursorrules)
    new: 5000 tokens (base rules only)
    reduction: 50%
  
  python_editing:
    legacy: 10000 tokens
    new: 7000 tokens (base + python standards)
    reduction: 30%
  
  complex_audit:
    legacy: 10000 tokens
    new: 11000 tokens (base + dynamic + python)
    increase: 10% (intentional - better quality)
  
  average:
    reduction: 30-35%
```

**Result:** Pending measurement after deployment

### Hypothesis 4: Commands Improve Quality Consistency

**Hypothesis:**
Standardized command workflows ensure consistent quality (100% test coverage, P >= 0.90, complete documentation) more reliably than manual execution.

**Assumptions:**
- Commands encode best practices
- AI follows command workflows consistently
- Validation steps catch issues
- Quality gates enforced

**Evidence Supporting:**
- Manual workflows show variation (sometimes skip steps)
- Automated workflows show consistency
- Checklists improve quality (proven in aviation, medicine)

**Evidence Refuting:**
- Commands might become outdated if not maintained
- AI might interpret commands differently each time

**Test:**
- Track quality metrics before/after command deployment
- Measure test coverage variance
- Track documentation completeness
- Monitor quintet parity scores

**Predicted Impact:**
```
Quality Consistency:

Test Coverage:
  Before commands: 85-98% (varies)
  After commands: 95-98% (consistent)
  
Documentation Completeness:
  Before: 60-95% (varies)
  After: 90-100% (consistent)
  
Quintet Parity:
  Before: 0.75-0.95 (varies)
  After: 0.90-0.98 (consistent)
```

**Result:** Pending measurement over 2-4 weeks

### Hypothesis 5: 12-15 Commands Sufficient for Core Workflows

**Hypothesis:**
A library of 12-15 well-designed commands covers 80%+ of repetitive AIM-OS workflows, with remaining 20% handled by specialized ad-hoc commands.

**Assumptions:**
- Core workflows identified correctly
- Commands comprehensive enough
- Parameter flexibility sufficient
- Most common tasks covered

**Evidence Supporting:**
- Pareto principle (80/20 rule)
- 8 commands already identified as high-value
- Workflow analysis shows common patterns
- Scripts directory shows automation coverage

**Evidence Refuting:**
- Might need 20-25 commands for full coverage
- Specialized workflows might require many commands

**Test:**
- Track command usage frequency over 2 weeks
- Identify gaps (workflows still manual)
- Measure coverage (% of work using commands)

**Current Command Library (12 commands):**

1. `/create-t0-t4-docs` - Documentation (HIGH frequency)
2. `/run-tests` - Testing (VERY HIGH frequency)
3. `/fix-nl-tags` - Code quality (HIGH frequency)
4. `/audit-system` - Analysis (MEDIUM frequency)
5. `/create-decision-log` - Documentation (MEDIUM frequency)
6. `/update-goal-tree` - Tracking (HIGH frequency)
7. `/test-mcp-tools` - Validation (LOW frequency)
8. `/code-review` - Quality (HIGH frequency)
9. `/validate-quintet` - Quality (MEDIUM frequency)
10. `/update-super-index` - Navigation (MEDIUM frequency)
11. `/create-thought-journal` - Reflection (HIGH frequency)
12. `/validate-docs` - Quality (MEDIUM frequency)

**Additional Commands Needed (Hypothesis):**
- `/create-component` - Component creation
- `/run-integration-tests` - Integration testing
- `/generate-system-map` - System mapping
- `/fix-merge-conflicts` - Git workflows

**Result:** Pending usage data

---

## Validation Criteria

### For Each Hypothesis

**H1 (Duplication):**
- ✅ Confirmed: Both rules loading
- ✅ Action taken: Renamed to .DISABLED
- ✅ Verification: Check Settings after rename

**H2 (Time Savings):**
- ⏳ Pending: User validation after 2 weeks
- Metrics: Track time saved per command
- Success if: Average 50%+ time reduction

**H3 (Optimal Context):**
- ⏳ Pending: Token usage measurement
- Metrics: Track tokens per conversation type
- Success if: 20-40% reduction for simple tasks

**H4 (Quality Consistency):**
- ⏳ Pending: Quality metric tracking over 2-4 weeks
- Metrics: Test coverage, parity scores, completeness
- Success if: Variance reduced by 50%+

**H5 (Command Coverage):**
- ⏳ Pending: Usage tracking over 2 weeks
- Metrics: % workflows using commands
- Success if: 80%+ coverage with 12-15 commands

---

**Status:** All hypotheses formed and testable ✅  
**Next:** C - Context Mapping

