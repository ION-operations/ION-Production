---
id: "cursor_rules_commands_T1_overview"
system: "cursor_rules_commands"
component: null
level: "T1"
type: "overview"
title: "Cursor Rules & Commands - Overview"
description: "500-word overview of Cursor Rules & Commands system"
audience: "architects, planners, developers"
confidence_threshold: 0.75
token_cost: 750
word_count: 500
created: "2025-11-05T18:45:00Z"
updated: "2025-11-05T18:45:00Z"
author: "aether"
status: "complete"
tags: ["cursor", "rules", "commands", "overview", "t0-t6", "transitional"]
dependencies: ["cursor_rules_commands_T0_executive"]
related_docs: ["cursor_rules_commands_T2_architecture", "base-rules.mdc", "dynamic-rules.mdc"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# Cursor Rules & Commands - Overview

## Purpose

Cursor 2.0's Rules & Commands system enables persistent AI context and workflow automation for AIM-OS development. Rules provide continuous guidance across sessions while Commands enable one-touch execution of complex tasks.

## Core Concepts

### Rules (Persistent Context)

**Rules** are MDC files (`.mdc`) providing persistent instructions to AI agents. Unlike ephemeral chat context, rules persist across sessions and automatically apply based on configuration.

**Four Rule Types:**

1. **Always Applied** (`alwaysApply: true`)
   - Loaded in every AI conversation
   - Example: `base-rules.mdc` (essential operational requirements)
   - Use for: Critical protocols, safety standards, core principles

2. **Auto-Attached** (`globs: ["**/*.py"]`)
   - Automatically included when matching files referenced
   - Example: Python standards attached when editing `.py` files
   - Use for: Language-specific standards, file-type conventions

3. **Agent Requested** (`description: "..."`)
   - AI decides whether to fetch based on relevance
   - Example: `dynamic-rules.mdc` (context-aware rules)
   - Use for: Situational guidance, workflow-specific protocols

4. **Manual** (`@ruleName`)
   - Only included when explicitly mentioned
   - Example: `@deployment` for deployment workflows
   - Use for: Specialized workflows, rare operations

### Commands (Workflow Automation)

**Commands** are plain Markdown files (`.md`) in `.cursor/commands/` triggering with `/` prefix. They encapsulate complex workflows into single commands.

**Current AIM-OS Commands:**

- `/create-t0-t4-docs` - Generate complete documentation stack
- `/run-tests` - Execute pytest with comprehensive reporting
- `/fix-nl-tags` - Auto-tag code with NL tags
- `/audit-system` - Run comprehensive system audit
- `/create-decision-log` - Generate structured decision log
- `/update-goal-tree` - Update GOAL_TREE.yaml with progress
- `/test-mcp-tools` - Verify all 59 MCP tools
- `/code-review` - Perform quality review with checks

## AIM-OS Implementation

### Rules Structure

```
.cursor/rules/
├── base-rules.mdc (Always Applied)
├── dynamic-rules.mdc (Agent Requested)
├── archive/
│   ├── aether-cursor-rules-core.mdc.DISABLED
│   └── aether-cursor-rules.mdc.DISABLED
└── [future glob-based rules]
```

### Commands Structure

```
.cursor/commands/
├── create-t0-t4-docs.md
├── run-tests.md
├── fix-nl-tags.md
├── audit-system.md
├── create-decision-log.md
├── update-goal-tree.md
├── test-mcp-tools.md
└── code-review.md
```

## Key Benefits

**For AI Agents:**
- Persistent memory across sessions
- Context-aware guidance
- Standardized workflows
- Quality enforcement

**For Developers:**
- One-touch complex operations
- Consistent standards application
- Reduced repetitive tasks
- Workflow automation

## Integration with AIM-OS

Rules & Commands integrate seamlessly with:
- **CMC** - Storage for decision logs, thought journals
- **HHNI** - Knowledge retrieval for context
- **VIF** - Confidence tracking in commands
- **APOE** - Execution planning workflows
- **SDF-CVF** - Quality enforcement via rules
- **MCP Tools** - Command execution via tools

## Status

- **Rules:** Production-ready (2 active rules, archive disabled)
- **Commands:** 8 core commands deployed
- **Documentation:** T0-T4 complete
- **Confidence:** 0.95 (proven system)

