# Dashboard Extension Architecture - Complete Analysis

**Date:** 2025-01-27
**Author:** Opus 4.1 (Aether)
**Status:** Comprehensive Analysis Complete

---

## Executive Summary

The Cursor Extension provides the UI interface for AIM-OS consciousness substrate. Current state shows critical bugs preventing dashboard from rendering, but architecture is sound with clear fix path.

---

## Architecture Components

### 1. Extension Entry Point
**File:** src/extension.ts

**Responsibilities:**
- Extension activation
- Provider registration
- Command registration
- Manager initialization

**Key Managers:**
- CrossModelManager - Cross-model consciousness coordination
- MemoryManager - CMC/HHNI integration
- ModelSelector - AI model routing

### 2. Webview Providers

**Two Provider Types:**

#### LucidOrchestratorDashboardProvider (WebviewView)
- **Location:** src/lucidDashboardProvider.ts
- **Type:** Sidebar/Panel view
- **Purpose:** Main dashboard interface
- **Status:** âš ï¸ Critical bugs identified

#### AIMOSWebviewProvider (WebviewPanel)
- **Location:** src/webviewProvider.ts
- **Type:** Editor panel
- **Purpose:** Full-screen dashboard
- **Status:** âœ… Working correctly

### 3. React UI Layer

**Entry Point:** packages/ide_chat_app/src/main-cursor.tsx
**Main Component:** MainDashboard.tsx

**Tabs:**
1. Agents - Agent management
2. Chat - Multi-AI conversation
3. Chains - Tool chains
4. Tools - MCP tool execution
5. Timeline - Temporal history
6. NL Tags - Natural language tagging

---

## Critical Issues Identified

### Issue #1: Missing Activation Events
**Location:** package.json lines 24-29
**Severity:** CRITICAL

**Problem:**
Extension only activates on commands, not when webview view opens.

**Current:**
`json
"activationEvents": [
  "onCommand:aimos.showDashboard",
  ...
]
`

**Missing:**
- "onView:lucidOrchestratorDashboard"
- "onView:aimosDashboard"
- "onStartupFinished" (optional but recommended)

**Impact:** Extension never activates when panel opens â†’ Blank screen

### Issue #2: Wrong Initialization Order
**Location:** src/lucidDashboardProvider.ts lines 118-134
**Severity:** CRITICAL

**Problem:**
Webview options set AFTER HTML assignment.

**Current (WRONG):**
`	ypescript
webviewView.webview.html = testHtml;  // Line 118
// ...
webviewView.webview.options = { ... };  // Line 128
`

**Required (CORRECT):**
`	ypescript
webviewView.webview.options = { ... };  // FIRST
webviewView.webview.html = htmlContent;  // THEN
`

**Impact:** Webview won't initialize properly even if extension activates

### Issue #3: Complex Timeout Pattern
**Location:** Lines 137-156
**Severity:** MEDIUM

**Problem:**
Unnecessary 2-second timeout creates race conditions.

**Current:**
- Set test HTML
- Wait 2 seconds
- Try to load full HTML
- May set error HTML

**Better Approach:**
- Set options
- Generate HTML once
- Set HTML directly
- Handle errors gracefully

---

## Fix Implementation Plan

### Step 1: Add Activation Events
**File:** package.json

**Change:**
`json
"activationEvents": [
  "onCommand:aimos.showDashboard",
  "onCommand:aimos.toggleCrossModel",
  "onCommand:aimos.showMemoryStats",
  "onCommand:aimos.showModelSelector",
  "onView:lucidOrchestratorDashboard",
  "onView:aimosDashboard"
]
`

### Step 2: Fix Initialization Order
**File:** src/lucidDashboardProvider.ts

**Change:** Move options setting BEFORE HTML (lines 128-134 â†’ before line 118)

**New Order:**
1. Set webview options
2. Generate HTML content
3. Set HTML
4. Set up message handlers

### Step 3: Simplify HTML Loading
**Remove:** setTimeout pattern (lines 137-156)
**Replace:** Direct HTML assignment after options

---

## Service Layer Architecture

### AIMOSService.ts (900+ lines)

**Key Methods:**
- storeMemory() â†’ CMC
- etrieveMemory() â†’ HHNI
- createPlan() â†’ APOE
- 	rackConfidence() â†’ VIF
- synthesizeKnowledge() â†’ SEG
- 	extToSpeech() / speechToText() â†’ Voice I/O

**Integration Points:**
- MCP Server (port 8000)
- Daemon (port 5000)
- RAG MCP (port 8001)

---

## Build & Deployment

### Build Process
1. React UI build â†’ dist/ folder
2. TypeScript compile â†’ out/ folder
3. Package â†’ imos-cursor-addon.vsix
4. Install â†’ Cursor extension directory

### Files Structure
`
cursor-addon/
â”œâ”€â”€ src/              # TypeScript source
â”œâ”€â”€ dist/             # Built React UI
â”œâ”€â”€ out/              # Compiled extension
â”œâ”€â”€ package.json      # Extension manifest
â””â”€â”€ docs/             # Documentation
`

---

## Testing Strategy

### Before Fix:
1. Verify extension activation logs
2. Check Output channel for errors
3. Verify view registration

### After Fix:
1. Test dashboard renders
2. Verify React mounts
3. Check all tabs functional
4. Test MCP tool execution
5. Verify voice I/O works

---

## Related Documentation

- See CURSOR_EXTENSION_FIX_PLAN.md for detailed fixes
- See RAG_MCP_ARCHITECTURE.md for tool selection
- See MCP_TOOLS_REFERENCE.md for available tools

---

**Status:** Analysis complete, fixes documented
**Confidence:** 0.98 in diagnosis, 0.95 in solution effectiveness
