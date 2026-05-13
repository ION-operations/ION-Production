/**
 * Goal Tree Service
 * Loads GOAL_TREE.yaml from the backend
 */

// Use relative path so Vite proxy can route to backend on port 8000
const API_BASE_URL = ''

export interface GoalTreeObjective {
  id: string
  name: string
  description: string
  owner: string
  priority_tier?: string
  target_date: string
  key_results: Array<{
    id: string
    metric: string
    target: string
    current?: string
    status?: string
  }>
  status?: string
  progress?: number
}

export interface GoalTreeData {
  north_star?: string
  objectives?: GoalTreeObjective[]
  [key: string]: any
}

export interface GoalTreeResponse {
  success: boolean
  data: GoalTreeData
  file_path: string
}

export class GoalTreeService {
  private apiBaseUrl: string
  private cache: GoalTreeResponse | null = null
  private cacheExpiry: number = 0
  private readonly CACHE_TTL = 5 * 60 * 1000 // 5 minutes

  constructor(apiBaseUrl: string = API_BASE_URL) {
    this.apiBaseUrl = apiBaseUrl
  }

  /**
   * Load GOAL_TREE from backend
   */
  async loadGoalTree(): Promise<{ success: boolean; data?: GoalTreeResponse; error?: string }> {
    const cached = this.getCached()
    if (cached) {
      return { success: true, data: cached }
    }

    try {
      const response = await fetch(`${this.apiBaseUrl}/api/goal-tree`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json() as GoalTreeResponse
      
      if (data.success) {
        this.setCached(data)
        return { success: true, data }
      } else {
        return {
          success: false,
          error: 'Invalid response format'
        }
      }
    } catch (error) {
      console.warn('API load failed:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Backend API not available. Please ensure the backend server is running on port 8000'
      }
    }
  }

  /**
   * Get north star goal
   */
  async getNorthStar(): Promise<string | null> {
    const result = await this.loadGoalTree()
    if (result.success && result.data) {
      return result.data.data.north_star || null
    }
    return null
  }

  /**
   * Get all objectives
   */
  async getObjectives(): Promise<GoalTreeObjective[]> {
    const result = await this.loadGoalTree()
    if (result.success && result.data) {
      return result.data.data.objectives || []
    }
    return []
  }

  /**
   * Get objective by ID
   */
  async getObjective(objectiveId: string): Promise<GoalTreeObjective | null> {
    const objectives = await this.getObjectives()
    return objectives.find(obj => obj.id === objectiveId) || null
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache = null
    this.cacheExpiry = 0
  }

  /**
   * Get cached data if still valid
   */
  private getCached(): GoalTreeResponse | null {
    if (this.cache && Date.now() < this.cacheExpiry) {
      return this.cache
    }
    return null
  }

  /**
   * Set cached data with expiry
   */
  private setCached(data: GoalTreeResponse): void {
    this.cache = data
    this.cacheExpiry = Date.now() + this.CACHE_TTL
  }
}

// Export singleton instance
export const goalTreeService = new GoalTreeService()

