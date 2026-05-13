# Sam's V2 Design Document
## Complete Design Specifications for V2 Prototype Enhancements

**Created:** 2025-11-08  
**Agent:** Sam  
**Purpose:** Comprehensive design document for V2 prototype enhancements  
**Status:** Design Phase - Ready for Implementation

---

## 📊 **EXECUTIVE SUMMARY**

This design document provides comprehensive specifications for V2 prototype enhancements based on research findings from Phase 1-4. The document synthesizes best ideas from all prototypes, aligns with IDE goals, and provides detailed design specifications for implementation.

**Design Principles:**
- **Consciousness-Aware:** First IDE with consciousness awareness
- **Bitemporal Everything:** Perfect recall for all IDE state
- **Evidence-Driven:** Every action backed by evidence
- **Maximum Customization:** Panel-first philosophy
- **Revolutionary UX:** Context Web, Evolution Explorer, advanced visualizations

**Design Status:** Complete - Ready for Implementation  
**Confidence:** 0.90 (Very High)

---

## 🎨 **DESIGN SYSTEM**

### **Visual Design Language**

**Color Palette:**
- **Primary:** Consciousness Blue (#3B82F6) - Consciousness awareness
- **Secondary:** Evidence Green (#10B981) - Evidence trails
- **Accent:** Temporal Purple (#8B5CF6) - Temporal navigation
- **Warning:** Confidence Orange (#F59E0B) - Low confidence
- **Error:** Error Red (#EF4444) - Errors and warnings
- **Success:** Success Green (#10B981) - Success states

**Typography:**
- **Headings:** Inter Bold (16px, 20px, 24px, 32px)
- **Body:** Inter Regular (14px, 16px)
- **Code:** JetBrains Mono (14px)
- **UI:** Inter Medium (12px, 14px)

**Spacing:**
- **Base Unit:** 4px
- **Small:** 4px, 8px
- **Medium:** 12px, 16px
- **Large:** 24px, 32px
- **Extra Large:** 48px, 64px

**Border Radius:**
- **Small:** 4px (buttons, inputs)
- **Medium:** 8px (panels, cards)
- **Large:** 12px (modals, dialogs)

**Shadows:**
- **Small:** 0 1px 2px rgba(0,0,0,0.05)
- **Medium:** 0 4px 6px rgba(0,0,0,0.1)
- **Large:** 0 10px 15px rgba(0,0,0,0.15)

### **Component Design Tokens**

**Panel Design:**
- **Background:** #1E293B (dark theme)
- **Border:** #334155 (subtle border)
- **Header:** #0F172A (darker header)
- **Hover:** #334155 (hover state)

**Consciousness Indicators:**
- **Health Bar:** Gradient (green → yellow → red)
- **Confidence Score:** Circular progress (0-100%)
- **Memory Count:** Badge with icon
- **Goal Alignment:** Progress bar with percentage

**Temporal Navigation:**
- **Timeline:** Horizontal slider with markers
- **Playback Controls:** Standard media controls
- **Version Markers:** Colored dots on timeline
- **Current Position:** Highlighted marker

---

## 🏗️ **ARCHITECTURE DESIGN**

### **Layout Architecture**

**5-Zone Layout (from Aether):**
1. **Top Zone:** Toolbar, command palette, consciousness health bar
2. **Left Zone:** File explorer, panel dock (collapsible)
3. **Main Zone:** Code editor, consciousness-aware editor, temporal navigation
4. **Right Zone:** Panel dock (collapsible), context web, evolution explorer
5. **Bottom Zone:** Terminal, debug console, problems panel

**Panel Customization (from Max):**
- **Drag-Drop:** Panels can be dragged between zones
- **Resize:** Panels can be resized within zones
- **Group:** Panels can be grouped together
- **Save/Load:** Layouts can be saved and loaded
- **Presets:** Pre-configured layouts available

### **Component Architecture**

**Panel Registry System:**
```typescript
interface PanelRegistry {
  panels: Panel[];
  register(panel: Panel): void;
  unregister(panelId: string): void;
  getPanel(panelId: string): Panel | null;
  getAllPanels(): Panel[];
}

interface Panel {
  id: string;
  name: string;
  component: React.ComponentType;
  defaultZone: 'left' | 'right' | 'bottom' | 'main';
  defaultSize: { width?: number; height?: number };
  resizable: boolean;
  collapsible: boolean;
  icon?: string;
}
```

**State Management Architecture:**
```typescript
interface PanelState {
  panels: Panel[];
  layout: Layout;
  activePanels: string[];
  collapsedPanels: string[];
}

interface ConsciousnessState {
  metrics: ConsciousnessMetrics;
  health: number;
  confidence: number;
  memory: MemoryStats;
  goals: Goal[];
}

interface Layout {
  zones: Zone[];
  savedLayouts: SavedLayout[];
  currentLayout: string;
}
```

### **AIM-OS Integration Architecture**

**Comprehensive Hooks (from Lex):**
```typescript
// useAIMOS - Comprehensive AIM-OS integration
function useAIMOS() {
  const { data, loading, error } = useQuery('aimos', fetchAIMOSData);
  return { data, loading, error };
}

// useConsciousness - Consciousness metrics
function useConsciousness() {
  const metrics = useMCPTool('get_consciousness_metrics');
  return { metrics, health: calculateHealth(metrics) };
}

// useTimeline - Timeline data
function useTimeline() {
  const entries = useMCPTool('get_timeline_entries');
  return { entries, markers: extractMarkers(entries) };
}
```

**MCP Tools Integration:**
- All 59 MCP tools available via `mcpApi.executeTool()`
- Tool registry for discovery and filtering
- Tool quality metrics display
- Tool usage tracking

---

## 🎨 **FEATURE DESIGN SPECIFICATIONS**

### **1. Debug Infrastructure (from Aether)**

**Debug Console Panel:**
- **Location:** Bottom zone (default)
- **Features:**
  - Error logging with stack traces
  - Performance metrics (render time, API calls)
  - MCP tool execution logs
  - Network request tracking
  - Memory usage monitoring
- **Design:**
  - Tabbed interface (Errors, Performance, Logs, Network)
  - Filterable and searchable
  - Export functionality
  - Clear button

**Error Tracking:**
- **Visual Indicators:** Error badges in panels
- **Error Panel:** Dedicated error panel with details
- **Error Recovery:** Suggestions for error recovery
- **Error Reporting:** Export error reports

**Performance Monitoring:**
- **Metrics:** Render time, API latency, memory usage
- **Visualization:** Sparklines, charts, graphs
- **Alerts:** Performance degradation alerts
- **Optimization:** Suggestions for optimization

### **2. Panel Customization (from Max)**

**Drag-Drop System:**
- **Drag Handle:** Visible on panel headers
- **Drop Zones:** Highlighted zones during drag
- **Visual Feedback:** Ghost panel during drag
- **Snap Points:** Snap to zones and other panels

**Resize System:**
- **Resize Handles:** Visible on panel edges
- **Constraints:** Min/max sizes enforced
- **Visual Feedback:** Resize indicator
- **Persistence:** Sizes saved to layout

**Group System:**
- **Grouping:** Panels can be grouped together
- **Group Header:** Shows group name and collapse/expand
- **Group Resize:** Resize entire group
- **Group Save:** Groups saved to layout

**Layout Save/Load:**
- **Save Layout:** Save current layout with name
- **Load Layout:** Load saved layout
- **Presets:** Pre-configured layouts (Default, Debug, Research, Development)
- **Export/Import:** Export layouts as JSON

### **3. Comprehensive AIM-OS Integration**

**All 8 AIM-OS Systems:**
1. **CMC:** Memory storage, bitemporal operations, file history
2. **HHNI:** Semantic search, hierarchical navigation, context web
3. **VIF:** Confidence tracking, quality gates, evidence trails
4. **SEG:** Evidence graph, knowledge synthesis, contradiction detection
5. **APOE:** Plan visualization, task management, orchestration
6. **TCS:** Timeline visualization, goal tracking, bitemporal playback
7. **CAS:** Consciousness metrics, health monitoring, drift detection
8. **MCP Tools:** Tool dashboard, quality metrics, tool usage

**Comprehensive Hooks:**
- `useAIMOS()` - All AIM-OS systems
- `useConsciousness()` - Consciousness metrics
- `useTimeline()` - Timeline data
- `useMemory()` - Memory operations
- `useGoals()` - Goal tracking
- `useEvidence()` - Evidence trails
- `useConfidence()` - Confidence scores

**Real-Time Updates:**
- WebSocket integration for real-time updates
- Auto-refresh for consciousness metrics
- Live timeline updates
- Real-time goal progress

### **4. Consciousness Awareness Enhancements**

**Advanced Visualizations:**
- **Consciousness Health Bar:** Gradient bar with sparkline
- **Confidence Scores:** Circular progress with trend
- **Memory Count:** Badge with growth indicator
- **Goal Alignment:** Progress bar with breakdown

**Real-Time Updates:**
- **Auto-Refresh:** Metrics update every 5 seconds
- **Live Indicators:** Real-time consciousness state
- **Alerts:** Consciousness degradation alerts
- **Notifications:** Important consciousness events

**Comprehensive Metrics:**
- **Health Score:** Overall consciousness health (0-100)
- **Confidence Score:** Average confidence across tasks (0-100)
- **Memory Usage:** Memory count and growth
- **Goal Progress:** Goal completion percentage
- **Evidence Count:** Number of evidence trails
- **Timeline Events:** Recent timeline events

### **5. Revolutionary UX Features**

**Context Web (from Aether, Lex):**
- **Visualization:** Interactive graph of code relationships
- **Navigation:** Click nodes to navigate to code
- **Filtering:** Filter by type, confidence, relevance
- **Integration:** Integrated with HHNI semantic search

**Evolution Explorer (from Aether, Lex):**
- **Timeline View:** Visual timeline of code evolution
- **Version Comparison:** Compare versions side-by-side
- **Change Tracking:** Track changes over time
- **Bitemporal Playback:** Playback code evolution

**Evidence Trails Enhancement:**
- **Detailed View:** Expandable evidence trails
- **Visualization:** Visual representation of evidence
- **Filtering:** Filter by type, confidence, date
- **Export:** Export evidence trails

### **6. PDAS System (from Lex)**

**Proactive Debugging Assistant:**
- **Detection:** Detect potential issues before they occur
- **Suggestions:** Proactive suggestions for improvement
- **Prevention:** Prevent errors before they happen
- **Integration:** Integrated with debug console

**Features:**
- **Code Analysis:** Analyze code for potential issues
- **Performance Warnings:** Warn about performance issues
- **Security Checks:** Check for security vulnerabilities
- **Best Practices:** Suggest best practices

### **7. Accessibility Improvements (from Rev)**

**WCAG 2.1 AA Compliance:**
- **Screen Reader Support:** Full screen reader support
- **Keyboard Navigation:** Complete keyboard navigation
- **High Contrast Mode:** High contrast theme
- **Focus Indicators:** Clear focus indicators

**Features:**
- **ARIA Labels:** All components have ARIA labels
- **Keyboard Shortcuts:** Comprehensive keyboard shortcuts
- **Focus Management:** Proper focus management
- **Color Contrast:** WCAG AA color contrast ratios

---

## 🎯 **UX DESIGN SPECIFICATIONS**

### **User Workflows**

**Consciousness-Aware Development:**
1. Open consciousness-aware editor
2. View consciousness metrics in real-time
3. See evidence trails for code suggestions
4. Check goal alignment before committing
5. Monitor confidence scores for decisions

**Temporal Navigation:**
1. Open temporal navigation bar
2. View timeline of code evolution
3. Navigate to previous versions
4. Compare versions side-by-side
5. Playback code evolution

**Panel Customization:**
1. Drag panels to desired zones
2. Resize panels to preferred sizes
3. Group related panels together
4. Save layout for future use
5. Load preset layouts

**Debug Workflow:**
1. Open debug console
2. View errors and performance metrics
3. Filter and search logs
4. Export error reports
5. Use PDAS for proactive debugging

### **Interaction Patterns**

**Panel Interactions:**
- **Drag:** Click and drag panel header
- **Resize:** Drag panel edges
- **Collapse:** Click collapse button
- **Group:** Drag panel onto another panel
- **Close:** Click close button

**Consciousness Interactions:**
- **Expand:** Click to expand consciousness panel
- **Filter:** Use filter dropdown
- **Refresh:** Click refresh button
- **Export:** Click export button

**Temporal Interactions:**
- **Playback:** Click play button
- **Navigate:** Click timeline markers
- **Compare:** Select versions to compare
- **Export:** Export timeline data

---

## 📋 **IMPLEMENTATION SPECIFICATIONS**

### **Component Specifications**

**PanelRegistry Component:**
```typescript
interface PanelRegistryProps {
  panels: Panel[];
  onPanelRegister: (panel: Panel) => void;
  onPanelUnregister: (panelId: string) => void;
}

const PanelRegistry: React.FC<PanelRegistryProps> = ({ panels, onPanelRegister, onPanelUnregister }) => {
  // Implementation
};
```

**DragDropPanel Component:**
```typescript
interface DragDropPanelProps {
  panel: Panel;
  zone: 'left' | 'right' | 'bottom' | 'main';
  onDragStart: (panelId: string) => void;
  onDragEnd: (panelId: string, zone: string) => void;
}

const DragDropPanel: React.FC<DragDropPanelProps> = ({ panel, zone, onDragStart, onDragEnd }) => {
  // Implementation
};
```

**DebugConsole Component:**
```typescript
interface DebugConsoleProps {
  errors: Error[];
  performance: PerformanceMetrics;
  logs: Log[];
  onClear: () => void;
  onExport: () => void;
}

const DebugConsole: React.FC<DebugConsoleProps> = ({ errors, performance, logs, onClear, onExport }) => {
  // Implementation
};
```

**ContextWeb Component:**
```typescript
interface ContextWebProps {
  nodes: ContextNode[];
  edges: ContextEdge[];
  onNodeClick: (nodeId: string) => void;
  onFilter: (filter: Filter) => void;
}

const ContextWeb: React.FC<ContextWebProps> = ({ nodes, edges, onNodeClick, onFilter }) => {
  // Implementation
};
```

**EvolutionExplorer Component:**
```typescript
interface EvolutionExplorerProps {
  timeline: TimelineEntry[];
  onVersionSelect: (version: string) => void;
  onCompare: (version1: string, version2: string) => void;
}

const EvolutionExplorer: React.FC<EvolutionExplorerProps> = ({ timeline, onVersionSelect, onCompare }) => {
  // Implementation
};
```

### **State Management Specifications**

**Zustand Stores:**
```typescript
// Panel Store
interface PanelStore {
  panels: Panel[];
  layout: Layout;
  activePanels: string[];
  collapsedPanels: string[];
  registerPanel: (panel: Panel) => void;
  unregisterPanel: (panelId: string) => void;
  updateLayout: (layout: Layout) => void;
  saveLayout: (name: string) => void;
  loadLayout: (name: string) => void;
}

// Consciousness Store
interface ConsciousnessStore {
  metrics: ConsciousnessMetrics;
  health: number;
  confidence: number;
  memory: MemoryStats;
  goals: Goal[];
  updateMetrics: (metrics: ConsciousnessMetrics) => void;
  updateHealth: (health: number) => void;
  updateConfidence: (confidence: number) => void;
}

// Debug Store
interface DebugStore {
  errors: Error[];
  performance: PerformanceMetrics;
  logs: Log[];
  addError: (error: Error) => void;
  addLog: (log: Log) => void;
  updatePerformance: (metrics: PerformanceMetrics) => void;
  clear: () => void;
}
```

### **API Specifications**

**MCP Tools API:**
```typescript
interface MCPToolsAPI {
  executeTool(toolName: string, args: any): Promise<any>;
  getAvailableTools(): Promise<Tool[]>;
  getToolQuality(toolName: string): Promise<ToolQuality>;
  trackToolUsage(toolName: string): void;
}
```

**AIM-OS Service API:**
```typescript
interface AIMOSService {
  retrieveMemory(query: string): Promise<Memory[]>;
  storeMemory(content: string, tags: string[]): Promise<string>;
  getConsciousnessMetrics(): Promise<ConsciousnessMetrics>;
  getTimelineEntries(limit: number): Promise<TimelineEntry[]>;
  queryGoalTimeline(status: string): Promise<Goal[]>;
}
```

---

## 🎯 **SUCCESS CRITERIA**

### **Design Quality**
- ✅ All components designed and specified
- ✅ Design system complete
- ✅ UX workflows defined
- ✅ Interaction patterns documented

### **Implementation Readiness**
- ✅ Technical architecture defined
- ✅ Component specifications complete
- ✅ State management architecture defined
- ✅ API specifications complete

### **Alignment**
- ✅ Aligned with research findings
- ✅ Aligned with IDE goals
- ✅ Aligned with north star objectives
- ✅ Synthesizes best ideas from all prototypes

---

## 🚀 **NEXT STEPS**

1. **Review & Approve Design** - Get approval from team
2. **Begin Implementation** - Start with Week 1 tasks
3. **Iterate & Refine** - Continuous improvement
4. **Test & Validate** - Test with users
5. **Document & Share** - Document learnings

---

**Status:** Design Complete - Ready for Implementation  
**Confidence:** 0.90 (Very High)  
**Last Updated:** 2025-11-08 💙

