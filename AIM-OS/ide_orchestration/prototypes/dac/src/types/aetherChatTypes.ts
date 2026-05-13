/**
 * Aether Chat - Complete Type System
 * 
 * This file contains all types for the Aether Chat pipeline (S0-S8)
 * Consolidates types from:
 * - ChatGPT's S0-S8 pipeline structure
 * - Perplexity's detailed technical architecture
 * - Gemini Pro's AIM-OS enhancements
 * - Operational fixes (gaps 1-5)
 * 
 * @module aetherChatTypes
 */

// ============================================================================
// S0: INGEST & SESSION ROUTING
// ============================================================================

/**
 * Raw user input before processing
 */
export interface RawUserTurn {
  sessionId: string
  userId?: string
  source: 'cursor' | 'web' | 'standalone'
  message: string
  timestamp: string
  editorContext?: EditorContext
  conversationHistory?: ChatMessage[] // For fallback context
}

/**
 * Editor context from IDE
 */
export interface EditorContext {
  openFiles: Array<{
    path: string
    content?: string
    language?: string
  }>
  cursorPosition?: {
    file: string
    line: number
    column: number
  }
  selectedText?: string
  workspaceRoot?: string
}

/**
 * Chat message (compatible with existing chatTypes.ts)
 */
export interface ChatMessage {
  id: string
  timestamp: Date
  role: 'user' | 'assistant' | 'system'
  content: string
  agent?: string
  agent_id?: string
  confidence?: number
}

// ============================================================================
// S1: PRE-PROCESSING PIPELINE
// ============================================================================

/**
 * Chat intent classification
 */
export type ChatIntent =
  | 'ask_explain'
  | 'code_edit'
  | 'debug_error'
  | 'design_arch'
  | 'meta_chat'
  | 'planning'
  | 'other'

/**
 * Chat mode based on complexity and requirements
 */
export type ChatMode = 'fast' | 'deep' | 'research' | 'surgical'

/**
 * Ambiguity detection result (Gap 1 + Gemini Pro Enhancement)
 */
export interface AmbiguityState {
  isAmbiguous: boolean
  ambiguityScore: number // 0.0 to 1.0 (Derived from entropy of interpretation confidence)
  interpretations: Array<{
    intent: string
    confidence: ConfidenceScore // VIF Score
    supportingEvidence: string[] // SEG Anchor IDs / CMC Atom IDs
  }>
  // If alpha > 0.5, trigger "Forked Path" UI instead of answering
  forkedPathUI?: {
    question: string
    options: string[]
  }
}

/**
 * Dynamic κ-Gating (Risk-Adjusted Confidence) - Gemini Pro Enhancement
 */
export interface DynamicKappaGate {
  baseThreshold: 0.70 | 0.85 | 0.90 | 0.95 // Tier C, B, A, S
  riskMultiplier: number // Derived from CAS capability ledger
  
  // The calculated requirement for this specific turn
  requiredConfidence(): number
  
  // Determines if the AI must abstain or can speculate
  determination: 'PROCEED' | 'SPECULATE_WITH_WARNING' | 'ABSTAIN_AND_CLARIFY'
}

/**
 * Confidence score with band classification
 */
export interface ConfidenceScore {
  value: number // 0–1
  band: 'A' | 'B' | 'C' | 'S' // S=0.95+, A=0.90+, B=0.85+, C=0.70+
}

/**
 * Enriched context from HHNI + CMC
 */
export interface EnrichedContext {
  hhniResults: HHNIResult[]
  cmcAtoms: CMCAtom[]
  sourceCount: number
  sourceQuality: number[]
  recentnessScore: number
  atomIds: string[]
  retrievedAtoms: CMCAtom[]
  hhniQueries: string[]
  completenessScore: number
}

/**
 * HHNI search result
 */
export interface HHNIResult {
  atomId: string
  relevanceScore: number
  content: string
  domain: string
  mentionCount?: number
  title?: string
}

/**
 * CMC atom reference
 */
export interface CMCAtom {
  id: string
  content: string
  modality: string
  tags: string[]
  metadata: {
    timestamp: Date
    location?: string
    relevance?: number
    [key: string]: any
  }
}

/**
 * Safety check result
 */
export interface SafetyResult {
  passed: boolean
  reason?: string
  suggestions?: string[]
  cognitiveState?: CognitiveState
}

/**
 * Cognitive state from CAS
 */
export interface CognitiveState {
  sessionLength: number // milliseconds
  messageCount: number
  recentErrors: number
  driftIndicators?: string[]
}

/**
 * Response plan from APOE
 */
export interface ResponsePlan {
  planId: string
  goal: string
  steps: PlanStep[]
  budget: {
    tokens: number
    cost: number
  }
  primaryRole: RoleType
  vifConfidence: number
}

/**
 * Plan step from APOE
 */
export interface PlanStep {
  stepId: string
  role: RoleType
  action: string
  dependencies: string[]
  domain?: string
}

/**
 * Role type for APOE orchestration
 */
export type RoleType = 'planner' | 'retriever' | 'builder' | 'verifier' | 'critic' | 'reasoner' | 'operator' | 'witness'

/**
 * Tool selection result
 */
export interface ToolSelection {
  tools: Array<{
    name: string
    provider: string
    cost: number
  }>
  totalCost: number
}

/**
 * Pre-processing result
 */
export interface PreProcessingResult {
  intent: ChatIntent
  mode: ChatMode
  enrichedContext: EnrichedContext
  ambiguity: AmbiguityState
  gating: DynamicKappaGate
  safety: SafetyResult
  initialConfidence: ConfidenceScore
  responsePlan: ResponsePlan
  tools: ToolSelection
  κ_score: number
  evidence_atoms: string[]
  retrieval_trace: RetrievalTrace
  userPreference?: UserPreference // Gap 4: Profile Bootstrapping
  degradedMode?: DegradedMode // Gap 2: Failure Modes
  specialistActivation?: SpecialistActivation // Phase 2: Specialist System Integration
}

/**
 * Specialist activation result (Phase 2: Specialist System Integration)
 */
export interface SpecialistActivation {
  work: {
    description: string
    domain: string[]
    systems: string[]
    data: string[]
    patterns: string[]
    complexity: number
  }
  mechanisms: Array<{
    type: 'ownership' | 'activation' | 'consultation'
    level: number
    message: string
    specialist_id: string
    specialist_name: string
    relevance: number
    action: string
  }>
  primary?: {
    type: 'ownership' | 'activation' | 'consultation'
    level: number
    message: string
    specialist_id: string
    specialist_name: string
    relevance: number
  }
  summary: string
}

/**
 * Retrieval trace for provenance
 */
export interface RetrievalTrace {
  hhni_queries: string[]
  cmc_atoms: string[]
  sources_count: number
}

/**
 * User preference (Gap 4: Profile Bootstrapping)
 */
export interface UserPreference {
  mode: 'Speed' | 'Mastery'
  confidence: number // 0.0 to 1.0 (how confident we are in this inference)
  source: 'explicit' | 'implicit' | 'default'
}

/**
 * Degraded mode flags (Gap 2: Failure Modes)
 */
export interface DegradedMode {
  vif: boolean // VIF system unavailable
  hhni: boolean // HHNI system unavailable
  cas: boolean // CAS system unavailable
  seg: boolean // SEG system unavailable
  apoe: boolean // APOE system unavailable
  cmc: boolean // CMC system unavailable
}

// ============================================================================
// S2: CONTEXT WEB & EVIDENCE CONSTRUCTION
// ============================================================================

/**
 * Context node in the Context Web graph
 */
export interface ContextNode {
  id: string
  type: 'msg' | 'file' | 'doc' | 'mige' | 'event'
  label: string
  importance: number
  recency: number
  size?: number // For visualization
  color?: string // For visualization
  glow?: number // For visualization
  context?: string // Snippet
  timestamp?: Date
  relevance?: number
}

/**
 * Context edge in the Context Web graph
 */
export interface ContextEdge {
  from: string
  to: string
  relation: 'refers_to' | 'explains' | 'extends' | 'contradicts' | 'depends_on'
  strength: number
  thickness?: number // For visualization
  color?: string // For visualization
  label?: string
}

/**
 * Context Web graph structure
 */
export interface ContextWeb {
  nodes: ContextNode[]
  edges: ContextEdge[]
  layout?: 'force-directed' | 'hierarchical'
}

/**
 * Evidence item from CMC + SEG
 */
export interface EvidenceItem {
  id: string
  kind: 'file_snippet' | 'doc_snippet' | 'prior_msg' | 'test_output' | 'other'
  sourceId: string // file path, message id, etc.
  excerpt: string
  trust: number // 0–1
  location?: string
  timestamp?: Date
}

/**
 * Evidence pack containing all evidence items
 */
export interface EvidencePack {
  items: EvidenceItem[]
  totalTrust: number
  completeness?: {
    isComplete: boolean
    completenessScore: number
    missingTypes: EvidenceItem['kind'][]
    recommendations: string[]
  }
}

/**
 * Evidence chain linking claims to sources
 */
export interface EvidenceChain {
  claims: Array<{
    text: string
    evidenceIds: string[]
  }>
  links: Array<{
    from: string
    to: string
    relation: string
  }>
}

// ============================================================================
// S3: THINKING MODE (REASONING CORE)
// ============================================================================

/**
 * Editable thinking block (Gemini Pro Enhancement - JIT Intervention)
 */
export interface EditableThinkingBlock {
  planId: string
  goal: string
  steps: Array<{
    stepId: string
    role: RoleType
    action: string
    status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'PAUSED' | 'GENERATING'
    isEditable: boolean
    onDelete?: () => void
    onModify?: (newPrompt: string) => void
    partialText?: string // For streaming (Gap 5)
  }>
  planningConfidence: number // VIF Witness for the plan generation itself
}

/**
 * Reasoning trace from LUCID Empire
 */
export interface ReasoningTrace {
  id: string
  rawText: string
  domains: string[]
  assumptions: string[]
  confidenceSelfReport: number
  summary?: string
  depth?: number // For infinite lucidity
}

/**
 * Draft response before gating
 */
export interface DraftResponse {
  userFacingText: string
  actions: PlannedAction[]
  rationale: string
  citedEvidenceIds: string[]
  selfEstimatedConfidence: number
}

/**
 * Planned action from response
 */
export interface PlannedAction {
  type: 'code_edit' | 'file_create' | 'file_delete' | 'test_run' | 'other'
  description: string
  target?: string
}

/**
 * Alternative response considered
 */
export interface Alternative {
  text: string
  whyNotChosen: string
  tradeOffs: string[]
}

/**
 * Thinking result from S3
 */
export interface ThinkingResult {
  draft: DraftResponse
  reasoningTrace: ReasoningTrace
  alternatives?: Alternative[]
  planExecution?: PlanExecutionResult
  lucidLayers?: {
    layer1: any // Thought Articulation
    layer2: any // Reasoning Reflection
    layer3: any // Pattern Identification
    layer4: any // Temporal Lucidity
    layer5: any // Infinite Lucidity
  }
}

/**
 * Plan execution result
 */
export interface PlanExecutionResult {
  planId: string
  stepsCompleted: number
  stepsTotal: number
  costUsed: number
  tokensUsed: number
  errors?: string[]
}

// ============================================================================
// S4: VIF / CAS GATING (κ-GATING, SAFETY)
// ============================================================================

/**
 * Gating result from S4
 */
export interface GatingResult {
  approved: boolean
  gatedConfidence: ConfidenceScore
  gateReason?: string
  requiredClarification?: string
  qualityIssues?: QualityIssue[]
  safetyIssues?: SafetyIssue[]
  contradictions?: Contradiction[]
}

/**
 * Quality issue detected
 */
export interface QualityIssue {
  type: 'factual' | 'logical' | 'formatting' | 'other'
  description: string
  severity: 'low' | 'medium' | 'high'
}

/**
 * Safety issue detected
 */
export interface SafetyIssue {
  type: 'manipulation' | 'bias' | 'harmful' | 'other'
  description: string
  severity: 'low' | 'medium' | 'high'
}

/**
 * Contradiction detected
 */
export interface Contradiction {
  claim1: string
  claim2: string
  evidence1: string[]
  evidence2: string[]
  severity: 'low' | 'medium' | 'high'
}

// ============================================================================
// S5: POST-PROCESSING PIPELINE
// ============================================================================

/**
 * UI formatting result
 */
export interface UiFormatting {
  markdown: string // Final markdown
  structure?: 'code' | 'list' | 'table' | 'paragraph' | 'narrative' | 'mixed' | 'decision_tree' // Phase 4 Week 15: Added 'table' and 'mixed'
  syntaxHighlighted?: boolean // Phase 4 Week 15: Code block syntax highlighting
}

/**
 * Suggested action for user
 */
export interface SuggestedAction {
  type: 'code_edit' | 'test' | 'documentation' | 'refactor' | 'other'
  description: string
  target?: string
  priority: 'low' | 'medium' | 'high'
}

/**
 * Post-processing result
 */
export interface PostProcessingResult {
  finalText: string
  uiFormatting: UiFormatting
  citations: EvidenceItem[]
  confidence: ConfidenceScore
  suggestedActions?: SuggestedAction[]
  suggestedFollowUps?: string[]
  correctionsMade?: Correction[]
  solutionReveal?: SocraticReveal // Gap 4: Socratic Gate
  // Phase 4 Week 15: Refinement metadata
  refinementMetadata?: {
    toneConsistent: boolean
    technicalAccuracy: 'high' | 'medium' | 'low'
    improvements: string[]
    structureDetected: 'code' | 'list' | 'table' | 'paragraph' | 'narrative' | 'mixed'
    codeBlocksCount: number
    listsCount: number
    tablesCount: number
    paragraphsCount: number
  }
  // Phase 4 Week 16: Citation and confidence metadata
  citationMetadata?: {
    citationMarkers: CitationMarker[]
    provenance: Provenance
    cmcLinks: Record<string, { atomId: string; metadata: any }>
  }
  sectionConfidences?: Array<{
    sectionId: string
    text: string
    startIndex: number
    endIndex: number
    confidence: ConfidenceScore
    evidenceCount: number
    evidenceStrength: 'high' | 'medium' | 'low'
    sources: Array<{
      evidenceId: string
      trust: number
      recency: number
    }>
  }>
}

/**
 * Correction made during post-processing
 */
export interface Correction {
  type: 'grammar' | 'factual' | 'logical' | 'formatting'
  original: string
  corrected: string
  reason: string
}

/**
 * Socratic reveal for Mastery mode (Gap 4)
 */
export interface SocraticReveal {
  hint: string
  solution: string // Code blocks wrapped in <details>
}

// ============================================================================
// S6: UX/UI POLISH & PANELS
// ============================================================================

/**
 * UI hints for panel display
 */
export interface UiHints {
  showContextWeb: boolean
  showEvidencePanel: boolean
  showThinkingMode: boolean
  showMigeTimeline?: boolean
}

/**
 * MIGE update for idea evolution
 */
export interface MigeUpdate {
  ideaId: string
  stage: 'SEED' | 'VISION_TENSOR' | 'TRUNK_INDEX' | 'DEPLOYED'
  context: {
    messageId: string
    confidence: number
    evidenceCount: number
  }
}

/**
 * Final chat turn payload to UI
 */
export interface FinalChatTurn {
  messageId: string
  sessionId: string
  userText: string
  assistantText: string
  confidence: ConfidenceScore
  contextWeb: ContextWeb
  evidence: EvidenceItem[]
  reasoningSummary?: string
  migeUpdates?: MigeUpdate[]
  uiHints: UiHints
  timestamp: string
  panelData?: {
    contextWeb?: ContextWebPanelData
    evidence?: EvidencePanelData
    migeTimeline?: MigeTimelineData
  }
  // Streaming plan data (Gap 5)
  plan?: ResponsePlan
  streamingChunks?: PlanStreamChunk[]
  // Ambiguity resolution (Phase 1 Week 3)
  ambiguity?: AmbiguityState
  // Dynamic κ-Gating (Phase 1 Week 4)
  gatingDetermination?: 'PROCEED' | 'SPECULATE_WITH_WARNING' | 'ABSTAIN_AND_CLARIFY'
  riskAssessment?: {
    riskScore: number
    riskLevel: 'low' | 'medium' | 'high' | 'critical'
    category: 'casual' | 'informational' | 'modification' | 'destructive' | 'critical'
  }
}

/**
 * Context Web panel data
 */
export interface ContextWebPanelData {
  graph: ContextWeb
  interactions: {
    semanticSearch: (query: string) => Promise<ContextNode[]>
    timelineView: (topicId: string, dateRange: [Date, Date]) => Promise<ContextEvolution>
    causationChain: (nodeId: string) => Promise<ContextNode[]>
    findCommonality: (nodeIds: string[]) => Promise<CommonThemes>
  }
}

/**
 * Context evolution over time
 */
export interface ContextEvolution {
  topicId: string
  snapshots: Array<{
    timestamp: Date
    state: string
    confidence: number
  }>
}

/**
 * Common themes across contexts
 */
export interface CommonThemes {
  themes: string[]
  sharedConcepts: string[]
  connections: ContextEdge[]
}

/**
 * Evidence panel data
 */
export interface EvidencePanelData {
  items: EvidenceItem[]
  chain: EvidenceChain
  provenance: Array<{
    atom: CMCAtom
    witness?: VIFWitness
  }>
}

/**
 * MIGE timeline data (Gap 1: Time-Lapse)
 */
export interface MigeTimelineData {
  ideaAtomId: string
  snapshots: Array<{
    timestamp: Date
    stage: 'SEED' | 'VISION_TENSOR' | 'TRUNK_INDEX' | 'DEPLOYED'
    contextState: {
      openFiles: string[]
      activeConstraints: string[]
      vifConfidence: number
    }
    segAnchors: string[]
  }>
  restoreState?: (snapshotIndex: number) => Promise<void>
}

/**
 * VIF witness for provenance
 */
export interface VIFWitness {
  id: string
  hash: string
  toolsUsed: string[]
  timestamp: Date
}

// ============================================================================
// S7: MEMORY, TIMELINE, & EVOLUTION
// ============================================================================

/**
 * Session state for persistence
 */
export interface SessionState {
  sessionId: string
  userId: string
  startTime: Date
  messageCount: number
  conversationHistory: ChatMessage[]
  ideaId?: string
  recentAtoms: string[]
  recentReasoningTraces: string[]
}

// ============================================================================
// GAP 1: COLD START & STATE HYDRATION
// ============================================================================

/**
 * Hydrated session with cached graphs (Gap 1)
 */
export interface HydratedSession {
  // Standard chat history
  history: FinalChatTurn[]
  
  // Cache the graph so we don't re-compute it on load
  contextGraphSnapshot: ContextWeb
  
  // Cache evidence so we don't re-fetch atoms
  evidenceCache: Record<string, EvidenceItem>
  
  // Metadata for cache invalidation
  cacheMetadata: {
    lastUpdated: Date
    version: string // Cache version for invalidation
    atomIds: string[] // CMC atom IDs used in cache
  }
}

// ============================================================================
// GAP 2: CIRCUIT BREAKER & FALLBACK
// ============================================================================

/**
 * Circuit breaker configuration
 */
export interface CircuitBreakerConfig {
  timeout: number // milliseconds
  maxFailures: number // Before opening circuit
  resetTimeout: number // Time before retry
}

/**
 * Circuit breaker state
 */
export type CircuitBreakerState = 'CLOSED' | 'OPEN' | 'HALF_OPEN'

// ============================================================================
// GAP 3: MODEL REGISTRY & CONFIGURATION
// ============================================================================

/**
 * Model configuration for provider
 */
export interface ModelConfig {
  provider: string
  model: string
  endpoint: string
  apiKey: string // From environment
  costPer1kTokens: {
    input: number
    output: number
  }
  capabilities: {
    maxContextWindow: number
    supportsFunctionCalling: boolean
    supportsStreaming: boolean
    supportsVision: boolean
    supportsAudio: boolean
  }
  performance: {
    avgLatency: number // milliseconds
    maxLatency: number // milliseconds
    throughput: number // requests per second
  }
  limits: {
    rateLimit: number // requests per minute
    dailyLimit?: number // requests per day
  }
}

/**
 * Model tier for selection
 */
export interface ModelTier {
  name: string
  models: ModelConfig[]
  selectionCriteria: {
    complexity: ('simple' | 'medium' | 'complex' | 'very_complex')[]
    intent: ChatIntent[]
    maxCost?: number
    maxLatency?: number
  }
}

/**
 * Environment configuration
 */
export interface EnvironmentConfig {
  nodeEnv: 'development' | 'production' | 'test'
  aimosSystems: {
    cmc: { enabled: boolean; endpoint?: string }
    hhni: { enabled: boolean; endpoint?: string }
    vif: { enabled: boolean; endpoint?: string }
    apoe: { enabled: boolean; endpoint?: string }
    seg: { enabled: boolean; endpoint?: string }
    cas: { enabled: boolean; endpoint?: string }
    tcs: { enabled: boolean; endpoint?: string }
    mige: { enabled: boolean; endpoint?: string }
  }
  defaultModel: {
    provider: string
    model: string
  }
  costTracking: {
    enabled: boolean
    budgetLimit?: number
    alertThreshold?: number
  }
}

// ============================================================================
// GAP 5: STREAMING THINKING MODE
// ============================================================================

/**
 * Streaming plan step (Gap 5)
 */
export interface StreamingPlanStep {
  stepId: string
  role: RoleType
  action: string
  status: 'GENERATING' | 'COMPLETE'
  partialText?: string // For streaming
}

/**
 * Streaming chunk from APOE
 */
export interface PlanStreamChunk {
  type: 'step_start' | 'step_update' | 'step_complete'
  stepId: string
  role?: RoleType
  partialAction?: string
}

// ============================================================================
// ORCHESTRATOR TYPES
// ============================================================================

/**
 * Complete orchestrator input
 */
export type OrchestratorInput = RawUserTurn

/**
 * Complete orchestrator output
 */
export type OrchestratorOutput = FinalChatTurn

/**
 * Stage result type mapping
 */
export type StageResult =
  | PreProcessingResult
  | { contextWeb: ContextWeb; evidencePack: EvidencePack }
  | ThinkingResult
  | GatingResult
  | PostProcessingResult
  | FinalChatTurn
  | void // S7 and S8 return void (side effects only)

