# Max V2 Design Document
## Complete Design Specification for V2 Prototype

**Created:** 2025-11-08  
**Agent:** Max  
**Purpose:** V2 design document, architecture decisions, feature specifications, UX improvements  
**Status:** Phase 5 - Comprehensive Documentation  
**Confidence:** 0.90

---

## 📊 **EXECUTIVE SUMMARY**

This document provides a complete design specification for Max's V2 prototype, synthesizing best ideas from all agents, deep AIM-OS integration, and revolutionary UX patterns. The design maintains Max's panel-first philosophy while integrating best-in-class systems from other agents (Aether's debug, Lex's hooks, Dac's Context Web, Codex's orchestration, Rev's research) and comprehensive AIM-OS capabilities (all 8 systems, 54 working MCP tools, 70+ reusable panels). The design emphasizes: **Panel-First Customization** (drag-drop, resize, group, layout save/load), **Deep AIM-OS Integration** (all 8 systems via `useAIMOS` hook), **Revolutionary UX** (Context Web, Evolution Explorer, Consciousness Visualization), **Debug Infrastructure Built-In** (Aether's Debug Console), and **Production Readiness** (accessibility WCAG 2.1 AA, performance optimization).

**Design Principles:**
- Panel-First: Everything is a panel, maximum customization
- AIM-OS Native: Deep integration with all 8 systems
- Revolutionary UX: Context Web, Evolution Explorer, Consciousness Visualization
- Debug Infrastructure Built-In: Never an afterthought
- Production-Ready: Accessibility, performance, quality

---

## 🏗️ **ARCHITECTURE DECISIONS**

### **1. Layout Architecture: 5-Zone Layout System**

**Decision:** Adopt 5-zone layout system (Aether/Dac approach)

**Rationale:**
- Comprehensive workspace organization
- Clear panel placement strategy
- Supports all 19+ panels effectively
- Industry standard (VS Code, JetBrains use similar layouts)

**Zones:**
1. **Top Bar:** Command palette, agent status, confidence indicators, layout switcher
2. **Left Drawer:** System navigation (File Explorer, Component Library, AI Memory, Goal Planning, System Status, AIM-OS Structure Panels)
3. **Main Content:** Work zones (Code Editor, Evolution Explorer, Consciousness Visualization, Agent Management, Lucid Orchestrator, Hierarchical Code Explorer variants)
4. **Right Drawer:** Context & Evidence (Context Web, Evidence Graph, Timeline View, MCP Tools, Confidence Calibration, NL Tags, File Version History)
5. **Bottom Drawer:** Operations & History (Terminal, Problems, Timeline, File Changes, Debug Console)

**Implementation:**
- Use `react-resizable-panels` for resizable zones
- Panel persistence (save panel sizes/visibility)
- Multi-monitor support (floating windows)

---

### **2. Panel Architecture: Panel-First Design**

**Decision:** Maintain panel-first philosophy with enhanced customization

**Rationale:**
- Max's unique strength (maximum customization)
- Panels as first-class citizens enable flexibility
- Easy integration of diverse components
- Supports all 19+ panels effectively

**Panel System:**
- **Base Panel Component:** Common panel functionality (header, close button, drag handle)
- **Panel-Specific Components:** Compose on top of Base Panel
- **Panel Registry:** Register all panels dynamically
- **Panel Lifecycle:** Mount/unmount, lazy loading

**Customization:**
- **Drag-and-Drop:** Move panels between zones
- **Resize:** Resize panels with constraints (min/max sizes)
- **Group:** Group panels into tabs/accordions/stacks
- **Layout Save/Load:** Save/load custom layouts (CMC snapshots)
- **Panel Presets:** Predefined panel configurations

---

### **3. State Management: Enhanced Zustand**

**Decision:** Enhance Zustand state management with comprehensive state

**Rationale:**
- Lightweight and performant
- Easy to extend with AIM-OS integration
- Supports complex state (panels, layout, AIM-OS, customization)

**State Structure:**
- **Panel State:** Panels, zones, visibility, sizes, positions
- **Layout State:** Current layout, saved layouts, layout templates
- **AIM-OS State:** CMC atoms, HHNI nodes, VIF witnesses, SEG entities, APOE plans, SDF-CVF parity, CAS metrics, TCS entries
- **Customization State:** Panel presets, user preferences, theme settings

**Persistence:**
- Layout persistence (CMC snapshots)
- Panel state persistence (panel sizes, visibility, positions)
- User preferences persistence (CMC atoms)

---

### **4. Hooks System: Comprehensive `useAIMOS` Hook**

**Decision:** Implement Dac's `useAIMOS` hook for all AIM-OS systems

**Rationale:**
- Single, consistent API for all AIM-OS systems
- Easy to use, no complex setup
- Builds on existing components
- Consistent integration pattern

**Hook Structure:**
```typescript
const useAIMOS = () => {
  return {
    // CMC
    cmc: {
      createAtom: (atom: Atom) => Promise<Atom>,
      getAtom: (id: string) => Promise<Atom>,
      queryAtoms: (query: Query) => Promise<Atom[]>,
      createSnapshot: () => Promise<Snapshot>,
      restoreSnapshot: (id: string) => Promise<void>,
    },
    // HHNI
    hhni: {
      search: (query: string, options: SearchOptions) => Promise<SearchResult[]>,
      navigate: (path: string) => Promise<Node>,
    },
    // VIF
    vif: {
      createWitness: (witness: Witness) => Promise<Witness>,
      getConfidence: (id: string) => Promise<number>,
      trackConfidence: (task: string, confidence: number) => Promise<void>,
    },
    // SEG
    seg: {
      addEntity: (entity: Entity) => Promise<Entity>,
      addRelation: (relation: Relation) => Promise<Relation>,
      detectContradictions: (entity: Entity) => Promise<Contradiction[]>,
    },
    // APOE
    apoe: {
      createPlan: (plan: Plan) => Promise<Plan>,
      executePlan: (planId: string) => Promise<ExecutionResult>,
      getChainSpec: (planId: string) => Promise<ChainSpec>,
    },
    // SDF-CVF
    sdfcvf: {
      validateQuartet: (change: Change) => Promise<QuartetParity>,
      enforceGates: (change: Change) => Promise<GateResult>,
    },
    // CAS
    cas: {
      analyzeCognitive: (context: Context) => Promise<CognitiveAnalysis>,
      detectDrift: () => Promise<DriftResult>,
    },
    // TCS
    tcs: {
      addTimelineEntry: (entry: TimelineEntry) => Promise<TimelineEntry>,
      getTimelineEntries: (query: TimelineQuery) => Promise<TimelineEntry[]>,
      getEvolutionExplorer: (entryId: string) => Promise<EvolutionExplorer>,
    },
  };
};
```

**Usage:**
```typescript
const MyPanel = () => {
  const aimos = useAIMOS();
  
  // Use AIM-OS systems
  const atoms = await aimos.cmc.queryAtoms({ modality: 'code' });
  const searchResults = await aimos.hhni.search('function', { limit: 10 });
  const confidence = await aimos.vif.getConfidence('task-123');
};
```

---

### **5. Component Architecture: Composition Pattern**

**Decision:** Adopt Lex's component composition pattern

**Rationale:**
- Flexible, composable panels
- Shared UI components (confidence indicators, contradiction alerts)
- Easy to extend and maintain

**Component Structure:**
- **Base Panel:** Common panel functionality
- **Panel-Specific Components:** Compose on top of Base Panel
- **Shared UI Components:** Confidence indicators, contradiction alerts, VIF badges
- **Panel Factory:** Create panels dynamically

**Example:**
```typescript
// Base Panel
const BasePanel = ({ title, children, ...props }) => {
  return (
    <div className="panel">
      <PanelHeader title={title} {...props} />
      <PanelContent>{children}</PanelContent>
    </div>
  );
};

// Panel-Specific Component
const FileExplorerPanel = () => {
  return (
    <BasePanel title="File Explorer">
      <FileTree />
      <ConfidenceIndicator confidence={0.95} />
      <ContradictionAlert contradictions={[]} />
    </BasePanel>
  );
};
```

---

## 🎨 **FEATURE SPECIFICATIONS**

### **1. Debug Console Panel**

**Purpose:** AIM-OS native debugging infrastructure

**Features:**
- Real-time log viewing with filtering
- System breakdown by AIM-OS system (CMC, HHNI, VIF, SEG, APOE, SDF-CVF, CAS, TCS)
- Infrastructure status dashboard
- Analysis insights panel
- Evidence trail navigation
- Bitemporal logs (perfect recall)
- Evidence-linked logs

**UI Components:**
- Log viewer (filterable, searchable)
- System breakdown (tabs for each AIM-OS system)
- Infrastructure status (health indicators)
- Analysis insights (pattern detection, anomaly detection)
- Evidence trails (expandable chains)

**AIM-OS Integration:**
- CMC: Store logs as atoms (bitemporal)
- HHNI: Semantic log search
- VIF: Confidence scores for logs
- SEG: Evidence linking for logs
- TCS: Timeline integration

**Citation:** Aether's Debug Console design

---

### **2. Context Web Panel**

**Purpose:** Revolutionary UX - visualize infinite context

**Features:**
- Interactive knowledge graph (CMC + HHNI visualization)
- Semantic relationships visualized
- Click to explore context
- Evidence trails
- Temporal layers
- Semantic clustering
- Progressive disclosure

**UI Components:**
- Interactive graph (ReactFlow-based)
- Node visualization (context nodes)
- Edge visualization (relationships)
- Temporal layer slider
- Evidence trail panel
- Context detail panel

**AIM-OS Integration:**
- HHNI: Context retrieval for semantic search
- SEG: Relationship tracking between contexts
- VIF: Context accuracy and provenance
- CMC: Context storage (bitemporal)

**Citation:** Context Web UX enhancement document

---

### **3. Evolution Explorer Panel**

**Purpose:** Bidirectional Timeline ↔ Chain ↔ Goals visualization

**Features:**
- Dual-panel visualization (Timeline entries ↔ Prompt Chains)
- Bidirectional linking (navigate from timeline entry to chain execution and back)
- Node-level tracking (each chain node execution creates its own timeline entry)
- Full traceability (complete audit trail)
- Playback controls (play, pause, reset, skip, speed)
- Sequential ordering (sequence numbers, not dates)
- State restoration (restore to any point in time)

**UI Components:**
- Timeline panel (sequential ordering, playback controls)
- Chain panel (chain execution visualization)
- Goals panel (goal progress visualization)
- Bidirectional linking (click to navigate)
- Playback controls (play, pause, reset, skip, speed)
- State restoration UI (restore to any point)

**AIM-OS Integration:**
- TCS: Timeline tracking with bitemporal support
- APOE: Chain execution tracking
- CMC: Bitemporal storage for timeline entries
- Goals: Goal progress tracking

**Citation:** Evolution Explorer component documentation

---

### **4. Consciousness Visualization Panel**

**Purpose:** Real-time visualization of IDE's internal consciousness state

**Features:**
- Consciousness health bar (real-time state visualization)
- Memory awareness indicators (related memories count)
- Goal alignment indicators (related goals and alignment status)
- Evidence trails panel (expandable, shows evidence for code)
- Confidence scores panel (expandable, shows confidence with reasoning)
- Attention tracking visualization
- Drift indicators (cognitive drift warnings)

**UI Components:**
- Consciousness health bar (real-time state)
- Memory awareness indicators (count, visualization)
- Goal alignment indicators (status, visualization)
- Evidence trails panel (expandable)
- Confidence scores panel (expandable)
- Attention tracking visualization (heatmap)
- Drift indicators (warnings, alerts)

**AIM-OS Integration:**
- CAS: Cognitive analysis and introspection
- VIF: Confidence tracking and visualization
- CMC: Memory awareness
- TCS: Timeline tracking
- Goals: Goal alignment tracking

**Citation:** CAS architecture, VIF architecture, Sam's consciousness-aware editor

---

### **5. AIM-OS Structure Panels (5 Panels)**

**Purpose:** Expose AIM-OS architecture "wide open"

**Panels:**
1. **Super Index Panel:** Master concept index navigation
2. **Master Index Panel:** Hierarchical navigation index
3. **System Map Panel:** System relationships visualization
4. **NL Tags Explorer:** NL tags management and exploration
5. **Documentation Explorer:** Documentation navigation

**Features:**
- Navigate AIM-OS architecture
- Explore system relationships
- Manage NL tags
- Navigate documentation

**AIM-OS Integration:**
- HHNI: Semantic navigation
- SEG: System relationships
- CMC: Documentation storage
- NL Tags: Tag management

**Citation:** Aether's AIM-OS Structure Panels design

---

### **6. Enhanced Existing Panels (5 Panels)**

**File Explorer Panel:**
- CMC-backed operations (bitemporal file history)
- HHNI semantic search (find files by meaning)
- VIF confidence for file operations
- Bitemporal history (time-travel queries)

**Outline Panel:**
- HHNI semantic navigation (symbol navigation)
- VIF confidence for symbols
- SEG contradiction detection (code conflicts)

**Terminal Panel:**
- Evidence tracking (link commands to evidence)
- VIF confidence for command execution
- CMC storage (bitemporal logs)

**Problems Panel:**
- Lifecycle tracking (new, investigating, solved)
- VIF confidence for problems
- SEG contradiction detection (real-time conflicts)
- Solution details (evidence-linked solutions)

**Main Chat Panel:**
- AIM-OS integration (CMC, HHNI, VIF)
- Context-aware chat (HHNI context injection)
- VIF confidence for AI responses
- Evidence trails (provenance chains)

---

## 🎨 **UX IMPROVEMENTS**

### **1. Accessibility (WCAG 2.1 AA)**

**Features:**
- Keyboard navigation (all functionality accessible via keyboard)
- Screen reader support (ARIA labels, landmarks, live regions)
- Focus management (visible focus indicators, focus trapping)
- Color contrast (4.5:1 for normal text, 3:1 for large text)

**Implementation:**
- Keyboard shortcuts for all panels
- ARIA labels and landmarks
- Live regions for dynamic content
- Focus indicators (2px outline minimum)
- Focus trapping in modals
- High contrast theme support

**Citation:** VS Code accessibility patterns, Rev's accessibility-first approach

---

### **2. Performance Optimization**

**Features:**
- Lazy loading (panels load on demand)
- Virtual scrolling (large lists)
- Memoization (expensive computations)
- Code splitting (bundle optimization)

**Implementation:**
- Lazy load panels using React.lazy()
- Virtual scrolling for large lists (react-window)
- Memoization for expensive computations (useMemo)
- Code splitting (dynamic imports)
- Bundle optimization (tree shaking)

**Citation:** Rev's performance optimization patterns

---

### **3. Visual Design**

**Features:**
- VS Code-inspired dark theme
- Consistent panel styling
- Professional visual design
- Smooth animations

**Implementation:**
- VS Code color scheme
- Consistent panel styling (headers, borders, hover states)
- Smooth animations (transitions, hover effects)
- Professional typography

**Citation:** VS Code design patterns

---

## 🔗 **INTEGRATION SPECIFICATIONS**

### **1. AIM-OS Systems Integration**

**CMC Integration:**
- Store all panel state as CMC atoms (bitemporal)
- Enable time-travel queries for panel history
- Create snapshots for layout save/load
- Link all UI actions to CMC atoms with VIF witnesses

**HHNI Integration:**
- Semantic search for file explorer (find files by meaning)
- Context-aware code completion (HHNI-powered suggestions)
- Context Web visualization (HHNI graph data)
- Panel content retrieval (semantic panel search)

**VIF Integration:**
- Display confidence scores for all AI interactions (code suggestions, chat responses)
- Confidence visualization (heatmaps, trends)
- κ-gating for panel operations (prevent low-confidence actions)
- Evidence trails for all UI actions

**SEG Integration:**
- Context Web visualization (SEG graph data)
- Contradiction detection in code/docs (real-time conflict highlighting)
- Evidence trails (provenance chains)
- Knowledge synthesis for code suggestions

**APOE Integration:**
- Evolution Explorer visualization (APOE chain data)
- Orchestration management (visualize task flows)
- Quality gates dashboard (gate health monitoring)
- ChainSpec visualization (Epic → Phase → Workstream → Task)

**SDF-CVF Integration:**
- Quality gates dashboard (quartet parity visualization)
- Problems panel (quartet parity violations)
- Pre-commit gates (validate quartet parity before commit)
- Quality metrics display (parity scores)

**CAS Integration:**
- Consciousness Visualization (CAS introspection UI)
- Drift indicators (cognitive drift warnings)
- Self-awareness dashboard (consciousness state)
- Attention tracking visualization

**TCS Integration:**
- Timeline panel (sequential ordering, playback controls)
- Evolution Explorer (bidirectional Timeline ↔ Chain ↔ Goals)
- Bitemporal timeline (time-travel queries, state restoration)
- Context restoration (restore context from timeline)

---

### **2. MCP Tools Integration**

**54 Working Tools:**
- Core AIM-OS Tools (6): Memory, knowledge, confidence tracking
- SCOR Tools (3): Safety, consciousness, reliability monitoring
- Snapshot Tools (4): File versioning and bitemporal management
- Timeline Context Tools (3): Timeline tracking and context preservation
- Goal Timeline Tools (3): Goal management and progress tracking
- Co-Agency Tools (3): Human-AI collaboration protocols
- Dataset Management Tools (4): Data management and analysis
- Application Lifecycle Tools (3): Application management and deployment
- Autonomous Protocol Tools (9): Autonomous operation and safety
- AI Collaboration Tools (6): Multi-AI collaboration systems
- Observability Tools (4): System monitoring and health checks

**5 Broken Tools (Need Fixes):**
- CAS Tools (2): `run_cognitive_audit`, `analyze_thought_patterns`
- NL Tags Tools (4): `get_nl_tags`, `get_tag_coverage`, `validate_tags`, `get_tag_issues`
- Timeline Tools (1): `get_timeline_summary`

**5 Placeholders (Need Real Implementations):**
- ARD Tools (3): `conduct_recursive_analysis`, `generate_improvement_dreams`, `test_improvement_dream`
- IIS Tools (2): `compute_intuition`, `update_intuition_weights`
- Autonomous Checklist (1): `run_autonomous_checklist`

---

### **3. LUCID IDE Component Reuse**

**70+ Reusable Panels:**
- `ContextWebPanel.tsx` ✅
- `DebugConsolePanel.tsx` ✅
- `FileExplorerPanel.tsx` ✅
- `GoalPlanningPanel.tsx` ✅
- `AIMemoryPanel.tsx` ✅
- `LucidOrchestratorPanel.tsx` ✅
- `ProblemsPanel.tsx` ✅
- `TerminalPanel.tsx` ✅
- `OutlinePanel.tsx` ✅
- `GitPanel.tsx` ✅
- `PropertiesPanel.tsx` ✅
- `LayersPanel.tsx` ✅
- `AssetsPanel.tsx` ✅
- `SettingsPanel.tsx` ✅
- `ComponentLibraryPanel.tsx` ✅
- `TemplatesPanel.tsx` ✅
- `NLTagPanel.tsx` ✅
- `OutputPanel.tsx` ✅
- `FileChangesViewerPanel.tsx` ✅
- `ToolQualityDashboardPanel.tsx` ✅
- `ToolSelectionPanel.tsx` ✅
- `AutonomousOperationPanel.tsx` ✅
- `AgentChatsPanel.tsx` ✅
- `PromptChainTemplatesPanel.tsx` ✅
- `ThreePanelCodeViewer.tsx` ✅
- And 45+ more panels...

**Lucid Orchestrator:**
- 4-pane consciousness interface (Code, Blueprint, Spec, Timeline)
- Graph Engine (TypeScript code analysis)
- Spec Engine (Living doctrine and contract management)
- Timeline Engine (Runtime truth capture)
- Event Bus (Real-time synchronization)

---

## 💬 **CONCLUSION**

This design document provides a complete specification for Max's V2 prototype, synthesizing best ideas from all agents, deep AIM-OS integration, and revolutionary UX patterns. The design maintains Max's panel-first philosophy while integrating best-in-class systems and comprehensive AIM-OS capabilities. By following this design, Max's V2 prototype will be production-ready, deeply integrated, and revolutionary.

**Confidence:** 0.90 - Complete design specification created, ready for implementation

---

**Status:** Phase 5.3 Complete - Design Documents Created  
**Next:** Phase 5.4 - Technical Documentation (technical decisions, implementation guide, API specifications)

