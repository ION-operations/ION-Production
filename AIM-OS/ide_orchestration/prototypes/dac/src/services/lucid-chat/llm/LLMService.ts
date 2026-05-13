/**
 * Unified LLM Service for Lucid Chat
 * Supports multiple LLM providers (Gemini, Claude, Cerebras) via MCP backend
 * 
 * Phase 4: LLM Integration
 */

import { BaseAPIService, APIResponse } from '../base/BaseAPIService'

export type LLMProvider = 'gemini' | 'anthropic' | 'cerebras' | 'minimax' | 'openai'

export interface LLMModel {
  id: string
  name: string
  provider: LLMProvider
  contextWindow: number
  maxOutputTokens: number
  supportsStreaming: boolean
  supportsFunctionCalling: boolean
  description?: string
}

export interface LLMMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export interface LLMChatRequest {
  provider: LLMProvider
  model?: string
  messages: LLMMessage[]
  system?: string
  temperature?: number
  maxTokens?: number
  stream?: boolean
}

export interface LLMChatResponse {
  text: string
  model: string
  provider: LLMProvider
  tokensUsed: number
  latencyMs: number
  confidence?: number
  metadata?: Record<string, any>
}

export interface LLMStreamChunk {
  text: string
  done: boolean
  model?: string
  tokensUsed?: number
}

/**
 * Available models for each provider
 */
export const AVAILABLE_MODELS: Record<LLMProvider, LLMModel[]> = {
  gemini: [
    {
      id: 'gemini-2.0-flash-exp',
      name: 'Gemini 2.0 Flash (Experimental)',
      provider: 'gemini',
      contextWindow: 1_000_000,
      maxOutputTokens: 8192,
      supportsStreaming: true,
      supportsFunctionCalling: true,
      description: 'Fast, high quality, 1M token context',
    },
    {
      id: 'gemini-1.5-pro',
      name: 'Gemini 1.5 Pro',
      provider: 'gemini',
      contextWindow: 1_000_000,
      maxOutputTokens: 8192,
      supportsStreaming: true,
      supportsFunctionCalling: true,
      description: 'High quality, 1M token context',
    },
    {
      id: 'gemini-pro',
      name: 'Gemini Pro',
      provider: 'gemini',
      contextWindow: 32_000,
      maxOutputTokens: 2048,
      supportsStreaming: true,
      supportsFunctionCalling: true,
      description: 'Balanced performance',
    },
  ],
  anthropic: [
    {
      id: 'claude-3-5-sonnet-20241022',
      name: 'Claude 3.5 Sonnet',
      provider: 'anthropic',
      contextWindow: 200_000,
      maxOutputTokens: 8192,
      supportsStreaming: true,
      supportsFunctionCalling: true,
      description: 'Fast, high quality, latest model',
    },
    {
      id: 'claude-3-opus-20240229',
      name: 'Claude 3 Opus',
      provider: 'anthropic',
      contextWindow: 200_000,
      maxOutputTokens: 4096,
      supportsStreaming: true,
      supportsFunctionCalling: true,
      description: 'Highest quality',
    },
    {
      id: 'claude-3-haiku-20240307',
      name: 'Claude 3 Haiku',
      provider: 'anthropic',
      contextWindow: 200_000,
      maxOutputTokens: 4096,
      supportsStreaming: true,
      supportsFunctionCalling: true,
      description: 'Fastest, cost-effective',
    },
  ],
  cerebras: [
    {
      id: 'llama3.1-8b',
      name: 'Llama 3.1 8B',
      provider: 'cerebras',
      contextWindow: 8192,
      maxOutputTokens: 4096,
      supportsStreaming: true,
      supportsFunctionCalling: false,
      description: 'Ultra-fast inference',
    },
    {
      id: 'llama3.1-70b',
      name: 'Llama 3.1 70B',
      provider: 'cerebras',
      contextWindow: 8192,
      maxOutputTokens: 4096,
      supportsStreaming: true,
      supportsFunctionCalling: false,
      description: 'High quality, fast',
    },
  ],
  minimax: [
    {
      id: 'abab5.5-chat',
      name: 'MiniMax abab5.5',
      provider: 'minimax',
      contextWindow: 128_000,
      maxOutputTokens: 4096,
      supportsStreaming: true,
      supportsFunctionCalling: false,
      description: 'MiniMax chat model',
    },
  ],
  openai: [
    {
      id: 'gpt-4',
      name: 'GPT-4',
      provider: 'openai',
      contextWindow: 128_000,
      maxOutputTokens: 4096,
      supportsStreaming: true,
      supportsFunctionCalling: true,
      description: 'OpenAI GPT-4',
    },
    {
      id: 'gpt-3.5-turbo',
      name: 'GPT-3.5 Turbo',
      provider: 'openai',
      contextWindow: 16_385,
      maxOutputTokens: 4096,
      supportsStreaming: true,
      supportsFunctionCalling: true,
      description: 'OpenAI GPT-3.5 Turbo',
    },
  ],
}

/**
 * Default models for each provider
 */
export const DEFAULT_MODELS: Record<LLMProvider, string> = {
  gemini: 'gemini-2.0-flash-exp',
  anthropic: 'claude-3-5-sonnet-20241022',
  cerebras: 'llama3.1-8b',
  minimax: 'abab5.5-chat',
  openai: 'gpt-4',
}

export class LLMService extends BaseAPIService {
  private commandServerUrl: string

  constructor(commandServerUrl: string = 'http://localhost:5001', aimosConfig?: any) {
    // BaseAPIService expects a baseURL, but we'll use Command Server
    super('llm', commandServerUrl, undefined, 'llm', aimosConfig)
    this.commandServerUrl = commandServerUrl
  }

  isAvailable(): boolean {
    // LLM service is available if Command Server is accessible
    return true
  }

  /**
   * Get available models for a provider
   */
  getAvailableModels(provider: LLMProvider): LLMModel[] {
    return AVAILABLE_MODELS[provider] || []
  }

  /**
   * Get default model for a provider
   */
  getDefaultModel(provider: LLMProvider): string {
    return DEFAULT_MODELS[provider]
  }

  /**
   * Chat completion via MCP backend
   */
  async chatCompletion(
    request: LLMChatRequest
  ): Promise<APIResponse<LLMChatResponse>> {
    const model = request.model || this.getDefaultModel(request.provider)

    // Convert messages format for backend
    const backendMessages = request.messages.map((msg) => ({
      role: msg.role,
      content: msg.content,
    }))

    // Build request data for MCP call_api tool
    const requestData: any = {
      model,
      messages: backendMessages,
    }

    if (request.system) {
      requestData.system = request.system
    }
    if (request.temperature !== undefined) {
      requestData.temperature = request.temperature
    }
    if (request.maxTokens !== undefined) {
      requestData.max_tokens = request.maxTokens
    }

    // Call Command Server's MCP execute endpoint
    return this.handleRequest(
      async () => {
        // Call Command Server HTTP endpoint
        const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            tool: 'call_api',
            arguments: {
              provider: request.provider,
              endpoint: 'chat-completion',
              method: 'POST',
              data: requestData,
              integrate_aimos: true,
            },
          }),
        })

        if (!response.ok) {
          throw new Error(`Command Server error: ${response.status}`)
        }

        const result = await response.json()

        // Command Server returns: {success: true, tool: 'call_api', result: {...}}
        const apiResult = result.result || result

        if (!apiResult.success) {
          throw new Error(apiResult.error || 'LLM call failed')
        }

        // Transform backend response to frontend format
        const backendData = apiResult.data
        return {
          text: backendData.text,
          model: backendData.model,
          provider: request.provider,
          tokensUsed: backendData.tokens_used,
          latencyMs: backendData.latency_ms,
          confidence: backendData.confidence,
          metadata: backendData.metadata,
        }
      },
      'chat-completion',
      request
    )
  }

  /**
   * Stream chat completion (future implementation)
   */
  async streamChatCompletion(
    request: LLMChatRequest,
    onChunk: (chunk: LLMStreamChunk) => void
  ): Promise<void> {
    // TODO: Implement streaming via MCP backend
    // For now, fall back to non-streaming
    const response = await this.chatCompletion({ ...request, stream: false })
    if (response.success && response.data) {
      // Simulate streaming by chunking the response
      const text = response.data.text
      const chunkSize = 10
      for (let i = 0; i < text.length; i += chunkSize) {
        onChunk({
          text: text.slice(i, i + chunkSize),
          done: i + chunkSize >= text.length,
          model: response.data.model,
          tokensUsed: i + chunkSize >= text.length ? response.data.tokensUsed : undefined,
        })
        // Small delay to simulate streaming
        await new Promise((resolve) => setTimeout(resolve, 50))
      }
    }
  }

  /**
   * Simple prompt completion (convenience method)
   */
  async complete(
    prompt: string,
    provider: LLMProvider = 'gemini',
    model?: string,
    options?: {
      temperature?: number
      maxTokens?: number
      system?: string
    }
  ): Promise<APIResponse<LLMChatResponse>> {
    return this.chatCompletion({
      provider,
      model,
      messages: [{ role: 'user', content: prompt }],
      system: options?.system,
      temperature: options?.temperature,
      maxTokens: options?.maxTokens,
    })
  }
}

// Singleton instance
let llmServiceInstance: LLMService | null = null

export function getLLMService(mcpServerUrl?: string): LLMService {
  if (!llmServiceInstance) {
    llmServiceInstance = new LLMService(mcpServerUrl)
  }
  return llmServiceInstance
}

