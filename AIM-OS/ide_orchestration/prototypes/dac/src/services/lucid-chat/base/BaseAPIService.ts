/**
 * Base API Service for Lucid Chat
 * All API services extend this base class
 * 
 * Phase 1: Integrated with AIM-OS systems (CMC, HHNI, VIF, SEG)
 */

import { APIClient } from './APIClient'
import {
  getAIMOSIntegrationService,
  AIMOSIntegrationConfig,
  APIResponseMetadata,
} from '../aimos/AIMOSIntegrationService'

export interface APIResponse<T> {
  success: boolean
  data?: T
  error?: string
  metadata?: {
    provider: string
    latency: number
    cached: boolean
    tokens?: number
    cost?: number
  }
  aimos?: {
    cmc?: { atom_id?: string }
    hhni?: { indexed: boolean }
    vif?: { witness_id?: string }
    seg?: { entities_created?: number; relations_created?: number }
  }
}

export abstract class BaseAPIService {
  protected client: APIClient
  protected apiKey: string | null
  protected baseURL: string
  protected provider: string
  protected apiName: string
  protected aimosIntegration: ReturnType<typeof getAIMOSIntegrationService>
  protected aimosConfig: AIMOSIntegrationConfig

  constructor(
    provider: string,
    baseURL: string,
    apiKey?: string,
    apiName?: string,
    aimosConfig?: AIMOSIntegrationConfig
  ) {
    this.provider = provider
    this.baseURL = baseURL
    this.apiName = apiName || provider
    this.apiKey = apiKey || this.getAPIKeyFromEnv()
    this.aimosConfig = aimosConfig || { enabled: true }
    this.aimosIntegration = getAIMOSIntegrationService(this.aimosConfig)
    this.client = new APIClient(baseURL, {
      headers: this.getDefaultHeaders(),
      timeout: 30000,
      retries: 3,
      cache: true,
    })
  }

  protected getAPIKeyFromEnv(): string | null {
    const envKey = `${this.provider.toUpperCase()}_API_KEY`
    // Vite uses import.meta.env for environment variables
    // Support both VITE_ prefix and direct provider name
    return (
      (import.meta.env[`VITE_${envKey}`] as string) ||
      (import.meta.env[envKey] as string) ||
      null
    )
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

  protected async handleRequest<T>(
    request: () => Promise<T>,
    endpoint: string = 'unknown',
    requestData?: any
  ): Promise<APIResponse<T>> {
    const startTime = Date.now()
    
    try {
      const data = await request()
      const latency = Date.now() - startTime
      
      const response: APIResponse<T> = {
        success: true,
        data,
        metadata: {
          provider: this.provider,
          latency,
          cached: false,
        },
      }

      // Integrate with AIM-OS systems
      if (this.aimosConfig.enabled) {
        const metadata: APIResponseMetadata = {
          provider: this.provider,
          api: this.apiName,
          endpoint,
          request: requestData,
          response: data,
          latency,
          timestamp: new Date().toISOString(),
          success: true,
        }

        const aimosResult = await this.aimosIntegration.integrateAPIResponse(metadata)
        response.aimos = {
          cmc: aimosResult.cmc?.success ? { atom_id: aimosResult.cmc.atom_id } : undefined,
          hhni: aimosResult.hhni?.success ? { indexed: aimosResult.hhni.indexed } : undefined,
          vif: aimosResult.vif?.success ? { witness_id: aimosResult.vif.witness_id } : undefined,
          seg: aimosResult.seg?.success
            ? {
                entities_created: aimosResult.seg.entities_created,
                relations_created: aimosResult.seg.relations_created,
              }
            : undefined,
        }
      }
      
      return response
    } catch (error: any) {
      const latency = Date.now() - startTime
      
      const response: APIResponse<T> = {
        success: false,
        error: error.message || 'Unknown error',
        metadata: {
          provider: this.provider,
          latency,
          cached: false,
        },
      }

      // Integrate error with AIM-OS systems
      if (this.aimosConfig.enabled) {
        const metadata: APIResponseMetadata = {
          provider: this.provider,
          api: this.apiName,
          endpoint,
          request: requestData,
          response: null,
          latency,
          timestamp: new Date().toISOString(),
          success: false,
          error: error.message || 'Unknown error',
        }

        const aimosResult = await this.aimosIntegration.integrateAPIResponse(metadata)
        response.aimos = {
          cmc: aimosResult.cmc?.success ? { atom_id: aimosResult.cmc.atom_id } : undefined,
          vif: aimosResult.vif?.success ? { witness_id: aimosResult.vif.witness_id } : undefined,
        }
      }
      
      return response
    }
  }

  abstract isAvailable(): boolean
}

