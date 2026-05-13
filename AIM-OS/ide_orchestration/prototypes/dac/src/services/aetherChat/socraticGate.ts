/**
 * Socratic Gate Service
 * Phase 4 Week 18: Socratic Gate & Error Correction
 * 
 * Implements:
 * - User profile retrieval from CMC
 * - Preference detection (Speed vs. Mastery)
 * - Socratic hint generation
 * - Solution reveal UI (<details> tag)
 */

import { CMCService } from '../CMCService'
import { LLMService } from '../lucid-chat/llm/LLMService'
import { getActiveModel } from '../../config/modelRegistry'
import type { 
  ChatIntent, 
  ChatMode, 
  DraftResponse,
  SocraticReveal
} from '../../types/aetherChatTypes'

const cmcService = new CMCService()
const llmService = new LLMService()

/**
 * User profile from CMC
 */
export interface UserProfile {
  userId: string
  preference: {
    mode: 'Speed' | 'Mastery'
    confidence: number
    source: 'explicit' | 'implicit' | 'default'
  }
  learningStyle?: {
    prefersHints: boolean
    prefersExamples: boolean
    prefersStepByStep: boolean
  }
  metadata?: Record<string, any>
}

/**
 * Apply Socratic Gate to response
 * Returns SocraticReveal if user preference is Mastery, undefined otherwise
 */
export async function applySocraticGate(
  intent: ChatIntent,
  mode: ChatMode,
  draft: DraftResponse,
  userId: string,
  responseText: string
): Promise<SocraticReveal | undefined> {
  try {
    // 1. Retrieve user profile from CMC
    const userProfile = await retrieveUserProfile(userId)
    
    // 2. Determine if Socratic Gate should be applied
    const shouldApply = shouldApplySocraticGate(intent, userProfile)
    
    if (!shouldApply) {
      return undefined
    }
    
    // 3. Generate Socratic hint
    const hint = await generateSocraticHint(intent, mode, draft, userProfile)
    
    // 4. Generate solution reveal UI
    const solution = generateSolutionReveal(responseText, intent)
    
    return {
      hint,
      solution
    }
  } catch (error) {
    console.warn('[Socratic Gate] Failed to apply, using fallback:', error)
    // Fallback: basic Socratic Gate for Mastery mode
    if (intent === 'code_edit' || intent === 'ask_explain') {
      return {
        hint: 'Think about the structure and patterns you\'ve seen before.',
        solution: generateSolutionReveal(responseText, intent)
      }
    }
    return undefined
  }
}

/**
 * Retrieve user profile from CMC
 */
async function retrieveUserProfile(userId: string): Promise<UserProfile> {
  try {
    // Query CMC for user profile
    const result = await cmcService.retrieveAtoms(`user_profile:${userId}`, 1)
    
    if (result.success && result.atoms && result.atoms.length > 0) {
      const atom = result.atoms[0]
      const profile = atom.metadata?.profile || atom.content
      
      if (typeof profile === 'string') {
        try {
          const parsed = JSON.parse(profile)
          return {
            userId,
            preference: parsed.preference || {
              mode: 'Speed',
              confidence: 0.5,
              source: 'default'
            },
            learningStyle: parsed.learningStyle,
            metadata: parsed.metadata
          }
        } catch (parseError) {
          // Fallback: use default profile
        }
      } else if (typeof profile === 'object') {
        return {
          userId,
          preference: profile.preference || {
            mode: 'Speed',
            confidence: 0.5,
            source: 'default'
          },
          learningStyle: profile.learningStyle,
          metadata: profile.metadata
        }
      }
    }
  } catch (error) {
    console.warn(`[Socratic Gate] Failed to retrieve user profile for ${userId}:`, error)
  }
  
  // Default profile
  return {
    userId,
    preference: {
      mode: 'Speed',
      confidence: 0.5,
      source: 'default'
    }
  }
}

/**
 * Determine if Socratic Gate should be applied
 */
function shouldApplySocraticGate(
  intent: ChatIntent,
  userProfile: UserProfile
): boolean {
  // Only apply for Mastery mode
  if (userProfile.preference.mode !== 'Mastery') {
    return false
  }
  
  // Apply for specific intents that benefit from Socratic method
  const socraticIntents: ChatIntent[] = [
    'ask_explain',
    'code_edit',
    'design_arch',
    'planning'
  ]
  
  return socraticIntents.includes(intent)
}

/**
 * Generate Socratic hint
 */
async function generateSocraticHint(
  intent: ChatIntent,
  mode: ChatMode,
  draft: DraftResponse,
  userProfile: UserProfile
): Promise<string> {
  const model = getActiveModel(intent, mode, 0.7, 300)
  
  if (!model) {
    // Fallback: intent-based hints
    return getDefaultHint(intent)
  }

  try {
    const systemPrompt = `You are a Socratic teacher. Generate a helpful hint that guides the user toward the solution without revealing it directly.

Guidelines:
- Ask a leading question or suggest a direction
- Reference patterns or concepts they might know
- Encourage exploration and thinking
- Keep it concise (1-2 sentences)
- Match the user's learning style if known`

    const userPrompt = `Intent: ${intent}
User preference: ${userProfile.preference.mode}
Learning style: ${userProfile.learningStyle ? JSON.stringify(userProfile.learningStyle) : 'unknown'}

Response context: ${draft.userFacingText.substring(0, 300)}

Generate a Socratic hint that guides the user.`

    const response = await llmService.chatCompletion({
      provider: model.provider as any,
      model: model.model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.8,
      maxTokens: 150
    })

    const hint = response.text.trim()
    if (hint.length > 10 && hint.length < 200) {
      return hint
    }
  } catch (error) {
    console.warn('[Socratic Gate] LLM hint generation failed:', error)
  }

  // Fallback: default hint
  return getDefaultHint(intent)
}

/**
 * Get default hint based on intent
 */
function getDefaultHint(intent: ChatIntent): string {
  const hints: Record<ChatIntent, string> = {
    'ask_explain': 'Think about the key concepts and how they relate to each other.',
    'code_edit': 'Consider the structure and patterns you\'ve seen in similar code.',
    'code_review': 'Look for common patterns and potential improvements.',
    'debug': 'Think about what could cause this behavior. What changed recently?',
    'design': 'Consider the trade-offs and constraints. What are the requirements?',
    'design_arch': 'Think about the relationships between components and their responsibilities.',
    'meta_chat': 'Reflect on what you\'re trying to understand or accomplish.',
    'planning': 'Break down the goal into smaller, manageable steps.',
    'other': 'Think about what you\'re trying to achieve and what information would help.'
  }
  
  return hints[intent] || hints.other
}

/**
 * Generate solution reveal UI with <details> tag
 */
function generateSolutionReveal(responseText: string, intent: ChatIntent): string {
  // Extract code blocks if present
  const codeBlockRegex = /```[\s\S]*?```/g
  const codeBlocks = responseText.match(codeBlockRegex) || []
  
  if (codeBlocks.length > 0) {
    // If there are code blocks, show them in details
    const codeContent = codeBlocks.join('\n\n')
    return `<details><summary>Show solution</summary>\n\n${codeContent}\n\n</details>`
  } else {
    // Otherwise, show the full response
    return `<details><summary>Show solution</summary>\n\n${responseText}\n\n</details>`
  }
}

/**
 * Store user preference in CMC
 */
export async function storeUserPreference(
  userId: string,
  preference: UserProfile['preference'],
  learningStyle?: UserProfile['learningStyle']
): Promise<{ success: boolean; error?: string }> {
  try {
    const profile: UserProfile = {
      userId,
      preference,
      learningStyle,
      metadata: {
        updatedAt: new Date().toISOString()
      }
    }
    
    const result = await cmcService.storeAtom(
      JSON.stringify(profile),
      'text',
      { user_profile: 1.0, user_id: 1.0 },
      { profile, type: 'user_profile' }
    )
    
    if (result.success) {
      return { success: true }
    } else {
      return { success: false, error: result.error }
    }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    }
  }
}

