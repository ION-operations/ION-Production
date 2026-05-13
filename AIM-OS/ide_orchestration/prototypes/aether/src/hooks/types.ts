// Types for all AIM-OS systems
export interface Memory {
  id: string
  content: string
  tags: Record<string, any>
  timestamp: string
  confidence?: number
}

export interface MemoryStats {
  total: number
  byTag: Record<string, number>
  recent: number
}

export interface CMCInterface {
  store: (content: string, tags?: Record<string, any>) => Promise<string>
  retrieve: (query: string, limit?: number) => Promise<Memory[]>
  getStats: () => Promise<MemoryStats>
  loading: boolean
  error: Error | null
}

export interface SearchResult {
  id: string
  content: string
  relevance: number
  metadata: Record<string, any>
}

export interface Atom {
  id: string
  content: string
  metadata: Record<string, any>
}

export interface Hierarchy {
  id: string
  children: Hierarchy[]
  level: number
}

export interface HHNIInterface {
  search: (query: string, limit?: number) => Promise<SearchResult[]>
  retrieve: (atomId: string) => Promise<Atom | null>
  getHierarchy: (atomId: string) => Promise<Hierarchy>
  loading: boolean
  error: Error | null
}

export interface Witness {
  id: string
  task: string
  confidence: number
  evidence: string[]
  timestamp: string
}

export interface ValidationResult {
  valid: boolean
  confidence: number
  evidence: string[]
  reasoning?: string
}

export interface VIFInterface {
  trackConfidence: (task: string, confidence: number, evidence?: string[]) => Promise<void>
  getWitnesses: (task: string) => Promise<Witness[]>
  validate: (statement: string) => Promise<ValidationResult>
  loading: boolean
  error: Error | null
}

export interface Evidence {
  id: string
  content: string
  source: string
  confidence: number
}

export interface Contradiction {
  id: string
  evidence1: string
  evidence2: string
  severity: 'low' | 'medium' | 'high'
}

export interface Synthesis {
  id: string
  topics: string[]
  summary: string
  insights: string[]
}

export interface SEGInterface {
  addEvidence: (evidence: Evidence) => Promise<string>
  detectContradictions: (query: string) => Promise<Contradiction[]>
  synthesize: (topics: string[]) => Promise<Synthesis>
  loading: boolean
  error: Error | null
}

export interface Plan {
  id: string
  goal: string
  tasks: Task[]
  status: 'planned' | 'in_progress' | 'completed' | 'failed'
}

export interface Task {
  id: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
}

export interface Execution {
  id: string
  planId: string
  status: 'running' | 'completed' | 'failed'
  progress: number
}

export interface Progress {
  planId: string
  completed: number
  total: number
  percentage: number
}

export interface APOEInterface {
  createPlan: (goal: string, context?: string) => Promise<Plan>
  executePlan: (planId: string) => Promise<Execution>
  getProgress: (planId: string) => Promise<Progress>
  loading: boolean
  error: Error | null
}

export interface TimelineEntry {
  id: string
  promptId: string
  userInput: string
  timestamp: string
  contextState?: Record<string, any>
}

export interface TimelineFilters {
  startTime?: string
  endTime?: string
  promptId?: string
  limit?: number
}

export interface TCSInterface {
  addEntry: (promptId: string, userInput: string, contextState?: Record<string, any>) => Promise<string>
  getSummary: (limit?: number) => Promise<TimelineEntry[]>
  getEntries: (filters?: TimelineFilters) => Promise<TimelineEntry[]>
  loading: boolean
  error: Error | null
}

export interface ConsciousnessMetrics {
  health: number
  drift: number
  selfAwareness: number
  memoryQuality: number
}

export interface DriftContext {
  contextSizeTokens?: number
  errorRate?: number
  workingMemoryItems?: number
}

export interface DriftResult {
  detected: boolean
  severity: 'low' | 'medium' | 'high'
  details: string
}

export type AuditType = 'hourly_check' | 'task_completion' | 'failure_analysis' | 'principle_review' | 'protocol_validation' | 'cognitive_load_assessment'

export interface AuditResult {
  type: AuditType
  passed: boolean
  issues: string[]
  recommendations: string[]
}

export interface CASInterface {
  getMetrics: () => Promise<ConsciousnessMetrics>
  detectDrift: (context?: DriftContext) => Promise<DriftResult>
  runAudit: (type?: AuditType) => Promise<AuditResult>
  loading: boolean
  error: Error | null
}

export interface InvariantResult {
  violated: boolean
  invariant: string
  details: string
}

export interface SDFCVFInterface {
  validate: (action: Record<string, any>, context?: Record<string, any>) => Promise<ValidationResult>
  checkInvariant: (action: Record<string, any>, context?: Record<string, any>) => Promise<InvariantResult>
  loading: boolean
  error: Error | null
}

export interface AIMOSHook {
  cmc: CMCInterface
  hhni: HHNIInterface
  vif: VIFInterface
  seg: SEGInterface
  apoe: APOEInterface
  tcs: TCSInterface
  cas: CASInterface
  sdfcvf: SDFCVFInterface
  isConnected: boolean
  connectionStatus: 'connected' | 'disconnected' | 'connecting' | 'error'
  error: Error | null
}

