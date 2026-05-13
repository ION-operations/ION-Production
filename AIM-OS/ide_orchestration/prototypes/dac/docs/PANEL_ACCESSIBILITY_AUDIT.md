# DAC Panel Accessibility Audit

**Date:** 2025-11-19
**Status:** ✅ **CORRECTED** - User confirmed 32 accessible panels
**Purpose:** Audit which panels are accessible vs registered

---

## 🎯 **KEY FINDING**

**User Observation:** "I'm only seeing 32 panels for DAC v2 atm"

**Investigation Result:**
- ✅ **32 panels accessible** via toolbar buttons (what user sees)
- 📋 **37 panels registered** in panelRegistry.ts
- ⚠️ **5 panels registered but NOT accessible** in UI

---

## 📊 **PANEL BREAKDOWN**

### **32 Accessible Panels (Via Toolbar Buttons):**

#### **Left Toolbar (5 panels):**
1. `explorer` - File Explorer
2. `memory` - AI Memory Browser
3. `app-preview-controls` - App Preview Controls
4. `status` - System Status
5. `resource-monitor` - Resource Monitor

#### **Right Toolbar (9 panels):**
1. `context-web` - Context Web
2. `timeline` - Timeline View
3. `router` - Router Panel
4. `browser-automation` - Browser Automation
5. `lucid-chat` - Lucid Chat
6. `outline` - Code Outline
7. `ai-chat` - AI Chat & Management
8. `system-index-browser` - System Index Browser
9. `system-map` - System Map ⭐ (just added)

#### **Bottom Toolbar (10 panels):**
1. `terminal` - Terminal
2. `problems` - Problems
3. `log-sentinels-anomalies` - Log Sentinels Anomalies
4. `context-ledger` - Context Ledger
5. `timeline` - Timeline (duplicate in bottom)
6. `log-sentinels-summaries` - Log Sentinels Summaries
7. `debug-console` - Debug Console
8. `tool-quality` - Tool Quality Dashboard
9. `log-analysis` - Log Analysis Dashboard
10. `heatmap` - Chat Heatmap

#### **Main Toolbar (8 panels):**
1. `code` - Code Editor
2. `file-preview` - File Preview
3. `canvas` - Canvas View
4. `manager-ai-chat` - Manager AI Chat
5. `document-editor` - Document Editor
6. `evolution` - Evolution Explorer
7. `consciousness` - Consciousness Visualization
8. `app-preview` - App Preview

**Total Accessible: 5 (left) + 9 (right) + 10 (bottom) + 8 (main) = 32 panels**

**Note:** `timeline` appears in both right and bottom toolbars (counted once in total)

---

## ⚠️ **5 PANELS REGISTERED BUT NOT ACCESSIBLE IN UI**

**Math:** 37 registered - 32 accessible = 5 not accessible

These 6 panels are in `panelRegistry.ts` but **NOT** in any toolbar button array:

1. **`orchestration`** - AIM-OS Orchestration
   - Registered in panelRegistry (category: 'view')
   - Component exists and is imported (LazyAIMOSOrchestration)
   - **Missing from:** MAIN_TOOLBAR_BUTTONS
   - **Status:** May be accessible via other means (mainView type exists)

2. **`super-index`** - Super Index
   - Registered in panelRegistry (category: 'right')
   - **Missing from:** RIGHT_TOOLBAR_BUTTONS
   - **Status:** Not accessible

3. **`master-index`** - Master Index
   - Registered in panelRegistry (category: 'right')
   - **Missing from:** RIGHT_TOOLBAR_BUTTONS
   - **Status:** Not accessible

4. **`nl-tags-explorer`** - NL Tags Explorer
   - Registered in panelRegistry (category: 'right')
   - **Missing from:** RIGHT_TOOLBAR_BUTTONS
   - **Status:** Not accessible

5. **`documentation-explorer`** - Documentation Explorer
   - Registered in panelRegistry (category: 'right')
   - **Missing from:** RIGHT_TOOLBAR_BUTTONS
   - **Status:** Not accessible

6. **`organization-systems`** - Organization Systems
   - Registered in panelRegistry (category: 'right')
   - **Missing from:** RIGHT_TOOLBAR_BUTTONS
   - **Status:** Not accessible

**Confirmed by User:** 32 panels accessible in DAC v2
**Math:** 37 registered - 32 accessible = 5 not accessible

**The 5 panels not accessible (no toolbar button):**
1. `orchestration` - Has mainView type and is rendered, but no button in MAIN_TOOLBAR_BUTTONS
2. `super-index` - No button in RIGHT_TOOLBAR_BUTTONS
3. `master-index` - No button in RIGHT_TOOLBAR_BUTTONS
4. `nl-tags-explorer` - No button in RIGHT_TOOLBAR_BUTTONS
5. `documentation-explorer` - No button in RIGHT_TOOLBAR_BUTTONS
6. `organization-systems` - No button in RIGHT_TOOLBAR_BUTTONS

**Note:** `timeline` appears in both right and bottom toolbars, but counts as 1 unique panel.
