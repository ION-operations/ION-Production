/**
 * AIMOSClient - Main client class for AIM-OS SDK
 * 
 * Provides access to all AIM-OS services via MCP tools through Command Server.
 */

import { AIMOSClientConfig, CommandServerResponse } from './types'
import { CMCService } from './services/cmc'
import { VIFService } from './services/vif'
import { APOEService } from './services/apoe'
import { SEGService } from './services/seg'
import { AppService } from './services/app'
import { PanelService } from './services/panel'
import { EventService } from './services/event'

/**
 * Main client class for interacting with AIM-OS systems
 */
export class AIMOSClient {
  private commandServerUrl: string
  private appId?: string
  private appToken?: string

  /** CMC (Context Memory Core) service */
  public readonly cmc: CMCService

  /** VIF (Verifiable Intelligence Framework) service */
  public readonly vif: VIFService

  /** APOE (Atomic Provenance Orchestration Engine) service */
  public readonly apoe: APOEService

  /** SEG (Shared Evidence Graph) service */
  public readonly seg: SEGService

  /** App lifecycle management service */
  public readonly apps: AppService

  /** Panel registration service */
  public readonly panels: PanelService

  /** Event publishing/subscription service */
  public readonly events: EventService

  /**
   * Create a new AIMOSClient instance
   * 
   * @param config Client configuration
   */
  constructor(config: AIMOSClientConfig = {}) {
    this.commandServerUrl = config.commandServerUrl || 'http://localhost:5001'
    this.appId = config.appId
    this.appToken = config.appToken

    // Initialize services
    this.cmc = new CMCService(this)
    this.vif = new VIFService(this)
    this.apoe = new APOEService(this)
    this.seg = new SEGService(this)
    this.apps = new AppService(this)
    this.panels = new PanelService(this)
    this.events = new EventService(this)
  }

  /**
   * Execute an MCP tool via Command Server
   * 
   * @param tool Tool name (without mcp_lucid-mcp_ prefix)
   * @param args Tool arguments
   * @returns Tool result
   * @throws Error if tool execution fails
   */
  async executeTool(tool: string, args: any = {}): Promise<any> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (this.appToken) {
      headers['Authorization'] = `Bearer ${this.appToken}`
    }

    const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        tool,
        arguments: args,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data: CommandServerResponse = await response.json()

    if (!data.success) {
      throw new Error(data.error || data.result?.error || 'Tool execution failed')
    }

    // Handle nested result structure
    if (data.result && typeof data.result === 'object') {
      // If result has an error field, throw it
      if ('error' in data.result && data.result.error) {
        throw new Error(data.result.error)
      }
      // If result has success: false, throw error
      if ('success' in data.result && !data.result.success) {
        throw new Error(data.result.error || 'Tool execution failed')
      }
    }

    return data.result || data
  }

  /**
   * Get the Command Server URL
   */
  getCommandServerUrl(): string {
    return this.commandServerUrl
  }

  /**
   * Get the app ID
   */
  getAppId(): string | undefined {
    return this.appId
  }

  /**
   * Set the app token (for authenticated requests)
   */
  setAppToken(token: string): void {
    this.appToken = token
  }
}

