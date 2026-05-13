---
id: "git_operation_priority_severity_summary"
system: "git_operations"
component: null
level: "T1"
type: "summary"
title: "Git Operations: Priority, Severity & Confidence Thresholds - Summary"
description: "500-word summary of how git operations should be classified by importance, severity, and priority with appropriate confidence thresholds"
audience: "all_agents"
confidence_threshold: 0.95
token_cost: 500
word_count: 500
created: "2025-11-07T20:20:00Z"
updated: "2025-11-07T20:20:00Z"
author: "dac"
status: "production"
tags: ["git", "priority", "severity", "confidence-thresholds", "summary"]
dependencies: ["GIT_OPERATION_RISK_CLASSIFICATION.md"]
related_docs: ["GIT_OPERATION_PROTOCOL.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# Git Operations: Priority, Severity & Confidence Thresholds - Summary

## Core Principle

**Operations that can cause data loss, branch confusion, or irreversible changes require HIGHER confidence thresholds regardless of frequency.**

## Key Insight

**Current Problem:** Git operations classified as "Mastery" (0.90-1.00) based on frequency, but ambiguity can cause mistakes even when confidence is actually lower.

**Solution:** Classify by **destructive potential** and **irreversibility**, not frequency. Apply tier-based confidence thresholds aligned with AIM-OS Confidence-Gated Controls.

## Risk Classification Matrix

| Risk Level | Confidence Threshold | Examples | Ambiguity Risk |
|:-----------|:---------------------|:---------|:---------------|
| **LOW** | 0.60-0.75 | `status`, `log`, `diff`, `add`, `commit` | Low |
| **MEDIUM** | 0.80 | `merge`, `cherry-pick`, `branch -d` | Medium |
| **HIGH** | 0.85 | `push`, `reset --hard`, `rebase` | **HIGH** |
| **CRITICAL** | 0.90 | `push --force`, `push --delete` | **HIGH** |

## Critical Operations Requiring High Confidence

**Operations with HIGH ambiguity risk require 0.85+ confidence:**
- **Push operations** - Branch name vs GitHub user confusion
- **Remote operations** - Which remote? Which branch?
- **Destructive operations** - Force push, branch deletion

## Integration with AIM-OS Systems

**Confidence-Gated Controls (Tier System):**
- TIER_0 (0.60): Read-only operations
- TIER_1 (0.75): Local staging, branch creation
- TIER_2 (0.85): Push operations, destructive local ops
- TIER_3 (0.90): Force push, remote deletion

**Priority Calculation:**
- High-risk git operations receive penalty in priority calculation
- Ambiguity detection increases required confidence threshold

## Mandatory Verification Protocol

**Before HIGH/CRITICAL risk operations:**
1. Verify git state (`status`, `branch -a`, `remote -v`)
2. Check for ambiguity (branch name vs GitHub user)
3. Require 0.85+ confidence if ambiguity detected
4. Ask user for clarification if confidence < threshold

## Success Criteria

- Git operations classified by risk, not frequency
- Confidence thresholds match risk levels
- Ambiguity detection prevents mistakes
- High-risk operations require verification
- Zero "sorry" messages needed

**Reference:** `knowledge_architecture/AETHER_MEMORY/protocols/GIT_OPERATION_RISK_CLASSIFICATION.md`

