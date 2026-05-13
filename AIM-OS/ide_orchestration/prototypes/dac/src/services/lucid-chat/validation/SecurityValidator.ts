/**
 * Security Validator
 * 
 * Security-focused validation utilities
 */

export class SecurityValidator {
  /**
   * Sanitize string to prevent XSS
   */
  static sanitizeString(value: string): string {
    if (typeof value !== 'string') {
      return ''
    }

    // Remove potentially dangerous characters
    return value
      .replace(/[<>]/g, '') // Remove < and >
      .replace(/javascript:/gi, '') // Remove javascript: protocol
      .replace(/on\w+=/gi, '') // Remove event handlers
      .trim()
  }

  /**
   * Validate search query (prevent injection)
   */
  static validateQuery(value: string): string {
    if (typeof value !== 'string') {
      throw new Error('Query must be a string')
    }

    // Remove potentially dangerous patterns
    const sanitized = value
      .replace(/[;'"]/g, '') // Remove SQL-like characters
      .replace(/<script/gi, '') // Remove script tags
      .trim()

    if (sanitized.length === 0) {
      throw new Error('Query cannot be empty after sanitization')
    }

    if (sanitized.length > 1000) {
      throw new Error('Query too long (max 1000 characters)')
    }

    return sanitized
  }

  /**
   * Validate URL
   */
  static validateURL(value: string): string {
    if (typeof value !== 'string') {
      throw new Error('URL must be a string')
    }

    try {
      const url = new URL(value)
      
      // Only allow http/https
      if (!['http:', 'https:'].includes(url.protocol)) {
        throw new Error('URL must use http or https protocol')
      }

      return url.toString()
    } catch (error) {
      throw new Error(`Invalid URL: ${error instanceof Error ? error.message : String(error)}`)
    }
  }

  /**
   * Detect potential XSS
   */
  static detectXSS(value: string): boolean {
    if (typeof value !== 'string') {
      return false
    }

    const xssPatterns = [
      /<script/i,
      /javascript:/i,
      /on\w+\s*=/i,
      /<iframe/i,
      /<object/i,
      /<embed/i,
    ]

    return xssPatterns.some(pattern => pattern.test(value))
  }

  /**
   * Detect potential injection
   */
  static detectInjection(value: string): boolean {
    if (typeof value !== 'string') {
      return false
    }

    const injectionPatterns = [
      /['";]/g, // SQL injection
      /<script/i, // XSS
      /javascript:/i, // JavaScript injection
      /eval\(/i, // Code execution
      /exec\(/i, // Code execution
    ]

    return injectionPatterns.some(pattern => pattern.test(value))
  }

  /**
   * Validate model name (prevent injection)
   */
  static validateModelName(value: string): string {
    if (typeof value !== 'string') {
      throw new Error('Model name must be a string')
    }

    // Only allow alphanumeric, dash, underscore, dot
    if (!/^[a-zA-Z0-9._-]+$/.test(value)) {
      throw new Error('Model name contains invalid characters')
    }

    if (value.length > 100) {
      throw new Error('Model name too long (max 100 characters)')
    }

    return value
  }

  /**
   * Validate API key format
   */
  static validateAPIKey(value: string): string {
    if (typeof value !== 'string') {
      throw new Error('API key must be a string')
    }

    if (value.length < 10) {
      throw new Error('API key too short (min 10 characters)')
    }

    if (value.length > 500) {
      throw new Error('API key too long (max 500 characters)')
    }

    // Basic format check (alphanumeric + some special chars)
    if (!/^[a-zA-Z0-9._-]+$/.test(value)) {
      throw new Error('API key contains invalid characters')
    }

    return value
  }
}

