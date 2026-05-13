/**
 * Branch Reasoning Service
 * 
 * Enables parallel exploration of multiple solution paths
 * Evaluates hypotheses, prunes weak branches, selects best solution
 * 
 * Epic 2.1: Branch Reasoning Integration
 */

import { LLMService, LLMProvider } from '../llm/LLMService'
import { APIResponse } from '../base/BaseAPIService'

/**
 * Reasoning Branch
 */
export interface ReasoningBranch {
  id: string
  hypothesis: string
  reasoning: string[]
  evidence: any[]
  confidence: number
  qualityScore: number
  metadata?: {
    temperature?: number
    tokensUsed?: number
    latencyMs?: number
  }
}

/**
 * Branch Reasoning Request
 */
export interface BranchReasoningRequest {
  problem: string
  numBranches?: number // Number of hypotheses to explore (default: 3)
  pruneThreshold?: number // Confidence threshold for pruning (default: 0.70)
  provider?: LLMProvider
  maxTokensPerBranch?: number
}

/**
 * Branch Reasoning Result
 */
export interface BranchReasoningResult {
  problem: string
  allBranches: ReasoningBranch[]
  prunedBranches: ReasoningBranch[]
  bestBranch: ReasoningBranch
  reasoning: string[]
  finalAnswer: string
  metadata: {
    totalBranches: number
    branchesKept: number
    branchesPruned: number
    totalTime: number
    totalTokens: number
  }
}

/**
 * Branch Reasoning Service Implementation
 */
export class BranchReasoningService {
  private llmService: LLMService
  private commandServerUrl: string

  constructor(llmService: LLMService, commandServerUrl: string = 'http://localhost:5001') {
    this.llmService = llmService
    this.commandServerUrl = commandServerUrl
  }

  /**
   * Reason through problem using multiple branches
   */
  async reasonWithBranches(
    request: BranchReasoningRequest
  ): Promise<APIResponse<BranchReasoningResult>> {
    const startTime = Date.now()
    const numBranches = request.numBranches || 3
    const pruneThreshold = request.pruneThreshold || 0.70
    const provider = request.provider || 'anthropic'

    try {
      // Step 1: Generate hypotheses (different approaches)
      const hypotheses = await this.generateHypotheses(
        request.problem,
        numBranches,
        provider
      )

      // Step 2: Reason through each branch in parallel
      const branches = await Promise.all(
        hypotheses.map((hypothesis, i) =>
          this.reasonThroughBranch(
            hypothesis,
            request.problem,
            i,
            provider,
            request.maxTokensPerBranch
          )
        )
      )

      // Step 3: Evaluate branches
      const evaluated = await this.evaluateBranches(branches, request.problem, provider)

      // Step 4: Prune low-confidence branches
      const pruned = this.pruneBranches(evaluated, pruneThreshold)

      // Step 5: Select best branch
      const best = this.selectBestBranch(pruned)

      // Step 6: Store in CMC for learning
      await this.storeBranchReasoning(branches, best, request.problem)

      // Build result
      const result: BranchReasoningResult = {
        problem: request.problem,
        allBranches: branches,
        prunedBranches: pruned,
        bestBranch: best,
        reasoning: best.reasoning,
        finalAnswer: this.extractFinalAnswer(best),
        metadata: {
          totalBranches: branches.length,
          branchesKept: pruned.length,
          branchesPruned: branches.length - pruned.length,
          totalTime: Date.now() - startTime,
          totalTokens: branches.reduce((sum, b) => sum + (b.metadata?.tokensUsed || 0), 0),
        },
      }

      return {
        success: true,
        data: result,
      }
    } catch (error: any) {
      return {
        success: false,
        error: error.message,
      }
    }
  }

  /**
   * Generate hypotheses (different approaches to the problem)
   */
  private async generateHypotheses(
    problem: string,
    numBranches: number,
    provider: LLMProvider
  ): Promise<string[]> {
    const prompt = `Generate ${numBranches} different hypotheses or approaches to solve this problem:

Problem: ${problem}

For each hypothesis, provide a distinct approach (not just variations).

Examples of distinct approaches:
1. Deductive reasoning from first principles
2. Inductive reasoning from examples
3. Analogical reasoning from similar cases
4. Abductive reasoning (best explanation)

Return as JSON array of strings:
["Hypothesis 1: ...", "Hypothesis 2: ...", "Hypothesis 3: ..."]`

    const response = await this.llmService.complete(
      prompt,
      provider,
      undefined,
      0.8, // High temperature for diverse hypotheses
      2000
    )

    if (!response.success || !response.data) {
      throw new Error('Failed to generate hypotheses')
    }

    // Parse hypotheses from response
    try {
      const jsonMatch = response.data.text.match(/\[[\s\S]*\]/)
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0])
      }
    } catch (error) {
      // Fallback: Split by newlines
    }

    // Fallback: Extract from text
    const lines = response.data.text
      .split('\n')
      .filter(line => line.trim().length > 0)
      .slice(0, numBranches)

    return lines.length > 0 ? lines : [
      'Approach 1: Direct logical analysis',
      'Approach 2: Pattern-based reasoning',
      'Approach 3: Example-driven solution',
    ]
  }

  /**
   * Reason through a single branch
   */
  private async reasonThroughBranch(
    hypothesis: string,
    problem: string,
    branchIndex: number,
    provider: LLMProvider,
    maxTokens?: number
  ): Promise<ReasoningBranch> {
    const startTime = Date.now()

    const prompt = `Using this hypothesis/approach: "${hypothesis}"

Solve this problem: ${problem}

Show your reasoning step-by-step:
1. Start with the hypothesis
2. Build reasoning chain
3. Reach a conclusion
4. Assess your confidence (0-1)

Provide detailed reasoning for each step.`

    const response = await this.llmService.complete(
      prompt,
      provider,
      undefined,
      0.5, // Moderate temperature for reasoning
      maxTokens || 3000
    )

    if (!response.success || !response.data) {
      return {
        id: `branch_${branchIndex}`,
        hypothesis,
        reasoning: ['Failed to generate reasoning'],
        evidence: [],
        confidence: 0.1,
        qualityScore: 0.1,
        metadata: {
          tokensUsed: 0,
          latencyMs: Date.now() - startTime,
        },
      }
    }

    // Extract reasoning steps
    const reasoningSteps = this.extractReasoningSteps(response.data.text)

    // Extract confidence
    const confidence = this.extractConfidence(response.data.text) || response.data.confidence || 0.7

    return {
      id: `branch_${branchIndex}`,
      hypothesis,
      reasoning: reasoningSteps,
      evidence: [],
      confidence,
      qualityScore: confidence, // Initially same as confidence
      metadata: {
        temperature: 0.5,
        tokensUsed: response.data.tokensUsed,
        latencyMs: Date.now() - startTime,
      },
    }
  }

  /**
   * Extract reasoning steps from LLM response
   */
  private extractReasoningSteps(text: string): string[] {
    const steps: string[] = []

    // Look for numbered steps
    const stepMatches = text.match(/(?:^|\n)(\d+)\.\s+([^\n]+)/g)

    if (stepMatches) {
      stepMatches.forEach(match => {
        const step = match.replace(/^\s*\d+\.\s+/, '').trim()
        if (step.length > 0) {
          steps.push(step)
        }
      })
    }

    // If no numbered steps, split by paragraphs
    if (steps.length === 0) {
      const paragraphs = text.split('\n\n').filter(p => p.trim().length > 0)
      steps.push(...paragraphs.slice(0, 5))
    }

    return steps
  }

  /**
   * Extract confidence from text
   */
  private extractConfidence(text: string): number | null {
    // Look for explicit confidence statements
    const confidenceMatch = text.match(/confidence[:\s]+(\d+\.?\d*)/) ||
                          text.match(/(\d+\.?\d*)\s*confidence/) ||
                          text.match(/(\d+)%\s*confident/)

    if (confidenceMatch) {
      const value = parseFloat(confidenceMatch[1])
      return value > 1 ? value / 100 : value // Convert percentage if needed
    }

    return null
  }

  /**
   * Evaluate branches comparatively
   */
  private async evaluateBranches(
    branches: ReasoningBranch[],
    problem: string,
    provider: LLMProvider
  ): Promise<ReasoningBranch[]> {
    const prompt = `Evaluate these different approaches to solving the problem:

Problem: ${problem}

Approaches:
${branches.map((b, i) => `
${i + 1}. ${b.hypothesis}
   Reasoning: ${b.reasoning.slice(0, 3).join('; ')}...
   Initial Confidence: ${b.confidence.toFixed(2)}
`).join('\n')}

For each approach, assess:
1. Logical soundness (0-1)
2. Completeness (0-1)
3. Practicality (0-1)
4. Overall quality score (0-1)

Return as JSON array:
[
  { "branch": 0, "soundness": 0.9, "completeness": 0.8, "practicality": 0.85, "quality": 0.85 },
  ...
]`

    const response = await this.llmService.complete(
      prompt,
      provider,
      undefined,
      0.3, // Low temperature for objective evaluation
      2000
    )

    if (!response.success || !response.data) {
      return branches // Return unchanged if evaluation fails
    }

    // Parse evaluation
    try {
      const jsonMatch = response.data.text.match(/\[[\s\S]*\]/)
      if (jsonMatch) {
        const evaluations = JSON.parse(jsonMatch[0])

        return branches.map((branch, i) => {
          const eval = evaluations[i] || {}
          return {
            ...branch,
            qualityScore: eval.quality || branch.confidence,
            evidence: [
              `Soundness: ${eval.soundness || 'N/A'}`,
              `Completeness: ${eval.completeness || 'N/A'}`,
              `Practicality: ${eval.practicality || 'N/A'}`,
            ],
          }
        })
      }
    } catch (error) {
      // Evaluation parsing failed, return unchanged
    }

    return branches
  }

  /**
   * Prune branches below confidence threshold
   */
  private pruneBranches(
    branches: ReasoningBranch[],
    threshold: number
  ): ReasoningBranch[] {
    return branches.filter(b => b.confidence >= threshold && b.qualityScore >= threshold)
  }

  /**
   * Select best branch based on quality score
   */
  private selectBestBranch(branches: ReasoningBranch[]): ReasoningBranch {
    if (branches.length === 0) {
      throw new Error('No branches passed pruning threshold')
    }

    return branches.reduce((best, current) =>
      current.qualityScore > best.qualityScore ? current : best
    )
  }

  /**
   * Extract final answer from best branch
   */
  private extractFinalAnswer(branch: ReasoningBranch): string {
    // Last reasoning step is typically the conclusion
    return branch.reasoning[branch.reasoning.length - 1] || branch.hypothesis
  }

  /**
   * Store branch reasoning in CMC for learning
   */
  private async storeBranchReasoning(
    branches: ReasoningBranch[],
    bestBranch: ReasoningBranch,
    problem: string
  ): Promise<void> {
    try {
      await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: 'store_memory',
          arguments: {
            content: JSON.stringify({
              problem,
              branches: branches.map(b => ({
                hypothesis: b.hypothesis,
                confidence: b.confidence,
                qualityScore: b.qualityScore,
              })),
              bestBranch: {
                hypothesis: bestBranch.hypothesis,
                reasoning: bestBranch.reasoning,
                confidence: bestBranch.confidence,
              },
            }),
            memory_type: 'branch_reasoning',
            tags: ['branch_reasoning', 'problem_solving'],
            metadata: {
              problem,
              timestamp: new Date().toISOString(),
              branches_explored: branches.length,
              best_confidence: bestBranch.confidence,
            },
          },
        }),
      })
    } catch (error) {
      console.warn('Failed to store branch reasoning:', error)
    }
  }
}

// Singleton instance
let branchReasoningServiceInstance: BranchReasoningService | null = null

export function getBranchReasoningService(
  llmService: LLMService,
  commandServerUrl?: string
): BranchReasoningService {
  if (!branchReasoningServiceInstance) {
    branchReasoningServiceInstance = new BranchReasoningService(llmService, commandServerUrl)
  }
  return branchReasoningServiceInstance
}

