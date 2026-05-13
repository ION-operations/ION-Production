# D - Deep Expansion Layer (DEL): Cursor Rules & Commands

**Date:** 2025-11-05  
**Author:** Aether  
**Status:** ✅ Complete  

---

## Complete System Expansion

### Tier Classification

**System Tier:** Tier 1 (Infrastructure/Tooling)
- Not core functionality (Tier 0)
- Not user-facing feature (Tier 2)
- Infrastructure supporting development
- Medium blast radius (affects AI, not data)

### Scope and Dimensionality

#### Rules System Scope

**Complete Rule Type Matrix:**

| Type | Load Mechanism | Token Cost | Use Cases | Examples |
|------|----------------|------------|-----------|----------|
| **Always** | Automatic (every conversation) | ~5,000 | Critical protocols, identity, safety | base-rules.mdc |
| **Auto-Attached** | Pattern match (glob) | ~2,000 | File-type standards | python-standards.mdc |
| **Agent Requested** | AI relevance decision | ~3,000 (conditional) | Context guidance | dynamic-rules.mdc |
| **Manual** | Explicit @mention | 0 (until invoked) | Specialized workflows | @deployment |

**Dimensionality:**
- 4 rule types
- 3 scopes (user/project/team)
- Unlimited rules per scope
- Nested rules (directory hierarchies)

**Predicted Full Scope:**

```
Project Rules (Predicted):
  .cursor/rules/
  ├── base-rules.mdc (Always - 300 lines)
  ├── dynamic-rules.mdc (Agent Requested - 600 lines)
  ├── python-standards.mdc (Auto-Attached *.py - 400 lines)
  ├── typescript-standards.mdc (Auto-Attached *.ts - 400 lines)
  ├── markdown-standards.mdc (Auto-Attached *.md - 200 lines)
  ├── test-standards.mdc (Auto-Attached test_*.py - 300 lines)
  ├── deployment.mdc (Manual @deployment - 200 lines)
  ├── security-audit.mdc (Manual @security - 200 lines)
  └── packages/
      ├── cmc_service/.cursor/rules/
      │   └── cmc-specific.mdc (50 lines)
      ├── hhni/.cursor/rules/
      │   └── hhni-specific.mdc (50 lines)
      └── vif/.cursor/rules/
          └── vif-specific.mdc (50 lines)

Total: ~15 rules, ~2,750 lines
Token Impact: 5,000 (always) + 0-6,000 (conditional) = 5,000-11,000 per conversation
```

User Rules (Predicted):
```
  Global Cursor Settings:
  - "LUCID AETHER AIM-OS Global User Rules" (current)
  - Communication preferences
  - Personal coding style
  
  Total: 1-3 rules, ~400 lines
  Token Impact: ~1,500 (constant across projects)
```

Team Rules (Future):
```
  If team expansion:
  - Organizational standards
  - Security requirements
  - Compliance protocols
  
  Total: 3-5 rules, ~1,000 lines
  Token Impact: ~3,000 (enforced)
```

#### Commands System Scope

**Complete Command Library (Predicted):**

**Documentation Commands (5):**
1. `/create-t0-t4-docs` ✅ - Generate T0-T4 stack
2. `/update-super-index` ✅ - Update master index
3. `/validate-docs` ✅ - Validate documentation
4. `/generate-system-map` - Create system maps
5. `/create-readme` - Generate README files

**Development Commands (8):**
1. `/run-tests` ✅ - Execute test suite
2. `/fix-nl-tags` ✅ - Auto-tag code
3. `/code-review` ✅ - Quality review
4. `/fix-linter` ✅ - Fix linter errors
5. `/create-component` - Generate component
6. `/refactor-module` - Refactor with tests
7. `/optimize-performance` - Profile and optimize
8. `/fix-merge-conflicts` - Resolve conflicts

**System Commands (6):**
1. `/audit-system` ✅ - Comprehensive audit
2. `/create-system` ✅ - New system creation
3. `/validate-quintet` ✅ - Check parity
4. `/deploy-package` ✅ - Create distributions
5. `/test-mcp-tools` ✅ - Verify MCP tools
6. `/health-check` - System health

**Memory Commands (4):**
1. `/create-decision-log` ✅ - Decision documentation
2. `/create-thought-journal` ✅ - Thought journal
3. `/update-goal-tree` ✅ - Goal tracking
4. `/create-learning-log` - Learning documentation

**Integration Commands (3):**
1. `/test-integration` - Integration tests
2. `/verify-connections` - Cross-system verification
3. `/generate-api-docs` - API documentation

**Total Predicted:** 26 commands across 5 categories

**Current Status:** 12/26 (46%) implemented

### Test Demand Prediction

#### Rules Testing

**Unit Tests:**
- MDC parsing validation (Cursor internal)
- Glob pattern matching (Cursor internal)
- Rule selection logic (not directly testable)

**Integration Tests:**
- Load rules and verify AI follows them
- Test each rule type loads correctly
- Verify nested rules scope properly

**Validation:**
- YAML frontmatter syntax
- Markdown content validity
- Glob pattern correctness

**Estimated Test Count:** ~15 validation tests (for AIM-OS rule files)

#### Commands Testing

**Per Command:**
- Workflow execution test
- Parameter handling test
- Error case test
- Integration test (with scripts/MCP)

**Estimated Tests:**
- 12 commands × 4 tests = 48 tests
- Plus 10 integration tests
- **Total:** ~58 tests

**Test Implementation:**

```python
# tests/test_cursor_commands.py

import pytest
from cursor_command_executor import execute_command

class TestRunTestsCommand:
    """Test /run-tests command."""
    
    def test_run_tests_basic(self):
        """Test basic /run-tests execution."""
        result = execute_command("/run-tests")
        assert result.success
        assert "tests passed" in result.output
    
    def test_run_tests_with_system(self):
        """Test /run-tests with system parameter."""
        result = execute_command("/run-tests for VIF")
        assert result.success
        assert "VIF" in result.output
        assert result.test_count > 0
    
    def test_run_tests_system_not_found(self):
        """Test /run-tests with invalid system."""
        result = execute_command("/run-tests for INVALID")
        assert not result.success
        assert "not found" in result.error
```

### Rollout Sequencing

**Phase 1: Core Setup (Complete ✅)**
- Disable archived rules
- Create commands directory
- Deploy 12 core commands
- Create T0-T3 documentation

**Phase 2: Expansion (Week 1)**
- Create glob-based rules (Python, TypeScript, Markdown, Test)
- Add 5-8 more commands (deployment, integration, refactoring)
- Create T4 complete reference
- Add command examples

**Phase 3: Refinement (Week 2-3)**
- Monitor usage patterns
- Iterate based on feedback
- Optimize token usage
- Add specialized commands

**Phase 4: Maturity (Week 4+)**
- Full command library (26 commands)
- Complete rule coverage
- Team rules (if team expansion)
- Analytics and optimization

### Resource Requirements

**Development Time:**

```yaml
phase_1: "4 hours" ✅ COMPLETE
  - Archive cleanup: 10 min
  - Commands creation: 2 hours
  - Documentation: 1.5 hours
  - Testing: 30 min

phase_2: "8 hours"
  - Glob rules: 2 hours
  - Additional commands: 3 hours
  - T4 documentation: 2 hours
  - Examples: 1 hour

phase_3: "4 hours"
  - Monitoring: 1 hour
  - Iteration: 2 hours
  - Optimization: 1 hour

phase_4: "8 hours"
  - Command expansion: 4 hours
  - Rule coverage: 2 hours
  - Analytics: 2 hours

total: "24 hours" (over 4 weeks)
current: "4 hours complete" (17%)
```

**Storage:**
- Rules: ~3 KB per rule × 15 rules = ~45 KB
- Commands: ~2 KB per command × 26 commands = ~52 KB
- Documentation: ~50 KB (T0-T4)
- A-H protocol docs: ~30 KB
- **Total:** ~177 KB (negligible)

**Token Costs:**
- Always rules: 5,000 tokens/conversation
- Average additional: 2,000-6,000 tokens (context-dependent)
- Commands: 500-1,000 tokens when invoked
- **Average conversation:** 7,000-11,000 tokens (vs 10,000 legacy)

---

## Context Mesh Map (CMM) Preview

### Critical Cross-Dependencies

**Rules System Depends On:**
- Cursor 2.0 MDC parser (built-in)
- File system (.cursor/rules/)
- Git (version control)

**Commands System Depends On:**
- Cursor 2.0 command detection (built-in)
- AIM-OS scripts (83 automation scripts)
- MCP tools (59 tools)
- Core systems (CMC, HHNI, VIF, APOE)

**Vows/Constraints:**
- MUST preserve bitemporal versioning (archive, not delete)
- MUST follow T0-T4 documentation standards
- MUST maintain quintet parity P >= 0.90
- MUST track confidence throughout

### Mutation Control Requirements

**For Rule Changes:**
```yaml
confidence_packet:
  operation: "modify_rule"
  confidence: ">= 0.80"
  validation:
    - Rule syntax valid (YAML + Markdown)
    - No duplication with existing rules
    - Token cost acceptable
    - AI can follow guidance
  
  evidence:
    - Test conversation with new rule
    - Token usage measurement
    - Compliance check
  
  rollback:
    - Git revert if issues
    - Archive old version
    - Document in decision log
```

**For Command Creation:**
```yaml
confidence_packet:
  operation: "create_command"
  confidence: ">= 0.75"
  validation:
    - Workflow clearly documented
    - Scripts/tools exist
    - Parameters well-defined
    - Error handling complete
  
  evidence:
    - Test execution with sample parameters
    - Verify script integration
    - Check output quality
  
  quality_gates:
    - Markdown syntax valid
    - Examples included
    - Edge cases documented
```

---

## Blast Radius Analysis

### Rules Changes Impact

**Blast Radius: MEDIUM**

**Affected Systems:**
- All AI conversations (if Always rules changed)
- Specific file types (if Auto-Attached rules changed)
- Specific contexts (if Agent Requested rules changed)

**Mitigation:**
- Test rules in isolation first
- Monitor AI behavior after changes
- Git version control (easy rollback)
- Incremental deployment

### Commands Changes Impact

**Blast Radius: LOW**

**Affected:**
- Only users who invoke command
- Only during command execution
- No persistent state changes

**Mitigation:**
- Commands are episodic (no persistent impact)
- Failed command = no lasting effect
- User can retry or abandon

---

## Performance and Security Budgets

### Performance Budget

**Token Usage:**
- Always rules: ≤ 5,000 tokens (strict)
- Total context: ≤ 15,000 tokens (including conditional rules)
- Commands: ≤ 1,000 tokens per invocation

**Execution Time:**
- Rule loading: < 100ms
- Command detection: < 50ms
- Command execution: Variable (depends on workflow)

**Memory:**
- Rules in memory: ≤ 10 MB
- Command cache: ≤ 5 MB

### Security Budget

**Threat Model:**
- Malicious rules in cloned repos
- Command injection via parameters
- Credential exposure in rules

**Security Measures:**
- Manual review of project rules before enabling
- No credentials in version-controlled files
- Parameter sanitization in commands
- Audit logging for sensitive operations

**Security Budget:**
- Risk tolerance: LOW (strict validation)
- Audit frequency: Every rule/command change
- Incident response: < 1 hour (disable malicious rule)

---

## Required Tests

### Validation Tests (15)

1. `test_base_rules_syntax` - YAML frontmatter valid
2. `test_dynamic_rules_syntax` - Metadata complete
3. `test_python_standards_glob` - Pattern matches correctly
4. `test_archived_rules_disabled` - Not loading
5. `test_rule_precedence` - Team > Project > User
6-15. One test per glob-based rule

### Command Execution Tests (48)

**Per command (4 tests each):**
- Basic execution
- Parameter handling
- Error case
- Integration test

**12 commands × 4 = 48 tests**

### Integration Tests (10)

1. `test_command_creates_decision_log_in_cmc` - CMC integration
2. `test_command_updates_hhni_index` - HHNI integration
3. `test_command_tracks_confidence_in_vif` - VIF integration
4. `test_rule_enforces_quintet_parity` - SDF-CVF integration
5. `test_command_executes_script` - Script integration
6. `test_command_calls_mcp_tool` - MCP integration
7. `test_nested_rule_scoping` - Nested rules work
8. `test_glob_pattern_matching` - Auto-attach works
9. `test_agent_requested_selection` - AI chooses correctly
10. `test_manual_rule_invocation` - @mention works

**Total Tests Required:** 73 tests

---

## Owner Track

**System Owner:** Aether  
**Maintainer:** Aether  
**Reviewers:** Braden (user validation)

**Responsibilities:**

**Owner (Aether):**
- Create and maintain rules
- Develop and test commands
- Write documentation
- Monitor effectiveness
- Iterate based on feedback

**User (Braden):**
- Validate command usefulness
- Report issues
- Suggest new commands
- Review rule changes

**Future (if team expansion):**
- Team admin manages team rules
- Individual developers can create project commands
- Shared command library

---

## Must-Never Vows

### For Rules

**MUST NEVER:**
1. ❌ Delete archived rules (rename/disable only - bitemporal)
2. ❌ Put credentials in rules (use env vars)
3. ❌ Create Always rules > 500 lines (token cost)
4. ❌ Use vague glob patterns like `**/*` (matches everything)
5. ❌ Skip testing rules before deploying
6. ❌ Remove old rules without archiving
7. ❌ Create duplicate guidance (check existing first)

**MUST ALWAYS:**
1. ✅ Archive old versions before changing
2. ✅ Test in conversation before committing
3. ✅ Document rule changes in decision logs
4. ✅ Monitor token usage impact
5. ✅ Validate YAML frontmatter syntax
6. ✅ Commit rules separately from code changes

### For Commands

**MUST NEVER:**
1. ❌ Create commands with shell injection risks
2. ❌ Skip validation in command workflows
3. ❌ Assume scripts exist (verify first)
4. ❌ Create commands without examples
5. ❌ Ignore error cases in workflows
6. ❌ Make commands too complex (split instead)

**MUST ALWAYS:**
1. ✅ Include error handling in workflows
2. ✅ Provide clear examples
3. ✅ Document parameters clearly
4. ✅ Validate command output
5. ✅ Test command execution
6. ✅ Update documentation when commands change

---

## Rollout Dependencies

### Phase 1 Dependencies (Complete ✅)

**Required Before Deployment:**
- ✅ Cursor 2.0 installed
- ✅ `.cursor/rules/` directory exists
- ✅ `base-rules.mdc` and `dynamic-rules.mdc` active
- ✅ `.cursor/commands/` directory created
- ✅ 12 core commands created
- ✅ T0-T3 documentation complete

**Validation:**
- ✅ Archived rules disabled
- ✅ No YAML syntax errors
- ✅ Command markdown valid
- ✅ All cross-references correct

### Phase 2 Dependencies

**Required:**
- Phase 1 complete
- Usage data collected (2 weeks)
- User feedback received
- Effectiveness metrics measured

**Enables:**
- Glob-based rule creation
- Additional commands
- Optimization based on data
- T4 complete reference

### Phase 3 Dependencies

**Required:**
- Phase 2 complete
- Command library proven effective
- Rule system optimized
- Team needs identified (if applicable)

**Enables:**
- Team rules creation
- Shared command library
- Advanced automation
- Analytics system

---

## Complete Feature Breakdown

### Rules Features

**Current (Phase 1):**
- [x] Always Applied rules (base-rules.mdc)
- [x] Agent Requested rules (dynamic-rules.mdc)
- [x] Archive disabled
- [ ] Auto-Attached rules (glob patterns)
- [ ] Manual rules (@mention)
- [ ] Nested rules (component-specific)

**Future (Phase 2-3):**
- [ ] Python standards (glob: **/*.py)
- [ ] TypeScript standards (glob: **/*.ts)
- [ ] Test standards (glob: test_*.py)
- [ ] Deployment protocol (@deployment)
- [ ] Security audit (@security)
- [ ] Component-specific rules (nested)
- [ ] Team rules (if team expansion)

### Commands Features

**Current (Phase 1):**
- [x] Documentation commands (3/5)
- [x] Development commands (4/8)
- [x] System commands (5/6)
- [x] Memory commands (3/4)
- [ ] Integration commands (0/3)

**Future (Phase 2-3):**
- [ ] Deployment commands
- [ ] Security commands
- [ ] Performance commands
- [ ] Git workflow commands
- [ ] Component generation
- [ ] Refactoring automation

---

## Scope Summary

**Total System Scope:**

**Rules:**
- Types: 4
- Categories: 3 (user/project/team)
- Current: 2 project rules
- Target: 15 project rules
- Test demand: 15 validation tests

**Commands:**
- Categories: 5 (docs/dev/system/memory/integration)
- Current: 12 commands
- Target: 26 commands
- Test demand: 58 execution tests + 10 integration tests

**Documentation:**
- T0-T4 complete (4 docs)
- README complete
- A-H protocol in progress (8 docs)
- System maps needed

**Time to Complete:**
- Phase 1: 4 hours ✅ COMPLETE
- Phase 2: 8 hours
- Phase 3: 4 hours
- Phase 4: 8 hours
- **Total:** 24 hours (over 4 weeks)

**Blast Radius:** MEDIUM (affects AI context, not data)

**Confidence:** 0.95 (proven approach, clear scope)

---

**Status:** Deep expansion complete ✅  
**Next:** E - Context Mesh Map (CMM)

