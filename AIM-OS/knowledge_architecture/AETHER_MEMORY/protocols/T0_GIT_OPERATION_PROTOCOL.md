---
id: "git_operation_protocol_T0_executive"
system: "git_operations"
component: null
level: "T0"
type: "executive_summary"
title: "Git Operation Protocol - Executive Summary"
description: "100-word executive summary of Git Operation Protocol - mandatory verification before all git operations"
audience: "executives, product_managers"
confidence_threshold: 0.95
token_cost: 100
word_count: 100
created: "2025-11-07T19:58:00Z"
updated: "2025-11-07T19:58:00Z"
author: "dac"
status: "production"
tags: ["git", "protocol", "verification", "safety", "t0-t6"]
dependencies: []
related_docs: ["GIT_OPERATION_PROTOCOL.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# Git Operation Protocol - Executive Summary

**Core Principle:** NEVER perform git operations without verification. Always check git state before creating branches, pushing, or making assumptions.

**Mandatory Checks:**
- Before branch operations: `git branch -a`, `git status`, `git remote -v`
- Before push operations: Verify remote URL, current branch, target branch
- Before commits: Verify staged changes match intent

**Ambiguity Resolution:**
- User mentions GitHub user → Check `git remote -v` first
- User mentions branch → Check `git branch -a` first
- If still unclear → Verify state, then ask user

**Impact:** Prevents branch/remote confusion, destructive operations, and unnecessary "sorry" messages. Mandatory for all git operations.

**Reference:** `knowledge_architecture/AETHER_MEMORY/protocols/GIT_OPERATION_PROTOCOL.md`

