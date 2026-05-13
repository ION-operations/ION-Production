/**
 * Common types for Lucid Chat API services
 */

export interface APIError {
  code: string
  message: string
  details?: any
}

export interface APIRequestOptions {
  timeout?: number
  retries?: number
  cache?: boolean
}

export interface PaginatedResponse<T> {
  data: T[]
  page: number
  pageSize: number
  total: number
  hasMore: boolean
}

export interface RateLimitInfo {
  limit: number
  remaining: number
  resetAt: Date
}

