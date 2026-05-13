// Deterministic Retrieval System
// Part of AI Chat System Enhancement: Significance Scoring & Typed Relationships

import {
  SummaryAtom,
  ClaimKind,
  RelationshipType,
  ContextUse,
  MessageContextInfo,
  ContextOverride
} from './summaryAtoms'

export type Need = {
  kind: ClaimKind
  objects: string[]
  mustInclude?: string[]
}

export type TokenBudget = number

export interface AssembledContext {
  atoms: SummaryAtom[]
  totalTokens: number
  usedByAgent: Record<string, number>
  reasons: Record<string, string[]>  // atom id -> reasons for inclusion
}

// Compute token count for an atom (rough estimate)
function estimateTokens(atom: SummaryAtom, level: 'macro' | 'meso' | 'micro' | 'raw' = atom.level): number {
  // Rough token estimation: ~4 chars per token
  const baseTokens = Math.ceil(atom.recap.length / 4)
  
  // Level multipliers (summaries are smaller)
  const multipliers: Record<string, number> = {
    macro: 0.3,  // Macro summaries are 30% of raw
    meso: 0.5,   // Meso summaries are 50% of raw
    micro: 0.7,  // Micro summaries are 70% of raw
    raw: 1.0     // Raw is 100%
  }
  
  return Math.ceil(baseTokens * (multipliers[level] ?? 1.0))
}

// Compute semantic similarity (simple cosine-like)
function computeSimilarity(atom: SummaryAtom, querySymbols: Set<string>): number {
  const atomSymbols = new Set<string>()
  
  // Collect symbols from claims
  atom.claims.forEach(claim => {
    claim.objects.forEach(obj => atomSymbols.add(obj))
  })
  
  if (atomSymbols.size === 0 || querySymbols.size === 0) return 0
  
  const intersection = new Set([...atomSymbols].filter(x => querySymbols.has(x)))
  const union = new Set([...atomSymbols, ...querySymbols])
  
  return union.size > 0 ? intersection.size / union.size : 0
}

// Compute relation boost based on needs
function computeRelationBoost(
  atom: SummaryAtom,
  needs: Need[]
): number {
  let boost = 0
  
  needs.forEach(need => {
    atom.rel.forEach(rel => {
      // Check if relationship targets objects we need
      const hasOverlap = rel.objects?.some(obj => need.objects.includes(obj)) ?? false
      
      if (hasOverlap) {
        switch (rel.type) {
          case 'supports':
          case 'depends_on':
            boost += rel.strength * 0.3  // Positive boost
            break
          case 'contradicts':
            boost -= rel.strength * 0.2  // Negative boost (unless reviewing contradictions)
            break
          case 'resolves':
            boost += rel.strength * 0.4  // Strong positive boost
            break
        }
      }
    })
  })
  
  return Math.max(-0.5, Math.min(0.5, boost))  // Clamp to [-0.5, 0.5]
}

// Check if atom covers a need
function coversNeed(atom: SummaryAtom, need: Need): boolean {
  // Check claim kind
  const hasKind = atom.claims.some(claim => claim.kind === need.kind)
  if (!hasKind) return false
  
  // Check object overlap
  const atomObjects = new Set<string>()
  atom.claims.forEach(claim => {
    claim.objects.forEach(obj => atomObjects.add(obj))
  })
  
  const hasObjects = need.objects.some(obj => atomObjects.has(obj))
  if (need.objects.length > 0 && !hasObjects) return false
  
  return true
}

// Diversify selection to avoid duplicates
function diversify(
  scored: Array<{ atom: SummaryAtom; score: number }>,
  needs: Need[]
): Array<{ atom: SummaryAtom; score: number }> {
  const picked: Array<{ atom: SummaryAtom; score: number }> = []
  const usedObjects = new Set<string>()
  const usedKinds = new Set<ClaimKind>()
  
  // Sort by score descending
  const sorted = [...scored].sort((a, b) => b.score - a.score)
  
  for (const item of sorted) {
    const atom = item.atom
    
    // Check if we need this kind
    const neededKinds = new Set(needs.map(n => n.kind))
    const hasNeededKind = atom.claims.some(claim => neededKinds.has(claim.kind))
    
    // Check object diversity
    const atomObjects = new Set<string>()
    atom.claims.forEach(claim => {
      claim.objects.forEach(obj => atomObjects.add(obj))
    })
    
    const overlap = [...atomObjects].filter(obj => usedObjects.has(obj)).length
    const diversityRatio = atomObjects.size > 0 ? 1 - (overlap / atomObjects.size) : 1
    
    // Prefer diverse atoms
    if (hasNeededKind && (diversityRatio > 0.3 || picked.length < needs.length)) {
      picked.push(item)
      atomObjects.forEach(obj => usedObjects.add(obj))
      atom.claims.forEach(claim => usedKinds.add(claim.kind))
    }
    
    // Stop if we have enough diversity
    if (picked.length >= needs.length * 2) break
  }
  
  return picked
}

// Pack atoms to budget
function packToBudget(
  scored: Array<{ atom: SummaryAtom; score: number }>,
  budget: TokenBudget,
  overrides: Record<string, ContextOverride>,
  agent: string
): AssembledContext {
  const picked: SummaryAtom[] = []
  let totalTokens = 0
  const reasons: Record<string, string[]> = {}
  const usedByAgent: Record<string, number> = { [agent]: 0 }
  
  // Sort by score descending
  const sorted = [...scored].sort((a, b) => b.score - a.score)
  
  for (const item of sorted) {
    const atom = item.atom
    const override = overrides[atom.id]
    
    // Determine level (respect override)
    const level = override?.forcedLevel ?? atom.level
    const tokens = estimateTokens(atom, level)
    
    // Check if we can fit it
    if (totalTokens + tokens <= budget) {
      picked.push(atom)
      totalTokens += tokens
      usedByAgent[agent] += tokens
      
      // Record reasons
      const atomReasons: string[] = []
      if (atom.sig.breakdown.recency > 0.7) atomReasons.push('recency')
      if (atom.sig.breakdown.usage > 0.5) atomReasons.push('usage')
      if (atom.sig.score > 0.7) atomReasons.push('significance')
      if (override?.pinned) atomReasons.push('pin')
      if (override?.priority && override.priority > 0) atomReasons.push('priority')
      if (atom.rel.length > 0) atomReasons.push('dependency')
      
      reasons[atom.id] = atomReasons.length > 0 ? atomReasons : ['semantic']
    } else {
      // Can't fit, but check if pinned (pins can exceed budget slightly)
      if (override?.pinned && totalTokens + tokens <= budget * 1.2) {
        picked.push(atom)
        totalTokens += tokens
        usedByAgent[agent] += tokens
        reasons[atom.id] = ['pin']
      }
    }
  }
  
  return {
    atoms: picked,
    totalTokens,
    usedByAgent,
    reasons
  }
}

// Final score with overrides
function finalScore(
  baseScore: number,
  override?: ContextOverride
): number {
  const pinBoost = override?.pinned ? 0.08 : 0.0
  const prioBoost = Math.max(-0.1, Math.min(0.1, (override?.priority ?? 0) * 0.1))
  
  return Math.max(0, Math.min(1, baseScore + pinBoost + prioBoost))
}

// Main assemble function
export function assemble(
  query: string,
  needs: Need[],
  budget: TokenBudget,
  availableAtoms: SummaryAtom[],
  overrides: Record<string, ContextOverride> = {},
  agent: string = 'default'
): AssembledContext {
  // Extract query symbols (simple tokenization)
  const queryWords = query.toLowerCase().split(/\s+/)
  const querySymbols = new Set(queryWords.filter(w => w.length > 3))  // Filter short words
  
  // Score all atoms
  const scored = availableAtoms.map(atom => {
    const baseScore = atom.sig.score
    const semanticScore = computeSimilarity(atom, querySymbols)
    const relationBoost = computeRelationBoost(atom, needs)
    const recencyBoost = atom.sig.breakdown.recency * 0.1
    const pinBoost = (overrides[atom.id]?.pinned ? 0.05 : 0)
    
    const compositeScore =
      0.45 * baseScore +
      0.25 * semanticScore +
      0.15 * relationBoost +
      0.10 * recencyBoost +
      0.05 * pinBoost
    
    const final = finalScore(compositeScore, overrides[atom.id])
    
    return {
      atom,
      score: final
    }
  })
  
  // Diversify to ensure coverage
  const diversified = diversify(scored, needs)
  
  // Pack to budget
  return packToBudget(diversified, budget, overrides, agent)
}

// Update context info with assembled results
export function updateContextInfo(
  contextInfo: Record<string, MessageContextInfo[]>,
  assembled: AssembledContext,
  agent: string,
  channelId: string
): Record<string, MessageContextInfo[]> {
  const updated = { ...contextInfo }
  
  if (!updated[channelId]) {
    updated[channelId] = []
  }
  
  const includedIds = new Set(assembled.atoms.map(a => a.id))
  
  // Update context info for each atom
  assembled.atoms.forEach(atom => {
    const info = updated[channelId].find(i => i.id === atom.id)
    
    if (info) {
      // Update existing
      info.included = true
      info.totalTokensInPack += assembled.totalTokens
      
      // Add context use
      const contextUse: ContextUse = {
        agent,
        level: atom.level,
        tokens: estimateTokens(atom),
        reasons: assembled.reasons[atom.id] || ['semantic'],
        score: atom.sig.score
      }
      
      info.uses.push(contextUse)
    } else {
      // Create new
      updated[channelId].push({
        id: atom.id,
        turn: atom.turn[0],
        included: true,
        totalTokensInPack: assembled.totalTokens,
        significance: atom.sig.score,
        relations: atom.rel.map(r => ({
          to: r.to,
          type: r.type,
          strength: r.strength
        })),
        uses: [{
          agent,
          level: atom.level,
          tokens: estimateTokens(atom),
          reasons: assembled.reasons[atom.id] || ['semantic'],
          score: atom.sig.score
        }]
      })
    }
  })
  
  // Mark non-included atoms
  updated[channelId].forEach(info => {
    if (!includedIds.has(info.id)) {
      info.included = false
    }
  })
  
  return updated
}

