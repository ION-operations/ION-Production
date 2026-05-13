/**
 * MCP Service
 * Shared service for executing MCP tools via Command Server
 * Used by all agents (Alex, Nova, Sage) for backend integration
 */

import { RetryManager } from './lucid-chat/recovery/RetryManager'
import { CircuitBreaker } from './lucid-chat/recovery/CircuitBreaker'
import {
  IntegrationTagContext,
  buildIntegrationTags
} from '../utils/integrationTags'

const COMMAND_SERVER_URL = 'http://localhost:5001'
const MCP_EXECUTE_ENDPOINT = '/mcp/execute'
const MCP_LIST_ENDPOINT = '/mcp/list'
const HEALTH_ENDPOINT = '/health'

export interface MCPToolRequest {
  tool: string
  arguments?: Record<string, any>
}

export interface MCPToolResponse<T = any> {
  success: boolean
  result?: T
  error?: string
  tool?: string
}

export interface CommandServerHealth {
  status: 'ok' | 'error'
  port?: number
  message?: string
}

export interface MCPExecuteOptions {
  /**
   * Optional pre-built tag list. If omitted, the service will build tags
   * using the provided integrationContext (if any).
   */
  integrationTags?: string[]
  /**
   * Structured context describing the action so standardized tags can be built.
   */
  integrationContext?: IntegrationTagContext
}

/**
 * MCP Service
 * Provides unified interface for MCP tool execution with retry and circuit breaker
 */
export class MCPService {
  private commandServerUrl: string
  private circuitBreaker: CircuitBreaker

  constructor(commandServerUrl: string = COMMAND_SERVER_URL) {
    this.commandServerUrl = commandServerUrl
    this.circuitBreaker = new CircuitBreaker({
      failureThreshold: 5,
      recoveryTimeout: 60000, // 1 minute
      halfOpenMaxAttempts: 3
    })
  }

  /**
   * Check Command Server health
   */
  async checkHealth(): Promise<CommandServerHealth> {
    try {
      const response = await fetch(`${this.commandServerUrl}${HEALTH_ENDPOINT}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        return {
          status: 'error',
          message: `Command Server returned ${response.status} ${response.statusText}`
        }
      }

      const data = await response.json()
      return {
        status: 'ok',
        port: data.port || 5001,
        message: data.message || 'Command Server is healthy'
      }
    } catch (error) {
      return {
        status: 'error',
        message: error instanceof Error ? error.message : 'Unknown error checking Command Server health'
      }
    }
  }

  /**
   * Execute MCP tool with retry and circuit breaker
   */
  async executeTool<T = any>(
    tool: string,
    arguments_: Record<string, any> = {},
    options?: MCPExecuteOptions
  ): Promise<MCPToolResponse<T>> {
    const args: Record<string, any> = { ...arguments_ }
    const resolvedTags =
      options?.integrationTags ||
      (options?.integrationContext ? buildIntegrationTags(options.integrationContext) : undefined)

    if (resolvedTags?.length) {
      const metadata = { ...(args.metadata || {}) }
      metadata.integration_tags = resolvedTags
      args.metadata = metadata
    }

    const request: MCPToolRequest = {
      tool,
      arguments: args
    }

    try {
      const result = await this.circuitBreaker.execute(() =>
        RetryManager.retry(
          async () => {
            // Aether recommendation: 30 second timeout per request
            const controller = new AbortController()
            const timeoutId = setTimeout(() => controller.abort(), 30000)
            
            try {
              const response = await fetch(`${this.commandServerUrl}${MCP_EXECUTE_ENDPOINT}`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify(request),
                signal: controller.signal
              })
              
              clearTimeout(timeoutId)

              if (!response.ok) {
                throw new Error(`Command Server error: ${response.status} ${response.statusText}`)
              }

              const data = await response.json()

              // Check if response indicates failure
              if (data.error || !data.success) {
                throw new Error(data.error || 'MCP tool execution failed')
              }

              return data
            } catch (error) {
              clearTimeout(timeoutId)
              if (error instanceof Error && error.name === 'AbortError') {
                throw new Error('Request timeout after 30 seconds')
              }
              throw error
            }
          },
          {
            maxRetries: 3,
            backoff: 'exponential',
            initialDelay: 500, // Aether recommendation: 500ms
            maxDelay: 5000, // Aether recommendation: 5s max delay
            retryable: (error: Error) => {
              // Retry on network errors, timeouts, 5xx errors
              const message = error.message.toLowerCase()
              return (
                message.includes('network') ||
                message.includes('timeout') ||
                message.includes('econnrefused') ||
                message.includes('500') ||
                message.includes('502') ||
                message.includes('503') ||
                message.includes('504')
              )
            }
          }
        )
      )

      return {
        success: true,
        result: result.result || result,
        tool
      }
    } catch (error) {
      console.error(`MCP tool execution error (${tool}):`, error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        tool
      }
    }
  }

  /**
   * List available MCP tools
   */
  async listTools(): Promise<{ success: boolean; tools?: string[]; error?: string }> {
    try {
      const response = await fetch(`${this.commandServerUrl}${MCP_LIST_ENDPOINT}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`Command Server error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()

      if (data.success && data.tools) {
        return {
          success: true,
          tools: data.tools
        }
      } else {
        return {
          success: false,
          error: data.error || 'Failed to list MCP tools'
        }
      }
    } catch (error) {
      console.error('MCP list tools error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Get circuit breaker state
   */
  getCircuitBreakerState(): 'closed' | 'open' | 'half-open' {
    return this.circuitBreaker.getState()
  }

  /**
   * Reset circuit breaker
   */
  resetCircuitBreaker(): void {
    this.circuitBreaker.reset()
  }
}

// Singleton instance for shared use across all agents
export const mcpService = new MCPService()

