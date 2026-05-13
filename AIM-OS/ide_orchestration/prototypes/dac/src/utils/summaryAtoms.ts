// Summary Atom Types and Significance Scoring
// Part of AI Chat System Enhancement: Significance Scoring & Typed Relationships

export type AtomLevel = "micro" | "meso" | "macro"
export type ClaimKind = "decision" | "fact" | "hypothesis" | "task"
export type RelationshipType = "supports" | "contradicts" | "depends_on" | "alternative_to" | "duplicates" | "resolves"

export interface Claim {
  id: string
  text: string
  kind: ClaimKind
  objects: string[]  // Symbols/files/APIs
  evidence: string[]  // SEG ids (CMC atoms, VIF witnesses)
  quality: {
    conf: number  // Confidence score [0,1]
    tests?: number  // Number of tests added
    gates?: string[]  // VIF gate IDs
  }
}

export interface SignificanceBreakdown {
  usage: number  // Opens, clicks, references, agent-loads [0,1]
  impact: number  // Tests added, bugs fixed, perf gain [0,1]
  novelty: number  // New symbols/edges introduced [0,1]
  recency: number  // Exponential decay [0,1]
  pins: number  // User pin (0 or 1)
}

export interface Significance {
  score: number  // Bounded [0,1] composite score
  breakdown: SignificanceBreakdown
  halfLifeDays: number  // Decay control (default: 30)
}

export interface Relationship {
  to: string  // Other atom id
  type: RelationshipType
  strength: number  // [0,1] cosine similarity × confidence
  objects?: string[]  // Overlapping symbols
}

export interface SummaryAtom {
  id: string  // ULID/hash (from message.id)
  level: AtomLevel  // Granularity level
  title: string  // Canonical, terse title
  turn: [number, number]  // Turn range covered [t0, t1]
  recap: string  // Natural-language recap (from message.content)
  updatedAt: string  // ISO timestamp
  
  claims: Claim[]
  sig: Significance
  rel: Relationship[]
}

export interface ContextUse {
  agent: string  // "coding" | "planning" | `tool:${string}`
  level: AtomLevel | "raw"
  tokens: number
  reasons: Array<"recency" | "semantic" | "symbolic" | "pin" | "dependency">
  score: number  // Per-agent selection score
}

export interface MessageContextInfo {
  id: string  // Message ID
  turn: number
  included: boolean  // Included in ANY agent's pack this turn
  totalTokensInPack: number  // Sum across agents
  significance: number  // Precomputed sig.score
  relations: Array<{
    to: string
    type: RelationshipType
    strength: number
  }>
  uses: ContextUse[]
}

export interface ContextOverride {
  id: string  // Message ID
  pinned?: boolean
  forcedLevel?: AtomLevel | "raw"
  priority?: number  // -1..+1 (salience delta)
  ttlTurns?: number  // Optional decay window
}

// Significance scoring weights (learnable, but fixed for now)
export const SIGNIFICANCE_WEIGHTS = {
  usage: 0.40,
  impact: 0.25,
  novelty: 0.20,
  recency: 0.10,
  pins: 0.05
} as const

// Sigmoid function for bounded output
function sigmoid(x: number): number {
  return 1 / (1 + Math.exp(-x))
}

// Clamp value to [0,1]
function clamp01(n: number): number {
  return Math.max(0, Math.min(1, n))
}

// Normalize log counts for usage
export function normalizeUsage(count: number): number {
  return clamp01(Math.log(1 + count) / Math.log(100))  // Normalize to [0,1] for counts up to 100
}

// Compute recency score with exponential decay
export function computeRecency(timestamp: Date, halfLifeDays: number = 30): number {
  const now = Date.now()
  const ageMs = now - timestamp.getTime()
  const ageDays = ageMs / (1000 * 60 * 60 * 24)
  const tau = halfLifeDays
  return Math.exp(-ageDays / tau)
}

// Compute novelty score (Jaccard distance of symbols vs. prior atoms)
export function computeNovelty(
  currentSymbols: string[],
  priorSymbols: Set<string>
): number {
  if (currentSymbols.length === 0) return 0
  
  const currentSet = new Set(currentSymbols)
  const intersection = new Set([...currentSet].filter(x => priorSymbols.has(x)))
  const union = new Set([...currentSet, ...priorSymbols])
  
  if (union.size === 0) return 0
  
  // Jaccard distance = 1 - Jaccard similarity
  const jaccardSimilarity = intersection.size / union.size
  return 1 - jaccardSimilarity
}

// Compute significance score from breakdown
export function computeSignificanceScore(breakdown: SignificanceBreakdown): number {
  const weightedSum =
    SIGNIFICANCE_WEIGHTS.usage * breakdown.usage +
    SIGNIFICANCE_WEIGHTS.impact * breakdown.impact +
    SIGNIFICANCE_WEIGHTS.novelty * breakdown.novelty +
    SIGNIFICANCE_WEIGHTS.recency * breakdown.recency +
    SIGNIFICANCE_WEIGHTS.pins * breakdown.pins
  
  // Apply sigmoid for bounded output [0,1]
  return clamp01(sigmoid(weightedSum * 2 - 1))  // Scale to [-1,1] then sigmoid
}

// Extract symbols from work references
export function extractSymbols(workReferences?: {
  files?: Array<{ path: string; operation?: string; lines?: number[] }>
  cmc_atoms?: string[]
  goals?: string[]
  timeline_entries?: string[]
  git_commits?: string[]
}): string[] {
  const symbols: string[] = []
  
  if (workReferences?.files) {
    workReferences.files.forEach(file => {
      symbols.push(file.path)
      // Extract function/class names from path if possible
      const parts = file.path.split('/')
      const fileName = parts[parts.length - 1]
      if (fileName) {
        symbols.push(fileName.replace(/\.[^.]+$/, ''))  // Remove extension
      }
    })
  }
  
  if (workReferences?.cmc_atoms) {
    symbols.push(...workReferences.cmc_atoms)
  }
  
  if (workReferences?.goals) {
    symbols.push(...workReferences.goals)
  }
  
  if (workReferences?.timeline_entries) {
    symbols.push(...workReferences.timeline_entries)
  }
  
  if (workReferences?.git_commits) {
    symbols.push(...workReferences.git_commits)
  }
  
  return symbols
}

// Extract claims from message content and work references
export function extractClaims(
  content: string,
  workReferences?: {
    files?: Array<{ path: string; operation?: string; lines?: number[] }>
    cmc_atoms?: string[]
    vif_witnesses?: string[]
    goals?: string[]
  },
  confidence?: number,
  goalAlignment?: {
    objective?: string
    key_result?: string
    progress?: number
  }
): Claim[] {
  const claims: Claim[] = []
  const symbols = extractSymbols(workReferences)
  const evidence: string[] = []
  
  if (workReferences?.cmc_atoms) {
    evidence.push(...workReferences.cmc_atoms)
  }
  
  if (workReferences?.vif_witnesses) {
    evidence.push(...workReferences.vif_witnesses)
  }
  
  // Extract task claims from goal alignment
  if (goalAlignment?.objective) {
    claims.push({
      id: `claim_${goalAlignment.objective}_${Date.now()}`,
      text: `Working on ${goalAlignment.objective}${goalAlignment.key_result ? ` (${goalAlignment.key_result})` : ''}`,
      kind: "task",
      objects: goalAlignment.key_result ? [goalAlignment.objective, goalAlignment.key_result] : [goalAlignment.objective],
      evidence,
      quality: {
        conf: confidence ?? 0.5,
        gates: workReferences?.vif_witnesses
      }
    })
  }
  
  // Extract decision claims from message content (simple heuristic)
  const decisionKeywords = ['decided', 'chose', 'selected', 'adopted', 'implemented', 'removed', 'refactored']
  const factKeywords = ['completed', 'fixed', 'added', 'created', 'modified']
  const hypothesisKeywords = ['think', 'believe', 'suggest', 'propose', 'hypothesis']
  
  const lowerContent = content.toLowerCase()
  
  // Check for decision patterns
  if (decisionKeywords.some(kw => lowerContent.includes(kw))) {
    claims.push({
      id: `claim_decision_${Date.now()}`,
      text: content.slice(0, 200),  // Truncate for claim text
      kind: "decision",
      objects: symbols,
      evidence,
      quality: {
        conf: confidence ?? 0.5
      }
    })
  }
  
  // Check for fact patterns
  if (factKeywords.some(kw => lowerContent.includes(kw))) {
    claims.push({
      id: `claim_fact_${Date.now()}`,
      text: content.slice(0, 200),
      kind: "fact",
      objects: symbols,
      evidence,
      quality: {
        conf: confidence ?? 0.5
      }
    })
  }
  
  // Check for hypothesis patterns
  if (hypothesisKeywords.some(kw => lowerContent.includes(kw))) {
    claims.push({
      id: `claim_hypothesis_${Date.now()}`,
      text: content.slice(0, 200),
      kind: "hypothesis",
      objects: symbols,
      evidence,
      quality: {
        conf: confidence ?? 0.5
      }
    })
  }
  
  // If no claims extracted, create a default fact claim
  if (claims.length === 0) {
    claims.push({
      id: `claim_default_${Date.now()}`,
      text: content.slice(0, 200),
      kind: "fact",
      objects: symbols,
      evidence,
      quality: {
        conf: confidence ?? 0.5
      }
    })
  }
  
  return claims
}

// Determine atom level from message characteristics
export function determineAtomLevel(
  content: string,
  claims: Claim[],
  workReferences?: {
    files?: Array<{ path: string }>
  }
): AtomLevel {
  const contentLength = content.length
  const fileCount = workReferences?.files?.length ?? 0
  const claimCount = claims.length
  
  // Macro: Long content, many files, many claims
  if (contentLength > 1000 || fileCount > 5 || claimCount > 3) {
    return "macro"
  }
  
  // Meso: Medium content, some files, some claims
  if (contentLength > 300 || fileCount > 1 || claimCount > 1) {
    return "meso"
  }
  
  // Micro: Short content, single file, single claim
  return "micro"
}

// Generate terse title from content
export function generateTitle(content: string, maxLength: number = 60): string {
  // Extract first sentence or first N characters
  const firstSentence = content.split(/[.!?]/)[0]
  if (firstSentence.length <= maxLength) {
    return firstSentence.trim()
  }
  
  // Truncate to maxLength with ellipsis
  return content.slice(0, maxLength - 3).trim() + "..."
}

