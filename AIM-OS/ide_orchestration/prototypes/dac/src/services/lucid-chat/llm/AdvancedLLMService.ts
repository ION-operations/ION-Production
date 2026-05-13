/**
 * Advanced LLM Service with Extreme Adjustability
 * Integrates with AIM-OS systems (APOE, SEG, VIF, CAS) for sophisticated output
 * 
 * Phase 4: Advanced LLM Integration
 */

import { LLMService, LLMProvider, LLMModel, LLMMessage, LLMChatRequest, LLMChatResponse } from './LLMService'
import { BaseAPIService, APIResponse } from '../base/BaseAPIService'
import type { IntegrationTagContext } from '../../../utils/integrationTags'

/**
 * Deep search results type
 */
interface DeepSearchResults {
  deepsearch: any[]
  perplexity: any[]
  tavily: any[]
  icip: any[]
  web: any[]
}

/**
 * Output Protocol Types
 */
export type OutputFormat = 'markdown' | 'code' | 'json' | 'table' | 'diagram' | 'mixed'
export type OutputStyle = 'concise' | 'detailed' | 'conversational' | 'technical' | 'creative'
export type OutputTone = 'professional' | 'casual' | 'friendly' | 'formal' | 'witty'

/**
 * Thinking Modes - Adjustable reasoning types
 */
export type ThinkingMode = 'creative' | 'analytical' | 'balanced' | 'reasoning' | 'intuitive'
export type ReasoningType = 'deductive' | 'inductive' | 'abductive' | 'analogical'

/**
 * Deep Search Configuration
 */
export interface DeepSearchConfig {
  // Search providers
  providers?: Array<'deepsearch' | 'perplexity' | 'tavily' | 'icip' | 'web'>
  
  // Search depth
  depth?: 'basic' | 'advanced' | 'comprehensive'
  
  // Crawling
  enableCrawling?: boolean
  crawlDepth?: number
  crawlTimeout?: number
  
  // Filtering
  domainFilter?: string[]
  dateFilter?: { after?: string; before?: string }
  trustThreshold?: number
  
  // Synthesis
  synthesizeResults?: boolean // Use SEG
  detectContradictions?: boolean
  requireCitations?: boolean
}

/**
 * Advanced Prompting Configuration
 */
export interface AdvancedPromptConfig {
  // System prompt engineering
  systemPrompt?: string
  role?: string // "You are an expert..."
  behaviorGuidelines?: string[]
  outputFormat?: OutputFormat
  outputStyle?: OutputStyle
  outputTone?: OutputTone
  
  // Few-shot examples
  fewShotExamples?: Array<{
    input: string
    output: string
    explanation?: string
  }>
  
  // Chain-of-thought
  useChainOfThought?: boolean
  reasoningSteps?: number
  
  // Structured output
  requireStructuredOutput?: boolean
  outputSchema?: Record<string, any> // JSON Schema
  
  // Context management
  includeContext?: boolean
  contextSources?: string[] // HHNI, CMC, SEG, etc.
  maxContextTokens?: number
  
  // Quality assurance
  requireCitations?: boolean
  requireVerification?: boolean
  confidenceThreshold?: number
  
  // Dynamic adaptation
  adaptToUser?: boolean
  learnFromHistory?: boolean
  personalizeOutput?: boolean
}

/**
 * APOE Role Configuration for LLM Output
 */
export interface APOERoleConfig {
  useAPOE?: boolean
  roles?: Array<{
    role: 'planner' | 'retriever' | 'reasoner' | 'verifier' | 'builder' | 'critic' | 'operator' | 'witness'
    temperature?: number
    maxTokens?: number
    instructions?: string
  }>
  orchestrationStrategy?: 'sequential' | 'parallel' | 'adaptive'
  budget?: {
    tokens?: number
    time?: number
    cost?: number
  }
}

/**
 * SEG Integration Configuration
 */
export interface SEGConfig {
  useSEG?: boolean
  synthesizeKnowledge?: boolean
  detectContradictions?: boolean
  includeProvenance?: boolean
  evidenceStrength?: 'weak' | 'medium' | 'strong'
}

/**
 * VIF Integration Configuration
 */
export interface VIFConfig {
  useVIF?: boolean
  trackConfidence?: boolean
  requireWitness?: boolean
  confidenceThreshold?: number
  includeProvenance?: boolean
}

/**
 * CAS Integration Configuration
 */
export interface CASConfig {
  useCAS?: boolean
  monitorQuality?: boolean
  detectDrift?: boolean
  cognitiveLoadLimit?: number
}

/**
 * Thinking Mode Configuration
 */
export interface ThinkingModeConfig {
  // Mode selection
  mode?: ThinkingMode
  
  // Reasoning type
  reasoningType?: ReasoningType
  
  // System 1/System 2 balance
  system1Weight?: number // 0-1
  system2Weight?: number // 0-1
  
  // Temperature mapping (auto-calculated from mode if not provided)
  temperature?: number
  
  // APOE roles (auto-selected from mode if not provided)
  useAPOERoles?: boolean
  roles?: Array<'planner' | 'reasoner' | 'critic' | 'builder' | 'retriever' | 'verifier' | 'operator' | 'witness'>
  
  // Cognitive load
  cognitiveLoadLimit?: number
  adaptiveThresholds?: boolean
}

/**
 * Advanced LLM Request
 */
export interface AdvancedLLMRequest extends LLMChatRequest {
  // Advanced prompting
  promptConfig?: AdvancedPromptConfig
  
  // Thinking modes
  thinkingMode?: ThinkingModeConfig
  
  // Deep search
  deepSearch?: DeepSearchConfig
  
  // AIM-OS integration
  apoe?: APOERoleConfig
  seg?: SEGConfig
  vif?: VIFConfig
  cas?: CASConfig
  
  // Output protocols
  outputProtocol?: OutputProtocolConfig
 
  // Model-specific overrides
  modelOverrides?: Record<string, any>

  // Integration tagging
  integrationContext?: IntegrationTagContext
}

/**
 * Output Protocol Configuration
 */
export interface OutputProtocolConfig {
  // Formatting
  enableMarkdown?: boolean
  enableCodeHighlighting?: boolean
  enableDiagrams?: boolean // Mermaid, etc.
  enableTables?: boolean
  enableMath?: boolean // LaTeX
  
  // Structure
  useSections?: boolean
  useHeaders?: boolean
  useLists?: boolean
  useCitations?: boolean
  
  // Visual elements
  useEmojis?: boolean
  useIcons?: boolean
  colorScheme?: 'default' | 'dark' | 'light'
  
  // Streaming
  streamFormat?: 'markdown' | 'plain' | 'structured'
  streamChunkSize?: number
}

/**
 * Advanced LLM Response
 */
export interface AdvancedLLMResponse extends LLMChatResponse {
  // AIM-OS metadata
  aimos?: {
    apoe?: {
      planId?: string
      rolesUsed?: string[]
      executionTime?: number
    }
    seg?: {
      knowledgeSynthesized?: boolean
      contradictionsDetected?: number
      evidenceCount?: number
    }
    vif?: {
      witnessId?: string
      confidence?: number
      provenance?: any
    }
    cas?: {
      qualityScore?: number
      cognitiveLoad?: number
      driftDetected?: boolean
    }
  }
  
  // Output protocol metadata
  outputProtocol?: {
    format?: OutputFormat
    sections?: string[]
    citations?: Array<{ id: string; source: string; url?: string }>
    diagrams?: Array<{ type: string; content: string }>
  }
  
  // Advanced metadata
  reasoning?: {
    steps?: Array<{ step: number; thought: string; confidence: number }>
    finalAnswer?: string
  }
  sources?: Array<{ title: string; url: string; relevance: number }>
}

/**
 * Advanced LLM Service
 * 
 * Provides extreme adjustability for LLM output through:
 * - Advanced prompting strategies
 * - APOE orchestration for complex workflows
 * - SEG knowledge synthesis
 * - VIF confidence tracking
 * - CAS quality monitoring
 * - Output protocol system
 */
export class AdvancedLLMService extends LLMService {
  private commandServerUrl: string

  constructor(commandServerUrl: string = 'http://localhost:5001', aimosConfig?: any) {
    super(commandServerUrl, aimosConfig)
    this.commandServerUrl = commandServerUrl
  }

  /**
   * Advanced chat completion with full AIM-OS integration
   */
  async advancedChatCompletion(
    request: AdvancedLLMRequest
  ): Promise<APIResponse<AdvancedLLMResponse>> {
    // Apply thinking mode configuration
    const enhancedRequest = await this.applyThinkingMode(request)
    
    // Use branch reasoning for complex analytical/reasoning tasks
    if (this.shouldUseBranchReasoning(enhancedRequest)) {
      return this.chatCompletionWithBranchReasoning(enhancedRequest)
    }
    
    // Perform deep search if enabled
    if (enhancedRequest.deepSearch?.providers && enhancedRequest.deepSearch.providers.length > 0) {
      await this.performDeepSearch(enhancedRequest)
    }
    
    // Build advanced prompt using prompt config
    const enhancedMessages = await this.buildAdvancedPrompt(enhancedRequest)
    
    // If APOE is enabled, orchestrate through APOE
    if (enhancedRequest.apoe?.useAPOE) {
      return this.chatCompletionViaAPOE(enhancedRequest, enhancedMessages)
    }
    
    // If SEG is enabled, synthesize knowledge first
    if (enhancedRequest.seg?.useSEG) {
      await this.synthesizeKnowledgeViaSEG(enhancedRequest)
    }
    
    // Build final request with all enhancements
    const finalRequest: LLMChatRequest = {
      ...enhancedRequest,
      messages: enhancedMessages,
      temperature: enhancedRequest.temperature ?? enhancedRequest.thinkingMode?.temperature,
    }
    
    // Call base LLM service
    const response = await this.chatCompletion(finalRequest)
    
    if (!response.success || !response.data) {
      return response as APIResponse<AdvancedLLMResponse>
    }
    
    // Enhance response with AIM-OS metadata
    const enhancedResponse: AdvancedLLMResponse = {
      ...response.data,
      aimos: await this.buildAIMOSMetadata(enhancedRequest, response.data),
      outputProtocol: await this.buildOutputProtocol(enhancedRequest, response.data),
    }
    
    return {
      ...response,
      data: enhancedResponse,
    }
  }
  
  /**
   * Determine if branch reasoning should be used
   */
  private shouldUseBranchReasoning(request: AdvancedLLMRequest): boolean {
    // Use branch reasoning for analytical/reasoning modes on complex problems
    const mode = request.thinkingMode?.mode
    const query = request.messages[request.messages.length - 1]?.content || ''
    
    // Enable if:
    // 1. Analytical or reasoning mode
    // 2. Problem seems complex (contains keywords like "analyze", "compare", "evaluate")
    // 3. User explicitly requested it
    
    if (request.thinkingMode?.reasoningType === 'abductive') {
      return true // Abductive reasoning benefits from multiple hypotheses
    }
    
    if ((mode === 'analytical' || mode === 'reasoning') && 
        (query.length > 100 || this.isComplexProblem(query))) {
      return true
    }
    
    return false
  }
  
  /**
   * Check if problem is complex (heuristic)
   */
  private isComplexProblem(query: string): boolean {
    const complexityKeywords = [
      'analyze', 'compare', 'evaluate', 'assess', 'critique',
      'multiple', 'various', 'different approaches', 'best way',
      'optimize', 'improve', 'design', 'architect'
    ]
    
    const lowerQuery = query.toLowerCase()
    return complexityKeywords.some(keyword => lowerQuery.includes(keyword))
  }
  
  /**
   * Chat completion with branch reasoning
   */
  private async chatCompletionWithBranchReasoning(
    request: AdvancedLLMRequest
  ): Promise<APIResponse<AdvancedLLMResponse>> {
    try {
      const { getBranchReasoningService } = await import('../reasoning')
      const branchService = getBranchReasoningService(this, this.commandServerUrl)
      
      const query = request.messages[request.messages.length - 1]?.content || ''
      
      const branchResult = await branchService.reasonWithBranches({
        problem: query,
        numBranches: 3,
        pruneThreshold: 0.70,
        provider: request.provider,
      })
      
      if (!branchResult.success || !branchResult.data) {
        // Fallback to standard completion
        return this.advancedChatCompletion({ ...request, thinkingMode: { mode: 'balanced' } })
      }
      
      // Build response from branch reasoning
      const enhancedResponse: AdvancedLLMResponse = {
        text: branchResult.data.finalAnswer,
        model: request.model || 'branch-reasoning',
        provider: request.provider,
        tokensUsed: branchResult.data.metadata.totalTokens,
        latencyMs: branchResult.data.metadata.totalTime,
        confidence: branchResult.data.bestBranch.confidence,
        metadata: {
          branchReasoning: {
            totalBranches: branchResult.data.metadata.totalBranches,
            branchesKept: branchResult.data.metadata.branchesKept,
            bestHypothesis: branchResult.data.bestBranch.hypothesis,
          },
        },
        aimos: {
          vif: {
            confidence: branchResult.data.bestBranch.confidence,
          },
        },
        reasoning: {
          steps: branchResult.data.bestBranch.reasoning.map((r, i) => ({
            step: i + 1,
            thought: r,
            confidence: branchResult.data.bestBranch.confidence,
          })),
          finalAnswer: branchResult.data.finalAnswer,
        },
      }
      
      return {
        success: true,
        data: enhancedResponse,
      }
    } catch (error) {
      console.error('[AdvancedLLMService] Branch reasoning failed:', error)
      // Fallback
      return this.advancedChatCompletion({ ...request, thinkingMode: { mode: 'balanced' } })
    }
  }

  /**
   * Apply thinking mode configuration
   * Enhanced with APOE, DEEPSEARCH, SEG, and CAS integration
   */
  private async applyThinkingMode(
    request: AdvancedLLMRequest
  ): Promise<AdvancedLLMRequest> {
    if (!request.thinkingMode?.mode) {
      return request
    }
    
    const mode = request.thinkingMode.mode
    const enhancedRequest = { ...request }
    
    // Map thinking mode to temperature
    const temperatureMap: Record<ThinkingMode, number> = {
      creative: 0.9,
      analytical: 0.3,
      balanced: 0.7,
      reasoning: 0.2,
      intuitive: 0.8,
    }
    
    if (!enhancedRequest.thinkingMode.temperature) {
      enhancedRequest.thinkingMode.temperature = temperatureMap[mode]
    }
    
    // Map thinking mode to APOE roles
    if (enhancedRequest.thinkingMode.useAPOERoles && !enhancedRequest.apoe) {
      const roleMap: Record<ThinkingMode, Array<'planner' | 'retriever' | 'reasoner' | 'verifier' | 'critic' | 'builder'>> = {
        creative: ['planner', 'builder'],
        analytical: ['retriever', 'reasoner', 'critic', 'verifier'],
        balanced: ['planner', 'retriever', 'reasoner', 'builder'],
        reasoning: ['retriever', 'reasoner', 'verifier', 'critic'],
        intuitive: ['builder'], // Fast, no orchestration overhead
      }
      
      enhancedRequest.apoe = {
        useAPOE: true,
        roles: roleMap[mode].map((role) => ({
          role,
          temperature: enhancedRequest.thinkingMode.temperature,
        })),
        orchestrationStrategy: mode === 'creative' ? 'adaptive' : 'sequential',
      }
    }
    
    // Auto-configure DEEPSEARCH depth based on mode
    if (!enhancedRequest.deepSearch && this.shouldEnableDeepSearch(mode)) {
      const depthMap: Record<ThinkingMode, { depth: 'basic' | 'advanced' | 'comprehensive'; providers: any[] }> = {
        creative: {
          depth: 'advanced',
          providers: ['perplexity', 'deepsearch'],
        },
        analytical: {
          depth: 'comprehensive',
          providers: ['deepsearch', 'icip', 'perplexity', 'tavily'],
        },
        balanced: {
          depth: 'advanced',
          providers: ['deepsearch', 'perplexity'],
        },
        reasoning: {
          depth: 'comprehensive',
          providers: ['deepsearch', 'icip', 'tavily'],
        },
        intuitive: {
          depth: 'basic',
          providers: ['perplexity'],
        },
      }
      
      enhancedRequest.deepSearch = depthMap[mode]
    }
    
    // Auto-enable SEG for analytical/reasoning modes
    if (!enhancedRequest.seg && this.shouldEnableSEG(mode)) {
      enhancedRequest.seg = {
        useSEG: true,
        synthesizeKnowledge: true,
        detectContradictions: mode === 'reasoning' || mode === 'analytical',
        includeProvenance: true,
        evidenceStrength: mode === 'reasoning' ? 'strong' : 'medium',
      }
    }
    
    // Auto-enable VIF for reasoning/analytical modes
    if (!enhancedRequest.vif && this.shouldEnableVIF(mode)) {
      enhancedRequest.vif = {
        useVIF: true,
        trackConfidence: true,
        requireWitness: mode === 'reasoning',
        confidenceThreshold: mode === 'reasoning' ? 0.90 : 0.80,
        includeProvenance: true,
      }
    }
    
    // Auto-enable CAS monitoring
    if (!enhancedRequest.cas) {
      const cognitiveLoadLimits: Record<ThinkingMode, number> = {
        creative: 0.60, // Allow high load for creativity
        analytical: 0.85, // High rigor acceptable
        balanced: 0.70, // Moderate
        reasoning: 0.90, // Very high rigor
        intuitive: 0.50, // Keep it light
      }
      
      enhancedRequest.cas = {
        useCAS: true,
        monitorQuality: true,
        detectDrift: mode !== 'intuitive',
        cognitiveLoadLimit: cognitiveLoadLimits[mode],
      }
    }
    
    // Map thinking mode to prompt config
    if (!enhancedRequest.promptConfig) {
      enhancedRequest.promptConfig = {}
    }
    
    const styleMap: Record<ThinkingMode, OutputStyle> = {
      creative: 'creative',
      analytical: 'technical',
      balanced: 'detailed',
      reasoning: 'technical',
      intuitive: 'conversational',
    }
    
    const toneMap: Record<ThinkingMode, OutputTone> = {
      creative: 'friendly',
      analytical: 'professional',
      balanced: 'professional',
      reasoning: 'formal',
      intuitive: 'casual',
    }
    
    enhancedRequest.promptConfig.outputStyle = styleMap[mode]
    enhancedRequest.promptConfig.outputTone = toneMap[mode]
    enhancedRequest.promptConfig.useChainOfThought = mode === 'reasoning' || mode === 'analytical'
    enhancedRequest.promptConfig.requireCitations = mode === 'reasoning' || mode === 'analytical'
    
    return enhancedRequest
  }
  
  /**
   * Determine if deep search should be enabled for this mode
   */
  private shouldEnableDeepSearch(mode: ThinkingMode): boolean {
    // All modes benefit from search except intuitive (which prioritizes speed)
    return mode !== 'intuitive'
  }
  
  /**
   * Determine if SEG should be enabled for this mode
   */
  private shouldEnableSEG(mode: ThinkingMode): boolean {
    // Analytical and reasoning modes benefit most from knowledge synthesis
    return mode === 'analytical' || mode === 'reasoning' || mode === 'balanced'
  }
  
  /**
   * Determine if VIF should be enabled for this mode
   */
  private shouldEnableVIF(mode: ThinkingMode): boolean {
    // All modes benefit from confidence tracking
    return true
  }

  /**
   * Perform deep search across multiple providers
   */
  private async performDeepSearch(
    request: AdvancedLLMRequest
  ): Promise<DeepSearchResults> {
    if (!request.deepSearch?.providers || request.deepSearch.providers.length === 0) {
      return { deepsearch: [], perplexity: [], tavily: [], icip: [], web: [] }
    }
    
    // Extract query from last user message
    const query = request.messages[request.messages.length - 1]?.content || ''
    
    const results: DeepSearchResults = {
      deepsearch: [],
      perplexity: [],
      tavily: [],
      icip: [],
      web: [],
    }
    
    // Map depth to numeric value
    const depthMap = { basic: 1, advanced: 3, comprehensive: 5 }
    const depth = depthMap[request.deepSearch.depth || 'advanced']
    
    // Execute searches in parallel
    const promises = request.deepSearch.providers.map(async (provider) => {
      try {
        if (provider === 'deepsearch') {
          const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              tool: 'deepsearch',
              arguments: {
                query,
                search_type: 'mixed',
                depth: request.deepSearch.crawlDepth || depth,
                max_results: 20,
                filters: {
                  domains: request.deepSearch.domainFilter,
                  trust_threshold: request.deepSearch.trustThreshold || 0.5,
                },
                synthesis: {
                  use_seg: request.deepSearch.synthesizeResults,
                  detect_contradictions: request.deepSearch.detectContradictions,
                  require_citations: request.deepSearch.requireCitations,
                },
              },
            }),
          })
          
          const result = await response.json()
          if (result.success || result.result) {
            const data = result.data || result.result
            results.deepsearch = data.results || []
          }
        }
        else if (provider === 'perplexity') {
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
                  messages: [{ role: 'user', content: query }],
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
                  query,
                  search_depth: request.deepSearch.depth || 'advanced',
                  include_answer: true,
                  max_results: 10,
                },
              },
            }),
          })
          
          const result = await response.json()
          if (result.success && result.data) {
            results.tavily = result.data.results || []
          }
        }
        else if (provider === 'icip') {
          const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              tool: 'icip_search',
              arguments: {
                query,
                search_tier: 'semantic',
                max_results: 20,
                include_context: true,
              },
            }),
          })
          
          const result = await response.json()
          if (result.success && result.data) {
            results.icip = result.data.results || []
          }
        }
      } catch (error) {
        console.warn(`[DeepSearch] ${provider} failed:`, error)
      }
    })
    
    await Promise.all(promises)
    
    // Add search results to request context
    if (this.hasSearchResults(results)) {
      await this.addSearchResultsToContext(request, results)
    }
    
    return results
  }
  
  /**
   * Check if search returned any results
   */
  private hasSearchResults(results: DeepSearchResults): boolean {
    return Object.values(results).some(arr => arr.length > 0)
  }
  
  /**
   * Add search results to prompt context
   */
  private async addSearchResultsToContext(
    request: AdvancedLLMRequest,
    results: DeepSearchResults
  ): Promise<void> {
    let contextAddition = '\n\n**Search Results:**\n\n'
    
    // Add DEEPSEARCH results
    if (results.deepsearch.length > 0) {
      contextAddition += `**DEEPSEARCH (${results.deepsearch.length} results):**\n`
      results.deepsearch.slice(0, 3).forEach((r, i) => {
        contextAddition += `${i + 1}. ${r.title} (trust: ${r.trustScore?.toFixed(2) || 'N/A'})\n`
        contextAddition += `   ${r.summary}\n\n`
      })
    }
    
    // Add Perplexity results
    if (results.perplexity.length > 0) {
      contextAddition += `**Perplexity (${results.perplexity.length} citations):**\n`
      results.perplexity.slice(0, 3).forEach((r, i) => {
        contextAddition += `${i + 1}. ${r.title || r.text}\n`
        contextAddition += `   Source: ${r.url}\n\n`
      })
    }
    
    // Add Tavily results
    if (results.tavily.length > 0) {
      contextAddition += `**Tavily (${results.tavily.length} results):**\n`
      results.tavily.slice(0, 3).forEach((r, i) => {
        contextAddition += `${i + 1}. ${r.title}\n`
        contextAddition += `   ${r.content}\n\n`
      })
    }
    
    // Add ICIP results
    if (results.icip.length > 0) {
      contextAddition += `**ICIP Code Search (${results.icip.length} results):**\n`
      results.icip.slice(0, 3).forEach((r, i) => {
        contextAddition += `${i + 1}. ${r.file}:${r.line} (${r.type})\n`
        contextAddition += `   \`\`\`${r.language}\n   ${r.code}\n   \`\`\`\n\n`
      })
    }
    
    // Add to last user message
    if (request.messages.length > 0) {
      const lastMessage = request.messages[request.messages.length - 1]
      if (lastMessage.role === 'user') {
        lastMessage.content += contextAddition
      }
    }
  }

  /**
   * Build advanced prompt using prompt config
   */
  private async buildAdvancedPrompt(
    request: AdvancedLLMRequest
  ): Promise<LLMMessage[]> {
    const messages: LLMMessage[] = []
    
    // Build system prompt
    if (request.promptConfig?.systemPrompt || request.promptConfig?.role) {
      let systemContent = ''
      
      if (request.promptConfig.role) {
        systemContent += `You are ${request.promptConfig.role}.\n\n`
      }
      
      if (request.promptConfig.systemPrompt) {
        systemContent += request.promptConfig.systemPrompt + '\n\n'
      }
      
      if (request.promptConfig.behaviorGuidelines) {
        systemContent += 'Behavior Guidelines:\n'
        request.promptConfig.behaviorGuidelines.forEach((guideline, i) => {
          systemContent += `${i + 1}. ${guideline}\n`
        })
        systemContent += '\n'
      }
      
      // Output format instructions
      if (request.promptConfig.outputFormat) {
        systemContent += `Output Format: ${request.promptConfig.outputFormat}\n`
      }
      if (request.promptConfig.outputStyle) {
        systemContent += `Output Style: ${request.promptConfig.outputStyle}\n`
      }
      if (request.promptConfig.outputTone) {
        systemContent += `Output Tone: ${request.promptConfig.outputTone}\n`
      }
      
      // Chain-of-thought instructions
      if (request.promptConfig.useChainOfThought) {
        systemContent += '\nUse chain-of-thought reasoning. Show your thinking process step by step.\n'
      }
      
      // Structured output instructions
      if (request.promptConfig.requireStructuredOutput && request.promptConfig.outputSchema) {
        systemContent += `\nOutput must conform to this schema:\n${JSON.stringify(request.promptConfig.outputSchema, null, 2)}\n`
      }
      
      // Citation requirements
      if (request.promptConfig.requireCitations) {
        systemContent += '\nAlways cite your sources using [1], [2], etc. format.\n'
      }
      
      messages.push({
        role: 'system',
        content: systemContent.trim(),
      })
    }
    
    // Add few-shot examples
    if (request.promptConfig?.fewShotExamples) {
      request.promptConfig.fewShotExamples.forEach((example) => {
        messages.push({
          role: 'user',
          content: example.input,
        })
        messages.push({
          role: 'assistant',
          content: example.output + (example.explanation ? `\n\nExplanation: ${example.explanation}` : ''),
        })
      })
    }
    
    // Add user messages
    messages.push(...request.messages)
    
    return messages
  }

  /**
   * Chat completion via APOE orchestration
   */
  private async chatCompletionViaAPOE(
    request: AdvancedLLMRequest,
    messages: LLMMessage[]
  ): Promise<APIResponse<AdvancedLLMResponse>> {
    try {
      // Import orchestration components
      const { WorkflowExecutor, PlannerExecutor, QualityGateSystem } = await import('../orchestration')
      
      // Create workflow executor
      const workflowExecutor = new WorkflowExecutor(this, this.commandServerUrl)
      
      // Use Planner role to create execution plan
      const planner = new PlannerExecutor(this, this.commandServerUrl)
      const planResult = await planner.execute(
        {
          goal: `Generate sophisticated LLM response for: ${messages[messages.length - 1].content}`,
          constraints: {
            roles: request.apoe?.roles?.map(r => r.role) || [],
            budget: request.apoe?.budget,
          },
        },
        {
          goal: `Generate sophisticated LLM response`,
          metadata: {
            messages,
            promptConfig: request.promptConfig,
          },
        }
      )
      
      if (!planResult.success || !planResult.output) {
        // Fallback to standard completion if planning fails
        return this.chatCompletion({
          ...request,
          messages,
        }) as Promise<APIResponse<AdvancedLLMResponse>>
      }
      
      // Execute workflow with generated plan
      const workflowResult = await workflowExecutor.execute({
        id: `workflow_${Date.now()}`,
        goal: `Generate sophisticated LLM response`,
        plan: planResult.output,
        budget: request.apoe?.budget,
        qualityGates: QualityGateSystem.createDefaultGates(),
        parallelExecution: request.apoe?.orchestrationStrategy === 'parallel',
      })
      
      // Extract final response from workflow
      const finalStep = workflowResult.steps_executed[workflowResult.steps_executed.length - 1]
      
      // Build enhanced response
      const enhancedResponse: AdvancedLLMResponse = {
        text: finalStep?.output?.artifact || finalStep?.output?.conclusion || 'No response generated',
        model: request.model || 'apoe-orchestrated',
        provider: request.provider,
        tokensUsed: workflowResult.total_tokens,
        latencyMs: workflowResult.total_time * 1000,
        confidence: workflowResult.final_confidence,
        metadata: {
          apoe: {
            planId: workflowResult.workflow_id,
            rolesUsed: workflowResult.steps_executed.map(s => s.role),
            executionTime: workflowResult.total_time,
          },
        },
        aimos: {
          apoe: {
            planId: workflowResult.workflow_id,
            rolesUsed: workflowResult.steps_executed.map(s => s.role),
            executionTime: workflowResult.total_time,
          },
        },
      }
      
      return {
        success: workflowResult.success,
        data: enhancedResponse,
        metadata: {
          provider: 'apoe',
          latency: workflowResult.total_time * 1000,
          cached: false,
          tokens: workflowResult.total_tokens,
          cost: workflowResult.total_cost,
        },
      }
    } catch (error: any) {
      console.error('[AdvancedLLMService] APOE orchestration failed:', error)
      
      // Fallback to standard completion
      return this.chatCompletion({
        ...request,
        messages,
      }) as Promise<APIResponse<AdvancedLLMResponse>>
    }
  }

  /**
   * Synthesize knowledge via SEG
   */
  private async synthesizeKnowledgeViaSEG(
    request: AdvancedLLMRequest
  ): Promise<void> {
    if (!request.seg?.useSEG) return
    
    // Extract query from last user message
    const query = request.messages[request.messages.length - 1]?.content || ''
    
    // Call SEG synthesis via Command Server
    const segRequest = {
      tool: 'synthesize_knowledge',
      arguments: {
        topics: [query],
        depth: 'medium',
        format: 'summary',
      },
    }
    
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(segRequest),
      })
      
      const result = await response.json()
      
      // TODO: Integrate SEG synthesis results into prompt
    } catch (error) {
      // Silently fail - SEG synthesis is optional
    }
  }

  /**
   * Build AIM-OS metadata for response
   */
  private async buildAIMOSMetadata(
    request: AdvancedLLMRequest,
    response: LLMChatResponse
  ): Promise<AdvancedLLMResponse['aimos']> {
    const aimos: AdvancedLLMResponse['aimos'] = {}
    
    // VIF metadata
    if (request.vif?.useVIF && response.confidence !== undefined) {
      aimos.vif = {
        confidence: response.confidence,
        witnessId: undefined, // TODO: Get from VIF
        provenance: undefined, // TODO: Get from VIF
      }
    }
    
    // SEG metadata
    if (request.seg?.useSEG) {
      aimos.seg = {
        knowledgeSynthesized: request.seg.synthesizeKnowledge || false,
        contradictionsDetected: 0, // TODO: Get from SEG
        evidenceCount: 0, // TODO: Get from SEG
      }
    }
    
    // CAS metadata
    if (request.cas?.useCAS) {
      aimos.cas = {
        qualityScore: response.confidence || 0.8,
        cognitiveLoad: 0, // TODO: Get from CAS
        driftDetected: false, // TODO: Get from CAS
      }
    }
    
    return aimos
  }

  /**
   * Build output protocol metadata
   */
  private async buildOutputProtocol(
    request: AdvancedLLMRequest,
    response: LLMChatResponse
  ): Promise<AdvancedLLMResponse['outputProtocol']> {
    const protocol: AdvancedLLMResponse['outputProtocol'] = {
      format: request.promptConfig?.outputFormat || 'markdown',
      sections: [],
      citations: [],
      diagrams: [],
    }
    
    // Extract sections from markdown
    if (response.text) {
      const sectionMatches = response.text.match(/^#+\s+(.+)$/gm)
      if (sectionMatches) {
        protocol.sections = sectionMatches.map((match) => match.replace(/^#+\s+/, ''))
      }
      
      // Extract citations
      const citationMatches = response.text.match(/\[(\d+)\]/g)
      if (citationMatches) {
        protocol.citations = citationMatches.map((match, i) => ({
          id: match,
          source: `Source ${i + 1}`,
        }))
      }
      
      // Extract diagrams (Mermaid, etc.)
      const diagramMatches = response.text.match(/```(mermaid|graph|diagram)\n([\s\S]*?)```/g)
      if (diagramMatches) {
        protocol.diagrams = diagramMatches.map((match) => {
          const typeMatch = match.match(/```(\w+)/)
          const contentMatch = match.match(/```[\w]+\n([\s\S]*?)```/)
          return {
            type: typeMatch ? typeMatch[1] : 'unknown',
            content: contentMatch ? contentMatch[1] : '',
          }
        })
      }
    }
    
    return protocol
  }

  /**
   * Get available output protocols
   */
  getAvailableOutputProtocols(): OutputProtocolConfig {
    return {
      enableMarkdown: true,
      enableCodeHighlighting: true,
      enableDiagrams: true,
      enableTables: true,
      enableMath: true,
      useSections: true,
      useHeaders: true,
      useLists: true,
      useCitations: true,
      useEmojis: true,
      useIcons: true,
      colorScheme: 'default',
      streamFormat: 'markdown',
      streamChunkSize: 10,
    }
  }

  /**
   * Get default thinking mode config
   */
  getDefaultThinkingMode(mode: ThinkingMode): ThinkingModeConfig {
    const configs: Record<ThinkingMode, ThinkingModeConfig> = {
      creative: {
        mode: 'creative',
        system1Weight: 0.8,
        system2Weight: 0.2,
        temperature: 0.9,
        useAPOERoles: true,
        roles: ['planner', 'builder'],
        adaptiveThresholds: true,
      },
      analytical: {
        mode: 'analytical',
        system1Weight: 0.2,
        system2Weight: 0.8,
        temperature: 0.3,
        reasoningType: 'deductive',
        useAPOERoles: true,
        roles: ['reasoner', 'critic', 'verifier'],
        adaptiveThresholds: true,
      },
      balanced: {
        mode: 'balanced',
        system1Weight: 0.5,
        system2Weight: 0.5,
        temperature: 0.7,
        useAPOERoles: true,
        roles: ['planner', 'reasoner', 'builder'],
        adaptiveThresholds: true,
      },
      reasoning: {
        mode: 'reasoning',
        system1Weight: 0.1,
        system2Weight: 0.9,
        temperature: 0.2,
        reasoningType: 'deductive',
        useAPOERoles: true,
        roles: ['reasoner', 'verifier', 'critic'],
        adaptiveThresholds: false,
      },
      intuitive: {
        mode: 'intuitive',
        system1Weight: 0.9,
        system2Weight: 0.1,
        temperature: 0.8,
        reasoningType: 'analogical',
        useAPOERoles: false,
        adaptiveThresholds: true,
      },
    }
    
    return configs[mode]
  }

  /**
   * Get default advanced prompt config for a use case
   */
  getDefaultPromptConfig(useCase: 'coding' | 'research' | 'creative' | 'analysis'): AdvancedPromptConfig {
    const configs: Record<string, AdvancedPromptConfig> = {
      coding: {
        role: 'an expert software engineer',
        outputFormat: 'code',
        outputStyle: 'technical',
        outputTone: 'professional',
        useChainOfThought: true,
        requireStructuredOutput: false,
        requireCitations: false,
        behaviorGuidelines: [
          'Write clean, well-documented code',
          'Follow best practices for the language/framework',
          'Include error handling',
          'Add comments explaining complex logic',
        ],
      },
      research: {
        role: 'a research analyst',
        outputFormat: 'markdown',
        outputStyle: 'detailed',
        outputTone: 'professional',
        useChainOfThought: true,
        requireCitations: true,
        requireVerification: true,
        behaviorGuidelines: [
          'Cite all sources',
          'Synthesize information from multiple sources',
          'Identify contradictions',
          'Provide balanced perspectives',
        ],
      },
      creative: {
        role: 'a creative writer',
        outputFormat: 'mixed',
        outputStyle: 'creative',
        outputTone: 'friendly',
        useChainOfThought: false,
        behaviorGuidelines: [
          'Be creative and engaging',
          'Use vivid descriptions',
          'Maintain narrative flow',
        ],
      },
      analysis: {
        role: 'a data analyst',
        outputFormat: 'table',
        outputStyle: 'detailed',
        outputTone: 'professional',
        useChainOfThought: true,
        requireStructuredOutput: true,
        behaviorGuidelines: [
          'Present data clearly',
          'Use tables and visualizations',
          'Provide insights and conclusions',
        ],
      },
    }
    
    return configs[useCase] || {}
  }
}

// Singleton instance
let advancedLLMServiceInstance: AdvancedLLMService | null = null

export function getAdvancedLLMService(commandServerUrl?: string): AdvancedLLMService {
  if (!advancedLLMServiceInstance) {
    advancedLLMServiceInstance = new AdvancedLLMService(commandServerUrl)
  }
  return advancedLLMServiceInstance
}

