/**
 * Response Planning Service
 * Enhanced APOE integration for Aether Chat
 * 
 * Phase 1: Enhanced Pre-Processing Pipeline
 */

import { APOEService } from '../APOEService'
import type { 
  ChatIntent, 
  ChatMode, 
  EnrichedContext, 
  AmbiguityState,
  ConfidenceScore,
  ResponsePlan
} from '../../types/aetherChatTypes'

const apoeService = new APOEService()

/**
 * Create enhanced response plan using APOE
 */
export async function createEnhancedResponsePlan(
  message: string,
  intent: ChatIntent,
  mode: ChatMode,
  enrichedContext: EnrichedContext,
  ambiguity: AmbiguityState,
  confidence: ConfidenceScore,
  sessionContext: {
    conversationHistory: Array<{ role: string; content: string }>
    messageCount: number
  }
): Promise<ResponsePlan> {
  try {
    // Build comprehensive context for APOE
    const contextParts: string[] = []
    
    // Add intent and mode
    contextParts.push(`Intent: ${intent}`)
    contextParts.push(`Mode: ${mode}`)
    contextParts.push(`Confidence: ${confidence.band} (${(confidence.value * 100).toFixed(0)}%)`)
    
    // Add ambiguity information
    if (ambiguity.isAmbiguous) {
      contextParts.push(`\nAmbiguity detected (score: ${ambiguity.ambiguityScore.toFixed(2)})`)
      contextParts.push(`Possible interpretations: ${ambiguity.interpretations.length}`)
      ambiguity.interpretations.forEach((interp, i) => {
        contextParts.push(`  ${i + 1}. ${interp.intent} (confidence: ${interp.confidence.band})`)
      })
    }
    
    // Add enriched context summary
    if (enrichedContext.sourceCount > 0) {
      contextParts.push(`\nFound ${enrichedContext.sourceCount} relevant sources:`)
      enrichedContext.hhniResults.slice(0, 3).forEach((result, i) => {
        contextParts.push(`  ${i + 1}. ${result.title || result.domain}: ${result.content.substring(0, 100)}...`)
      })
      if (enrichedContext.cmcAtoms.length > 0) {
        contextParts.push(`  + ${enrichedContext.cmcAtoms.length} memory atoms from CMC`)
      }
    } else {
      contextParts.push(`\nNo relevant sources found - low context availability`)
    }
    
    // Add conversation history context
    if (sessionContext.conversationHistory.length > 0) {
      const recentMessages = sessionContext.conversationHistory.slice(-2)
      contextParts.push(`\nRecent conversation context:`)
      recentMessages.forEach(msg => {
        contextParts.push(`  ${msg.role}: ${msg.content.substring(0, 100)}${msg.content.length > 100 ? '...' : ''}`)
      })
    }
    
    // Determine priority based on intent and mode
    let priority: 'low' | 'medium' | 'high' | 'critical' = 'medium'
    if (intent === 'debug_error' || intent === 'code_edit') {
      priority = 'high'
    } else if (intent === 'design_arch' || mode === 'deep') {
      priority = 'high'
    } else if (confidence.value < 0.7) {
      priority = 'low' // Lower priority if low confidence
    }
    
    // Build goal with context
    const goal = `Answer user's question: "${message}"`
    const context = contextParts.join('\n')
    
    // Create plan via APOE
    const planResult = await apoeService.createPlan(goal, context, priority)
    
    if (planResult.success && planResult.plan) {
      // Enhance plan with confidence and context information
      return {
        planId: planResult.plan.plan_id,
        goal: planResult.plan.goal || goal,
        steps: (planResult.plan.steps || []).map((step: any) => ({
          stepId: step.id || `step_${Date.now()}_${Math.random()}`,
          role: (step.role || 'builder') as any,
          action: step.description || step.action || 'Process request',
          dependencies: step.dependencies || []
        })),
        budget: {
          tokens: estimateTokenBudget(intent, mode, enrichedContext.sourceCount),
          cost: estimateCost(intent, mode, enrichedContext.sourceCount)
        },
        primaryRole: (planResult.plan.steps?.[0]?.role || 'builder') as any,
        vifConfidence: confidence.value
      }
    }
    
    // Fallback: create simple plan
    return createFallbackPlan(message, intent, mode, confidence)
  } catch (error) {
    console.error('[ResponsePlanning] APOE plan creation failed, using fallback:', error)
    return createFallbackPlan(message, intent, mode, confidence)
  }
}

/**
 * Create fallback plan when APOE is unavailable
 */
function createFallbackPlan(
  message: string,
  intent: ChatIntent,
  mode: ChatMode,
  confidence: ConfidenceScore
): ResponsePlan {
  // Determine steps based on intent
  const steps: Array<{
    stepId: string
    role: 'planner' | 'retriever' | 'reasoner' | 'builder' | 'verifier' | 'critic' | 'operator'
    action: string
    dependencies: string[]
  }> = []
  
  // Add retrieval step if needed
  if (intent === 'ask_explain' || intent === 'planning' || mode === 'research') {
    steps.push({
      stepId: '1',
      role: 'retriever',
      action: 'Gather relevant information and context',
      dependencies: []
    })
  }
  
  // Add reasoning step for complex intents
  if (intent === 'design_arch' || intent === 'planning' || mode === 'deep') {
    steps.push({
      stepId: '2',
      role: 'reasoner',
      action: 'Analyze requirements and design approach',
      dependencies: steps.length > 0 ? [steps[steps.length - 1].stepId] : []
    })
  }
  
  // Always add builder step
  steps.push({
    stepId: String(steps.length + 1),
    role: 'builder',
    action: `Generate response for: ${message}`,
    dependencies: steps.length > 0 ? [steps[steps.length - 1].stepId] : []
  })
  
  // Add verification step for high-risk intents
  if (intent === 'code_edit' || intent === 'debug_error') {
    steps.push({
      stepId: String(steps.length + 1),
      role: 'verifier',
      action: 'Verify response accuracy and completeness',
      dependencies: [steps[steps.length - 1].stepId]
    })
  }
  
  return {
    planId: `plan_${Date.now()}`,
    goal: `Answer: ${message}`,
    steps,
    budget: {
      tokens: estimateTokenBudget(intent, mode, 0),
      cost: estimateCost(intent, mode, 0)
    },
    primaryRole: steps[0]?.role || 'builder',
    vifConfidence: confidence.value
  }
}

/**
 * Estimate token budget based on intent, mode, and context
 */
function estimateTokenBudget(
  intent: ChatIntent,
  mode: ChatMode,
  sourceCount: number
): number {
  let baseTokens = 2000
  
  // Adjust based on mode
  if (mode === 'deep') {
    baseTokens = 5000
  } else if (mode === 'research') {
    baseTokens = 4000
  } else if (mode === 'surgical') {
    baseTokens = 3000
  }
  
  // Adjust based on intent
  if (intent === 'design_arch' || intent === 'planning') {
    baseTokens += 2000
  } else if (intent === 'code_edit' || intent === 'debug_error') {
    baseTokens += 1500
  }
  
  // Add tokens for context
  baseTokens += sourceCount * 200
  
  return Math.min(baseTokens, 10000) // Cap at 10k tokens
}

/**
 * Estimate cost based on token budget
 */
function estimateCost(
  intent: ChatIntent,
  mode: ChatMode,
  sourceCount: number
): number {
  const tokens = estimateTokenBudget(intent, mode, sourceCount)
  // Rough estimate: $0.01 per 1k tokens (average across providers)
  return (tokens / 1000) * 0.01
}

