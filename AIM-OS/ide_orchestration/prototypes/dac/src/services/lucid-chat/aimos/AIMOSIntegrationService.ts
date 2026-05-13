/**
 * AIM-OS Integration Service for Lucid Chat API Services
 * Integrates API responses with CMC, HHNI, VIF, APOE, and SEG
 * 
 * Phase 1: AIM-OS Integration
 */

export interface AIMOSIntegrationConfig {
  enabled: boolean
  baseUrl?: string
  cmc?: boolean
  hhni?: boolean
  vif?: boolean
  apoe?: boolean
  seg?: boolean
}

export interface APIResponseMetadata {
  provider: string
  api: string
  endpoint: string
  request: any
  response: any
  latency: number
  tokens?: number
  cost?: number
  timestamp: string
  success: boolean
  error?: string
}

export interface AIMOSIntegrationResult {
  cmc?: {
    success: boolean
    atom_id?: string
    error?: string
  }
  hhni?: {
    success: boolean
    indexed: boolean
    error?: string
  }
  vif?: {
    success: boolean
    witness_id?: string
    error?: string
  }
  apoe?: {
    success: boolean
    plan_id?: string
    error?: string
  }
  seg?: {
    success: boolean
    entities_created?: number
    relations_created?: number
    error?: string
  }
}

class AIMOSIntegrationService {
  private config: AIMOSIntegrationConfig
  private baseUrl: string

  constructor(config: AIMOSIntegrationConfig = { enabled: true }) {
    this.config = {
      enabled: config.enabled ?? true,
      baseUrl: config.baseUrl || 'http://localhost:8000',
      cmc: config.cmc ?? true,
      hhni: config.hhni ?? true,
      vif: config.vif ?? true,
      apoe: config.apoe ?? false, // Optional - only for workflows
      seg: config.seg ?? true,
    }
    this.baseUrl = this.config.baseUrl!
  }

  /**
   * Integrate API response with AIM-OS systems
   */
  async integrateAPIResponse(
    metadata: APIResponseMetadata
  ): Promise<AIMOSIntegrationResult> {
    if (!this.config.enabled) {
      return {}
    }

    const result: AIMOSIntegrationResult = {}

    // CMC: Store API response
    if (this.config.cmc) {
      result.cmc = await this.storeInCMC(metadata)
    }

    // HHNI: Index API response for semantic search
    if (this.config.hhni && result.cmc?.atom_id) {
      result.hhni = await this.indexInHHNI(result.cmc.atom_id, metadata)
    }

    // VIF: Create witness for API operation
    if (this.config.vif) {
      result.vif = await this.createVIFWitness(metadata)
    }

    // SEG: Synthesize knowledge from API response
    if (this.config.seg && result.cmc?.atom_id) {
      result.seg = await this.synthesizeInSEG(result.cmc.atom_id, metadata)
    }

    return result
  }

  /**
   * Store API response in CMC
   */
  private async storeInCMC(
    metadata: APIResponseMetadata
  ): Promise<{ success: boolean; atom_id?: string; error?: string }> {
    try {
      const content = this.extractContent(metadata)
      const tags = this.generateTags(metadata)
      const cmcMetadata = {
        api_provider: metadata.provider,
        api_name: metadata.api,
        endpoint: metadata.endpoint,
        latency_ms: metadata.latency,
        tokens: metadata.tokens,
        cost: metadata.cost,
        timestamp: metadata.timestamp,
        success: metadata.success,
        error: metadata.error,
        request: metadata.request,
        response: metadata.response,
      }

      const response = await fetch(`${this.baseUrl}/mcp/tools/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'mcp_lucid-mcp_store_memory',
          arguments: {
            content,
            tags,
            metadata: cmcMetadata,
          },
        }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        return {
          success: false,
          error: `CMC storage failed: ${response.status} - ${errorText}`,
        }
      }

      const data = await response.json()
      const atomId = data.result?.atom_id || data.atom_id

      return {
        success: true,
        atom_id: atomId,
      }
    } catch (error: any) {
      console.error('CMC storage error:', error)
      return {
        success: false,
        error: error.message || 'Unknown CMC storage error',
      }
    }
  }

  /**
   * Index API response in HHNI
   * Note: HHNI indexing happens automatically when storing in CMC,
   * but we can trigger explicit indexing if needed
   */
  private async indexInHHNI(
    atomId: string,
    metadata: APIResponseMetadata
  ): Promise<{ success: boolean; indexed: boolean; error?: string }> {
    try {
      // HHNI indexing is typically automatic via CMC storage
      // This is a placeholder for explicit indexing if needed
      return {
        success: true,
        indexed: true,
      }
    } catch (error: any) {
      console.error('HHNI indexing error:', error)
      return {
        success: false,
        indexed: false,
        error: error.message || 'Unknown HHNI indexing error',
      }
    }
  }

  /**
   * Create VIF witness for API operation
   */
  private async createVIFWitness(
    metadata: APIResponseMetadata
  ): Promise<{ success: boolean; witness_id?: string; error?: string }> {
    try {
      const confidence = this.calculateConfidence(metadata)
      const task = `API call: ${metadata.provider}/${metadata.api}/${metadata.endpoint}`
      const evidence = [
        `Provider: ${metadata.provider}`,
        `API: ${metadata.api}`,
        `Endpoint: ${metadata.endpoint}`,
        `Latency: ${metadata.latency}ms`,
        `Success: ${metadata.success}`,
      ]
      const reasoning = metadata.success
        ? `API call succeeded with ${metadata.latency}ms latency`
        : `API call failed: ${metadata.error}`

      const response = await fetch(`${this.baseUrl}/mcp/tools/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'mcp_lucid-mcp_track_confidence',
          arguments: {
            task,
            confidence,
            evidence,
            reasoning,
          },
        }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        return {
          success: false,
          error: `VIF witness creation failed: ${response.status} - ${errorText}`,
        }
      }

      const data = await response.json()
      const witnessId = data.result?.witness_id || data.witness_id

      return {
        success: true,
        witness_id: witnessId,
      }
    } catch (error: any) {
      console.error('VIF witness creation error:', error)
      return {
        success: false,
        error: error.message || 'Unknown VIF witness creation error',
      }
    }
  }

  /**
   * Synthesize knowledge in SEG
   */
  private async synthesizeInSEG(
    atomId: string,
    metadata: APIResponseMetadata
  ): Promise<{
    success: boolean
    entities_created?: number
    relations_created?: number
    error?: string
  }> {
    try {
      const topics = [
        metadata.provider,
        metadata.api,
        metadata.endpoint,
        metadata.success ? 'api_success' : 'api_error',
      ]

      const response = await fetch(`${this.baseUrl}/mcp/tools/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'mcp_lucid-mcp_synthesize_knowledge',
          arguments: {
            topics,
            depth: 'shallow',
            format: 'summary',
          },
        }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        return {
          success: false,
          error: `SEG synthesis failed: ${response.status} - ${errorText}`,
        }
      }

      const data = await response.json()
      const result = data.result || data

      return {
        success: true,
        entities_created: result.entities_found || 0,
        relations_created: result.relations_found || 0,
      }
    } catch (error: any) {
      console.error('SEG synthesis error:', error)
      return {
        success: false,
        error: error.message || 'Unknown SEG synthesis error',
      }
    }
  }

  /**
   * Extract content from API response metadata
   */
  private extractContent(metadata: APIResponseMetadata): string {
    if (metadata.success && metadata.response) {
      // Try to extract meaningful content from response
      if (typeof metadata.response === 'string') {
        return metadata.response
      }
      if (metadata.response.text || metadata.response.content) {
        return metadata.response.text || metadata.response.content
      }
      if (metadata.response.data) {
        return JSON.stringify(metadata.response.data)
      }
      return JSON.stringify(metadata.response)
    }
    return `API call to ${metadata.provider}/${metadata.api}/${metadata.endpoint}`
  }

  /**
   * Generate tags for CMC storage
   */
  private generateTags(metadata: APIResponseMetadata): Record<string, number> {
    const tags: Record<string, number> = {
      api: 1.0,
      [`api_${metadata.provider}`]: 0.95,
      [`api_${metadata.api}`]: 0.9,
      [`endpoint_${metadata.endpoint}`]: 0.85,
    }

    if (metadata.success) {
      tags.success = 1.0
    } else {
      tags.error = 1.0
      tags.failed = 0.95
    }

    if (metadata.tokens) {
      tags.has_tokens = 0.8
    }

    if (metadata.cost) {
      tags.has_cost = 0.8
    }

    return tags
  }

  /**
   * Calculate confidence for VIF witness
   */
  private calculateConfidence(metadata: APIResponseMetadata): number {
    if (!metadata.success) {
      return 0.3 // Low confidence for failed calls
    }

    // Base confidence on latency and success
    let confidence = 0.85

    // Adjust based on latency (faster = higher confidence)
    if (metadata.latency < 500) {
      confidence += 0.05
    } else if (metadata.latency > 5000) {
      confidence -= 0.1
    }

    // Adjust based on response quality (if available)
    if (metadata.response && typeof metadata.response === 'object') {
      if (metadata.response.confidence) {
        confidence = metadata.response.confidence
      }
    }

    return Math.max(0.0, Math.min(1.0, confidence))
  }

  /**
   * Create APOE workflow plan for multi-step API operations
   */
  async createAPOEPlan(
    goal: string,
    steps: Array<{
      api: string
      endpoint: string
      parameters: any
    }>,
    priority: 'low' | 'medium' | 'high' | 'critical' = 'medium'
  ): Promise<{ success: boolean; plan_id?: string; error?: string }> {
    if (!this.config.apoe) {
      return { success: false, error: 'APOE integration not enabled' }
    }

    try {
      const response = await fetch(`${this.baseUrl}/mcp/tools/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'mcp_lucid-mcp_create_plan',
          arguments: {
            goal,
            context: JSON.stringify({ steps }),
            priority,
          },
        }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        return {
          success: false,
          error: `APOE plan creation failed: ${response.status} - ${errorText}`,
        }
      }

      const data = await response.json()
      const planId = data.result?.plan_id || data.plan_id

      return {
        success: true,
        plan_id: planId,
      }
    } catch (error: any) {
      console.error('APOE plan creation error:', error)
      return {
        success: false,
        error: error.message || 'Unknown APOE plan creation error',
      }
    }
  }
}

// Singleton instance
let instance: AIMOSIntegrationService | null = null

export function getAIMOSIntegrationService(
  config?: AIMOSIntegrationConfig
): AIMOSIntegrationService {
  if (!instance) {
    instance = new AIMOSIntegrationService(config)
  }
  return instance
}

export { AIMOSIntegrationService }

