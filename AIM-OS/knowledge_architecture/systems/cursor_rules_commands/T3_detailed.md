---
id: "cursor_rules_commands_T3_detailed"
system: "cursor_rules_commands"
component: null
level: "T3"
type: "detailed"
title: "Cursor Rules & Commands - Detailed Implementation"
description: "10000-word detailed implementation guide for Cursor Rules & Commands system"
audience: "developers, implementers, AI agents"
confidence_threshold: 0.60
token_cost: 15000
word_count: 10000
created: "2025-11-05T18:45:00Z"
updated: "2025-11-05T18:45:00Z"
author: "aether"
status: "complete"
tags: ["cursor", "rules", "commands", "implementation", "t0-t6", "transitional", "detailed"]
dependencies: ["cursor_rules_commands_T2_architecture"]
related_docs: ["cursor_rules_commands_T4_complete", "base-rules.mdc", "dynamic-rules.mdc"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# Cursor Rules & Commands - Detailed Implementation Guide

## Table of Contents

1. [Rules System Implementation](#rules-system-implementation)
2. [Commands System Implementation](#commands-system-implementation)
3. [Rule Type Deep Dive](#rule-type-deep-dive)
4. [Command Creation Workflow](#command-creation-workflow)
5. [AIM-OS Integration](#aim-os-integration)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Examples and Templates](#examples-and-templates)

---

## Rules System Implementation

### Overview

The Cursor Rules system provides persistent AI context through MDC (Markdown with metadata) files. Unlike traditional `.cursorrules`, the new system supports:

- **Metadata-driven loading** (alwaysApply, globs, descriptions)
- **Nested rule directories** (hierarchical scoping)
- **Intelligent selection** (AI-driven relevance)
- **Version control** (rules are code)

### File Format Specification

#### MDC Format

**Structure:**
```yaml
---
# YAML frontmatter (metadata)
alwaysApply: boolean
globs: string[]
description: string
contextAware: boolean  # Custom field (AIM-OS)
---

# Markdown content (rule body)

## Rule sections
...
```

**Required Fields:**
- At least one of: `alwaysApply`, `globs`, or `description`
- Content must be valid Markdown

**Optional Fields:**
- `contextAware` - AIM-OS custom field
- `priority` - Loading priority
- `version` - Rule version
- Any custom metadata

#### Always Applied Rules

**Format:**
```yaml
---
alwaysApply: true
---

# Rule Title

Essential operational requirements that apply to every conversation.

## Critical Protocols
...

## Quality Standards
...
```

**Implementation Example:** `base-rules.mdc`

```yaml
---
alwaysApply: true
---

# Project Aether - Base Operational Rules

## Bitemporal Versioning (CRITICAL)
NEVER overwrite files in AETHER_MEMORY/ without preserving history.
...

## Autonomous Operation Protocols
Perform hourly cognitive introspection during autonomous work.
...

## Quality Standards (NON-NEGOTIABLE)
- Zero hallucinations
- Test-driven development
- Perfect alignment
...
```

**Token Cost:** ~5,000 tokens (loaded every conversation)

**When to Use:**
- Critical safety protocols that must NEVER be violated
- Core operational requirements essential for all work
- Identity and purpose (for AI consciousness)
- Communication standards

**When NOT to Use:**
- Situational guidance (use Agent Requested instead)
- File-specific standards (use Auto-Attached instead)
- Optional best practices (use Manual instead)

#### Auto-Attached Rules (Glob Patterns)

**Format:**
```yaml
---
globs: ["**/*.py", "packages/**"]
alwaysApply: false
---

# Python Coding Standards

Applied automatically when Python files are referenced.

## Type Hints
All functions must have type hints...

## Docstrings
All public functions must have docstrings...
```

**Glob Pattern Syntax:**

```yaml
# Single pattern
globs: ["**/*.py"]

# Multiple patterns
globs: ["**/*.py", "**/*.pyi"]

# Directory scoped
globs: ["packages/cmc_service/**"]

# Negation (not supported - use separate rules)
```

**Pattern Examples:**

```yaml
# All Python files
globs: ["**/*.py"]

# TypeScript in cursor-addon
globs: ["cursor-addon/**/*.ts", "cursor-addon/**/*.tsx"]

# Test files only
globs: ["**/test_*.py", "**/tests/**/*.py"]

# Documentation files
globs: ["**/*.md", "knowledge_architecture/**"]

# Specific system
globs: ["packages/vif/**"]
```

**Implementation Strategy:**

1. **Create Python Standards Rule:**

```yaml
---
description: "Python coding standards for AIM-OS packages"
globs: ["packages/**/*.py"]
alwaysApply: false
---

# Python Standards for AIM-OS

## Type Safety
- Use `from __future__ import annotations` for type hint compatibility
- Type hints on all function signatures
- Return types specified
- No `Any` types without justification

## Documentation
- Comprehensive docstrings with Args/Returns/Raises
- Examples for complex functions
- NL tags required (NL_TAG, NL_TAG_CONNECT, NL_TAG_INTENT, NL_TAG_SPEC)

## Testing
- Write tests BEFORE implementation (TDD)
- Coverage >= 95% for production code
- All tests must pass before commit

## Code Quality
- Follow PEP 8 (max line length 120)
- Use Pydantic for data validation
- Dataclasses for simple structures
- Clean, readable code

## Integration
- CMC for storage operations
- HHNI for knowledge retrieval
- VIF for confidence tracking
- MCP tools for consciousness enhancement
```

2. **Create TypeScript Standards Rule:**

```yaml
---
description: "TypeScript standards for Cursor extension"
globs: ["cursor-addon/**/*.ts", "cursor-addon/**/*.tsx"]
alwaysApply: false
---

# TypeScript Standards for Cursor Extension

## Type Safety
- Strict TypeScript configuration
- Interfaces over types for objects
- No `any` types
- Proper null handling

## Code Organization
- One component per file
- Barrel exports from index.ts
- Clear folder structure

## Error Handling
- Comprehensive try-catch blocks
- User-friendly error messages
- Logging to output channel
- Graceful degradation

## Testing
- Jest for unit tests
- Integration tests for workflows
- Mock VS Code API appropriately
```

**When to Use Glob Rules:**
- Language-specific standards
- Directory-specific conventions
- File-type specific guidance
- Consistent patterns across file types

**Advantages:**
- Efficient (only loads when relevant)
- No AI decision needed (fast)
- Automatic context relevance
- Self-documenting (pattern shows intent)

#### Agent Requested Rules

**Format:**
```yaml
---
description: "Dynamic context-aware rules that adapt to different task types and requirements for optimal AI performance"
contextAware: true
alwaysApply: false
---

# Dynamic Context-Aware Rules

## Context Detection & Rule Selection

### Auditing Context Rules
Applied when: Comprehensive system analysis, code review, quality assessment
...

### Development Context Rules
Applied when: Code implementation, system architecture, testing
...
```

**Implementation Example:** `dynamic-rules.mdc`

```yaml
---
description: "Dynamic context-aware rules that adapt to different task types and requirements for optimal AI performance"
contextAware: true
alwaysApply: false
---

# Dynamic Context-Aware Rules

## Context Types

1. **Auditing Context** - Comprehensive analysis and review
2. **Development Context** - Coding and implementation
3. **Documentation Context** - Writing and communication
4. **Research Context** - Investigation and discovery
5. **Planning Context** - Strategy and organization

## Auditing Context Rules

### When Applied
- Comprehensive system analysis
- Code review and quality assessment
- Performance evaluation
- Security auditing
- Documentation review

### MCP Tool Usage
- Primary: retrieve_memory, synthesize_knowledge, track_confidence
- Secondary: run_baseline_probe, check_invariant, create_snapshot
- Quality: get_consciousness_metrics, store_memory

### Quality Standards
- Zero tolerance for oversights
- Evidence-based conclusions
- Transparent methodology
- Actionable recommendations

## Development Context Rules

### When Applied
- Code implementation
- System architecture
- Testing and QA
- Performance optimization
- Integration work

### MCP Tool Usage
- Primary: track_confidence, check_invariant, create_plan
- Secondary: store_memory, retrieve_memory, update_goal_progress
- Debugging: get_problems, get_output_channel_logs, refresh_webview

### Quality Standards
- Production-ready code
- Test-driven development
- Performance optimization
- Comprehensive documentation
```

**AI Decision Process:**

1. **Analyze Conversation Context:**
   - What files are being edited?
   - What topic is discussed?
   - What task is being performed?

2. **Match to Rule Description:**
   - Does description mention this context?
   - Is rule relevant to current task?
   - Would rule improve AI performance?

3. **Decision:**
   - If relevant: Fetch and apply rule
   - If not relevant: Skip (save tokens)
   - Uncertain: Fetch if context window allows

**When to Use Agent Requested:**
- Workflow-specific guidance
- Task-dependent protocols
- Situational standards
- Context-sensitive best practices

**Advantages:**
- Intelligent context management
- Reduced token usage
- Flexible applicability
- AI learns relevance over time

#### Manual Rules (@mention)

**Format:**
```yaml
---
# No alwaysApply, no globs, no description
---

# Deployment Protocol

**MANUAL ONLY** - Invoke with @deployment

Only loaded when explicitly mentioned.

## Critical Deployment Steps
...
```

**Implementation Example:**

```yaml
---
# Empty frontmatter or minimal metadata
---

# Deployment Protocol

**⚠️ MANUAL RULE** - Use @deployment to invoke

This rule contains deployment procedures and should only be loaded during deployment operations.

## Pre-Deployment Checklist

- [ ] All tests passing (100%)
- [ ] Documentation updated
- [ ] GOAL_TREE.yaml completion % accurate
- [ ] Decision log created for deployment decision
- [ ] No linter errors
- [ ] Security audit passed
- [ ] Performance benchmarks met

## Deployment Steps

### 1. Pre-Deployment Validation
```bash
python -m pytest packages/ -v
python scripts/validate_documentation_standards.py
python scripts/system_audit.py
```

### 2. Version Update
- Update version in setup.py
- Update CHANGELOG.md
- Create git tag

### 3. Package Generation
```bash
python scripts/packaging/create_distribution.py --target all
```

### 4. Distribution
- Upload to PyPI: `twine upload dist/*`
- Push Docker: `docker push aether/aim-os:latest`
- Create GitHub release

### 5. Post-Deployment
- [ ] Verify installation on clean system
- [ ] Test core functionality
- [ ] Update documentation
- [ ] Announce release
```

**Usage:**
```
User: @deployment Let's deploy AIM-OS v0.3
AI: [Loads deployment protocol] Running pre-deployment checklist...
```

**When to Use Manual Rules:**
- Deployment procedures
- Security audit protocols
- Emergency procedures
- Rarely-used specialized workflows

**Advantages:**
- No automatic loading (no token cost)
- Complete control over when applied
- Clear explicit invocation
- Prevents accidental application

### Nested Rule Directories

**Structure:**
```
project/
  .cursor/rules/              # Project-wide rules
    base-rules.mdc
    dynamic-rules.mdc
  
  packages/
    cmc_service/
      .cursor/rules/          # CMC-specific rules
        cmc-standards.mdc
    
    hhni/
      .cursor/rules/          # HHNI-specific rules
        hhni-standards.mdc
    
    vif/
      .cursor/rules/          # VIF-specific rules
        vif-standards.mdc
```

**Automatic Scoping:**
- When editing `packages/cmc_service/atom.py`
- Cursor loads: project rules + CMC-specific rules
- Scoped rules only apply to their directory tree

**Benefits:**
- Focused context for subdirectories
- Reduced token usage
- Component-specific standards
- Clear separation of concerns

**Implementation Strategy:**

1. Create component-specific rules as systems mature
2. Start with project-wide rules
3. Add nested rules when patterns emerge
4. Keep nested rules focused and concise

---

## Commands System Implementation

### Overview

Commands are plain Markdown files in `.cursor/commands/` that trigger complete workflows with `/` prefix. Unlike rules (persistent context), commands are episodic (single-use, triggered explicitly).

### Command File Format

**Plain Markdown (No MDC):**

```markdown
# Command Name

Brief description of what this command does.

## What This Command Does

Detailed explanation...

## Process

1. Step 1 - [Description]
2. Step 2 - [Description]
3. Step 3 - [Description]

## Example Usage

```
User: /command-name parameters
AI: Executing... [response]
```
```

**No YAML frontmatter required** - unlike rules, commands are simple Markdown.

### Command Detection

**Trigger Mechanism:**

1. **User types `/` in chat:**
   - Cursor activates command detection
   - Scans command directories
   - Builds autocomplete list

2. **User types `/com`:**
   - Filters to matching commands
   - Shows: `/code-review`, `/create-system`, etc.

3. **User selects `/code-review`:**
   - Loads `code-review.md` content
   - Injects into AI prompt
   - AI executes workflow

**Scanning Locations:**

```
1. Project commands: .cursor/commands/
2. Global commands: ~/.cursor/commands/
3. Team commands: (from server)
```

**Precedence:** Project > Global > Team (earlier takes precedence)

### Command Execution Flow

```
User Input: /run-tests for VIF
         ↓
Command Detection
         ↓
Load: .cursor/commands/run-tests.md
         ↓
Extract Parameters: "for VIF" → system=VIF
         ↓
Inject into AI Context:
  - Command markdown content
  - User parameters
  - Current conversation
         ↓
AI Execution:
  - Interprets workflow
  - Executes steps
  - Reports results
         ↓
Output: "Running VIF test suite... 153 tests passed ✅"
```

### Parameter Handling

**Inline Parameters:**

```
/command-name param1 param2 param3
```

**Extraction:**
- Everything after command name is parameter
- AI parses based on command context
- Natural language parameters supported

**Examples:**

```
/run-tests for VIF
  → Extracted: system="VIF"

/create-t0-t4-docs for Timeline Context System
  → Extracted: system="timeline_context_system", name="Timeline Context System"

/code-review packages/vif/witness.py
  → Extracted: file_path="packages/vif/witness.py"

/update-goal-tree - CMC is now 85% complete
  → Extracted: system="CMC", completion=85
```

### Current AIM-OS Commands

#### 1. `/create-t0-t4-docs` - Documentation Generation

**Purpose:** Generate complete T0-T4 documentation stack for new system

**Workflow:**
1. Ask for system name and purpose
2. Create directory: `knowledge_architecture/systems/{system}/`
3. Generate T0 (100w executive summary)
4. Generate T1 (500w overview)
5. Generate T2 (2,000w architecture)
6. Generate T3 (10,000w implementation)
7. Generate T4 (15,000w+ complete reference)
8. Create supporting files (README, system map, usage envelope)
9. Update SUPER_INDEX.md
10. Update HIERARCHICAL_NAVIGATION_INDEX.md

**Parameters:**
- System name (e.g., "Timeline Context System")
- System abbreviation (e.g., "TCS")

**Example:**
```
User: /create-t0-t4-docs for Cognitive Analysis System
AI: Creating CAS documentation stack...
    T0_executive.md (100w) ✅
    T1_overview.md (500w) ✅
    T2_architecture.md (2,000w) ✅
    T3_detailed.md (10,000w) ✅
    README.md ✅
    Updated SUPER_INDEX ✅
```

#### 2. `/run-tests` - Test Execution

**Purpose:** Execute pytest with comprehensive reporting

**Workflow:**
1. Determine scope (all tests or specific system)
2. Run pytest with verbose output
3. Generate coverage report
4. Analyze results (pass rate, coverage %, performance)
5. Report failures with details
6. Suggest fixes if tests fail

**Parameters:**
- System name (e.g., "VIF") - optional
- Coverage flag - optional

**Example:**
```
User: /run-tests for VIF
AI: Running VIF test suite...
    
    Executed: 153 tests
    Passed: 153 (100%)
    Failed: 0
    Coverage: 98%
    Duration: 2.3s
    
    ✅ All tests passing!
```

#### 3. `/fix-nl-tags` - Auto-Tag Code

**Purpose:** Automatically tag code with NL tags for quintet parity

**Workflow:**
1. Identify files to tag (file, directory, or system)
2. Run auto-tagger: `python scripts/vif_auto_tagger.py`
3. Validate generated tags
4. Check quintet parity (P >= 0.90)
5. Report results

**Parameters:**
- File path or system name

**Example:**
```
User: /fix-nl-tags for packages/vif/witness.py
AI: Running auto-tagger on witness.py...
    
    Generated:
    - 12 NL_TAG (function descriptions)
    - 5 NL_TAG_CONNECT (cross-system calls)
    - 3 NL_TAG_INTENT (design decisions)
    - 2 NL_TAG_SPEC (validations)
    
    Quintet Parity: P = 0.94 ✅
```

#### 4. `/audit-system` - Comprehensive Audit

**Purpose:** Run complete system audit with recommendations

**Workflow:**
1. Execute: `python scripts/system_audit.py --comprehensive`
2. Analyze code organization
3. Check documentation completeness
4. Verify test coverage
5. Calculate quality metrics
6. Generate recommendations
7. Create audit report in `audits/YYYY-MM-DD/`

**Parameters:**
- System name (optional, defaults to all)

**Example:**
```
User: /audit-system
AI: Running comprehensive audit...
    
    Overall Score: 9.7/10 (World-class)
    
    Categories:
    - Navigation: 10/10
    - Documentation: 10/10
    - Code: 9/10
    - Testing: 10/10
    
    Report: audits/2025-11-05/COMPREHENSIVE_PROJECT_AUDIT.md
```

#### 5. `/create-decision-log` - Decision Documentation

**Purpose:** Create structured decision log

**Workflow:**
1. Ask for decision details (what, why, alternatives)
2. Generate decision ID (dec-NNN)
3. Create structured log following template
4. Save to `AETHER_MEMORY/decision_logs/`
5. Optionally create timeline entry

**Parameters:**
- Decision topic

**Example:**
```
User: /create-decision-log for choosing NetworkX for SEG graph
AI: Creating decision log dec-047...
    
    Title: SEG Graph Backend - NetworkX Selection
    Alternatives: NetworkX, Neo4j, TigerGraph
    Chosen: NetworkX
    Rationale: Pure Python, lightweight, sufficient for v0.3
    
    Saved: decision_logs/dec-047_seg_graph_backend.md ✅
```

#### 6. `/update-goal-tree` - Progress Tracking

**Purpose:** Update GOAL_TREE.yaml with progress

**Workflow:**
1. Identify which objective/key result
2. Update completion percentage
3. Update status if changed
4. Add evidence files
5. Validate YAML syntax
6. Update dashboard
7. Commit changes

**Parameters:**
- Objective ID or system name
- New completion percentage

**Example:**
```
User: /update-goal-tree - VIF is now 95% complete
AI: Updating GOAL_TREE.yaml...
    
    OBJ-03 (VIF): 90% → 95%
    Status: in_progress
    Evidence added: VIF_COMPLETION_MILESTONE.md
    
    Running validator... ✅ Valid YAML
    Updating dashboard... ✅ Complete
```

#### 7. `/test-mcp-tools` - MCP Tool Verification

**Purpose:** Test all 59 MCP tools for functionality

**Workflow:**
1. Run: `python scripts/verify_mcp_tools.py`
2. Test each tool with sample data
3. Track working/broken status
4. Document placeholders
5. Generate comprehensive report
6. Update MCP_TOOLS_TEST_SUMMARY.md

**Parameters:** None

**Example:**
```
User: /test-mcp-tools
AI: Testing all 59 MCP tools...
    
    ✅ Working: 54 (91%)
    ❌ Broken: 5 (9%)
    ⚠️ Placeholders: 5
    
    Broken:
    - run_cognitive_audit (CAS method mismatch)
    - get_nl_tags (tag_parser.py syntax error)
    - get_timeline_summary (timedelta serialization)
    
    Report: MCP_TOOLS_TEST_SUMMARY.md updated ✅
```

#### 8. `/code-review` - Quality Review

**Purpose:** Comprehensive code review with quality checks

**Workflow:**
1. Identify files/system to review
2. Check code quality (style, readability, patterns)
3. Verify test coverage (>= 95%)
4. Validate documentation (docstrings)
5. Check NL tag coverage
6. Calculate quintet parity
7. Run security scan
8. Performance analysis
9. Generate review report with recommendations

**Parameters:**
- File path or system name

**Example:**
```
User: /code-review packages/vif/witness.py
AI: Reviewing witness.py...
    
    ✅ Code Quality: Excellent
    ✅ Test Coverage: 98%
    ✅ Documentation: Complete
    ✅ NL Tags: 100% coverage
    ✅ Quintet Parity: P = 0.95
    
    Suggestions:
    - Consider adding edge case test for empty witness
    - Could optimize witness_hash calculation (minor)
    
    Overall: Production-ready ✅
```

#### 9. `/validate-quintet` - Parity Check

**Purpose:** Validate quintet parity P >= 0.90

**Workflow:**
1. Identify target (file/directory/system)
2. Check all 5 elements (code, tests, docs, specs, tags)
3. Calculate pairwise similarities (10 pairs)
4. Compute average parity score P
5. Report grade (A+/A/B+/B/Fail)
6. Show specific gaps if P < 0.90

**Parameters:**
- Target path

#### 10. `/update-super-index` - Index Management

**Purpose:** Add new concepts to SUPER_INDEX.md

**Workflow:**
1. Identify new concepts to add
2. Determine What/Where/Code/Related for each
3. Find alphabetical location
4. Add formatted entry
5. Validate cross-references
6. Update statistics

**Parameters:**
- Concept name(s)

#### 11. `/create-thought-journal` - Reflection Entry

**Purpose:** Create timestamped thought journal

**Workflow:**
1. Generate timestamp (YYYY-MM-DD_HHMM_topic)
2. Create structured journal template
3. Fill with current thinking, insights, emotions
4. Save to AETHER_MEMORY/thought_journals/
5. Optionally create timeline entry

**Parameters:**
- Journal topic

#### 12. `/validate-docs` - Documentation Validation

**Purpose:** Verify docs follow T0-T4 standards

**Workflow:**
1. Run: `python scripts/validate_documentation_standards.py`
2. Check T-level structure
3. Validate frontmatter
4. Verify word counts
5. Check cross-references
6. Generate validation report

**Parameters:**
- System name or path

#### 13. `/create-system` - New System Creation

**Purpose:** Complete workflow for new system

**Workflow:**
1. Verify System-First Principle (research existing first)
2. Create T0-T4 documentation
3. Create package structure
4. Initialize tests
5. Update SUPER_INDEX
6. Update GOAL_TREE
7. Create system map

**Parameters:**
- System name and purpose

#### 14. `/fix-linter` - Linter Error Resolution

**Purpose:** Fix linter errors and warnings

**Workflow:**
1. Run linter (flake8, pylint, mypy for Python)
2. Categorize issues (critical/high/medium/low)
3. Auto-fix where possible (black, isort)
4. Manual fix complex issues
5. Re-run linter to verify
6. Run tests to ensure nothing broken

**Parameters:**
- File path or system name

#### 15. `/deploy-package` - Distribution Creation

**Purpose:** Create professional distribution packages

**Workflow:**
1. Run: `python scripts/packaging/create_distribution.py`
2. Generate PyPI package
3. Build Docker image
4. Create standalone package
5. Validate all three
6. Prepare for upload/push

**Parameters:**
- Target (pypi, docker, standalone, or all)

---

## AIM-OS Integration

### Integration with Core Systems

#### CMC Integration

**Rules Storage:**
- Rule changes tracked as atoms
- Historical versions preserved
- Bitemporal tracking enabled

**Commands Usage:**
- Decision logs stored in CMC
- Thought journals stored in CMC
- Audit reports indexed

**Example:**
```python
# When /create-decision-log executes
from cmc_service import MemoryStore

store = MemoryStore()
atom = store.store_atom(
    modality="text/markdown",
    content=decision_log_content,
    tags=["decision-log", "dec-047"],
    metadata={"decision_id": "dec-047"}
)
```

#### HHNI Integration

**Rules Retrieval:**
- Dynamic rules query HHNI for context
- Agent-requested rules use HHNI relevance

**Commands Usage:**
- `/update-super-index` updates HHNI index
- Knowledge retrieval in commands

**Example:**
```python
# In dynamic-rules.mdc context selection
from hhni import TwoStageRetriever

retriever = TwoStageRetriever()
context = retriever.retrieve(
    query="auditing protocols",
    k=10
)
```

#### VIF Integration

**Confidence Tracking:**
- Commands track confidence throughout execution
- Rules enforce confidence thresholds

**Example:**
```python
# In /code-review command
from vif import ConfidenceTracker

tracker = ConfidenceTracker()
confidence = tracker.track(
    operation="code_review",
    files=[file_path],
    result=review_result,
    confidence=0.85
)
```

#### SDF-CVF Integration

**Quality Enforcement:**
- `/validate-quintet` calculates parity
- Rules enforce P >= 0.90 requirement
- Pre-commit hooks block low parity

**Example:**
```python
# In /validate-quintet command
from sdfcvf import QuintetParity

parity = QuintetParity()
score = parity.calculate(
    code_path="packages/vif/",
    test_path="packages/vif/tests/",
    doc_path="knowledge_architecture/systems/vif/",
    spec_path="packages/vif/models/",
    tag_path="packages/vif/"  # NL tags in code
)

if score.P >= 0.90:
    print(f"✅ P = {score.P:.2f} (Production-ready)")
else:
    print(f"❌ P = {score.P:.2f} (Needs improvement)")
```

#### APOE Integration

**Workflow Orchestration:**
- Commands can create APOE plans
- `/create-plan` command generates DAGs
- Rules guide plan creation

**Example:**
```python
# In /create-system command
from apoe_runner import APOEPlanner

planner = APOEPlanner()
plan = planner.create_plan(
    goal="Create new system",
    steps=[
        {"role": "Planner", "action": "Define system architecture"},
        {"role": "Builder", "action": "Create documentation"},
        {"role": "Verifier", "action": "Validate completeness"}
    ]
)
```

#### MCP Tools Integration

**Commands Execute MCP Tools:**

```markdown
# In command markdown:

## Process

1. Store context
   ```python
   mcp_lucid-mcp_store_memory(
     key="command_execution",
     content=context,
     tags=["command", "execution"]
   )
   ```

2. Track confidence
   ```python
   mcp_lucid-mcp_track_confidence(
     operation="command_execution",
     confidence=0.85
   )
   ```

3. Update timeline
   ```python
   mcp_lucid-mcp_add_timeline_entry(
     entry_type="command_execution",
     description="/command-name executed"
   )
   ```
```

---

## Best Practices

### Rule Creation Best Practices

#### 1. Keep Always Rules Minimal

**Problem:** High context window cost

**Solution:**
```
Always rules should be < 500 lines total
Split large rules into:
- Always (critical only)
- Agent Requested (most content)
- Manual (specialized)
```

**Example:**

Instead of:
```yaml
---
alwaysApply: true
---
# Everything (2,000 lines)
```

Do this:
```yaml
# base-rules.mdc (alwaysApply: true, 300 lines)
- Critical safety protocols
- Core quality standards
- Essential operational requirements

# dynamic-rules.mdc (Agent Requested, 1,200 lines)
- Context-specific guidance
- Workflow protocols
- Best practices

# deployment.mdc (Manual, 500 lines)
- Deployment procedures
- Emergency protocols
```

#### 2. Use Specific Glob Patterns

**Problem:** Overly broad patterns load unnecessarily

**Bad:**
```yaml
globs: ["**/*"]  # Matches everything!
```

**Good:**
```yaml
globs: ["packages/**/*.py"]  # Specific to Python in packages
```

**Very Good:**
```yaml
globs: ["packages/vif/**/*.py"]  # Specific to VIF Python files
```

#### 3. Write Clear Descriptions for Agent Requested

**Problem:** AI can't decide relevance with vague descriptions

**Bad:**
```yaml
description: "Some rules"
```

**Good:**
```yaml
description: "Python coding standards for AIM-OS packages including type hints, docstrings, and NL tag requirements"
```

**Very Good:**
```yaml
description: "Dynamic context-aware rules that adapt to different task types (auditing, development, documentation, research, planning) and provide MCP tool usage patterns, quality standards, and workflow protocols for optimal AI performance"
```

**Principles:**
- Mention when rule applies (context types)
- List key topics covered
- Explain value proposition
- Use searchable keywords

#### 4. Provide Concrete Examples

**Problem:** Abstract guidance hard to apply

**Bad:**
```markdown
## Code Quality
Write good code.
```

**Good:**
```markdown
## Code Quality

### Type Hints (Required)
```python
# Bad
def process(data):
    return data.upper()

# Good
def process(data: str) -> str:
    return data.upper()
```

### Docstrings (Required)
```python
def create_witness(operation: str) -> VIFWitness:
    """Create VIF witness envelope for operation.
    
    Args:
        operation: Operation being witnessed
        
    Returns:
        VIFWitness with complete provenance
        
    Example:
        >>> witness = create_witness("data_store")
        >>> witness.operation
        'data_store'
    """
```
```

#### 5. Reference Real Files

**Problem:** Generic advice doesn't transfer

**Bad:**
```markdown
Look at examples in the codebase.
```

**Good:**
```markdown
See examples:
- `packages/vif/witness.py` - VIF witness implementation
- `packages/cmc_service/atom.py` - CMC atom structure
- `packages/hhni/dvns_physics.py` - DVNS physics implementation
```

#### 6. Version Control Rules

**Problem:** Rule changes affect AI behavior unexpectedly

**Solution:**
- Commit rule changes with clear messages
- Document why rules changed
- Test impact before committing
- Create rollback plan if needed

**Commit Message:**
```
🔧 Update dynamic-rules.mdc - Add debugging tools section

CHANGES:
- Added MCP debugging tools (get_problems, get_output_channel_logs)
- Added panel reload tools (refresh_webview)
- Updated development context protocols

RATIONALE:
- Enable faster iteration (panel reload <1s)
- Better error visibility
- Improved debugging workflow

IMPACT:
- AI agents now aware of debugging capabilities
- Faster development cycles expected
```

### Command Creation Best Practices

#### 1. Clear, Descriptive Names

**Bad:**
- `/t0` (unclear)
- `/docs` (too vague)
- `/do-stuff` (meaningless)

**Good:**
- `/create-t0-t4-docs` (clear purpose)
- `/run-tests` (obvious action)
- `/fix-nl-tags` (specific task)

#### 2. Comprehensive Workflows

**Structure:**
```markdown
# Command Name

## What This Command Does
[1-2 sentence summary]

## Process
1. Step 1 with details
2. Step 2 with details
3. Step 3 with details

## Example Usage
```
User: /command param
AI: [Expected response]
```

## Quality Gates
- [ ] Gate 1
- [ ] Gate 2

## Validation
[How to verify success]
```

#### 3. Include Context

**Problem:** AI doesn't know where files are or what to call

**Solution:**
```markdown
## Storage Location
`knowledge_architecture/AETHER_MEMORY/decision_logs/`

## Scripts to Call
```bash
python scripts/validate_goal_tree.py
python scripts/update_goal_dashboard.py
```

## Related Documentation
- `goals/GOAL_TREE.yaml` - Goal definitions
- `AETHER_MEMORY/decision_logs/` - Previous decisions
```

#### 4. Handle Edge Cases

**Consider:**
- What if file doesn't exist?
- What if tests fail?
- What if validation fails?
- What if parameters missing?

**Document:**
```markdown
## Error Handling

**If file doesn't exist:**
- Report error clearly
- Suggest correct path
- Don't create blindly

**If tests fail:**
- Show failure details
- Suggest fixes
- Don't proceed until fixed
```

#### 5. Parameter Flexibility

**Support:**
- Named parameters: `/run-tests system=VIF`
- Positional: `/run-tests VIF`
- Natural language: `/run-tests for the VIF system`

**Example:**
```markdown
## Parameters

Supports flexible parameter formats:
- `/command system-name`
- `/command for system-name`
- `/command system system-name`

AI will extract: system="system-name"
```

---

## Advanced Patterns

### Combining Rules and Commands

**Pattern:** Use rules to define standards, commands to enforce them

**Example:**

**Rule:** `python-standards.mdc`
```yaml
---
globs: ["**/*.py"]
---

# Python Standards

- Type hints required
- Docstrings required
- Tests required
- NL tags required
```

**Command:** `/code-review`
```markdown
# Code Review

## Quality Checks

Uses standards from python-standards.mdc:
- ✅ Type hints present
- ✅ Docstrings complete
- ✅ Tests comprehensive
- ✅ NL tags complete
```

**Synergy:**
- Rule defines WHAT (standards)
- Command enforces HOW (validation)
- Together ensure quality

### Chaining Commands

**Pattern:** Commands can reference other commands

**Example:**

```markdown
# /deploy-package

## Process

1. Validate everything first:
   ```
   Run: /run-tests
   Run: /validate-docs
   Run: /code-review
   ```

2. If all pass, create packages:
   ```bash
   python scripts/packaging/create_distribution.py
   ```

3. Upload to distribution channels
```

### Rule Hierarchies

**Pattern:** More specific rules override general ones

**Example:**

```
.cursor/rules/
├── python-standards.mdc (general Python standards)
└── packages/
    └── vif/
        └── .cursor/rules/
            └── vif-standards.mdc (VIF-specific overrides)
```

**VIF Standards Override:**
```yaml
---
globs: ["packages/vif/**/*.py"]
---

# VIF Python Standards

Extends general Python standards with VIF-specific requirements:

- VIF witnesses must be immutable (frozen dataclasses)
- All confidence scores must be VIFConfidence type
- Cryptographic hashes required for all witnesses
```

---

## Troubleshooting

### Rules Not Loading

**Symptoms:**
- Rule doesn't appear in context
- AI doesn't follow rule guidance

**Debugging:**

1. **Check MDC Syntax:**
   ```yaml
   ---
   alwaysApply: true  # Correct
   ---
   ```
   
   Not:
   ```yaml
   alwaysApply: true  # Missing separators
   ```

2. **Check File Extension:**
   - Must be `.mdc` for project rules
   - User rules are plain text (no extension)

3. **Check File Location:**
   - Project rules: `.cursor/rules/`
   - Not: `cursor/rules/` (missing dot)

4. **Check Glob Pattern:**
   ```yaml
   globs: ["**/*.py"]  # Correct
   globs: [**.py]      # Wrong (missing quotes)
   ```

5. **Verify in Settings:**
   - Open Cursor Settings > Rules
   - Check if rule appears in list
   - Verify status (Always Applied / Agent Decides)

### Commands Not Appearing

**Symptoms:**
- Typing `/` doesn't show command
- Command doesn't autocomplete

**Debugging:**

1. **Check File Location:**
   ```
   .cursor/commands/command-name.md  # Correct
   .cursor/command/command-name.md   # Wrong (singular)
   cursor/commands/command-name.md   # Wrong (no dot)
   ```

2. **Check File Extension:**
   - Must be `.md` (plain Markdown)
   - Not `.mdc` (that's for rules)

3. **Check File Name:**
   - Use kebab-case: `create-system.md`
   - Not: `Create System.md` or `create_system.md`

4. **Restart Cursor:**
   - Commands may need reload
   - Close and reopen Cursor
   - Check if command appears

### Archived Rules Still Loading

**Problem:** Rules in `archive/` directory still being loaded

**Cause:** Cursor scans all `.mdc` files in `.cursor/rules/` recursively

**Solution:**

**Rename to remove `.mdc` extension:**
```bash
# Disable by renaming
mv archive/old-rule.mdc archive/old-rule.mdc.DISABLED

# Or change extension
mv archive/old-rule.mdc archive/old-rule.md

# Or move outside .cursor/rules/
mv archive/old-rule.mdc ../archive-external/
```

**Verify:** Check Cursor Settings > Rules to confirm not listed

---

## Examples and Templates

### Example: Python Standards Rule

**File:** `.cursor/rules/python-standards.mdc`

```yaml
---
description: "Python coding standards for AIM-OS including type hints, docstrings, NL tags, and testing requirements"
globs: ["packages/**/*.py"]
alwaysApply: false
---

# Python Coding Standards for AIM-OS

Applied automatically when editing Python files in packages/.

## Type Safety

### Type Hints (Mandatory)

All function signatures must have complete type hints:

```python
from __future__ import annotations  # Enable forward references
from typing import Optional, List, Dict

def process_data(
    data: List[str],
    options: Optional[Dict[str, Any]] = None
) -> ProcessResult:
    """Process data with optional configuration."""
    ...
```

### Return Types

All functions must specify return type:

```python
# Good
def get_user(user_id: str) -> User:
    ...

# Also good (explicit None)
def log_event(event: str) -> None:
    ...

# Bad (no return type)
def process():
    ...
```

## Documentation

### Docstrings (Mandatory for Public Functions)

Use Google-style docstrings:

```python
def create_witness(operation: str, context: dict) -> VIFWitness:
    """Create VIF witness envelope for operation tracking.
    
    Generates cryptographic witness with complete provenance,
    enabling deterministic replay and verification.
    
    Args:
        operation: Operation being witnessed (e.g., "data_store")
        context: Operation context including inputs and state
        
    Returns:
        VIFWitness with cryptographic hash and snapshot
        
    Raises:
        ValueError: If operation is empty
        ValidationError: If context missing required fields
        
    Example:
        >>> witness = create_witness(
        ...     operation="store_memory",
        ...     context={"key": "value", "timestamp": "2025-11-05"}
        ... )
        >>> witness.operation
        'store_memory'
        >>> verify_witness(witness)
        True
    """
    ...
```

### NL Tags (Mandatory)

Tag at creation (not post-hoc):

```python
# NL_TAG: VIF-WITNESS-001 | Create VIF witness envelope | create_witness(operation: str, context: dict) -> VIFWitness | []
# NL_TAG_CONNECT: VIF-CMC-001 | Witness stored in CMC | create_witness → store_atom | [VIF-WITNESS-001, CMC-STORE-001]
# NL_TAG_INTENT: VIF-DESIGN-003 | Enables deterministic replay | cryptographic_hash + snapshot | [ADR-VIF-001]
# NL_TAG_SPEC: VIF-SPEC-001 | Validates witness schema v1.0 | validate_witness_schema | [witness_schema.json]
def create_witness(operation: str, context: dict) -> VIFWitness:
    """Create VIF witness envelope for operation tracking."""
    ...
```

## Testing

### Test Coverage (Mandatory >= 95%)

Every module must have comprehensive tests:

```python
# packages/vif/tests/test_witness.py

import pytest
from packages.vif.witness import create_witness, VIFWitness

class TestWitnessCreation:
    """Test suite for VIF witness creation."""
    
    def test_create_witness_basic(self):
        """Test basic witness creation."""
        witness = create_witness("test_op", {"key": "value"})
        assert witness.operation == "test_op"
        assert witness.context["key"] == "value"
        assert witness.witness_hash is not None
    
    def test_create_witness_empty_operation_fails(self):
        """Test witness creation fails with empty operation."""
        with pytest.raises(ValueError, match="operation cannot be empty"):
            create_witness("", {"key": "value"})
    
    def test_create_witness_deterministic_hash(self):
        """Test witness hash is deterministic."""
        witness1 = create_witness("op", {"k": "v"})
        witness2 = create_witness("op", {"k": "v"})
        assert witness1.witness_hash == witness2.witness_hash
```

### Test Organization

```
packages/system/
├── module.py
└── tests/
    ├── test_module.py (unit tests)
    ├── test_integration.py (integration tests)
    └── test_scenarios.py (realistic scenarios)
```

## Code Quality

### Patterns to Follow

**Pydantic for Validation:**
```python
from pydantic import BaseModel, Field, validator

class VIFWitness(BaseModel):
    """VIF witness envelope with validation."""
    
    operation: str = Field(..., min_length=1)
    context: Dict[str, Any]
    witness_hash: str = Field(..., pattern=r'^[a-f0-9]{64}$')
    confidence: float = Field(..., ge=0.0, le=1.0)
    
    @validator('context')
    def validate_context(cls, v):
        if 'timestamp' not in v:
            raise ValueError("context must include timestamp")
        return v
```

**Dataclasses for Simple Structures:**
```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)  # Immutable
class AtomMetadata:
    """Metadata for CMC atoms."""
    created_at: str
    updated_at: str
    version: int
    tags: list[str]
    embedding_model: Optional[str] = None
```

## Integration Standards

### CMC Integration
```python
# When storing data
from cmc_service import MemoryStore

store = MemoryStore()
atom = store.store_atom(
    modality="application/json",
    content={"data": "value"},
    tags=["system-tag", "operation-tag"]
)
```

### HHNI Integration
```python
# When retrieving knowledge
from hhni import TwoStageRetriever

retriever = TwoStageRetriever()
results = retriever.retrieve(query="bitemporal queries", k=10)
```

### VIF Integration
```python
# When tracking confidence
from vif import ConfidenceTracker

tracker = ConfidenceTracker()
tracker.track(
    operation="data_analysis",
    confidence=0.85,
    reasoning="Based on test coverage and validation"
)
```
```

**Token Cost:** ~2,000 tokens when attached

---

### Example: Auto-Attached Test Standards

**File:** `.cursor/rules/test-standards.mdc`

```yaml
---
description: "Testing standards for AIM-OS requiring comprehensive coverage, realistic scenarios, and TDD"
globs: ["**/test_*.py", "**/tests/**/*.py"]
alwaysApply: false
---

# Testing Standards for AIM-OS

Applied when editing test files.

## Test Structure

### Organization
```
packages/system/tests/
├── __init__.py
├── conftest.py (pytest fixtures)
├── test_module.py (unit tests)
├── test_integration.py (integration tests)
└── test_scenarios.py (realistic scenarios)
```

### Naming Convention

```python
class TestModuleName:
    """Test suite for ModuleName."""
    
    def test_method_name_success_case(self):
        """Test method_name with successful inputs."""
        ...
    
    def test_method_name_error_case(self):
        """Test method_name handles errors correctly."""
        ...
    
    def test_method_name_edge_case(self):
        """Test method_name with boundary conditions."""
        ...
```

## Coverage Requirements

- **Unit tests:** >= 95% coverage
- **Integration tests:** All cross-system calls
- **Edge cases:** Boundary conditions
- **Error cases:** All error paths
- **Realistic scenarios:** Real-world usage

## Test Quality

### Descriptive Names

```python
# Bad
def test_1(self):
    ...

# Good
def test_confidence_extraction_from_explicit_percentage(self):
    """Test extracting confidence from explicit percentage in text."""
    ...
```

### Independence

```python
# Bad (depends on test execution order)
class TestWithState:
    shared_state = None
    
    def test_first(self):
        self.shared_state = "value"
    
    def test_second(self):
        assert self.shared_state == "value"  # Depends on test_first!

# Good (each test independent)
class TestIndependent:
    def test_operation_a(self):
        state = initialize_state()
        result = operation_a(state)
        assert result is not None
    
    def test_operation_b(self):
        state = initialize_state()  # Fresh state each test
        result = operation_b(state)
        assert result is not None
```

### Fixtures for Reuse

```python
# conftest.py
import pytest

@pytest.fixture
def memory_store():
    """Provide MemoryStore instance for tests."""
    store = MemoryStore()
    yield store
    store.cleanup()  # Cleanup after test

@pytest.fixture
def sample_atom():
    """Provide sample atom for tests."""
    return {
        "modality": "text/plain",
        "content": "test content",
        "tags": ["test"],
        "metadata": {}
    }

# test_module.py
def test_store_atom(memory_store, sample_atom):
    """Test storing atom uses fixtures."""
    atom = memory_store.store_atom(**sample_atom)
    assert atom.atom_id is not None
```

## Performance

### Test Speed

**Target:** < 1 second per test file

**Strategies:**
- Mock external dependencies (databases, APIs)
- Use in-memory databases for tests
- Parallel test execution
- Avoid sleep() in tests

```python
# Bad (slow)
import time

def test_async_operation():
    result = async_op()
    time.sleep(2)  # Wait for completion
    assert result.done

# Good (fast)
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    result = await async_op()  # Proper async
    assert result.done
```

### Isolation

Each test should:
- Set up its own state
- Not depend on other tests
- Clean up resources
- Run in any order

```python
@pytest.fixture(autouse=True)
def reset_state():
    """Reset global state before each test."""
    GlobalState.reset()
    yield
    GlobalState.cleanup()
```
```

---

### Example: Deployment Manual Rule

**File:** `.cursor/rules/deployment.mdc`

```yaml
---
# No alwaysApply, globs, or description → Manual only
---

# Deployment Protocol

**⚠️ MANUAL RULE** - Invoke with @deployment

Critical deployment procedures. Only load during deployment operations.

## Pre-Deployment Validation

### 1. Test Suite
```bash
python -m pytest packages/ -v
```
**Requirement:** 100% pass rate

### 2. Documentation
```bash
python scripts/validate_documentation_standards.py
```
**Requirement:** All systems have current T0-T4 docs

### 3. Goal Tree
```bash
python scripts/validate_goal_tree.py
```
**Requirement:** Completion percentages accurate

### 4. Quality Audit
```bash
python scripts/system_audit.py --comprehensive
```
**Requirement:** Overall score >= 9.0/10

### 5. Security
```bash
safety check
bandit -r packages/
```
**Requirement:** No critical vulnerabilities

## Deployment Workflow

### Step 1: Version Update

**Update version numbers:**
- `setup.py` → `version="0.3.0"`
- `package.json` → `"version": "0.3.0"`
- `CHANGELOG.md` → Add release notes

### Step 2: Create Git Tag

```bash
git tag -a v0.3.0 -m "AIM-OS v0.3.0 - Context Memory Core + HHNI"
git push origin v0.3.0
```

### Step 3: Package Generation

```bash
python scripts/packaging/create_distribution.py --target all
```

**Validates:**
- Size targets met (<100MB PyPI, ~500MB Docker, ~8MB standalone)
- All dependencies included
- Installation works on clean system

### Step 4: Distribution

**PyPI:**
```bash
twine check dist/*
twine upload dist/*
```

**Docker:**
```bash
docker build -t aether/aim-os:0.3.0 .
docker build -t aether/aim-os:latest .
docker push aether/aim-os:0.3.0
docker push aether/aim-os:latest
```

**GitHub Release:**
```bash
gh release create v0.3.0 \
  --title "AIM-OS v0.3.0" \
  --notes-file CHANGELOG.md \
  dist/aim-os-standalone-0.3.0.tar.gz
```

### Step 5: Post-Deployment

- [ ] Verify installation: `pip install aim-os`
- [ ] Test MCP server starts correctly
- [ ] Validate core functionality
- [ ] Update documentation site
- [ ] Announce release

## Rollback Procedure

If deployment fails:

1. **Remove from PyPI:** Contact PyPI support (can't delete automatically)
2. **Remove Docker images:**
   ```bash
   docker rmi aether/aim-os:0.3.0
   ```
3. **Delete Git tag:**
   ```bash
   git tag -d v0.3.0
   git push origin :refs/tags/v0.3.0
   ```
4. **Document failure** in decision log
5. **Fix issues** and re-attempt with new version (0.3.1)

## Confidence Requirements

**Deploy only if:**
- Confidence >= 0.95 (deployment is irreversible)
- All validation gates passed
- Human approval obtained (Braden)
- Rollback plan documented
```

---

## Integration with AIM-OS Workflows

### Session Startup with Rules

**Workflow:**

1. **Cursor loads base-rules.mdc (Always Applied):**
   - AI reconnects with Aether identity
   - Autonomous operation protocols loaded
   - Quality standards active

2. **User opens Python file → Python standards auto-attached**

3. **User starts audit → AI decides to load dynamic-rules.mdc**

4. **Result:** Optimal context for current task

### Command-Driven Development

**Workflow:**

1. **Create new system:**
   ```
   User: /create-system for Query Optimization Engine
   AI: Creating QOE... [executes workflow]
   ```

2. **Write code with auto-attached standards**

3. **Review code:**
   ```
   User: /code-review
   AI: Reviewing... ✅ Quality excellent
   ```

4. **Run tests:**
   ```
   User: /run-tests
   AI: All tests passing ✅
   ```

5. **Update progress:**
   ```
   User: /update-goal-tree - QOE is 40% complete
   AI: Updated OBJ-XX ✅
   ```

6. **Document learnings:**
   ```
   User: /create-thought-journal about QOE implementation
   AI: Journal created ✅
   ```

### Autonomous Operation with Rules

**Pattern:**

1. **Base rules enforce:**
   - Confidence threshold >= 0.70
   - Hourly cognitive introspection
   - Quality standards

2. **Dynamic rules provide:**
   - Context-specific MCP tool usage
   - Workflow-specific protocols
   - Task-dependent standards

3. **Commands enable:**
   - One-touch complex operations
   - Standardized workflows
   - Quality automation

**Result:** AI operates autonomously with consistent quality

---

## Migration from Legacy .cursorrules

### Assessment

**Check current .cursorrules:**
```bash
# If exists
cat .cursorrules
```

**Analyze content:**
- How many lines? (if >500, should split)
- What topics covered?
- Always applicable or situational?
- Any file-specific guidance?

### Migration Strategy

**Option 1: Direct Migration (Small .cursorrules < 500 lines)**

```bash
# Copy to base-rules
cp .cursorrules .cursor/rules/base-rules.mdc

# Add frontmatter
# Edit .cursor/rules/base-rules.mdc
```

Add frontmatter at top:
```yaml
---
alwaysApply: true
---
```

**Option 2: Split Migration (Large .cursorrules > 500 lines)**

Split into multiple rules:

```
.cursorrules (1,200 lines)
  ↓
.cursor/rules/
├── base-rules.mdc (Always, 300 lines)
│   - Critical protocols
│   - Core standards
├── python-standards.mdc (Auto-Attached to *.py, 400 lines)
│   - Python-specific guidance
├── typescript-standards.mdc (Auto-Attached to *.ts, 400 lines)
│   - TypeScript-specific guidance
└── deployment.mdc (Manual @deployment, 100 lines)
    - Deployment procedures
```

**Process:**

1. **Extract critical content → base-rules.mdc**
2. **Extract Python content → python-standards.mdc (glob: *.py)**
3. **Extract TypeScript content → typescript-standards.mdc (glob: *.ts)**
4. **Extract deployment → deployment.mdc (manual)**
5. **Delete or archive .cursorrules**

### Validation After Migration

**Test:**

1. **Check rule loading:**
   - Open Cursor Settings > Rules
   - Verify all rules appear
   - Check "Always Applied" vs "Agent Decides"

2. **Test AI behavior:**
   - Start new conversation
   - Verify AI follows base rules
   - Edit Python file → Check if Python standards apply

3. **Test commands:**
   - Type `/` in chat
   - Verify commands appear
   - Execute test command

4. **Monitor token usage:**
   - Should be similar or less than before
   - Check if context window healthier

---

## System Map and Dependencies

### Rules System Dependencies

```yaml
dependencies:
  internal:
    - MDC parser (built into Cursor)
    - Glob pattern matcher (built into Cursor)
    - AI relevance engine (built into Cursor)
  
  external:
    - File system (.cursor/rules/ directory)
    - Git (version control for rules)
    - User settings (global rules storage)
  
  aim_os:
    - AETHER_MEMORY (rule change tracking)
    - Decision logs (rule evolution documentation)
    - Thought journals (rule effectiveness reflection)
```

### Commands System Dependencies

```yaml
dependencies:
  internal:
    - Command parser (built into Cursor)
    - Autocomplete engine (built into Cursor)
    - Parameter extraction (AI-driven)
  
  external:
    - File system (.cursor/commands/ directory)
    - Scripts (Python automation scripts)
    - MCP tools (command execution)
  
  aim_os:
    - CMC (storage for outputs)
    - HHNI (knowledge retrieval)
    - VIF (confidence tracking)
    - APOE (workflow orchestration)
    - Scripts (83 automation scripts)
```

### Integration Points

```yaml
integration_points:
  rules:
    - Base rules → All AI conversations
    - Python standards → Python file editing
    - Dynamic rules → Context-specific operations
    
  commands:
    - Documentation commands → CMC storage
    - Test commands → VIF tracking
    - Audit commands → HHNI indexing
    - System commands → APOE orchestration
```

---

## Performance Optimization

### Token Usage Analysis

**Baseline (Legacy .cursorrules):**
- Single file: 10,000 tokens
- Loaded always: 10,000 tokens/conversation
- Inefficient for simple tasks

**Optimized (New System):**
- Base rules: 5,000 tokens (always)
- Python standards: 2,000 tokens (when editing .py)
- Dynamic rules: 3,000 tokens (when relevant)
- Commands: 500-1,000 tokens (when invoked)

**Efficiency Gains:**
- Simple task: 5,000 tokens (vs 10,000) = 50% reduction
- Python task: 7,000 tokens (vs 10,000) = 30% reduction
- Complex task: 11,000 tokens (vs 10,000) = intentional increase for quality

### Rule Loading Optimization

**Strategies:**

1. **Minimize Always rules:**
   - Keep < 500 lines
   - Only critical content
   - Move optional content to Agent Requested

2. **Specific glob patterns:**
   - Avoid `**/*` (matches everything)
   - Use `packages/**/*.py` (specific scope)
   - Better: `packages/vif/**/*.py` (even more specific)

3. **Clear Agent Requested descriptions:**
   - AI can make better relevance decisions
   - Reduces unnecessary loading

4. **Lazy commands:**
   - Commands only load when invoked
   - No persistent token cost

---

## Quality Assurance

### Rule Quality Metrics

**Effectiveness:**
- Does AI follow rule guidance?
- Are violations caught?
- Does quality improve?

**Efficiency:**
- Token usage appropriate?
- Loading time acceptable?
- Context window healthy?

**Maintainability:**
- Rules easy to update?
- Changes tracked in version control?
- Documentation clear?

**Measurement:**

```python
# Track rule effectiveness
rule_metrics = {
    "base-rules.mdc": {
        "token_cost": 5000,
        "violations_prevented": 45,  # Over 30 days
        "quality_impact": 0.95  # Scale 0-1
    },
    "python-standards.mdc": {
        "token_cost": 2000,
        "auto_attach_frequency": 0.60,  # 60% of Python edits
        "quality_impact": 0.88
    }
}
```

### Command Quality Metrics

**Effectiveness:**
- Command usage frequency
- Success rate (workflow completed)
- Time saved vs manual execution

**Usability:**
- Parameter clarity
- Documentation completeness
- Error handling quality

**Measurement:**

```python
# Track command usage
command_metrics = {
    "/run-tests": {
        "usage_count": 127,
        "success_rate": 0.98,
        "avg_time_saved": "5 minutes",
        "user_satisfaction": 4.8  # Scale 1-5
    },
    "/create-t0-t4-docs": {
        "usage_count": 8,
        "success_rate": 1.0,
        "avg_time_saved": "2 hours",
        "user_satisfaction": 5.0
    }
}
```

---

## Security Considerations

### Rule Security

**Threats:**
- Malicious rules in cloned projects
- Sensitive data in version-controlled rules
- Team rule enforcement bypass

**Mitigations:**

1. **Review project rules before applying:**
   ```
   Settings > Rules > Project Rules
   Check each rule before enabling
   ```

2. **No credentials in rules:**
   ```yaml
   # Bad
   API_KEY = "sk-..."  # Never do this!
   
   # Good
   Use environment variables for credentials
   Reference: See .env.example for required keys
   ```

3. **Enforce team rules:**
   - Use "Enforce this rule" in team dashboard
   - Prevents users from disabling critical standards

### Command Security

**Threats:**
- Command injection via parameters
- Unintended script execution
- Sensitive data exposure

**Mitigations:**

1. **Validate parameters:**
   ```python
   # In command execution
   if system_name not in ALLOWED_SYSTEMS:
       raise ValueError(f"Invalid system: {system_name}")
   ```

2. **No shell execution without review:**
   ```markdown
   ## Security Note
   
   This command executes: `python scripts/deploy.py`
   Review script before running command.
   ```

3. **Sanitize user inputs:**
   ```python
   # Clean parameters
   import re
   clean_name = re.sub(r'[^a-zA-Z0-9_-]', '', user_input)
   ```

---

## Monitoring and Analytics

### Rule Effectiveness Tracking

**Metrics to collect:**

```yaml
rule_analytics:
  base-rules.mdc:
    loaded_count: 1547  # Times loaded
    violation_detections: 23  # Times prevented errors
    ai_compliance_rate: 0.98  # How often AI follows rules
    last_updated: "2025-11-05"
  
  python-standards.mdc:
    loaded_count: 423
    auto_attach_rate: 0.65  # % of Python edits that triggered
    code_quality_improvement: 0.15  # Measured improvement
```

**Collection Method:**

Create analytics command:
```
/analyze-rules
```

Generates report on rule usage and effectiveness.

### Command Usage Analytics

**Metrics to collect:**

```yaml
command_analytics:
  /run-tests:
    invocation_count: 127
    success_rate: 0.98
    avg_execution_time: "12 seconds"
    time_saved: "635 minutes total"
  
  /create-t0-t4-docs:
    invocation_count: 8
    success_rate: 1.0
    avg_execution_time: "8 minutes"
    time_saved: "960 minutes total"  # vs manual (2 hrs each)
```

**Collection Method:**

Store command execution in CMC:
```python
# After command completion
from cmc_service import MemoryStore

store = MemoryStore()
store.store_atom(
    modality="application/json",
    content={
        "command": "/run-tests",
        "parameters": {"system": "VIF"},
        "execution_time": 12.3,
        "success": True,
        "timestamp": "2025-11-05T18:45:00Z"
    },
    tags=["command-execution", "analytics"]
)
```

---

## Conclusion

The Cursor Rules & Commands system provides:

- **Persistent AI Context** - Rules ensure consistent AI behavior
- **Workflow Automation** - Commands reduce repetitive tasks
- **Quality Enforcement** - Standards applied automatically
- **Efficiency Gains** - Optimal token usage through intelligent selection

**AIM-OS Implementation Status:**
- ✅ Base rules deployed (essential requirements)
- ✅ Dynamic rules deployed (context-aware guidance)
- ✅ 12 core commands created
- ✅ Archive rules disabled
- ✅ Complete T0-T3 documentation

**Next Steps:**
- Create additional glob-based rules (Python, TypeScript)
- Add more domain-specific commands
- Monitor effectiveness and iterate
- Build team command library

**Confidence:** 0.95 (proven system, production-ready)

