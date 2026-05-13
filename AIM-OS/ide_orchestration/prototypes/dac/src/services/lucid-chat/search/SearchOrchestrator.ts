/**
 * Search Orchestrator
 * 
 * Unified orchestration for all search providers:
 * - DEEPSEARCH (sovereign intelligence)
 * - ICIP (semantic code search)
 * - Perplexity (AI web search)
 * - Tavily (research)
 * - Web (fallback)
 * 
 * Epic 1.3: ICIP Semantic Search Integration
 */

import { DeepSearchService, getDeepSearchService } from './DeepSearchService'
import { ICIPSearchService, getICIPSearchService } from './ICIPSearchService'

/**
 * Search Provider Type
 */
export type SearchProvider = 'deepsearch' | 'icip' | 'perplexity' | 'tavily' | 'web'

/**
 * Unified Search Request
 */
export interface UnifiedSearchRequest {
  query: string
  providers?: SearchProvider[]
  depth?: 'basic' | 'advanced' | 'comprehensive'
  maxResultsPerProvider?: number
  synthesize?: boolean
  includeCodeSearch?: boolean
}

/**
 * Unified Search Result
 */
export interface UnifiedSearchResult {
  query: string
  results: {
    deepsearch?: any[]
    icip?: any[]
    perplexity?: any[]
    tavily?: any[]
    web?: any[]
  }
  aggregated: any[] // Deduplicated and ranked
  metadata: {
    totalResults: number
    providersUsed: string[]
    searchTime: number
  }
  synthesis?: {
    summary: string
    keyInsights: string[]
    citations: Array<{ source: string; url: string }>
  }
}

/**
 * Search Orchestrator Implementation
 */
export class SearchOrchestrator {
  private deepSearchService: DeepSearchService
  private icipSearchService: ICIPSearchService
  private commandServerUrl: string

  constructor(commandServerUrl: string = 'http://localhost:5001') {
    this.commandServerUrl = commandServerUrl
    this.deepSearchService = getDeepSearchService(commandServerUrl)
    this.icipSearchService = getICIPSearchService(commandServerUrl)
  }

  /**
   * Execute unified search across all providers
   */
  async search(request: UnifiedSearchRequest): Promise<UnifiedSearchResult> {
    const startTime = Date.now()
    const providers = request.providers || ['deepsearch', 'icip', 'perplexity']
    const results: any = {}

    // Execute all searches in parallel
    const searchPromises = providers.map(async (provider) => {
      try {
        if (provider === 'deepsearch') {
          const response = await this.deepSearchService.search({
            query: request.query,
            searchType: 'mixed',
            depth: this.mapDepth(request.depth),
            maxResults: request.maxResultsPerProvider || 20,
          })
          if (response.success && response.data) {
            results.deepsearch = response.data.results
          }
        }
        else if (provider === 'icip') {
          const response = await this.icipSearchService.semanticSearch(
            request.query
          )
          if (response.success && response.data) {
            results.icip = response.data.results
          }
        }
        else if (provider === 'perplexity') {
          // Call via Command Server
          const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              tool: 'call_api',
              arguments: {
                provider: 'perplexity',
                endpoint: 'chat-completion',
                method: 'POST',
                data: {
                  model: 'llama-3.1-sonar-large-128k-online',
                  messages: [{ role: 'user', content: request.query }],
                  return_citations: true,
                },
              },
            }),
          })
          const result = await response.json()
          if (result.success && result.data) {
            results.perplexity = result.data.citations || []
          }
        }
        else if (provider === 'tavily') {
          const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              tool: 'call_api',
              arguments: {
                provider: 'tavily',
                endpoint: 'search',
                method: 'POST',
                data: {
                  query: request.query,
                  search_depth: request.depth || 'advanced',
                  include_answer: true,
                },
              },
            }),
          })
          const result = await response.json()
          if (result.success && result.data) {
            results.tavily = result.data.results || []
          }
        }
      } catch (error) {
        console.warn(`[SearchOrchestrator] ${provider} failed:`, error)
      }
    })

    await Promise.all(searchPromises)

    // Aggregate and deduplicate results
    const aggregated = this.aggregateResults(results)

    // Synthesize if requested
    let synthesis
    if (request.synthesize) {
      synthesis = await this.synthesizeResults(aggregated)
    }

    return {
      query: request.query,
      results,
      aggregated,
      metadata: {
        totalResults: Object.values(results).reduce(
          (sum: number, arr: any[]) => sum + (arr?.length || 0),
          0
        ),
        providersUsed: Object.keys(results),
        searchTime: Date.now() - startTime,
      },
      synthesis,
    }
  }

  /**
   * Map depth to numeric value
   */
  private mapDepth(depth?: 'basic' | 'advanced' | 'comprehensive'): number {
    const depthMap = { basic: 1, advanced: 3, comprehensive: 5 }
    return depthMap[depth || 'advanced']
  }

  /**
   * Aggregate and deduplicate results
   */
  private aggregateResults(results: any): any[] {
    const aggregated: any[] = []
    const seen = new Set<string>()

    // Add all results with deduplication
    for (const providerResults of Object.values(results)) {
      if (!Array.isArray(providerResults)) continue

      for (const result of providerResults) {
        const key = result.url || result.file || result.title
        if (!seen.has(key)) {
          seen.add(key)
          aggregated.push(result)
        }
      }
    }

    // Sort by relevance/trust score
    aggregated.sort((a, b) => {
      const scoreA = a.relevance || a.trustScore || a.score || 0
      const scoreB = b.relevance || b.trustScore || b.score || 0
      return scoreB - scoreA
    })

    return aggregated
  }

  /**
   * Synthesize results using SEG
   */
  private async synthesizeResults(results: any[]): Promise<any> {
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: 'synthesize_knowledge',
          arguments: {
            topics: results.map(r => r.title || r.summary || r.code).slice(0, 10),
            depth: 'medium',
            format: 'summary',
          },
        }),
      })

      const result = await response.json()
      return result.data || {}
    } catch (error) {
      console.warn('[SearchOrchestrator] Synthesis failed:', error)
      return {}
    }
  }
}

// Singleton instance
let searchOrchestratorInstance: SearchOrchestrator | null = null

export function getSearchOrchestrator(commandServerUrl?: string): SearchOrchestrator {
  if (!searchOrchestratorInstance) {
    searchOrchestratorInstance = new SearchOrchestrator(commandServerUrl)
  }
  return searchOrchestratorInstance
}

