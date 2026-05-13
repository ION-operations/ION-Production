/**
 * Error Correction Service
 * Phase 4 Week 18: Socratic Gate & Error Correction
 * 
 * Implements:
 * - CAS integration for error detection
 * - Factual consistency checking
 * - Self-contradiction detection
 * - Code validity checking
 */

import { CASService } from '../CASService'
import { LLMService } from '../lucid-chat/llm/LLMService'
import { getActiveModel } from '../../config/modelRegistry'
import type { 
  ChatIntent, 
  ChatMode, 
  DraftResponse,
  Correction
} from '../../types/aetherChatTypes'

const casService = new CASService()
const llmService = new LLMService()

/**
 * Error detection result
 */
export interface ErrorDetectionResult {
  hasErrors: boolean
  corrections: Correction[]
  errorTypes: Array<'factual' | 'contradiction' | 'code' | 'logical' | 'other'>
  confidence: number
}

/**
 * Detect and correct errors in response
 */
export async function detectAndCorrectErrors(
  intent: ChatIntent,
  mode: ChatMode,
  draft: DraftResponse,
  responseText: string,
  conversationHistory: Array<{ role: string; content: string }>
): Promise<ErrorDetectionResult> {
  const corrections: Correction[] = []
  const errorTypes: Array<'factual' | 'contradiction' | 'code' | 'logical' | 'other'> = []
  
  try {
    // 1. CAS error detection
    const casErrors = await detectCASErrors(responseText, intent)
    if (casErrors.length > 0) {
      corrections.push(...casErrors)
      errorTypes.push('factual', 'logical')
    }
    
    // 2. Factual consistency checking
    const factualErrors = await checkFactualConsistency(responseText, conversationHistory)
    if (factualErrors.length > 0) {
      corrections.push(...factualErrors)
      if (!errorTypes.includes('factual')) errorTypes.push('factual')
    }
    
    // 3. Self-contradiction detection
    const contradictionErrors = await detectSelfContradictions(responseText)
    if (contradictionErrors.length > 0) {
      corrections.push(...contradictionErrors)
      if (!errorTypes.includes('contradiction')) errorTypes.push('contradiction')
    }
    
    // 4. Code validity checking (if intent involves code)
    if (intent === 'code_edit' || intent === 'code_review' || intent === 'debug') {
      const codeErrors = await checkCodeValidity(responseText)
      if (codeErrors.length > 0) {
        corrections.push(...codeErrors)
        if (!errorTypes.includes('code')) errorTypes.push('code')
      }
    }
    
    return {
      hasErrors: corrections.length > 0,
      corrections,
      errorTypes: [...new Set(errorTypes)],
      confidence: corrections.length > 0 ? 0.8 : 0.95
    }
  } catch (error) {
    console.warn('[Error Correction] Detection failed:', error)
    return {
      hasErrors: false,
      corrections: [],
      errorTypes: [],
      confidence: 0.5
    }
  }
}

/**
 * Detect errors using CAS
 */
async function detectCASErrors(
  responseText: string,
  intent: ChatIntent
): Promise<Correction[]> {
  try {
    // CAS Service currently doesn't have checkSafety method
    // Use pattern-based safety checks as fallback
    // TODO: Add checkSafety method to CASService when CAS MCP tool is available
    
    const corrections: Correction[] = []
    
    // Check for potentially harmful patterns
    const harmfulPatterns = [
      { pattern: /rm\s+-rf\s+\//, type: 'error' as const, reason: 'Potentially destructive command detected' },
      { pattern: /eval\s*\(/, type: 'warning' as const, reason: 'Code execution via eval() may be unsafe' },
      { pattern: /exec\s*\(/, type: 'warning' as const, reason: 'Code execution via exec() may be unsafe' },
      { pattern: /dangerouslySetInnerHTML/, type: 'warning' as const, reason: 'React dangerouslySetInnerHTML may introduce XSS' }
    ]
    
    for (const { pattern, type, reason } of harmfulPatterns) {
      if (pattern.test(responseText)) {
        corrections.push({
          type,
          location: 'response',
          original: 'Potentially unsafe code pattern detected',
          corrected: 'Review this code carefully before executing',
          reason
        })
      }
    }
    
    return corrections
  } catch (error) {
    console.warn('[Error Correction] CAS error detection failed:', error)
  }
  
  return []
}

/**
 * Check factual consistency with conversation history
 */
async function checkFactualConsistency(
  responseText: string,
  conversationHistory: Array<{ role: string; content: string }>
): Promise<Correction[]> {
  if (conversationHistory.length === 0) {
    return []
  }

  try {
    const model = getActiveModel('other', 'Speed', 0.7, 500)
    if (!model) {
      return []
    }

    const systemPrompt = `You are a factual consistency checker. Compare the new response with the conversation history and identify any factual contradictions or inconsistencies.

Respond with JSON:
{
  "inconsistencies": [
    {
      "original": "text from response that contradicts history",
      "corrected": "corrected version",
      "reason": "explanation of the contradiction"
    }
  ]
}`

    const historySummary = conversationHistory
      .slice(-5) // Last 5 messages
      .map(m => `${m.role}: ${m.content.substring(0, 200)}`)
      .join('\n')

    const userPrompt = `Conversation history:\n${historySummary}\n\nNew response:\n${responseText.substring(0, 500)}\n\nFind any factual inconsistencies.`

    const response = await llmService.chatCompletion({
      provider: model.provider as any,
      model: model.model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.3,
      maxTokens: 400
    })

    try {
      const jsonMatch = response.text.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0])
        if (parsed.inconsistencies && Array.isArray(parsed.inconsistencies)) {
          return parsed.inconsistencies.map((inc: any) => ({
            type: 'warning' as const,
            location: 'response',
            original: inc.original || '',
            corrected: inc.corrected || '',
            reason: inc.reason || 'Factual inconsistency detected'
          }))
        }
      }
    } catch (parseError) {
      console.warn('[Error Correction] Failed to parse consistency check response:', parseError)
    }
  } catch (error) {
    console.warn('[Error Correction] Factual consistency check failed:', error)
  }

  return []
}

/**
 * Detect self-contradictions within the response
 */
async function detectSelfContradictions(responseText: string): Promise<Correction[]> {
  try {
    const model = getActiveModel('other', 'Speed', 0.7, 400)
    if (!model) {
      return []
    }

    const systemPrompt = `You are a contradiction detector. Analyze the text and identify any self-contradictions or conflicting statements.

Respond with JSON:
{
  "contradictions": [
    {
      "original": "contradictory text",
      "corrected": "resolved version",
      "reason": "explanation of the contradiction"
    }
  ]
}`

    const userPrompt = `Analyze this text for self-contradictions:\n\n${responseText.substring(0, 1000)}`

    const response = await llmService.chatCompletion({
      provider: model.provider as any,
      model: model.model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.3,
      maxTokens: 300
    })

    try {
      const jsonMatch = response.text.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0])
        if (parsed.contradictions && Array.isArray(parsed.contradictions)) {
          return parsed.contradictions.map((cont: any) => ({
            type: 'warning' as const,
            location: 'response',
            original: cont.original || '',
            corrected: cont.corrected || '',
            reason: cont.reason || 'Self-contradiction detected'
          }))
        }
      }
    } catch (parseError) {
      console.warn('[Error Correction] Failed to parse contradiction check response:', parseError)
    }
  } catch (error) {
    console.warn('[Error Correction] Self-contradiction detection failed:', error)
  }

  return []
}

/**
 * Check code validity (syntax, common errors)
 */
async function checkCodeValidity(responseText: string): Promise<Correction[]> {
  const corrections: Correction[] = []
  
  // Extract code blocks
  const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g
  const codeBlocks: Array<{ language?: string; code: string }> = []
  let match
  
  while ((match = codeBlockRegex.exec(responseText)) !== null) {
    codeBlocks.push({
      language: match[1],
      code: match[2]
    })
  }
  
  // Basic code validation (syntax checking would require language-specific parsers)
  for (const block of codeBlocks) {
    // Check for common issues
    if (block.code.includes('undefined') && !block.code.includes('typeof')) {
      corrections.push({
        type: 'warning',
        location: 'code_block',
        original: 'Potential undefined variable usage',
        corrected: 'Consider checking for undefined before use',
        reason: 'Code may reference undefined variables'
      })
    }
    
    // Check for unclosed brackets/parentheses (simple check)
    const openBraces = (block.code.match(/\{/g) || []).length
    const closeBraces = (block.code.match(/\}/g) || []).length
    if (openBraces !== closeBraces) {
      corrections.push({
        type: 'error',
        location: 'code_block',
        original: 'Unmatched braces',
        corrected: 'Check for missing opening or closing braces',
        reason: `Found ${openBraces} opening braces but ${closeBraces} closing braces`
      })
    }
    
    const openParens = (block.code.match(/\(/g) || []).length
    const closeParens = (block.code.match(/\)/g) || []).length
    if (openParens !== closeParens) {
      corrections.push({
        type: 'error',
        location: 'code_block',
        original: 'Unmatched parentheses',
        corrected: 'Check for missing opening or closing parentheses',
        reason: `Found ${openParens} opening parentheses but ${closeParens} closing parentheses`
      })
    }
  }
  
  return corrections
}

