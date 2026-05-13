# AIM-OS Extension Commands Guide

## Simplified Command Structure

When you type `lucid` or `aimos` in the Command Palette (Ctrl+Shift+P), you'll see these commands:

### Primary Commands (Use These)

1. **`AIM-OS: Show Dashboard`** ⭐
   - Opens the main Lucid Orchestrator Dashboard
   - This is the primary command - use this to access the dashboard
   - Command ID: `aimos.showDashboard`

2. **`AIM-OS: Debug Dashboard`**
   - Shows diagnostic information in Output panel
   - Use when troubleshooting dashboard issues
   - Command ID: `aimos.debugDashboard`

### Feature Commands

3. **`AIM-OS: Toggle Cross-Model Consciousness`**
   - Enable/disable cross-model features
   - Command ID: `aimos.toggleCrossModel`

4. **`AIM-OS: Show Memory Statistics`**
   - Display AIM-OS memory stats
   - Command ID: `aimos.showMemoryStats`

5. **`AIM-OS: Show Model Selector`**
   - Select AI model for tasks
   - Command ID: `aimos.showModelSelector`

6. **`AIM-OS: Store Memory`**
   - Store selected text in AIM-OS memory
   - Requires text selection in editor
   - Command ID: `aimos.storeMemory`

7. **`AIM-OS: Retrieve Memory`**
   - Search and retrieve memories
   - Command ID: `aimos.retrieveMemory`

8. **`AIM-OS: Create Execution Plan`**
   - Create APOE execution plan
   - Command ID: `aimos.createPlan`

9. **`AIM-OS: Track Confidence`**
   - Track confidence for tasks
   - Command ID: `aimos.trackConfidence`

### Auto-Generated Commands (Ignore These)

VS Code automatically creates commands from views. You can **ignore** these:

- `View: Show Lucid UI` - Use "Show Dashboard" instead
- `View: Toggle Lucid Orchestrator` - Use "Show Dashboard" instead
- `Lucid UI: Focus on Dashboard View` - Use "Show Dashboard" instead
- `Lucid Orchestrator: Focus on Lucid Dashboard View` - Use "Show Dashboard" instead

**All these do the same thing** - they show the dashboard. Use `AIM-OS: Show Dashboard` instead.

## Quick Access

**Shortcut:** Type `aimos` or `lucid` in Command Palette, then select:
- **"Show Dashboard"** - Main command (recommended)
- **"Debug Dashboard"** - For troubleshooting

## What Changed

**Before:** 7+ confusing commands that all did similar things
**After:** 1 primary command + 8 feature commands with clear purposes

The consolidation removes:
- ❌ `Show AIM-OS Dashboard` (duplicate)
- ❌ `Show Lucid Orchestrator Dashboard` (duplicate)
- ❌ `Show AIM-OS Tree Dashboard` (broken, removed)
- ✅ **All consolidated into `Show Dashboard`**

---

**Last Updated:** 2025-01-27  
**Version:** 1.2.0

