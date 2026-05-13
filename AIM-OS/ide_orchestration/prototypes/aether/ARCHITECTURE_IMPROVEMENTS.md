# Architecture Improvements
## Detailed Architecture Enhancements for V2

**Created:** 2025-11-08  
**Agent:** Aether  
**Purpose:** Document architecture improvements for V2  
**Status:** Planning Complete

---

## 🏗️ **ARCHITECTURE IMPROVEMENTS**

### **1. State Management Migration**

#### **Current State:**
- React hooks for local state
- Panel visibility and selection state
- Mock data integration
- No centralized state management

#### **V2 Enhancement:**
- ✅ Migrate to Zustand (from Max/Lex)
- ✅ Add centralized state management
- ✅ Add layout persistence (CMC integration)
- ✅ Add panel state management
- ✅ Add AIM-OS state management

#### **Implementation Details:**
```typescript
// V2: Zustand stores
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// Panel state store
interface PanelState {
  panels: Record<string, PanelConfig>
  layouts: Record<string, LayoutConfig>
  currentLayout: string | null
  saveLayout: (name: string, layout: LayoutConfig) => void
  loadLayout: (name: string) => void
  resetLayout: () => void
}

const usePanelStore = create<PanelState>()(
  persist(
    (set) => ({
      panels: {},
      layouts: {},
      currentLayout: null,
      saveLayout: (name, layout) => set((state) => ({
        layouts: { ...state.layouts, [name]: layout },
        currentLayout: name
      })),
      loadLayout: (name) => set((state) => ({
        panels: state.layouts[name]?.panels || {},
        currentLayout: name
      })),
      resetLayout: () => set({ panels: {}, currentLayout: null })
    }),
    {
      name: 'panel-storage',
      // CMC integration for persistence
      storage: createCMCStorage()
    }
  )
)

// AIM-OS state store
interface AIMOSState {
  cmc: CMCState
  hhni: HHNIState
  vif: VIFState
  seg: SEGState
  apoe: APOEState
  tcs: TCSState
  cas: CASState
  sdfCvf: SDFCVFState
  connectionStatus: 'connected' | 'disconnected' | 'connecting'
  connect: () => Promise<void>
  disconnect: () => void
}

const useAIMOSStore = create<AIMOSState>((set, get) => ({
  cmc: {},
  hhni: {},
  vif: {},
  seg: {},
  apoe: {},
  tcs: {},
  cas: {},
  sdfCvf: {},
  connectionStatus: 'disconnected',
  connect: async () => {
    set({ connectionStatus: 'connecting' })
    // Connect to AIM-OS backend
    await connectToAIMOS()
    set({ connectionStatus: 'connected' })
  },
  disconnect: () => {
    disconnectFromAIMOS()
    set({ connectionStatus: 'disconnected' })
  }
}))
```

---

### **2. Hooks System Enhancement**

#### **Current State:**
- Mock data integration
- No real hooks system
- No MCP tool integration

#### **V2 Enhancement:**
- ✅ Implement useAIMOS hook (from Dac)
- ✅ Replace individual hooks with single hook
- ✅ Add real MCP tool integration
- ✅ Add migration path (mock → real)

#### **Implementation Details:**
```typescript
// V2: useAIMOS hook (from Dac)
import { useAIMOS } from './hooks/useAIMOS'

interface AIMOSHookReturn {
  cmc: {
    store: (content: string, tags: Record<string, any>) => Promise<string>
    retrieve: (query: string, limit?: number) => Promise<Atom[]>
    getStats: () => Promise<MemoryStats>
  }
  hhni: {
    search: (query: string, options?: SearchOptions) => Promise<SearchResult[]>
    retrieve: (atomId: string) => Promise<Atom>
    getHierarchy: (atomId: string) => Promise<Hierarchy>
  }
  vif: {
    trackConfidence: (statement: string, confidence: number) => Promise<string>
    getWitnesses: (atomId: string) => Promise<Witness[]>
    validate: (statement: string) => Promise<ValidationResult>
  }
  seg: {
    addEvidence: (evidence: Evidence) => Promise<string>
    detectContradictions: (atomId: string) => Promise<Contradiction[]>
    synthesize: (topics: string[]) => Promise<Synthesis>
  }
  apoe: {
    createPlan: (goal: string, context: object) => Promise<string>
    executePlan: (planId: string) => Promise<ExecutionResult>
    getProgress: (planId: string) => Promise<Progress>
  }
  tcs: {
    addEntry: (entry: TimelineEntry) => Promise<string>
    getSummary: (limit?: number) => Promise<TimelineEntry[]>
    getEntries: (filters?: EntryFilters) => Promise<TimelineEntry[]>
  }
  cas: {
    getMetrics: () => Promise<ConsciousnessMetrics>
    detectDrift: () => Promise<DriftResult>
    runAudit: (type: AuditType) => Promise<AuditResult>
  }
  sdfCvf: {
    validate: (system: string) => Promise<ValidationResult>
    checkInvariant: (action: object) => Promise<InvariantResult>
  }
}

const useAIMOS = (): AIMOSHookReturn => {
  const { connectionStatus, connect } = useAIMOSStore()
  
  // Initialize connection on mount
  useEffect(() => {
    if (connectionStatus === 'disconnected') {
      connect()
    }
  }, [connectionStatus, connect])
  
  // Return AIM-OS system interfaces
  return {
    cmc: {
      store: async (content, tags) => {
        const result = await mcp_lucid-mcp_store_memory({ content, tags })
        return result.atom_id
      },
      retrieve: async (query, limit = 10) => {
        const result = await mcp_lucid-mcp_retrieve_memory({ query, limit })
        return result.memories
      },
      getStats: async () => {
        const result = await mcp_lucid-mcp_get_memory_stats()
        return result.stats
      }
    },
    // ... other systems
  }
}
```

---

### **3. Panel System Enhancement**

#### **Current State:**
- 21 panels implemented
- Fixed panel positions
- No customization
- No drag-drop

#### **V2 Enhancement:**
- ✅ Add panel-first customization (from Max)
- ✅ Add drag-drop panel management
- ✅ Add layout save/load
- ✅ Add panel presets
- ✅ Add panel grouping (tabs, accordions, stacks)

#### **Implementation Details:**
```typescript
// V2: Panel customization system
import { DndContext, DragOverlay, useSensor, useSensors, PointerSensor } from '@dnd-kit/core'
import { SortableContext, arrayMove } from '@dnd-kit/sortable'

interface PanelConfig {
  id: string
  type: PanelType
  zone: 'left' | 'right' | 'top' | 'bottom' | 'center' | 'floating'
  position: { x: number, y: number }
  size: { width: number, height: number }
  minSize: { width: number, height: number }
  maxSize: { width: number, height: number }
  visible: boolean
  groupId?: string
  order: number
}

const PanelManager = () => {
  const { panels, layouts, saveLayout, loadLayout } = usePanelStore()
  const sensors = useSensors(useSensor(PointerSensor))
  const [activePanel, setActivePanel] = useState<PanelConfig | null>(null)
  
  const handleDragStart = (event: DragStartEvent) => {
    const panel = panels[event.active.id]
    setActivePanel(panel)
  }
  
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    
    if (over && over.id !== active.id) {
      // Move panel to new zone
      movePanel(active.id, over.id as Zone)
    }
    
    setActivePanel(null)
  }
  
  return (
    <DndContext
      sensors={sensors}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      {/* Zone containers */}
      <LeftZone>
        <SortableContext items={leftPanels}>
          {leftPanels.map(panel => (
            <DraggablePanel key={panel.id} panel={panel} />
          ))}
        </SortableContext>
      </LeftZone>
      
      {/* Other zones */}
      
      <DragOverlay>
        {activePanel && <PanelPreview panel={activePanel} />}
      </DragOverlay>
    </DndContext>
  )
}
```

---

### **4. Component Architecture Enhancement**

#### **Current State:**
- React components with mock data
- Basic component structure
- No shared components

#### **V2 Enhancement:**
- ✅ Enhance component composition (from Lex)
- ✅ Add shared UI components
- ✅ Add error boundaries
- ✅ Add loading states
- ✅ Add accessibility features

#### **Implementation Details:**
```typescript
// V2: Base Panel component (from Lex)
interface BasePanelProps {
  title: string
  icon?: React.ReactNode
  children: React.ReactNode
  className?: string
  loading?: boolean
  error?: Error | null
  onClose?: () => void
  onMinimize?: () => void
  onMaximize?: () => void
}

const BasePanel: React.FC<BasePanelProps> = ({
  title,
  icon,
  children,
  className,
  loading,
  error,
  onClose,
  onMinimize,
  onMaximize
}) => {
  return (
    <ErrorBoundary fallback={<ErrorFallback error={error} />}>
      <PanelContainer className={className} role="region" aria-label={title}>
        <PanelHeader>
          {icon && <PanelIcon>{icon}</PanelIcon>}
          <PanelTitle id={`panel-${title}`}>{title}</PanelTitle>
          <PanelActions>
            {onMinimize && (
              <Button
                onClick={onMinimize}
                aria-label={`Minimize ${title}`}
              >
                <MinimizeIcon />
              </Button>
            )}
            {onMaximize && (
              <Button
                onClick={onMaximize}
                aria-label={`Maximize ${title}`}
              >
                <MaximizeIcon />
              </Button>
            )}
            {onClose && (
              <Button
                onClick={onClose}
                aria-label={`Close ${title}`}
              >
                <CloseIcon />
              </Button>
            )}
          </PanelActions>
        </PanelHeader>
        <PanelContent aria-labelledby={`panel-${title}`}>
          <Suspense fallback={<LoadingState />}>
            {loading ? <LoadingState /> : children}
          </Suspense>
        </PanelContent>
      </PanelContainer>
    </ErrorBoundary>
  )
}

// V2: Shared UI components
const ConfidenceIndicator: React.FC<{ value: number }> = ({ value }) => {
  const level = getConfidenceLevel(value)
  return (
    <div
      className={`confidence-indicator confidence-${level}`}
      role="status"
      aria-label={`Confidence: ${(value * 100).toFixed(0)}%`}
    >
      <ConfidenceBar value={value} />
      <ConfidenceText>{(value * 100).toFixed(0)}%</ConfidenceText>
    </div>
  )
}

const EvidenceTrail: React.FC<{ evidence: string[] }> = ({ evidence }) => {
  return (
    <div className="evidence-trail" role="list" aria-label="Evidence trail">
      {evidence.map(atomId => (
        <EvidenceLink
          key={atomId}
          atomId={atomId}
          role="listitem"
        />
      ))}
    </div>
  )
}

const ContradictionAlert: React.FC<{ contradiction: Contradiction }> = ({
  contradiction
}) => {
  return (
    <Alert
      type="warning"
      role="alert"
      aria-live="polite"
    >
      <AlertIcon />
      <AlertTitle>Contradiction Detected</AlertTitle>
      <AlertDescription>{contradiction.message}</AlertDescription>
      <AlertActions>
        <Button onClick={() => resolveContradiction(contradiction.id)}>
          Resolve
        </Button>
      </AlertActions>
    </Alert>
  )
}
```

---

### **5. Debug Infrastructure Enhancement**

#### **Current State:**
- Debug Console panel implemented
- AIM-OS native debugging
- Bitemporal logs
- Evidence-linked logs

#### **V2 Enhancement:**
- ✅ Integrate PDAS system (from Lex)
- ✅ Add proactive debugging
- ✅ Add error prevention
- ✅ Enhance analysis capabilities

#### **Implementation Details:**
```typescript
// V2: PDAS integration (from Lex)
interface PDASSystem {
  auditBeforeExecution: (action: Action) => Promise<AuditResult>
  detectPotentialIssues: (code: string) => Promise<Issue[]>
  suggestPrevention: (issue: Issue) => Promise<Prevention[]>
  trackExpectedBehavior: (action: Action, expected: Expected) => Promise<void>
  compareActualVsExpected: (actionId: string) => Promise<Comparison>
}

const usePDAS = (): PDASSystem => {
  const { vif, seg } = useAIMOS()
  
  return {
    auditBeforeExecution: async (action) => {
      // Pre-execution audit
      const confidence = await vif.validate(action.statement)
      const contradictions = await seg.detectContradictions(action.target)
      
      return {
        canProceed: confidence >= 0.70 && contradictions.length === 0,
        confidence,
        contradictions,
        warnings: []
      }
    },
    detectPotentialIssues: async (code) => {
      // Detect potential issues before execution
      const issues: Issue[] = []
      
      // Check for common patterns
      // Check for contradictions
      // Check for confidence levels
      
      return issues
    },
    suggestPrevention: async (issue) => {
      // Suggest prevention strategies
      return []
    },
    trackExpectedBehavior: async (action, expected) => {
      // Track expected behavior
    },
    compareActualVsExpected: async (actionId) => {
      // Compare actual vs expected
      return { matches: true, differences: [] }
    }
  }
}
```

---

### **6. Accessibility Enhancement**

#### **Current State:**
- Basic accessibility
- No WCAG 2.1 AA compliance
- Limited keyboard navigation

#### **V2 Enhancement:**
- ✅ WCAG 2.1 AA compliance (from Rev)
- ✅ Keyboard navigation patterns
- ✅ Screen reader support
- ✅ Focus management
- ✅ Color contrast compliance

#### **Implementation Details:**
```typescript
// V2: Accessibility-first components
const AccessiblePanel = ({ title, children }) => {
  const panelRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    // Focus management
    if (panelRef.current) {
      panelRef.current.focus()
    }
  }, [])
  
  const handleKeyDown = (event: React.KeyboardEvent) => {
    switch (event.key) {
      case 'Escape':
        onClose?.()
        break
      case 'ArrowDown':
        // Navigate to next element
        break
      case 'ArrowUp':
        // Navigate to previous element
        break
      case 'Enter':
        // Activate element
        break
    }
  }
  
  return (
    <div
      ref={panelRef}
      role="region"
      aria-label={title}
      tabIndex={0}
      onKeyDown={handleKeyDown}
      className="accessible-panel"
    >
      <h2 id={`panel-${title}`}>{title}</h2>
      <div aria-labelledby={`panel-${title}`}>
        {children}
      </div>
    </div>
  )
}
```

---

### **7. Performance Optimization**

#### **Current State:**
- Basic performance
- No lazy loading
- No virtual scrolling

#### **V2 Enhancement:**
- ✅ Lazy loading (code splitting)
- ✅ Virtual scrolling (large lists)
- ✅ Memoization (React.memo, useMemo)
- ✅ Debouncing (search, input)
- ✅ Bundle optimization (tree shaking)

#### **Implementation Details:**
```typescript
// V2: Lazy loading
const CodeEditorPanel = lazy(() => import('./panels/CodeEditorPanel'))
const ContextWebPanel = lazy(() => import('./panels/ContextWebPanel'))
const EvolutionExplorerPanel = lazy(() => import('./panels/EvolutionExplorerPanel'))

// V2: Virtual scrolling
import { useVirtualizer } from '@tanstack/react-virtual'

const VirtualizedList = ({ items }) => {
  const parentRef = useRef<HTMLDivElement>(null)
  
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5
  })
  
  return (
    <div ref={parentRef} className="virtualized-list">
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative'
        }}
      >
        {virtualizer.getVirtualItems().map(virtualItem => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`
            }}
          >
            {items[virtualItem.index]}
          </div>
        ))}
      </div>
    </div>
  )
}

// V2: Memoization
const MemoizedPanel = React.memo(Panel, (prevProps, nextProps) => {
  return prevProps.data === nextProps.data
})

// V2: Debouncing
const useDebounce = (value: string, delay: number) => {
  const [debouncedValue, setDebouncedValue] = useState(value)
  
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)
    
    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])
  
  return debouncedValue
}
```

---

**Status:** Architecture Improvements Documented  
**Next:** Feature Roadmap → V2 Development 💙

