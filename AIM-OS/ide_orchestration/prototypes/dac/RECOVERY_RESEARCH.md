# IDELayout/TopBar Recovery Research - For DAC

**Date:** 2025-11-10  
**Status:** Research Complete - Ready for DAC to implement  
**Critical:** If this fails, AIM-OS is CANCELED

---

## WHAT HAPPENED

- **IDELayout.tsx**: 0 bytes (empty) - Last modified 10:29 AM today
- **TopBar.tsx**: 0 bytes (empty) - Last modified 10:29 AM today  
- **All other files**: INTACT (23 panels, all components exist)
- **No git history**: Files were untracked
- **No backups found**

---

## REFERENCE IMPLEMENTATIONS FOUND

### 1. IDELayout Reference (packages/ide_chat_app/src/components/IDELayout.tsx)
- **Size**: 388 lines, full implementation
- **Uses**: PanelGroup, Panel, PanelResizeHandle from react-resizable-panels
- **Structure**: Left/Right/Bottom panels with resizable handles
- **State**: Uses useState for panel visibility
- **Key Pattern**: renderPanelContent() function maps panel types to components

### 2. TopBar Reference (packages/ide_chat_app/src/components/TopBar.tsx)
- **Size**: 59 lines
- **Uses**: useApp context, theme selector
- **Structure**: Logo, title, theme selector, action buttons
- **Key Pattern**: Simple header with navigation buttons

### 3. DAC's App Structure (ide_orchestration/prototypes/dac/)
- **Panel Store**: Uses Zustand (panelStore.ts) - 16KB, fully intact
- **Panel Types**: 23 panel types defined in panelStore
- **Hooks**: usePanelManagement.ts - 4KB, fully intact
- **Components**: All 23 panels exist in src/panels/
- **Views**: All views exist in src/views/

---

## WHAT NEEDS TO BE REBUILT

### IDELayout.tsx Requirements:
1. **Import PanelGroup/Panel/PanelResizeHandle** from react-resizable-panels
2. **Use usePanelStore** to get panels by zone (left/right/bottom)
3. **Use usePanelInitialization** hook to initialize default panels
4. **Use usePanelsByZone** hook to get panels for each zone
5. **Map panel types** to actual panel components (23 panels)
6. **Render panels** in PanelGroup structure (vertical for main, horizontal for zones)
7. **Include TopBar** component at top
8. **Handle main view** switching (code/evolution/consciousness/orchestration/app-preview)

### TopBar.tsx Requirements:
1. **Use usePanelStore** to get/set mainView
2. **Render navigation buttons** for each main view
3. **Show active view** with highlighted button
4. **Include app title** ("IDE DAC v2")
5. **Include settings/menu buttons** (optional)

---

## PANEL TYPE MAPPING (from panelStore.ts)

```typescript
'file-explorer' → FileTree
'memory-browser' → MemoryBrowser
'system-status' → SystemStatus
'context-web' → ContextWeb
'timeline-view' → TimelineView
'outline' → OutlinePanel
'code-editor' → CodeEditor
'terminal' → TerminalPanel
'problems' → ProblemsPanel
'evolution-explorer' → EvolutionExplorer (view)
'consciousness-visualization' → ConsciousnessVisualization (view)
'aimos-orchestration' → AIMOSOrchestration (view)
'super-index' → SuperIndexPanel
'master-index' → MasterIndexPanel
'system-map' → SystemMapPanel
'nl-tags' → NLTagsExplorerPanel
'documentation-explorer' → DocumentationExplorerPanel
'tool-quality-dashboard' → ToolQualityDashboard
'debug-console' → DebugConsolePanel
```

---

## CRITICAL ISSUES TO FIX FIRST

1. **TypeScript Error**: ConsciousnessVisualization.tsx line 582 - "')' expected"
   - This is BLOCKING the build
   - Must fix BEFORE verifying IDELayout/TopBar

2. **Missing Imports**: Verify all panel imports exist
   - Check src/panels/ directory
   - Check src/views/ directory

3. **Hook Usage**: Verify usePanelsByZone hook works correctly
   - Check usePanelManagement.ts
   - Verify it returns panels correctly

---

## RECOVERY CHECKLIST FOR DAC

- [ ] Fix TypeScript error in ConsciousnessVisualization.tsx (line 582)
- [ ] Verify all panel imports exist
- [ ] Rebuild IDELayout.tsx using:
  - [ ] PanelGroup/Panel/PanelResizeHandle from react-resizable-panels
  - [ ] usePanelStore for state
  - [ ] usePanelInitialization hook
  - [ ] usePanelsByZone hook
  - [ ] Panel type to component mapping
  - [ ] Main view rendering
- [ ] Rebuild TopBar.tsx using:
  - [ ] usePanelStore for mainView
  - [ ] Navigation buttons
  - [ ] Active view highlighting
- [ ] Test build: `npm run build`
- [ ] Test run: `npm run dev`
- [ ] Verify app renders in browser
- [ ] Verify panels work
- [ ] Verify resizing works
- [ ] Verify drag-and-drop works

---

## REFERENCE FILES

- **IDELayout Reference**: `packages/ide_chat_app/src/components/IDELayout.tsx`
- **TopBar Reference**: `packages/ide_chat_app/src/components/TopBar.tsx`
- **Panel Store**: `ide_orchestration/prototypes/dac/src/store/panelStore.ts`
- **Panel Hooks**: `ide_orchestration/prototypes/dac/src/hooks/usePanelManagement.ts`
- **All Panels**: `ide_orchestration/prototypes/dac/src/panels/`
- **All Views**: `ide_orchestration/prototypes/dac/src/views/`

---

## CRITICAL REMINDER

**If this recovery fails, AIM-OS is CANCELED.**

This is the worst crisis in a year. Everything must work perfectly.

---

**Research compiled by Aether**  
**Ready for DAC to implement**

