/**
 * Intent Analysis Service
 * LLM-based intent classification for Aether Chat
 * 
 * Phase 1: Enhanced Pre-Processing Pipeline
 */

import { LLMService } from '../lucid-chat/llm/LLMService'
import { getActiveModel } from '../../config/modelRegistry'
import type { ChatIntent, ChatMode, RawUserTurn } from '../../types/aetherChatTypes'

const llmService = new LLMService()

/**
 * Analyze user intent using LLM
 */
export async function analyzeIntentLLM(
  message: string,
  conversationHistory: Array<{ role: string; content: string }> = []
): Promise<{
  intent: ChatIntent
  mode: ChatMode
  confidence: number
  reasoning?: string
}> {
  try {
    // Select appropriate model for intent analysis (fast tier)
    const model = getActiveModel('ask_explain', 'simple', 0.01, 1000)
    
    if (!model) {
      // Fallback to pattern matching
      return analyzeIntentPattern(message)
    }

    // Build prompt for intent analysis
    const systemPrompt = `You are an intent classification system for an AI chat interface. Analyze the user's message and classify their intent.

Available intents:
- ask_explain: User wants explanation or information
- code_edit: User wants to edit, modify, or create code
- debug_error: User is debugging an error or issue
- design_arch: User wants architectural design or system design
- meta_chat: User wants to chat about the chat system itself
- planning: User wants planning, strategy, or roadmap
- other: Other intents not covered above

Available modes:
- fast: Simple questions, quick responses
- deep: Complex reasoning, architectural questions
- research: Information gathering, explanation requests
- surgical: Code editing, debugging, precise changes

Respond with JSON:
{
  "intent": "one of the intents above",
  "mode": "one of the modes above",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation of why this intent/mode"
}`

    const userPrompt = `Message: "${message}"

${conversationHistory.length > 0 ? `\nRecent conversation:\n${conversationHistory.slice(-3).map(m => `${m.role}: ${m.content}`).join('\n')}` : ''}

Classify the intent and mode.`

    // Call LLM
    const response = await llmService.chatCompletion({
      provider: model.provider as any,
      model: model.model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.3, // Low temperature for classification
      maxTokens: 200
    })

    // Parse JSON response
    try {
      const jsonMatch = response.text.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0])
        return {
          intent: parsed.intent as ChatIntent || 'other',
          mode: parsed.mode as ChatMode || 'fast',
          confidence: parsed.confidence || 0.7,
          reasoning: parsed.reasoning
        }
      }
    } catch (parseError) {
      console.warn('[IntentAnalysis] Failed to parse LLM response, using fallback:', parseError)
    }

    // Fallback to pattern matching
    return analyzeIntentPattern(message)
  } catch (error) {
    console.error('[IntentAnalysis] LLM analysis failed, using fallback:', error)
    return analyzeIntentPattern(message)
  }
}

/**
 * Pattern-based intent analysis (fallback)
 */
export function analyzeIntentPattern(message: string): {
  intent: ChatIntent
  mode: ChatMode
  confidence: number
} {
  const lower = message.toLowerCase()
  
  // Intent classification
  let intent: ChatIntent = 'other'
  let confidence = 0.6
  
  if (lower.includes('fix') || lower.includes('bug') || lower.includes('error') || lower.includes('broken')) {
    intent = 'debug_error'
    confidence = 0.8
  } else if (lower.includes('how') || lower.includes('explain') || lower.includes('what') || lower.includes('why')) {
    intent = 'ask_explain'
    confidence = 0.75
  } else if (lower.includes('design') || lower.includes('architecture') || lower.includes('structure') || lower.includes('system design')) {
    intent = 'design_arch'
    confidence = 0.8
  } else if (lower.includes('plan') || lower.includes('strategy') || lower.includes('roadmap') || lower.includes('timeline')) {
    intent = 'planning'
    confidence = 0.75
  } else if (lower.includes('edit') || lower.includes('change') || lower.includes('update') || lower.includes('modify') || lower.includes('create') || lower.includes('write code')) {
    intent = 'code_edit'
    confidence = 0.8
  } else if (lower.includes('chat') || lower.includes('talk') || lower.includes('conversation') || lower.includes('help')) {
    intent = 'meta_chat'
    confidence = 0.7
  }
  
  // Mode classification
  let mode: ChatMode = 'fast'
  if (intent === 'code_edit' || intent === 'debug_error') {
    mode = 'surgical'
  } else if (intent === 'design_arch' || intent === 'planning') {
    mode = 'deep'
  } else if (intent === 'ask_explain') {
    mode = 'research'
  }
  
  return { intent, mode, confidence }
}

/**
 * Enhanced context query generation based on intent
 */
export function generateContextQueries(
  message: string,
  intent: ChatIntent,
  mode: ChatMode
): string[] {
  const queries: string[] = [message] // Always include original message
  
  // Add intent-specific queries
  switch (intent) {
    case 'code_edit':
      queries.push(`code implementation ${message}`)
      queries.push(`programming ${message}`)
      break
    case 'debug_error':
      queries.push(`error debugging ${message}`)
      queries.push(`troubleshooting ${message}`)
      break
    case 'design_arch':
      queries.push(`system architecture ${message}`)
      queries.push(`design patterns ${message}`)
      break
    case 'planning':
      queries.push(`project planning ${message}`)
      queries.push(`strategy ${message}`)
      break
    case 'ask_explain':
      queries.push(`explanation ${message}`)
      queries.push(`how does ${message}`)
      break
  }
  
  return queries
}

