# IDE Layout Prototype - Codex Design Document
## Architecture-First + Lucid Orchestrator Integration

**Author:** Codex (Design & Implementation by Codex, Design Document Completed by Lex)  
**Date:** 2025-11-07  
**Status:** Design Phase - Aligned with Lucid Orchestrator  
**Focus:** Architecture-First + Lucid Orchestrator + ChainSpec Integration + Scalability  
**Competition:** IDE Layout Prototype Mission

---

## 🎯 **PROTOTYPE DIFFERENTIATION**

### **Codex's Prototype vs Lex's Prototype**

**Codex's Prototype (This Document):**
- **Approach:** Architecture-First - Extends existing Lucid Orchestrator
- **Foundation:** Builds on Codex's existing Lucid Orchestrator work (`packages/lucid_orchestrator/`)
- **Unique Features:** Lucid Orchestrator four-pane interface (Code, Blueprint, Spec, Timeline), ChainSpec visualization, orchestration canvas
- **Focus:** Architecture visualization and orchestration management
- **Panels:** Extends Lucid Orchestrator with ChainSpec and orchestration panels
- **Status:** Extension of Codex's existing work - Lex completing Codex's design document and implementation
- **Responsibility:** Lex is responsible for completing Codex's prototype implementation

**Lex's Prototype (`IDE_LAYOUT_PROTOTYPE_LEX.md`):**
- **Approach:** AIM-OS Native First - Deep integration with all AIM-OS systems
- **Foundation:** Built from scratch, leveraging past IDE implementations
- **Unique Features:** Context Web, Evolution Explorer, Consciousness Visualization, VIF confidence indicators
- **Focus:** Making invisible AIM-OS systems visible and actionable
- **Panels:** 20+ panels with deep AIM-OS integration
- **Status:** Independent prototype - Lex's own design and implementation

**Key Difference:**
- **Codex:** Extension of existing Lucid Orchestrator, architecture-first, orchestration-focused
- **Lex:** New prototype from scratch, AIM-OS-native, revolutionary UX features

**Note:** Lex is building BOTH prototypes:
1. **Lex's Prototype** - Independent, AIM-OS-native design
2. **Codex's Prototype** - Completing Codex's work, extending Lucid Orchestrator

---

---

## 🎯 **DESIGN PHILOSOPHY**

### **Core Principle: Architecture-First, UI Follows**

This prototype builds on **Codex's existing Lucid Orchestrator** work—a four-pane consciousness interface that unifies Code, Blueprint, Spec, and Timeline into a living system. The IDE layout extends this architecture-first approach to create a comprehensive IDE experience.

### **Lucid Orchestrator Foundation**

Codex has already built:
- ✅ **Lucid Orchestrator Core** (`packages/lucid_orchestrator/`)
- ✅ **Four-Pane Interface** (Code, Blueprint, Spec, Timeline)
- ✅ **React Components** (`LucidOrchestratorMain.tsx` + individual panes)
- ✅ **Data Services** (CodePaneService, BlueprintPaneService, SpecPaneService, TimelinePaneService)
- ✅ **Graph Engine, Spec Engine, Timeline Engine**
- ✅ **Event Bus** for cross-pane synchronization
- ✅ **Real-time Collaboration** support

**This prototype extends Lucid Orchestrator into a full IDE layout** with additional panels, orchestration visualization, and ChainSpec integration.

### **Key Design Pillars:**

1. **Architecture-First** - Start with architecture, then UI
2. **Orchestration Integration** - Deep integration with APOE, ChainSpec, quality gates, progress tracking
3. **Scalability** - Design for scale and complexity (multi-agent coordination, dynamic tasking, parallel execution)
4. **ChainSpec-Driven** - UI reflects ChainSpec structure (epics → phases → workstreams → tasks)
5. **Quality Gates Visualization** - Visual representation of quality gates and validation
6. **Progress Tracking** - Real-time progress visualization with predictive analytics

---

## 🏗️ **ARCHITECTURE OVERVIEW**

### **System Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│              IDE Layout Prototype (Codex)                   │
│         Architecture-First + Orchestration Native           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  UI Layer    │  │ Orchestration│  │  AIM-OS      │      │
│  │  (React)     │→ │  Layer       │→ │  Systems     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                    │             │
│         └─────────────────┴────────────────────┘            │
│                            │                                  │
│                    ┌───────▼────────┐                        │
│                    │  ChainSpec      │                        │
│                    │  (Epic/Phase/  │                        │
│                    │   Workstream/   │                        │
│                    │   Task)         │                        │
│                    └─────────────────┘                        │
│                            │                                  │
│                    ┌───────▼────────┐                        │
│                    │  APOE Engine   │                        │
│                    │  (Orchestration│                        │
│                    │   Execution)    │                        │
│                    └─────────────────┘                        │
│                            │                                  │
│                    ┌───────▼────────┐                        │
│                    │  Quality Gates │                        │
│                    │  (VIF, SDF-CVF)│                        │
│                    └─────────────────┘                        │
│                            │                                  │
│                    ┌───────▼────────┐                        │
│                    │  Progress      │                        │
│                    │  Tracking      │                        │
│                    │  (Predictive)  │                        │
│                    └─────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### **Component Hierarchy**

```
IDELayout (Root)
├── LucidOrchestrator (Core - Codex's existing work)
│   ├── CodePane (Left) - Monaco editor, file browser
│   ├── BlueprintPane (Center) - Structural graph, health states
│   ├── SpecPane (Right) - SpecBlocks, compliance status
│   └── TimelinePane (Bottom) - Runtime truth, execution traces
├── LeftDrawer (Extended)
│   ├── ChainSpecExplorer (Epic/Phase/Workstream/Task tree)
│   ├── AgentRegistry (Agent capabilities, assignments)
│   ├── QualityGatesDashboard (Gate health, pass rates)
│   └── FileExplorer (Standard file tree)
├── MainArea (Extended)
│   ├── LucidOrchestratorMain (Primary - Codex's work)
│   ├── OrchestrationCanvas (ChainSpec visualization)
│   ├── TaskExecutionView (Task execution visualization)
│   └── ChainSpecEditor (ChainSpec authoring)
├── RightDrawer (Extended)
│   ├── TaskDetails (Task details, dependencies)
│   ├── QualityMetrics (VIF, SDF-CVF metrics)
│   ├── AgentCoordination (Multi-agent coordination)
│   └── APIMediation (API routing, enhancement)
└── BottomDrawer (Extended)
    ├── TimelinePane (Lucid Orchestrator - Codex's work)
    ├── ProgressDashboard (Wave status, gate health)
    ├── TelemetryView (Telemetry dashboards)
    └── RollbackConsole (Rollback mechanisms)
```

---

## 🎨 **PANEL DESIGN**

### **Panel Types (20+ Panels)**

#### **Core Panels (Lucid Orchestrator - Codex's Existing Work):**

1. **CodePane** (Left) - ✅ **EXISTING**
   - Monaco editor for source text
   - File browser
   - Code metrics
   - Dependency visualization
   - Selection syncs to other panes

2. **BlueprintPane** (Center) - ✅ **EXISTING**
   - Live structural graph
   - Interactive architecture diagram
   - Drag-and-drop nodes
   - Health states (Green/Amber/Red)
   - Node relationships

3. **SpecPane** (Right) - ✅ **EXISTING**
   - SpecBlocks viewer
   - Compliance status
   - Drift detection
   - Specification management
   - Quality metrics

4. **TimelinePane** (Bottom) - ✅ **EXISTING**
   - Event timeline
   - Execution traces
   - Performance data
   - Violation tracking
   - Evolution analysis

#### **Extended Panels (New for IDE Layout):**

5. **ChainSpecExplorer** (Left Drawer)
   - Epic/Phase/Workstream/Task tree
   - Hierarchical navigation
   - Dependency visualization
   - Status indicators
   - Integration with Lucid Orchestrator

6. **AgentRegistry** (Left Drawer)
   - Agent list with capabilities
   - Capability matching visualization
   - Agent assignments
   - Quality history
   - Integration with APOE

7. **QualityGatesDashboard** (Left Drawer)
   - Gate pass rates
   - Gate health metrics
   - Quality gate visualization
   - Validation status
   - Integration with VIF, SDF-CVF

8. **FileExplorer** (Left Drawer)
   - File tree
   - CMC integration
   - Standard file operations
   - Integration with CodePane

#### **Main Area Panels:**

9. **LucidOrchestratorMain** (Primary) - ✅ **EXISTING**
   - Four-pane interface
   - View modes (Single, Split, Grid)
   - Cross-pane synchronization
   - System selection
   - Export functionality

10. **OrchestrationCanvas** (ChainSpec Visualization)
    - Visual orchestration interface
    - Task flow visualization
    - Parallel execution groups
    - Dependency graph
    - Integration with ChainSpec

11. **TaskExecutionView** (Task Execution)
    - Task execution visualization
    - Real-time task status
    - Task dependencies
    - Execution timeline
    - Integration with APOE

12. **ChainSpecEditor** (ChainSpec Authoring)
    - ChainSpec YAML editor
    - Syntax highlighting
    - Validation
    - Auto-completion
    - Integration with ChainSpec structure

13. **ArchitectureDiagram** (System Architecture)
    - System architecture visualization
    - Component relationships
    - Data flow diagrams
    - Integration points
    - Integration with BlueprintPane

#### **Right Drawer Panels:**

11. **TaskDetails** (Task Information)
    - Task details
    - Dependencies
    - Quality gates
    - Execution status

12. **QualityMetrics** (VIF, SDF-CVF)
    - VIF confidence metrics
    - SDF-CVF quality scores
    - Quality trends
    - Validation results

13. **AgentCoordination** (Multi-Agent)
    - Agent coordination view
    - Task assignments
    - Communication flow
    - Consensus building

14. **APIMediation** (API Routing)
    - API routing visualization
    - Capability matching
    - Enhancement pipeline
    - Adapter status

15. **SearchPanel** (Standard)
    - Search functionality
    - ChainSpec search
    - Task search
    - Agent search

#### **Bottom Drawer Panels:**

14. **PDAS Panel** (Proactive Debugging & Auditing System) ⭐ **NEW**
    - **Pre-Execution Auditing** - Audit logs created BEFORE operations execute
    - **Always-On Observability** - Real-time operation tracking
    - **Debug Console** - Interactive debugging interface
    - **Expected vs Actual** - Compare expected outcomes with actual outcomes
    - **Error Prevention** - Identify errors before they occur
    - **Integration:** Lucid Orchestrator (Code, Blueprint, Spec, Timeline), ChainSpec, APOE
    - **Architecture-First:** Debugging reflects architecture and orchestration

15. **ProgressDashboard** (Wave Status)
    - Wave status dashboard
    - Gate health dashboard
    - Predictive metrics dashboard
    - Progress visualization

16. **TelemetryView** (Telemetry)
    - Telemetry dashboards
    - Metrics visualization
    - Analytics
    - Performance monitoring

17. **RollbackConsole** (Rollback)
    - Rollback mechanisms
    - Recovery strategies
    - Checkpoint management
    - State restoration

18. **LogsView** (Execution Logs)
    - Execution logs
    - Error logs
    - Debug logs
    - System logs

19. **Terminal** (Standard)
    - Terminal interface
    - Command execution
    - Standard terminal features

---

## 🔧 **ORCHESTRATION INTEGRATION ARCHITECTURE**

### **ChainSpec Integration**

```typescript
// ChainSpec structure visualization
interface ChainSpecStructure {
  epic: Epic
  phases: Phase[]
  workstreams: Workstream[]
  tasks: Task[]
}

interface Epic {
  id: string
  name: string
  phases: Phase[]
  quality_targets: QualityTargets
  telemetry: TelemetryConfig
}

interface Phase {
  id: string
  title: string
  workstreams: Workstream[]
  entry_gates: string[]
  exit_gates: string[]
  parallel_groups: ParallelGroup[]
}

interface Workstream {
  id: string
  title: string
  tasks: Task[]
  owner: string
  agents: string[]
}

interface Task {
  id: string
  description: string
  dependencies: string[]
  gate_refs: string[]
  quality_gates: QualityGate[]
}
```

### **APOE Integration**

```typescript
// APOE orchestration hooks
export const useAPOE = () => {
  const executePlan = (planId: string) => { /* ... */ }
  const createPlan = (goal: string) => { /* ... */ }
  const getPlanStatus = (planId: string) => { /* ... */ }
  const getExecutionFlow = (planId: string) => { /* ... */ }
  return { executePlan, createPlan, getPlanStatus, getExecutionFlow }
}
```

### **Quality Gates Integration**

```typescript
// Quality gates visualization
interface QualityGate {
  id: string
  type: 'task' | 'phase' | 'epic'
  status: 'pending' | 'passed' | 'failed'
  metrics: QualityMetrics
  validation: ValidationResult
}

interface QualityMetrics {
  vif_confidence: number
  sdf_cvf_quality: number
  relevance: number
  density: number
  completion: number
  thoroughness: number
}
```

### **Progress Tracking Integration**

```typescript
// Progress tracking hooks
export const useProgressTracking = () => {
  const getWaveStatus = () => { /* ... */ }
  const getGateHealth = () => { /* ... */ }
  const getPredictiveMetrics = () => { /* ... */ }
  const getRollbackRisk = () => { /* ... */ }
  return { getWaveStatus, getGateHealth, getPredictiveMetrics, getRollbackRisk }
}
```

---

## 🎯 **REVOLUTIONARY FEATURES**

### **1. Orchestration Canvas**

**Purpose:** Visual orchestration interface showing task flow, dependencies, and parallel execution

**Design:**
- Visual flow diagram
- Task nodes with status indicators
- Dependency arrows
- Parallel execution groups highlighted
- Real-time updates

**UI:**
```
┌─────────────────────────────────────────┐
│ Orchestration Canvas                    │
├─────────────────────────────────────────┤
│  [Epic]                                 │
│    │                                    │
│    ├─→ [Phase 1] ──→ [Phase 2]         │
│    │      │                │            │
│    │      ├─→ [WS 1]       ├─→ [WS 3]  │
│    │      ├─→ [WS 2]       └─→ [WS 4]  │
│    │      │                            │
│    │      └─→ [Task 1] ──→ [Task 2]    │
│                                         │
│  Status: 🟢 In Progress                 │
│  Progress: 45%                          │
└─────────────────────────────────────────┘
```

### **2. ChainSpec Explorer**

**Purpose:** Hierarchical navigation of ChainSpec structure

**Design:**
- Tree view of Epic → Phase → Workstream → Task
- Status indicators at each level
- Dependency visualization
- Quick navigation

### **3. Quality Gates Dashboard**

**Purpose:** Visual representation of quality gate health

**Design:**
- Gate pass rates
- Quality metrics visualization
- Validation status
- Trend analysis

### **4. Predictive Progress Tracking**

**Purpose:** Predictive analytics for completion and rollback risk

**Design:**
- Predictive completion timeline
- Rollback risk indicators
- Progress trends
- Risk alerts

---

## 📐 **LAYOUT ARCHITECTURE**

### **Layout Structure**

```
┌─────────────────────────────────────────────────────────────┐
│ Top Bar: ChainSpec Selector, Search, Settings              │
├──────────┬──────────────────────────────────────┬──────────┤
│          │                                      │          │
│ Left     │         Main Area                    │ Right    │
│ Drawer   │         (Orchestration)              │ Drawer   │
│          │                                      │          │
│ [Chain]  │  [Orchestration Canvas]             │ [Task]   │
│ [Agent]  │  [Task Execution]                   │ [Quality]│
│ [Gates]  │  [ChainSpec Editor]                 │ [API]    │
│ [Progress]│  [Architecture]                    │ [Search] │
│          │                                      │          │
├──────────┴──────────────────────────────────────┴──────────┤
│ Bottom Drawer: PDAS, Progress, Telemetry, Rollback, Logs   │
└─────────────────────────────────────────────────────────────┘
```

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

3. **Layout Saving/Loading**
   - Save named layouts
   - Load predefined layouts
   - Export/import layouts

4. **Orchestration Views**
   - Different views per orchestration phase
   - Context-aware layouts
   - Workflow-based layouts

---

## 📊 **MOCK DATA STRUCTURE**

### **ChainSpec Mock Data**

```typescript
const mockChainSpec: ChainSpecStructure = {
  epic: {
    id: 'ide_chat_orchestration',
    name: 'IDE Orchestration Build Plan',
    phases: [
      {
        id: 'research_phase',
        title: 'Phase 1 - Research & Analysis',
        workstreams: [
          {
            id: 'ws_cursor_analysis',
            title: 'Cursor System Deep Dive',
            tasks: [
              {
                id: 'task_cursor_landscape',
                description: 'Document Cursor architecture',
                dependencies: [],
                gate_refs: ['task.research_artifact_quality'],
                quality_gates: [],
              },
            ],
          },
        ],
      },
    ],
  },
}
```

### **Quality Gates Mock Data**

```typescript
const mockQualityGates: QualityGate[] = [
  {
    id: 'task.research_artifact_quality',
    type: 'task',
    status: 'passed',
    metrics: {
      vif_confidence: 0.90,
      sdf_cvf_quality: 0.88,
      relevance: 0.92,
      density: 0.85,
      completion: 1.0,
      thoroughness: 0.90,
    },
    validation: {
      passed: true,
      timestamp: '2025-11-07T10:00:00Z',
    },
  },
]
```

### **Progress Tracking Mock Data**

```typescript
const mockProgress = {
  wave_status: {
    research_phase: { completed: 80, total: 100, blockers: [] },
    architecture_phase: { completed: 0, total: 100, blockers: [] },
  },
  gate_health: {
    pass_rate: 0.95,
    failed_gates: [],
    pending_gates: 5,
  },
  predictive_metrics: {
    estimated_completion: '2025-11-15',
    rollback_risk: 0.15,
    confidence: 0.85,
  },
}
```

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Integrate Lucid Orchestrator (Week 1)**

1. **Day 1-2:** Integrate existing Lucid Orchestrator
   - Import `LucidOrchestratorMain` component
   - Integrate into IDE layout
   - Test four-pane functionality
   - Verify cross-pane synchronization

2. **Day 3-4:** Extend with ChainSpec integration
   - ChainSpec types
   - ChainSpec parser
   - ChainSpec visualization hooks
   - Integration with Lucid Orchestrator

3. **Day 5:** Add orchestration hooks
   - APOE hooks
   - Quality gates hooks
   - Progress tracking hooks
   - Integration with existing services

### **Phase 2: Build Extended Panels (Week 2)**

1. **Day 1-2:** ChainSpec Explorer
   - Epic/Phase/Workstream/Task tree
   - Hierarchical navigation
   - Integration with Lucid Orchestrator

2. **Day 3-4:** Orchestration Canvas
   - Visual flow diagram
   - Task visualization
   - Dependency visualization
   - Integration with ChainSpec

3. **Day 5:** Quality Gates Dashboard
   - Gate health visualization
   - Quality metrics
   - Validation status
   - Integration with VIF, SDF-CVF

### **Phase 3: Customization & Polish (Week 3)**

1. **Day 1-2:** Panel Management
   - Drag-drop panels
   - Resizable panels
   - Layout saving/loading
   - Panel visibility toggle

2. **Day 3-4:** ChainSpec Editor
   - YAML editor
   - Validation
   - Auto-completion
   - Integration with ChainSpec structure

3. **Day 5:** Polish
   - Mobile-responsive
   - Keyboard shortcuts
   - Final polish
   - Integration testing

---

## ✅ **SUCCESS CRITERIA**

### **Must Have:**

- ✅ 20+ panel types implemented
- ✅ ChainSpec integration complete
- ✅ Orchestration visualization working
- ✅ Quality gates dashboard functional
- ✅ Progress tracking with predictive analytics
- ✅ Drag-and-drop working
- ✅ Resizable panels working
- ✅ Layout saving/loading working
- ✅ Comprehensive mock data
- ✅ Mobile-responsive version

### **Should Have:**

- ⚠️ ChainSpec editor with validation
- ⚠️ Architecture diagram visualization
- ⚠️ API mediation visualization
- ⚠️ Rollback console functional

### **Nice to Have:**

- 💡 Real-time orchestration updates
- 💡 Advanced predictive analytics
- 💡 Custom orchestration views

---

## 🎯 **COMPETITIVE ADVANTAGES**

### **1. Architecture-First Approach (Innovation Bonus)**

- **ChainSpec-driven** UI structure
- **Orchestration-native** design
- **Scalability** built-in from architecture

### **2. Deep Orchestration Integration (20% of score)**

- **APOE integration** throughout
- **Quality gates** visualization
- **Progress tracking** with predictive analytics
- **ChainSpec** as first-class citizen

### **3. Scalability Focus (Innovation Bonus)**

- **Multi-agent coordination** visualization
- **Dynamic tasking** support
- **Parallel execution** visualization
- **Scale-ready** architecture

### **4. Developer Workflow Optimization (30% of score)**

- **Orchestration workflows** optimized
- **ChainSpec authoring** streamlined
- **Quality validation** integrated
- **Progress tracking** transparent

---

## 📝 **NEXT STEPS**

1. ✅ **Design Document Complete** - This document (aligned with Lucid Orchestrator)
2. ✅ **Lucid Orchestrator Exists** - Codex's existing work ready to integrate
3. ⏳ **Start Implementation** - Integrate Lucid Orchestrator into IDE layout
4. ⏳ **Extend with ChainSpec** - Add ChainSpec visualization and integration
5. ⏳ **Build Extended Panels** - Add orchestration panels around Lucid Orchestrator
6. ⏳ **Add Customization** - Drag-drop, resize, layouts
7. ⏳ **Polish & Test** - Final polish and testing

## 🔗 **INTEGRATION WITH EXISTING WORK**

### **Lucid Orchestrator Integration**

**Existing Components:**
- `packages/lucid_orchestrator/lucid_orchestrator.ts` - Core orchestrator
- `packages/lucid_orchestrator/data_services/` - Data services
- `packages/ide_chat_app/src/components/LucidOrchestrator/` - React components
- `LucidOrchestratorMain.tsx` - Main component with four-pane interface

**Integration Strategy:**
1. Use `LucidOrchestratorMain` as primary main area panel
2. Extend with ChainSpec panels in left/right drawers
3. Add orchestration visualization panels
4. Integrate ChainSpec with Lucid Orchestrator's event bus
5. Connect quality gates to Lucid Orchestrator's spec engine

### **Architecture Alignment**

**Lucid Orchestrator Architecture:**
- Graph Engine → Blueprint Pane
- Spec Engine → Spec Pane
- Timeline Engine → Timeline Pane
- Event Bus → Cross-pane synchronization

**IDE Layout Extension:**
- ChainSpec → ChainSpec Explorer
- APOE → Orchestration Canvas
- Quality Gates → Quality Gates Dashboard
- Progress Tracking → Progress Dashboard

**Unified Architecture:**
- Lucid Orchestrator provides core consciousness interface
- IDE Layout extends with orchestration visualization
- ChainSpec integrates with Lucid Orchestrator's event bus
- Quality gates connect to Spec Engine

---

**Status:** Design Complete - Aligned with Lucid Orchestrator  
**Focus:** Architecture-First + Lucid Orchestrator + ChainSpec Integration + Scalability  
**Competition:** Ready to win with Codex's existing foundation! 🏆

