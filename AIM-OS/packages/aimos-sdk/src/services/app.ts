/**
 * App Service - Application lifecycle management
 */

import { AIMOSClient } from '../client'
import {
  AppManifest,
  AppRegistrationResult,
  ApplicationData,
} from '../types'

/**
 * App class representing a registered application
 */
export class App {
  constructor(
    private client: AIMOSClient,
    public readonly data: ApplicationData
  ) {}

  /**
   * Get app ID
   */
  get id(): string {
    return this.data.app_id
  }

  /**
   * Get app name
   */
  get name(): string {
    return this.data.app_name
  }

  /**
   * Get app status
   */
  get status(): string {
    return this.data.status
  }

  /**
   * Deploy app to environment
   * 
   * @param params Deployment parameters
   * @returns Deployment result
   */
  async deploy(params: {
    environment: string
    config_overrides?: any
  }): Promise<any> {
    return this.client.executeTool('deploy_application', {
      app_id: this.id,
      environment: params.environment,
      config_overrides: params.config_overrides || {},
    })
  }

  /**
   * Start app
   */
  async start(): Promise<any> {
    return this.client.executeTool('manage_application_lifecycle', {
      app_id: this.id,
      action: 'start',
    })
  }

  /**
   * Stop app
   */
  async stop(): Promise<any> {
    return this.client.executeTool('manage_application_lifecycle', {
      app_id: this.id,
      action: 'stop',
    })
  }

  /**
   * Restart app
   */
  async restart(): Promise<any> {
    return this.client.executeTool('manage_application_lifecycle', {
      app_id: this.id,
      action: 'restart',
    })
  }

  /**
   * Get app status
   */
  async getStatus(): Promise<any> {
    return this.client.executeTool('manage_application_lifecycle', {
      app_id: this.id,
      action: 'status',
    })
  }

  /**
   * Get app metrics
   */
  async getMetrics(): Promise<any> {
    const result = await this.client.executeTool('retrieve_memory', {
      query: `metrics for ${this.name}`,
      tags: { type: 'app_metrics', app_id: this.id },
      limit: 10,
    })

    return result.results || []
  }
}

/**
 * App Service for application lifecycle management
 */
export class AppService {
  constructor(private client: AIMOSClient) {}

  /**
   * Register a new application
   * 
   * @param manifest App manifest
   * @returns Registered App instance
   */
  async register(manifest: AppManifest): Promise<App> {
    const result: AppRegistrationResult = await this.client.executeTool('create_application', {
      app_name: manifest.app_name,
      app_type: manifest.app_type,
      config: manifest,
      dependencies: manifest.dependencies?.other_apps || [],
    })

    if (!result.success || !result.application) {
      throw new Error(result.error || 'Application registration failed')
    }

    return new App(this.client, result.application)
  }

  /**
   * List all registered applications
   * 
   * @returns Array of App instances
   */
  async list(): Promise<App[]> {
    const result = await this.client.executeTool('retrieve_memory', {
      query: 'applications',
      tags: { type: 'application' },
      limit: 100,
    })

    const apps: App[] = []
    for (const item of result.results || []) {
      try {
        // Extract application data from CMC atom
        const appData = item.metadata?.application || item.metadata?.app_record || item.content
        if (appData && appData.app_id) {
          apps.push(new App(this.client, appData))
        }
      } catch (e) {
        // Skip invalid app records
        console.warn('Skipping invalid app record:', e)
      }
    }

    return apps
  }

  /**
   * Get application by ID
   * 
   * @param appId Application ID
   * @returns App instance or null if not found
   */
  async getById(appId: string): Promise<App | null> {
    const result = await this.client.executeTool('retrieve_memory', {
      query: `application ${appId}`,
      tags: { type: 'application', app_id: appId },
      limit: 1,
    })

    const items = result.results || []
    if (items.length === 0) {
      return null
    }

    try {
      const appData = items[0].metadata?.application || items[0].metadata?.app_record || items[0].content
      if (appData && appData.app_id) {
        return new App(this.client, appData)
      }
    } catch (e) {
      console.warn('Failed to parse app data:', e)
    }

    return null
  }
}

