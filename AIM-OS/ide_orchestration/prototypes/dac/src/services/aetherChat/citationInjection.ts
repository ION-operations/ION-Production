/**
 * Citation Injection Service
 * Phase 4 Week 16: Citation Injection & Confidence Indicators
 * 
 * Implements:
 * - Citation marker insertion into text
 * - Linking citations to CMC atoms
 * - Building evidence chain using SEG
 * - Formatting citations (inline numbered style)
 */

import { SEGService } from '../SEGService'
import { CMCService } from '../CMCService'
import type { EvidenceItem, EvidencePack, CitationMarker, Provenance, EvidenceAnchor } from '../../types/aetherChatTypes'

const segService = new SEGService()
const cmcService = new CMCService()

/**
 * Inject citations into text with inline numbered markers
 * Returns text with citation markers and CitationMarker[] array
 */
export async function injectCitations(
  text: string,
  evidencePack: EvidencePack,
  citedEvidenceIds: string[]
): Promise<{
  textWithCitations: string
  citationMarkers: CitationMarker[]
  provenance: Provenance
}> {
  const citationMarkers: CitationMarker[] = []
  const provenance: Provenance = {
    anchors: {},
    overallConfidence: { value: 0.8, band: 'B' } // Default, will be updated
  }

  // Get cited evidence items
  const citedEvidence = citedEvidenceIds
    .map(id => evidencePack.items.find(item => item.id === id))
    .filter((item): item is EvidenceItem => item !== undefined)
    .sort((a, b) => b.trust - a.trust) // Sort by trust score

  if (citedEvidence.length === 0) {
    return {
      textWithCitations: text,
      citationMarkers: [],
      provenance
    }
  }

  // Build evidence chain using SEG (Phase 4 Week 16)
  const evidenceChain = await buildEvidenceChain(citedEvidence, evidencePack)

  // Create citation markers and anchors
  let citationNumber = 1
  const citationMap = new Map<string, number>() // Map evidence ID to citation number

  for (const evidence of citedEvidence) {
    if (!citationMap.has(evidence.id)) {
      citationMap.set(evidence.id, citationNumber++)
    }
  }

  // Find natural insertion points in text (after sentences, before code blocks, etc.)
  const insertionPoints = findCitationInsertionPoints(text, citedEvidence)

  // Insert citations at appropriate points
  let textWithCitations = text
  const sortedInsertions = insertionPoints.sort((a, b) => b.position - a.position) // Sort descending to insert from end

  for (const insertion of sortedInsertions) {
    const citationNum = citationMap.get(insertion.evidenceId)!
    const citationMarker = `[${citationNum}]`
    
    // Insert citation marker
    textWithCitations = 
      textWithCitations.substring(0, insertion.position) +
      ` ${citationMarker}` +
      textWithCitations.substring(insertion.position)

    // Create CitationMarker object
    const marker: CitationMarker = {
      id: citationMarker,
      evidenceId: insertion.evidenceId,
      position: insertion.position,
      length: citationMarker.length
    }
    citationMarkers.push(marker)

    // Create EvidenceAnchor for provenance
    const evidence = citedEvidence.find(e => e.id === insertion.evidenceId)!
    const anchor: EvidenceAnchor = {
      citationId: citationMarker,
      claim: {
        text: text.substring(Math.max(0, insertion.position - 50), insertion.position + 50),
        confidence: { value: evidence.trust, band: evidence.trust >= 0.9 ? 'A' : evidence.trust >= 0.7 ? 'B' : 'C' }
      },
      source: {
        atomId: evidence.id,
        type: evidence.kind === 'file_snippet' ? 'CODE_SNIPPET' :
              evidence.kind === 'doc_snippet' ? 'DOCUMENT' :
              evidence.kind === 'prior_msg' ? 'USER_MESSAGE' :
              'OTHER',
        preview: evidence.excerpt.substring(0, 100),
        location: evidence.location,
        timestamp: evidence.timestamp || new Date()
      },
      witness: evidence.segAnchorId ? {
        id: evidence.segAnchorId,
        hash: '', // TODO: Get from SEG
        toolsUsed: []
      } : undefined
    }

    provenance.anchors[insertion.evidenceId] = anchor
  }

  // Update overall confidence based on evidence trust scores
  const avgTrust = citedEvidence.reduce((sum, e) => sum + e.trust, 0) / citedEvidence.length
  provenance.overallConfidence = {
    value: avgTrust,
    band: avgTrust >= 0.95 ? 'S' : avgTrust >= 0.90 ? 'A' : avgTrust >= 0.85 ? 'B' : 'C'
  }

  return {
    textWithCitations,
    citationMarkers,
    provenance
  }
}

/**
 * Build evidence chain using SEG
 * Links evidence items together based on relationships
 */
async function buildEvidenceChain(
  citedEvidence: EvidenceItem[],
  evidencePack: EvidencePack
): Promise<Array<{ from: string; to: string; relation: string }>> {
  try {
    // Use SEG to find relationships between evidence items
    const evidenceIds = citedEvidence.map(e => e.id)
    
    // Query SEG for relationships
    const relationships = await segService.findRelationships(evidenceIds)
    
    if (relationships.success && relationships.relationships) {
      return relationships.relationships.map(rel => ({
        from: rel.from,
        to: rel.to,
        relation: rel.type || 'related'
      }))
    }
  } catch (error) {
    console.warn('[Citation Injection] SEG unavailable, skipping evidence chain:', error)
  }

  // Fallback: return empty chain
  return []
}

/**
 * Find natural insertion points for citations in text
 * Looks for sentence endings, code block boundaries, list items, etc.
 */
function findCitationInsertionPoints(
  text: string,
  citedEvidence: EvidenceItem[]
): Array<{ position: number; evidenceId: string; relevance: number }> {
  const insertionPoints: Array<{ position: number; evidenceId: string; relevance: number }> = []

  // Simple strategy: Insert citations after sentences that mention concepts from evidence
  // For now, we'll use a simple approach: insert at sentence boundaries
  
  // Split text into sentences (simple regex-based)
  const sentenceRegex = /[.!?]\s+/g
  const sentences: Array<{ text: string; start: number; end: number }> = []
  let lastIndex = 0
  let match

  while ((match = sentenceRegex.exec(text)) !== null) {
    sentences.push({
      text: text.substring(lastIndex, match.index + match[0].length),
      start: lastIndex,
      end: match.index + match[0].length
    })
    lastIndex = match.index + match[0].length
  }

  // Add final sentence if text doesn't end with punctuation
  if (lastIndex < text.length) {
    sentences.push({
      text: text.substring(lastIndex),
      start: lastIndex,
      end: text.length
    })
  }

  // For each sentence, try to match it with evidence
  for (const sentence of sentences) {
    // Simple keyword matching (in production, use semantic similarity)
    for (const evidence of citedEvidence) {
      const relevance = calculateRelevance(sentence.text, evidence.excerpt)
      if (relevance > 0.3) { // Threshold for citation insertion
        insertionPoints.push({
          position: sentence.end,
          evidenceId: evidence.id,
          relevance
        })
      }
    }
  }

  // Sort by relevance and limit to avoid too many citations
  return insertionPoints
    .sort((a, b) => b.relevance - a.relevance)
    .slice(0, Math.min(citedEvidence.length * 2, 10)) // Max 2 citations per evidence item, or 10 total
}

/**
 * Calculate relevance between sentence and evidence excerpt
 * Simple keyword-based approach (in production, use semantic similarity)
 */
function calculateRelevance(sentence: string, excerpt: string): number {
  const sentenceWords = sentence.toLowerCase().split(/\s+/)
  const excerptWords = excerpt.toLowerCase().split(/\s+/)
  
  // Count common words (excluding common stop words)
  const stopWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can'])
  
  const sentenceSet = new Set(sentenceWords.filter(w => w.length > 3 && !stopWords.has(w)))
  const excerptSet = new Set(excerptWords.filter(w => w.length > 3 && !stopWords.has(w)))
  
  const commonWords = Array.from(sentenceSet).filter(w => excerptSet.has(w))
  const totalWords = Math.max(sentenceSet.size, excerptSet.size, 1)
  
  return commonWords.length / totalWords
}

/**
 * Link citations to CMC atoms
 * Retrieves CMC atom metadata for each citation
 */
export async function linkCitationsToCMCAtoms(
  citationMarkers: CitationMarker[],
  evidencePack: EvidencePack
): Promise<Record<string, { atomId: string; metadata: any }>> {
  const links: Record<string, { atomId: string; metadata: any }> = {}

  for (const marker of citationMarkers) {
    const evidence = evidencePack.items.find(e => e.id === marker.evidenceId)
    if (evidence) {
      // Try to retrieve CMC atom if we have the ID
      // Use retrieveAtoms with a query for the specific atom ID
      if (evidence.id) {
        try {
          const result = await cmcService.retrieveAtoms(`id:${evidence.id}`, 1)
          if (result.success && result.atoms && result.atoms.length > 0) {
            const atom = result.atoms[0]
            links[marker.id] = {
              atomId: evidence.id,
              metadata: atom.metadata || {}
            }
          }
        } catch (error) {
          console.warn(`[Citation Injection] Failed to retrieve CMC atom ${evidence.id}:`, error)
        }
      }
    }
  }

  return links
}

