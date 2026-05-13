/**
 * Retriever Role Executor
 * 
 * Specializes in knowledge retrieval from HHNI and CMC
 * Temperature: 0.1 (precise retrieval)
 * 
 * Epic 1.1: Complete APOE Execution
 */

import { RoleExecutor, RoleContext, RoleExecutionResult } from './RoleExecutor'
import { LLMService } from '../llm/LLMService'

/**
 * Retrieval Result Structure
 */
export interface RetrievalResult {
  query: string
  results: Array<{
    source: 'hhni' | 'cmc' | 'seg'
    content: string
    relevance: number
    metadata?: Record<string, any>
  }>
  total_results: number
  retrieval_time: number
  context_assembled: string
}

/**
 * Retriever Executor Implementation
 */
export class RetrieverExecutor extends RoleExecutor {
  constructor(llmService: LLMService, commandServerUrl?: string) {
    super(
      {
        role: 'retriever',
      },
      llmService,
      commandServerUrl
    )
  }

  async execute(
    input: any,
    context: RoleContext
  ): Promise<RoleExecutionResult> {
    this.validateInput(input)
    this.validateContext(context)

    const startTime = Date.now()

    try {
      // Build retrieval query
      const query = input.query || input.topic || context.goal

      // Retrieve from HHNI
      const hhniResults = await this.retrieveFromHHNI(query)

      // Retrieve from CMC
      const cmcResults = await this.retrieveFromCMC(query)

      // Assemble context
      const assembledContext = this.assembleContext(hhniResults, cmcResults)

      // Build result
      const retrievalResult: RetrievalResult = {
        query,
        results: [...hhniResults, ...cmcResults],
        total_results: hhniResults.length + cmcResults.length,
        retrieval_time: Date.now() - startTime,
        context_assembled: assembledContext,
      }

      const result: RoleExecutionResult = {
        role: 'retriever',
        input,
        output: retrievalResult,
        success: true,
        confidence: this.calculateRetrievalConfidence(retrievalResult),
        tokensUsed: Math.floor(assembledContext.length / 4), // Approximate
        latencyMs: Date.now() - startTime,
        reasoning: `Retrieved ${retrievalResult.total_results} results`,
        metadata: {
          sources_used: ['hhni', 'cmc'],
          total_results: retrievalResult.total_results,
        },
      }

      // Track with VIF
      await this.trackExecution(result)

      // Store in CMC
      await this.storeResult(result, context)

      return result
    } catch (error: any) {
      return {
        role: 'retriever',
        input,
        output: null,
        success: false,
        confidence: 0,
        tokensUsed: 0,
        latencyMs: Date.now() - startTime,
        error: error.message,
      }
    }
  }

  /**
   * Retrieve from HHNI
   */
  private async retrieveFromHHNI(query: string): Promise<any[]> {
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: 'retrieve_memory',
          arguments: {
            query,
            limit: 10,
          },
        }),
      })

      const result = await response.json()
      
      return (result.result?.memories || []).map((m: any) => ({
        source: 'hhni',
        content: m.content || m,
        relevance: m.relevance || 0.8,
        metadata: m.metadata,
      }))
    } catch (error) {
      console.warn('HHNI retrieval failed:', error)
      return []
    }
  }

  /**
   * Retrieve from CMC
   */
  private async retrieveFromCMC(query: string): Promise<any[]> {
    // CMC retrieval happens through retrieve_memory tool (HHNI indexes CMC)
    // So this is effectively the same as HHNI retrieval
    // We could add specific CMC filters here if needed
    return []
  }

  /**
   * Assemble context from results
   */
  private assembleContext(hhniResults: any[], cmcResults: any[]): string {
    let context = '**Retrieved Context:**\n\n'
    
    const allResults = [...hhniResults, ...cmcResults]
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, 5) // Top 5 results
    
    allResults.forEach((result, i) => {
      context += `${i + 1}. [${result.source.toUpperCase()}] ${result.content.slice(0, 200)}...\n\n`
    })
    
    return context
  }

  /**
   * Calculate retrieval confidence
   */
  private calculateRetrievalConfidence(result: RetrievalResult): number {
    if (result.total_results === 0) {
      return 0.3 // Low confidence if no results
    }
    
    // Average relevance of top results
    const avgRelevance = result.results
      .slice(0, 5)
      .reduce((sum, r) => sum + r.relevance, 0) / Math.min(5, result.results.length)
    
    return avgRelevance
  }
}

