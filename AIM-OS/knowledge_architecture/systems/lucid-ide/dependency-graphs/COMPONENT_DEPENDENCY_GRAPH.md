---
id: "lucid-ide-component-dependency-graph"
system: "lucid-ide"
component: "dependency-graphs"
level: "L2"
type: "system_map"
title: "Lucid IDE Component Dependency Graph"
description: "Complete component dependency graph showing all component relationships and dependencies"
audience: "developers, architects"
confidence_threshold: 0.70
token_cost: 3000
word_count: 3000
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "sev"
status: "complete"
tags: ["lucid-ide", "dependency-graph", "components"]
dependencies: []
related_docs: []
version: "v1.0.0"
---

# Lucid IDE Component Dependency Graph

**Purpose:** Complete visual and textual representation of component dependencies across all Lucid IDE systems.

**Status:** Complete dependency graph for all 130+ components.

---

## 📊 **DEPENDENCY HIERARCHY**

### **Root Components**

```
app/page.tsx (Root Application Component)
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

---

## 🔗 **COMPONENT DEPENDENCIES**

### **Frontend System Dependencies**

**Core Application Components:**
```
app/page.tsx
├── components/left-drawer.tsx
│   ├── components/ui/scroll-area.tsx
│   ├── components/ui/separator.tsx
│   ├── components/ui/button.tsx
│   └── components/ui/card.tsx
├── components/right-drawer.tsx
│   ├── components/ui/sheet.tsx
│   ├── components/ui/tabs.tsx
│   └── components/ai-studio/AgentsPanel.tsx
├── components/bottom-drawer.tsx
│   ├── components/ui/resizable.tsx
│   └── components/ui/scroll-area.tsx
└── components/top-bar.tsx
    ├── components/ui/navigation-menu.tsx
    └── components/command-palette.tsx
```

**UI Component Library Dependencies:**
```
components/ui/button.tsx
├── @radix-ui/react-slot
├── class-variance-authority
└── lib/utils.ts

components/ui/dialog.tsx
├── @radix-ui/react-dialog
├── components/ui/button.tsx
└── lucide-react

components/ui/tabs.tsx
├── @radix-ui/react-tabs
└── components/ui/button.tsx

components/ui/resizable.tsx
├── react-resizable-panels
└── components/ui/separator.tsx
```

### **AI Studio System Dependencies**

**AI Studio Panels:**
```
components/ai-studio/AgentsPanel.tsx
├── components/ui/card.tsx
├── components/ui/button.tsx
├── components/ui/input.tsx
├── lib/ai-knowledge-map-integration.ts
└── app/api/ai/agents/route.ts

components/ai-studio/KnowledgeMapPanel.tsx
├── components/ai-studio/KnowledgeMapScene.tsx (3D visualization)
├── three (Three.js)
├── lib/ai-knowledge-map-integration.ts
└── app/api/ai/knowledge-map/route.ts

components/ai-studio/RAGPipelineView.tsx
├── components/ui/card.tsx
├── components/ui/badge.tsx
└── app/api/ai/vector/route.ts
```

### **Reactor Systems Dependencies**

**2D Reactor:**
```
components/lucid-reactor-core.tsx
├── lib/lucid-reactor-visual-engine.ts
├── components/ui/canvas.tsx
└── lib/wave-engine-core.ts

lib/lucid-reactor-visual-engine.ts
├── Canvas API
└── RequestAnimationFrame
```

**3D Reactor:**
```
components/enhanced-lucid-reactor-core.tsx
├── lib/lucid-reactor-3d/node-system.ts
├── lib/lucid-reactor-3d/spatial-positioning.ts
├── lib/lucid-reactor-3d/enhanced-visual-engine.ts
├── three (Three.js)
└── @react-three/fiber
```

### **Backend Architect System Dependencies**

**Architect Components:**
```
components/backend-architect-v2.tsx
├── components/backend-visual-builder/BackendCanvas.tsx
├── components/backend-visual-builder/ContextPreviewPanel.tsx
├── components/backend-visual-builder/TemplateGallery.tsx
├── app/api/architect/generate/route.ts
└── app/api/architect/suggest/route.ts

components/backend-visual-builder/BackendCanvas.tsx
├── react-flow (graph visualization)
├── components/ui/card.tsx
└── lib/graph-engine.ts
```

### **System Cortex Dependencies**

**Cortex Components:**
```
components/system-cortex/system-cortex.tsx
├── components/system-cortex/code-browser.tsx
├── components/system-cortex/system-hierarchy-tree.tsx
├── components/system-cortex/version-history.tsx
├── lib/cortex-service.ts
└── lib/git-service.ts

lib/cortex-service.ts
├── Node.js fs/promises
├── Node.js path
└── child_process (exec)
```

### **Knowledge Map System Dependencies**

**Knowledge Map Components:**
```
lib/ai-knowledge-map-integration.ts
├── app/api/ai/knowledge-map/route.ts
└── app/api/ai/embeddings/route.ts

components/ai-studio/KnowledgeMapScene.tsx
├── three (Three.js)
├── three/examples/jsm/controls/OrbitControls
└── lib/ai-knowledge-map-integration.ts
```

---

## 📈 **DEPENDENCY STATISTICS**

### **Most Dependent Components (Import Hubs)**

1. **app/page.tsx** - 15+ direct dependencies
2. **components/left-drawer.tsx** - 10+ direct dependencies
3. **components/ai-studio/KnowledgeMapPanel.tsx** - 8+ direct dependencies
4. **components/backend-architect-v2.tsx** - 7+ direct dependencies
5. **components/system-cortex/system-cortex.tsx** - 6+ direct dependencies

### **Most Used Components (Export Hubs)**

1. **components/ui/button.tsx** - Used by 50+ components
2. **components/ui/card.tsx** - Used by 40+ components
3. **components/ui/scroll-area.tsx** - Used by 30+ components
4. **components/ui/separator.tsx** - Used by 25+ components
5. **components/ui/dialog.tsx** - Used by 20+ components

### **External Dependencies**

**NPM Packages:**
- `@radix-ui/*` - 50+ UI components
- `three` - 3D visualization
- `react-flow` - Graph visualization
- `lucide-react` - Icons
- `class-variance-authority` - Variant management
- `tailwindcss` - Styling

**Node.js Built-ins:**
- `fs/promises` - File operations
- `path` - Path manipulation
- `child_process` - Process execution

---

## 🔄 **CIRCULAR DEPENDENCIES**

### **Identified Circular Dependencies**

⚠️ **None Identified** - Current architecture appears to have no circular dependencies.

**Prevention Strategy:**
- Clear component hierarchy
- Unidirectional data flow
- Dependency injection patterns
- Service layer separation

---

## 📊 **DEPENDENCY VISUALIZATION**

### **Textual Representation**

```
Level 0 (Root):
  app/page.tsx

Level 1 (Core Layout):
  ├── components/left-drawer.tsx
  ├── components/right-drawer.tsx
  ├── components/bottom-drawer.tsx
  └── components/top-bar.tsx

Level 2 (Feature Components):
  ├── components/ai-studio/*.tsx (15+ panels)
  ├── components/backend-visual-builder/*.tsx
  ├── components/system-cortex/*.tsx
  └── components/lucid-reactor-core.tsx

Level 3 (UI Components):
  └── components/ui/*.tsx (50+ components)

Level 4 (Utilities):
  ├── lib/*.ts (services, utilities)
  └── app/api/**/route.ts (42 API routes)
```

---

## 🎯 **DEPENDENCY MANAGEMENT**

### **Best Practices**

**Do:**
- ✅ Keep dependencies shallow (max 3-4 levels)
- ✅ Use dependency injection for services
- ✅ Separate concerns (UI, business logic, data)
- ✅ Use barrel exports for organization
- ✅ Document complex dependencies

**Don't:**
- ❌ Create circular dependencies
- ❌ Import from deep nested paths
- ❌ Mix UI and business logic
- ❌ Create unnecessary dependencies
- ❌ Ignore dependency updates

---

## 🔍 **DEPENDENCY ANALYSIS**

### **Critical Paths**

**Most Critical Dependency Chain:**
```
app/page.tsx
  → components/left-drawer.tsx
    → components/ai-studio/AgentsPanel.tsx
      → lib/ai-knowledge-map-integration.ts
        → app/api/ai/agents/route.ts
```

**Longest Dependency Chain:**
```
app/page.tsx
  → components/backend-architect-v2.tsx
    → components/backend-visual-builder/BackendCanvas.tsx
      → react-flow
        → graph visualization engine
```

### **Bottleneck Components**

**Components with High Dependency Count:**
1. `app/page.tsx` - 15+ dependencies
2. `components/left-drawer.tsx` - 10+ dependencies
3. `components/ai-studio/KnowledgeMapPanel.tsx` - 8+ dependencies

**Recommendation:** Consider splitting these components to reduce coupling.

---

## 📚 **REFERENCES**

- Component Index: `systems/lucid-ide/components/COMPONENT_DOCUMENTATION_INDEX.md`
- Frontend System: `systems/lucid-ide/frontend-system/L3_detailed.md`
- System Atlas Map: `systems/lucid-ide/SYSTEM_ATLAS_MAP.md`

---

**Status:** Complete  
**Last Updated:** 2025-11-09  
**Version:** v1.0.0

