/**
 * User Profile Service
 * 
 * Manages user preferences and personalization
 * 
 * Epic 2.4: Context Management
 */

import { BaseAPIService, APIResponse } from '../base/BaseAPIService'

/**
 * User Preferences
 */
export interface UserPreferences {
  // AI behavior
  preferredThinkingMode?: 'creative' | 'analytical' | 'balanced' | 'reasoning' | 'intuitive'
  preferredProvider?: 'anthropic' | 'openai' | 'gemini' | 'deepseek'
  temperature?: number
  
  // Search preferences
  enableDeepSearch?: boolean
  searchDepth?: 'basic' | 'advanced' | 'comprehensive'
  
  // UI preferences
  theme?: 'light' | 'dark' | 'auto'
  language?: string
  
  // Advanced
  enableAPOE?: boolean
  enableBranchReasoning?: boolean
}

/**
 * User Context
 */
export interface UserContext {
  recentTopics: string[]
  frequentQueries: string[]
  expertise: Record<string, number> // domain -> proficiency level
  interests: string[]
}

/**
 * User Profile
 */
export interface UserProfile {
  id: string
  name?: string
  email?: string
  preferences: UserPreferences
  context: UserContext
  metadata: {
    created: Date
    lastActive: Date
    totalSessions: number
    totalMessages: number
  }
}

/**
 * User Profile Service Implementation
 */
export class UserProfileService extends BaseAPIService {
  private currentProfile: UserProfile | null = null

  constructor(commandServerUrl: string = 'http://localhost:5001') {
    super('user_profile', commandServerUrl, undefined, 'user_profile')
  }

  /**
   * Load or create user profile
   */
  async loadProfile(userId: string): Promise<APIResponse<UserProfile>> {
    return this.handleRequest(
      async () => {
        // Try to retrieve existing profile
        const response = await fetch(`${this.baseURL}/mcp/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tool: 'retrieve_memory',
            arguments: {
              query: `user profile ${userId}`,
              memory_type: 'user_profile',
              limit: 1,
            },
          }),
        })

        const result = await response.json()

        if (result.success && result.data && result.data.results?.length > 0) {
          // Profile exists
          const profile: UserProfile = JSON.parse(result.data.results[0].content)
          this.currentProfile = profile
          return profile
        }

        // Create new profile
        const profile: UserProfile = {
          id: userId,
          preferences: this.getDefaultPreferences(),
          context: {
            recentTopics: [],
            frequentQueries: [],
            expertise: {},
            interests: [],
          },
          metadata: {
            created: new Date(),
            lastActive: new Date(),
            totalSessions: 0,
            totalMessages: 0,
          },
        }

        await this.saveProfile(profile)
        this.currentProfile = profile

        return profile
      },
      'loadProfile',
      { userId }
    )
  }

  /**
   * Get current profile
   */
  getCurrentProfile(): UserProfile | null {
    return this.currentProfile
  }

  /**
   * Update preferences
   */
  async updatePreferences(
    preferences: Partial<UserPreferences>
  ): Promise<APIResponse<UserProfile>> {
    return this.handleRequest(
      async () => {
        if (!this.currentProfile) {
          throw new Error('No active profile')
        }

        this.currentProfile.preferences = {
          ...this.currentProfile.preferences,
          ...preferences,
        }

        await this.saveProfile(this.currentProfile)

        return this.currentProfile
      },
      'updatePreferences',
      preferences
    )
  }

  /**
   * Update user context
   */
  async updateContext(topic: string, query: string): Promise<void> {
    if (!this.currentProfile) return

    // Add to recent topics
    this.currentProfile.context.recentTopics.unshift(topic)
    this.currentProfile.context.recentTopics = this.currentProfile.context.recentTopics.slice(0, 10)

    // Add to frequent queries
    if (!this.currentProfile.context.frequentQueries.includes(query)) {
      this.currentProfile.context.frequentQueries.unshift(query)
      this.currentProfile.context.frequentQueries = this.currentProfile.context.frequentQueries.slice(0, 20)
    }

    // Update activity
    this.currentProfile.metadata.lastActive = new Date()
    this.currentProfile.metadata.totalMessages += 1

    await this.saveProfile(this.currentProfile)
  }

  /**
   * Add expertise
   */
  async addExpertise(domain: string, level: number): Promise<void> {
    if (!this.currentProfile) return

    this.currentProfile.context.expertise[domain] = level
    await this.saveProfile(this.currentProfile)
  }

  /**
   * Add interest
   */
  async addInterest(interest: string): Promise<void> {
    if (!this.currentProfile) return

    if (!this.currentProfile.context.interests.includes(interest)) {
      this.currentProfile.context.interests.push(interest)
      await this.saveProfile(this.currentProfile)
    }
  }

  /**
   * Get personalized recommendations
   */
  async getRecommendations(): Promise<string[]> {
    if (!this.currentProfile) return []

    const recommendations: string[] = []

    // Based on recent topics
    if (this.currentProfile.context.recentTopics.length > 0) {
      recommendations.push(`Explore more about: ${this.currentProfile.context.recentTopics[0]}`)
    }

    // Based on expertise
    const expertiseDomains = Object.keys(this.currentProfile.context.expertise)
    if (expertiseDomains.length > 0) {
      recommendations.push(`Advanced topics in: ${expertiseDomains.join(', ')}`)
    }

    return recommendations
  }

  /**
   * Save profile to CMC
   */
  private async saveProfile(profile: UserProfile): Promise<void> {
    try {
      await fetch(`${this.baseURL}/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: 'store_memory',
          arguments: {
            content: JSON.stringify(profile),
            memory_type: 'user_profile',
            tags: ['user', 'profile', profile.id],
            metadata: {
              user_id: profile.id,
              timestamp: new Date().toISOString(),
            },
          },
        }),
      })
    } catch (error) {
      console.warn('[UserProfile] Failed to save profile:', error)
    }
  }

  /**
   * Get default preferences
   */
  private getDefaultPreferences(): UserPreferences {
    return {
      preferredThinkingMode: 'balanced',
      preferredProvider: 'anthropic',
      temperature: 0.7,
      enableDeepSearch: true,
      searchDepth: 'advanced',
      theme: 'dark',
      language: 'en',
      enableAPOE: true,
      enableBranchReasoning: true,
    }
  }

  isAvailable(): boolean {
    return true
  }
}

// Singleton instance
let userProfileServiceInstance: UserProfileService | null = null

export function getUserProfileService(commandServerUrl?: string): UserProfileService {
  if (!userProfileServiceInstance) {
    userProfileServiceInstance = new UserProfileService(commandServerUrl)
  }
  return userProfileServiceInstance
}

