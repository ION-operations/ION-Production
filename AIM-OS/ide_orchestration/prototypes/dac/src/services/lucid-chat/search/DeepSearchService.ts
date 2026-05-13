/**
 * DEEPSEARCH Service - TypeScript Wrapper
 * 
 * Provides access to the DEEPSEARCH 9-layer sovereign intelligence engine
 * Integrates web crawling, file system search, trust scoring, and knowledge synthesis
 * 
 * Epic 1.2: DEEPSEARCH Full Integration
 */

import { BaseAPIService, APIResponse } from '../base/BaseAPIService'

/**
 * Search Types
 */
export type SearchType = 'web' | 'filesystem' | 'code' | 'mixed'

/**
 * Search Depth
 */
export type SearchDepth = 'basic' | 'advanced' | 'comprehensive'

/**
 * DEEPSEARCH Request
 */
export interface DeepSearchRequest {
  // Required
  query: string
  
  // Search configuration
  searchType?: SearchType
  depth?: number // 1-10 (crawl depth)
  maxResults?: number
  
  // Filters
  filters?: {
    domains?: string[] // Domain filter (include)
    excludeDomains?: string[]
    fileTypes?: string[] // For filesystem search
    trustThreshold?: number // 0-1
    entropyMin?: number // Minimum entropy
    dateAfter?: string // ISO 8601
    dateBefore?: string
  }
  
  // Analysis options
  analysis?: {
    extractMetadata?: boolean
    analyzeCode?: boolean
    classifyDoc?: boolean
    generateSummary?: boolean
  }
  
  // Synthesis options
  synthesis?: {
    useSEG?: boolean // Synthesize with SEG
    detectContradictions?: boolean
    requireCitations?: boolean
  }
}

/**
 * DEEPSEARCH Result Item
 */
export interface DeepSearchResultItem {
  // Core fields
  url: string
  title: string
  summary: string
  content?: string
  
  // Quality metrics
  trustScore: number // 0-1
  entropy: number
  qualityScore: number // Combined metric
  
  // Classification
  tags: string[]
  verified: boolean
  sourceType: 'web' | 'internal_doc' | 'code' | 'sensitive'
  
  // Metadata
  crawlDate: string
  publishDate?: string
  
  // Advanced features
  embeddingVector?: number[]
  codeSnippets?: Array<{
    language: string
    snippet: string
    line?: number
  }>
  manualNotes?: string
  residueHash?: string
}

/**
 * DEEPSEARCH Result
 */
export interface DeepSearchResult {
  results: DeepSearchResultItem[]
  metadata: {
    query: string
    searchType: SearchType
    depth: number
    totalResults: number
    searchTime: number
    providersUsed: string[]
  }
  synthesis?: {
    unifiedAnswer?: string
    contradictions?: Array<{
      item1: string
      item2: string
      description: string
    }>
    keyInsights?: string[]
  }
}

/**
 * DEEPSEARCH Service Implementation
 */
export class DeepSearchService extends BaseAPIService {
  constructor(commandServerUrl: string = 'http://localhost:5001') {
    super('deepsearch', commandServerUrl, undefined, 'deepsearch')
  }

  /**
   * Execute DEEPSEARCH query
   */
  async search(
    request: DeepSearchRequest
  ): Promise<APIResponse<DeepSearchResult>> {
    return this.handleRequest(
      async () => {
        // Call DEEPSEARCH via Command Server MCP tool
        const response = await fetch(`${this.baseURL}/mcp/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tool: 'deepsearch',
            arguments: {
              query: request.query,
              search_type: request.searchType || 'mixed',
              depth: request.depth || 3,
              max_results: request.maxResults || 20,
              filters: request.filters || {},
              analysis: request.analysis || {},
              synthesis: request.synthesis || {},
            },
          }),
        })

        if (!response.ok) {
          throw new Error(`DEEPSEARCH failed: ${response.status}`)
        }

        const result = await response.json()
        
        if (!result.success && !result.result) {
          throw new Error(result.error || 'DEEPSEARCH failed')
        }

        return result.result || result.data
      },
      'search',
      request
    )
  }

  /**
   * Quick web search (basic depth)
   */
  async quickWebSearch(query: string): Promise<APIResponse<DeepSearchResult>> {
    return this.search({
      query,
      searchType: 'web',
      depth: 1,
      maxResults: 5,
    })
  }

  /**
   * Deep research (comprehensive depth)
   */
  async deepResearch(query: string): Promise<APIResponse<DeepSearchResult>> {
    return this.search({
      query,
      searchType: 'mixed',
      depth: 5,
      maxResults: 20,
      analysis: {
        extractMetadata: true,
        generateSummary: true,
      },
      synthesis: {
        useSEG: true,
        detectContradictions: true,
        requireCitations: true,
      },
    })
  }

  /**
   * Code search in filesystem
   */
  async searchCode(
    query: string,
    codebasePath?: string
  ): Promise<APIResponse<DeepSearchResult>> {
    return this.search({
      query,
      searchType: 'code',
      depth: 3,
      maxResults: 20,
      filters: {
        fileTypes: ['.ts', '.tsx', '.js', '.jsx', '.py', '.java', '.cpp'],
      },
      analysis: {
        analyzeCode: true,
      },
    })
  }

  /**
   * Search local documents
   */
  async searchDocuments(query: string): Promise<APIResponse<DeepSearchResult>> {
    return this.search({
      query,
      searchType: 'filesystem',
      depth: 2,
      filters: {
        fileTypes: ['.md', '.txt', '.pdf', '.docx'],
      },
      analysis: {
        extractMetadata: true,
        classifyDoc: true,
      },
    })
  }

  isAvailable(): boolean {
    return true // DEEPSEARCH is always available
  }
}

// Singleton instance
let deepSearchServiceInstance: DeepSearchService | null = null

export function getDeepSearchService(commandServerUrl?: string): DeepSearchService {
  if (!deepSearchServiceInstance) {
    deepSearchServiceInstance = new DeepSearchService(commandServerUrl)
  }
  return deepSearchServiceInstance
}

