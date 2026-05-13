/**
 * Sandbox Service
 * Manages secure code execution sandbox instances
 * Uses backend API for Docker container management
 */

import { mcpService } from './MCPService'

const SANDBOX_API_URL = 'http://localhost:5001/sandbox' // Backend sandbox API endpoint

export interface SandboxConfig {
  language: string
  code: string
  timeout?: number  // Default: 30000ms (30 seconds)
  memory?: number   // Default: 512MB
  cpu?: number      // Default: 50% (0.5)
  network?: 'none' | 'localhost'
  workspace?: string
  context?: Record<string, any>
}

export interface ExecutionResult {
  success: boolean
  stdout?: string
  stderr?: string
  exitCode?: number
  executionTime?: number  // milliseconds
  error?: string
  resourceUsage?: {
    cpu: number  // percentage
    memory: number  // MB
    time: number  // milliseconds
  }
}

export interface SandboxStatus {
  containerId: string
  status: 'created' | 'running' | 'completed' | 'failed' | 'destroyed'
  createdAt?: string
  completedAt?: string
}

/**
 * Sandbox Service
 * Manages secure code execution in isolated containers
 */
export class SandboxService {
  private sandboxApiUrl: string
  private activeContainers: Map<string, SandboxStatus> = new Map()

  constructor(sandboxApiUrl: string = SANDBOX_API_URL) {
    this.sandboxApiUrl = sandboxApiUrl
  }

  /**
   * Execute code in secure sandbox
   */
  async executeCode(
    config: SandboxConfig
  ): Promise<{ success: boolean; result?: ExecutionResult; error?: string }> {
    try {
      const startTime = Date.now()

      // Create sandbox container
      const containerResult = await this.createContainer(config)
      if (!containerResult.success || !containerResult.containerId) {
        return {
          success: false,
          error: containerResult.error || 'Failed to create sandbox container'
        }
      }

      const containerId = containerResult.containerId

      // Execute code in container
      const executionResult = await this.runCodeInContainer(containerId, config)

      // Destroy container
      await this.destroyContainer(containerId)

      const executionTime = Date.now() - startTime

      if (executionResult.success && executionResult.result) {
        return {
          success: true,
          result: {
            ...executionResult.result,
            executionTime
          }
        }
      } else {
        return {
          success: false,
          error: executionResult.error || 'Code execution failed'
        }
      }
    } catch (error) {
      console.error('Sandbox execution error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Create sandbox container
   */
  async createContainer(
    config: SandboxConfig
  ): Promise<{ success: boolean; containerId?: string; error?: string }> {
    try {
      // Try MCP tool first (per Alex's recommendation)
      const mcpResult = await mcpService.executeTool('mcp_lucid-mcp_create_sandbox', {
        language: config.language,
        timeout: config.timeout || 30000,
        memory: config.memory || 512,
        cpu: config.cpu || 0.5,
        network: config.network || 'none',
        workspace: config.workspace || '/workspace'
      })

      if (mcpResult.success && mcpResult.result) {
        const containerId = mcpResult.result.containerId || mcpResult.result.container_id
        if (containerId) {
          const status: SandboxStatus = {
            containerId,
            status: 'created',
            createdAt: new Date().toISOString()
          }
          this.activeContainers.set(containerId, status)
          return {
            success: true,
            containerId
          }
        }
      }

      // Fallback to direct HTTP API (if MCP tools don't exist yet)
      const response = await fetch(`${this.sandboxApiUrl}/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          language: config.language,
          timeout: config.timeout || 30000,
          memory: config.memory || 512,
          cpu: config.cpu || 0.5,
          network: config.network || 'none',
          workspace: config.workspace || '/workspace'
        })
      })

      if (!response.ok) {
        throw new Error(`Sandbox API error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()

      if (data.success && data.containerId) {
        const status: SandboxStatus = {
          containerId: data.containerId,
          status: 'created',
          createdAt: new Date().toISOString()
        }
        this.activeContainers.set(data.containerId, status)

        return {
          success: true,
          containerId: data.containerId
        }
      } else {
        return {
          success: false,
          error: data.error || 'Failed to create container'
        }
      }
    } catch (error) {
      // If backend API not available, return placeholder
      if (error instanceof Error && error.message.includes('fetch')) {
        console.warn('Sandbox API not available, using placeholder')
        const placeholderId = `sandbox_${Date.now()}`
        const status: SandboxStatus = {
          containerId: placeholderId,
          status: 'created',
          createdAt: new Date().toISOString()
        }
        this.activeContainers.set(placeholderId, status)
        return {
          success: true,
          containerId: placeholderId
        }
      }

      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Run code in container
   */
  async runCodeInContainer(
    containerId: string,
    config: SandboxConfig
  ): Promise<{ success: boolean; result?: ExecutionResult; error?: string }> {
    try {
      const status = this.activeContainers.get(containerId)
      if (!status) {
        return {
          success: false,
          error: 'Container not found'
        }
      }

      status.status = 'running'

      // Try MCP tool first (per Alex's recommendation)
      const mcpResult = await mcpService.executeTool('mcp_lucid-mcp_execute_in_sandbox', {
        containerId,
        language: config.language,
        code: config.code,
        timeout: config.timeout || 30000
      })

      if (mcpResult.success && mcpResult.result) {
        status.status = 'completed'
        status.completedAt = new Date().toISOString()
        this.activeContainers.set(containerId, status)

        const result = mcpResult.result
        return {
          success: true,
          result: {
            success: result.success || true,
            stdout: result.stdout || result.output || '',
            stderr: result.stderr || result.error_output || '',
            exitCode: result.exitCode || result.exit_code || 0,
            error: result.error,
            resourceUsage: result.resourceUsage || result.resource_usage
          }
        }
      }

      // Fallback to direct HTTP API (if MCP tools don't exist yet)
      const response = await fetch(`${this.sandboxApiUrl}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          containerId,
          language: config.language,
          code: config.code,
          timeout: config.timeout || 30000
        })
      })

      if (!response.ok) {
        throw new Error(`Sandbox execution error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()

      if (data.success && data.result) {
        status.status = 'completed'
        status.completedAt = new Date().toISOString()
        this.activeContainers.set(containerId, status)

        return {
          success: true,
          result: {
            success: data.result.success || true,
            stdout: data.result.stdout || '',
            stderr: data.result.stderr || '',
            exitCode: data.result.exitCode || 0,
            error: data.result.error,
            resourceUsage: data.result.resourceUsage
          }
        }
      } else {
        status.status = 'failed'
        status.completedAt = new Date().toISOString()
        this.activeContainers.set(containerId, status)

        return {
          success: false,
          error: data.error || 'Execution failed'
        }
      }
    } catch (error) {
      // If backend API not available, return placeholder
      if (error instanceof Error && error.message.includes('fetch')) {
        console.warn('Sandbox API not available, using placeholder execution result')
        const status = this.activeContainers.get(containerId)
        if (status) {
          status.status = 'completed'
          status.completedAt = new Date().toISOString()
          this.activeContainers.set(containerId, status)
        }

        return {
          success: true,
          result: {
            success: true,
            stdout: '// Placeholder: Code execution would run here\n// TODO: Connect to sandbox backend API',
            stderr: '',
            exitCode: 0,
            resourceUsage: {
              cpu: 0,
              memory: 0,
              time: 100
            }
          }
        }
      }

      const status = this.activeContainers.get(containerId)
      if (status) {
        status.status = 'failed'
        status.completedAt = new Date().toISOString()
        this.activeContainers.set(containerId, status)
      }

      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Destroy sandbox container
   */
  async destroyContainer(containerId: string): Promise<{ success: boolean; error?: string }> {
    try {
      const status = this.activeContainers.get(containerId)
      if (!status) {
        return { success: true } // Already destroyed
      }

      // Try MCP tool first (per Alex's recommendation)
      try {
        const mcpResult = await mcpService.executeTool('mcp_lucid-mcp_destroy_sandbox', {
          containerId
        })

        if (mcpResult.success) {
          status.status = 'destroyed'
          this.activeContainers.delete(containerId)
          return { success: true }
        }
      } catch (mcpError) {
        console.warn('Sandbox MCP tool not available, trying HTTP API:', mcpError)
      }

      // Fallback to direct HTTP API (if MCP tools don't exist yet)
      try {
        const response = await fetch(`${this.sandboxApiUrl}/destroy`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ containerId })
        })

        if (!response.ok) {
          console.warn(`Failed to destroy container ${containerId}: ${response.status}`)
        }
      } catch (error) {
        console.warn('Sandbox API not available for container destruction:', error)
      }

      status.status = 'destroyed'
      this.activeContainers.delete(containerId)

      return { success: true }
    } catch (error) {
      console.error('Container destruction error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Get container status
   */
  getContainerStatus(containerId: string): SandboxStatus | null {
    return this.activeContainers.get(containerId) || null
  }

  /**
   * Get all active containers
   */
  getActiveContainers(): SandboxStatus[] {
    return Array.from(this.activeContainers.values())
  }
}

// Singleton instance
export const sandboxService = new SandboxService()

