/**
 * Meshy API Service
 * Text-to-3D and Image-to-3D model generation
 */

import { BaseAPIService, APIResponse } from '../base/BaseAPIService'
import { APIClient } from '../base/APIClient'

export type MeshyV2TaskType =
  | 'text-to-3d'
  | 'image-to-3d'
  | 'multi-image-to-3d'
  | 'remesh'
  | 'retexture'

export interface MeshyTextTo3DRequest {
  mode: 'preview' | 'refine' // Two-stage workflow: preview generates mesh, refine adds texture
  prompt?: string // Required for preview mode (max 600 chars)
  preview_task_id?: string // Required for refine mode (preview task must be SUCCEEDED)
  art_style?: 'realistic' | 'sculpture'
  seed?: number
  ai_model?: 'meshy-4' | 'meshy-5' | 'latest' // Default: 'latest' (Meshy 6 Preview)
  topology?: 'quad' | 'triangle' // Default: 'triangle'
  target_polycount?: number // 100 to 300,000, default: 30,000
  should_remesh?: boolean // Default: true
  symmetry_mode?: 'off' | 'auto' | 'on' // Default: 'auto'
  pose_mode?: '' | 'a-pose' | 't-pose'
  /**
   * @deprecated Meshy docs mark `is_a_t_pose` as deprecated. Use `pose_mode` instead.
   */
  is_a_t_pose?: boolean
  moderation?: boolean // Default: false
  // Refine-only parameters
  enable_pbr?: boolean // Generate PBR maps (metallic, roughness, normal)
  texture_prompt?: string // Additional prompt for texturing (max 600 chars)
  texture_image_url?: string // Image URL or data URI for texture guidance
}

export interface MeshyImageTo3DRequest {
  image_url: string // Publicly accessible URL or Data URI (.jpg/.jpeg/.png)
  ai_model?: 'meshy-4' | 'meshy-5' | 'latest'
  topology?: 'quad' | 'triangle'
  target_polycount?: number
  symmetry_mode?: 'off' | 'auto' | 'on'
  should_remesh?: boolean
  save_pre_remeshed_model?: boolean
  should_texture?: boolean
  enable_pbr?: boolean
  pose_mode?: '' | 'a-pose' | 't-pose'
  /**
   * @deprecated Use `pose_mode` instead.
   */
  is_a_t_pose?: boolean
  texture_prompt?: string // Max 600 chars
  texture_image_url?: string // Public URL or Data URI
  moderation?: boolean
}

export interface MeshyMultiImageTo3DRequest {
  image_url: string[] // 1–4 images, each public URL or Data URI
  ai_model?: 'meshy-5' | 'latest'
  topology?: 'quad' | 'triangle'
  target_polycount?: number
  symmetry_mode?: 'off' | 'auto' | 'on'
  should_remesh?: boolean
  save_pre_remeshed_model?: boolean
  should_texture?: boolean
  enable_pbr?: boolean
  pose_mode?: '' | 'a-pose' | 't-pose'
  /**
   * @deprecated Use `pose_mode` instead.
   */
  is_a_t_pose?: boolean
  texture_prompt?: string
  texture_image_url?: string
  moderation?: boolean
}

export interface MeshyRemeshRequest {
  input_task_id?: string // Completed Image-to-3D or Text-to-3D task ID
  model_url?: string // Public URL or Data URI (.glb/.gltf/.obj/.fbx/.stl)
  target_format?: Array<'glb' | 'fbx' | 'obj' | 'usdz' | 'blend' | 'stl'> // Default: ['glb']
  target_polycount?: number // 100 to 300,000
  topology?: 'quad' | 'triangle'
  resize_height?: number // meters; 0 = no resize
  convert_format_only?: boolean
}

export interface MeshyRetextureRequest {
  model_url: string // Public URL or Data URI (.glb/.gltf/.obj/.fbx/.stl)
  text_style_prompt?: string // Required if image_style_url not provided (max 600 chars)
  image_style_url?: string // Optional public URL or Data URI
  enable_pbr?: boolean
}

export interface MeshyRigRequest {
  input_task_id?: string // Recommended if you have a Meshy task
  model_url?: string // Public URL or Data URI (textured humanoid GLB)
  height_meters?: number // Default: 1.7
  texture_image_url?: string // Optional base color texture PNG (URL or Data URI)
}

export interface MeshyModelUrlMap {
  glb?: string
  fbx?: string
  usdz?: string
  obj?: string
  mtl?: string
  blend?: string
  stl?: string
}

export interface Meshy3DResult {
  id: string // Task ID (k-sortable UUID)
  /**
   * Raw API responses across Meshy endpoints may use either `model_url` (docs) or `model_urls` (legacy).
   * We normalize both and also provide a legacy `model_url` string for GLB compatibility.
   */
  model_urls?: MeshyModelUrlMap
  model_url?: MeshyModelUrlMap | string
  prompt?: string
  art_style?: string
  texture_prompt?: string
  texture_image_url?: string
  thumbnail_url?: string
  video_url?: string
  progress: number // 0-100
  seed?: number
  started_at: number // Timestamp in milliseconds
  created_at: number // Timestamp in milliseconds
  finished_at: number // Timestamp in milliseconds
  status: 'PENDING' | 'IN_PROGRESS' | 'SUCCEEDED' | 'FAILED' | 'CANCELED'
  texture_urls?: Array<{
    base_color?: string
    metallic?: string
    normal?: string
    roughness?: string
  }>
  preceding_tasks?: number
  task_error?: {
    message: string
  }
  // Legacy fields for backward compatibility
  task_id?: string // Deprecated, use id
  // `model_url` is also used by docs as an object. When present as a string, treat as GLB.
  preview_url?: string // Deprecated, use thumbnail_url
  error?: string // Deprecated, use task_error.message
}

export class MeshyService extends BaseAPIService {
  private v1Client: APIClient

  constructor(apiKey?: string) {
    super('meshy', 'https://api.meshy.ai/openapi/v2', apiKey)
    this.v1Client = new APIClient('https://api.meshy.ai/openapi/v1', {
      headers: this.getDefaultHeaders(),
      timeout: 30000,
      retries: 3,
      cache: true,
    })
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

  isAvailable(): boolean {
    return !!this.apiKey
  }

  private getV2TaskPath(taskType: MeshyV2TaskType, taskId: string): string {
    switch (taskType) {
      case 'text-to-3d':
        return `/text-to-3d/${taskId}`
      case 'image-to-3d':
        return `/image-to-3d/${taskId}`
      case 'multi-image-to-3d':
        return `/multi-image-to-3d/${taskId}`
      case 'remesh':
        return `/remesh/${taskId}`
      case 'retexture':
        return `/retexture/${taskId}`
      default: {
        const exhaustiveCheck: never = taskType
        return exhaustiveCheck
      }
    }
  }

  private extractModelUrls(result: Meshy3DResult): MeshyModelUrlMap | undefined {
    if (result.model_urls) return result.model_urls
    if (result.model_url && typeof result.model_url === 'object') return result.model_url
    return undefined
  }

  private extractGlbUrl(result: Meshy3DResult): string | undefined {
    const urls = this.extractModelUrls(result)
    if (urls?.glb) return urls.glb
    if (typeof result.model_url === 'string') return result.model_url
    return undefined
  }

  private normalizeV2TaskResult(response: Meshy3DResult): Meshy3DResult {
    const modelUrls = this.extractModelUrls(response)
    const glbUrl = this.extractGlbUrl(response)
    return {
      ...response,
      model_urls: modelUrls,
      task_id: response.id,
      model_url: glbUrl,
      preview_url: response.thumbnail_url,
      error: response.task_error?.message,
    }
  }

  async textTo3D(
    request: MeshyTextTo3DRequest
  ): Promise<APIResponse<Meshy3DResult>> {
    return this.handleRequest(
      async () => {
        const body: any = { mode: request.mode }

        if (request.mode === 'preview') {
          if (!request.prompt) {
            throw new Error('Text-to-3D preview requires `prompt`.')
          }
          body.prompt = request.prompt
        } else {
          if (!request.preview_task_id) {
            throw new Error('Text-to-3D refine requires `preview_task_id`.')
          }
          body.preview_task_id = request.preview_task_id
        }

        // Optional parameters
        if (request.art_style) body.art_style = request.art_style
        if (request.seed !== undefined) body.seed = request.seed
        if (request.ai_model) body.ai_model = request.ai_model
        if (request.topology) body.topology = request.topology
        if (request.target_polycount !== undefined) body.target_polycount = request.target_polycount
        if (request.should_remesh !== undefined) body.should_remesh = request.should_remesh
        if (request.symmetry_mode) body.symmetry_mode = request.symmetry_mode
        if (request.pose_mode !== undefined) body.pose_mode = request.pose_mode
        if (request.is_a_t_pose !== undefined) body.is_a_t_pose = request.is_a_t_pose
        if (request.moderation !== undefined) body.moderation = request.moderation

        // Refine-only parameters
        if (request.mode === 'refine') {
          if (request.enable_pbr !== undefined) body.enable_pbr = request.enable_pbr
          if (request.texture_prompt) body.texture_prompt = request.texture_prompt
          if (request.texture_image_url) body.texture_image_url = request.texture_image_url
        }

        const response = await this.client.post<{ result: string }>(
          '/text-to-3d',
          body
        )
        
        // API returns { result: "task-id" }, we need to fetch the task details
        const taskId = response.result
        const task = await this.getTaskStatus(taskId, 'text-to-3d')
        if (!task.success || !task.data) {
          throw new Error(task.error || 'Failed to retrieve created task')
        }
        return task.data
      },
      '/text-to-3d',
      request
    )
  }

  async imageTo3D(
    request: MeshyImageTo3DRequest
  ): Promise<APIResponse<Meshy3DResult>> {
    return this.handleRequest(
      async () => {
        const body: any = {
          image_url: request.image_url,
        }

        if (request.ai_model) body.ai_model = request.ai_model
        if (request.topology) body.topology = request.topology
        if (request.target_polycount !== undefined) body.target_polycount = request.target_polycount
        if (request.should_remesh !== undefined) body.should_remesh = request.should_remesh
        if (request.save_pre_remeshed_model !== undefined) body.save_pre_remeshed_model = request.save_pre_remeshed_model
        if (request.should_texture !== undefined) body.should_texture = request.should_texture
        if (request.enable_pbr !== undefined) body.enable_pbr = request.enable_pbr
        if (request.symmetry_mode) body.symmetry_mode = request.symmetry_mode
        if (request.pose_mode !== undefined) body.pose_mode = request.pose_mode
        if (request.is_a_t_pose !== undefined) body.is_a_t_pose = request.is_a_t_pose
        if (request.texture_prompt) body.texture_prompt = request.texture_prompt
        if (request.texture_image_url) body.texture_image_url = request.texture_image_url
        if (request.moderation !== undefined) body.moderation = request.moderation

        const response = await this.client.post<{ result: string }>(
          '/image-to-3d',
          body
        )
        
        const taskId = response.result
        const task = await this.getTaskStatus(taskId, 'image-to-3d')
        if (!task.success || !task.data) {
          throw new Error(task.error || 'Failed to retrieve created task')
        }
        return task.data
      },
      '/image-to-3d',
      request
    )
  }

  async multiImageTo3D(
    request: MeshyMultiImageTo3DRequest
  ): Promise<APIResponse<Meshy3DResult>> {
    return this.handleRequest(
      async () => {
        const body: any = {
          image_url: request.image_url,
        }

        if (request.ai_model) body.ai_model = request.ai_model
        if (request.topology) body.topology = request.topology
        if (request.target_polycount !== undefined) body.target_polycount = request.target_polycount
        if (request.should_remesh !== undefined) body.should_remesh = request.should_remesh
        if (request.save_pre_remeshed_model !== undefined) body.save_pre_remeshed_model = request.save_pre_remeshed_model
        if (request.should_texture !== undefined) body.should_texture = request.should_texture
        if (request.enable_pbr !== undefined) body.enable_pbr = request.enable_pbr
        if (request.symmetry_mode) body.symmetry_mode = request.symmetry_mode
        if (request.pose_mode !== undefined) body.pose_mode = request.pose_mode
        if (request.is_a_t_pose !== undefined) body.is_a_t_pose = request.is_a_t_pose
        if (request.texture_prompt) body.texture_prompt = request.texture_prompt
        if (request.texture_image_url) body.texture_image_url = request.texture_image_url
        if (request.moderation !== undefined) body.moderation = request.moderation

        const response = await this.client.post<{ result: string }>(
          '/multi-image-to-3d',
          body
        )
        
        const taskId = response.result
        const task = await this.getTaskStatus(taskId, 'multi-image-to-3d')
        if (!task.success || !task.data) {
          throw new Error(task.error || 'Failed to retrieve created task')
        }
        return task.data
      },
      '/multi-image-to-3d',
      request
    )
  }

  async remesh(
    request: MeshyRemeshRequest
  ): Promise<APIResponse<Meshy3DResult>> {
    return this.handleRequest(
      async () => {
        const body: any = {}
        if (request.input_task_id) body.input_task_id = request.input_task_id
        if (request.model_url) body.model_url = request.model_url
        if (!body.input_task_id && !body.model_url) {
          throw new Error('Remesh requires either `input_task_id` or `model_url`.')
        }

        if (request.target_format) body.target_format = request.target_format
        if (request.target_polycount !== undefined) body.target_polycount = request.target_polycount
        if (request.topology) body.topology = request.topology
        if (request.resize_height !== undefined) body.resize_height = request.resize_height
        if (request.convert_format_only !== undefined) body.convert_format_only = request.convert_format_only

        const response = await this.client.post<{ result: string }>(
          '/remesh',
          body
        )
        
        const taskId = response.result
        const task = await this.getTaskStatus(taskId, 'remesh')
        if (!task.success || !task.data) {
          throw new Error(task.error || 'Failed to retrieve created task')
        }
        return task.data
      },
      '/remesh',
      request
    )
  }

  async retexture(
    request: MeshyRetextureRequest
  ): Promise<APIResponse<Meshy3DResult>> {
    return this.handleRequest(
      async () => {
        const body: any = {
          model_url: request.model_url,
        }

        if (request.text_style_prompt) body.text_style_prompt = request.text_style_prompt
        if (request.image_style_url) body.image_style_url = request.image_style_url
        if (!body.text_style_prompt && !body.image_style_url) {
          throw new Error('Retexture requires `text_style_prompt` or `image_style_url`.')
        }
        if (request.enable_pbr !== undefined) body.enable_pbr = request.enable_pbr

        const response = await this.client.post<{ result: string }>(
          '/retexture',
          body
        )
        
        const taskId = response.result
        const task = await this.getTaskStatus(taskId, 'retexture')
        if (!task.success || !task.data) {
          throw new Error(task.error || 'Failed to retrieve created task')
        }
        return task.data
      },
      '/retexture',
      request
    )
  }

  async rig(
    request: MeshyRigRequest
  ): Promise<APIResponse<Meshy3DResult>> {
    return this.handleRequest(
      async () => {
        const body: any = {}
        if (request.input_task_id) body.input_task_id = request.input_task_id
        if (request.model_url) body.model_url = request.model_url
        if (!body.input_task_id && !body.model_url) {
          throw new Error('Rigging requires either `input_task_id` or `model_url`.')
        }
        if (request.height_meters !== undefined) body.height_meters = request.height_meters
        if (request.texture_image_url) body.texture_image_url = request.texture_image_url

        // Rigging/animation are documented under OpenAPI v1.
        const response = await this.v1Client.post<{ result: string }>(
          '/rigging',
          body
        )

        const taskId = response.result
        // NOTE: Rigging task response schema differs; we return a minimal Meshy3DResult-shaped object
        // for compatibility (status/progress are expected to be present on retrieval).
        // If retrieval fails due to API changes, caller should handle the error.
        const rigTask = await this.v1Client.get<any>(`/rigging/${taskId}`)
        return {
          id: rigTask.id || taskId,
          status: rigTask.status,
          progress: rigTask.progress ?? 0,
          task_error: rigTask.task_error,
          // Provide a best-effort GLB URL for viewer compatibility
          model_urls: rigTask.result?.rigged_character_glb_url
            ? { glb: rigTask.result.rigged_character_glb_url }
            : undefined,
          thumbnail_url: undefined,
          started_at: rigTask.started_at ?? 0,
          created_at: rigTask.created_at ?? Date.now(),
          finished_at: rigTask.finished_at ?? 0,
        }
      },
      '/openapi/v1/rigging',
      request
    )
  }

  private normalizeRigTask(rigTask: any, fallbackId: string): Meshy3DResult {
    return {
      id: rigTask.id || fallbackId,
      status: rigTask.status,
      progress: rigTask.progress ?? 0,
      task_error: rigTask.task_error,
      // Provide a best-effort GLB URL for viewer compatibility
      model_urls: rigTask.result?.rigged_character_glb_url
        ? { glb: rigTask.result.rigged_character_glb_url }
        : undefined,
      thumbnail_url: undefined,
      started_at: rigTask.started_at ?? 0,
      created_at: rigTask.created_at ?? Date.now(),
      finished_at: rigTask.finished_at ?? 0,
    }
  }

  async getRigTaskStatus(taskId: string): Promise<APIResponse<Meshy3DResult>> {
    return this.handleRequest(
      async () => {
        const rigTask = await this.v1Client.get<any>(`/rigging/${taskId}`)
        return this.normalizeRigTask(rigTask, taskId)
      },
      `/openapi/v1/rigging/${taskId}`,
      { taskId }
    )
  }

  async pollRigTaskStatus(
    taskId: string,
    onProgress?: (progress: number, status: string) => void,
    interval: number = 2000,
    maxAttempts: number = 150
  ): Promise<APIResponse<Meshy3DResult>> {
    let attempts = 0

    while (attempts < maxAttempts) {
      const result = await this.getRigTaskStatus(taskId)

      if (!result.success || !result.data) {
        return result
      }

      const { status, progress } = result.data

      if (onProgress && progress !== undefined) {
        onProgress(progress, status)
      }

      if (status === 'SUCCEEDED') {
        return result
      }

      if (status === 'FAILED' || status === 'CANCELED') {
        return {
          success: false,
          error: result.data.task_error?.message || result.data.error || 'Task failed',
          metadata: result.metadata,
        }
      }

      await new Promise((resolve) => setTimeout(resolve, interval))
      attempts++
    }

    return {
      success: false,
      error: 'Task polling timeout',
    }
  }

  async balance(): Promise<APIResponse<{ balance: number }>> {
    return this.handleRequest(
      async () => {
        const response = await this.client.get<{ balance: number }>('/balance')
        return response
      },
      '/balance',
      {}
    )
  }

  async getTaskStatus(
    taskId: string,
    taskType: MeshyV2TaskType = 'text-to-3d'
  ): Promise<APIResponse<Meshy3DResult>> {
    return this.handleRequest(
      async () => {
        const response = await this.client.get<Meshy3DResult>(this.getV2TaskPath(taskType, taskId))
        return this.normalizeV2TaskResult(response)
      },
      this.getV2TaskPath(taskType, taskId),
      { taskId, taskType }
    )
  }

  /**
   * Poll task status until completion or failure
   * @param taskId Task ID to poll
   * @param onProgress Optional callback for progress updates
   * @param interval Polling interval in milliseconds (default: 2000)
   * @param maxAttempts Maximum polling attempts (default: 150 = 5 minutes)
   */
  async pollTaskStatus(
    taskId: string,
    onProgress?: (progress: number, status: string) => void,
    interval: number = 2000,
    maxAttempts: number = 150,
    taskType: MeshyV2TaskType = 'text-to-3d'
  ): Promise<APIResponse<Meshy3DResult>> {
    let attempts = 0
    
    while (attempts < maxAttempts) {
      const result = await this.getTaskStatus(taskId, taskType)
      
      if (!result.success || !result.data) {
        return result
      }
      
      const { status, progress } = result.data
      
      // Call progress callback
      if (onProgress && progress !== undefined) {
        // Pass raw Meshy status (PENDING/IN_PROGRESS/SUCCEEDED/FAILED/CANCELED)
        onProgress(progress, status)
      }
      
      // Check if completed or failed
      if (status === 'SUCCEEDED') {
        return result
      }
      
      if (status === 'FAILED' || status === 'CANCELED') {
        return {
          success: false,
          error: result.data.task_error?.message || result.data.error || 'Task failed',
          metadata: result.metadata,
        }
      }
      
      // Wait before next poll
      await new Promise(resolve => setTimeout(resolve, interval))
      attempts++
    }
    
    return {
      success: false,
      error: 'Task polling timeout',
    }
  }
}

