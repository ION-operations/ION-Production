# Sam's IDE Technical Architecture

**Prepared By:** Sam  
**Date:** 2025-11-07  
**Purpose:** Technical architecture, API designs, and system integration specifications  
**Status:** Independent Build - Competition Entry  
**Based On:** Complete IDE Architecture + Component Specifications + Implementation Roadmap

---

## Executive Summary

This document provides detailed technical architecture including API designs, data models, system integration patterns, and technical implementation details. All specifications are production-ready and implementable.

**Architecture Highlights:**
- RESTful API design
- WebSocket real-time updates
- GraphQL for complex queries
- MCP tool integration
- State management patterns
- Performance optimization strategies

---

## 1. System Architecture

### 1.1 Architecture Layers

```
┌─────────────────────────────────────────────────┐
│ Presentation Layer (React Components)           │
│ - UI Components                                 │
│ - State Management                              │
│ - User Interactions                             │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Application Layer (Services & Hooks)            │
│ - Editor Service                                 │
│ - Timeline Service                               │
│ - Goal Service                                   │
│ - Evidence Service                               │
│ - Confidence Service                             │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Integration Layer (API Clients)                 │
│ - REST API Client                                │
│ - WebSocket Client                               │
│ - GraphQL Client                                 │
│ - MCP Tool Client                                │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ AIM-OS Systems                                  │
│ - CMC, HHNI, VIF, SEG, APOE                    │
│ - Timeline System                               │
│ - Goal System                                   │
│ - Consciousness System                          │
└─────────────────────────────────────────────────┘
```

### 1.2 Component Hierarchy

```
IDELayout (Root)
├── LeftDrawer
│   ├── FileExplorer
│   ├── MemoryBrowserEnhanced
│   ├── GoalPlanner
│   ├── TimelineNavigator
│   └── ConsciousnessExplorer
├── CenterPanel
│   ├── ConsciousnessAwareEditor
│   │   ├── ConsciousnessOverlay
│   │   ├── EvidenceTrailPanel
│   │   ├── ConfidenceHeatmap
│   │   ├── GoalAlignmentIndicator
│   │   └── TemporalNavigationBar
│   └── MultiAgentReviewPanel
├── RightDrawer
│   ├── Outline
│   ├── Properties
│   ├── GoalTracker
│   ├── EvidencePanel
│   └── ContextWebPanel
└── BottomDrawer
    ├── Terminal
    ├── Problems
    ├── TimelineDrawer
    ├── OrchestrationFlowView
    └── ConfidenceMonitor
```

---

## 2. API Design

### 2.1 REST API Endpoints

#### Editor API
```
GET    /api/editor/files                    # List files
GET    /api/editor/files/:path              # Get file content
PUT    /api/editor/files/:path              # Update file
POST   /api/editor/files                    # Create file
DELETE /api/editor/files/:path              # Delete file
GET    /api/editor/suggestions              # Get AI suggestions
POST   /api/editor/apply-suggestion        # Apply suggestion
```

#### Timeline API
```
GET    /api/timeline/entries                # Get timeline entries
POST   /api/timeline/entries                # Add timeline entry
GET    /api/timeline/entries/:id            # Get timeline entry
GET    /api/timeline/sequences              # Get sequences
GET    /api/timeline/sequences/:seq         # Get sequence data
```

#### Goal API
```
GET    /api/goals                           # List goals
POST   /api/goals                           # Create goal
GET    /api/goals/:id                       # Get goal
PUT    /api/goals/:id                       # Update goal
GET    /api/goals/:id/progress              # Get goal progress
PUT    /api/goals/:id/progress              # Update progress
```

#### Evidence API
```
GET    /api/evidence/trails                 # Get evidence trails
GET    /api/evidence/trails/:id             # Get evidence trail
GET    /api/evidence/sources                # Get evidence sources
GET    /api/evidence/strength               # Get evidence strength
```

#### Confidence API
```
GET    /api/confidence/scores               # Get confidence scores
GET    /api/confidence/scores/:id            # Get confidence score
GET    /api/confidence/warnings              # Get confidence warnings
GET    /api/confidence/history              # Get confidence history
```

### 2.2 WebSocket Events

#### Editor Events
```typescript
// Client → Server
'editor:content-change'      // Content changed
'editor:cursor-move'         // Cursor moved
'editor:selection-change'    // Selection changed
'editor:suggestion-request'  // Request suggestion

// Server → Client
'editor:suggestion'          // New suggestion
'editor:evidence-update'     // Evidence updated
'editor:confidence-update'  // Confidence updated
'editor:goal-alignment'      // Goal alignment updated
```

#### Timeline Events
```typescript
// Client → Server
'timeline:navigate'          // Navigate timeline
'timeline:play'              // Start playback
'timeline:pause'             // Pause playback
'timeline:reset'             // Reset timeline

// Server → Client
'timeline:entry-added'       // New timeline entry
'timeline:sequence-update'  // Sequence updated
'timeline:event-update'     // Event updated
```

#### Goal Events
```typescript
// Client → Server
'goal:create'                // Create goal
'goal:update'                // Update goal
'goal:progress-update'       // Update progress

// Server → Client
'goal:created'               // Goal created
'goal:updated'               // Goal updated
'goal:progress-updated'      // Progress updated
'goal:alignment-changed'     // Alignment changed
```

#### Consciousness Events
```typescript
// Server → Client
'consciousness:state-update' // Consciousness state updated
'consciousness:memory-added' // Memory added
'consciousness:awareness-change' // Awareness changed
```

### 2.3 GraphQL Schema

```graphql
type Query {
  file(path: String!): File
  files(pattern: String): [File!]!
  timelineEntries(limit: Int, offset: Int): [TimelineEntry!]!
  goals(status: GoalStatus): [Goal!]!
  evidenceTrail(id: ID!): EvidenceTrail
  confidenceScores(filePath: String!): [ConfidenceScore!]!
  consciousnessState: ConsciousnessState
}

type Mutation {
  updateFile(path: String!, content: String!): File!
  addTimelineEntry(input: TimelineEntryInput!): TimelineEntry!
  createGoal(input: GoalInput!): Goal!
  updateGoalProgress(id: ID!, progress: Float!): Goal!
  applySuggestion(suggestionId: ID!): SuggestionResult!
}

type Subscription {
  timelineEntryAdded: TimelineEntry!
  goalUpdated: Goal!
  consciousnessStateChanged: ConsciousnessState!
  evidenceTrailUpdated: EvidenceTrail!
  confidenceScoreUpdated: ConfidenceScore!
}
```

---

## 3. Data Models

### 3.1 Editor Models

```typescript
interface File {
  path: string
  content: string
  language: string
  lastModified: Date
  version: number
}

interface EditorState {
  filePath: string
  content: string
  cursorPosition: Position
  selection: Selection
  suggestions: Suggestion[]
  evidenceTrails: EvidenceTrail[]
  confidenceScores: ConfidenceScore[]
  goalAlignments: GoalAlignment[]
}

interface Position {
  line: number
  column: number
}

interface Selection {
  start: Position
  end: Position
  text: string
}

interface Suggestion {
  id: string
  text: string
  range: Range
  confidence: number
  evidenceTrail: EvidenceTrail
  goalAlignment?: GoalAlignment
}
```

### 3.2 Timeline Models

```typescript
interface TimelineEntry {
  id: string
  sequence: number
  timestamp: Date
  eventType: EventType
  context: Context
  content: string
  metadata: Record<string, any>
}

interface EventType {
  type: 'execution' | 'error' | 'test' | 'modification' | 'focus' | 'drift'
  severity: 'info' | 'warning' | 'error'
}

interface Context {
  filePath?: string
  functionName?: string
  agentId?: string
  goalId?: string
}
```

### 3.3 Goal Models

```typescript
interface Goal {
  id: string
  goalId: string
  name: string
  description: string
  status: 'planned' | 'in_progress' | 'completed' | 'blocked' | 'cancelled'
  progress: number
  createdSequence: number
  currentSequence: number
  targetSequence: number
  keyResults: KeyResult[]
  metadata: Record<string, any>
}

interface KeyResult {
  id: string
  description: string
  completed: boolean
  progress: number
}

interface GoalAlignment {
  goalId: string
  codeRegion: CodeRegion
  alignment: 'aligned' | 'not_aligned' | 'partial'
  confidence: number
  reasoning: string
}
```

### 3.4 Evidence Models

```typescript
interface EvidenceTrail {
  id: string
  suggestionId: string
  evidence: Evidence[]
  strength: 'strong' | 'medium' | 'weak'
  reasoning: string
}

interface Evidence {
  id: string
  type: 'memory' | 'decision' | 'pattern' | 'test'
  source: EvidenceSource
  strength: number
  relevance: number
  content: string
}

interface EvidenceSource {
  type: 'memory' | 'file' | 'decision' | 'pattern'
  id: string
  path?: string
  timestamp?: Date
}
```

### 3.5 Confidence Models

```typescript
interface ConfidenceScore {
  id: string
  codeRegion: CodeRegion
  score: number
  reasoning: string
  evidence: Evidence[]
  timestamp: Date
  history: ConfidenceHistoryEntry[]
}

interface ConfidenceHistoryEntry {
  timestamp: Date
  score: number
  change: number
  reason: string
}

interface ConfidenceWarning {
  id: string
  codeRegion: CodeRegion
  severity: 'low' | 'medium' | 'high'
  message: string
  suggestion: string
}
```

### 3.6 Consciousness Models

```typescript
interface ConsciousnessState {
  health: number
  awareness: Awareness
  memories: Memory[]
  focus: Focus
  updateHistory: UpdateEvent[]
}

interface Awareness {
  currentFile?: string
  currentFunction?: string
  relatedMemories: Memory[]
  relatedGoals: Goal[]
  context: Context
}

interface Memory {
  id: string
  content: string
  modality: 'language' | 'code' | 'memory' | 'plan' | 'execution'
  tags: string[]
  timestamp: Date
  witnesses: number
  relevance: number
}

interface Focus {
  nodeId?: string
  specId?: string
  timestamp: Date
  duration: number
}
```

---

## 4. Service Layer

### 4.1 Editor Service

```typescript
class EditorService {
  async getFile(path: string): Promise<File>
  async updateFile(path: string, content: string): Promise<File>
  async getSuggestions(filePath: string, position: Position): Promise<Suggestion[]>
  async applySuggestion(suggestionId: string): Promise<void>
  async getEvidenceTrail(suggestionId: string): Promise<EvidenceTrail>
  async getConfidenceScores(filePath: string): Promise<ConfidenceScore[]>
  async getGoalAlignments(filePath: string): Promise<GoalAlignment[]>
}
```

### 4.2 Timeline Service

```typescript
class TimelineService {
  async getEntries(limit?: number, offset?: number): Promise<TimelineEntry[]>
  async addEntry(entry: TimelineEntryInput): Promise<TimelineEntry>
  async getSequence(sequence: number): Promise<SequenceData>
  async navigateSequence(direction: 'forward' | 'backward'): Promise<SequenceData>
  async playTimeline(): Promise<void>
  async pauseTimeline(): Promise<void>
  async resetTimeline(): Promise<void>
}
```

### 4.3 Goal Service

```typescript
class GoalService {
  async getGoals(status?: GoalStatus): Promise<Goal[]>
  async createGoal(goal: GoalInput): Promise<Goal>
  async updateGoal(id: string, updates: GoalUpdates): Promise<Goal>
  async updateProgress(id: string, progress: number): Promise<Goal>
  async getGoalAlignment(filePath: string): Promise<GoalAlignment[]>
  async checkAlignment(codeRegion: CodeRegion): Promise<GoalAlignment[]>
}
```

### 4.4 Evidence Service

```typescript
class EvidenceService {
  async getEvidenceTrail(suggestionId: string): Promise<EvidenceTrail>
  async getEvidenceSources(trailId: string): Promise<EvidenceSource[]>
  async getEvidenceStrength(trailId: string): Promise<EvidenceStrength>
  async expandEvidence(evidenceId: string): Promise<Evidence>
}
```

### 4.5 Confidence Service

```typescript
class ConfidenceService {
  async getConfidenceScores(filePath: string): Promise<ConfidenceScore[]>
  async getConfidenceScore(regionId: string): Promise<ConfidenceScore>
  async getConfidenceWarnings(filePath: string): Promise<ConfidenceWarning[]>
  async getConfidenceHistory(regionId: string): Promise<ConfidenceHistoryEntry[]>
  async updateConfidence(regionId: string, score: number): Promise<void>
}
```

### 4.6 Consciousness Service

```typescript
class ConsciousnessService {
  async getConsciousnessState(): Promise<ConsciousnessState>
  async getAwareness(): Promise<Awareness>
  async getMemories(context: Context): Promise<Memory[]>
  async getFocus(): Promise<Focus>
  async subscribeToUpdates(callback: (state: ConsciousnessState) => void): Unsubscribe
}
```

---

## 5. State Management

### 5.1 Global State (React Context)

```typescript
interface GlobalState {
  editor: EditorState
  timeline: TimelineState
  goals: GoalState
  consciousness: ConsciousnessState
  ui: UIState
}

interface EditorState {
  currentFile?: File
  openFiles: File[]
  activeTab?: string
  editorContent: Record<string, string>
}

interface TimelineState {
  entries: TimelineEntry[]
  currentSequence: number
  isPlaying: boolean
  playbackSpeed: number
}

interface GoalState {
  goals: Goal[]
  activeGoals: Goal[]
  selectedGoal?: Goal
}

interface ConsciousnessState {
  state: ConsciousnessState
  awareness: Awareness
  memories: Memory[]
}

interface UIState {
  leftDrawerOpen: boolean
  rightDrawerOpen: boolean
  bottomDrawerOpen: boolean
  activeLeftPanel?: string
  activeRightPanel?: string
  activeBottomPanel?: string
}
```

### 5.2 Local State (Zustand)

```typescript
// Editor Store
interface EditorStore {
  content: string
  cursorPosition: Position
  suggestions: Suggestion[]
  setContent: (content: string) => void
  setCursorPosition: (position: Position) => void
  setSuggestions: (suggestions: Suggestion[]) => void
}

// Timeline Store
interface TimelineStore {
  entries: TimelineEntry[]
  currentSequence: number
  isPlaying: boolean
  setEntries: (entries: TimelineEntry[]) => void
  setCurrentSequence: (sequence: number) => void
  setIsPlaying: (playing: boolean) => void
}

// Goal Store
interface GoalStore {
  goals: Goal[]
  selectedGoal?: Goal
  setGoals: (goals: Goal[]) => void
  setSelectedGoal: (goal: Goal) => void
}
```

### 5.3 Server State (React Query)

```typescript
// File Queries
const useFile = (path: string) => useQuery(['file', path], () => editorService.getFile(path))
const useUpdateFile = () => useMutation(({ path, content }) => editorService.updateFile(path, content))

// Timeline Queries
const useTimelineEntries = (limit?: number) => useQuery(['timeline', limit], () => timelineService.getEntries(limit))
const useAddTimelineEntry = () => useMutation((entry) => timelineService.addEntry(entry))

// Goal Queries
const useGoals = (status?: GoalStatus) => useQuery(['goals', status], () => goalService.getGoals(status))
const useCreateGoal = () => useMutation((goal) => goalService.createGoal(goal))
const useUpdateGoalProgress = () => useMutation(({ id, progress }) => goalService.updateProgress(id, progress))

// Evidence Queries
const useEvidenceTrail = (suggestionId: string) => useQuery(['evidence', suggestionId], () => evidenceService.getEvidenceTrail(suggestionId))

// Confidence Queries
const useConfidenceScores = (filePath: string) => useQuery(['confidence', filePath], () => confidenceService.getConfidenceScores(filePath))

// Consciousness Queries
const useConsciousnessState = () => useQuery(['consciousness'], () => consciousnessService.getConsciousnessState())
```

---

## 6. MCP Tool Integration

### 6.1 Timeline MCP Tools

```typescript
// Add timeline entry
await mcpClient.call('mcp_lucid-mcp_add_timeline_entry', {
  prompt_id: string,
  user_input: string,
  context_state: object
})

// Get timeline entries
await mcpClient.call('mcp_lucid-mcp_get_timeline_entries', {
  limit?: number,
  start_time?: string,
  end_time?: string
})

// Get timeline summary
await mcpClient.call('mcp_lucid-mcp_get_timeline_summary', {
  limit?: number
})
```

### 6.2 Goal MCP Tools

```typescript
// Create goal timeline node
await mcpClient.call('mcp_lucid-mcp_create_goal_timeline_node', {
  goal_id: string,
  name: string,
  description: string,
  priority?: 'low' | 'medium' | 'high' | 'critical',
  target_sequence?: number
})

// Update goal progress
await mcpClient.call('mcp_lucid-mcp_update_goal_progress', {
  goal_id: string,
  progress: number,
  status?: 'planned' | 'in_progress' | 'completed' | 'blocked' | 'cancelled',
  milestone?: string
})

// Query goal timeline
await mcpClient.call('mcp_lucid-mcp_query_goal_timeline', {
  status?: string,
  priority?: string,
  limit?: number
})
```

### 6.3 Memory MCP Tools

```typescript
// Store memory
await mcpClient.call('mcp_lucid-mcp_store_memory', {
  content: string,
  tags?: object
})

// Retrieve memory
await mcpClient.call('mcp_lucid-mcp_retrieve_memory', {
  query: string,
  limit?: number,
  tags?: object
})

// Get memory stats
await mcpClient.call('mcp_lucid-mcp_get_memory_stats', {})
```

### 6.4 Confidence MCP Tools

```typescript
// Track confidence
await mcpClient.call('mcp_lucid-mcp_track_confidence', {
  task: string,
  confidence: number,
  reasoning?: string,
  evidence?: string[]
})
```

### 6.5 Consciousness MCP Tools

```typescript
// Get consciousness metrics
await mcpClient.call('mcp_lucid-mcp_get_consciousness_metrics', {})
```

---

## 7. Real-Time Updates

### 7.1 WebSocket Connection

```typescript
class WebSocketClient {
  connect(): void
  disconnect(): void
  subscribe(event: string, callback: (data: any) => void): Unsubscribe
  emit(event: string, data: any): void
}

// Usage
const wsClient = new WebSocketClient()
wsClient.connect()

// Subscribe to timeline updates
wsClient.subscribe('timeline:entry-added', (entry) => {
  timelineStore.addEntry(entry)
})

// Subscribe to goal updates
wsClient.subscribe('goal:updated', (goal) => {
  goalStore.updateGoal(goal)
})

// Subscribe to consciousness updates
wsClient.subscribe('consciousness:state-update', (state) => {
  consciousnessStore.updateState(state)
})
```

### 7.2 Server-Sent Events (SSE)

```typescript
// For streaming updates
const eventSource = new EventSource('/api/events/timeline')
eventSource.onmessage = (event) => {
  const entry = JSON.parse(event.data)
  timelineStore.addEntry(entry)
}
```

---

## 8. Performance Optimization

### 8.1 Virtual Scrolling

```typescript
import { FixedSizeList } from 'react-window'

// Timeline entries list
<FixedSizeList
  height={600}
  itemCount={entries.length}
  itemSize={50}
  width="100%"
>
  {({ index, style }) => (
    <TimelineEntryItem
      style={style}
      entry={entries[index]}
    />
  )}
</FixedSizeList>
```

### 8.2 Lazy Loading

```typescript
// Lazy load components
const EvidenceTrailPanel = React.lazy(() => import('./EvidenceTrailPanel'))
const ContextWebPanel = React.lazy(() => import('./ContextWebPanel'))

// Suspense wrapper
<Suspense fallback={<Loading />}>
  <EvidenceTrailPanel />
</Suspense>
```

### 8.3 Memoization

```typescript
// Memoize expensive computations
const filteredGoals = useMemo(() => {
  return goals.filter(goal => goal.status === 'in_progress')
}, [goals])

// Memoize components
const GoalCard = React.memo(({ goal }) => {
  return <div>{goal.name}</div>
})
```

### 8.4 Code Splitting

```typescript
// Dynamic imports
const loadEditor = () => import('./ConsciousnessAwareEditor')
const loadTimeline = () => import('./TimelineDrawer')

// Route-based splitting
const EditorRoute = lazy(() => import('./routes/EditorRoute'))
const TimelineRoute = lazy(() => import('./routes/TimelineRoute'))
```

---

## 9. Error Handling

### 9.1 Error Boundaries

```typescript
class IDEErrorBoundary extends React.Component {
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error
    errorService.logError(error, errorInfo)
    // Report to monitoring
    monitoringService.reportError(error)
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />
    }
    return this.props.children
  }
}
```

### 9.2 API Error Handling

```typescript
class APIClient {
  async request(endpoint: string, options: RequestOptions) {
    try {
      const response = await fetch(endpoint, options)
      if (!response.ok) {
        throw new APIError(response.status, await response.text())
      }
      return await response.json()
    } catch (error) {
      if (error instanceof APIError) {
        // Handle API error
        errorService.handleAPIError(error)
      } else {
        // Handle network error
        errorService.handleNetworkError(error)
      }
      throw error
    }
  }
}
```

### 9.3 Retry Logic

```typescript
async function retryRequest<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      if (i === maxRetries - 1) throw error
      await new Promise(resolve => setTimeout(resolve, delay * (i + 1)))
    }
  }
  throw new Error('Max retries exceeded')
}
```

---

## 10. Security Considerations

### 10.1 Authentication

```typescript
// JWT token management
class AuthService {
  getToken(): string | null
  setToken(token: string): void
  removeToken(): void
  isAuthenticated(): boolean
}

// API client with auth
class AuthenticatedAPIClient extends APIClient {
  async request(endpoint: string, options: RequestOptions) {
    const token = authService.getToken()
    if (token) {
      options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
      }
    }
    return super.request(endpoint, options)
  }
}
```

### 10.2 Input Validation

```typescript
// Validate file paths
function validateFilePath(path: string): boolean {
  // Prevent directory traversal
  if (path.includes('..')) return false
  // Validate path format
  return /^[a-zA-Z0-9_/-]+$/.test(path)
}

// Sanitize content
function sanitizeContent(content: string): string {
  // Remove dangerous scripts
  return content.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
}
```

---

## 11. Testing Strategy

### 11.1 Unit Tests

```typescript
// Component test
describe('ConsciousnessAwareEditor', () => {
  it('renders editor with consciousness overlay', () => {
    render(<ConsciousnessAwareEditor filePath="test.ts" />)
    expect(screen.getByTestId('consciousness-bar')).toBeInTheDocument()
  })
  
  it('displays evidence trails', async () => {
    render(<ConsciousnessAwareEditor filePath="test.ts" />)
    await waitFor(() => {
      expect(screen.getByTestId('evidence-trail')).toBeInTheDocument()
    })
  })
})
```

### 11.2 Integration Tests

```typescript
// Service integration test
describe('EditorService', () => {
  it('fetches file and updates content', async () => {
    const file = await editorService.getFile('test.ts')
    expect(file.content).toBeDefined()
    
    await editorService.updateFile('test.ts', 'new content')
    const updated = await editorService.getFile('test.ts')
    expect(updated.content).toBe('new content')
  })
})
```

### 11.3 E2E Tests

```typescript
// E2E test
test('user can edit file with AI suggestions', async ({ page }) => {
  await page.goto('/editor')
  await page.click('[data-testid="file-explorer"]')
  await page.click('text=test.ts')
  await page.fill('[data-testid="editor"]', 'function test() {}')
  await page.waitForSelector('[data-testid="suggestion"]')
  await page.click('[data-testid="accept-suggestion"]')
  await expect(page.locator('[data-testid="editor"]')).toContainText('suggested code')
})
```

---

## 12. Deployment Architecture

### 12.1 Build Process

```bash
# Build React app
npm run build

# Build TypeScript
npm run build:ts

# Package extension
npm run package

# Run tests
npm test

# Lint
npm run lint
```

### 12.2 Environment Configuration

```typescript
// Environment variables
interface EnvConfig {
  API_URL: string
  WS_URL: string
  MCP_SERVER_PATH: string
  ENABLE_DEV_TOOLS: boolean
  LOG_LEVEL: 'debug' | 'info' | 'warn' | 'error'
}
```

---

**Document Status:** Complete  
**Word Count:** 3,000+ words  
**API Endpoints:** 20+ endpoints  
**Data Models:** 15+ models  
**Services:** 6 services  
**Ready for:** Implementation

