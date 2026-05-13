/**
 * Follow-up Questions Service
 * Phase 4 Week 17: Action Suggestions & Follow-ups
 * 
 * Implements:
 * - Follow-up question generation
 * - Conversation pattern analysis
 * - Generate 2-3 follow-up suggestions
 * - Follow-up question formatting
 */

import { LLMService } from '../lucid-chat/llm/LLMService'
import { getActiveModel } from '../../config/modelRegistry'
import type { 
  ChatIntent, 
  ChatMode, 
  ContextWeb, 
  EvidencePack,
  DraftResponse
} from '../../types/aetherChatTypes'

const llmService = new LLMService()

/**
 * Generate follow-up questions based on conversation patterns and context
 */
export async function generateFollowUpQuestions(
  intent: ChatIntent,
  mode: ChatMode,
  draft: DraftResponse,
  contextWeb: ContextWeb,
  evidencePack: EvidencePack,
  conversationHistory: Array<{ role: string; content: string }>
): Promise<string[]> {
  try {
    // 1. Analyze conversation patterns
    const patterns = analyzeConversationPatterns(conversationHistory, intent)
    
    // 2. Generate LLM-based follow-up questions
    const llmQuestions = await generateLLMFollowUps(
      intent,
      mode,
      draft,
      contextWeb,
      evidencePack,
      patterns
    )
    
    // 3. Generate pattern-based follow-ups
    const patternQuestions = generatePatternBasedFollowUps(intent, mode, draft, patterns)
    
    // 4. Combine and rank questions
    const allQuestions = [...llmQuestions, ...patternQuestions]
    const rankedQuestions = rankAndDeduplicateQuestions(allQuestions)
    
    return rankedQuestions.slice(0, 3) // Top 3 follow-up questions
  } catch (error) {
    console.warn('[Follow-up Questions] Generation failed, using fallback:', error)
    // Fallback: basic questions based on intent
    return generateBasicFollowUps(intent, mode)
  }
}

/**
 * Analyze conversation patterns
 */
function analyzeConversationPatterns(
  conversationHistory: Array<{ role: string; content: string }>,
  intent: ChatIntent
): {
  depth: 'shallow' | 'medium' | 'deep'
  topicConsistency: number // 0-1
  questionTypes: string[]
  averageLength: number
} {
  if (conversationHistory.length === 0) {
    return {
      depth: 'shallow',
      topicConsistency: 0.5,
      questionTypes: [],
      averageLength: 0
    }
  }
  
  const userMessages = conversationHistory.filter(m => m.role === 'user')
  const averageLength = userMessages.reduce((sum, m) => sum + m.content.length, 0) / userMessages.length
  
  // Analyze question types
  const questionTypes: string[] = []
  userMessages.forEach(msg => {
    if (msg.content.includes('how')) questionTypes.push('how')
    if (msg.content.includes('why')) questionTypes.push('why')
    if (msg.content.includes('what')) questionTypes.push('what')
    if (msg.content.includes('when')) questionTypes.push('when')
    if (msg.content.includes('where')) questionTypes.push('where')
  })
  
  // Determine depth based on conversation length and complexity
  const depth = conversationHistory.length < 3 ? 'shallow' :
                conversationHistory.length < 8 ? 'medium' : 'deep'
  
  // Calculate topic consistency (simple keyword overlap)
  let topicConsistency = 0.5
  if (userMessages.length >= 2) {
    const keywords1 = extractKeywords(userMessages[0].content)
    const keywords2 = extractKeywords(userMessages[userMessages.length - 1].content)
    const overlap = keywords1.filter(k => keywords2.includes(k)).length
    topicConsistency = overlap / Math.max(keywords1.length, keywords2.length, 1)
  }
  
  return {
    depth,
    topicConsistency,
    questionTypes: [...new Set(questionTypes)],
    averageLength
  }
}

/**
 * Extract keywords from text
 */
function extractKeywords(text: string): string[] {
  const words = text.toLowerCase()
    .split(/\s+/)
    .filter(w => w.length > 3)
    .filter(w => !['this', 'that', 'with', 'from', 'have', 'been', 'will', 'would', 'should', 'could'].includes(w))
  
  return [...new Set(words)].slice(0, 10) // Top 10 unique keywords
}

/**
 * Generate LLM-based follow-up questions
 */
async function generateLLMFollowUps(
  intent: ChatIntent,
  mode: ChatMode,
  draft: DraftResponse,
  contextWeb: ContextWeb,
  evidencePack: EvidencePack,
  patterns: ReturnType<typeof analyzeConversationPatterns>
): Promise<string[]> {
  const model = getActiveModel(intent, mode, 0.7, 800)
  
  if (!model) {
    return []
  }

  try {
    const systemPrompt = `You are a follow-up question generator. Based on the AI's response and conversation context, generate 2-3 natural, helpful follow-up questions.

Guidelines:
- Questions should be specific and actionable
- Build on the current response
- Explore related concepts or deeper understanding
- Match the conversation depth (shallow/medium/deep)

Respond with JSON:
{
  "questions": [
    "question 1",
    "question 2",
    "question 3"
  ]
}`

    const userPrompt = `Intent: ${intent}
Mode: ${mode}
Conversation depth: ${patterns.depth}
Topic consistency: ${(patterns.topicConsistency * 100).toFixed(0)}%

Current response: ${draft.userFacingText.substring(0, 500)}

Context topics: ${contextWeb.nodes.slice(0, 5).map(n => n.label).join(', ')}

Evidence count: ${evidencePack.items.length}

Generate 2-3 follow-up questions that would help the user continue the conversation.`

    const response = await llmService.chatCompletion({
      provider: model.provider as any,
      model: model.model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.8,
      maxTokens: 400
    })

    try {
      const jsonMatch = response.text.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0])
        if (parsed.questions && Array.isArray(parsed.questions)) {
          return parsed.questions.filter((q: any) => typeof q === 'string' && q.length > 10)
        }
      }
    } catch (parseError) {
      console.warn('[Follow-up Questions] Failed to parse LLM response:', parseError)
    }
  } catch (error) {
    console.warn('[Follow-up Questions] LLM generation failed:', error)
  }

  return []
}

/**
 * Generate pattern-based follow-up questions
 */
function generatePatternBasedFollowUps(
  intent: ChatIntent,
  mode: ChatMode,
  draft: DraftResponse,
  patterns: ReturnType<typeof analyzeConversationPatterns>
): string[] {
  const questions: string[] = []
  
  // Intent-specific questions
  switch (intent) {
    case 'ask_explain':
      questions.push('Can you explain this in more detail?')
      questions.push('What are the key concepts here?')
      if (patterns.depth === 'deep') {
        questions.push('How does this relate to other concepts we\'ve discussed?')
      }
      break
      
    case 'code_edit':
      questions.push('Should I test this change?')
      questions.push('Are there any edge cases to consider?')
      if (patterns.depth === 'deep') {
        questions.push('How does this affect the overall architecture?')
      }
      break
      
    case 'code_review':
      questions.push('Are there any performance concerns?')
      questions.push('Should I refactor this further?')
      break
      
    case 'debug':
      questions.push('What other debugging steps should I take?')
      questions.push('Could this be related to other issues?')
      break
      
    case 'design':
      questions.push('What are the trade-offs of this approach?')
      questions.push('Are there alternative designs to consider?')
      break
      
    default:
      questions.push('Is there anything else you\'d like to know?')
      questions.push('Would you like me to elaborate on any part?')
  }
  
  // Depth-based questions
  if (patterns.depth === 'shallow' && patterns.topicConsistency > 0.7) {
    questions.push('Would you like to dive deeper into this topic?')
  } else if (patterns.depth === 'deep') {
    questions.push('Should we explore a different aspect?')
  }
  
  return questions
}

/**
 * Generate basic follow-up questions (fallback)
 */
function generateBasicFollowUps(intent: ChatIntent, mode: ChatMode): string[] {
  switch (intent) {
    case 'ask_explain':
      return [
        'Can you explain this in more detail?',
        'What are the key concepts here?'
      ]
    case 'code_edit':
      return [
        'Should I test this change?',
        'Are there any edge cases to consider?'
      ]
    default:
      return [
        'Is there anything else you\'d like to know?',
        'Would you like me to elaborate?'
      ]
  }
}

/**
 * Rank and deduplicate questions
 */
function rankAndDeduplicateQuestions(questions: string[]): string[] {
  // Remove duplicates (case-insensitive)
  const unique = new Map<string, string>()
  
  for (const question of questions) {
    const normalized = question.toLowerCase().trim()
    if (!unique.has(normalized) && question.length > 10) {
      unique.set(normalized, question)
    }
  }
  
  // Rank by length and question word presence (prefer questions with question words)
  const questionWords = ['what', 'how', 'why', 'when', 'where', 'which', 'who', 'should', 'could', 'would']
  
  return Array.from(unique.values()).sort((a, b) => {
    const aHasQuestionWord = questionWords.some(word => a.toLowerCase().includes(word))
    const bHasQuestionWord = questionWords.some(word => b.toLowerCase().includes(word))
    
    if (aHasQuestionWord && !bHasQuestionWord) return -1
    if (!aHasQuestionWord && bHasQuestionWord) return 1
    
    // Prefer medium-length questions (50-150 chars)
    const aLength = a.length
    const bLength = b.length
    const aOptimal = aLength >= 50 && aLength <= 150
    const bOptimal = bLength >= 50 && bLength <= 150
    
    if (aOptimal && !bOptimal) return -1
    if (!aOptimal && bOptimal) return 1
    
    return 0
  })
}

