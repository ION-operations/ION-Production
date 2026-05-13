/**
 * LLM Service for Manager AI Chat
 * Handles LLM API integration with streaming support
 */

export interface LLMRequest {
  prompt: string
  context?: string[]
  systemPrompt?: string
  model?: string
  temperature?: number
  maxTokens?: number
  stream?: boolean
}

export interface LLMResponse {
  content: string
  model: string
  usage?: {
    promptTokens: number
    completionTokens: number
    totalTokens: number
  }
  finishReason?: string
}

export interface LLMStreamChunk {
  content: string
  done: boolean
}

/**
 * LLM Service Interface
 * Supports multiple providers (OpenAI, Anthropic, etc.)
 */
export interface LLMService {
  generate(request: LLMRequest): Promise<LLMResponse>
  stream(request: LLMRequest): AsyncGenerator<LLMStreamChunk>
}

/**
 * Manager AI LLM Service
 * Integrates with Command Server /aimos/chat endpoint or direct LLM APIs
 */
export class ManagerAILLMService implements LLMService {
  private commandServerUrl: string
  private useCommandServer: boolean

  constructor(commandServerUrl: string = 'http://localhost:5001', useCommandServer: boolean = true) {
    this.commandServerUrl = commandServerUrl
    this.useCommandServer = useCommandServer
  }

  /**
   * Generate a response using Command Server /aimos/chat endpoint
   */
  async generate(request: LLMRequest): Promise<LLMResponse> {
    if (this.useCommandServer) {
      return this.generateViaCommandServer(request)
    } else {
      return this.generateDirect(request)
    }
  }

  /**
   * Generate via Command Server
   */
  private async generateViaCommandServer(request: LLMRequest): Promise<LLMResponse> {
    try {
      const response = await fetch(`${this.commandServerUrl}/aimos/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          prompt: request.prompt,
          references: request.context?.map((c, i) => ({
            name: `context_${i}`,
            uri: `data:text/plain;base64,${btoa(c)}`
          }))
        })
      })

      if (!response.ok) {
        throw new Error(`Command Server error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()

      return {
        content: data.response || data.content || '',
        model: data.model || 'gpt-4-turbo',
        usage: data.usage,
        finishReason: data.finishReason
      }
    } catch (error) {
      console.error('LLM Service error:', error)
      throw error
    }
  }

  /**
   * Generate directly via LLM API (future implementation)
   */
  private async generateDirect(request: LLMRequest): Promise<LLMResponse> {
    // TODO: Implement direct LLM API integration
    // For now, fallback to Command Server
    return this.generateViaCommandServer(request)
  }

  /**
   * Stream response chunks
   */
  async *stream(request: LLMRequest): AsyncGenerator<LLMStreamChunk> {
    if (this.useCommandServer) {
      yield* this.streamViaCommandServer(request)
    } else {
      yield* this.streamDirect(request)
    }
  }

  /**
   * Stream via Command Server
   */
  private async *streamViaCommandServer(request: LLMRequest): AsyncGenerator<LLMStreamChunk> {
    try {
      const response = await fetch(`${this.commandServerUrl}/aimos/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          prompt: request.prompt,
          references: request.context?.map((c, i) => ({
            name: `context_${i}`,
            uri: `data:text/plain;base64,${btoa(c)}`
          })),
          stream: true
        })
      })

      if (!response.ok) {
        throw new Error(`Command Server error: ${response.status} ${response.statusText}`)
      }

      // Check if response is streaming
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('text/event-stream')) {
        const reader = response.body?.getReader()
        const decoder = new TextDecoder()

        if (reader) {
          let buffer = ''
          while (true) {
            const { done, value } = await reader.read()
            if (done) {
              yield { content: buffer, done: true }
              break
            }

            const chunk = decoder.decode(value, { stream: true })
            buffer += chunk

            // Yield chunks as they arrive
            const lines = buffer.split('\n')
            buffer = lines.pop() || ''

            for (const line of lines) {
              if (line.trim()) {
                try {
                  const data = JSON.parse(line)
                  yield { content: data.content || data.chunk || '', done: false }
                } catch {
                  // Not JSON, yield as text
                  yield { content: line, done: false }
                }
              }
            }
          }
        }
      } else {
        // Non-streaming response
        const data = await response.json()
        yield { content: data.response || data.content || '', done: true }
      }
    } catch (error) {
      console.error('LLM Stream error:', error)
      yield { content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`, done: true }
    }
  }

  /**
   * Stream directly via LLM API (future implementation)
   */
  private async *streamDirect(request: LLMRequest): AsyncGenerator<LLMStreamChunk> {
    // TODO: Implement direct LLM API streaming
    // For now, fallback to Command Server
    yield* this.streamViaCommandServer(request)
  }
}

// Singleton instance
export const llmService = new ManagerAILLMService()

