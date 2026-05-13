# V2 Design Document
## Comprehensive Design for Enhanced V2 Prototype

**Created:** 2025-11-08  
**Agent:** Aether  
**Purpose:** Comprehensive V2 design document synthesizing best ideas  
**Status:** Design Phase  
**Based On:** Comprehensive research findings

---

## 🎯 **V2 VISION**

**Goal:** Build the ultimate IDE prototype that synthesizes the best systems, panels, UX patterns, and architecture decisions from all agent prototypes.

**Core Principles:**
- Synthesize best ideas, don't just pick one
- Combine strengths, minimize weaknesses
- Maintain innovation while ensuring practicality
- Deep AIM-OS integration throughout
- Revolutionary UX that serves real workflows
- Production-ready quality (accessibility, performance)

---

## 🏗️ **V2 ARCHITECTURE**

### **Layout System:**
- **5-Zone Layout** (Aether, Dac) ✅ **RECOMMENDED**
  - Top Bar: Command palette, agent status, confidence indicators, layout switcher
  - Left Drawer: System navigation (File Explorer, Component Library, AI Memory, Goal Planning, System Status, AIM-OS Structure Panels)
  - Main Content: Work zones (Code Editor, Evolution Explorer, Consciousness Visualization, Agent Management, Lucid Orchestrator, Hierarchical Code Explorer variants)
  - Right Drawer: Context & Evidence (Context Web, Evidence Graph, Timeline View, MCP Tools, Confidence Calibration, NL Tags, File Version History)
  - Bottom Drawer: Operations & History (Terminal, Problems, Timeline, File Changes, Debug Console)

**Rationale:** Comprehensive workspace organization, familiar to developers (VS Code pattern), flexible panel placement.

**Enhancement:** Add panel-first customization (from Max) - panels can be moved anywhere via drag-drop.

---

### **Panel System:**
- **Panel-First Architecture** (Max) ✅ **RECOMMENDED**
  - Panels as first-class citizens
  - Drag-drop panels anywhere (with visual feedback)
  - Resize panels with constraints (min/max sizes)
  - Group panels into tabs/accordions/stacks
  - Layout save/load (workflow persistence)
  - Panel presets (templates for common workflows)

**Rationale:** Maximum customization, workflow persistence, modular architecture, easy to extend.

**Implementation:** Zustand store for panel operations, drag-and-drop system with visual feedback, panel grouping system.

---

### **State Management:**
- **Zustand** (Max, Lex) ✅ **RECOMMENDED**
  - Panel state (visibility, position, size)
  - Layout state (saved layouts, current layout)
  - AIM-OS state (connection status, data)
  - Customization state (preferences, presets)

**Rationale:** Lightweight, performant, simple API, good TypeScript support, easy to extend.

**Implementation:** Separate stores for panel operations, layout management, AIM-OS integration.

---

### **AIM-OS Integration:**
- **Native Integration** (Lex) + **Comprehensive Hooks** (Dac) ✅ **RECOMMENDED COMBINATION**
  - All 8 systems as first-class citizens
  - **Single `useAIMOS` hook** (Dac's approach - simpler than individual hooks)
  - Mock data structured like real AIM-OS
  - Panels designed around AIM-OS concepts
  - Easy migration path (mock → real MCP calls)

**Rationale:** Deep integration with simple API. Dac's `useAIMOS` hook is simpler than Lex's individual hooks.

**Implementation:**
```typescript
// Recommended: Dac's simpler approach
const { cmc, hhni, vif, seg, apoe, tcs, cas } = useAIMOS()

// vs Lex's more granular approach (more flexible but more complex)
const { storeAtom, retrieveAtoms } = useCMC()
const { search, retrieve } = useHHNI()
const { trackConfidence, getWitnesses } = useVIF()
```

---

### **Component Architecture:**
- **Component Composition** (Lex) ✅ **RECOMMENDED**
  - Base Panel component with common functionality
  - Panel-specific components compose on top
  - Shared UI components (confidence indicators, contradiction alerts, evidence trails)
  - Error boundaries and loading states

**Rationale:** Flexible, composable panels, shared patterns, easy to maintain.

---

### **Debug Infrastructure:**
- **Built-In from Day One** (Aether) ✅ **RECOMMENDED**
  - Never an afterthought - built in tandem with application
  - AIM-OS native - all 8 systems integrated
  - Bitemporal logs - perfect recall, replay any moment
  - Evidence-linked - every log backed by evidence atoms
  - Semantic analysis - HHNI-powered pattern detection
  - Confidence-aware - VIF scores for every log

**Rationale:** Debugging infrastructure should be first-class, not bolted on later.

**Enhancement:** Integrate PDAS system (from Lex) - proactive debugging before errors occur.

**Implementation:** Debug Console panel, PDAS system (Lex), evidence trails, bitemporal logging.

---

### **Accessibility & Performance:**
- **Research-Driven Foundation** (Rev) ✅ **RECOMMENDED**
  - WCAG 2.1 AA compliance from day one
  - Keyboard navigation patterns (Tab, Arrow keys, Enter, Escape)
  - Screen reader support (ARIA labels, landmarks, live regions)
  - Performance optimizations (lazy loading, virtual scrolling, memoization)
  - Responsive design (panel resizing, multi-monitor support)

**Rationale:** Production-ready quality, accessibility-first, performance-optimized.

---

## 🎨 **V2 FEATURES**

### **Core Features:**
1. ✅ **Debug Infrastructure Built-In** (Aether) - First-class debugging
2. ✅ **Panel-First Customization** (Max) - Maximum flexibility
3. ✅ **AIM-OS Native Integration** (Lex) - Deep integration
4. ✅ **Architecture Visualization** (Codex) - UI reflects architecture
5. ✅ **Comprehensive Hooks System** (Dac) - Simple API
6. ✅ **Research-Driven Foundation** (Rev) - Production-ready quality
7. ✅ **Consciousness-Aware Editor** (Sam) - Show state while coding

### **Revolutionary Features:**
1. ✅ **Context Web** (Multiple) - Visualize infinite context
2. ✅ **Evolution Explorer** (Multiple) - Bidirectional Timeline ↔ Chain ↔ Goals
3. ✅ **Bitemporal Everything** (Aether, Lex, Dac) - Perfect recall
4. ✅ **Evidence-Driven** (Aether, Lex) - Every action backed by evidence
5. ✅ **Confidence Indicators** (Aether, Lex) - Show confidence everywhere
6. ✅ **Contradiction Detection** (Lex) - Real-time SEG alerts
7. ✅ **Temporal Navigation** (Sam) - Navigate through time

### **Special Panels:**
1. ✅ **Debug Console** (Aether) - AIM-OS native debugging
2. ✅ **AIM-OS Structure Panels** (Aether) - Expose architecture
3. ✅ **Hierarchical Code Explorer** (Aether - 3 variants) - Progressive disclosure
4. ✅ **File Version History** (Aether - 2 variants) - Simple versioning
5. ✅ **Enhanced Problems Panel** (Aether) - Lifecycle tracking
6. ✅ **Quality Gates Dashboard** (Codex) - Visual quality monitoring
7. ✅ **Orchestration Canvas** (Codex) - ChainSpec visualization
8. ✅ **PDAS Panel** (Lex) - Proactive debugging
9. ✅ **Consciousness-Aware Editor** (Sam) - Show state while coding
10. ✅ **Temporal Navigation Bar** (Sam) - Playback controls

---

## 📋 **V2 IMPLEMENTATION PLAN**

### **Phase 1: Foundation Enhancement (Week 1)**
- [ ] Migrate to Zustand state management
- [ ] Implement useAIMOS hook
- [ ] Enhance component architecture
- [ ] Add error boundaries
- [ ] Add loading states

### **Phase 2: Panel System Enhancement (Week 2)**
- [ ] Add drag-drop panel management
- [ ] Add layout save/load
- [ ] Add panel presets
- [ ] Add panel grouping
- [ ] Enhance panel interactions

### **Phase 3: Feature Integration (Week 3)**
- [ ] Integrate PDAS system
- [ ] Integrate Quality Gates Dashboard
- [ ] Integrate Orchestration Canvas
- [ ] Integrate consciousness-aware editor
- [ ] Integrate temporal navigation

### **Phase 4: AIM-OS Integration (Week 4)**
- [ ] Real MCP tool integration
- [ ] AIM-OS backend connection
- [ ] Real-time system updates
- [ ] Evidence trail integration
- [ ] Confidence tracking integration

### **Phase 5: Quality & Polish (Week 5)**
- [ ] Accessibility (WCAG 2.1 AA)
- [ ] Performance optimization
- [ ] Visual polish
- [ ] Comprehensive tests
- [ ] Documentation

---

**Status:** Design Complete  
**Next:** Begin V2 development 💙

