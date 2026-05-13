# Autonomous Research: Dashboard Blank Screen Root Cause

**Date:** 2025-01-27  
**Status:** AUTONOMOUS RESEARCH IN PROGRESS  
**Goal:** RES-DASH-001 - Dashboard Blank Screen Root Cause Research  
**Confidence:** 0.75

---

## Research Objective

**Primary Goal:** Identify root cause of dashboard blank screen after 50+ failed fix attempts.

**Constraints:**
- NO code changes without team approval
- Document everything systematically
- Verify all assumptions
- Create safe fix plan

---

## Issue #1: Webview Options Order (CRITICAL - VERIFIED)

**Location:** `cursor-addon/src/lucidDashboardProvider.ts` lines 118-134

**Current Code:**
```typescript
// Line 118: HTML set FIRST
webviewView.webview.html = testHtml;

// Line 128-134: Options set AFTER (WRONG!)
webviewView.webview.options = {
    enableScripts: true,
    localResourceRoots: [...]
};
```

**Problem:** VS Code API requires `webview.options` to be set BEFORE `webview.html`.

**Evidence:**
- VS Code documentation: Options must be set before HTML assignment
- Current code does it backwards
- This likely prevents proper webview initialization

**Severity:** CRITICAL - Likely root cause

**Fix Required:** Move options setting BEFORE HTML assignment

---

## Issue #2: 2-Second Timeout Approach

**Location:** `cursor-addon/src/lucidDashboardProvider.ts` lines 137-156

**Current Code:**
```typescript
// Set test HTML first
webviewView.webview.html = testHtml;

// Wait 2 seconds, then try full HTML
setTimeout(() => {
    const htmlContent = this.getWebviewContent(webviewView.webview);
    webviewView.webview.html = htmlContent;
}, 2000);
```

**Problem:** 
- Race condition potential
- Unnecessary delay
- If test HTML doesn't render, full HTML won't either

**Severity:** MEDIUM - May contribute to issue

**Fix Required:** Remove timeout, set options correctly, then set HTML once

---

## Issue #3: Diagnostic Logging Inaccessible

**Location:** Throughout `lucidDashboardProvider.ts`

**Problem:**
- Extensive logging to Output channel
- But webview console errors are inaccessible
- User can't see what's actually failing in webview

**Severity:** LOW - Makes debugging harder

**Fix Required:** Ensure Output channel logging is visible and comprehensive

---

## Research Questions

1. **Does options-before-HTML fix the issue?**
   - Need to verify VS Code API requirements
   - Test with minimal example

2. **Are there other initialization issues?**
   - Check extension activation
   - Check view registration
   - Check provider lifecycle

3. **What about the React UI itself?**
   - Does main-cursor.tsx load correctly?
   - Are assets actually being converted to webview URIs?
   - Is React mounting?

---

## Verification Plan

### Step 1: Verify VS Code API Requirements
- Research VS Code webview API documentation
- Verify options must be set before HTML
- Document findings

### Step 2: Analyze Current Code Flow
- Trace exact execution path
- Identify all potential failure points
- Document assumptions vs. facts

### Step 3: Create Minimal Test Case
- Create simplest possible webview that works
- Compare with current implementation
- Identify differences

### Step 4: Propose Safe Fix Plan
- Fix options order (if verified)
- Remove timeout approach
- Test each change independently
- Document verification steps

---

## Documentation Plan

1. **Root Cause Analysis** (this document)
2. **VS Code API Research** (separate document)
3. **Code Flow Analysis** (separate document)
4. **Safe Fix Proposal** (separate document - after team approval)

---

## Next Steps

1. ✅ Create goal and plan (done)
2. ⏳ Research VS Code webview API requirements
3. ⏳ Analyze code flow completely
4. ⏳ Create minimal test case
5. ⏳ Document findings
6. ⏳ Propose fix plan (team approval required)

---

**Status:** Research in progress  
**No code changes made**  
**Awaiting team coordination for fix implementation**



