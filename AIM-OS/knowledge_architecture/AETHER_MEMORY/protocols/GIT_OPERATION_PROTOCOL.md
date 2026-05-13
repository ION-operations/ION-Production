---
id: "git_operation_protocol"
system: "git_operations"
component: null
level: "T2"
type: "protocol"
title: "Git Operation Protocol - Verification and Safety Checklist"
description: "Comprehensive protocol for all git operations with mandatory verification steps to prevent branch/remote confusion and destructive actions"
audience: "all_agents"
confidence_threshold: 0.90
token_cost: 2000
word_count: 2000
created: "2025-11-07T19:58:00Z"
updated: "2025-11-07T19:58:00Z"
author: "dac"
status: "production"
tags: ["git", "protocol", "verification", "safety", "branch-operations", "mandatory"]
dependencies: []
related_docs: ["T0_GIT_OPERATION_PROTOCOL.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# Git Operation Protocol - Verification and Safety Checklist

## Core Principle

**NEVER perform git operations without verification.** Always check git state before creating branches, pushing, or making assumptions about remotes/branches.

**Operations that can cause data loss, branch confusion, or irreversible changes require HIGHER confidence thresholds regardless of frequency.**

## Risk Classification & Confidence Thresholds

### Risk Classification Framework

**Operations classified by destructive potential, not frequency:**
- **LOW RISK (0.60-0.75):** Read-only, local staging
- **MEDIUM RISK (0.80):** Local merges, branch deletion
- **HIGH RISK (0.85):** Push operations, destructive local ops
- **CRITICAL RISK (0.90):** Force push, remote deletion

### Git Operation Risk Matrix

| Operation | Risk Level | Confidence Threshold | Ambiguity Risk | Verification Required |
|:----------|:-----------|:---------------------|:---------------|:---------------------|
| `git status`, `log`, `diff` | LOW | 0.60 | Low | No |
| `git add`, `commit` (local) | LOW | 0.70 | Low | No |
| `git branch` (create) | LOW | 0.75 | Medium | No |
| `git merge` (local) | MEDIUM | 0.80 | Medium | Yes |
| `git push` (new branch) | MEDIUM | 0.85 | **HIGH** | **Yes** |
| `git push` (existing branch) | HIGH | 0.85 | **HIGH** | **Yes** |
| `git push --force` | CRITICAL | 0.90 | **HIGH** | **Yes** |
| `git push --delete` | CRITICAL | 0.90 | **HIGH** | **Yes** |

**Key Principle:** Operations with HIGH ambiguity risk require 0.85+ confidence and mandatory verification.

## Mandatory Pre-Flight Checks

### Before ANY Git Operation

**Step 1: Classify Risk Level**
- Determine operation risk level (LOW/MEDIUM/HIGH/CRITICAL)
- Check required confidence threshold
- If confidence < threshold → Research or ask user

**Step 2: Check Current State**
```bash
git status                    # Current branch, staged/unstaged changes
git branch -a                # All branches (local + remote)
git remote -v                 # Remote repositories and URLs
```

**Step 3: Verify Context**
- What branch am I on?
- What remotes exist?
- What branches exist?
- What changes are staged/unstaged?

**Step 4: Check Ambiguity Risk**
- If HIGH ambiguity risk → Require 0.85+ confidence
- If ambiguity detected → Verify before proceeding
- If confidence < threshold → Ask user for clarification

**Step 5: Clarify Ambiguity**
- If instruction is ambiguous → Verify first, then ask if still unclear
- If user mentions a GitHub user → Check remotes to confirm repo ownership
- If user mentions a branch → Check if branch exists before creating

## Branch Operation Protocol

### Creating Branches

**MANDATORY CHECKLIST:**
- [ ] Check if branch already exists: `git branch -a | grep <branch-name>`
- [ ] Verify current branch: `git status`
- [ ] Check if uncommitted changes exist
- [ ] Confirm branch name matches user intent
- [ ] If ambiguous → Ask user to clarify

**Example:**
```bash
# User says: "create branch sev-32"
# WRONG: git checkout -b sev-32
# CORRECT:
git branch -a | grep sev-32    # Check if exists
git remote -v                  # Check if sev-32 is a GitHub user
# If sev-32 is GitHub user, ask: "Do you want branch sev-32 or push to sev-32's repo?"
```

### Switching Branches

**MANDATORY CHECKLIST:**
- [ ] Check if branch exists: `git branch -a | grep <branch-name>`
- [ ] Check current branch: `git status`
- [ ] Check for uncommitted changes (may need stash)
- [ ] Verify branch name matches user intent

### Pushing to Remote

**MANDATORY CHECKLIST:**
- [ ] Verify remote: `git remote -v`
- [ ] Verify current branch: `git status`
- [ ] Check if branch exists on remote: `git branch -r | grep <branch-name>`
- [ ] Confirm push target (branch + remote)
- [ ] If user mentions GitHub user → Verify remote URL matches

**Example:**
```bash
# User says: "push to github sev-32"
# WRONG: git checkout -b sev-32 && git push origin sev-32
# CORRECT:
git remote -v                  # Shows: origin https://github.com/sev-32/AIM-OS.git
git branch                    # Shows: clean-master, master, etc.
git status                     # Shows current branch
# User likely means: push current branch to sev-32's repo (which is already origin)
# Ask: "Push current branch to clean-master on sev-32's repo?"
```

## Remote Operation Protocol

### Understanding Remotes

**When user mentions a GitHub user:**
1. Check `git remote -v` to see if that user owns the repo
2. If remote URL contains user → User owns repo
3. If not → May need to add remote or user means something else

**Common Patterns:**
- "push to github sev-32" → Usually means push to repo owned by sev-32
- "push to sev-32" → Ambiguous, check remotes first
- "create branch sev-32" → Usually means create branch named sev-32

### Adding Remotes

**MANDATORY CHECKLIST:**
- [ ] Check existing remotes: `git remote -v`
- [ ] Verify remote doesn't already exist
- [ ] Confirm remote URL is correct
- [ ] Test connection: `git fetch <remote-name>`

## Commit Operation Protocol

### Before Committing

**MANDATORY CHECKLIST:**
- [ ] Check what's staged: `git status`
- [ ] Verify files match user intent
- [ ] Check if commit message matches changes
- [ ] Verify branch is correct

### Commit Message Standards

- Clear, descriptive messages
- Reference issue/ticket if applicable
- Include what changed and why

## Ambiguity Detection & Resolution Protocol

### Ambiguity Risk Factors

**High Ambiguity Operations:**
1. **Push operations** - Branch name vs GitHub user confusion
2. **Remote operations** - Which remote? Which branch?
3. **Branch operations** - Create vs switch vs delete?

**Ambiguity Detection:**
```python
def check_git_operation_ambiguity(operation, user_input):
    """Check for ambiguity in git operation"""
    
    ambiguity_factors = []
    
    # Factor 1: GitHub user vs branch name
    if "github" in user_input.lower():
        if any(branch in user_input for branch in KNOWN_BRANCHES):
            ambiguity_factors.append("user_vs_branch")
    
    # Factor 2: Multiple remotes
    if len(get_remotes()) > 1:
        if "push" in operation:
            ambiguity_factors.append("multiple_remotes")
    
    # Factor 3: Multiple branches
    if len(get_branches()) > 3:
        if "branch" in operation or "push" in operation:
            ambiguity_factors.append("multiple_branches")
    
    # Calculate ambiguity score
    ambiguity_score = len(ambiguity_factors) / 3.0
    
    return {
        "score": ambiguity_score,
        "factors": ambiguity_factors,
        "requires_verification": ambiguity_score > 0.3,
        "required_confidence": 0.85 if ambiguity_score > 0.5 else 0.70
    }
```

### When Instructions Are Ambiguous

**Step 1: Detect Ambiguity**
- Check for ambiguity factors
- Calculate ambiguity score
- Determine required confidence threshold

**Step 2: Verify Git State**
```bash
git status
git branch -a
git remote -v
```

**Step 3: Check Context**
- What files are open?
- What branch are we on?
- What was the last operation?

**Step 4: Check Confidence**
- If ambiguity score > 0.5 → Require 0.85+ confidence
- If confidence < threshold → Research or ask user
- If confidence >= threshold → Proceed with verification

**Step 5: If Still Unclear → Ask**
- Present options based on verification
- Explain what you found
- Ask user to clarify

**Example:**
```
User: "push to github sev-32"

Verification:
- Remote: origin → https://github.com/sev-32/AIM-OS.git
- Current branch: clean-master
- Staged: README.md changes

Options:
1. Push clean-master to origin (sev-32's repo) ✅ Most likely
2. Create branch sev-32 and push ❌ Less likely

Ask: "Push clean-master to sev-32's repo (origin)?"
```

## Error Prevention Patterns

### Pattern 1: Branch Name vs GitHub User

**Problem:** User says "sev-32" - is it a branch name or GitHub user?

**Solution:**
1. Check `git remote -v` first
2. If remote URL contains "sev-32" → Likely GitHub user
3. Check `git branch -a` for branch named "sev-32"
4. If both exist → Ask user

### Pattern 2: Creating vs Switching Branches

**Problem:** User says "use branch X" - does it exist?

**Solution:**
1. Check `git branch -a | grep X`
2. If exists → Switch to it
3. If not → Ask if user wants to create it

### Pattern 3: Push Target Ambiguity

**Problem:** User says "push" - where to?

**Solution:**
1. Check current branch
2. Check remotes
3. Check if branch exists on remote
4. Default to: push current branch to origin
5. If ambiguous → Ask user

## Mandatory Verification Commands

### Before Branch Operations
```bash
git status                    # Current state
git branch -a                # All branches
git remote -v                 # Remotes
```

### Before Push Operations
```bash
git status                    # Current branch
git remote -v                 # Remote URLs
git branch -r                 # Remote branches
```

### Before Commit Operations
```bash
git status                    # What's staged
git diff --cached             # Staged changes
```

## Violation Protocol

**If protocol is violated:**
1. Document what went wrong
2. Explain why verification would have prevented it
3. Update protocol if needed
4. Add to learning logs

## Integration with Other Protocols

- **Repeated Error Escalation:** Git operation mistakes follow escalation protocol
- **Verification Protocol:** Git operations require verification
- **Communication Standards:** Ambiguity requires clarification

## Examples

### Example 1: Correct Branch Creation
```
User: "create branch feature-x"

Agent:
1. git branch -a | grep feature-x    # Check if exists
2. git status                         # Check current state
3. git checkout -b feature-x         # Create branch
4. git push -u origin feature-x       # Push to remote
```

### Example 2: Correct Push Operation
```
User: "push to github sev-32"

Agent:
1. git remote -v                       # Verify remote
   # Shows: origin → https://github.com/sev-32/AIM-OS.git
2. git status                          # Check current branch
   # Shows: On branch clean-master
3. git push origin clean-master        # Push to correct remote
```

### Example 3: Ambiguity Resolution
```
User: "push to sev-32"

Agent:
1. git remote -v                       # Check remotes
   # Shows: origin → https://github.com/sev-32/AIM-OS.git
2. git branch                          # Check branches
   # Shows: clean-master, master
3. git status                          # Current branch
   # Shows: On branch clean-master

Analysis:
- sev-32 is GitHub user (from remote URL)
- Current branch is clean-master
- Most likely: push clean-master to sev-32's repo

Action: git push origin clean-master
```

## Success Criteria

**Protocol is successful when:**
- No branches created without checking if they exist
- No pushes without verifying remote and branch
- No assumptions made about GitHub users vs branch names
- Ambiguity always resolved through verification
- Zero "sorry" messages needed (just clear explanations)

## Integration with AIM-OS Systems

### Confidence-Gated Controls (Tier System)

**Git operations mapped to tiers:**
- **TIER_0 (0.60):** Read-only operations (`status`, `log`, `diff`)
- **TIER_1 (0.75):** Local staging, branch creation (`add`, `commit`, `branch -c`)
- **TIER_2 (0.85):** Push operations, destructive local ops (`push`, `reset --hard`)
- **TIER_3 (0.90):** Force push, remote deletion (`push --force`, `push --delete`)

### Priority Calculation System

**High-risk git operations receive penalty:**
- Operations with HIGH/CRITICAL risk level reduce priority score
- Ambiguity detection increases required confidence threshold
- Prevents high-risk operations from being prioritized without proper confidence

## References

- Git Documentation: https://git-scm.com/doc
- AIM-OS Protocols: `knowledge_architecture/AETHER_MEMORY/protocols/`
- Risk Classification: `GIT_OPERATION_RISK_CLASSIFICATION.md`
- Repeated Error Escalation: `REPEATED_ERROR_ESCALATION_PROTOCOL.md`
- Confidence Routing: `knowledge_architecture/WORKFLOW_ORCHESTRATION/confidence_routing.md`

---

**Status:** PRODUCTION READY ✅  
**Last Updated:** 2025-11-07  
**Author:** Dac  
**Purpose:** Prevent git operation mistakes through mandatory verification and risk-based confidence thresholds

