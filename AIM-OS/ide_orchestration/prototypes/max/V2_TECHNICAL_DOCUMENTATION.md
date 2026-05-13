# Max V2 Technical Documentation
## Technical Decisions, Implementation Guide, API Specifications, Integration Guide

**Created:** 2025-11-08  
**Agent:** Max  
**Purpose:** Technical documentation for V2 prototype implementation  
**Status:** Phase 5 - Comprehensive Documentation  
**Confidence:** 0.90

---

## 📊 **EXECUTIVE SUMMARY**

This document provides comprehensive technical documentation for Max's V2 prototype implementation, including technical decisions, implementation guide, API specifications, and integration guide. The documentation covers: **Technical Decisions** (5-zone layout, panel-first architecture, Zustand state management, `useAIMOS` hook, component composition), **Implementation Guide** (step-by-step implementation instructions), **API Specifications** (AIM-OS integration APIs, panel APIs, layout APIs), and **Integration Guide** (AIM-OS systems integration, MCP tools integration, LUCID IDE component reuse).

**Technical Stack:**
- **Frontend:** React + TypeScript
- **State Management:** Zustand
- **Layout:** react-resizable-panels
- **Drag-and-Drop:** @hello-pangea/dnd
- **Styling:** Tailwind CSS
- **Build Tool:** Vite
- **AIM-OS Integration:** MCP tools (54 working tools)

---

## 🔧 **TECHNICAL DECISIONS**

### **1. 5-Zone Layout System**

**Decision:** Implement 5-zone layout system using `react-resizable-panels`

**Technical Details:**
- **Top Bar:** Fixed height (48px), no resizing
- **Left Drawer:** Resizable (200-600px, default 300px)
- **Main Content:** Flexible (30-70% of width, default 50%)
- **Right Drawer:** Resizable (250-500px, default 350px)
- **Bottom Drawer:** Resizable (150-400px, default 250px)

**Implementation:**
```typescript
import { PanelGroup, Panel, PanelResizeHandle } from 'react-resizable-panels';

<PanelGroup direction="vertical">
  <Panel defaultSize={48} minSize={48} maxSize={48}>
    <TopBar />
  </Panel>
  <PanelResizeHandle />
  <Panel defaultSize={100} minSize={50}>
    <PanelGroup direction="horizontal">
      <Panel defaultSize={15} minSize={10} maxSize={30}>
        <LeftDrawer />
      </Panel>
      <PanelResizeHandle />
      <Panel defaultSize={70} minSize={40}>
        <MainContent />
      </Panel>
      <PanelResizeHandle />
      <Panel defaultSize={15} minSize={10} maxSize={30}>
        <RightDrawer />
      </Panel>
    </PanelGroup>
  </Panel>
  <PanelResizeHandle />
  <Panel defaultSize={25} minSize={15} maxSize={40}>
    <BottomDrawer />
  </Panel>
</PanelGroup>
```

**Rationale:**
- Industry standard (VS Code, JetBrains use similar layouts)
- Comprehensive workspace organization
- Supports all 19+ panels effectively

---

### **2. Panel-First Architecture**

**Decision:** Treat panels as first-class citizens with comprehensive panel system

**Technical Details:**
- **Base Panel Component:** Common panel functionality (header, close button, drag handle)
- **Panel Registry:** Register all panels dynamically
- **Panel Lifecycle:** Mount/unmount, lazy loading
- **Panel State:** Panel sizes, visibility, positions, zones

**Implementation:**
```typescript
// Base Panel Component
interface BasePanelProps {
  id: string;
  title: string;
  zone: ZoneType;
  onClose?: () => void;
  children: React.ReactNode;
}

const BasePanel: React.FC<BasePanelProps> = ({ id, title, zone, onClose, children }) => {
  return (
    <div className="panel" data-panel-id={id} data-zone={zone}>
      <PanelHeader title={title} onClose={onClose} />
      <PanelContent>{children}</PanelContent>
    </div>
  );
};

// Panel Registry
const panelRegistry = new Map<string, React.ComponentType>();

const registerPanel = (id: string, component: React.ComponentType) => {
  panelRegistry.set(id, component);
};

const getPanel = (id: string): React.ComponentType | undefined => {
  return panelRegistry.get(id);
};
```

**Rationale:**
- Maximum customization
- Easy integration of diverse components
- Supports all 19+ panels effectively

---

### **3. Zustand State Management**

**Decision:** Enhance Zustand state management with comprehensive state

**Technical Details:**
- **Panel State:** Panels, zones, visibility, sizes, positions
- **Layout State:** Current layout, saved layouts, layout templates
- **AIM-OS State:** CMC atoms, HHNI nodes, VIF witnesses, SEG entities, APOE plans, SDF-CVF parity, CAS metrics, TCS entries
- **Customization State:** Panel presets, user preferences, theme settings

**Implementation:**
```typescript
import { create } from 'zustand';

interface PanelState {
  panels: Panel[];
  zones: Zone[];
  layouts: Layout[];
  currentLayout: string;
  aimosState: {
    cmc: { atoms: Atom[] };
    hhni: { nodes: Node[] };
    vif: { witnesses: Witness[] };
    seg: { entities: Entity[]; relations: Relation[] };
    apoe: { plans: Plan[] };
    sdfcvf: { parity: QuartetParity };
    cas: { metrics: CognitiveMetrics };
    tcs: { entries: TimelineEntry[] };
  };
  customization: {
    presets: PanelPreset[];
    preferences: UserPreferences;
    theme: Theme;
  };
}

const usePanelStore = create<PanelState>((set, get) => ({
  panels: [],
  zones: [],
  layouts: [],
  currentLayout: 'default',
  aimosState: {
    cmc: { atoms: [] },
    hhni: { nodes: [] },
    vif: { witnesses: [] },
    seg: { entities: [], relations: [] },
    apoe: { plans: [] },
    sdfcvf: { parity: { score: 0.90 } },
    cas: { metrics: {} },
    tcs: { entries: [] },
  },
  customization: {
    presets: [],
    preferences: {},
    theme: 'dark',
  },
  // Actions
  addPanel: (panel: Panel) => set((state) => ({ panels: [...state.panels, panel] })),
  updatePanel: (id: string, updates: Partial<Panel>) => set((state) => ({
    panels: state.panels.map((p) => (p.id === id ? { ...p, ...updates } : p)),
  })),
  removePanel: (id: string) => set((state) => ({
    panels: state.panels.filter((p) => p.id !== id),
  })),
  saveLayout: (name: string) => {
    const state = get();
    const layout: Layout = {
      id: `layout-${Date.now()}`,
      name,
      panels: state.panels,
      zones: state.zones,
      createdAt: new Date().toISOString(),
    };
    set((s) => ({ layouts: [...s.layouts, layout] }));
    // Save to CMC snapshot
    return layout;
  },
  loadLayout: (id: string) => {
    const state = get();
    const layout = state.layouts.find((l) => l.id === id);
    if (layout) {
      set({ panels: layout.panels, zones: layout.zones, currentLayout: id });
      // Restore from CMC snapshot
    }
  },
}));
```

**Rationale:**
- Lightweight and performant
- Easy to extend with AIM-OS integration
- Supports complex state (panels, layout, AIM-OS, customization)

---

### **4. `useAIMOS` Hook Implementation**

**Decision:** Implement Dac's `useAIMOS` hook for all AIM-OS systems

**Technical Details:**
- Single hook for all 8 AIM-OS systems
- Consistent API across all systems
- Error handling and loading states
- Caching and memoization

**Implementation:**
```typescript
import { useState, useEffect, useCallback } from 'react';
import { useMCPTools } from './useMCPTools';

interface AIMOSHook {
  // CMC
  cmc: {
    createAtom: (atom: Atom) => Promise<Atom>;
    getAtom: (id: string) => Promise<Atom>;
    queryAtoms: (query: Query) => Promise<Atom[]>;
    createSnapshot: () => Promise<Snapshot>;
    restoreSnapshot: (id: string) => Promise<void>;
  };
  // HHNI
  hhni: {
    search: (query: string, options: SearchOptions) => Promise<SearchResult[]>;
    navigate: (path: string) => Promise<Node>;
  };
  // VIF
  vif: {
    createWitness: (witness: Witness) => Promise<Witness>;
    getConfidence: (id: string) => Promise<number>;
    trackConfidence: (task: string, confidence: number) => Promise<void>;
  };
  // SEG
  seg: {
    addEntity: (entity: Entity) => Promise<Entity>;
    addRelation: (relation: Relation) => Promise<Relation>;
    detectContradictions: (entity: Entity) => Promise<Contradiction[]>;
  };
  // APOE
  apoe: {
    createPlan: (plan: Plan) => Promise<Plan>;
    executePlan: (planId: string) => Promise<ExecutionResult>;
    getChainSpec: (planId: string) => Promise<ChainSpec>;
  };
  // SDF-CVF
  sdfcvf: {
    validateQuartet: (change: Change) => Promise<QuartetParity>;
    enforceGates: (change: Change) => Promise<GateResult>;
  };
  // CAS
  cas: {
    analyzeCognitive: (context: Context) => Promise<CognitiveAnalysis>;
    detectDrift: () => Promise<DriftResult>;
  };
  // TCS
  tcs: {
    addTimelineEntry: (entry: TimelineEntry) => Promise<TimelineEntry>;
    getTimelineEntries: (query: TimelineQuery) => Promise<TimelineEntry[]>;
    getEvolutionExplorer: (entryId: string) => Promise<EvolutionExplorer>;
  };
}

export const useAIMOS = (): AIMOSHook => {
  const mcp = useMCPTools();
  const [cache, setCache] = useState<Map<string, any>>(new Map());

  // CMC
  const cmc = {
    createAtom: useCallback(async (atom: Atom) => {
      const result = await mcp.call('mcp_lucid-mcp_store_memory', { content: atom.content, tags: atom.tags });
      return result;
    }, [mcp]),
    getAtom: useCallback(async (id: string) => {
      const cached = cache.get(`atom-${id}`);
      if (cached) return cached;
      const result = await mcp.call('mcp_lucid-mcp_retrieve_memory', { query: id });
      setCache((c) => new Map(c).set(`atom-${id}`, result));
      return result;
    }, [mcp, cache]),
    queryAtoms: useCallback(async (query: Query) => {
      const result = await mcp.call('mcp_lucid-mcp_retrieve_memory', { query: query.text, limit: query.limit });
      return result;
    }, [mcp]),
    createSnapshot: useCallback(async () => {
      const result = await mcp.call('mcp_lucid-mcp_create_snapshot', { snapshot_name: `layout-${Date.now()}` });
      return result;
    }, [mcp]),
    restoreSnapshot: useCallback(async (id: string) => {
      await mcp.call('mcp_lucid-mcp_restore_snapshot', { snapshot_name: id });
    }, [mcp]),
  };

  // HHNI
  const hhni = {
    search: useCallback(async (query: string, options: SearchOptions) => {
      const result = await mcp.call('mcp_lucid-mcp_retrieve_memory', { query, limit: options.limit || 10 });
      return result;
    }, [mcp]),
    navigate: useCallback(async (path: string) => {
      // Navigate hierarchical index
      const result = await mcp.call('mcp_lucid-mcp_retrieve_memory', { query: path });
      return result;
    }, [mcp]),
  };

  // VIF
  const vif = {
    createWitness: useCallback(async (witness: Witness) => {
      const result = await mcp.call('mcp_lucid-mcp_track_confidence', {
        task: witness.task,
        confidence: witness.confidence_score,
        evidence: witness.evidence,
      });
      return result;
    }, [mcp]),
    getConfidence: useCallback(async (id: string) => {
      // Get confidence from VIF witness
      const result = await mcp.call('mcp_lucid-mcp_track_confidence', { task: id });
      return result.confidence || 0.5;
    }, [mcp]),
    trackConfidence: useCallback(async (task: string, confidence: number) => {
      await mcp.call('mcp_lucid-mcp_track_confidence', { task, confidence });
    }, [mcp]),
  };

  // SEG
  const seg = {
    addEntity: useCallback(async (entity: Entity) => {
      // Add entity to SEG
      const result = await mcp.call('mcp_lucid-mcp_store_memory', {
        content: JSON.stringify(entity),
        tags: { type: 'seg_entity', id: entity.id },
      });
      return result;
    }, [mcp]),
    addRelation: useCallback(async (relation: Relation) => {
      // Add relation to SEG
      const result = await mcp.call('mcp_lucid-mcp_store_memory', {
        content: JSON.stringify(relation),
        tags: { type: 'seg_relation', id: relation.id },
      });
      return result;
    }, [mcp]),
    detectContradictions: useCallback(async (entity: Entity) => {
      // Detect contradictions using SEG
      // This would require SEG-specific MCP tool (may need to be created)
      return [];
    }, []),
  };

  // APOE
  const apoe = {
    createPlan: useCallback(async (plan: Plan) => {
      const result = await mcp.call('mcp_lucid-mcp_create_plan', {
        goal: plan.goal,
        context: plan.context,
        priority: plan.priority,
      });
      return result;
    }, [mcp]),
    executePlan: useCallback(async (planId: string) => {
      // Execute plan via APOE
      // This would require APOE-specific MCP tool (may need to be created)
      return { success: true, planId };
    }, []),
    getChainSpec: useCallback(async (planId: string) => {
      // Get ChainSpec for plan
      // This would require APOE-specific MCP tool (may need to be created)
      return { planId, chain: [] };
    }, []),
  };

  // SDF-CVF
  const sdfcvf = {
    validateQuartet: useCallback(async (change: Change) => {
      // Validate quartet parity
      // This would require SDF-CVF-specific MCP tool (may need to be created)
      return { score: 0.90, passed: true };
    }, []),
    enforceGates: useCallback(async (change: Change) => {
      // Enforce quality gates
      // This would require SDF-CVF-specific MCP tool (may need to be created)
      return { passed: true };
    }, []),
  };

  // CAS
  const cas = {
    analyzeCognitive: useCallback(async (context: Context) => {
      // Analyze cognitive patterns
      // Use detect_cognitive_drift as workaround (run_cognitive_audit is broken)
      const result = await mcp.call('mcp_lucid-mcp_detect_cognitive_drift', {
        context_size_tokens: context.tokens || 0,
        error_rate: 0.0,
        working_memory_items: context.items || 0,
      });
      return result;
    }, [mcp]),
    detectDrift: useCallback(async () => {
      const result = await mcp.call('mcp_lucid-mcp_detect_cognitive_drift', {
        context_size_tokens: 0,
        error_rate: 0.0,
        working_memory_items: 0,
      });
      return result;
    }, [mcp]),
  };

  // TCS
  const tcs = {
    addTimelineEntry: useCallback(async (entry: TimelineEntry) => {
      const result = await mcp.call('mcp_lucid-mcp_add_timeline_entry', {
        prompt_id: entry.prompt_id,
        user_input: entry.user_input,
        context_state: entry.context_state,
      });
      return result;
    }, [mcp]),
    getTimelineEntries: useCallback(async (query: TimelineQuery) => {
      // Use get_timeline_entries (get_timeline_summary is broken)
      const result = await mcp.call('mcp_lucid-mcp_get_timeline_entries', {
        limit: query.limit || 50,
        start_time: query.start_time,
        end_time: query.end_time,
      });
      return result;
    }, [mcp]),
    getEvolutionExplorer: useCallback(async (entryId: string) => {
      // Get Evolution Explorer data (bidirectional Timeline ↔ Chain ↔ Goals)
      const entries = await mcp.call('mcp_lucid-mcp_get_timeline_entries', { limit: 100 });
      const goals = await mcp.call('mcp_lucid-mcp_query_goal_timeline', {});
      // Combine entries and goals for Evolution Explorer
      return { entries, goals, chains: [] };
    }, [mcp]),
  };

  return { cmc, hhni, vif, seg, apoe, sdfcvf, cas, tcs };
};
```

**Rationale:**
- Single, consistent API for all AIM-OS systems
- Easy to use, no complex setup
- Builds on existing components
- Consistent integration pattern

---

### **5. Component Composition Pattern**

**Decision:** Adopt Lex's component composition pattern

**Technical Details:**
- Base Panel component with common functionality
- Panel-specific components compose on top
- Shared UI components (confidence indicators, contradiction alerts)

**Implementation:**
```typescript
// Base Panel Component
interface BasePanelProps {
  id: string;
  title: string;
  zone: ZoneType;
  onClose?: () => void;
  children: React.ReactNode;
  showConfidence?: boolean;
  showContradictions?: boolean;
}

const BasePanel: React.FC<BasePanelProps> = ({
  id,
  title,
  zone,
  onClose,
  children,
  showConfidence = false,
  showContradictions = false,
}) => {
  const aimos = useAIMOS();
  const [confidence, setConfidence] = useState<number | null>(null);
  const [contradictions, setContradictions] = useState<Contradiction[]>([]);

  useEffect(() => {
    if (showConfidence) {
      aimos.vif.getConfidence(id).then(setConfidence);
    }
    if (showContradictions) {
      aimos.seg.detectContradictions({ id }).then(setContradictions);
    }
  }, [id, showConfidence, showContradictions, aimos]);

  return (
    <div className="panel" data-panel-id={id} data-zone={zone}>
      <PanelHeader title={title} onClose={onClose} />
      {showConfidence && confidence !== null && <ConfidenceIndicator confidence={confidence} />}
      {showContradictions && contradictions.length > 0 && <ContradictionAlert contradictions={contradictions} />}
      <PanelContent>{children}</PanelContent>
    </div>
  );
};

// Panel-Specific Component
const FileExplorerPanel: React.FC = () => {
  const aimos = useAIMOS();
  const [files, setFiles] = useState<File[]>([]);

  useEffect(() => {
    // Load files using AIM-OS
    aimos.cmc.queryAtoms({ modality: 'file' }).then((atoms) => {
      setFiles(atoms.map((atom) => JSON.parse(atom.content)));
    });
  }, [aimos]);

  return (
    <BasePanel
      id="file-explorer"
      title="File Explorer"
      zone="left"
      showConfidence={true}
      showContradictions={true}
    >
      <FileTree files={files} />
    </BasePanel>
  );
};
```

**Rationale:**
- Flexible, composable panels
- Shared UI components (confidence indicators, contradiction alerts)
- Easy to extend and maintain

---

## 📖 **IMPLEMENTATION GUIDE**

### **Step 1: Set Up Project Structure**

**Directory Structure:**
```
ide_orchestration/prototypes/max-v2/
├── src/
│   ├── components/
│   │   ├── panels/
│   │   │   ├── BasePanel.tsx
│   │   │   ├── FileExplorerPanel.tsx
│   │   │   ├── DebugConsolePanel.tsx
│   │   │   ├── ContextWebPanel.tsx
│   │   │   ├── EvolutionExplorerPanel.tsx
│   │   │   └── ...
│   │   ├── shared/
│   │   │   ├── ConfidenceIndicator.tsx
│   │   │   ├── ContradictionAlert.tsx
│   │   │   ├── VIFBadge.tsx
│   │   │   └── ...
│   │   ├── Layout.tsx
│   │   ├── TopBar.tsx
│   │   ├── LeftDrawer.tsx
│   │   ├── MainContent.tsx
│   │   ├── RightDrawer.tsx
│   │   └── BottomDrawer.tsx
│   ├── hooks/
│   │   ├── useAIMOS.ts
│   │   ├── usePanel.ts
│   │   ├── useLayout.ts
│   │   └── useCustomization.ts
│   ├── stores/
│   │   ├── panelStore.ts
│   │   └── aimosStore.ts
│   ├── types/
│   │   ├── Panel.types.ts
│   │   ├── AIMOS.types.ts
│   │   └── Layout.types.ts
│   ├── utils/
│   │   ├── mcpTools.ts
│   │   └── aimosHelpers.ts
│   └── App.tsx
├── package.json
├── vite.config.ts
└── tsconfig.json
```

**Tasks:**
- [ ] Create project structure
- [ ] Set up Vite + React + TypeScript
- [ ] Install dependencies (`react-resizable-panels`, `@hello-pangea/dnd`, `zustand`, `tailwindcss`)
- [ ] Set up TypeScript configuration
- [ ] Set up Tailwind CSS configuration

---

### **Step 2: Implement 5-Zone Layout**

**Tasks:**
- [ ] Create `Layout.tsx` with 5-zone layout
- [ ] Implement `TopBar.tsx` component
- [ ] Implement `LeftDrawer.tsx` component
- [ ] Implement `MainContent.tsx` component
- [ ] Implement `RightDrawer.tsx` component
- [ ] Implement `BottomDrawer.tsx` component
- [ ] Add resizable panels with constraints
- [ ] Test layout resizing

**Implementation:**
```typescript
// Layout.tsx
import { PanelGroup, Panel, PanelResizeHandle } from 'react-resizable-panels';
import { TopBar } from './TopBar';
import { LeftDrawer } from './LeftDrawer';
import { MainContent } from './MainContent';
import { RightDrawer } from './RightDrawer';
import { BottomDrawer } from './BottomDrawer';

export const Layout: React.FC = () => {
  return (
    <div className="h-screen flex flex-col">
      <PanelGroup direction="vertical">
        {/* Top Bar */}
        <Panel defaultSize={48} minSize={48} maxSize={48}>
          <TopBar />
        </Panel>
        <PanelResizeHandle className="h-1 bg-gray-700 hover:bg-gray-600" />
        
        {/* Main Layout */}
        <Panel defaultSize={100} minSize={50}>
          <PanelGroup direction="horizontal">
            {/* Left Drawer */}
            <Panel defaultSize={15} minSize={10} maxSize={30}>
              <LeftDrawer />
            </Panel>
            <PanelResizeHandle className="w-1 bg-gray-700 hover:bg-gray-600" />
            
            {/* Main Content */}
            <Panel defaultSize={70} minSize={40}>
              <MainContent />
            </Panel>
            <PanelResizeHandle className="w-1 bg-gray-700 hover:bg-gray-600" />
            
            {/* Right Drawer */}
            <Panel defaultSize={15} minSize={10} maxSize={30}>
              <RightDrawer />
            </Panel>
          </PanelGroup>
        </Panel>
        <PanelResizeHandle className="h-1 bg-gray-700 hover:bg-gray-600" />
        
        {/* Bottom Drawer */}
        <Panel defaultSize={25} minSize={15} maxSize={40}>
          <BottomDrawer />
        </Panel>
      </PanelGroup>
    </div>
  );
};
```

---

### **Step 3: Implement `useAIMOS` Hook**

**Tasks:**
- [ ] Create `useMCPTools.ts` hook (MCP tools connection)
- [ ] Create `useAIMOS.ts` hook (all 8 systems)
- [ ] Add error handling and loading states
- [ ] Add caching and memoization
- [ ] Test AIM-OS integration

**Implementation:**
See `useAIMOS` hook implementation above.

---

### **Step 4: Implement Base Panel Component**

**Tasks:**
- [ ] Create `BasePanel.tsx` component
- [ ] Add panel header (title, close button, drag handle)
- [ ] Add panel content area
- [ ] Add confidence indicators
- [ ] Add contradiction alerts
- [ ] Add VIF badges
- [ ] Test base panel functionality

**Implementation:**
See Base Panel component implementation above.

---

### **Step 5: Implement Panel-Specific Components**

**Tasks:**
- [ ] Enhance existing panels (File Explorer, Outline, Terminal, Problems, Main Chat)
- [ ] Create new panels (Debug Console, Context Web, Evolution Explorer, Consciousness Visualization, AIM-OS Structure Panels)
- [ ] Add AIM-OS integration to all panels
- [ ] Add bitemporal support to all panels
- [ ] Add evidence trails to all panels
- [ ] Test all panels

---

### **Step 6: Implement Customization Features**

**Tasks:**
- [ ] Implement drag-and-drop (react-beautiful-dnd or @hello-pangea/dnd)
- [ ] Implement panel grouping (tabs, accordions, stacks)
- [ ] Implement layout save/load (CMC snapshots)
- [ ] Implement panel presets
- [ ] Test customization features

---

### **Step 7: Implement Revolutionary Features**

**Tasks:**
- [ ] Implement Context Web (HHNI+SEG visualization)
- [ ] Implement Evolution Explorer (TCS+APOE bidirectional linking)
- [ ] Implement Consciousness Visualization (CAS+VIF introspection)
- [ ] Add bitemporal support throughout
- [ ] Add evidence-driven features
- [ ] Test revolutionary features

---

### **Step 8: Polish & Quality**

**Tasks:**
- [ ] Implement accessibility (WCAG 2.1 AA)
- [ ] Optimize performance (lazy loading, virtual scrolling, memoization)
- [ ] Enhance visual design
- [ ] Write comprehensive tests
- [ ] Add error handling
- [ ] Create documentation

---

## 🔌 **API SPECIFICATIONS**

### **1. AIM-OS Integration APIs**

**CMC API:**
```typescript
interface CMCAPI {
  createAtom(atom: Atom): Promise<Atom>;
  getAtom(id: string): Promise<Atom>;
  queryAtoms(query: Query): Promise<Atom[]>;
  createSnapshot(): Promise<Snapshot>;
  restoreSnapshot(id: string): Promise<void>;
}
```

**HHNI API:**
```typescript
interface HHNIAPI {
  search(query: string, options: SearchOptions): Promise<SearchResult[]>;
  navigate(path: string): Promise<Node>;
}
```

**VIF API:**
```typescript
interface VIFAPI {
  createWitness(witness: Witness): Promise<Witness>;
  getConfidence(id: string): Promise<number>;
  trackConfidence(task: string, confidence: number): Promise<void>;
}
```

**SEG API:**
```typescript
interface SEGAPI {
  addEntity(entity: Entity): Promise<Entity>;
  addRelation(relation: Relation): Promise<Relation>;
  detectContradictions(entity: Entity): Promise<Contradiction[]>;
}
```

**APOE API:**
```typescript
interface APOEAPI {
  createPlan(plan: Plan): Promise<Plan>;
  executePlan(planId: string): Promise<ExecutionResult>;
  getChainSpec(planId: string): Promise<ChainSpec>;
}
```

**SDF-CVF API:**
```typescript
interface SDFCVFAPI {
  validateQuartet(change: Change): Promise<QuartetParity>;
  enforceGates(change: Change): Promise<GateResult>;
}
```

**CAS API:**
```typescript
interface CASAPI {
  analyzeCognitive(context: Context): Promise<CognitiveAnalysis>;
  detectDrift(): Promise<DriftResult>;
}
```

**TCS API:**
```typescript
interface TCSAPI {
  addTimelineEntry(entry: TimelineEntry): Promise<TimelineEntry>;
  getTimelineEntries(query: TimelineQuery): Promise<TimelineEntry[]>;
  getEvolutionExplorer(entryId: string): Promise<EvolutionExplorer>;
}
```

---

### **2. Panel APIs**

**Panel Management API:**
```typescript
interface PanelAPI {
  addPanel(panel: Panel): void;
  updatePanel(id: string, updates: Partial<Panel>): void;
  removePanel(id: string): void;
  movePanel(id: string, targetZone: ZoneType): void;
  resizePanel(id: string, size: number): void;
  togglePanel(id: string): void;
}
```

**Layout Management API:**
```typescript
interface LayoutAPI {
  saveLayout(name: string): Promise<Layout>;
  loadLayout(id: string): Promise<void>;
  resetLayout(): void;
  getLayouts(): Layout[];
  deleteLayout(id: string): void;
}
```

---

### **3. MCP Tools API**

**MCP Tools Connection:**
```typescript
interface MCPToolsAPI {
  call(tool: string, args: any): Promise<any>;
  listTools(): Promise<Tool[]>;
  getToolInfo(tool: string): Promise<ToolInfo>;
}
```

**Implementation:**
```typescript
const useMCPTools = () => {
  const call = useCallback(async (tool: string, args: any) => {
    // Call MCP tool via HTTP endpoint or WebSocket
    const response = await fetch('http://localhost:5001/mcp/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tool, arguments: args }),
    });
    return response.json();
  }, []);

  return { call };
};
```

---

## 🔗 **INTEGRATION GUIDE**

### **1. AIM-OS Systems Integration**

**Step-by-Step Integration:**

1. **Set Up MCP Tools Connection:**
   - Install MCP server (`lucid_mcp_server.py`)
   - Configure MCP client in IDE
   - Test MCP tools connection

2. **Implement `useAIMOS` Hook:**
   - Create `useAIMOS.ts` hook
   - Implement all 8 system APIs
   - Add error handling and loading states

3. **Integrate CMC:**
   - Store panel state as CMC atoms
   - Enable time-travel queries
   - Create snapshots for layout save/load

4. **Integrate HHNI:**
   - Semantic search for file explorer
   - Context-aware code completion
   - Context Web visualization

5. **Integrate VIF:**
   - Display confidence scores
   - Confidence visualization
   - κ-gating for panel operations

6. **Integrate SEG:**
   - Context Web visualization
   - Contradiction detection
   - Evidence trails

7. **Integrate APOE:**
   - Evolution Explorer visualization
   - Orchestration management
   - Quality gates dashboard

8. **Integrate SDF-CVF:**
   - Quality gates dashboard
   - Problems panel (quartet parity violations)
   - Pre-commit gates

9. **Integrate CAS:**
   - Consciousness Visualization
   - Drift indicators
   - Self-awareness dashboard

10. **Integrate TCS:**
    - Timeline panel
    - Evolution Explorer
    - Bitemporal timeline

---

### **2. MCP Tools Integration**

**54 Working Tools Integration:**

**Core AIM-OS Tools (6):**
- `mcp_lucid-mcp_store_memory` - Store knowledge in CMC
- `mcp_lucid-mcp_retrieve_memory` - Retrieve insights from HHNI
- `mcp_lucid-mcp_get_memory_stats` - Get AIM-OS statistics
- `mcp_lucid-mcp_create_plan` - Create APOE execution plans
- `mcp_lucid-mcp_track_confidence` - Track VIF confidence
- `mcp_lucid-mcp_synthesize_knowledge` - Synthesize SEG knowledge

**Usage:**
```typescript
const aimos = useAIMOS();

// Store memory
await aimos.cmc.createAtom({ content: '...', tags: {} });

// Retrieve memory
const memories = await aimos.cmc.queryAtoms({ query: '...' });

// Track confidence
await aimos.vif.trackConfidence('task-123', 0.95);
```

**5 Broken Tools (Need Fixes):**
- CAS Tools (2): Fix method signature mismatches
- NL Tags Tools (4): Fix syntax errors in tag_parser.py
- Timeline Tools (1): Fix timedelta serialization bug

**5 Placeholders (Need Real Implementations):**
- ARD Tools (3): Replace with real AIM-OS integrations
- IIS Tools (2): Replace with real IIS implementations
- Autonomous Checklist (1): Replace with real validation

---

### **3. LUCID IDE Component Reuse**

**Reusable Components:**

**70+ Panels Available:**
- `ContextWebPanel.tsx` ✅
- `DebugConsolePanel.tsx` ✅
- `FileExplorerPanel.tsx` ✅
- `GoalPlanningPanel.tsx` ✅
- `AIMemoryPanel.tsx` ✅
- `LucidOrchestratorPanel.tsx` ✅
- `ProblemsPanel.tsx` ✅
- `TerminalPanel.tsx` ✅
- And 60+ more panels...

**Integration Steps:**
1. Copy panel components from `packages/ide_chat_app/src/components/panels/`
2. Refactor to use `BasePanel` component
3. Add AIM-OS integration via `useAIMOS` hook
4. Add bitemporal support
5. Add evidence trails
6. Test panel functionality

**Lucid Orchestrator Integration:**
1. Copy `LucidOrchestratorPanel.tsx` from `packages/ide_chat_app/src/components/`
2. Integrate as customizable panel in main content area
3. Add AIM-OS integration
4. Test 4-pane interface (Code, Blueprint, Spec, Timeline)

---

## 💬 **CONCLUSION**

This technical documentation provides comprehensive guidance for implementing Max's V2 prototype, including technical decisions, implementation guide, API specifications, and integration guide. By following this documentation, developers can implement a production-ready IDE prototype with deep AIM-OS integration and revolutionary UX.

**Confidence:** 0.90 - Comprehensive technical documentation complete, ready for implementation

---

**Status:** Phase 5.4 Complete - Technical Documentation Created  
**Next:** Phase 6 - V2 Prototype Development (foundation enhancement, feature implementation, quality & polish)

