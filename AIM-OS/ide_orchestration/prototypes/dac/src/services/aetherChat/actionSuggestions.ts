/**
 * Action Suggestions Service
 * Phase 4 Week 17: Action Suggestions & Follow-ups
 * 
 * Implements:
 * - SEG integration for related concept finding
 * - APOE next step recommendations
 * - Action suggestion formatting
 * - Action execution hooks
 */

import { SEGService } from '../SEGService'
import { APOEService } from '../APOEService'
import { LLMService } from '../lucid-chat/llm/LLMService'
import { getActiveModel } from '../../config/modelRegistry'
import type { 
  ChatIntent, 
  ChatMode, 
  ContextWeb, 
  EvidencePack, 
  DraftResponse,
  SuggestedAction 
} from '../../types/aetherChatTypes'

const segService = new SEGService()
const apoeService = new APOEService()
const llmService = new LLMService()

/**
 * Generate action suggestions using SEG and APOE
 */
export async function generateActionSuggestions(
  intent: ChatIntent,
  mode: ChatMode,
  contextWeb: ContextWeb,
  evidencePack: EvidencePack,
  draft: DraftResponse,
  conversationHistory: Array<{ role: string; content: string }>
): Promise<SuggestedAction[]> {
  const actions: SuggestedAction[] = []

  try {
    // 1. Get related concepts from SEG
    const relatedConcepts = await findRelatedConcepts(contextWeb, evidencePack)
    
    // 2. Get APOE next step recommendations
    const apoeRecommendations = await getAPOENextSteps(intent, mode, draft, conversationHistory)
    
    // 3. Generate LLM-based action suggestions
    const llmSuggestions = await generateLLMActionSuggestions(
      intent,
      mode,
      draft,
      relatedConcepts,
      apoeRecommendations
    )
    
    // 4. Combine and rank all suggestions
    const allSuggestions = [
      ...(draft.actions || []).map(action => ({
        type: mapActionType(action.type),
        description: action.description,
        target: action.target,
        priority: 'medium' as const,
        source: 'draft' as const
      })),
      ...apoeRecommendations.map(rec => ({
        type: rec.type,
        description: rec.description,
        target: rec.target,
        priority: rec.priority,
        source: 'apoe' as const
      })),
      ...llmSuggestions.map(sug => ({
        type: sug.type,
        description: sug.description,
        target: sug.target,
        priority: sug.priority,
        source: 'llm' as const
      }))
    ]
    
    // 5. Deduplicate and rank by priority and relevance
    const rankedActions = rankAndDeduplicateActions(allSuggestions, intent, mode)
    
    return rankedActions.slice(0, 5) // Top 5 actions
  } catch (error) {
    console.warn('[Action Suggestions] Generation failed, using fallback:', error)
    // Fallback: use draft actions only
    return (draft.actions || []).slice(0, 3).map(action => ({
      type: mapActionType(action.type),
      description: action.description,
      target: action.target,
      priority: 'medium' as const
    }))
  }
}

/**
 * Find related concepts using SEG
 */
async function findRelatedConcepts(
  contextWeb: ContextWeb,
  evidencePack: EvidencePack
): Promise<Array<{ concept: string; relevance: number; source: string }>> {
  try {
    // Extract key concepts from context web nodes
    const concepts = contextWeb.nodes
      .filter(node => node.importance > 0.5)
      .map(node => ({
        concept: node.label,
        relevance: node.relevance || 0.5,
        source: 'context_web'
      }))
    
    // Extract concepts from evidence
    const evidenceConcepts = evidencePack.items
      .filter(item => item.trust > 0.6)
      .map(item => ({
        concept: item.excerpt.substring(0, 50), // First 50 chars as concept
        relevance: item.trust,
        source: 'evidence'
      }))
    
    // Use SEG to find related concepts
    const allConcepts = [...concepts, ...evidenceConcepts]
    const related: Array<{ concept: string; relevance: number; source: string }> = []
    
    for (const concept of allConcepts.slice(0, 5)) { // Limit to 5 concepts
      try {
        const segResult = await segService.synthesizeKnowledge(concept.concept, 3)
        if (segResult.success && segResult.entities) {
          segResult.entities.forEach(entity => {
            related.push({
              concept: entity.label || entity.id,
              relevance: concept.relevance * 0.8, // Slightly lower relevance for related
              source: 'seg'
            })
          })
        }
      } catch (error) {
        console.warn(`[Action Suggestions] SEG query failed for concept "${concept.concept}":`, error)
      }
    }
    
    return [...allConcepts, ...related]
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, 10) // Top 10 concepts
  } catch (error) {
    console.warn('[Action Suggestions] Related concept finding failed:', error)
    return []
  }
}

/**
 * Get APOE next step recommendations
 */
async function getAPOENextSteps(
  intent: ChatIntent,
  mode: ChatMode,
  draft: DraftResponse,
  conversationHistory: Array<{ role: string; content: string }>
): Promise<Array<{
  type: SuggestedAction['type']
  description: string
  target?: string
  priority: 'low' | 'medium' | 'high'
}>> {
  try {
    // Use APOE to generate next steps based on current response
    const nextStepsQuery = `Based on the response: "${draft.userFacingText.substring(0, 200)}", what are the logical next steps?`
    
    const apoePlan = await apoeService.createPlan({
      goal: `Generate next steps for ${intent} task`,
      context: {
        intent,
        mode,
        currentResponse: draft.userFacingText.substring(0, 500),
        conversationLength: conversationHistory.length
      },
      constraints: {
        maxSteps: 3,
        priority: 'medium'
      }
    })
    
    if (apoePlan.success && apoePlan.plan) {
      return apoePlan.plan.steps
        .slice(0, 3) // Top 3 steps
        .map(step => ({
          type: inferActionType(step.action),
          description: step.action,
          target: step.target,
          priority: step.priority || 'medium'
        }))
    }
  } catch (error) {
    console.warn('[Action Suggestions] APOE next steps failed:', error)
  }
  
  return []
}

/**
 * Generate LLM-based action suggestions
 */
async function generateLLMActionSuggestions(
  intent: ChatIntent,
  mode: ChatMode,
  draft: DraftResponse,
  relatedConcepts: Array<{ concept: string; relevance: number; source: string }>,
  apoeRecommendations: Array<{ type: SuggestedAction['type']; description: string; target?: string; priority: 'low' | 'medium' | 'high' }>
): Promise<Array<{
  type: SuggestedAction['type']
  description: string
  target?: string
  priority: 'low' | 'medium' | 'high'
}>> {
  const model = getActiveModel(intent, mode, 0.7, 1000)
  
  if (!model) {
    return []
  }

  try {
    const systemPrompt = `You are an action suggestion system. Based on the user's intent and the AI's response, suggest 2-3 logical next actions.

Action types:
- code_edit: Edit or modify code
- test: Run tests or validate code
- refactor: Refactor or restructure code
- documentation: Write or update documentation
- other: Other actions

Respond with JSON:
{
  "actions": [
    {
      "type": "code_edit" | "test" | "refactor" | "documentation" | "other",
      "description": "clear action description",
      "target": "optional file or target",
      "priority": "low" | "medium" | "high"
    }
  ]
}`

    const userPrompt = `Intent: ${intent}
Mode: ${mode}

Response: ${draft.userFacingText.substring(0, 500)}

Related concepts: ${relatedConcepts.slice(0, 5).map(c => c.concept).join(', ')}

APOE recommendations: ${apoeRecommendations.map(r => r.description).join(', ')}

Suggest 2-3 logical next actions.`

    const response = await llmService.chatCompletion({
      provider: model.provider as any,
      model: model.model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.7,
      maxTokens: 500
    })

    try {
      const jsonMatch = response.text.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0])
        if (parsed.actions && Array.isArray(parsed.actions)) {
          return parsed.actions.map((action: any) => ({
            type: action.type || 'other',
            description: action.description || 'Action',
            target: action.target,
            priority: action.priority || 'medium'
          }))
        }
      }
    } catch (parseError) {
      console.warn('[Action Suggestions] Failed to parse LLM response:', parseError)
    }
  } catch (error) {
    console.warn('[Action Suggestions] LLM suggestion generation failed:', error)
  }

  return []
}

/**
 * Map action type from draft to SuggestedAction type
 */
function mapActionType(
  type: string
): SuggestedAction['type'] {
  if (type === 'code_edit' || type === 'file_edit') return 'code_edit'
  if (type === 'test_run' || type === 'test') return 'test'
  if (type === 'file_create' || type === 'file_delete' || type === 'refactor') return 'refactor'
  if (type === 'documentation' || type === 'doc') return 'documentation'
  return 'other'
}

/**
 * Infer action type from action description
 */
function inferActionType(action: string): SuggestedAction['type'] {
  const lower = action.toLowerCase()
  if (lower.includes('test') || lower.includes('run') || lower.includes('validate')) return 'test'
  if (lower.includes('refactor') || lower.includes('restructure') || lower.includes('reorganize')) return 'refactor'
  if (lower.includes('document') || lower.includes('doc') || lower.includes('write')) return 'documentation'
  if (lower.includes('edit') || lower.includes('modify') || lower.includes('change') || lower.includes('code')) return 'code_edit'
  return 'other'
}

/**
 * Rank and deduplicate actions
 */
function rankAndDeduplicateActions(
  actions: Array<SuggestedAction & { source?: string }>,
  intent: ChatIntent,
  mode: ChatMode
): SuggestedAction[] {
  // Priority weights
  const priorityWeights = {
    high: 3,
    medium: 2,
    low: 1
  }
  
  // Source weights (prefer APOE > LLM > draft)
  const sourceWeights = {
    apoe: 3,
    llm: 2,
    draft: 1
  }
  
  // Deduplicate by description similarity
  const uniqueActions: SuggestedAction[] = []
  const seenDescriptions = new Set<string>()
  
  for (const action of actions) {
    const normalizedDesc = action.description.toLowerCase().trim()
    
    // Check if similar description already exists
    const isDuplicate = Array.from(seenDescriptions).some(seen => {
      const similarity = calculateSimilarity(normalizedDesc, seen)
      return similarity > 0.8 // 80% similarity threshold
    })
    
    if (!isDuplicate) {
      seenDescriptions.add(normalizedDesc)
      uniqueActions.push({
        type: action.type,
        description: action.description,
        target: action.target,
        priority: action.priority
      })
    }
  }
  
  // Rank by priority and source
  return uniqueActions.sort((a, b) => {
    const aScore = priorityWeights[a.priority] * (sourceWeights[(a as any).source || 'draft'] || 1)
    const bScore = priorityWeights[b.priority] * (sourceWeights[(b as any).source || 'draft'] || 1)
    return bScore - aScore
  })
}

/**
 * Calculate similarity between two strings (simple word overlap)
 */
function calculateSimilarity(str1: string, str2: string): number {
  const words1 = new Set(str1.split(/\s+/).filter(w => w.length > 2))
  const words2 = new Set(str2.split(/\s+/).filter(w => w.length > 2))
  
  const intersection = Array.from(words1).filter(w => words2.has(w))
  const union = new Set([...words1, ...words2])
  
  return union.size > 0 ? intersection.length / union.size : 0
}

