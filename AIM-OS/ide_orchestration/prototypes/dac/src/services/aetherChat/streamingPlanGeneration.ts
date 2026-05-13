/**
 * Streaming Plan Generation Service
 * Token-by-token APOE plan generation for Thinking Mode
 * 
 * Phase 1 Week 2: Thinking Mode Enhancements (Gap 5)
 */

import { LLMService } from '../lucid-chat/llm/LLMService'
import { getActiveModel } from '../../config/modelRegistry'
import type { 
  ChatIntent, 
  ChatMode, 
  EnrichedContext, 
  AmbiguityState,
  ConfidenceScore,
  ResponsePlan,
  StreamingPlanStep,
  PlanStreamChunk
} from '../../types/aetherChatTypes'

const llmService = new LLMService()

/**
 * Generate APOE plan with streaming updates
 * Yields chunks as the plan is generated token-by-token
 */
export async function* createPlanStreaming(
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
): AsyncGenerator<PlanStreamChunk, ResponsePlan, unknown> {
  try {
    const model = getActiveModel(intent, mode === 'deep' ? 'complex' : 'medium', 0.05, 2000)
    
    if (!model) {
      // Fallback: non-streaming plan
      const fallbackPlan = await createNonStreamingPlan(message, intent, mode, enrichedContext, ambiguity, confidence, sessionContext)
      yield* convertPlanToStream(fallbackPlan)
      return fallbackPlan
    }

    // Build comprehensive context for APOE (same as non-streaming)
    const contextParts: string[] = []
    
    contextParts.push(`Intent: ${intent}`)
    contextParts.push(`Mode: ${mode}`)
    contextParts.push(`Confidence: ${confidence.band} (${(confidence.value * 100).toFixed(0)}%)`)
    
    if (ambiguity.isAmbiguous) {
      contextParts.push(`\nAmbiguity detected (score: ${ambiguity.ambiguityScore.toFixed(2)})`)
      contextParts.push(`Possible interpretations: ${ambiguity.interpretations.length}`)
    }
    
    if (enrichedContext.sourceCount > 0) {
      contextParts.push(`\nFound ${enrichedContext.sourceCount} relevant sources`)
    }
    
    if (sessionContext.conversationHistory.length > 0) {
      const recentMessages = sessionContext.conversationHistory.slice(-2)
      contextParts.push(`\nRecent conversation context:`)
      recentMessages.forEach(msg => {
        contextParts.push(`  ${msg.role}: ${msg.content.substring(0, 100)}${msg.content.length > 100 ? '...' : ''}`)
      })
    }
    
    // Determine priority
    let priority: 'low' | 'medium' | 'high' | 'critical' = 'medium'
    if (intent === 'debug_error' || intent === 'code_edit') {
      priority = 'high'
    } else if (intent === 'design_arch' || mode === 'deep') {
      priority = 'high'
    } else if (confidence.value < 0.7) {
      priority = 'low'
    }
    
    // Build prompt for plan generation
    const systemPrompt = `You are an APOE (Autonomous Planning and Orchestration Engine) system. Generate an execution plan as JSON.

The plan should be a JSON object with this structure:
{
  "plan_id": "plan_123",
  "goal": "Answer user's question: [question]",
  "steps": [
    {
      "id": "step_1",
      "role": "planner|retriever|reasoner|builder|verifier|critic|operator",
      "description": "Step description here",
      "dependencies": []
    }
  ]
}

Generate the plan step-by-step. Start with the goal, then add steps one at a time.`

    const userPrompt = `User Question: "${message}"

Context:
${contextParts.join('\n')}

Generate an execution plan to answer this question. Output the plan as JSON, generating it step-by-step.`

    // Stream plan generation
    const steps: Array<{
      stepId: string
      role: any
      action: string
      dependencies: string[]
      partialText: string
    }> = []
    
    let buffer = ''
    let inJsonBlock = false
    let jsonBuffer = ''
    
    // Use LLM streaming if available
    try {
      // Check if model supports streaming
      if (model.capabilities?.supportsStreaming) {
        // Convert callback-based streaming to async generator
        const streamGenerator = createStreamGenerator(llmService, {
          provider: model.provider as any,
          model: model.model,
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt }
          ],
          temperature: 0.7,
          maxTokens: 2000,
          stream: true
        })
        
        // Process streaming chunks
        for await (const chunk of streamGenerator) {
          buffer += chunk.text
      
          // Detect JSON block start
          if (buffer.includes('```json') || buffer.includes('{')) {
            if (!inJsonBlock) {
              inJsonBlock = true
              const jsonStart = buffer.indexOf('{')
              if (jsonStart >= 0) {
                jsonBuffer = buffer.substring(jsonStart)
              }
            } else {
              jsonBuffer += chunk.text
            }
            
            // Try to parse partial JSON to extract steps
            if (inJsonBlock && jsonBuffer.length > 0) {
              const parsed = tryParsePartialJSON(jsonBuffer)
              if (parsed) {
                // Emit step updates
                if (parsed.steps && Array.isArray(parsed.steps)) {
                  for (let i = steps.length; i < parsed.steps.length; i++) {
                    const step = parsed.steps[i]
                    if (step && step.id) {
                      // New step started
                      yield {
                        type: 'step_start' as const,
                        stepId: step.id,
                        role: step.role,
                        partialAction: step.description || ''
                      }
                      
                      steps.push({
                        stepId: step.id,
                        role: step.role || 'builder',
                        action: step.description || '',
                        dependencies: step.dependencies || [],
                        partialText: step.description || ''
                      })
                    }
                  }
                  
                  // Update existing steps with partial text
                  parsed.steps.forEach((step: any, index: number) => {
                    if (step && step.description && steps[index]) {
                      steps[index].partialText = step.description
                      steps[index].action = step.description
                      
                      yield {
                        type: 'step_update' as const,
                        stepId: step.id,
                        partialAction: step.description
                      }
                    }
                  })
                }
              }
            }
          }
        }
        
        // Final parse of complete JSON
        const finalJson = tryParseCompleteJSON(jsonBuffer || buffer)
        if (finalJson && finalJson.steps) {
          // Mark all steps as complete
          finalJson.steps.forEach((step: any) => {
            yield {
              type: 'step_complete' as const,
              stepId: step.id
            }
          })
          
          // Build final plan
          const finalPlan: ResponsePlan = {
            planId: finalJson.plan_id || `plan_${Date.now()}`,
            goal: finalJson.goal || `Answer: ${message}`,
            steps: finalJson.steps.map((step: any) => ({
              stepId: step.id,
              role: (step.role || 'builder') as any,
              action: step.description || step.action || 'Process request',
              dependencies: step.dependencies || []
            })),
            budget: {
              tokens: estimateTokenBudget(intent, mode, enrichedContext.sourceCount),
              cost: estimateCost(intent, mode, enrichedContext.sourceCount)
            },
            primaryRole: (finalJson.steps[0]?.role || 'builder') as any,
            vifConfidence: confidence.value
          }
          
          return finalPlan
        }
      }
    } catch (streamError) {
      console.warn('[StreamingPlan] Streaming failed, using non-streaming fallback:', streamError)
    }
    
    // Fallback: non-streaming plan
    const fallbackPlan = await createNonStreamingPlan(message, intent, mode, enrichedContext, ambiguity, confidence, sessionContext)
    yield* convertPlanToStream(fallbackPlan)
    return fallbackPlan
  } catch (error) {
    console.error('[StreamingPlan] Plan generation failed:', error)
    // Return minimal fallback plan
    const fallbackPlan: ResponsePlan = {
      planId: `plan_${Date.now()}`,
      goal: `Answer: ${message}`,
      steps: [{
        stepId: '1',
        role: 'builder',
        action: `Generate response for: ${message}`,
        dependencies: []
      }],
      budget: { tokens: 2000, cost: 0.02 },
      primaryRole: 'builder',
      vifConfidence: confidence.value
    }
    yield* convertPlanToStream(fallbackPlan)
    return fallbackPlan
  }
}

/**
 * Convert a complete plan to streaming chunks (for fallback)
 */
async function* convertPlanToStream(plan: ResponsePlan): AsyncGenerator<PlanStreamChunk, void, unknown> {
  for (const step of plan.steps) {
    yield {
      type: 'step_start' as const,
      stepId: step.stepId,
      role: step.role,
      partialAction: step.action
    }
    
    yield {
      type: 'step_complete' as const,
      stepId: step.stepId
    }
  }
}

/**
 * Create non-streaming plan (fallback)
 */
async function createNonStreamingPlan(
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
  // Import the non-streaming version
  const { createEnhancedResponsePlan } = await import('./responsePlanning')
  return await createEnhancedResponsePlan(
    message,
    intent,
    mode,
    enrichedContext,
    ambiguity,
    confidence,
    sessionContext
  )
}

/**
 * Try to parse partial JSON (for streaming)
 */
function tryParsePartialJSON(text: string): any {
  try {
    // Remove markdown code blocks if present
    let jsonText = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim()
    
    // Try to find a complete JSON object
    const jsonStart = jsonText.indexOf('{')
    if (jsonStart < 0) return null
    
    jsonText = jsonText.substring(jsonStart)
    
    // Try to close incomplete JSON
    let braceCount = 0
    let inString = false
    let escapeNext = false
    let lastValidIndex = -1
    
    for (let i = 0; i < jsonText.length; i++) {
      const char = jsonText[i]
      
      if (escapeNext) {
        escapeNext = false
        continue
      }
      
      if (char === '\\') {
        escapeNext = true
        continue
      }
      
      if (char === '"' && !escapeNext) {
        inString = !inString
        continue
      }
      
      if (!inString) {
        if (char === '{') braceCount++
        if (char === '}') braceCount--
        
        if (braceCount === 0 && i > 0) {
          lastValidIndex = i
        }
      }
    }
    
    // If we found a complete object, parse it
    if (lastValidIndex > 0) {
      const completeJson = jsonText.substring(0, lastValidIndex + 1)
      return JSON.parse(completeJson)
    }
    
    // Otherwise, try to close it manually
    if (braceCount > 0) {
      const closedJson = jsonText + '}'.repeat(braceCount)
      try {
        return JSON.parse(closedJson)
      } catch {
        // If that fails, return null
        return null
      }
    }
    
    return null
  } catch {
    return null
  }
}

/**
 * Try to parse complete JSON
 */
function tryParseCompleteJSON(text: string): any {
  try {
    let jsonText = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim()
    const jsonStart = jsonText.indexOf('{')
    if (jsonStart >= 0) {
      jsonText = jsonText.substring(jsonStart)
    }
    return JSON.parse(jsonText)
  } catch {
    return null
  }
}

/**
 * Estimate token budget
 */
function estimateTokenBudget(
  intent: ChatIntent,
  mode: ChatMode,
  sourceCount: number
): number {
  let baseTokens = 2000
  
  if (mode === 'deep') {
    baseTokens = 5000
  } else if (mode === 'research') {
    baseTokens = 4000
  } else if (mode === 'surgical') {
    baseTokens = 3000
  }
  
  if (intent === 'design_arch' || intent === 'planning') {
    baseTokens += 2000
  } else if (intent === 'code_edit' || intent === 'debug_error') {
    baseTokens += 1500
  }
  
  baseTokens += sourceCount * 200
  
  return Math.min(baseTokens, 10000)
}

/**
 * Estimate cost
 */
function estimateCost(
  intent: ChatIntent,
  mode: ChatMode,
  sourceCount: number
): number {
  const tokens = estimateTokenBudget(intent, mode, sourceCount)
  return (tokens / 1000) * 0.01
}

/**
 * Convert callback-based streaming to async generator
 */
async function* createStreamGenerator(
  llmService: LLMService,
  request: any
): AsyncGenerator<{ text: string; done: boolean }, void, unknown> {
  const chunks: Array<{ text: string; done: boolean }> = []
  let streamComplete = false
  let streamError: Error | null = null
  
  // Start streaming
  llmService.streamChatCompletion(
    request,
    (chunk) => {
      chunks.push({ text: chunk.text, done: chunk.done || false })
      if (chunk.done) {
        streamComplete = true
      }
    }
  )
  
  // Yield chunks as they arrive
  while (!streamComplete || chunks.length > 0) {
    if (chunks.length > 0) {
      const chunk = chunks.shift()!
      yield chunk
      if (chunk.done) {
        break
      }
    } else {
      // Wait a bit for more chunks
      await new Promise(resolve => setTimeout(resolve, 10))
    }
  }
  
  if (streamError) {
    throw streamError
  }
}

