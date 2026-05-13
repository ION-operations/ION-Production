---
id: "cursor_rules_commands_T2_architecture"
system: "cursor_rules_commands"
component: null
level: "T2"
type: "architecture"
title: "Cursor Rules & Commands - Architecture"
description: "2000-word architecture of Cursor Rules & Commands system"
audience: "developers, architects, implementers"
confidence_threshold: 0.70
token_cost: 3000
word_count: 2000
created: "2025-11-05T18:45:00Z"
updated: "2025-11-05T18:45:00Z"
author: "aether"
status: "complete"
tags: ["cursor", "rules", "commands", "architecture", "t0-t6", "transitional"]
dependencies: ["cursor_rules_commands_T1_overview"]
related_docs: ["cursor_rules_commands_T3_detailed", "base-rules.mdc", "dynamic-rules.mdc", ".cursor/commands/"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# Cursor Rules & Commands - Architecture

## System Overview

The Cursor Rules & Commands system provides two complementary capabilities: **persistent context** (rules) and **workflow automation** (commands). Together, they enable sophisticated AI-driven development with consistent quality and reduced repetitive work.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Cursor IDE Agent                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Context Assembly                         │   │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐    │   │
│  │  │ User   │  │Project │  │  Team  │  │ User   │    │   │
│  │  │ Rules  │  │ Rules  │  │ Rules  │  │Commands│    │   │
│  │  │(Global)│  │(.cursor│  │(Server)│  │ (~/)   │    │   │
│  │  └────────┘  │/rules/)│  └────────┘  └────────┘    │   │
│  │              └────────┘                              │   │
│  │                   ↓                                   │   │
│  │         ┌──────────────────────┐                     │   │
│  │         │ Rule Selection Engine │                    │   │
│  │         │ - Always rules         │                    │   │
│  │         │ - Glob pattern match   │                    │   │
│  │         │ - AI relevance decision│                    │   │
│  │         │ - Manual @mentions     │                    │   │
│  │         └──────────────────────┘                     │   │
│  │                   ↓                                   │   │
│  │         ┌──────────────────────┐                     │   │
│  │         │  Combined AI Context  │                    │   │
│  │         │  (Rules + Conversation)│                   │   │
│  │         └──────────────────────┘                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Command Execution System                     │   │
│  │  User types: /command-name [parameters]              │   │
│  │              ↓                                         │   │
│  │  ┌──────────────────────┐                             │   │
│  │  │ Command Detection     │                             │   │
│  │  │ - Scan .cursor/commands/ │                         │   │
│  │  │ - Scan ~/.cursor/commands/│                        │   │
│  │  │ - Fetch team commands    │                         │   │
│  │  └──────────────────────┘                             │   │
│  │              ↓                                         │   │
│  │  ┌──────────────────────┐                             │   │
│  │  │ Execute Command       │                             │   │
│  │  │ - Load markdown content│                            │   │
│  │  │ - Inject into prompt   │                            │   │
│  │  │ - Execute workflow     │                            │   │
│  │  └──────────────────────┘                             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Rules System Architecture

### Rule Types and Loading

#### 1. Always Applied Rules

**Characteristics:**
- `alwaysApply: true` in frontmatter
- Loaded in every AI conversation
- Highest precedence
- Use sparingly (context window cost)

**AIM-OS Example:** `base-rules.mdc`

```yaml
---
alwaysApply: true
---

# Project Aether - Base Operational Rules

## Bitemporal Versioning
...

## Autonomous Operation Protocols
...
```

**When to Use:**
- Critical safety protocols
- Non-negotiable quality standards
- Core operational requirements
- Identity and purpose

#### 2. Auto-Attached Rules (Glob Patterns)

**Characteristics:**
- `globs: ["pattern"]` in frontmatter
- Automatically attached when files matching pattern referenced
- Efficient context usage
- File-type or directory-scoped

**Pattern Examples:**

```yaml
# Python Standards
---
globs: ["**/*.py"]
---

# TypeScript Standards  
---
globs: ["cursor-addon/**/*.ts"]
---

# Test Files
---
globs: ["**/test_*.py", "**/tests/**"]
---

# Documentation
---
globs: ["**/*.md", "knowledge_architecture/**"]
---
```

**When to Use:**
- Language-specific standards
- Directory-specific conventions
- File-type specific guidance
- Component-scoped rules

#### 3. Agent Requested Rules

**Characteristics:**
- `description: "..."` in frontmatter
- AI decides whether to fetch based on relevance
- Context-aware intelligent selection
- Reduces context window usage

**AIM-OS Example:** `dynamic-rules.mdc`

```yaml
---
description: "Dynamic context-aware rules that adapt to different task types and requirements for optimal AI performance"
contextAware: true
---

# Dynamic Context-Aware Rules

## Auditing Context Rules
...

## Development Context Rules
...
```

**Selection Criteria:**
- Task type detection (auditing, development, documentation)
- File paths being edited
- Conversation context
- Explicit mentions

**When to Use:**
- Workflow-specific guidance
- Task-dependent protocols
- Situational standards
- Optional best practices

#### 4. Manual Rules (@mention)

**Characteristics:**
- Only loaded when explicitly mentioned with `@ruleName`
- No automatic loading
- Complete control over inclusion
- Specialized workflows

**Example:**

```yaml
---
# No alwaysApply, no globs, no description
---

# Deployment Protocol

Only invoke when explicitly mentioned with @deployment

## Pre-Deployment Checklist
...
```

**When to Use:**
- Deployment procedures
- Security audits
- Rare specialized workflows
- Emergency protocols

### Rule Precedence

**Loading Order:**
1. Team Rules (highest precedence, server-enforced)
2. Project Rules (from `.cursor/rules/`)
3. User Rules (global, from settings)

**Conflict Resolution:**
When multiple rules provide guidance on same topic, earlier source takes precedence.

### Rule File Format (MDC)

**MDC (Markdown with Metadata):**

```yaml
---
alwaysApply: false
globs: ["**/*.py"]
description: "Python coding standards"
---

# Python Standards

- Use type hints
- Write docstrings
- Follow PEP 8
```

**Key Metadata Fields:**
- `alwaysApply: boolean` - Always load?
- `globs: string[]` - Auto-attach patterns
- `description: string` - For AI relevance decision
- Custom fields allowed

## Commands System Architecture

### Command Detection and Execution

**Workflow:**

1. **User Types:** `/command-name optional parameters`

2. **Detection:**
   - Cursor scans `.cursor/commands/` (project)
   - Scans `~/.cursor/commands/` (global)
   - Fetches team commands (server)

3. **Display:**
   - Shows available commands in autocomplete
   - Displays command descriptions

4. **Execution:**
   - Loads Markdown content
   - Injects into AI prompt
   - AI interprets and executes workflow

### Command File Format

**Plain Markdown:**

```markdown
# Command Name

Brief description of what command does.

## Process

1. Step 1
2. Step 2
3. Step 3

## Example

```
User: /command-name param
AI: Executing workflow...
```
```

**No MDC frontmatter** - plain Markdown only

### Command Categories

**1. Documentation Commands**

Generate, validate, update documentation:
- `/create-t0-t4-docs` - Complete T0-T4 stack
- `/update-super-index` - Update master index
- `/validate-docs` - Run validation

**2. Development Commands**

Code quality and testing:
- `/run-tests` - Execute test suite
- `/fix-nl-tags` - Auto-tag code
- `/code-review` - Quality review

**3. System Commands**

System-level operations:
- `/audit-system` - Comprehensive audit
- `/update-goal-tree` - Progress tracking
- `/test-mcp-tools` - Tool verification

**4. Memory Commands**

Documentation and learning:
- `/create-decision-log` - Structured decisions
- `/create-thought-journal` - Reflection entry
- `/store-insight` - Knowledge capture

### Parameter Handling

Commands support inline parameters:

```
/run-tests for VIF
/create-t0-t4-docs for Timeline Context System
/code-review packages/vif/witness.py
```

AI extracts parameters and uses them in workflow execution.

## Integration Architecture

### With AIM-OS Core Systems

**CMC (Context Memory Core):**
- Decision logs created by commands
- Thought journals stored
- Rule changes tracked

**HHNI (Hierarchical Index):**
- Knowledge retrieval in rules
- Context search in commands
- Documentation indexing

**VIF (Verifiable Intelligence):**
- Confidence tracking in workflows
- Witness creation for operations
- Quality validation

**SDF-CVF (Quality Framework):**
- Quintet parity enforcement via rules
- Quality gates in commands
- Test validation

### With MCP Tools

Commands trigger MCP tool execution:

```markdown
# Command: test-mcp-tools

## Process
1. Call mcp_lucid-mcp_store_memory
2. Verify response
3. Test all 59 tools
```

### With Scripts

Commands execute AIM-OS scripts:

```bash
# In command markdown
python scripts/vif_auto_tagger.py packages/vif/
python scripts/validate_goal_tree.py
python scripts/system_audit.py
```

## Storage Architecture

### File Locations

**Project Rules:**
```
.cursor/rules/
├── base-rules.mdc
├── dynamic-rules.mdc
├── python-standards.mdc
├── typescript-standards.mdc
├── deployment-protocol.mdc
└── archive/
```

**Global Rules:**
- User settings in Cursor (plain text)
- Global to all projects

**Team Rules:**
- Stored on server
- Synced to all team members
- Admin-managed

**Project Commands:**
```
.cursor/commands/
├── create-t0-t4-docs.md
├── run-tests.md
├── fix-nl-tags.md
└── [custom commands]
```

**Global Commands:**
```
~/.cursor/commands/
└── [personal commands]
```

## Performance Considerations

### Context Window Management

**Token Costs:**
- Always rules: ~5,000 tokens (constant)
- Auto-attached: ~2,000 tokens (when matched)
- Agent requested: ~3,000 tokens (when relevant)
- Commands: ~500-1,000 tokens (when invoked)

**Optimization:**
- Keep Always rules < 500 lines
- Use specific glob patterns
- Write concise commands
- Leverage Agent Requested for optional guidance

### Rule Selection Efficiency

**Glob Matching:**
- Fast pattern matching
- Only loads when files referenced
- No AI decision needed

**AI Relevance Decision:**
- Slightly slower (requires AI judgment)
- More flexible
- Better context efficiency

## Quality Assurance

### Rule Validation

**Pre-Deployment:**
- MDC syntax validation
- Glob pattern testing
- Metadata completeness

**Runtime:**
- Monitor token usage
- Track rule effectiveness
- Measure AI performance impact

### Command Validation

**Pre-Deployment:**
- Markdown syntax check
- Workflow clarity review
- Example execution test

**Usage:**
- Track command effectiveness
- User feedback collection
- Workflow improvement

## Security Considerations

### Rule Security

**Risks:**
- Malicious rules in shared projects
- Sensitive information in rules
- Team rule enforcement bypass

**Mitigations:**
- Review project rules before applying
- No credentials in rules
- Enforce team rules properly

### Command Security

**Risks:**
- Command injection
- Unintended script execution
- Sensitive data exposure

**Mitigations:**
- Validate command parameters
- No shell execution without review
- Audit command results

## Migration and Evolution

### From Legacy .cursorrules

**Old System:**
- Single `.cursorrules` file in root
- No metadata
- Always applied

**Migration Path:**
1. Move to `.cursor/rules/base-rules.mdc`
2. Add MDC frontmatter
3. Split into multiple rules if >500 lines
4. Leverage glob patterns

### Future Enhancements

**Planned:**
- More glob-based rules (Python, TypeScript specific)
- Additional workflow commands
- Team command library
- Command parameter validation
- Rule effectiveness analytics

## Best Practices

### Rules

1. **Keep Always rules minimal** - High context cost
2. **Use glob patterns liberally** - Efficient auto-attachment
3. **Write clear descriptions** - Enables AI relevance decisions
4. **Split large rules** - Multiple focused rules better than monolith
5. **Version control** - Commit rule changes

### Commands

1. **Clear naming** - Descriptive command names
2. **Comprehensive workflows** - Complete step-by-step processes
3. **Include examples** - Show expected usage
4. **Handle parameters** - Support inline parameters
5. **Document outputs** - Explain what command produces

## Summary

The Cursor Rules & Commands system provides:
- **Persistent context** via intelligent rule selection
- **Workflow automation** via slash commands
- **Quality enforcement** through always-applied standards
- **Efficiency gains** through context-aware loading

**Status:** Production-ready in AIM-OS with 2 rules, 8 commands deployed.

