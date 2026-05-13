/**
 * 3D Service - Unified interface for all 3D model APIs
 */

import { MeshyService, type MeshyV2TaskType } from './MeshyService'
import { PentopixService, PentopixRequest } from './PentopixService'
import { APIResponse } from '../base/BaseAPIService'

export interface ThreeDGenerationRequest {
  prompt: string
  image?: string // Data URI or public URL for image-to-3D
  provider?: 'meshy' | 'pentopix' | 'auto'
  // Meshy text-to-3d only
  mode?: 'preview' | 'refine'
  preview_task_id?: string // required if mode='refine'
}

export interface ThreeDResult {
  task_id: string
  provider: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  model_url?: string
  preview_url?: string
  progress?: number
}

export class ThreeDService {
  private meshy: MeshyService
  private pentopix: PentopixService

  constructor() {
    this.meshy = new MeshyService()
    this.pentopix = new PentopixService()
  }

  async generate(request: ThreeDGenerationRequest): Promise<APIResponse<ThreeDResult>> {
    const provider = request.provider || this.selectProvider()

    if (provider === 'meshy' && this.meshy.isAvailable()) {
      if (request.image) {
        const result = await this.meshy.imageTo3D({
          image_url: request.image,
          should_texture: true,
        })
        return this.mapMeshyResult(result, 'meshy')
      } else {
        const result = await this.meshy.textTo3D({
          mode: request.mode || 'preview',
          prompt: request.prompt,
          preview_task_id: request.preview_task_id,
        })
        return this.mapMeshyResult(result, 'meshy')
      }
    }

    if (provider === 'pentopix' && this.pentopix.isAvailable()) {
      const result = await this.pentopix.generate3D({
        prompt: request.prompt,
      })
      return this.mapPentopixResult(result, 'pentopix')
    }

    return {
      success: false,
      error: 'No 3D generation service available',
    }
  }

  private selectProvider(): 'meshy' | 'pentopix' {
    // Prefer Meshy if available, fallback to Pentopix
    if (this.meshy.isAvailable()) return 'meshy'
    if (this.pentopix.isAvailable()) return 'pentopix'
    return 'meshy' // Default
  }

  private mapMeshyResult(
    result: APIResponse<any>,
    provider: string
  ): APIResponse<ThreeDResult> {
    if (!result.success || !result.data) {
      return result as APIResponse<ThreeDResult>
    }

    const normalizeStatus = (status: string): 'pending' | 'processing' | 'completed' | 'failed' => {
      if (status === 'SUCCEEDED') return 'completed'
      if (status === 'FAILED' || status === 'CANCELED') return 'failed'
      if (status === 'IN_PROGRESS') return 'processing'
      return 'pending'
    }

    return {
      success: true,
      data: {
        task_id: result.data.task_id,
        provider,
        status: normalizeStatus(result.data.status),
        model_url: result.data.model_url,
        preview_url: result.data.preview_url,
        progress: result.data.progress,
      },
      metadata: result.metadata,
    }
  }

  private mapPentopixResult(
    result: APIResponse<any>,
    provider: string
  ): APIResponse<ThreeDResult> {
    if (!result.success || !result.data) {
      return result as APIResponse<ThreeDResult>
    }

    return {
      success: true,
      data: {
        task_id: result.data.task_id,
        provider,
        status: result.data.status,
        model_url: result.data.model_url,
        preview_url: result.data.preview_url,
      },
      metadata: result.metadata,
    }
  }

  async getTaskStatus(
    taskId: string,
    provider: 'meshy' | 'pentopix',
    taskType: MeshyV2TaskType = 'text-to-3d'
  ): Promise<APIResponse<ThreeDResult>> {
    if (provider === 'meshy') {
      const result = await this.meshy.getTaskStatus(taskId, taskType)
      return this.mapMeshyResult(result, 'meshy')
    } else {
      const result = await this.pentopix.getTaskStatus(taskId)
      return this.mapPentopixResult(result, 'pentopix')
    }
  }
}

