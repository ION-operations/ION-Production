/**
 * Pentopix API Service
 * 3D model generation and manipulation
 */

import { BaseAPIService, APIResponse } from '../base/BaseAPIService'

export interface PentopixRequest {
  prompt: string
  style?: string
  quality?: 'low' | 'medium' | 'high'
}

export interface Pentopix3DResult {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  model_url?: string
  preview_url?: string
  error?: string
}

export class PentopixService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('pentopix', 'https://api.pentopix.com/v1', apiKey)
  }

  isAvailable(): boolean {
    return !!this.apiKey
  }

  async generate3D(
    request: PentopixRequest
  ): Promise<APIResponse<Pentopix3DResult>> {
    return this.handleRequest(async () => {
      const response = await this.client.post<Pentopix3DResult>(
        '/generate',
        {
          prompt: request.prompt,
          style: request.style,
          quality: request.quality || 'medium',
        }
      )
      return response
    })
  }

  async getTaskStatus(taskId: string): Promise<APIResponse<Pentopix3DResult>> {
    return this.handleRequest(async () => {
      const response = await this.client.get<Pentopix3DResult>(
        `/tasks/${taskId}`
      )
      return response
    })
  }
}

