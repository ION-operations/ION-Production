/**
 * Authentication
 * 
 * API key authentication and request signing
 */

import { SecurityValidator } from '../validation/SecurityValidator'

export interface AuthConfig {
  apiKey?: string
  requireAuth?: boolean
  validateSignature?: boolean
}

export interface AuthResult {
  authenticated: boolean
  apiKey?: string
  error?: string
}

export class Authentication {
  /**
   * Authenticate request with API key
   */
  static authenticate(
    apiKey: string | undefined,
    config: AuthConfig = {}
  ): AuthResult {
    const { requireAuth = false } = config

    // If auth not required, allow
    if (!requireAuth) {
      return { authenticated: true }
    }

    // Validate API key format
    if (!apiKey) {
      return {
        authenticated: false,
        error: 'API key required',
      }
    }

    try {
      // Validate API key format
      SecurityValidator.validateAPIKey(apiKey)

      // Check if API key matches configured key
      const configuredKey = config.apiKey || process.env.API_KEY
      if (!configuredKey) {
        return {
          authenticated: false,
          error: 'API key not configured',
        }
      }

      if (apiKey !== configuredKey) {
        return {
          authenticated: false,
          error: 'Invalid API key',
        }
      }

      return {
        authenticated: true,
        apiKey,
      }
    } catch (error) {
      return {
        authenticated: false,
        error: error instanceof Error ? error.message : 'Invalid API key format',
      }
    }
  }

  /**
   * Validate API key from request
   */
  static validateAPIKeyFromRequest(
    request: Request | { headers?: Headers | Record<string, string> },
    config: AuthConfig = {}
  ): AuthResult {
    // Extract API key from headers
    let apiKey: string | undefined

    if (request instanceof Request) {
      apiKey = request.headers.get('X-API-Key') || request.headers.get('Authorization')?.replace('Bearer ', '')
    } else if (request.headers) {
      if (request.headers instanceof Headers) {
        apiKey = request.headers.get('X-API-Key') || request.headers.get('Authorization')?.replace('Bearer ', '')
      } else {
        apiKey = request.headers['X-API-Key'] || request.headers['Authorization']?.replace('Bearer ', '')
      }
    }

    return this.authenticate(apiKey, config)
  }

  /**
   * Extract API key from environment
   */
  static getAPIKeyFromEnv(provider: string): string | undefined {
    // Try provider-specific env var first
    const providerKey = process.env[`${provider.toUpperCase()}_API_KEY`]
    if (providerKey) {
      return providerKey
    }

    // Try generic API key
    return process.env.API_KEY
  }

  /**
   * Mask API key for logging
   */
  static maskAPIKey(apiKey: string): string {
    if (apiKey.length <= 8) {
      return '***'
    }

    // Show first 4 and last 4 characters
    const start = apiKey.substring(0, 4)
    const end = apiKey.substring(apiKey.length - 4)
    const masked = '*'.repeat(Math.max(0, apiKey.length - 8))

    return `${start}${masked}${end}`
  }
}

