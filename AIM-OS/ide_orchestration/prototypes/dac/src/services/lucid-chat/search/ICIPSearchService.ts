/**
 * ICIP Search Service - TypeScript Wrapper
 * 
 * Provides 3-tier semantic code search capabilities:
 * - Tier 1: Literal Search (grep-based)
 * - Tier 2: Structural Search (AST-based)
 * - Tier 3: Semantic Search (intent-based natural language)
 * 
 * Epic 1.3: ICIP Semantic Search Integration
 */

import { BaseAPIService, APIResponse } from '../base/BaseAPIService'

/**
 * Search Tier Types
 */
export type SearchTier = 'literal' | 'structural' | 'semantic'

/**
 * Code Result Type
 */
export type CodeResultType = 'function' | 'class' | 'variable' | 'import' | 'type' | 'interface'

/**
 * ICIP Search Request
 */
export interface ICIPSearchRequest {
  // Required
  query: string
  
  // Search configuration
  searchTier?: SearchTier
  codebase?: string // Path to codebase (default: current workspace)
  
  // Filters
  languages?: string[] // Filter by language (ts, js, py, etc.)
  filePattern?: string // Glob pattern
  excludePatterns?: string[] // Patterns to exclude
  
  // Options
  maxResults?: number
  includeContext?: boolean // Include surrounding code
  contextLines?: number // Lines of context (default: 3)
  
  // Semantic search options (Tier 3)
  semanticOptions?: {
    useNaturalLanguage?: boolean
    expandQuery?: boolean // Query expansion
    rankByRelevance?: boolean
  }
}

/**
 * Code Search Result Item
 */
export interface CodeSearchResultItem {
  // Location
  file: string
  line: number
  column?: number
  
  // Content
  code: string
  context?: string // Surrounding code
  
  // Classification
  type: CodeResultType
  language: string
  symbol?: string // Function/class name
  
  // Quality metrics
  relevance: number // 0-1
  confidence: number // 0-1
  
  // Metadata
  definition?: boolean // Is this the definition?
  usage?: boolean // Is this a usage?
  documentation?: string
}

/**
 * ICIP Search Result
 */
export interface ICIPSearchResult {
  results: CodeSearchResultItem[]
  metadata: {
    query: string
    searchTier: SearchTier
    totalResults: number
    searchTime: number
    languagesSearched: string[]
    filesSearched: number
  }
  suggestions?: string[] // Query suggestions
}

/**
 * ICIP Search Service Implementation
 */
export class ICIPSearchService extends BaseAPIService {
  constructor(commandServerUrl: string = 'http://localhost:5001') {
    super('icip_search', commandServerUrl, undefined, 'icip_search')
  }

  /**
   * Execute ICIP search
   */
  async search(
    request: ICIPSearchRequest
  ): Promise<APIResponse<ICIPSearchResult>> {
    return this.handleRequest(
      async () => {
        // Call ICIP search via Command Server MCP tool
        const response = await fetch(`${this.baseURL}/mcp/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tool: 'icip_search',
            arguments: {
              query: request.query,
              search_tier: request.searchTier || 'semantic',
              codebase: request.codebase || process.cwd(),
              languages: request.languages,
              file_pattern: request.filePattern,
              exclude_patterns: request.excludePatterns,
              max_results: request.maxResults || 20,
              include_context: request.includeContext ?? true,
              context_lines: request.contextLines || 3,
              semantic_options: request.semanticOptions || {},
            },
          }),
        })

        if (!response.ok) {
          throw new Error(`ICIP search failed: ${response.status}`)
        }

        const result = await response.json()
        
        if (!result.success && !result.result) {
          throw new Error(result.error || 'ICIP search failed')
        }

        return result.result || result.data
      },
      'search',
      request
    )
  }

  /**
   * Literal search (Tier 1) - Fast grep-based search
   */
  async literalSearch(
    query: string,
    codebase?: string
  ): Promise<APIResponse<ICIPSearchResult>> {
    return this.search({
      query,
      searchTier: 'literal',
      codebase,
      maxResults: 50,
    })
  }

  /**
   * Structural search (Tier 2) - AST-based pattern matching
   */
  async structuralSearch(
    pattern: string,
    codebase?: string,
    languages?: string[]
  ): Promise<APIResponse<ICIPSearchResult>> {
    return this.search({
      query: pattern,
      searchTier: 'structural',
      codebase,
      languages,
      maxResults: 30,
    })
  }

  /**
   * Semantic search (Tier 3) - Natural language intent-based
   */
  async semanticSearch(
    naturalLanguageQuery: string,
    codebase?: string
  ): Promise<APIResponse<ICIPSearchResult>> {
    return this.search({
      query: naturalLanguageQuery,
      searchTier: 'semantic',
      codebase,
      maxResults: 20,
      semanticOptions: {
        useNaturalLanguage: true,
        expandQuery: true,
        rankByRelevance: true,
      },
    })
  }

  /**
   * Find function definition
   */
  async findFunction(
    functionName: string,
    codebase?: string
  ): Promise<APIResponse<ICIPSearchResult>> {
    return this.structuralSearch(
      `function ${functionName}`,
      codebase,
      ['typescript', 'javascript', 'python']
    )
  }

  /**
   * Find class definition
   */
  async findClass(
    className: string,
    codebase?: string
  ): Promise<APIResponse<ICIPSearchResult>> {
    return this.structuralSearch(
      `class ${className}`,
      codebase,
      ['typescript', 'javascript', 'python']
    )
  }

  /**
   * Find usages of a symbol
   */
  async findUsages(
    symbol: string,
    codebase?: string
  ): Promise<APIResponse<ICIPSearchResult>> {
    return this.search({
      query: symbol,
      searchTier: 'structural',
      codebase,
      maxResults: 100, // Usages can be many
    })
  }

  /**
   * Explain code (semantic)
   */
  async explainCode(
    description: string,
    codebase?: string
  ): Promise<APIResponse<ICIPSearchResult>> {
    return this.semanticSearch(
      `Find code that: ${description}`,
      codebase
    )
  }

  isAvailable(): boolean {
    return true // ICIP search is always available
  }
}

// Singleton instance
let icipSearchServiceInstance: ICIPSearchService | null = null

export function getICIPSearchService(commandServerUrl?: string): ICIPSearchService {
  if (!icipSearchServiceInstance) {
    icipSearchServiceInstance = new ICIPSearchService(commandServerUrl)
  }
  return icipSearchServiceInstance
}

