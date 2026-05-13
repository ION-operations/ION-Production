# IDE Layout Prototype - Lex Design Document
## AIM-OS Native + Revolutionary Features

**Author:** Lex  
**Date:** 2025-11-07  
**Status:** Design Phase  
**Focus:** AIM-OS Integration + Past Learnings + Revolutionary Features  
**Competition:** IDE Layout Prototype Mission

---

## 🎯 **PROTOTYPE DIFFERENTIATION**

### **Lex's Prototype vs Codex's Prototype**

**Lex's Prototype (This Document):**
- **Approach:** AIM-OS Native First - Deep integration with all AIM-OS systems
- **Foundation:** Built from scratch, leveraging past IDE implementations (`IDELayout.tsx`, `MonacoEditor.tsx`, etc.)
- **Unique Features:** Context Web, Evolution Explorer, Consciousness Visualization, VIF confidence indicators
- **Focus:** Making invisible AIM-OS systems visible and actionable
- **Panels:** 20+ panels with deep AIM-OS integration
- **Status:** Independent prototype - Lex's own design and implementation

**Codex's Prototype (`IDE_LAYOUT_PROTOTYPE_CODEX.md`):**
- **Approach:** Architecture-First - Extends existing Lucid Orchestrator
- **Foundation:** Builds on Codex's existing Lucid Orchestrator work (`packages/lucid_orchestrator/`)
- **Unique Features:** Lucid Orchestrator four-pane interface, ChainSpec visualization, orchestration canvas
- **Focus:** Architecture visualization and orchestration management
- **Panels:** Extends Lucid Orchestrator with ChainSpec and orchestration panels
- **Status:** Extension of Codex's existing work - Lex completing Codex's design

**Key Difference:**
- **Lex:** New prototype from scratch, AIM-OS-native, revolutionary UX features
- **Codex:** Extension of existing Lucid Orchestrator, architecture-first, orchestration-focused

---

---

## 🎯 **DESIGN PHILOSOPHY**

### **Core Principle: AIM-OS Native First**

This prototype is built from the ground up with AIM-OS systems as **first-class citizens**, not afterthoughts. Every panel, every interaction, every workflow is designed to leverage AIM-OS capabilities naturally and seamlessly.

### **Key Design Pillars:**

1. **Deep AIM-OS Integration** - CMC, HHNI, VIF, APOE, SEG, TCS, IIS, SCOR are not optional features, they're the foundation
2. **Past Learnings Applied** - Patterns from `IDELayout.tsx`, `MonacoEditor.tsx`, `FileTree.tsx` refined and enhanced
3. **Revolutionary Features** - Context Web, Evolution Explorer, Consciousness Visualization as core panels
4. **Developer Workflow Optimization** - Every feature serves actual coding workflows, not just looks cool
5. **Systematic Architecture** - Error boundaries, loading states, proper state management from day one

---

## 🏗️ **ARCHITECTURE OVERVIEW**

### **System Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    IDE Layout Prototype                      │
│                    (AIM-OS Native)                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Panel Layer │  │  State Layer │  │  AIM-OS Layer│      │
│  │  (React)     │→ │  (Zustand)   │→ │  (Hooks)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                    │             │
│         └─────────────────┴────────────────────┘            │
│                            │                                  │
│                    ┌───────▼────────┐                        │
│                    │  AIM-OS Systems │                        │
│                    │  (CMC, HHNI,    │                        │
│                    │   VIF, APOE,    │                        │
│                    │   SEG, TCS,     │                        │
│                    │   IIS, SCOR)    │                        │
│                    └─────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### **Component Hierarchy**

```
IDELayout (Root)
├── PanelManager (Drag-drop, resize, visibility)
├── LeftDrawer
│   ├── FileExplorer (CMC-integrated)
│   ├── MemoryBrowser (CMC + HHNI)
│   ├── SystemMonitor (VIF + SCOR)
│   └── AgentManagement (APOE)
├── MainArea
│   ├── CodeEditor (Monaco + VIF + SEG)
│   ├── ContextWeb (CMC + HHNI visualization)
│   ├── EvolutionExplorer (Timeline + Chain)
│   └── DocumentationViewer (SEG-integrated)
├── RightDrawer
│   ├── CodingChat (VIF confidence indicators)
│   ├── PlanningChat (APOE plan visualization)
│   ├── OutlinePanel (SEG contradiction detection)
│   └── PropertiesPanel (VIF witnesses)
└── BottomDrawer
    ├── Terminal (CMC command history)
    ├── Timeline (TCS visualization)
    ├── Problems (SEG contradictions)
    └── DebugConsole (VIF provenance)
```

---

## 🎨 **PANEL DESIGN**

### **Panel Types (20+ Panels)**

#### **Left Drawer Panels:**

1. **FileExplorer** (CMC-Integrated)
   - File tree with CMC atom metadata
   - VIF witness indicators
   - SEG contradiction alerts
   - HHNI context retrieval on hover

2. **MemoryBrowser** (CMC + HHNI)
   - CMC atom browser
   - HHNI semantic search
   - Memory statistics dashboard
   - Context retrieval visualization

3. **SystemMonitor** (VIF + SCOR)
   - VIF confidence metrics
   - SCOR system health
   - AIM-OS system status
   - Performance monitoring

4. **AgentManagement** (APOE)
   - Active agent list
   - Agent capabilities
   - Task assignments
   - Agent coordination view

5. **ComponentLibrary** (SEG-integrated)
   - Component catalog
   - Component relationships (SEG)
   - Component usage tracking
   - Component documentation

#### **Main Area Panels:**

6. **CodeEditor** (Monaco + VIF + SEG)
   - Monaco Editor with AIM-OS enhancements
   - VIF confidence indicators for AI suggestions
   - SEG contradiction detection inline
   - CMC context retrieval on demand
   - HHNI code completion

7. **ContextWeb** (CMC + HHNI Visualization)
   - Interactive graph of CMC atoms
   - HHNI retrieval paths
   - Context relationships
   - Infinite context visualization

8. **EvolutionExplorer** (Timeline + Chain)
   - Dual-panel Timeline ↔ Chain view
   - Bidirectional navigation
   - Temporal visualization
   - Synchronized selection

9. **DocumentationViewer** (SEG-integrated)
   - Code + Docs synchronized view
   - SEG knowledge graph integration
   - Documentation relationships
   - Contradiction detection

10. **UIEditor** (Visual Editor)
    - Visual UI builder
    - Component drag-drop
    - Live preview
    - Code generation

#### **Right Drawer Panels:**

11. **CodingChat** (VIF Confidence Indicators)
    - AI coding assistant
    - VIF confidence scores on responses
    - CMC context retrieval
    - SEG contradiction warnings

12. **PlanningChat** (APOE Plan Visualization)
    - AI planning assistant
    - APOE plan visualization
    - Task breakdown
    - Execution tracking

13. **OutlinePanel** (SEG Contradiction Detection)
    - Code structure outline
    - SEG contradiction alerts
    - VIF witness indicators
    - Navigation shortcuts

14. **PropertiesPanel** (VIF Witnesses)
    - Selected element properties
    - VIF witness display
    - CMC atom metadata
    - SEG relationships

15. **SearchPanel** (HHNI Semantic Search)
    - Full-text search
    - HHNI semantic search
    - CMC atom search
    - Search history (CMC)

#### **Bottom Drawer Panels:**

16. **Terminal** (CMC Command History)
    - Terminal interface
    - CMC command history
    - AIM-OS command integration
    - Command completion

17. **Timeline** (TCS Visualization)
    - Timeline event stream
    - TCS context entries
    - Goal progress tracking
    - Activity visualization

18. **Problems** (SEG Contradictions)
    - Error list
    - SEG contradiction alerts
    - VIF confidence warnings
    - Issue resolution suggestions

19. **PDAS Panel** (Proactive Debugging & Auditing System) ⭐ **NEW**
    - **Pre-Execution Auditing** - Audit logs created BEFORE operations execute
    - **Always-On Observability** - Real-time operation tracking
    - **Debug Console** - Interactive debugging interface
    - **Expected vs Actual** - Compare expected outcomes with actual outcomes
    - **Error Prevention** - Identify errors before they occur
    - **Integration:** CMC (audit logs), VIF (provenance), SEG (evidence), TCS (timeline)
    - **Revolutionary:** No blank pages - always have visibility into operations

20. **DebugConsole** (VIF Provenance)
    - Debug output
    - VIF provenance tracking
    - Execution traces
    - Confidence metrics

21. **GitPanel** (Version Control)
    - Git status
    - Commit history
    - Branch management
    - Diff viewer

---

## 🔧 **AIM-OS INTEGRATION ARCHITECTURE**

### **AIM-OS Hooks System**

```typescript
// Custom hooks for AIM-OS systems
export const useCMC = () => {
  // CMC atom operations
  const storeAtom = (content: string) => { /* ... */ }
  const retrieveAtoms = (query: string) => { /* ... */ }
  const getStats = () => { /* ... */ }
  return { storeAtom, retrieveAtoms, getStats }
}

export const useHHNI = () => {
  // HHNI semantic search
  const search = (query: string) => { /* ... */ }
  const retrieve = (atomIds: string[]) => { /* ... */ }
  return { search, retrieve }
}

export const useVIF = () => {
  // VIF confidence tracking
  const trackConfidence = (task: string, confidence: number) => { /* ... */ }
  const getWitnesses = (taskId: string) => { /* ... */ }
  return { trackConfidence, getWitnesses }
}

export const useAPOE = () => {
  // APOE plan management
  const createPlan = (goal: string) => { /* ... */ }
  const executePlan = (planId: string) => { /* ... */ }
  return { createPlan, executePlan }
}

export const useSEG = () => {
  // SEG knowledge graph
  const detectContradictions = (content: string) => { /* ... */ }
  const synthesizeKnowledge = (topics: string[]) => { /* ... */ }
  return { detectContradictions, synthesizeKnowledge }
}

export const useTCS = () => {
  // Timeline Context System
  const addEntry = (entry: TimelineEntry) => { /* ... */ }
  const getSummary = (limit: number) => { /* ... */ }
  return { addEntry, getSummary }
}
```

### **Panel Integration Pattern**

```typescript
// Example: FileExplorer with AIM-OS integration
export const FileExplorer: React.FC = () => {
  const { retrieveAtoms, getStats } = useCMC()
  const { search } = useHHNI()
  const { getWitnesses } = useVIF()
  const { detectContradictions } = useSEG()
  
  // File tree with AIM-OS metadata
  const files = useMemo(() => {
    return fileTree.map(file => ({
      ...file,
      cmcAtoms: retrieveAtoms(`file:${file.path}`),
      witnesses: getWitnesses(file.path),
      contradictions: detectContradictions(file.content)
    }))
  }, [fileTree])
  
  return (
    <div className="file-explorer">
      {files.map(file => (
        <FileNode
          key={file.path}
          file={file}
          cmcAtoms={file.cmcAtoms}
          witnesses={file.witnesses}
          contradictions={file.contradictions}
        />
      ))}
    </div>
  )
}
```

---

## 🎯 **REVOLUTIONARY FEATURES**

### **1. Context Web Visualization**

**Purpose:** Visualize infinite effective context (CMC + HHNI)

**Design:**
- Interactive graph of CMC atoms
- HHNI retrieval paths highlighted
- Context relationships visualized
- On-demand context loading

**UI:**
```
┌─────────────────────────────────────────┐
│ Context Web                              │
├─────────────────────────────────────────┤
│  [Atom 123] ──→ [Atom 456] ──→ [Atom 789]│
│     │              │              │      │
│     └──────────────┴──────────────┘      │
│              [Current Context]            │
│                                         │
│  Total Context: 127K tokens            │
│  Active Window: 8K tokens              │
│  Retrieved: 3.2K tokens                │
└─────────────────────────────────────────┘
```

### **2. Evolution Explorer**

**Purpose:** Bidirectional Timeline ↔ Chain visualization

**Design:**
- Dual-panel layout (Timeline | Chain)
- Synchronized selection
- Temporal navigation
- Evolution tracking

**UI:**
```
┌──────────────┬──────────────┐
│ Timeline     │ Chain        │
├──────────────┼──────────────┤
│ [Event 1]    │ [Node A]     │
│ [Event 2] ←→ │ [Node B] ←→  │
│ [Event 3]    │ [Node C]     │
└──────────────┴──────────────┘
```

### **3. VIF Confidence Indicators**

**Purpose:** Show confidence levels for all AI interactions

**Design:**
- Color-coded confidence (green/yellow/red)
- Confidence scores displayed
- Evidence sources shown
- Abstention when confidence too low

**UI:**
```
┌─────────────────────────────────────────┐
│ AI Response                             │
├─────────────────────────────────────────┤
│ Q: "What's the best practice for X?"    │
│                                         │
│ A: "Based on evidence..."               │
│                                         │
│ Confidence: 🟢 HIGH (κ=0.85)           │
│ ├─ Sources: 3 documents                 │
│ ├─ Evidence: Strong                    │
│ └─ Recommendation: Use approach Y       │
└─────────────────────────────────────────┘
```

### **4. SEG Contradiction Detection**

**Purpose:** Detect contradictions in real-time

**Design:**
- Inline contradiction alerts
- Contradiction resolution suggestions
- Knowledge graph visualization
- Contradiction history

**UI:**
```
┌─────────────────────────────────────────┐
│ Code Editor                              │
├─────────────────────────────────────────┤
│ function example() {                     │
│   // ⚠️ CONTRADICTION DETECTED          │
│   // This conflicts with line 45        │
│   return x;                              │
│ }                                        │
│                                         │
│ [Resolve] [View Details] [Ignore]      │
└─────────────────────────────────────────┘
```

---

## 📐 **LAYOUT ARCHITECTURE**

### **Layout Structure**

```
┌─────────────────────────────────────────────────────────────┐
│ Top Bar: Command Palette, Search, Settings                  │
├──────────┬──────────────────────────────────────┬──────────┤
│          │                                      │          │
│ Left     │         Main Area                    │ Right    │
│ Drawer   │         (Resizable)                  │ Drawer   │
│          │                                      │          │
│ [File]   │  [Code Editor]                       │ [Chat]   │
│ [Memory] │  [Context Web]                       │ [Outline]│
│ [Monitor]│  [Evolution]                         │ [Props]  │
│ [Agents] │  [Docs]                              │ [Search] │
│          │                                      │          │
├──────────┴──────────────────────────────────────┴──────────┤
│ Bottom Drawer: Terminal, Timeline, Problems, PDAS, Debug   │
└─────────────────────────────────────────────────────────────┘
```

### **Panel Zones**

1. **Left Drawer** (15-25% width)
   - File Explorer
   - Memory Browser
   - System Monitor
   - Agent Management
   - Component Library

2. **Main Area** (50-70% width)
   - Code Editor
   - Context Web
   - Evolution Explorer
   - Documentation Viewer
   - UI Editor

3. **Right Drawer** (15-25% width)
   - Coding Chat
   - Planning Chat
   - Outline Panel
   - Properties Panel
   - Search Panel

4. **Bottom Drawer** (20-40% height when open)
   - Terminal
   - Timeline
   - Problems
   - Debug Console
   - Git Panel

---

## 🎛️ **CUSTOMIZATION FEATURES**

### **Panel Management**

1. **Drag-and-Drop**
   - Drag panels between zones
   - Reorder panels within zones
   - Create custom panel groups

2. **Resizable Panels**
   - All panels resizable
   - Minimum/maximum sizes
   - Snap-to-grid option

3. **Panel Visibility**
   - Toggle panel visibility
   - Panel presets (coding, debugging, planning)
   - Custom panel groups

4. **Layout Saving/Loading**
   - Save named layouts
   - Load predefined layouts
   - Export/import layouts

5. **Panel-Specific Layouts**
   - Different layouts per panel type
   - Context-aware layouts
   - Workflow-based layouts

### **Customization UI**

```
┌─────────────────────────────────────────┐
│ Panel Manager                           │
├─────────────────────────────────────────┤
│ Available Panels:                       │
│  [File Explorer] [Drag to add]         │
│  [Memory Browser] [Drag to add]        │
│  ...                                    │
│                                         │
│ Current Layout:                         │
│  Left: [File] [Memory]                 │
│  Main: [Code Editor]                   │
│  Right: [Chat] [Outline]               │
│                                         │
│ [Save Layout] [Load Layout] [Reset]    │
└─────────────────────────────────────────┘
```

---

## 📊 **MOCK DATA STRUCTURE**

### **File Tree Mock Data**

```typescript
const mockFileTree = {
  "src/": {
    "components/": {
      "IDELayout.tsx": {
        type: "file",
        size: 1234,
        modified: "2025-11-07",
        cmcAtoms: ["atom_123", "atom_456"],
        witnesses: ["witness_789"],
        contradictions: []
      },
      "MonacoEditor.tsx": {
        type: "file",
        size: 2345,
        modified: "2025-11-07",
        cmcAtoms: ["atom_321"],
        witnesses: [],
        contradictions: ["contradiction_001"]
      }
    },
    "hooks/": {
      "useCMC.ts": { /* ... */ },
      "useHHNI.ts": { /* ... */ }
    }
  }
}
```

### **CMC Mock Data**

```typescript
const mockCMCAtoms = [
  {
    id: "atom_123",
    content: "File IDELayout.tsx uses react-resizable-panels",
    timestamp: "2025-11-07T10:00:00Z",
    tags: ["ide", "layout", "react"],
    confidence: 0.95
  },
  // ... more atoms
]
```

### **VIF Mock Data**

```typescript
const mockVIFWitnesses = [
  {
    id: "witness_789",
    task: "File IDELayout.tsx implementation",
    confidence: 0.85,
    evidence: ["atom_123", "atom_456"],
    timestamp: "2025-11-07T10:05:00Z"
  },
  // ... more witnesses
]
```

### **Timeline Mock Data**

```typescript
const mockTimelineEntries = [
  {
    id: "entry_001",
    prompt_id: "prompt_123",
    user_input: "Create IDE layout prototype",
    context_state: { /* ... */ },
    timestamp: "2025-11-07T10:00:00Z"
  },
  // ... more entries
]
```

### **Agent Mock Data**

```typescript
const mockAgents = [
  {
    id: "agent_lex",
    name: "Lex",
    status: "active",
    currentTask: "IDE Layout Prototype Design",
    capabilities: ["research", "analysis", "documentation"],
    confidence: 0.90
  },
  // ... more agents
]
```

---

## 🎨 **VISUAL DESIGN**

### **Color Scheme**

- **Primary:** Blue (#3B82F6) - AIM-OS brand
- **Success:** Green (#10B981) - High confidence
- **Warning:** Yellow (#F59E0B) - Medium confidence
- **Error:** Red (#EF4444) - Low confidence / Contradictions
- **Background:** Dark (#1F2937) - Professional IDE look
- **Text:** Light (#F9FAFB) - High contrast

### **Typography**

- **Font Family:** Inter, system-ui, sans-serif
- **Headings:** Bold, 16-24px
- **Body:** Regular, 14px
- **Code:** 'Fira Code', monospace, 13px

### **Spacing**

- **Panel Padding:** 12px
- **Component Gap:** 8px
- **Section Gap:** 16px
- **Drawer Width:** 250-400px (resizable)

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Core Layout (Week 1)**

1. **Day 1-2:** Layout structure
   - Panel zones (left, main, right, bottom)
   - Resizable panels
   - Basic panel management

2. **Day 3-4:** AIM-OS hooks
   - useCMC, useHHNI, useVIF, useAPOE, useSEG, useTCS
   - Mock data integration
   - Error boundaries

3. **Day 5:** Basic panels
   - File Explorer (CMC-integrated)
   - Code Editor (Monaco)
   - Terminal
   - Chat (basic)

### **Phase 2: AIM-OS Integration (Week 2)**

1. **Day 1-2:** Revolutionary features
   - Context Web visualization
   - Evolution Explorer
   - VIF confidence indicators
   - SEG contradiction detection

2. **Day 3-4:** Advanced panels
   - Memory Browser (CMC + HHNI)
   - System Monitor (VIF + SCOR)
   - Agent Management (APOE)
   - Timeline (TCS)

3. **Day 5:** Integration testing
   - All panels AIM-OS integrated
   - Mock data comprehensive
   - Error handling complete

### **Phase 3: Customization (Week 3)**

1. **Day 1-2:** Drag-and-drop
   - Panel drag-drop between zones
   - Panel reordering
   - Custom panel groups

2. **Day 3-4:** Layout management
   - Layout saving/loading
   - Panel presets
   - Custom layouts

3. **Day 5:** Polish
   - Mobile-responsive version
   - Keyboard shortcuts
   - Final polish

---

## ✅ **SUCCESS CRITERIA**

### **Must Have:**

- ✅ 20+ panel types implemented
- ✅ All panels AIM-OS integrated
- ✅ Drag-and-drop working
- ✅ Resizable panels working
- ✅ Layout saving/loading working
- ✅ Comprehensive mock data
- ✅ Mobile-responsive version
- ✅ Error boundaries implemented
- ✅ Loading states for async operations

### **Should Have:**

- ⚠️ Panel presets
- ⚠️ Keyboard shortcuts
- ⚠️ Panel search/filter
- ⚠️ Context-aware layouts

### **Nice to Have:**

- 💡 Panel analytics
- 💡 Panel recommendations
- 💡 Panel marketplace concept

---

## 🎯 **COMPETITIVE ADVANTAGES**

### **1. Deep AIM-OS Integration (20% of score)**

- **All panels** integrated with AIM-OS systems
- **Revolutionary features** (Context Web, Evolution Explorer)
- **VIF confidence** indicators everywhere
- **SEG contradiction** detection in real-time

### **2. Past Learnings Applied (Innovation Bonus)**

- Patterns from `IDELayout.tsx` refined
- Error boundaries from day one
- Loading states for async operations
- Proper state management

### **3. Developer Workflow Optimization (30% of score)**

- Every feature serves actual coding workflows
- Context Web solves "forgotten context" problem
- VIF confidence solves "confident lies" problem
- SEG contradictions solve "self-contradictions" problem

### **4. Completeness & Polish (Bonus Points)**

- 20+ panels (more than required 15)
- Comprehensive mock data
- Error handling complete
- Mobile-responsive version

---

## 📝 **NEXT STEPS**

1. ✅ **Design Document Complete** - This document
2. ⏳ **Start Implementation** - Begin with core layout
3. ⏳ **Build AIM-OS Hooks** - Create useCMC, useHHNI, etc.
4. ⏳ **Implement Panels** - Build all 20+ panels
5. ⏳ **Add Customization** - Drag-drop, resize, layouts
6. ⏳ **Polish & Test** - Final polish and testing

---

**Status:** Design Complete - Ready for Implementation  
**Focus:** AIM-OS Native + Revolutionary Features  
**Competition:** Ready to win! 🏆

