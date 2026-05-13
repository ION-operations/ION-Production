---
id: "orchestration_builder_T1_overview"
system: "orchestration_builder"
component: null
level: "T1"
type: "overview"
title: "Orchestration Builder Overview"
description: "500-word overview of Orchestration Builder system"
audience: "architects, planners"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-18T00:00:00Z"
updated: "2025-11-18T00:00:00Z"
author: "aether"
status: "complete"
tags: ["orchestration_builder", "sub-layer", "apoe", "orchestration", "t1"]
dependencies: ["orchestration_builder_T0_executive"]
related_docs: ["orchestration_builder_T2_architecture"]
version: "1.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Orchestration Builder - T1 Overview (≈500 words)

## Purpose & Scope

**Orchestration Builder** is a sub-layer of APOE (AI-Powered Orchestration Engine) that provides plan building capabilities. It constructs execution plans from natural language intent, role assignments, and step definitions. The system is an internal component of APOE, handling the plan construction phase before execution by the DAG executor.

**Core Guarantees:**
- **Plan Construction:** Builds execution plans from natural language intent
- **Role Assignment:** Assigns roles to plan steps
- **Step Definition:** Defines execution steps with dependencies
- **Budget Management:** Integrates budget constraints into plans
- **Gate Integration:** Adds quality/safety gates to plans

**Primary Use Cases:**
- Build execution plans from user intent
- Assign roles to plan steps
- Define step dependencies
- Integrate budget constraints
- Add quality/safety gates

## Components

**1. PlanBuilder**
- Constructs execution plans from natural language intent
- Defines plan structure and steps
- Integrates budget and gate constraints

**2. RoleAssigner**
- Assigns roles to plan steps
- Integrates with Role Dispatcher for optimal role selection
- Handles role capability matching

**3. StepDefiner**
- Defines execution steps with dependencies
- Creates step dependency graph
- Handles step requirements and constraints

**4. BudgetIntegrator**
- Integrates budget constraints into plans
- Handles token, time, and tool budgets
- Validates budget feasibility

## Architecture

Orchestration Builder uses a plan construction architecture:
- **Intent Parsing:** Parses natural language intent
- **Plan Construction:** Builds execution plan structure
- **Role Assignment:** Assigns roles to steps
- **Step Definition:** Defines steps with dependencies
- **Constraint Integration:** Integrates budgets and gates

The system is an internal component of APOE, working with ACL compiler, Role Dispatcher, and DAG executor.

## Integration

**Integrates With:**
- **APOE:** Internal component (sub-layer)
- **ACL Compiler:** Uses ACL for plan language
- **Role Dispatcher:** Uses role selection for assignments
- **DAG Executor:** Provides plans for execution
- **Gate Manager:** Integrates gates into plans
- **Budget Tracker:** Integrates budgets into plans

**Relationship to APOE:**
- **Sub-Layer Type:** Internal component of APOE
- **Integration:** Part of APOE plan construction pipeline
- **Design Philosophy:** Plan building as sub-layer of orchestration

## Relationship to APOE

Orchestration Builder is a **Sub-Layer System** within APOE:
- **Sub-Layer Type:** Internal component of APOE
- **Integration:** Part of APOE plan construction pipeline
- **Design Philosophy:** Plan building as sub-layer of orchestration
- **Classification:** Sub-Layer System (sub-layer of APOE)

## Status

**Package:** `packages/orchestration_builder/` (5 Python files)
**Status:** ✅ Implemented
**Documentation:** ✅ T0-T1 complete (this document)
**Integration:** ✅ Part of APOE (sub-layer)

---

**Next:** T2 Architecture (detailed architecture documentation)

