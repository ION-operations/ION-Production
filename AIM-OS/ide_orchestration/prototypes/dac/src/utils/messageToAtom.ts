// Message to SummaryAtom Migration and Significance Computation
// Part of AI Chat System Enhancement: Significance Scoring & Typed Relationships

import {
  SummaryAtom,
  Claim,
  Significance,
  SignificanceBreakdown,
  Relationship,
  RelationshipType,
  AtomLevel,
  extractSymbols,
  extractClaims,
  determineAtomLevel,
  generateTitle,
  computeSignificanceScore,
  computeRecency,
  computeNovelty,
  normalizeUsage
} from './summaryAtoms'
import { ChatMessage } from '../types/chatTypes'

// Track prior symbols for novelty computation
const priorSymbols = new Set<string>()

// Track message views and references for usage computation
const messageViews = new Map<string, number>()
const messageReferences = new Map<string, number>()
const messageToolCalls = new Map<string, number>()

// Initialize usage tracking for a message
export function initializeUsageTracking(messageId: string) {
  if (!messageViews.has(messageId)) {
    messageViews.set(messageId, 0)
  }
  if (!messageReferences.has(messageId)) {
    messageReferences.set(messageId, 0)
  }
  if (!messageToolCalls.has(messageId)) {
    messageToolCalls.set(messageId, 0)
  }
}

// Track message view
export function trackMessageView(messageId: string) {
  const current = messageViews.get(messageId) ?? 0
  messageViews.set(messageId, current + 1)
}

// Track message reference (by agent)
export function trackMessageReference(messageId: string) {
  const current = messageReferences.get(messageId) ?? 0
  messageReferences.set(messageId, current + 1)
}

// Track tool calls for a message
export function trackToolCalls(messageId: string, count: number) {
  const current = messageToolCalls.get(messageId) ?? 0
  messageToolCalls.set(messageId, current + count)
}

// Compute usage score from tracked metrics
function computeUsageScore(messageId: string): number {
  const views = messageViews.get(messageId) ?? 0
  const references = messageReferences.get(messageId) ?? 0
  const toolCalls = messageToolCalls.get(messageId) ?? 0
  
  // Combine metrics (weighted)
  const totalUsage = views * 1.0 + references * 2.0 + toolCalls * 1.5
  
  return normalizeUsage(totalUsage)
}

// Compute impact score from work references
function computeImpactScore(
  workReferences?: {
    files?: Array<{ path: string; operation?: string }>
  },
  goalAlignment?: {
    progress?: number
  }
): number {
  let impact = 0
  
  // Count test files (high impact)
  if (workReferences?.files) {
    const testFiles = workReferences.files.filter(f => 
      f.path.includes('test') || f.path.includes('spec') || f.path.includes('__tests__')
    ).length
    impact += testFiles * 0.3  // Each test file adds 0.3 impact
  }
  
  // Count file operations (medium impact)
  if (workReferences?.files) {
    const fileOps = workReferences.files.length
    impact += fileOps * 0.1  // Each file operation adds 0.1 impact
  }
  
  // Goal progress (high impact)
  if (goalAlignment?.progress) {
    impact += goalAlignment.progress * 0.5  // Progress adds up to 0.5 impact
  }
  
  return clamp01(impact)
}

function clamp01(n: number): number {
  return Math.max(0, Math.min(1, n))
}

// Compute significance breakdown for a message
export function computeSignificanceBreakdown(
  message: ChatMessage,
  priorSymbolsSet: Set<string> = new Set()
): SignificanceBreakdown {
  const messageId = message.id
  
  // Initialize tracking if needed
  initializeUsageTracking(messageId)
  
  // Track tool calls
  if (message.tool_calls && message.tool_calls.length > 0) {
    trackToolCalls(messageId, message.tool_calls.length)
  }
  
  // Compute usage
  const usage = computeUsageScore(messageId)
  
  // Compute impact
  const impact = computeImpactScore(message.work_references, message.goal_alignment)
  
  // Compute novelty
  const symbols = extractSymbols(message.work_references)
  const novelty = computeNovelty(symbols, priorSymbolsSet)
  
  // Update prior symbols
  symbols.forEach(s => priorSymbolsSet.add(s))
  
  // Compute recency
  const recency = computeRecency(message.timestamp, 30)  // 30 day half-life
  
  // Pins (from override, default to 0)
  const pins = 0  // Will be set by override system
  
  return {
    usage,
    impact,
    novelty,
    recency,
    pins
  }
}

// Extract relationships by comparing messages
export function extractRelationships(
  currentMessage: ChatMessage,
  otherMessages: ChatMessage[]
): Relationship[] {
  const relationships: Relationship[] = []
  const currentSymbols = new Set(extractSymbols(currentMessage.work_references))
  const currentContent = currentMessage.content.toLowerCase()
  const currentTimestamp = currentMessage.timestamp.getTime()
  
  for (const other of otherMessages) {
    if (other.id === currentMessage.id) continue
    
    const otherSymbols = new Set(extractSymbols(other.work_references))
    const otherContent = other.content.toLowerCase()
    const otherTimestamp = other.timestamp.getTime()
    
    // Compute symbol overlap
    const intersection = new Set([...currentSymbols].filter(x => otherSymbols.has(x)))
    const union = new Set([...currentSymbols, ...otherSymbols])
    const symbolOverlap = union.size > 0 ? intersection.size / union.size : 0
    
    // Compute text similarity (simple cosine-like)
    const currentWords = new Set(currentContent.split(/\s+/))
    const otherWords = new Set(otherContent.split(/\s+/))
    const wordIntersection = new Set([...currentWords].filter(x => otherWords.has(x)))
    const wordUnion = new Set([...currentWords, ...otherWords])
    const textSimilarity = wordUnion.size > 0 ? wordIntersection.size / wordUnion.size : 0
    
    // Combined similarity
    const similarity = (symbolOverlap * 0.6 + textSimilarity * 0.4)
    
    // Determine relationship type
    let relationshipType: RelationshipType | null = null
    
    // Same symbols + opposite polarity → contradicts
    if (symbolOverlap > 0.3) {
      const oppositeKeywords = ['not', 'no', 'never', 'avoid', 'remove', 'reject']
      const hasOpposite = oppositeKeywords.some(kw => 
        (currentContent.includes(kw) && !otherContent.includes(kw)) ||
        (!currentContent.includes(kw) && otherContent.includes(kw))
      )
      if (hasOpposite) {
        relationshipType = "contradicts"
      }
    }
    
    // Same goal + different approach → alternative_to
    if (!relationshipType && symbolOverlap > 0.2 && textSimilarity < 0.3) {
      if (currentMessage.goal_alignment?.objective === other.goal_alignment?.objective) {
        relationshipType = "alternative_to"
      }
    }
    
    // References as justification → supports
    if (!relationshipType && similarity > 0.4) {
      const supportKeywords = ['based on', 'using', 'from', 'according to', 'following']
      if (supportKeywords.some(kw => currentContent.includes(kw) || otherContent.includes(kw))) {
        relationshipType = "supports"
      }
    }
    
    // Code change unblocks task → resolves
    if (!relationshipType && otherTimestamp < currentTimestamp && symbolOverlap > 0.3) {
      const resolveKeywords = ['fixed', 'resolved', 'completed', 'implemented']
      if (resolveKeywords.some(kw => otherContent.includes(kw))) {
        relationshipType = "resolves"
      }
    }
    
    // Shared pre-reqs → depends_on
    if (!relationshipType && otherTimestamp < currentTimestamp && symbolOverlap > 0.2) {
      relationshipType = "depends_on"
    }
    
    // High text+symbol overlap → duplicates
    if (!relationshipType && similarity > 0.7) {
      relationshipType = "duplicates"
    }
    
    // Default: supports if similarity is high
    if (!relationshipType && similarity > 0.5) {
      relationshipType = "supports"
    }
    
    // Add relationship if type determined
    if (relationshipType) {
      const strength = similarity * (currentMessage.confidence ?? 0.5) * (other.confidence ?? 0.5)
      
      relationships.push({
        to: other.id,
        type: relationshipType,
        strength: clamp01(strength),
        objects: Array.from(intersection)
      })
    }
  }
  
  return relationships
}

// Convert ChatMessage to SummaryAtom
export function messageToSummaryAtom(
  message: ChatMessage,
  allMessages: ChatMessage[],
  turnNumber: number,
  priorSymbolsSet: Set<string> = new Set()
): SummaryAtom {
  // Extract claims
  const claims = extractClaims(
    message.content,
    message.work_references,
    message.confidence,
    message.goal_alignment
  )
  
  // Determine level
  const level = determineAtomLevel(message.content, claims, message.work_references)
  
  // Generate title
  const title = generateTitle(message.content)
  
  // Compute significance breakdown
  const breakdown = computeSignificanceBreakdown(message, priorSymbolsSet)
  
  // Compute significance score
  const sig: Significance = {
    score: computeSignificanceScore(breakdown),
    breakdown,
    halfLifeDays: 30
  }
  
  // Extract relationships (compare to other messages in same channel/thread)
  const relatedMessages = allMessages.filter(m => 
    m.id !== message.id &&
    (m.thread_id === message.thread_id || 
     m.connected_channel === message.connected_channel ||
     m.agent_id === message.agent_id)
  )
  const rel = extractRelationships(message, relatedMessages)
  
  return {
    id: message.id,
    level,
    title,
    turn: [turnNumber, turnNumber],  // Single turn for now
    recap: message.content,
    updatedAt: message.timestamp.toISOString(),
    claims,
    sig,
    rel
  }
}

// Batch convert messages to SummaryAtoms
export function messagesToSummaryAtoms(
  messages: ChatMessage[],
  startTurn: number = 0
): { atoms: SummaryAtom[]; priorSymbols: Set<string> } {
  const atoms: SummaryAtom[] = []
  const priorSymbolsSet = new Set<string>()
  
  messages.forEach((message, index) => {
    const atom = messageToSummaryAtom(message, messages, startTurn + index, priorSymbolsSet)
    atoms.push(atom)
  })
  
  return { atoms, priorSymbols: priorSymbolsSet }
}

