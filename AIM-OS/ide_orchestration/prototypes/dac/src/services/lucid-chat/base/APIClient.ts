/**
 * Base API Client for Lucid Chat
 * Handles HTTP requests with error handling, retries, and caching
 */

export interface APIClientOptions {
  headers?: Record<string, string>
  timeout?: number
  retries?: number
  cache?: boolean
}

export class APIClient {
  private baseURL: string
  private options: Required<APIClientOptions>
  private cache: Map<string, { data: any; timestamp: number }> = new Map()

  constructor(baseURL: string, options: APIClientOptions = {}) {
    this.baseURL = baseURL
    this.options = {
      headers: options.headers || {},
      timeout: options.timeout || 30000,
      retries: options.retries || 3,
      cache: options.cache ?? false,
    }
  }

  async get<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>('GET', endpoint, undefined, options)
  }

  async post<T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    return this.request<T>('POST', endpoint, data, options)
  }

  async put<T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    return this.request<T>('PUT', endpoint, data, options)
  }

  async delete<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>('DELETE', endpoint, undefined, options)
  }

  private async request<T>(
    method: string,
    endpoint: string,
    data?: any,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const cacheKey = `${method}:${url}:${JSON.stringify(data)}`

    // Check cache
    if (this.options.cache) {
      const cached = this.cache.get(cacheKey)
      if (cached && Date.now() - cached.timestamp < 60000) {
        return cached.data as T
      }
    }

    const headers = {
      ...this.options.headers,
      ...options?.headers,
    }

    if (data && !(data instanceof FormData)) {
      headers['Content-Type'] = 'application/json'
    }

    let lastError: Error | null = null

    for (let attempt = 0; attempt <= this.options.retries; attempt++) {
      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), this.options.timeout)

        const response = await fetch(url, {
          method,
          headers,
          body: data ? (data instanceof FormData ? data : JSON.stringify(data)) : undefined,
          signal: controller.signal,
          ...options,
        })

        clearTimeout(timeoutId)

        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`API Error ${response.status}: ${errorText}`)
        }

        const result = await response.json()

        // Cache result
        if (this.options.cache) {
          this.cache.set(cacheKey, {
            data: result,
            timestamp: Date.now(),
          })
        }

        return result as T
      } catch (error: any) {
        lastError = error
        if (attempt < this.options.retries) {
          await this.delay(1000 * (attempt + 1)) // Exponential backoff
        }
      }
    }

    throw lastError || new Error('Request failed')
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms))
  }

  clearCache(): void {
    this.cache.clear()
  }
}

