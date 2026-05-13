/**
 * Ambiguity Detection Service
 * LLM-based ambiguity analysis for Aether Chat
 * 
 * Phase 1: Enhanced Pre-Processing Pipeline
 */

import { LLMService } from '../lucid-chat/llm/LLMService'
import { getActiveModel } from '../../config/modelRegistry'
import type { EnrichedContext, AmbiguityState } from '../../types/aetherChatTypes'

const llmService = new LLMService()

/**
 * Detect ambiguity in user message using LLM
 */
export async function detectAmbiguityLLM(
  message: string,
  enrichedContext: EnrichedContext,
  conversationHistory: Array<{ role: string; content: string }> = []
): Promise<AmbiguityState> {
  try {
    // Select appropriate model for ambiguity detection (fast tier)
    const model = getActiveModel('ask_explain', 'simple', 0.01, 1000)
    
    if (!model) {
      // Fallback to simple detection
      return detectAmbiguitySimple(message, enrichedContext)
    }

    // Build context summary for LLM
    const contextSummary = enrichedContext.hhniResults.length > 0
      ? `Found ${enrichedContext.hhniResults.length} related contexts:\n` +
        enrichedContext.hhniResults.slice(0, 3).map((r, i) => 
          `${i + 1}. ${r.title || r.domain}: ${r.content.substring(0, 100)}...`
        ).join('\n')
      : 'No related contexts found.'

    // Build prompt for ambiguity detection
    const systemPrompt = `You are an ambiguity detection system for an AI chat interface. Analyze the user's message and determine if it's ambiguous (could have multiple interpretations).

An ambiguous message:
- Has multiple valid interpretations
- Lacks sufficient context to determine intent
- Could refer to multiple things/concepts
- Requires clarification to answer accurately

Respond with JSON:
{
  "isAmbiguous": true/false,
  "ambiguityScore": 0.0-1.0,
  "interpretations": [
    {
      "intent": "description of interpretation",
      "confidence": 0.0-1.0,
      "supportingEvidence": ["evidence1", "evidence2"]
    }
  ],
  "clarificationQuestion": "question to ask user if ambiguous"
}`

    const userPrompt = `Message: "${message}"

${conversationHistory.length > 0 ? `\nRecent conversation:\n${conversationHistory.slice(-3).map(m => `${m.role}: ${m.content}`).join('\n')}` : ''}

${contextSummary}

Is this message ambiguous? If yes, what are the possible interpretations?`

    // Call LLM
    const response = await llmService.chatCompletion({
      provider: model.provider as any,
      model: model.model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.3, // Low temperature for analysis
      maxTokens: 300
    })

    // Parse JSON response
    try {
      const jsonMatch = response.text.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0])
        
        if (parsed.isAmbiguous && parsed.interpretations && parsed.interpretations.length > 1) {
          return {
            isAmbiguous: true,
            ambiguityScore: parsed.ambiguityScore || 0.7,
            interpretations: parsed.interpretations.map((interp: any, index: number) => ({
              intent: interp.intent || `Interpretation ${index + 1}`,
              confidence: {
                value: interp.confidence || 0.6,
                band: interp.confidence >= 0.8 ? 'A' as const :
                      interp.confidence >= 0.7 ? 'B' as const : 'C' as const
              },
              supportingEvidence: interp.supportingEvidence || []
            })),
            forkedPathUI: {
              question: parsed.clarificationQuestion || "I see multiple potential interpretations. Which one?",
              options: parsed.interpretations.map((i: any) => i.intent || `Option ${parsed.interpretations.indexOf(i) + 1}`)
            }
          }
        }
      }
    } catch (parseError) {
      console.warn('[AmbiguityDetection] Failed to parse LLM response, using fallback:', parseError)
    }

    // Fallback to simple detection
    return detectAmbiguitySimple(message, enrichedContext)
  } catch (error) {
    console.error('[AmbiguityDetection] LLM analysis failed, using fallback:', error)
    return detectAmbiguitySimple(message, enrichedContext)
  }
}

/**
 * Simple ambiguity detection (fallback)
 */
export function detectAmbiguitySimple(
  message: string,
  enrichedContext: EnrichedContext
): AmbiguityState {
  // Check for multiple similar contexts
  if (enrichedContext.hhniResults.length >= 3 && 
      enrichedContext.hhniResults.filter(r => r.relevanceScore > 0.7).length >= 3) {
    // High ambiguity - multiple similar contexts
    const interpretations = enrichedContext.hhniResults
      .slice(0, 3)
      .map((result, index) => ({
        intent: result.title || `Interpretation ${index + 1}`,
        confidence: {
          value: result.relevanceScore,
          band: result.relevanceScore >= 0.8 ? 'A' as const :
                result.relevanceScore >= 0.7 ? 'B' as const : 'C' as const
        },
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
  
  // Check for vague language
  const vagueWords = ['it', 'this', 'that', 'they', 'them', 'here', 'there']
  const vagueCount = vagueWords.filter(word => 
    message.toLowerCase().includes(` ${word} `) || 
    message.toLowerCase().startsWith(`${word} `) ||
    message.toLowerCase().endsWith(` ${word}`)
  ).length
  
  if (vagueCount >= 2 && enrichedContext.sourceCount === 0) {
    return {
      isAmbiguous: true,
      ambiguityScore: 0.6,
      interpretations: [{
        intent: 'Unclear reference',
        confidence: { value: 0.5, band: 'C' as const },
        supportingEvidence: []
      }],
      forkedPathUI: {
        question: "I need clarification. What does 'it' or 'this' refer to?",
        options: ['Previous message', 'A specific file', 'A concept we discussed', 'Something else']
      }
    }
  }
  
  return {
    isAmbiguous: false,
    ambiguityScore: 0.2,
    interpretations: []
  }
}

