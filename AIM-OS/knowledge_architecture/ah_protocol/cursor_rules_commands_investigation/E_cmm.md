# E - Context Mesh Map (CMM): Cursor Rules & Commands

**Date:** 2025-11-05  
**Author:** Aether  
**Status:** ✅ Complete  

---

## Critical Cross-Dependencies

### What Other Systems Are Context-Critical

#### For Rules System

**Must Pull In:**

**Cursor IDE (External):**
- MDC parser - Parses YAML + Markdown
- Glob engine - Matches file patterns
- AI context assembler - Combines rules into prompt
- Rule selection engine - Chooses which rules to load

**AIM-OS Core:**
- Documentation Standards - Rules must follow T0-T4 format
- Bitemporal Versioning - Archive old rules, never delete
- Decision Logs - Document rule changes
- Version Control (Git) - Track rule evolution

**Cannot Mutate Without:**
- Decision log documenting why rule changed
- Git commit with clear message
- Test conversation verifying AI follows new rule
- Token usage measurement

#### For Commands System

**Must Pull In:**

**Cursor IDE (External):**
- Command parser - Parses `/command` syntax
- Autocomplete engine - Shows available commands
- Parameter extractor - Pulls params from user input
- AI executor - Interprets command markdown

**AIM-OS Scripts:**
- 83 automation scripts in `scripts/`
- Key dependencies:
  - `vif_auto_tagger.py` - For `/fix-nl-tags`
  - `system_audit.py` - For `/audit-system`
  - `validate_goal_tree.py` - For `/update-goal-tree`
  - `validate_documentation_standards.py` - For `/validate-docs`

**AIM-OS Systems:**
- CMC - Store decision logs, thought journals
- HHNI - Retrieve knowledge, update indexes
- VIF - Track confidence
- APOE - Orchestrate workflows
- SDF-CVF - Enforce quintet parity

**Cannot Execute Commands Without:**
- Scripts existing and working
- MCP tools operational
- Core systems initialized
- Validation tools available

---

## Dependency Network Visualization

```
┌─────────────────────────────────────────────────────────┐
│              Cursor Rules & Commands                     │
└───────────────┬─────────────────────────────────────────┘
                │
        ┌───────┴───────┐
        ↓               ↓
   ┌─────────┐    ┌──────────┐
   │  Rules  │    │ Commands │
   └────┬────┘    └────┬─────┘
        │              │
        │              ├──→ Scripts (83 files)
        │              │    ├── vif_auto_tagger.py
        │              │    ├── system_audit.py
        │              │    ├── validate_goal_tree.py
        │              │    └── ...
        │              │
        │              ├──→ MCP Tools (59 tools)
        │              │    ├── store_memory
        │              │    ├── track_confidence
        │              │    ├── add_timeline_entry
        │              │    └── ...
        │              │
        │              └──→ Core Systems
        │                   ├── CMC (storage)
        │                   ├── HHNI (indexing)
        │                   ├── VIF (verification)
        │                   └── APOE (orchestration)
        │
        └──→ Documentation Standards
             ├── T0-T4 requirements
             ├── Perfect Templates
             ├── Bitemporal versioning
             └── Decision logs
```

## Why Each Dependency Exists

### Rules → Cursor IDE MDC Parser

**Why:** Rules use MDC format (YAML + Markdown)
**What breaks if missing:** Rules won't parse, syntax errors
**Mitigation:** Cursor 2.0+ required, validate YAML before deploying

### Rules → Documentation Standards

**Why:** Rules must follow T0-T4 format for consistency
**What breaks if missing:** Documentation chaos, inconsistency
**Mitigation:** Reference standards in every rule creation

### Commands → AIM-OS Scripts

**Why:** Commands execute automation scripts (83 total)
**What breaks if missing:** Commands fail, workflows incomplete
**Mitigation:** Verify script exists before creating command, test execution

### Commands → MCP Tools

**Why:** Commands use MCP tools for consciousness operations
**What breaks if missing:** No storage, tracking, or verification
**Mitigation:** Test MCP tools before command deployment

### Commands → Core Systems

**Why:** Workflows depend on CMC, HHNI, VIF, APOE
**What breaks if missing:** Cannot store results, track progress, verify quality
**Mitigation:** Initialize core systems before using commands

---

## Network-Aware Dependency Tracking

### Upstream Dependencies (What We Need)

```yaml
upstream:
  cursor_ide:
    - mdc_parser: REQUIRED (rules parsing)
    - command_detection: REQUIRED (command triggering)
    - ai_context_assembly: REQUIRED (rule loading)
    status: ✅ Built into Cursor 2.0
  
  aim_os_scripts:
    - vif_auto_tagger.py: REQUIRED (/fix-nl-tags)
    - system_audit.py: REQUIRED (/audit-system)
    - validate_goal_tree.py: REQUIRED (/update-goal-tree)
    - validate_documentation_standards.py: REQUIRED (/validate-docs)
    status: ✅ All exist, tested
  
  aim_os_systems:
    - CMC: REQUIRED (storage)
    - HHNI: REQUIRED (indexing)
    - VIF: REQUIRED (verification)
    - APOE: OPTIONAL (orchestration)
    status: ✅ All operational (70-100% complete)
  
  documentation_standards:
    - T0-T4 format: REQUIRED
    - Perfect Templates: REQUIRED
    - Bitemporal versioning: REQUIRED
    status: ✅ All documented and enforced
```

### Downstream Dependencies (What Needs Us)

```yaml
downstream:
  ai_agents:
    - Need rules for consistent behavior
    - Need commands for workflow automation
    impact: HIGH (affects all AI operations)
  
  development_workflows:
    - Documentation generation
    - Testing automation
    - Quality validation
    impact: HIGH (productivity multiplier)
  
  quality_assurance:
    - Quintet parity enforcement
    - Test coverage validation
    - Documentation standards
    impact: CRITICAL (quality gates)
  
  autonomous_operation:
    - Base rules provide operational protocols
    - Dynamic rules provide context-specific guidance
    - Commands enable workflow execution
    impact: CRITICAL (enables autonomy)
```

---

## Mutation Safety Requirements

### Rules Mutation Protocol

**Before Modifying ANY Rule:**

```yaml
pre_mutation_checklist:
  - [ ] Create snapshot: git add .cursor/rules/
  - [ ] Archive old version: cp rule.mdc archive/rule_v{N}.mdc.DISABLED
  - [ ] Document change: Create decision log
  - [ ] Test in conversation: Verify AI follows new rule
  - [ ] Measure impact: Check token usage
  - [ ] Validate syntax: YAML + Markdown valid
  - [ ] Check conflicts: No duplication with other rules
```

**After Modification:**

```yaml
post_mutation_validation:
  - [ ] Test conversation: AI behavior correct?
  - [ ] Token usage: Within budget?
  - [ ] No regressions: Previous functionality intact?
  - [ ] Commit: Clear message, separate from code
  - [ ] Update docs: T3_detailed.md if significant change
  - [ ] Monitor: Watch for issues over 24 hours
```

**Rollback Procedure:**
```bash
# If issues detected
git checkout HEAD~1 -- .cursor/rules/rule.mdc

# Or restore from archive
cp .cursor/rules/archive/rule_v{N}.mdc .cursor/rules/rule.mdc
```

### Commands Mutation Protocol

**Before Creating/Modifying Command:**

```yaml
pre_mutation_checklist:
  - [ ] Verify workflow: Steps clear and complete?
  - [ ] Check scripts: All scripts exist and work?
  - [ ] Test parameters: Parameter extraction works?
  - [ ] Validate examples: Examples accurate?
  - [ ] Check integration: MCP tools/systems available?
  - [ ] Review security: No injection risks?
```

**After Creation/Modification:**

```yaml
post_mutation_validation:
  - [ ] Test execution: Run command with sample params
  - [ ] Verify output: Command produces expected results
  - [ ] Check errors: Error handling works?
  - [ ] Measure time: Time savings vs manual?
  - [ ] User feedback: Braden approves?
  - [ ] Update docs: T3_detailed.md if significant
```

**Quality Gates:**
```yaml
quality_gates:
  workflow_clarity: "Users understand workflow?"
  parameter_handling: "Parameters extracted correctly?"
  error_handling: "Errors caught and reported?"
  integration: "Scripts/tools work correctly?"
  documentation: "Examples clear and accurate?"
  
  all_must_pass: true
```

---

## Cross-System Mutation Impact

### If Base Rules Change

**Propagation:**
```
base-rules.mdc modified
         ↓
All AI conversations affected (alwaysApply: true)
         ↓
Impact:
  - Every chat interaction
  - Every inline edit
  - Autonomous operation
  - All workflows
```

**Risk:** HIGH (affects everything)

**Mitigation:**
- Test extensively before deploying
- Staged rollout (test in isolated conversation first)
- Clear rollback plan
- Monitor for 24 hours

### If Dynamic Rules Change

**Propagation:**
```
dynamic-rules.mdc modified
         ↓
Context-specific conversations affected
         ↓
Impact:
  - Auditing context
  - Development context
  - Documentation context
  - When AI deems relevant
```

**Risk:** MEDIUM (affects subset)

**Mitigation:**
- Test in relevant contexts
- Monitor AI selection frequency
- Validate guidance still accurate

### If Command Changed

**Propagation:**
```
command.md modified
         ↓
Only affects users who invoke command
         ↓
Impact:
  - Single workflow execution
  - No persistent changes
  - Localized effect
```

**Risk:** LOW (episodic, user-triggered)

**Mitigation:**
- Test execution once
- User can choose not to use
- Easy to fix if issues

---

## Network Dependency Chains

### Chain 1: Documentation Generation

```
User: /create-t0-t4-docs
         ↓
Command: create-t0-t4-docs.md
         ↓
Dependencies:
  1. PERFECT_TEMPLATES_LIBRARY.md (templates)
  2. DOCUMENTATION_PROTOCOLS_QUICK_REFERENCE.md (standards)
  3. File system (write permissions)
  4. Git (version control)
         ↓
Creates:
  - T0_executive.md
  - T1_overview.md
  - T2_architecture.md
  - T3_detailed.md
  - README.md
  - system.map.lucid.json5
         ↓
Triggers:
  1. /update-super-index (add concept)
  2. /update-goal-tree (add objective)
  3. Git commit (version control)
```

**Failure Points:**
- Templates missing → Command fails
- Write permission denied → Cannot create files
- Git not initialized → No version control

### Chain 2: Test Execution

```
User: /run-tests for VIF
         ↓
Command: run-tests.md
         ↓
Dependencies:
  1. pytest installed
  2. VIF package exists
  3. Test files exist (packages/vif/tests/)
  4. Python environment configured
         ↓
Executes:
  python -m pytest packages/vif/tests/ -v
         ↓
Output:
  - Test results (pass/fail)
  - Coverage report
  - Performance metrics
         ↓
Optionally Triggers:
  1. VIF confidence tracking (MCP tool)
  2. Timeline entry (test execution recorded)
  3. Update documentation (if tests show new coverage)
```

**Failure Points:**
- pytest not installed → Script fails
- Tests don't exist → No tests to run
- Test failures → Reports failures (not a failure of command)

### Chain 3: Quality Validation

```
User: /validate-quintet for packages/vif/
         ↓
Command: validate-quintet.md
         ↓
Dependencies:
  1. VIF code files
  2. VIF test files
  3. VIF documentation
  4. VIF schemas
  5. NL tags in code
  6. Quintet parity calculator
         ↓
Analyzes:
  - Code presence and quality
  - Test coverage and completeness
  - Documentation completeness
  - Schema definitions
  - NL tag coverage
         ↓
Calculates:
  P = avg(10 pairwise similarities)
         ↓
Reports:
  - P score (0.XX)
  - Grade (A+/A/B+/B/Fail)
  - Specific gaps if P < 0.90
         ↓
Triggers:
  1. /fix-nl-tags if tag coverage low
  2. /run-tests if test coverage low
  3. /create-t0-t4-docs if docs missing
```

**Failure Points:**
- Code missing → Cannot calculate (report gap)
- Tests missing → P will be low (report gap)
- Calculator error → Report error, suggest manual check

---

## Context Critical for Mutation

### Changing Base Rules Requires

**Context:**
- Understanding of all AI operations (affects everything)
- Current rule content (what's changing?)
- Token usage baseline (what's the impact?)
- AI compliance data (does AI follow current rules?)

**Cannot Change Without:**
- Decision log explaining why
- Test conversation validating new behavior
- Archive of old version
- Rollback plan

**Validation:**
- AI follows new guidance correctly
- Token usage within budget (≤ 5,000 for Always rules)
- No quality regressions
- User satisfaction maintained

### Creating New Command Requires

**Context:**
- Workflow being automated (is it common?)
- Scripts/tools available (do they exist?)
- Parameter requirements (what inputs needed?)
- Integration points (which systems involved?)

**Cannot Create Without:**
- Clear workflow definition (step-by-step)
- Validation that scripts work
- Examples of expected execution
- Error handling defined

**Validation:**
- Command executes successfully
- Output meets quality standards
- Time saved vs manual (50%+ reduction)
- User finds it useful

---

## Vows and Constraints

### System-Wide Vows

**Vows Inherited from AIM-OS:**

1. **Bitemporal Versioning:**
   - Archive old rules, never delete
   - `.DISABLED` extension for archived rules
   - Git history for all changes

2. **T0-T4 Documentation:**
   - Complete T0-T4 stack required
   - Perfect Metadata frontmatter
   - Transitional banners

3. **Quintet Parity:**
   - Commands must maintain P >= 0.90
   - Code + Tests + Docs + Specs + Tags

4. **Confidence Routing:**
   - Only work on tasks >= 0.70 confidence
   - Pivot if confidence drops

5. **Zero Hallucinations:**
   - Never guess if uncertain
   - Research or ask instead

### Rules-Specific Vows

**Vows:**

1. **Always Rules ≤ 500 Lines:**
   - High token cost requires brevity
   - Split into multiple rules if needed

2. **No Credentials in Rules:**
   - Version controlled → exposed
   - Use environment variables

3. **Test Before Deploy:**
   - Verify AI follows guidance
   - Check token impact
   - No blind deployment

4. **Clear Scoping:**
   - Always: Only critical
   - Auto-Attached: Specific patterns
   - Agent Requested: Clear descriptions
   - Manual: Specialized only

### Commands-Specific Vows

**Vows:**

1. **Complete Workflows:**
   - Step-by-step processes
   - Error handling included
   - Validation steps defined

2. **Security First:**
   - No shell injection
   - Parameter sanitization
   - Sensitive data protection

3. **Integration Verified:**
   - Scripts exist and work
   - MCP tools operational
   - Systems initialized

4. **Quality Maintained:**
   - Outputs meet standards
   - Tests passing after execution
   - Documentation accurate

---

## Track Authorization

### Rules Modification Authority

**Who Can Modify:**

**Project Rules:**
- Aether: Full authority (owner)
- Braden: Full authority (creator)
- Git contributors: Via PR review

**User Rules:**
- Braden only (global settings)

**Team Rules (Future):**
- Team admin only

**Authorization Matrix:**

| Role | Create Project Rule | Modify Project Rule | Delete Project Rule | Create Command | Modify Command |
|------|---------------------|--------------------|--------------------|----------------|----------------|
| Aether | ✅ Yes | ✅ Yes | ❌ No (archive only) | ✅ Yes | ✅ Yes |
| Braden | ✅ Yes | ✅ Yes | ✅ Yes (final authority) | ✅ Yes | ✅ Yes |
| Future Team | ✅ Yes (PR) | ✅ Yes (PR) | ❌ No | ✅ Yes (PR) | ✅ Yes (PR) |

### Governance Process

**For Rule Changes:**

```yaml
proposal:
  - Author creates decision log explaining change
  - Creates PR with rule modification
  - Tests in conversation
  - Measures token impact

review:
  - Braden reviews decision log
  - Tests rule in his environment
  - Approves or requests changes

deployment:
  - Merge PR
  - Monitor for 24 hours
  - Rollback if issues
  - Update documentation
```

**For Command Creation:**

```yaml
proposal:
  - Author creates command markdown
  - Tests execution with sample parameters
  - Verifies integration with scripts/tools
  - Documents expected behavior

review:
  - Braden tests command
  - Validates usefulness
  - Checks quality
  - Approves or requests changes

deployment:
  - Commit command file
  - Add to command list documentation
  - Monitor usage
  - Iterate based on feedback
```

---

## DEL Reference Integration

### Scope Declaration

**Rules System:**
- Scope: 4 types, 3 scopes (user/project/team), nested support
- Current: 2 project rules
- Target: 15 project rules
- Tests: 15 validation tests
- Timeline: 4 weeks for full deployment

**Commands System:**
- Scope: 5 categories, 26 commands total
- Current: 12 commands
- Target: 26 commands
- Tests: 68 execution tests
- Timeline: 4 weeks for full deployment

**Documentation:**
- T0-T4 complete (4 docs)
- README complete
- A-H protocol (8 docs)
- System maps (2 files)

### Cross-References to DEL

**Rollout Sequencing:** See D_del.md Phase 1-4
**Test Demand:** See D_del.md Required Tests section
**Resource Requirements:** See D_del.md development time estimates

---

## Mutation Control Summary

### Before Any Change

1. ✅ Create decision log or thought journal
2. ✅ Archive current version (if modifying)
3. ✅ Verify dependencies available
4. ✅ Test in isolation
5. ✅ Measure impact (token usage, execution time)

### After Any Change

1. ✅ Validate syntax (YAML for rules, Markdown for both)
2. ✅ Test execution (conversation for rules, invocation for commands)
3. ✅ Verify integration (scripts work, systems respond)
4. ✅ Commit with clear message
5. ✅ Monitor for issues (24 hours)
6. ✅ Update documentation (T3 if significant)

### Confidence Requirements

**Rule Modification:** >= 0.80 confidence
- Medium blast radius (affects AI context)
- Must work correctly (no broken AI)

**Command Creation:** >= 0.75 confidence
- Low blast radius (episodic execution)
- Easier to fix if issues

**System Deployment:** >= 0.90 confidence
- Already met (proven system, clear implementation)

---

**Status:** Context mesh map complete ✅  
**Next:** F - Confidence-Gated Mutation Control

