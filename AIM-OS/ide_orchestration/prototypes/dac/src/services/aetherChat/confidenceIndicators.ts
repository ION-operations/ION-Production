/**
 * Confidence Indicators Service
 * Phase 4 Week 16: Citation Injection & Confidence Indicators
 * 
 * Implements:
 * - Section-level confidence assessment
 * - VIF confidence scoring per section
 * - Visual indicators (HIGH, MEDIUM, LOW)
 * - Evidence strength display (source count, recency)
 */

import { VIFService } from '../VIFService'
import type { EvidenceItem, EvidencePack, ConfidenceScore } from '../../types/aetherChatTypes'

const vifService = new VIFService()

/**
 * Section-level confidence assessment
 * Splits text into sections and assesses confidence for each
 */
export interface SectionConfidence {
  sectionId: string
  text: string
  startIndex: number
  endIndex: number
  confidence: ConfidenceScore
  evidenceCount: number
  evidenceStrength: 'high' | 'medium' | 'low'
  sources: Array<{
    evidenceId: string
    trust: number
    recency: number // Days since timestamp
  }>
}

/**
 * Assess confidence for each section of text
 */
export async function assessSectionConfidence(
  text: string,
  evidencePack: EvidencePack,
  citedEvidenceIds: string[]
): Promise<SectionConfidence[]> {
  // Split text into sections (paragraphs, code blocks, lists)
  const sections = splitIntoSections(text)
  
  const sectionConfidences: SectionConfidence[] = []

  for (let i = 0; i < sections.length; i++) {
    const section = sections[i]
    
    // Find evidence relevant to this section
    const relevantEvidence = findRelevantEvidence(section.text, evidencePack, citedEvidenceIds)
    
    // Calculate evidence strength
    const evidenceStrength = calculateEvidenceStrength(relevantEvidence)
    
    // Get VIF confidence for this section
    const vifConfidence = await getVIFConfidenceForSection(section.text, relevantEvidence)
    
    sectionConfidences.push({
      sectionId: `section_${i}`,
      text: section.text,
      startIndex: section.start,
      endIndex: section.end,
      confidence: vifConfidence,
      evidenceCount: relevantEvidence.length,
      evidenceStrength,
      sources: relevantEvidence.map(e => ({
        evidenceId: e.id,
        trust: e.trust,
        recency: e.timestamp ? 
          (Date.now() - e.timestamp.getTime()) / (1000 * 60 * 60 * 24) : // Days
          Infinity
      }))
    })
  }

  return sectionConfidences
}

/**
 * Split text into logical sections
 */
function splitIntoSections(text: string): Array<{ text: string; start: number; end: number; type: 'paragraph' | 'code' | 'list' | 'table' }> {
  const sections: Array<{ text: string; start: number; end: number; type: 'paragraph' | 'code' | 'list' | 'table' }> = []
  let currentIndex = 0

  // Detect code blocks
  const codeBlockRegex = /```[\s\S]*?```/g
  let match
  const codeBlocks: Array<{ start: number; end: number }> = []
  
  while ((match = codeBlockRegex.exec(text)) !== null) {
    codeBlocks.push({ start: match.index, end: match.index + match[0].length })
  }

  // Detect lists
  const listRegex = /^[-*+]\s+.+$/gm
  const lists: Array<{ start: number; end: number }> = []
  
  while ((match = listRegex.exec(text)) !== null) {
    lists.push({ start: match.index, end: match.index + match[0].length })
  }

  // Detect tables
  const tableRegex = /^\|.+\|\s*\n\|[-:|\s]+\|\s*\n((?:\|.+\|\s*\n?)+)/gm
  const tables: Array<{ start: number; end: number }> = []
  
  while ((match = tableRegex.exec(text)) !== null) {
    tables.push({ start: match.index, end: match.index + match[0].length })
  }

  // Split by paragraphs (double newlines)
  const paragraphs = text.split(/\n\n+/)
  let paragraphIndex = 0

  for (const paragraph of paragraphs) {
    const paragraphStart = text.indexOf(paragraph, paragraphIndex)
    const paragraphEnd = paragraphStart + paragraph.length

    // Check if this paragraph is inside a code block, list, or table
    const inCodeBlock = codeBlocks.some(cb => paragraphStart >= cb.start && paragraphEnd <= cb.end)
    const inList = lists.some(l => paragraphStart >= l.start && paragraphEnd <= l.end)
    const inTable = tables.some(t => paragraphStart >= t.start && paragraphEnd <= t.end)

    if (inCodeBlock) {
      const codeBlock = codeBlocks.find(cb => paragraphStart >= cb.start && paragraphEnd <= cb.end)!
      sections.push({
        text: text.substring(codeBlock.start, codeBlock.end),
        start: codeBlock.start,
        end: codeBlock.end,
        type: 'code'
      })
      paragraphIndex = codeBlock.end
    } else if (inList) {
      const list = lists.find(l => paragraphStart >= l.start && paragraphEnd <= l.end)!
      sections.push({
        text: text.substring(list.start, list.end),
        start: list.start,
        end: list.end,
        type: 'list'
      })
      paragraphIndex = list.end
    } else if (inTable) {
      const table = tables.find(t => paragraphStart >= t.start && paragraphEnd <= t.end)!
      sections.push({
        text: text.substring(table.start, table.end),
        start: table.start,
        end: table.end,
        type: 'table'
      })
      paragraphIndex = table.end
    } else if (paragraph.trim().length > 0) {
      sections.push({
        text: paragraph.trim(),
        start: paragraphStart,
        end: paragraphEnd,
        type: 'paragraph'
      })
      paragraphIndex = paragraphEnd
    }
  }

  return sections
}

/**
 * Find evidence relevant to a section
 */
function findRelevantEvidence(
  sectionText: string,
  evidencePack: EvidencePack,
  citedEvidenceIds: string[]
): EvidenceItem[] {
  const relevant: EvidenceItem[] = []

  // Get cited evidence first
  const citedEvidence = citedEvidenceIds
    .map(id => evidencePack.items.find(item => item.id === id))
    .filter((item): item is EvidenceItem => item !== undefined)

  // Simple keyword matching (in production, use semantic similarity)
  for (const evidence of citedEvidence) {
    const relevance = calculateRelevance(sectionText, evidence.excerpt)
    if (relevance > 0.2) {
      relevant.push(evidence)
    }
  }

  return relevant.sort((a, b) => b.trust - a.trust)
}

/**
 * Calculate relevance between section and evidence
 */
function calculateRelevance(sectionText: string, excerpt: string): number {
  const sectionWords = sectionText.toLowerCase().split(/\s+/)
  const excerptWords = excerpt.toLowerCase().split(/\s+/)
  
  const stopWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can'])
  
  const sectionSet = new Set(sectionWords.filter(w => w.length > 3 && !stopWords.has(w)))
  const excerptSet = new Set(excerptWords.filter(w => w.length > 3 && !stopWords.has(w)))
  
  const commonWords = Array.from(sectionSet).filter(w => excerptSet.has(w))
  const totalWords = Math.max(sectionSet.size, excerptSet.size, 1)
  
  return commonWords.length / totalWords
}

/**
 * Calculate evidence strength based on count, trust, and recency
 */
function calculateEvidenceStrength(evidence: EvidenceItem[]): 'high' | 'medium' | 'low' {
  if (evidence.length === 0) return 'low'
  
  const avgTrust = evidence.reduce((sum, e) => sum + e.trust, 0) / evidence.length
  const recentCount = evidence.filter(e => {
    if (!e.timestamp) return false
    const daysAgo = (Date.now() - e.timestamp.getTime()) / (1000 * 60 * 60 * 24)
    return daysAgo < 7 // Within 7 days
  }).length
  
  const recencyScore = recentCount / evidence.length
  
  // High: 3+ sources, avg trust > 0.8, >50% recent
  // Medium: 2+ sources, avg trust > 0.6, >25% recent
  // Low: otherwise
  if (evidence.length >= 3 && avgTrust > 0.8 && recencyScore > 0.5) {
    return 'high'
  } else if (evidence.length >= 2 && avgTrust > 0.6 && recencyScore > 0.25) {
    return 'medium'
  } else {
    return 'low'
  }
}

/**
 * Get VIF confidence for a section
 */
async function getVIFConfidenceForSection(
  sectionText: string,
  evidence: EvidenceItem[]
): Promise<ConfidenceScore> {
  try {
    // Use VIF to assess confidence based on evidence
    if (evidence.length === 0) {
      return { value: 0.5, band: 'C' }
    }

    // Calculate confidence based on evidence trust scores
    const avgTrust = evidence.reduce((sum, e) => sum + e.trust, 0) / evidence.length
    const maxTrust = Math.max(...evidence.map(e => e.trust))
    
    // Weighted average: 70% max trust, 30% avg trust
    const confidence = (maxTrust * 0.7) + (avgTrust * 0.3)
    
    return {
      value: confidence,
      band: confidence >= 0.95 ? 'S' :
            confidence >= 0.90 ? 'A' :
            confidence >= 0.85 ? 'B' : 'C'
    }
  } catch (error) {
    console.warn('[Confidence Indicators] VIF unavailable, using fallback:', error)
    // Fallback: basic confidence calculation
    if (evidence.length === 0) {
      return { value: 0.5, band: 'C' }
    }
    const avgTrust = evidence.reduce((sum, e) => sum + e.trust, 0) / evidence.length
    return {
      value: avgTrust,
      band: avgTrust >= 0.90 ? 'A' : avgTrust >= 0.85 ? 'B' : 'C'
    }
  }
}

/**
 * Create visual indicator for confidence level
 */
export function getConfidenceIndicator(confidence: ConfidenceScore): {
  level: 'HIGH' | 'MEDIUM' | 'LOW'
  color: string
  icon: string
} {
  if (confidence.band === 'S' || confidence.band === 'A') {
    return {
      level: 'HIGH',
      color: '#10b981', // green
      icon: '✓'
    }
  } else if (confidence.band === 'B') {
    return {
      level: 'MEDIUM',
      color: '#f59e0b', // amber
      icon: '⚠'
    }
  } else {
    return {
      level: 'LOW',
      color: '#ef4444', // red
      icon: '?'
    }
  }
}

/**
 * Format evidence strength display
 */
export function formatEvidenceStrength(
  sectionConfidence: SectionConfidence
): {
  display: string
  sourceCount: number
  recency: string
  trustScore: string
} {
  const sourceCount = sectionConfidence.evidenceCount
  const avgRecency = sectionConfidence.sources.length > 0
    ? sectionConfidence.sources.reduce((sum, s) => sum + s.recency, 0) / sectionConfidence.sources.length
    : Infinity
  
  const recencyDisplay = avgRecency === Infinity ? 'Unknown' :
                         avgRecency < 1 ? 'Today' :
                         avgRecency < 7 ? `${Math.round(avgRecency)} days ago` :
                         avgRecency < 30 ? `${Math.round(avgRecency / 7)} weeks ago` :
                         `${Math.round(avgRecency / 30)} months ago`
  
  const avgTrust = sectionConfidence.sources.length > 0
    ? sectionConfidence.sources.reduce((sum, s) => sum + s.trust, 0) / sectionConfidence.sources.length
    : 0
  
  const trustScore = `${(avgTrust * 100).toFixed(0)}%`
  
  return {
    display: `${sourceCount} source${sourceCount !== 1 ? 's' : ''} • ${recencyDisplay} • ${trustScore} trust`,
    sourceCount,
    recency: recencyDisplay,
    trustScore
  }
}

