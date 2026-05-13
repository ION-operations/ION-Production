/**
 * Evidence Pack Construction Service
 * Enhanced evidence extraction, trust calculation, and chain building
 * 
 * Phase 2 Week 9: Evidence Pack Construction
 */

import { SEGService } from '../SEGService'
import { VIFService } from '../VIFService'
import type { CMCAtom, EvidenceItem, EvidencePack, EvidenceChain, ContextWeb } from '../../types/aetherChatTypes'

export interface EvidenceConstructionOptions {
  minTrustScore?: number // Minimum trust score to include (default: 0.3)
  maxItems?: number // Maximum evidence items to return (default: 20)
  prioritizeRecent?: boolean // Boost recency in ranking (default: true)
  requireSEGAnchor?: boolean // Only include items with SEG anchors (default: false)
}

/**
 * Enhanced Evidence Item extraction from CMC atoms
 * Phase 2 Week 9: Day 1-2
 */
export async function extractEvidenceItems(
  cmcAtoms: CMCAtom[],
  options: EvidenceConstructionOptions = {}
): Promise<EvidenceItem[]> {
  const {
    minTrustScore = 0.3,
    maxItems = 20,
    prioritizeRecent = true,
    requireSEGAnchor = false
  } = options

  const evidenceItems: EvidenceItem[] = []

  for (const atom of cmcAtoms) {
    // Determine evidence kind based on atom properties
    let kind: EvidenceItem['kind'] = 'other'
    
    if (atom.modality === 'code') {
      kind = 'file_snippet'
    } else if (atom.modality === 'text') {
      // Check if it's a prior message or document
      if (atom.tags?.some(tag => tag.includes('message') || tag.includes('chat'))) {
        kind = 'prior_msg'
      } else {
        kind = 'doc_snippet'
      }
    } else if (atom.modality === 'test' || atom.tags?.some(tag => tag.includes('test'))) {
      kind = 'test_output'
    }

    // Calculate trust score
    const trustScore = calculateTrustScore(atom, prioritizeRecent)

    // Skip if below minimum trust
    if (trustScore < minTrustScore) {
      continue
    }

    // Extract excerpt (smart truncation)
    const excerpt = extractExcerpt(atom.content, kind)

    // Create evidence item
    const evidenceItem: EvidenceItem = {
      id: atom.id,
      kind,
      sourceId: atom.id,
      excerpt,
      trust: trustScore,
      location: atom.metadata.location,
      timestamp: atom.metadata.timestamp
    }

    evidenceItems.push(evidenceItem)
  }

  // Rank and filter
  const rankedItems = rankEvidenceItems(evidenceItems, prioritizeRecent)
  const filteredItems = rankedItems.slice(0, maxItems)

  return filteredItems
}

/**
 * Calculate trust score for evidence item
 * Factors: relevance, recency, source quality, VIF confidence
 */
function calculateTrustScore(
  atom: CMCAtom,
  prioritizeRecent: boolean
): number {
  let trust = 0.5 // Base trust

  // Relevance boost (from metadata)
  if (atom.metadata.relevance !== undefined) {
    trust += atom.metadata.relevance * 0.3
  }

  // Recency boost
  if (atom.metadata.timestamp && prioritizeRecent) {
    const age = Date.now() - new Date(atom.metadata.timestamp).getTime()
    const daysOld = age / (1000 * 60 * 60 * 24)
    const recencyBoost = Math.max(0, 1 - (daysOld / 30)) // Decay over 30 days
    trust += recencyBoost * 0.2
  }

  // Source quality boost (based on tags)
  if (atom.tags) {
    const qualityTags = ['verified', 'tested', 'production', 'documented']
    const qualityCount = atom.tags.filter(tag => 
      qualityTags.some(qt => tag.toLowerCase().includes(qt))
    ).length
    trust += (qualityCount / qualityTags.length) * 0.2
  }

  // Modality boost (code and text are more trustworthy than other types)
  if (atom.modality === 'code' || atom.modality === 'text') {
    trust += 0.1
  }

  return Math.min(1.0, trust)
}

/**
 * Extract excerpt from content (smart truncation based on kind)
 */
function extractExcerpt(content: string, kind: EvidenceItem['kind']): string {
  const maxLengths: Record<EvidenceItem['kind'], number> = {
    'file_snippet': 200,
    'doc_snippet': 300,
    'prior_msg': 150,
    'test_output': 250,
    'other': 200
  }

  const maxLength = maxLengths[kind] || 200

  if (content.length <= maxLength) {
    return content
  }

  // Try to truncate at sentence boundary
  const truncated = content.substring(0, maxLength)
  const lastPeriod = truncated.lastIndexOf('.')
  const lastNewline = truncated.lastIndexOf('\n')

  const cutPoint = Math.max(lastPeriod, lastNewline)
  if (cutPoint > maxLength * 0.7) {
    return truncated.substring(0, cutPoint + 1) + '...'
  }

  return truncated + '...'
}

/**
 * Rank evidence items by trust, recency, and relevance
 */
function rankEvidenceItems(
  items: EvidenceItem[],
  prioritizeRecent: boolean
): EvidenceItem[] {
  return [...items].sort((a, b) => {
    // Primary: trust score
    if (Math.abs(a.trust - b.trust) > 0.05) {
      return b.trust - a.trust
    }

    // Secondary: recency (if prioritizeRecent)
    if (prioritizeRecent && a.timestamp && b.timestamp) {
      const aTime = new Date(a.timestamp).getTime()
      const bTime = new Date(b.timestamp).getTime()
      return bTime - aTime
    }

    // Tertiary: kind priority (file_snippet > doc_snippet > prior_msg > test_output > other)
    const kindPriority: Record<EvidenceItem['kind'], number> = {
      'file_snippet': 5,
      'doc_snippet': 4,
      'prior_msg': 3,
      'test_output': 2,
      'other': 1
    }
    return kindPriority[b.kind] - kindPriority[a.kind]
  })
}

/**
 * Build Evidence Chain using SEG
 * Phase 2 Week 9: Day 3-4
 */
export async function buildEvidenceChain(
  claims: Array<{ text: string; claimId?: string }>,
  evidenceItems: EvidenceItem[],
  contextWeb: ContextWeb,
  segService?: SEGService
): Promise<EvidenceChain> {
  const evidenceChain: EvidenceChain = {
    claims: [],
    links: []
  }

  // Link each claim to relevant evidence
  for (const claim of claims) {
    // Find evidence items that support this claim
    const supportingEvidence = findSupportingEvidence(claim.text, evidenceItems)

    evidenceChain.claims.push({
      text: claim.text,
      evidenceIds: supportingEvidence.map(item => item.id)
    })

    // Build links between evidence items (if SEG available)
    if (segService && supportingEvidence.length > 1) {
      for (let i = 0; i < supportingEvidence.length; i++) {
        for (let j = i + 1; j < supportingEvidence.length; j++) {
          // Check if there's a relationship in context web
          const edge = contextWeb.edges.find(
            e => (e.from === supportingEvidence[i].id && e.to === supportingEvidence[j].id) ||
                 (e.to === supportingEvidence[i].id && e.from === supportingEvidence[j].id)
          )

          if (edge) {
            evidenceChain.links.push({
              from: supportingEvidence[i].id,
              to: supportingEvidence[j].id,
              relation: edge.relation
            })
          }
        }
      }
    }
  }

  return evidenceChain
}

/**
 * Find evidence items that support a claim
 * Uses simple keyword matching (can be enhanced with LLM)
 */
function findSupportingEvidence(
  claimText: string,
  evidenceItems: EvidenceItem[]
): EvidenceItem[] {
  const claimKeywords = claimText.toLowerCase().split(/\s+/).filter(w => w.length > 3)

  return evidenceItems
    .map(item => ({
      item,
      score: calculateSupportScore(claimKeywords, item)
    }))
    .filter(({ score }) => score > 0.1)
    .sort((a, b) => b.score - a.score)
    .slice(0, 5) // Top 5 supporting evidence items
    .map(({ item }) => item)
}

/**
 * Calculate how well an evidence item supports a claim
 */
function calculateSupportScore(
  claimKeywords: string[],
  evidenceItem: EvidenceItem
): number {
  const excerptLower = evidenceItem.excerpt.toLowerCase()
  let score = 0

  for (const keyword of claimKeywords) {
    if (excerptLower.includes(keyword)) {
      score += 1
    }
  }

  // Normalize by keyword count
  return claimKeywords.length > 0 ? score / claimKeywords.length : 0
}

/**
 * Check evidence completeness
 * Phase 2 Week 9: Day 3-4
 */
export interface EvidenceCompletenessResult {
  isComplete: boolean
  completenessScore: number // 0-1
  missingTypes: EvidenceItem['kind'][]
  recommendations: string[]
}

export function checkEvidenceCompleteness(
  evidenceItems: EvidenceItem[],
  claimText: string
): EvidenceCompletenessResult {
  const types = new Set(evidenceItems.map(item => item.kind))
  const expectedTypes: EvidenceItem['kind'][] = ['file_snippet', 'doc_snippet', 'prior_msg']
  const missingTypes = expectedTypes.filter(type => !types.has(type))

  // Calculate completeness score
  let completenessScore = 0.5 // Base score

  // Boost for having multiple types
  if (types.size >= 2) {
    completenessScore += 0.2
  }

  // Boost for high trust items
  const avgTrust = evidenceItems.length > 0
    ? evidenceItems.reduce((sum, item) => sum + item.trust, 0) / evidenceItems.length
    : 0
  completenessScore += avgTrust * 0.3

  // Penalty for missing types
  completenessScore -= missingTypes.length * 0.1

  completenessScore = Math.max(0, Math.min(1, completenessScore))

  // Generate recommendations
  const recommendations: string[] = []
  if (missingTypes.includes('file_snippet')) {
    recommendations.push('Consider adding code examples or file references')
  }
  if (missingTypes.includes('doc_snippet')) {
    recommendations.push('Consider adding documentation references')
  }
  if (missingTypes.includes('prior_msg')) {
    recommendations.push('Consider referencing prior conversation context')
  }
  if (avgTrust < 0.6) {
    recommendations.push('Evidence trust scores are low - verify sources')
  }

  return {
    isComplete: completenessScore >= 0.7 && missingTypes.length === 0,
    completenessScore,
    missingTypes,
    recommendations
  }
}

/**
 * Build complete Evidence Pack with ranking and filtering
 * Phase 2 Week 9: Day 5
 */
export async function buildEvidencePack(
  cmcAtoms: CMCAtom[],
  claims: Array<{ text: string; claimId?: string }>,
  contextWeb: ContextWeb,
  options: EvidenceConstructionOptions = {},
  segService?: SEGService
): Promise<{
  evidencePack: EvidencePack
  evidenceChain: EvidenceChain
  completeness: EvidenceCompletenessResult
}> {
  // Extract evidence items
  const evidenceItems = await extractEvidenceItems(cmcAtoms, options)

  // Build evidence chain
  const evidenceChain = await buildEvidenceChain(claims, evidenceItems, contextWeb, segService)

  // Calculate total trust
  const totalTrust = evidenceItems.length > 0
    ? evidenceItems.reduce((sum, item) => sum + item.trust, 0) / evidenceItems.length
    : 0

  // Create evidence pack
  const evidencePack: EvidencePack = {
    items: evidenceItems,
    totalTrust
  }

  // Check completeness (using first claim as representative)
  const mainClaim = claims[0]?.text || ''
  const completeness = checkEvidenceCompleteness(evidenceItems, mainClaim)

  return {
    evidencePack,
    evidenceChain,
    completeness
  }
}

