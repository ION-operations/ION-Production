/**
 * Aether Chat Orchestrator - Main Pipeline Execution Engine
 * 
 * Implements the complete S0-S8 pipeline for Aether Chat
 * Integrates all AIM-OS systems with graceful degradation
 * 
 * Gap 2: Circuit Breakers & Fallback Strategy
 * Gap 1: Session Hydration
 */

import type {
  RawUserTurn,
  PreProcessingResult,
  ContextWeb,
  EvidencePack,
  ThinkingResult,
  GatingResult,
  PostProcessingResult,
  FinalChatTurn,
  HydratedSession,
  CircuitBreakerConfig,
  CircuitBreakerState,
  DegradedMode,
  ConfidenceScore,
  EnrichedContext,
  AmbiguityState,
  DynamicKappaGate,
  SafetyResult,
  ResponsePlan,
  ToolSelection,
  UserPreference,
  ChatIntent,
  ChatMode,
  HHNIResult,
  CMCAtom,
  EvidenceItem,
  EvidenceChain,
  ReasoningTrace,
  DraftResponse,
  QualityIssue,
  SafetyIssue,
  Contradiction,
  MigeUpdate
} from '../types/aetherChatTypes'

// Import existing AIM-OS services
import { CMCService } from './CMCService'
import { HHNIService } from './HHNIService'
import { VIFService } from './VIFService'
import { APOEService } from './APOEService'
import { SEGService } from './SEGService'
import { CASService } from './CASService'
import { TCSService } from './TCSService'
import { loadEnvironmentConfig, getActiveModel } from '../config/modelRegistry'
import { analyzeIntentLLM, generateContextQueries } from './aetherChat/intentAnalysis'
import { detectAmbiguityLLM } from './aetherChat/ambiguityDetection'
import { createEnhancedResponsePlan } from './aetherChat/responsePlanning'
import { createPlanStreaming } from './aetherChat/streamingPlanGeneration'
import { runLucidEmpireReasoning } from './aetherChat/lucidEmpire'
import { MCPService } from './MCPService'

// ============================================================================
// CIRCUIT BREAKER IMPLEMENTATION (Gap 2)
// ============================================================================

/**
 * Circuit breaker for AIM-OS system calls
 */
class CircuitBreaker {
  private failures: number = 0
  private lastFailureTime: Date | null = null
  private state: CircuitBreakerState = 'CLOSED'
  
  constructor(private config: CircuitBreakerConfig) {}
  
  async execute<T>(
    operation: () => Promise<T>,
    fallback: () => T
  ): Promise<T> {
    // Check if circuit is open
    if (this.state === 'OPEN') {
      if (this.lastFailureTime && 
          Date.now() - this.lastFailureTime.getTime() > this.config.resetTimeout) {
        this.state = 'HALF_OPEN'
      } else {
        return fallback() // Fast fail
      }
    }
    
    try {
      // Execute with timeout
      const result = await Promise.race([
        operation(),
        new Promise<never>((_, reject) =>
          setTimeout(() => reject(new Error('Timeout')), this.config.timeout)
        )
      ])
      
      // Success - reset failures
      this.failures = 0
      this.state = 'CLOSED'
      return result
    } catch (error) {
      this.failures++
      this.lastFailureTime = new Date()
      
      if (this.failures >= this.config.maxFailures) {
        this.state = 'OPEN'
      }
      
      // Return fallback
      return fallback()
    }
  }
  
  getState(): CircuitBreakerState {
    return this.state
  }
  
  reset(): void {
    this.failures = 0
    this.lastFailureTime = null
    this.state = 'CLOSED'
  }
}

// Global circuit breakers for each AIM-OS system
const circuitBreakers = {
  vif: new CircuitBreaker({ timeout: 2000, maxFailures: 3, resetTimeout: 30000 }),
  hhni: new CircuitBreaker({ timeout: 3000, maxFailures: 3, resetTimeout: 30000 }),
  cas: new CircuitBreaker({ timeout: 2000, maxFailures: 3, resetTimeout: 30000 }),
  seg: new CircuitBreaker({ timeout: 2000, maxFailures: 3, resetTimeout: 30000 }),
  apoe: new CircuitBreaker({ timeout: 5000, maxFailures: 3, resetTimeout: 30000 }),
  cmc: new CircuitBreaker({ timeout: 2000, maxFailures: 3, resetTimeout: 30000 }),
  tcs: new CircuitBreaker({ timeout: 2000, maxFailures: 3, resetTimeout: 30000 }),
  mige: new CircuitBreaker({ timeout: 2000, maxFailures: 3, resetTimeout: 30000 })
}

/**
 * Run operation with fallback (Gap 2)
 */
export async function runWithFallback<T>(
  system: keyof typeof circuitBreakers,
  operation: () => Promise<T>,
  fallback: () => T
): Promise<T> {
  return circuitBreakers[system].execute(operation, fallback)
}

// ============================================================================
// MAIN ORCHESTRATOR FUNCTION
// ============================================================================

/**
 * Run complete Aether Chat turn (S0-S8)
 * 
 * This is the main entry point for processing a user message
 * through the complete pipeline with all AIM-OS integrations
 */
export async function runAetherChatTurn(
  input: RawUserTurn
): Promise<FinalChatTurn> {
  // S0: Ingest & Session Routing
  const sessionContext = await runIngestAndSessionRouting(input)
  
  // S1: Pre-Processing
  const pre = await runPreProcessing(input, sessionContext)
  
  // S2: Context Web + Evidence
  const { contextWeb, evidencePack } = await buildContextAndEvidence(input, pre)
  
  // S3: Thinking Mode / Reasoning
  const thinking = await runThinkingMode(input, pre, contextWeb, evidencePack)
  
  // S4: Gating (VIF / CAS / SCOR)
  const gating = await runGating(input, pre, contextWeb, evidencePack, thinking)
  
  // If gating fails, answer is a clarification question
  const thinkingForOutput =
    gating.approved ? thinking : await buildClarificationDraft(input, pre, gating, contextWeb, evidencePack)
  
  // S5: Post-Processing
  const post = await runPostProcessing(input, pre, contextWeb, evidencePack, thinkingForOutput, gating)
  
  // S6: Build FinalChatTurn (UI payload)
  const finalTurn = buildFinalChatTurn(input, pre, contextWeb, evidencePack, thinkingForOutput, gating, post)
  
  // S7: Persist to AIM-OS (CMC, HHNI, SEG, TCS, MIGE)
  await persistTurnToAimos(input, pre, contextWeb, evidencePack, thinkingForOutput, gating, post, finalTurn)
  
  // S8: Optional autonomous follow-ups (APOE, cursor loop)
  await maybeScheduleFollowUps(input, pre, finalTurn)
  
  return finalTurn
}

// ============================================================================
// SERVICE INSTANCES
// ============================================================================

const cmcService = new CMCService()
const hhniService = new HHNIService()
const vifService = new VIFService()
const apoeService = new APOEService()
const segService = new SEGService()
const casService = new CASService()
const tcsService = new TCSService()
const mcpService = new MCPService()

// Environment configuration
const envConfig = loadEnvironmentConfig()

// ============================================================================
// S0: INGEST & SESSION ROUTING
// ============================================================================

interface SessionContext {
  sessionId: string
  userId?: string
  startTime: Date
  messageCount: number
  conversationHistory: Array<{
    id: string
    timestamp: Date
    role: 'user' | 'assistant' | 'system'
    content: string
  }>
  recentAtoms: string[]
  recentReasoningTraces: string[]
  ideaId?: string
}

/**
 * S0: Ingest & Session Routing
 */
async function runIngestAndSessionRouting(
  input: RawUserTurn
): Promise<SessionContext> {
  // Check if session exists and load state
  let sessionContext: SessionContext
  
  try {
    // Try to load existing session (Gap 1: Session Hydration)
    const hydratedSession = await loadSessionState(input.sessionId)
    
    sessionContext = {
      sessionId: input.sessionId,
      userId: input.userId,
      startTime: new Date(hydratedSession.cacheMetadata.lastUpdated),
      messageCount: hydratedSession.history.length,
      conversationHistory: hydratedSession.history.map(turn => ({
        id: turn.messageId,
        timestamp: new Date(turn.timestamp),
        role: 'user',
        content: turn.userText
      })),
      recentAtoms: hydratedSession.cacheMetadata.atomIds,
      recentReasoningTraces: []
    }
  } catch (error) {
    // New session or hydration failed - create fresh context
    sessionContext = {
      sessionId: input.sessionId,
      userId: input.userId,
      startTime: new Date(),
      messageCount: 0,
      conversationHistory: input.conversationHistory || [],
      recentAtoms: [],
      recentReasoningTraces: []
    }
  }
  
  // Add timeline entry for this turn
  if (envConfig.aimosSystems.tcs.enabled) {
    await runWithFallback(
      'tcs',
      async () => {
        await tcsService.addEntry(
          'chat_turn',
          input.message,
          {
            sessionId: input.sessionId,
            userId: input.userId,
            source: input.source
          }
        )
      },
      () => {
        console.warn('TCS unavailable - skipping timeline entry')
      }
    )
  }
  
  return sessionContext
}

// ============================================================================
// S1: PRE-PROCESSING PIPELINE
// ============================================================================

/**
 * S1: Pre-Processing Pipeline
 */
async function runPreProcessing(
  input: RawUserTurn,
  sessionContext: SessionContext
): Promise<PreProcessingResult> {
  const degradedMode: DegradedMode = {
    vif: false,
    hhni: false,
    cas: false,
    seg: false,
    apoe: false,
    cmc: false
  }
  
  // 1. Intent Analysis (LLM-based with fallback to pattern matching)
  const intentAnalysis = await analyzeIntentLLM(
    input.message,
    sessionContext.conversationHistory.map(m => ({
      role: m.role,
      content: m.content
    }))
  )
  const intent = intentAnalysis.intent
  const mode = intentAnalysis.mode
  
  // 1.5. Specialist Activation (Phase 2: Specialist System Integration)
  let specialistActivation: PreProcessingResult['specialistActivation'] | undefined
  try {
    // Detect work from chat input
    const detectWorkResult = await mcpService.executeTool('mcp_lucid-mcp_detect_work', {
      message: input.message,
      intent_analysis: {
        intent: intent,
        mode: mode
        // domains, systems, complexity will be extracted by work detector
      }
    })
    
    if (detectWorkResult.success && detectWorkResult.result?.work) {
      const work = detectWorkResult.result.work
      
      // Activate specialists
      const activateResult = await mcpService.executeTool('mcp_lucid-mcp_activate_specialists', {
        work: work
      })
      
      if (activateResult.success && activateResult.result?.activation_result) {
        // Get activation mechanisms
        const mechanismsResult = await mcpService.executeTool('mcp_lucid-mcp_get_specialist_activation', {
          work: work,
          activation_result: activateResult.result.activation_result
        })
        
        if (mechanismsResult.success && mechanismsResult.result) {
          specialistActivation = {
            work: work,
            mechanisms: mechanismsResult.result.mechanisms || [],
            primary: mechanismsResult.result.primary,
            summary: mechanismsResult.result.summary || 'No specialist activation'
          }
          
          // Log specialist activation
          console.log(`[S1] Specialist activation: ${specialistActivation.summary}`)
        }
      }
    }
  } catch (error) {
    // Fail-soft: Specialist activation is optional
    console.warn('[S1] Specialist activation failed:', error)
    specialistActivation = undefined
  }
  
  // 2. Generate context queries based on intent (enhanced with specialist context)
  let contextQueries = generateContextQueries(input.message, intent, mode)
  
  // Enhance context queries with specialist context (Task 2.5: Enhanced Context Queries)
  if (specialistActivation?.primary) {
    const specialist = specialistActivation.primary
    // Add specialist-specific queries
    const specialistQueries = [
      `${specialist.specialist_name} expertise: ${input.message}`,
      `${specialist.specialist_name} domain knowledge: ${specialistActivation.work.domain.join(', ')}`,
      ...specialistActivation.work.systems.map(sys => `${specialist.specialist_name} ${sys} knowledge`)
    ]
    contextQueries = [...contextQueries, ...specialistQueries]
    console.log(`[S1] Enhanced context queries with ${specialistQueries.length} specialist queries`)
  }
  
  // 3. Context Enrichment (HHNI + CMC) with multiple queries
  const hhniResults = await runWithFallback(
    'hhni',
    async () => {
      if (!envConfig.aimosSystems.hhni.enabled) throw new Error('HHNI disabled')
      
      // Search with multiple queries and combine results
      const allResults: Array<{
        atomId: string
        relevanceScore: number
        content: string
        domain: string
        title?: string
      }> = []
      
      for (const query of contextQueries.slice(0, 3)) { // Limit to 3 queries to avoid too many calls
        const result = await hhniService.search(query, 5, 'paragraph')
        if (result.success && result.results) {
          allResults.push(...result.results.map(r => ({
            atomId: r.node.id,
            relevanceScore: r.score || 0.7,
            content: r.node.content || '',
            domain: r.node.level || 'conversation',
            title: r.node.summary
          })))
        }
      }
      
      // Deduplicate by atomId and sort by relevance
      const uniqueResults = Array.from(
        new Map(allResults.map(r => [r.atomId, r])).values()
      ).sort((a, b) => b.relevanceScore - a.relevanceScore).slice(0, 10)
      
      return uniqueResults
    },
    () => {
      degradedMode.hhni = true
      return [] // Fallback: empty results
    }
  )
  
  const cmcAtoms = await runWithFallback(
    'cmc',
    async () => {
      if (!envConfig.aimosSystems.cmc.enabled) throw new Error('CMC disabled')
      
      // Retrieve with multiple queries
      const allAtoms: Array<{
        id: string
        content: string
        modality: string
        tags: string[]
        metadata: {
          timestamp: Date
          location?: string
          relevance?: number
        }
      }> = []
      
      for (const query of contextQueries.slice(0, 2)) { // Limit to 2 queries
        const result = await cmcService.retrieveAtoms(query, 3)
        if (result.success && result.atoms) {
          allAtoms.push(...result.atoms.map((atom: any) => ({
            id: atom.id,
            content: typeof atom.content === 'string' ? atom.content : JSON.stringify(atom.content),
            modality: atom.modality || 'text',
            tags: atom.tags || [],
            metadata: {
              timestamp: new Date(atom.metadata?.timestamp || Date.now()),
              location: atom.metadata?.location,
              relevance: atom.metadata?.relevance || 0.7
            }
          })))
        }
      }
      
      // Deduplicate by id
      const uniqueAtoms = Array.from(
        new Map(allAtoms.map(a => [a.id, a])).values()
      ).slice(0, 5)
      
      return uniqueAtoms
    },
    () => {
      degradedMode.cmc = true
      return [] // Fallback: empty atoms
    }
  )
  
  // Build enriched context
  const enrichedContext: EnrichedContext = {
    hhniResults,
    cmcAtoms,
    sourceCount: hhniResults.length + cmcAtoms.length,
    sourceQuality: [...hhniResults.map(r => r.relevanceScore), ...cmcAtoms.map(a => a.metadata.relevance || 0.7)],
    recentnessScore: calculateRecency(cmcAtoms.map(a => ({ metadata: { timestamp: a.metadata.timestamp } }))),
    atomIds: cmcAtoms.map(a => a.id),
    retrievedAtoms: cmcAtoms,
    hhniQueries: contextQueries,
    completenessScore: (hhniResults.length + cmcAtoms.length) > 0 ? 0.8 : 0.3
  }
  
  // 3. Ambiguity Detection (LLM-based with fallback)
  const ambiguity = await detectAmbiguityLLM(
    input.message,
    enrichedContext,
    sessionContext.conversationHistory.map(m => ({
      role: m.role,
      content: m.content
    }))
  )
  
  // 4. Dynamic κ-Gating (CAS + VIF)
  const confidenceAssessment = await runWithFallback(
    'vif',
    async () => {
      if (!envConfig.aimosSystems.vif.enabled) throw new Error('VIF disabled')
      // Calculate confidence from evidence
      const avgQuality = enrichedContext.sourceQuality.length > 0
        ? enrichedContext.sourceQuality.reduce((a, b) => a + b, 0) / enrichedContext.sourceQuality.length
        : 0.5
      
      const κ = Math.min(0.95, 0.5 + (enrichedContext.sourceCount * 0.1) + (avgQuality * 0.3))
      
      return {
        value: κ,
        band: κ >= 0.95 ? 'S' as const : κ >= 0.90 ? 'A' as const : κ >= 0.85 ? 'B' as const : 'C' as const
      }
    },
    () => {
      degradedMode.vif = true
      return { value: 0.5, band: 'C' as const } // Default medium confidence
    }
  )
  
  // Enhanced risk assessment (Phase 1 Week 4)
  let riskAssessment: Awaited<ReturnType<typeof import('./aetherChat/riskAssessment').assessRisk>>
  try {
    if (envConfig.aimosSystems.cas.enabled) {
      const { assessRisk } = await import('./aetherChat/riskAssessment')
      riskAssessment = await assessRisk(intent, mode, enrichedContext, input.message, casService)
    } else {
      throw new Error('CAS disabled')
    }
  } catch (error) {
    degradedMode.cas = true
    // Fallback to basic risk assessment without CAS
    const { assessRisk } = await import('./aetherChat/riskAssessment')
    riskAssessment = await assessRisk(intent, mode, enrichedContext, input.message)
  }
  
  const baseThreshold = getVIFTierThreshold(intent, mode)
  const requiredConfidence = baseThreshold + (riskAssessment.riskScore * 0.10)
  
  // Determine gating decision (Phase 1 Week 4)
  const gatingDetermination = confidenceAssessment.value >= requiredConfidence ? 'PROCEED' :
                               riskAssessment.riskScore < 0.3 ? 'SPECULATE_WITH_WARNING' :
                               'ABSTAIN_AND_CLARIFY'
  
  const gating: DynamicKappaGate = {
    baseThreshold,
    riskMultiplier: riskAssessment.riskScore,
    requiredConfidence: () => requiredConfidence,
    determination: gatingDetermination
  }
  
  // 5. Safety Filtering (CAS + SCOR)
  const safety: SafetyResult = await runWithFallback(
    'cas',
    async () => {
      // Basic safety check - can be enhanced
      const passed = input.message.length < 10000 // Basic length check
      return {
        passed,
        reason: passed ? undefined : 'Message too long',
        cognitiveState: {
          sessionLength: Date.now() - sessionContext.startTime.getTime(),
          messageCount: sessionContext.messageCount,
          recentErrors: 0
        }
      }
    },
    () => {
      degradedMode.cas = true
      return { 
        passed: true, 
        reason: 'CAS unavailable - using basic safety',
        cognitiveState: {
          sessionLength: Date.now() - sessionContext.startTime.getTime(),
          messageCount: sessionContext.messageCount,
          recentErrors: 0
        }
      }
    }
  )
  
  // 6. Response Planning (Enhanced APOE integration)
  let responsePlan: ResponsePlan
  try {
    if (envConfig.aimosSystems.apoe.enabled) {
      responsePlan = await createEnhancedResponsePlan(
        input.message,
        intent,
        mode,
        enrichedContext,
        ambiguity,
        confidenceAssessment,
        {
          conversationHistory: sessionContext.conversationHistory,
          messageCount: sessionContext.messageCount
        }
      )
    } else {
      throw new Error('APOE disabled')
    }
  } catch (error) {
    degradedMode.apoe = true
    // Fallback: create plan without APOE
    responsePlan = await createEnhancedResponsePlan(
      input.message,
      intent,
      mode,
      enrichedContext,
      ambiguity,
      confidenceAssessment,
      {
        conversationHistory: sessionContext.conversationHistory,
        messageCount: sessionContext.messageCount
      }
    )
  }
  
  // 7. Tool Selection (simplified for now)
  const tools: ToolSelection = {
    tools: [],
    totalCost: 0
  }
  
  // 8. User Preference Inference (Gap 4)
  const userPreference = await inferUserPreference(input.message, intent, sessionContext.userId)
  
  return {
    intent,
    mode,
    enrichedContext,
    ambiguity,
    gating,
    safety,
    initialConfidence: confidenceAssessment,
    responsePlan,
    tools,
    κ_score: confidenceAssessment.value,
    evidence_atoms: cmcAtoms.map(a => a.id),
    retrieval_trace: {
      hhni_queries: contextQueries,
      cmc_atoms: cmcAtoms.map(a => a.id),
      sources_count: enrichedContext.sourceCount
    },
    userPreference,
    degradedMode,
    specialistActivation // Phase 2: Specialist System Integration
  }
}

// Helper functions (legacy - now using LLM-based analysis)
// Kept for backward compatibility and fallback
function analyzeIntent(message: string): ChatIntent {
  const lower = message.toLowerCase()
  if (lower.includes('fix') || lower.includes('bug') || lower.includes('error')) return 'debug_error'
  if (lower.includes('how') || lower.includes('explain') || lower.includes('what')) return 'ask_explain'
  if (lower.includes('design') || lower.includes('architecture') || lower.includes('structure')) return 'design_arch'
  if (lower.includes('plan') || lower.includes('strategy') || lower.includes('roadmap')) return 'planning'
  if (lower.includes('edit') || lower.includes('change') || lower.includes('update')) return 'code_edit'
  if (lower.includes('chat') || lower.includes('talk') || lower.includes('conversation')) return 'meta_chat'
  return 'other'
}

function getVIFTierThreshold(intent: ChatIntent, mode: ChatMode): 0.70 | 0.85 | 0.90 | 0.95 {
  if (mode === 'surgical' || intent === 'code_edit' || intent === 'debug_error') return 0.95
  if (mode === 'deep' || intent === 'design_arch') return 0.90
  if (mode === 'research') return 0.85
  return 0.70
}

function calculateRecency(items: Array<{ metadata?: { timestamp?: Date } }>): number {
  if (items.length === 0) return 0
  const now = Date.now()
  const avgAge = items.reduce((sum, item) => {
    const timestamp = item.metadata?.timestamp?.getTime() || now
    return sum + (now - timestamp)
  }, 0) / items.length
  // Normalize to 0-1 (1 = very recent, 0 = very old)
  const maxAge = 7 * 24 * 60 * 60 * 1000 // 7 days
  return Math.max(0, 1 - (avgAge / maxAge))
}

async function detectAmbiguity(
  message: string,
  context: EnrichedContext,
  degradedMode: DegradedMode
): Promise<AmbiguityState> {
  // Simple ambiguity detection based on number of similar contexts
  if (context.hhniResults.length >= 3 && 
      context.hhniResults.filter(r => r.relevanceScore > 0.7).length >= 3) {
    // High ambiguity - multiple similar contexts
    const interpretations = context.hhniResults
      .slice(0, 3)
      .map((result, index) => ({
        intent: `Interpretation ${index + 1}`,
        confidence: { value: result.relevanceScore, band: 'B' as const },
        supportingEvidence: [result.atomId]
      }))
    
    return {
      isAmbiguous: true,
      ambiguityScore: 0.7,
      interpretations,
      forkedPathUI: {
        question: "I see multiple potential interpretations. Which one?",
        options: interpretations.map(i => i.intent)
      }
    }
  }
  
  return {
    isAmbiguous: false,
    ambiguityScore: 0.2,
    interpretations: []
  }
}

async function inferUserPreference(
  message: string,
  intent: ChatIntent,
  userId?: string
): Promise<UserPreference> {
  // TODO: Check CMC for user profile
  // For now, infer from prompt patterns
  
  const masteryPatterns = [/explain how/i, /how does/i, /why does/i, /teach me/i, /help me understand/i]
  const speedPatterns = [/fix this/i, /solve/i, /quick/i, /fast/i, /just give me/i, /show me the code/i]
  
  const masteryMatches = masteryPatterns.filter(p => p.test(message)).length
  const speedMatches = speedPatterns.filter(p => p.test(message)).length
  
  if (masteryMatches > speedMatches) {
    return {
      mode: 'Mastery',
      confidence: Math.min(0.8, 0.5 + (masteryMatches * 0.1)),
      source: 'implicit'
    }
  } else if (speedMatches > masteryMatches) {
    return {
      mode: 'Speed',
      confidence: Math.min(0.8, 0.5 + (speedMatches * 0.1)),
      source: 'implicit'
    }
  }
  
  // Default based on intent
  const intentBasedPreference: Record<ChatIntent, 'Speed' | 'Mastery'> = {
    'ask_explain': 'Mastery',
    'code_edit': 'Speed',
    'debug_error': 'Speed',
    'design_arch': 'Mastery',
    'meta_chat': 'Mastery',
    'planning': 'Mastery',
    'other': 'Speed'
  }
  
  return {
    mode: intentBasedPreference[intent],
    confidence: 0.6,
    source: 'implicit'
  }
}

// ============================================================================
// S2: CONTEXT WEB & EVIDENCE CONSTRUCTION
// ============================================================================

/**
 * S2: Build Context Web and Evidence Pack
 */
async function buildContextAndEvidence(
  input: RawUserTurn,
  pre: PreProcessingResult
): Promise<{ contextWeb: ContextWeb; evidencePack: EvidencePack }> {
  // 1. Context Node Building (HHNI + CMC)
  const nodes = await Promise.all(
    pre.enrichedContext.hhniResults.map(async (result) => {
      const atom = pre.enrichedContext.cmcAtoms.find(a => a.id === result.atomId)
      return {
        id: result.atomId,
        type: (atom?.modality === 'code' ? 'file' : 'doc') as 'msg' | 'file' | 'doc' | 'mige' | 'event',
        label: result.title || result.content.substring(0, 50),
        importance: result.relevanceScore,
        recency: calculateRecency([{ metadata: { timestamp: atom?.metadata.timestamp } }]),
        context: result.content.substring(0, 200),
        timestamp: atom?.metadata.timestamp,
        relevance: result.relevanceScore,
        size: result.relevanceScore * 10,
        color: getColorForDomain(result.domain),
        glow: calculateRecency([{ metadata: { timestamp: atom?.metadata.timestamp } }])
      }
    })
  )
  
  // 2. Context Edge Building (SEG)
  const edges = await runWithFallback(
    'seg',
    async () => {
      if (!envConfig.aimosSystems.seg.enabled) throw new Error('SEG disabled')
      // Build edges between nodes
      const edgePromises: Promise<any>[] = []
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          // Simple relationship detection (can be enhanced with SEG)
          if (nodes[i].relevance && nodes[j].relevance && 
              Math.abs(nodes[i].relevance - nodes[j].relevance) < 0.2) {
            edgePromises.push(Promise.resolve({
              from: nodes[i].id,
              to: nodes[j].id,
              relation: 'refers_to' as const,
              strength: 0.7,
              thickness: 2,
              color: '#6366f1'
            }))
          }
        }
      }
      return (await Promise.all(edgePromises)).filter(e => e !== null)
    },
    () => {
      pre.degradedMode!.seg = true
      return [] // Fallback: no edges
    }
  )
  
  const contextWeb: ContextWeb = {
    nodes,
    edges,
    layout: 'force-directed'
  }
  
  // 3. Enhanced Evidence Pack Construction (Phase 2 Week 9)
  const { buildEvidencePack } = await import('./aetherChat/evidencePackConstruction')
  
  // Build evidence pack with enhanced extraction and chain building
  let evidenceResult: Awaited<ReturnType<typeof buildEvidencePack>>
  try {
    if (envConfig.aimosSystems.seg.enabled) {
      evidenceResult = await buildEvidencePack(
        pre.enrichedContext.cmcAtoms,
        [{ text: input.message }],
        contextWeb,
        {
          minTrustScore: 0.3,
          maxItems: 20,
          prioritizeRecent: true,
          requireSEGAnchor: false
        },
        segService
      )
    } else {
      throw new Error('SEG disabled')
    }
  } catch (error) {
    pre.degradedMode!.seg = true
    // Fallback: build without SEG
    evidenceResult = await buildEvidencePack(
      pre.enrichedContext.cmcAtoms,
      [{ text: input.message }],
      contextWeb,
      {
        minTrustScore: 0.3,
        maxItems: 20,
        prioritizeRecent: true,
        requireSEGAnchor: false
      }
    )
  }
  
  const evidencePack: EvidencePack = {
    ...evidenceResult.evidencePack,
    completeness: evidenceResult.completeness
  }
  
  // Log completeness if incomplete
  if (!evidenceResult.completeness.isComplete) {
    console.warn('[EvidencePack] Incomplete evidence:', {
      score: evidenceResult.completeness.completenessScore,
      missing: evidenceResult.completeness.missingTypes,
      recommendations: evidenceResult.completeness.recommendations
    })
  }
  
  return { contextWeb, evidencePack }
}

function getColorForDomain(domain: string): string {
  const colors: Record<string, string> = {
    'conversation': '#6366f1',
    'code': '#10b981',
    'documentation': '#f59e0b',
    'architecture': '#8b5cf6'
  }
  return colors[domain] || '#6b7280'
}

// ============================================================================
// S3: THINKING MODE (REASONING CORE)
// ============================================================================

/**
 * S3: Thinking Mode / Reasoning (LUCID Empire 5-Layer)
 */
async function runThinkingMode(
  input: RawUserTurn,
  pre: PreProcessingResult,
  contextWeb: ContextWeb,
  evidencePack: EvidencePack
): Promise<ThinkingResult> {
  // Execute APOE plan (simplified - plan execution happens in APOE service)
  const planExecution = {
    planId: pre.responsePlan.planId,
    stepsCompleted: 1,
    stepsTotal: pre.responsePlan.steps.length,
    costUsed: 0.01,
    tokensUsed: 1000
  }
  
  // Run LUCID Empire 5-layer reasoning
  let lucidResult
  try {
    lucidResult = await runLucidEmpireReasoning(
      input.message,
      pre.enrichedContext,
      evidencePack,
      input.sessionId
    )
  } catch (error) {
    console.error('[ThinkingMode] LUCID Empire failed, using fallback:', error)
    // Fallback: simple reasoning
    lucidResult = {
      reasoningTrace: {
        id: `trace_${Date.now()}`,
        rawText: `Reasoning about: ${input.message}`,
        domains: pre.enrichedContext.hhniResults.map(r => r.domain),
        assumptions: ['User wants accurate information', 'Context is relevant'],
        confidenceSelfReport: pre.initialConfidence.value,
        summary: `Processed ${evidencePack.items.length} evidence items`
      },
      draft: {
        userFacingText: `Based on the context, here's my response to: ${input.message}`,
        actions: [],
        rationale: 'Generated from context and evidence',
        citedEvidenceIds: evidencePack.items.slice(0, 3).map(item => item.id),
        selfEstimatedConfidence: pre.initialConfidence.value
      },
      lucidLayers: {
        layer1: {},
        layer2: {},
        layer3: {},
        layer4: {},
        layer5: {}
      }
    }
  }
  
  return {
    draft: lucidResult.draft,
    reasoningTrace: lucidResult.reasoningTrace,
    planExecution,
    lucidLayers: lucidResult.lucidLayers
  }
}

// ============================================================================
// S4: VIF / CAS GATING (κ-GATING, SAFETY)
// ============================================================================

/**
 * S4: Gating (VIF / CAS / SCOR)
 */
async function runGating(
  input: RawUserTurn,
  pre: PreProcessingResult,
  contextWeb: ContextWeb,
  evidencePack: EvidencePack,
  thinking: ThinkingResult
): Promise<GatingResult> {
  // 1. Confidence assessment (VIF)
  const confidenceCheck = await runWithFallback(
    'vif',
    async () => {
      if (!envConfig.aimosSystems.vif.enabled) throw new Error('VIF disabled')
      // Check if confidence meets threshold
      const meetsThreshold = thinking.draft.selfEstimatedConfidence >= pre.gating.requiredConfidence()
      
      return {
        approved: meetsThreshold,
        gatedConfidence: pre.initialConfidence,
        gateReason: meetsThreshold ? undefined : `Confidence ${thinking.draft.selfEstimatedConfidence.toFixed(2)} below required ${pre.gating.requiredConfidence().toFixed(2)}`
      }
    },
    () => {
      pre.degradedMode!.vif = true
      // Fallback: approve if basic confidence check passes
      return {
        approved: thinking.draft.selfEstimatedConfidence >= 0.5,
        gatedConfidence: pre.initialConfidence,
        gateReason: 'VIF unavailable - using basic confidence check'
      }
    }
  )
  
  // 2. Quality validation (CAS)
  const qualityCheck = await runWithFallback(
    'cas',
    async () => {
      if (!envConfig.aimosSystems.cas.enabled) throw new Error('CAS disabled')
      // Basic quality checks
      const issues: QualityIssue[] = []
      
      if (thinking.draft.userFacingText.length < 10) {
        issues.push({
          type: 'formatting',
          description: 'Response too short',
          severity: 'medium'
        })
      }
      
      return {
        approved: issues.length === 0,
        qualityIssues: issues.length > 0 ? issues : undefined
      } as { approved: boolean; qualityIssues?: QualityIssue[] }
    },
    () => {
      pre.degradedMode!.cas = true
      return { approved: true, qualityIssues: undefined } as { approved: boolean; qualityIssues?: QualityIssue[] }
    }
  )
  
  // 3. Contradiction detection (SEG)
  const contradictionCheck = await runWithFallback(
    'seg',
    async () => {
      if (!envConfig.aimosSystems.seg.enabled) throw new Error('SEG disabled')
      // Simplified contradiction check
      return {
        approved: true,
        contradictions: []
      }
    },
    () => {
      pre.degradedMode!.seg = true
      return { approved: true, contradictions: [] }
    }
  )
  
  // Combine all checks
  const approved = confidenceCheck.approved && qualityCheck.approved && contradictionCheck.approved
  
  return {
    approved,
    gatedConfidence: confidenceCheck.gatedConfidence,
    gateReason: confidenceCheck.gateReason || qualityCheck.qualityIssues?.[0]?.description,
    requiredClarification: !approved ? 'Please clarify your question or provide more context.' : undefined,
    qualityIssues: qualityCheck.qualityIssues,
    contradictions: contradictionCheck.contradictions
  }
}

/**
 * Build clarification draft when gating fails
 */
async function buildClarificationDraft(
  input: RawUserTurn,
  pre: PreProcessingResult,
  gating: GatingResult,
  contextWeb: ContextWeb,
  evidencePack: EvidencePack
): Promise<ThinkingResult> {
  const clarificationText = gating.requiredClarification || 
    `I need more information to answer your question accurately. ${gating.gateReason || 'Could you provide more context?'}`
  
  const draft: DraftResponse = {
    userFacingText: clarificationText,
    actions: [],
    rationale: 'Low confidence - requesting clarification',
    citedEvidenceIds: [],
    selfEstimatedConfidence: gating.gatedConfidence.value
  }
  
  const reasoningTrace: ReasoningTrace = {
    id: `trace_clarification_${Date.now()}`,
    rawText: `Requesting clarification for: ${input.message}`,
    domains: [],
    assumptions: [],
    confidenceSelfReport: gating.gatedConfidence.value,
    summary: 'Clarification requested due to low confidence'
  }
  
  return {
    draft,
    reasoningTrace
  }
}

// ============================================================================
// S5: POST-PROCESSING PIPELINE
// ============================================================================

/**
 * S5: Post-Processing Pipeline
 */
async function runPostProcessing(
  input: RawUserTurn,
  pre: PreProcessingResult,
  contextWeb: ContextWeb,
  evidencePack: EvidencePack,
  thinking: ThinkingResult,
  gating: GatingResult
): Promise<PostProcessingResult> {
  // Phase 4 Week 15: Enhanced Response Refinement & Formatting
  const { refineResponse, detectStructure, formatMarkdown } = await import('./aetherChat/postProcessingRefinement')
  
  // 1. Response refinement (enhanced with LLM-based cleanup)
  let refinement: Awaited<ReturnType<typeof refineResponse>>
  try {
    refinement = await refineResponse(thinking.draft, pre.intent, pre.mode)
  } catch (error) {
    console.warn('[Post-Processing] Refinement failed, using basic cleanup:', error)
    // Fallback: basic cleanup
    refinement = {
      refinedText: thinking.draft.userFacingText.trim(),
      toneConsistent: true,
      technicalAccuracy: 'medium' as const,
      improvements: []
    }
  }
  
  let refinedText = refinement.refinedText
  
  // 2. Structure detection (code blocks, lists, tables, paragraphs)
  const structure = detectStructure(refinedText)
  
  // 3. Enhanced markdown formatting
  const formatting = formatMarkdown(refinedText, structure)
  
  const formatted = {
    markdown: formatting.markdown,
    structure: structure.structure,
    syntaxHighlighted: formatting.syntaxHighlighted
  }
  
  // Phase 4 Week 16: Enhanced Citation Injection & Confidence Indicators
  const { injectCitations, linkCitationsToCMCAtoms } = await import('./aetherChat/citationInjection')
  const { assessSectionConfidence } = await import('./aetherChat/confidenceIndicators')
  
  // 3. Citation injection with markers and provenance
  const citationResult = await runWithFallback(
    'seg',
    async () => {
      return await injectCitations(
        refinedText,
        evidencePack,
        thinking.draft.citedEvidenceIds
      )
    },
    () => {
      // Fallback: basic citation list without markers
      const citedEvidence = thinking.draft.citedEvidenceIds
        .map(id => evidencePack.items.find(item => item.id === id))
        .filter((item): item is EvidenceItem => item !== undefined)
      
      return {
        textWithCitations: refinedText,
        citationMarkers: [],
        provenance: {
          anchors: {},
          overallConfidence: gating.gatedConfidence
        }
      }
    }
  )
  
  // Update refined text with citations
  refinedText = citationResult.textWithCitations
  
  // Link citations to CMC atoms
  const cmcLinks = await linkCitationsToCMCAtoms(citationResult.citationMarkers, evidencePack)
  
  // 4. Section-level confidence indicators
  const sectionConfidences = await assessSectionConfidence(
    refinedText,
    evidencePack,
    thinking.draft.citedEvidenceIds
  )
  
  // Overall confidence (from gating, but can be enhanced with section analysis)
  const confidence = gating.gatedConfidence
  
  // Citations for return (EvidenceItem[] format for backward compatibility)
  const citations = citationResult.citationMarkers
    .map(marker => evidencePack.items.find(item => item.id === marker.evidenceId))
    .filter((item): item is EvidenceItem => item !== undefined)
    .slice(0, 5) // Limit to 5 citations
  
  // Phase 4 Week 17: Enhanced Action Suggestions & Follow-up Questions
  const { generateActionSuggestions } = await import('./aetherChat/actionSuggestions')
  const { generateFollowUpQuestions } = await import('./aetherChat/followUpQuestions')
  
  // 5. Action suggestions (enhanced with SEG and APOE)
  const suggestedActions = await runWithFallback(
    'apoe',
    async () => {
      return await generateActionSuggestions(
        pre.intent,
        pre.mode,
        contextWeb,
        evidencePack,
        thinking.draft,
        input.conversationHistory || []
      )
    },
    () => {
      // Fallback: use draft actions only
      return thinking.draft.actions.length > 0 ? thinking.draft.actions.map(action => ({
        type: (action.type === 'code_edit' ? 'code_edit' : 
               action.type === 'test_run' ? 'test' :
               action.type === 'file_create' || action.type === 'file_delete' ? 'refactor' :
               'other') as 'code_edit' | 'test' | 'refactor' | 'other',
        description: action.description,
        target: action.target,
        priority: 'medium' as const
      })) : []
    }
  )
  
  // 6. Follow-up questions (enhanced with conversation pattern analysis)
  const suggestedFollowUps = await generateFollowUpQuestions(
    pre.intent,
    pre.mode,
    thinking.draft,
    contextWeb,
    evidencePack,
    input.conversationHistory || []
  )
  
  // Phase 4 Week 18: Enhanced Socratic Gate & Error Correction
  const { applySocraticGate } = await import('./aetherChat/socraticGate')
  const { detectAndCorrectErrors } = await import('./aetherChat/errorCorrection')
  
  // 7. Socratic Gate (enhanced with user profile from CMC)
  const solutionReveal = await applySocraticGate(
    pre.intent,
    pre.mode,
    thinking.draft,
    input.userId || 'anonymous',
    refinedText
  )
  
  // 8. Error Correction (CAS integration, factual consistency, self-contradiction, code validity)
  const errorDetection = await detectAndCorrectErrors(
    pre.intent,
    pre.mode,
    thinking.draft,
    refinedText,
    input.conversationHistory || []
  )
  
  const correctionsMade = errorDetection.corrections.length > 0 ? errorDetection.corrections : undefined
  
  return {
    finalText: refinedText,
    uiFormatting: formatted,
    citations,
    confidence,
    suggestedActions: suggestedActions.length > 0 ? suggestedActions : undefined,
    suggestedFollowUps: suggestedFollowUps.length > 0 ? suggestedFollowUps : undefined,
    correctionsMade,
    solutionReveal,
    // Phase 4 Week 15: Refinement metadata
    refinementMetadata: {
      toneConsistent: refinement.toneConsistent,
      technicalAccuracy: refinement.technicalAccuracy,
      improvements: refinement.improvements,
      structureDetected: structure.structure,
      codeBlocksCount: structure.codeBlocks.length,
      listsCount: structure.lists.length,
      tablesCount: structure.tables.length,
      paragraphsCount: structure.paragraphs.length
    },
    // Phase 4 Week 16: Citation and confidence metadata
    citationMetadata: {
      citationMarkers: citationResult.citationMarkers,
      provenance: citationResult.provenance,
      cmcLinks
    },
    sectionConfidences
  }
}

// ============================================================================
// S6: UX/UI POLISH & PANELS
// ============================================================================

/**
 * S6: Build FinalChatTurn (UI payload)
 */
function buildFinalChatTurn(
  input: RawUserTurn,
  pre: PreProcessingResult,
  contextWeb: ContextWeb,
  evidencePack: EvidencePack,
  thinking: ThinkingResult,
  gating: GatingResult,
  post: PostProcessingResult
): FinalChatTurn {
  const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  
  // UI hints calculation
  const uiHints = {
    showContextWeb: contextWeb.nodes.length > 0,
    showEvidencePanel: evidencePack.items.length > 0,
    showThinkingMode: pre.mode === 'deep' || pre.mode === 'research',
    showMigeTimeline: false // TODO: Implement MIGE integration
  }
  
  // Panel data preparation
  const panelData = {
    contextWeb: uiHints.showContextWeb ? {
      graph: contextWeb,
      interactions: {
        semanticSearch: async (query: string) => {
          // Would use HHNI in production
          return contextWeb.nodes.filter(n => n.label.toLowerCase().includes(query.toLowerCase()))
        },
        timelineView: async (topicId: string, dateRange: [Date, Date]) => {
          // Would use TCS in production
          return { topicId, snapshots: [] }
        },
        causationChain: async (nodeId: string) => {
          return contextWeb.nodes.filter(n => contextWeb.edges.some(e => e.to === nodeId && e.from === n.id))
        },
        findCommonality: async (nodeIds: string[]) => {
          return { themes: [], sharedConcepts: [], connections: [] }
        }
      }
    } : undefined,
    evidence: uiHints.showEvidencePanel ? {
      items: evidencePack.items,
      chain: {
        claims: [{ text: input.message, evidenceIds: evidencePack.items.map(i => i.id) }],
        links: contextWeb.edges
      },
      provenance: evidencePack.items.map(item => ({
        atom: pre.enrichedContext.cmcAtoms.find(a => a.id === item.id) || {
          id: item.id,
          content: item.excerpt,
          modality: 'text',
          tags: [],
          metadata: { timestamp: item.timestamp || new Date() }
        },
        witness: undefined // TODO: Add VIF witness
      }))
    } : undefined
  }
  
  return {
    messageId,
    sessionId: input.sessionId,
    userText: input.message,
    assistantText: post.finalText,
    confidence: post.confidence,
    contextWeb,
    evidence: post.citations,
    reasoningSummary: thinking.reasoningTrace.summary,
    migeUpdates: undefined, // TODO: Implement MIGE
    uiHints,
    timestamp: new Date().toISOString(),
    panelData,
    // Include plan from pre-processing (for Thinking Mode panel)
    plan: pre.responsePlan,
    streamingChunks: undefined, // TODO: Add streaming support to orchestrator
    // Include ambiguity state if ambiguous (for Ambiguity Resolver UI)
    ambiguity: pre.ambiguity.isAmbiguous ? pre.ambiguity : undefined,
    // Include gating determination and risk assessment (Phase 1 Week 4)
    gatingDetermination: pre.gating.determination,
    riskAssessment: (() => {
      // Derive risk assessment from gating data
      const riskScore = pre.gating.riskMultiplier
      let riskLevel: 'low' | 'medium' | 'high' | 'critical'
      let category: 'casual' | 'informational' | 'modification' | 'destructive' | 'critical'
      
      if (riskScore >= 0.8) {
        riskLevel = 'critical'
      } else if (riskScore >= 0.6) {
        riskLevel = 'high'
      } else if (riskScore >= 0.4) {
        riskLevel = 'medium'
      } else {
        riskLevel = 'low'
      }
      
      if (riskScore >= 0.9) {
        category = 'critical'
      } else if (riskScore >= 0.7) {
        category = 'destructive'
      } else if (riskScore >= 0.5) {
        category = 'modification'
      } else if (riskScore >= 0.3) {
        category = 'informational'
      } else {
        category = 'casual'
      }
      
      return {
        riskScore,
        riskLevel,
        category
      }
    })()
  }
}

// ============================================================================
// S7: MEMORY, TIMELINE, & EVOLUTION
// ============================================================================

/**
 * S7: Persist to AIM-OS (CMC, HHNI, SEG, TCS, MIGE)
 */
async function persistTurnToAimos(
  input: RawUserTurn,
  pre: PreProcessingResult,
  contextWeb: ContextWeb,
  evidencePack: EvidencePack,
  thinking: ThinkingResult,
  gating: GatingResult,
  post: PostProcessingResult,
  finalTurn: FinalChatTurn
): Promise<void> {
  // 1. CMC storage (chat message atom)
  await runWithFallback(
    'cmc',
    async () => {
      if (!envConfig.aimosSystems.cmc.enabled) return
      await cmcService.storeAtom(
        JSON.stringify({
          userMessage: input.message,
          assistantMessage: finalTurn.assistantText,
          confidence: finalTurn.confidence,
          evidenceIds: finalTurn.evidence.map(e => e.id)
        }),
        'text',
        {
          chat: 1,
          session: 1
        },
        {
          session: input.sessionId,
          userId: input.userId,
          messageId: finalTurn.messageId,
          timestamp: finalTurn.timestamp
        }
      )
    },
    () => console.warn('CMC unavailable - skipping message storage')
  )
  
  // 2. CMC storage (enhanced reasoning trace with all 5 LUCID layers)
  await runWithFallback(
    'cmc',
    async () => {
      if (!envConfig.aimosSystems.cmc.enabled) return
      
      // Use enhanced reasoning trace storage if LUCID layers are available
      if (thinking.lucidLayers) {
        const { storeLucidEmpireTrace } = await import('./aetherChat/reasoningTraceStorage')
        const { retrieveRelatedTraces } = await import('./aetherChat/reasoningTraceStorage')
        
        // Find related traces across sessions
        const domain = pre.enrichedContext.hhniResults[0]?.domain || 'general'
        const relatedTracesResult = await retrieveRelatedTraces(
          thinking.reasoningTrace.id,
          domain,
          input.sessionId
        )
        
        // Store complete LUCID Empire trace
        await storeLucidEmpireTrace({
          traceId: thinking.reasoningTrace.id,
          sessionId: input.sessionId,
          messageId: finalTurn.messageId,
          question: input.message,
          timestamp: new Date(),
          layer1: {
            articulation: thinking.lucidLayers.layer1 || {},
            reasoningTrace: thinking.reasoningTrace,
            atomId: undefined // Will be set by storeLucidEmpireTrace
          },
          layer2: {
            reflection: thinking.lucidLayers.layer2 || {},
            evolvedReasoning: thinking.reasoningTrace,
            atomId: undefined,
            reflectsOn: relatedTracesResult.success 
              ? relatedTracesResult.traces.map(t => t.atomId).filter(Boolean) as string[]
              : []
          },
          layer3: {
            patterns: thinking.lucidLayers.layer3 || {},
            insights: (thinking.lucidLayers.layer3 as any)?.insights || [],
            atomId: undefined,
            domain
          },
          layer4: {
            evolution: thinking.lucidLayers.layer4 || {},
            trends: (thinking.lucidLayers.layer4 as any)?.trends || [],
            atomId: undefined
          },
          layer5: {
            metaReasoning: thinking.lucidLayers.layer5 || {},
            depth: (thinking.lucidLayers.layer5 as any)?.depth || 0,
            atomId: undefined
          },
          finalReasoningTrace: thinking.reasoningTrace,
          relatedTraces: relatedTracesResult.success
            ? relatedTracesResult.traces.map(t => t.traceId)
            : [],
          domain,
          topics: thinking.reasoningTrace.domains
        })
      } else {
        // Fallback: store basic reasoning trace
        await cmcService.storeAtom(
          JSON.stringify(thinking.reasoningTrace),
          'text',
          {
            reasoning: 1,
            trace: 1
          },
          {
            session: input.sessionId,
            messageId: finalTurn.messageId,
            confidence: thinking.reasoningTrace.confidenceSelfReport.toString()
          }
        )
      }
    },
    () => console.warn('CMC unavailable - skipping reasoning trace storage')
  )
  
  // 3. Cache session state (Gap 1)
  await cacheSessionState(input.sessionId, contextWeb, evidencePack.items.reduce((acc, item) => {
    acc[item.id] = item
    return acc
  }, {} as Record<string, EvidenceItem>))
  
  // 4. TCS timeline entry (already done in S0, but add completion entry)
  await runWithFallback(
    'tcs',
    async () => {
      if (!envConfig.aimosSystems.tcs.enabled) return
      await tcsService.addEntry(
        'chat_turn_complete',
        `Completed response for: ${input.message}`,
        {
          sessionId: input.sessionId,
          messageId: finalTurn.messageId,
          confidence: finalTurn.confidence.value.toString()
        }
      )
    },
    () => console.warn('TCS unavailable - skipping completion entry')
  )
  
  // 5. SEG graph updates (relationships) - simplified
  await runWithFallback(
    'seg',
    async () => {
      if (!envConfig.aimosSystems.seg.enabled) return
      // Would use SEG to update relationships between evidence items
      // For now, just log
      console.log('SEG: Would update relationships for', evidencePack.items.length, 'items')
    },
    () => console.warn('SEG unavailable - skipping graph updates')
  )
  
  // 6. HHNI indexing happens automatically via CMC storage
  // 7. MIGE idea evolution - TODO: Implement when MIGE is available
}

// ============================================================================
// S8: OPTIONAL AUTONOMOUS FOLLOW-UPS
// ============================================================================

/**
 * S8: Optional autonomous follow-ups (APOE, cursor loop)
 */
async function maybeScheduleFollowUps(
  input: RawUserTurn,
  pre: PreProcessingResult,
  finalTurn: FinalChatTurn
): Promise<void> {
  // Only schedule follow-ups for certain intents
  if (pre.intent !== 'code_edit' && pre.intent !== 'debug_error') {
    return
  }
  
  // Schedule background tasks via APOE (simplified)
  await runWithFallback(
    'apoe',
    async () => {
      if (!envConfig.aimosSystems.apoe.enabled) return
      // Would create background plan for:
      // - Running tests
      // - Refactoring code
      // - Further research
      console.log('APOE: Would schedule follow-up tasks for', pre.intent)
    },
    () => console.warn('APOE unavailable - skipping follow-up scheduling')
  )
  
  // Cursor autonomous loop integration would happen here
  // For now, just log
  console.log('Would integrate with Cursor autonomous loop if enabled')
}

// ============================================================================
// GAP 1: SESSION HYDRATION
// ============================================================================

/**
 * Load session state with cached graphs (Gap 1)
 */
export async function loadSessionState(sessionId: string): Promise<HydratedSession> {
  try {
    // 1. Load message history from CMC
    const historyResult = await runWithFallback(
      'cmc',
      async () => {
        if (!envConfig.aimosSystems.cmc.enabled) throw new Error('CMC disabled')
      const result = await cmcService.retrieveAtoms(`session:${sessionId}`, 100)
        
        if (result.success && result.atoms) {
        const turns: FinalChatTurn[] = []
        for (const atom of result.atoms || []) {
          if (atom.modality === 'text' || (atom.tags && Object.keys(atom.tags).includes('chat'))) {
            try {
              const content = typeof atom.content === 'string' 
                ? JSON.parse(atom.content) 
                : atom.content
              turns.push({
                messageId: atom.id,
                sessionId,
                userText: content.userMessage || '',
                assistantText: content.assistantMessage || '',
                confidence: { value: 0.7, band: 'B' as const },
                contextWeb: { nodes: [], edges: [] },
                evidence: [],
                uiHints: { showContextWeb: false, showEvidencePanel: false, showThinkingMode: false },
                timestamp: new Date(atom.metadata?.timestamp || Date.now()).toISOString()
              })
            } catch {
              // Skip invalid atoms
            }
          }
        }
        return turns
        }
        return []
      },
      () => [] // Fallback: empty history
    )
    
    // 2. Load cached context graph snapshot
    const contextGraphResult = await runWithFallback(
      'cmc',
      async () => {
        if (!envConfig.aimosSystems.cmc.enabled) throw new Error('CMC disabled')
        const result = await cmcService.retrieveAtoms(`context_graph_snapshot session:${sessionId}`, 1)
        
        if (result.success && result.atoms && result.atoms.length > 0) {
          const atom = result.atoms[0]
          try {
            const content = typeof atom.content === 'string' 
              ? JSON.parse(atom.content) 
              : atom.content
            return content as ContextWeb
          } catch {
            return null
          }
        }
        return null
      },
      () => null // Fallback: no cached graph
    )
    
    // 3. Load cached evidence
    const evidenceCacheResult = await runWithFallback(
      'cmc',
      async () => {
        if (!envConfig.aimosSystems.cmc.enabled) throw new Error('CMC disabled')
        const result = await cmcService.retrieveAtoms(`evidence_cache session:${sessionId}`, 1)
        
        if (result.success && result.atoms && result.atoms.length > 0) {
          const atom = result.atoms[0]
          try {
            const content = typeof atom.content === 'string' 
              ? JSON.parse(atom.content) 
              : atom.content
            return content as Record<string, EvidenceItem>
          } catch {
            return {}
          }
        }
        return {}
      },
      () => ({}) // Fallback: empty cache
    )
    
    // 4. Validate cache freshness
    let contextGraphSnapshot = contextGraphResult
    let evidenceCache = evidenceCacheResult
    
    if (contextGraphSnapshot) {
      // Check if atoms still exist
      const atomIds = contextGraphSnapshot.nodes.map(n => n.id)
      const verifyResult = await runWithFallback(
        'cmc',
        async () => {
          // Verify atoms exist (simplified - check first few)
            const checkAtoms = await Promise.all(
              atomIds.slice(0, 5).map(id => 
                cmcService.retrieveAtoms(`atom:${id}`, 1)
                  .then((r: any) => r.success && r.atoms && r.atoms.length > 0)
                  .catch(() => false)
              )
            )
          const existingCount = checkAtoms.filter(Boolean).length
          return existingCount / 5 >= 0.8 // 80% threshold
        },
        () => false
      )
      
      if (!verifyResult) {
        // Cache is stale
        contextGraphSnapshot = null
        evidenceCache = {}
      }
    }
    
    // 5. If cache is missing or stale, return empty (will be computed fresh)
    if (!contextGraphSnapshot || Object.keys(evidenceCache).length === 0) {
      return {
        history: historyResult,
        contextGraphSnapshot: { nodes: [], edges: [] },
        evidenceCache: {},
        cacheMetadata: {
          lastUpdated: new Date(),
          version: '1.0',
          atomIds: []
        }
      }
    }
    
    return {
      history: historyResult,
      contextGraphSnapshot,
      evidenceCache,
      cacheMetadata: {
        lastUpdated: new Date(),
        version: '1.0',
        atomIds: Object.keys(evidenceCache)
      }
    }
  } catch (error) {
    console.error('Session hydration error:', error)
    // Return empty session on error
    return {
      history: [],
      contextGraphSnapshot: { nodes: [], edges: [] },
      evidenceCache: {},
      cacheMetadata: {
        lastUpdated: new Date(),
        version: '1.0',
        atomIds: []
      }
    }
  }
}

/**
 * Cache session state after computation (Gap 1)
 */
export async function cacheSessionState(
  sessionId: string,
  contextWeb: ContextWeb,
  evidenceCache: Record<string, EvidenceItem>
): Promise<void> {
  if (!envConfig.aimosSystems.cmc.enabled) return
  
  try {
    // Store context graph snapshot
    await runWithFallback(
      'cmc',
      async () => {
      await cmcService.storeAtom(
        JSON.stringify(contextWeb),
        'text',
        {
          cache: 1,
          context_graph: 1
        },
        {
          session: sessionId,
          cache: 'true',
          version: '1.0'
        }
      )
      },
      () => {
        console.warn('Failed to cache context graph snapshot')
      }
    )
    
    // Store evidence cache
    await runWithFallback(
      'cmc',
      async () => {
      await cmcService.storeAtom(
        JSON.stringify(evidenceCache),
        'text',
        {
          cache: 1,
          evidence: 1
        },
        {
          session: sessionId,
          cache: 'true',
          version: '1.0'
        }
      )
      },
      () => {
        console.warn('Failed to cache evidence')
      }
    )
  } catch (error) {
    console.error('Session state caching error:', error)
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

export { CircuitBreaker }
export type { SessionContext }

