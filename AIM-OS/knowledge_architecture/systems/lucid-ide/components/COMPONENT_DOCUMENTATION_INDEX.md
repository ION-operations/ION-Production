---
id: "lucid-ide-component-documentation-index"
system: "lucid-ide"
component: "components"
level: "L1"
type: "index"
title: "Lucid IDE Component Documentation Index"
description: "Comprehensive index of all Lucid IDE components with documentation status"
audience: "developers, maintainers"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "sev"
status: "complete"
tags: ["lucid-ide", "components", "documentation", "index"]
dependencies: []
related_docs: []
version: "v1.0.0"
---

# Lucid IDE Component Documentation Index

**Purpose:** Comprehensive index of all Lucid IDE components with documentation status, location, and relationships.

**Status:** Complete inventory of 130+ components across 7 systems.

---

## 📋 **COMPONENT INVENTORY**

### **UI Component Library (50+ Radix UI Components)**

**Location:** `components/ui/`

**Components:**
- `button.tsx` - Button component with variants
- `input.tsx` - Input field component
- `textarea.tsx` - Textarea component
- `select.tsx` - Select dropdown component
- `checkbox.tsx` - Checkbox component
- `radio-group.tsx` - Radio button group
- `switch.tsx` - Toggle switch component
- `dialog.tsx` - Modal dialog component
- `drawer.tsx` - Side drawer component
- `sheet.tsx` - Sheet overlay component
- `popover.tsx` - Popover component
- `tooltip.tsx` - Tooltip component
- `hover-card.tsx` - Hover card component
- `tabs.tsx` - Tab navigation component
- `accordion.tsx` - Accordion component
- `breadcrumb.tsx` - Breadcrumb navigation
- `navigation-menu.tsx` - Navigation menu
- `menubar.tsx` - Menu bar component
- `toast.tsx` - Toast notification component
- `alert.tsx` - Alert component
- `alert-dialog.tsx` - Alert dialog component
- `progress.tsx` - Progress bar component
- `table.tsx` - Table component
- `card.tsx` - Card component
- `badge.tsx` - Badge component
- `avatar.tsx` - Avatar component
- `separator.tsx` - Separator component
- `resizable.tsx` - Resizable panel component
- `scroll-area.tsx` - Scrollable area component
- `sidebar.tsx` - Sidebar component
- `chart.tsx` - Chart component (recharts wrapper)

**Documentation Status:** 
- ⚠️ Individual component docs: Pending
- ✅ Component library overview: Complete (in Frontend System L3)

**Critical Components Requiring Documentation:**
1. `button.tsx` - Most used component
2. `dialog.tsx` - Complex modal system
3. `tabs.tsx` - Tab navigation system
4. `resizable.tsx` - Panel resizing system
5. `chart.tsx` - Data visualization

---

### **AI Studio Panels (15+ Panels)**

**Location:** `components/ai-studio/`

**Panels:**
- `AgentsPanel.tsx` - Agent management panel
- `KnowledgeMapPanel.tsx` - 3D knowledge map visualization (3700+ lines ⚠️ CRITICAL)
- `ModelsPanel.tsx` - Model management panel
- `ProvidersPanel.tsx` - AI provider configuration
- `RAGPipelineView.tsx` - RAG pipeline visualization
- `VectorDBPanel.tsx` - Vector database operations
- `PerformanceMetricsPanel.tsx` - Performance monitoring
- `PoliciesPanel.tsx` - Policy configuration
- `PromptChainsPanel.tsx` - Prompt chain management
- `ToolsPanel.tsx` - Tool management
- `TemplatesPanel.tsx` - Template management
- `ExportsPanel.tsx` - Export functionality
- `SqlPanel.tsx` - SQL operations
- `SchemasPanel.tsx` - Schema management
- `MemoryPanel.tsx` - Memory management
- `CachingPanel.tsx` - Cache configuration
- `EvaluationPanel.tsx` - Evaluation metrics
- `SafetyPanel.tsx` - Safety configurations
- `RoutingPanel.tsx` - AI routing configuration
- `PlaygroundPanel.tsx` - AI playground
- `GraphPanel.tsx` - Graph visualization

**Documentation Status:**
- ⚠️ Individual panel docs: Pending
- ✅ Panel overview: Complete (in AI Studio System L3)

**Critical Panels Requiring Documentation:**
1. `KnowledgeMapPanel.tsx` - 3700+ lines, needs urgent refactoring
2. `AgentsPanel.tsx` - Core functionality
3. `ProvidersPanel.tsx` - Security-critical
4. `RAGPipelineView.tsx` - Complex visualization
5. `PerformanceMetricsPanel.tsx` - Real-time metrics

---

### **Reactor Components (2D/3D)**

**Location:** `components/`

**Components:**
- `lucid-reactor-core.tsx` - 2D canvas-based reactor
- `enhanced-lucid-reactor-core.tsx` - 3D WebGL-based reactor
- `reactor-navigation.tsx` - Reactor navigation controls

**Supporting Libraries:**
- `lib/lucid-reactor-visual-engine.ts` - 2D visual engine
- `lib/lucid-reactor-3d/node-system.ts` - 3D node system
- `lib/lucid-reactor-3d/spatial-positioning.ts` - Spatial positioning
- `lib/lucid-reactor-3d/enhanced-visual-engine.ts` - 3D visual engine

**Documentation Status:**
- ✅ Component overview: Complete (in Reactor Systems L3)
- ⚠️ Individual component docs: Pending

**Critical Components Requiring Documentation:**
1. `lucid-reactor-core.tsx` - 2D rendering system
2. `enhanced-lucid-reactor-core.tsx` - 3D rendering system
3. `lib/lucid-reactor-visual-engine.ts` - Core visual engine

---

### **Backend Architect Components**

**Location:** `components/backend-visual-builder/`

**Components:**
- `BackendCanvas.tsx` - Visual canvas for architecture design
- `ContextPreviewPanel.tsx` - Context preview panel
- `TemplateGallery.tsx` - Template gallery
- `backend-architect-v2.tsx` - Main architect component (1200+ lines ⚠️ CRITICAL)

**Documentation Status:**
- ✅ Component overview: Complete (in Backend Architect System L3)
- ⚠️ Individual component docs: Pending

**Critical Components Requiring Documentation:**
1. `BackendCanvas.tsx` - Core canvas functionality
2. `backend-architect-v2.tsx` - 1200+ lines, needs refactoring
3. `ContextPreviewPanel.tsx` - Real-time preview system

---

### **System Cortex Components**

**Location:** `components/system-cortex/`

**Components:**
- `system-cortex.tsx` - Main cortex component (900+ lines)
- `code-browser.tsx` - Code browser component
- `system-hierarchy-tree.tsx` - Hierarchy tree visualization
- `version-history.tsx` - Version history component

**Documentation Status:**
- ✅ Component overview: Complete (in System Cortex L3)
- ⚠️ Individual component docs: Pending

**Critical Components Requiring Documentation:**
1. `system-cortex.tsx` - Main orchestrator
2. `code-browser.tsx` - File navigation system
3. `system-hierarchy-tree.tsx` - Tree visualization

---

### **Core Application Components**

**Location:** `components/`

**Components:**
- `page.tsx` (app/) - Main application root (413 lines)
- `left-drawer.tsx` - Left sidebar (4700+ lines ⚠️ CRITICAL)
- `right-drawer.tsx` - Right sidebar
- `bottom-drawer.tsx` - Bottom panel
- `top-bar.tsx` - Top navigation bar
- `command-palette.tsx` - Command palette
- `keyboard-shortcuts.tsx` - Keyboard shortcuts
- `ai-context-provider.tsx` - AI context provider
- `theme-provider.tsx` - Theme provider
- `resize-handle.tsx` - Resize handle component
- `preview-area.tsx` - Preview area component

**Documentation Status:**
- ✅ Component overview: Complete (in Frontend System L3)
- ⚠️ Individual component docs: Pending

**Critical Components Requiring Documentation:**
1. `left-drawer.tsx` - 4700+ lines ⚠️ CRITICAL - needs urgent refactoring
2. `page.tsx` - Main application orchestrator
3. `command-palette.tsx` - Command system
4. `ai-context-provider.tsx` - Global state management

---

## 📊 **DOCUMENTATION PRIORITY**

### **Priority 1: Critical Large Components (Immediate)**
1. `left-drawer.tsx` (4700+ lines) - ⚠️ CRITICAL
2. `KnowledgeMapPanel.tsx` (3700+ lines) - ⚠️ CRITICAL
3. `backend-architect-v2.tsx` (1200+ lines) - ⚠️ CRITICAL
4. `system-cortex.tsx` (900+ lines)
5. `page.tsx` (413 lines)

### **Priority 2: Core Functionality Components**
1. `BackendCanvas.tsx` - Visual builder core
2. `lucid-reactor-core.tsx` - 2D reactor
3. `enhanced-lucid-reactor-core.tsx` - 3D reactor
4. `command-palette.tsx` - Command system
5. `ai-context-provider.tsx` - Global state

### **Priority 3: UI Component Library**
1. `button.tsx` - Most used component
2. `dialog.tsx` - Modal system
3. `tabs.tsx` - Tab navigation
4. `resizable.tsx` - Panel resizing
5. `chart.tsx` - Data visualization

---

## 🔗 **COMPONENT RELATIONSHIPS**

### **Dependency Graph**

```
app/page.tsx
├── TopBar
├── LeftDrawer
│   ├── FileTree
│   ├── SearchPanel
│   ├── TemplateHub
│   └── MasterDocumentationCenter
├── RightDrawer
│   ├── AIChat
│   └── ToolsPanel
├── BottomDrawer
│   ├── Terminal
│   └── Logs
└── PreviewArea
    ├── UIEditor
    └── CodeEditor
```

### **System Integration Points**

**Frontend System:**
- All UI components
- Core application components
- Theme and context providers

**AI Studio System:**
- All AI Studio panels
- Knowledge map visualization
- Provider management

**Reactor Systems:**
- 2D/3D reactor components
- Visual engines
- Particle systems

**Backend Architect System:**
- Canvas components
- Template system
- Context preview

**System Cortex:**
- Code browser
- Hierarchy tree
- Version history

---

## 📝 **DOCUMENTATION TEMPLATE**

For each component, create L0-L4 documentation:

**L0_executive.md** (100 words)
- Quick summary
- Purpose
- Key features

**L1_overview.md** (500 words)
- Overview
- Usage
- Props/API
- Examples

**L2_architecture.md** (2000 words)
- Architecture
- Implementation details
- State management
- Performance considerations

**L3_detailed.md** (10000 words)
- Complete implementation guide
- Code examples
- Testing
- Troubleshooting
- Best practices

**L4_complete.md** (15000+ words)
- Complete reference
- All edge cases
- Advanced usage
- Integration patterns

---

## ✅ **NEXT STEPS**

1. **Document Priority 1 Components** (5 components)
   - Create L0-L4 documentation for critical large components
   - Focus on refactoring guidance

2. **Document Priority 2 Components** (5 components)
   - Create L0-L4 documentation for core functionality
   - Focus on implementation patterns

3. **Document Priority 3 Components** (5 components)
   - Create L0-L2 documentation for UI components
   - Focus on usage and examples

4. **Create Component Usage Guide**
   - Comprehensive guide for using all components
   - Best practices and patterns
   - Common pitfalls

---

**Status:** Index Complete  
**Last Updated:** 2025-11-09  
**Version:** v1.0.0

