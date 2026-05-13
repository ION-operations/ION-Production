/**
 * Agent Registry
 * 
 * Manages registration and discovery of AI agents
 * 
 * Epic 2.3: Multi-Agent Orchestration
 */

import { BaseAgent, AgentProfile, AgentTask, AgentCapability } from './BaseAgent'

/**
 * Agent Registry Implementation
 */
export class AgentRegistry {
  private agents: Map<string, BaseAgent> = new Map()
  private capabilities: Map<AgentCapability, string[]> = new Map()

  /**
   * Register an agent
   */
  register(agent: BaseAgent): void {
    const profile = agent.getProfile()
    
    this.agents.set(profile.id, agent)

    // Index by capabilities
    profile.capabilities.forEach(capability => {
      if (!this.capabilities.has(capability)) {
        this.capabilities.set(capability, [])
      }
      this.capabilities.get(capability)!.push(profile.id)
    })
  }

  /**
   * Unregister an agent
   */
  unregister(agentId: string): void {
    const agent = this.agents.get(agentId)
    if (!agent) return

    const profile = agent.getProfile()

    // Remove from capability index
    profile.capabilities.forEach(capability => {
      const agents = this.capabilities.get(capability)
      if (agents) {
        const index = agents.indexOf(agentId)
        if (index > -1) {
          agents.splice(index, 1)
        }
      }
    })

    this.agents.delete(agentId)
  }

  /**
   * Get agent by ID
   */
  getAgent(agentId: string): BaseAgent | undefined {
    return this.agents.get(agentId)
  }

  /**
   * Get all agents
   */
  getAllAgents(): BaseAgent[] {
    return Array.from(this.agents.values())
  }

  /**
   * Get agent profiles
   */
  getAllProfiles(): AgentProfile[] {
    return this.getAllAgents().map(agent => agent.getProfile())
  }

  /**
   * Find agents by capability
   */
  findByCapability(capability: AgentCapability): BaseAgent[] {
    const agentIds = this.capabilities.get(capability) || []
    return agentIds
      .map(id => this.agents.get(id))
      .filter((agent): agent is BaseAgent => agent !== undefined)
  }

  /**
   * Find best agent for task
   */
  findBestAgent(task: AgentTask): BaseAgent | null {
    const availableAgents = this.getAllAgents().filter(agent => agent.canHandle(task))

    if (availableAgents.length === 0) {
      return null
    }

    // Sort by average quality and select best
    return availableAgents.sort((a, b) => {
      const qualityA = a.getProfile().metadata?.averageQuality || 0
      const qualityB = b.getProfile().metadata?.averageQuality || 0
      return qualityB - qualityA
    })[0]
  }

  /**
   * Get registry statistics
   */
  getStats(): {
    totalAgents: number
    capabilities: Record<AgentCapability, number>
    tasksCompleted: number
  } {
    const stats = {
      totalAgents: this.agents.size,
      capabilities: {} as Record<AgentCapability, number>,
      tasksCompleted: 0,
    }

    this.capabilities.forEach((agents, capability) => {
      stats.capabilities[capability] = agents.length
    })

    this.getAllAgents().forEach(agent => {
      stats.tasksCompleted += agent.getProfile().metadata?.tasksCompleted || 0
    })

    return stats
  }
}

// Singleton instance
let registryInstance: AgentRegistry | null = null

export function getAgentRegistry(): AgentRegistry {
  if (!registryInstance) {
    registryInstance = new AgentRegistry()
  }
  return registryInstance
}

