/**
 * Minimax API Service
 * LLM chat completion and video generation
 */

import { BaseAPIService, APIResponse } from '../base/BaseAPIService'

export interface MinimaxChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export interface MinimaxChatRequest {
  model: string
  messages: MinimaxChatMessage[]
  temperature?: number
  max_tokens?: number
  stream?: boolean
  top_p?: number
  frequency_penalty?: number
  presence_penalty?: number
}

export interface MinimaxChatResponse {
  id: string
  object: string
  created: number
  model: string
  choices: Array<{
    index: number
    message: {
      role: 'assistant'
      content: string
    }
    finish_reason: string
  }>
  usage: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}

export interface MinimaxChatChunk {
  id: string
  object: string
  created: number
  model: string
  choices: Array<{
    index: number
    delta: {
      role?: 'assistant'
      content?: string
    }
    finish_reason?: string
  }>
}

export interface MinimaxVideoRequest {
  model: 'hailuo' | 'hailuo-director'
  image_url?: string
  prompt: string
  duration?: number
  camera_motion?: string
  style?: string
}

export interface MinimaxVideoResponse {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress?: number
  video_url?: string
  preview_url?: string
  error?: string
}

export class MinimaxService extends BaseAPIService {
  constructor(apiKey?: string) {
    // Estimated base URL - may need adjustment based on actual API
    super('minimax', 'https://api.minimax.chat/v1', apiKey)
  }

  isAvailable(): boolean {
    return !!this.apiKey
  }

  protected getDefaultHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }
    
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`
    }
    
    return headers
  }

  async chatCompletion(
    request: MinimaxChatRequest
  ): Promise<APIResponse<MinimaxChatResponse>> {
    return this.handleRequest(
      async () => {
        const response = await this.client.post<MinimaxChatResponse>(
          '/chat/completions',
          {
            model: request.model,
            messages: request.messages,
            temperature: request.temperature ?? 0.7,
            max_tokens: request.max_tokens,
            top_p: request.top_p,
            frequency_penalty: request.frequency_penalty,
            presence_penalty: request.presence_penalty,
            stream: false,
          }
        )
        return response
      },
      '/chat/completions',
      request
    )
  }

  async streamChatCompletion(
    request: MinimaxChatRequest,
    onChunk: (chunk: MinimaxChatChunk) => void
  ): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}/chat/completions`, {
        method: 'POST',
        headers: this.getDefaultHeaders(),
        body: JSON.stringify({
          ...request,
          stream: true,
        }),
      })

      if (!response.ok) {
        throw new Error(`Minimax API Error: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('Response body is not readable')
      }

      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              return
            }
            try {
              const chunk: MinimaxChatChunk = JSON.parse(data)
              onChunk(chunk)
            } catch (e) {
              console.error('Error parsing chunk:', e)
            }
          }
        }
      }
    } catch (error: any) {
      throw new Error(`Streaming error: ${error.message}`)
    }
  }

  async generateVideo(
    request: MinimaxVideoRequest
  ): Promise<APIResponse<MinimaxVideoResponse>> {
    return this.handleRequest(
      async () => {
        const response = await this.client.post<MinimaxVideoResponse>(
          '/video/generate',
          {
            model: request.model,
            image_url: request.image_url,
            prompt: request.prompt,
            duration: request.duration ?? 6,
            camera_motion: request.camera_motion,
            style: request.style,
          }
        )
        return response
      },
      '/video/generate',
      request
    )
  }

  async getTaskStatus(taskId: string): Promise<APIResponse<MinimaxVideoResponse>> {
    return this.handleRequest(
      async () => {
        const response = await this.client.get<MinimaxVideoResponse>(
          `/video/tasks/${taskId}`
        )
        return response
      },
      `/video/tasks/${taskId}`,
      { taskId }
    )
  }

  async pollTaskStatus(
    taskId: string,
    onProgress?: (progress: number, status: string) => void,
    interval: number = 2000,
    maxAttempts: number = 150
  ): Promise<APIResponse<MinimaxVideoResponse>> {
    let attempts = 0
    
    while (attempts < maxAttempts) {
      const result = await this.getTaskStatus(taskId)
      
      if (!result.success || !result.data) {
        return result
      }
      
      const { status, progress } = result.data
      
      if (onProgress && progress !== undefined) {
        onProgress(progress, status)
      }
      
      if (status === 'completed') {
        return result
      }
      
      if (status === 'failed') {
        return {
          success: false,
          error: result.data.error || 'Task failed',
          metadata: result.metadata,
        }
      }
      
      await new Promise(resolve => setTimeout(resolve, interval))
      attempts++
    }
    
    return {
      success: false,
      error: 'Task polling timeout',
    }
  }
}

