/**
 * Enhanced Message Monitor Service with Agent Coordination
 * 
 * Features:
 * - Monitors CMC for new AI collaboration messages
 * - Triggers agent activation when "proceed" detected
 * - Coordinates with autonomous operation system
 * - Handles agent-to-agent waiting (wait for reply before continuing)
 * - Confidence-based automation (stop when confidence low)
 * - Multi-agent coordination
 */

import { getMCPAPI } from './mcpApi'
import { getAutonomousOperationService, AutonomousStatus } from './autonomousOperationService'

// Re-export AutonomousStatus for convenience
export type { AutonomousStatus }

export interface AIMessage {
  message_id: string
  from_ai: string
  to_ai: string
  content: string
  message_type: string
  priority: string
  thread_id?: string
  timestamp: string
  response_required: boolean
}

export interface MessageMonitorCallbacks {
  onMessageDetected?: (message: AIMessage) => void
  onAgentTriggered?: (agentId: string, messageId: string) => void
  onAgentWaiting?: (agentId: string, waitingFor: string) => void
  onAgentContinued?: (agentId: string) => void
  onAgentStopped?: (agentId: string, reason: string) => void
  onError?: (error: Error) => void
}

interface AgentState {
  agentId: string
  isActive: boolean
  isWaiting: boolean
  waitingFor?: string // Agent ID we're waiting for
  lastMessageId?: string
  confidence: number
  status?: AutonomousStatus
}

class MessageMonitorService {
  private mcpApi = getMCPAPI()
  private autonomousService = getAutonomousOperationService()
  private pollingInterval: NodeJS.Timeout | null = null
  private isMonitoring = false
  private lastCheckTime: Date | null = null
  private processedMessageIds = new Set<string>()
  private callbacks: MessageMonitorCallbacks = {}
  private agentStates = new Map<string, AgentState>()
  private confidenceThreshold = 0.70 // Stop automation if confidence drops below this

  /**
   * Start monitoring for new messages
   */
  startMonitoring(callbacks: MessageMonitorCallbacks = {}): void {
    if (this.isMonitoring) {
      console.warn('[MessageMonitor] Already monitoring')
      return
    }

    this.callbacks = callbacks
    this.isMonitoring = true
    this.lastCheckTime = new Date()

    console.log('[MessageMonitor] Starting message monitoring with agent coordination...')

    // Poll every 3 seconds
    this.pollingInterval = setInterval(() => {
      this.checkForNewMessages()
      this.checkAgentStates()
    }, 3000)

    // Initial check
    this.checkForNewMessages()
    this.checkAgentStates()
  }

  /**
   * Stop monitoring
   */
  stopMonitoring(): void {
    if (!this.isMonitoring) {
      return
    }

    this.isMonitoring = false

    if (this.pollingInterval) {
      clearInterval(this.pollingInterval)
      this.pollingInterval = null
    }

    // Stop all active agents
    for (const [agentId, state] of this.agentStates.entries()) {
      if (state.isActive) {
        this.stopAgent(agentId, 'Monitoring stopped')
      }
    }

    console.log('[MessageMonitor] Stopped monitoring')
  }

  /**
   * Check for new messages and trigger agents if needed
   */
  private async checkForNewMessages(): Promise<void> {
    try {
      // Get messages via MCP API
      const messages: AIMessage[] = await this.mcpApi.getAIMessages(undefined, undefined, undefined, 100)

      // Filter for new messages since last check
      const newMessages = messages.filter(msg => {
        // Skip if already processed
        if (this.processedMessageIds.has(msg.message_id)) {
          return false
        }

        // Skip if message is older than last check
        if (this.lastCheckTime) {
          const msgTime = new Date(msg.timestamp)
          if (msgTime <= this.lastCheckTime) {
            return false
          }
        }

        return true
      })

      // Process new messages
      for (const message of newMessages) {
        this.processedMessageIds.add(message.message_id)

        // Check if this is a "proceed" message
        if (this.isProceedMessage(message)) {
          console.log(`[MessageMonitor] Detected proceed message: ${message.message_id}`)
          
          this.callbacks.onMessageDetected?.(message)
          
          // Trigger agent activation
          await this.triggerAgent(message)
        }

        // Check if agent is waiting for a reply
        await this.checkWaitingAgents(message)
      }

      // Update last check time
      if (newMessages.length > 0) {
        this.lastCheckTime = new Date()
      }

    } catch (error: any) {
      console.error('[MessageMonitor] Error checking messages:', error)
      this.callbacks.onError?.(error)
    }
  }

  /**
   * Check agent states and manage automation
   */
  private async checkAgentStates(): Promise<void> {
    for (const [agentId, state] of this.agentStates.entries()) {
      if (!state.isActive) {
        continue
      }

      try {
        // Get current autonomous status via MCP tool
        const statusResult = await this.mcpApi.executeTool('get_autonomous_status', {})
        
        if (statusResult.success && statusResult.result) {
          const status = statusResult.result as any
          state.status = {
            isActive: status.is_active || false,
            isPaused: status.is_paused || false,
            currentTask: status.current_task || null,
            confidence: status.confidence || 0.75,
            startTime: status.start_time || null,
            pauseTime: status.pause_time || null,
            tasksCompleted: status.tasks_completed || 0,
            tasksFailed: status.tasks_failed || 0,
            uptime: status.uptime || 0,
            qualityScore: status.quality_score || 0.0,
            lastCheckTime: status.last_check_time || null,
            shouldContinue: status.should_continue || false,
            reason: status.reason
          }
          state.confidence = status.confidence || 0.75

          // Check if confidence dropped below threshold
          if (state.confidence < this.confidenceThreshold) {
            console.log(`[MessageMonitor] Agent ${agentId} confidence low (${state.confidence}), stopping automation`)
            await this.stopAgent(agentId, `Confidence dropped below threshold (${state.confidence} < ${this.confidenceThreshold})`)
            continue
          }

          // Check if should continue
          const shouldContinueResult = await this.mcpApi.executeTool('should_continue_autonomous', {})
          
          if (!shouldContinueResult.success || !shouldContinueResult.result?.should_continue) {
            const reason = shouldContinueResult.result?.reason || 'Checklist failed'
            console.log(`[MessageMonitor] Agent ${agentId} should not continue: ${reason}`)
            await this.pauseAgent(agentId, reason)
            continue
          }

          // If agent is waiting, check if reply received (handled in checkWaitingAgents)
          if (state.isWaiting && state.waitingFor) {
            // Don't generate next task while waiting
            continue
          }

          // Generate next task if not waiting and not paused
          if (!state.isWaiting && !state.status?.isPaused) {
            await this.generateNextTask(agentId)
          }

        } else {
          // Agent status unavailable - might have stopped
          console.warn(`[MessageMonitor] Could not get status for agent ${agentId}`)
        }

      } catch (error: any) {
        console.error(`[MessageMonitor] Error checking agent ${agentId} state:`, error)
      }
    }
  }

  /**
   * Check if waiting agents received replies
   */
  private async checkWaitingAgents(message: AIMessage): Promise<void> {
    // Check if any agent is waiting for this sender
    for (const [agentId, state] of this.agentStates.entries()) {
      if (state.isWaiting && state.waitingFor === message.from_ai) {
        console.log(`[MessageMonitor] Agent ${agentId} received reply from ${message.from_ai}, continuing...`)
        
        state.isWaiting = false
        state.waitingFor = undefined
        
        this.callbacks.onAgentContinued?.(agentId)
        
        // Resume agent work
        await this.generateNextTask(agentId)
      }
    }
  }

  /**
   * Check if message is a "proceed" command
   */
  private isProceedMessage(message: AIMessage): boolean {
    const content = message.content.toLowerCase().trim()
    
    // Check for explicit "proceed" command
    if (content === 'proceed' || content.startsWith('proceed')) {
      return true
    }

    // Check for task handoff type
    if (message.message_type === 'task_handoff') {
      return true
    }

    // Check for high priority urgent messages
    if (message.priority === 'urgent' && message.response_required) {
      return true
    }

    return false
  }

  /**
   * Trigger agent activation for a message
   */
  private async triggerAgent(message: AIMessage): Promise<void> {
    const agentId = message.to_ai

    if (!agentId || agentId === 'unknown' || agentId === 'electron-app') {
      console.warn(`[MessageMonitor] Invalid agent ID: ${agentId}`)
      return
    }

    try {
      console.log(`[MessageMonitor] Triggering agent activation: ${agentId}`)

      // Initialize agent state
      const agentState: AgentState = {
        agentId,
        isActive: true,
        isWaiting: false,
        confidence: 0.75,
        lastMessageId: message.message_id
      }
      this.agentStates.set(agentId, agentState)

      // Call start_autonomous_operation MCP tool
      const result = await this.mcpApi.executeTool('start_autonomous_operation', {
        task: message.content,
        confidence: 0.75,
        context: {
          message_id: message.message_id,
          from_ai: message.from_ai,
          thread_id: message.thread_id,
          priority: message.priority
        }
      })

      if (result.success) {
        console.log(`[MessageMonitor] Agent ${agentId} activated successfully`)
        this.callbacks.onAgentTriggered?.(agentId, message.message_id)
      } else {
        console.error(`[MessageMonitor] Failed to activate agent ${agentId}:`, result.error)
        this.agentStates.delete(agentId)
      }

    } catch (error: any) {
      console.error(`[MessageMonitor] Error triggering agent ${agentId}:`, error)
      this.callbacks.onError?.(error)
    }
  }

  /**
   * Generate next task for agent
   */
  private async generateNextTask(agentId: string): Promise<void> {
    const state = this.agentStates.get(agentId)
    if (!state || !state.isActive || state.isWaiting) {
      return
    }

    try {
      const result = await this.mcpApi.executeTool('generate_next_autonomous_task', {})
      
      if (result.success && result.result?.success) {
        const task = result.result.next_task || 'Continue current work'
        const confidence = result.result.confidence || 0.70
        
        state.confidence = confidence

        // Check if task requires waiting for another agent
        if (this.taskRequiresReply(task)) {
          const waitingFor = this.extractWaitingFor(task)
          if (waitingFor) {
            state.isWaiting = true
            state.waitingFor = waitingFor
            console.log(`[MessageMonitor] Agent ${agentId} waiting for reply from ${waitingFor}`)
            this.callbacks.onAgentWaiting?.(agentId, waitingFor)
            return
          }
        }

        console.log(`[MessageMonitor] Agent ${agentId} generated next task: ${task} (confidence: ${confidence})`)

      } else {
        console.warn(`[MessageMonitor] Failed to generate next task for ${agentId}`)
      }

    } catch (error: any) {
      console.error(`[MessageMonitor] Error generating next task for ${agentId}:`, error)
    }
  }

  /**
   * Check if task requires waiting for a reply
   */
  private taskRequiresReply(task: string): boolean {
    const lowerTask = task.toLowerCase()
    return lowerTask.includes('wait') || 
           lowerTask.includes('reply') || 
           lowerTask.includes('response') ||
           lowerTask.includes('await')
  }

  /**
   * Extract agent ID from "waiting for" task
   */
  private extractWaitingFor(task: string): string | undefined {
    // Look for patterns like "wait for Aether" or "awaiting reply from Sev"
    const match = task.match(/(?:wait(?:ing)?|await(?:ing)?)\s+(?:for|reply from)\s+([A-Z][a-zA-Z]+)/i)
    return match ? match[1] : undefined
  }

  /**
   * Pause agent (waiting for reply)
   */
  private async pauseAgent(agentId: string, reason: string): Promise<void> {
    const state = this.agentStates.get(agentId)
    if (!state) return

    try {
      await this.mcpApi.executeTool('pause_autonomous_operation', {})
      console.log(`[MessageMonitor] Paused agent ${agentId}: ${reason}`)
    } catch (error: any) {
      console.error(`[MessageMonitor] Error pausing agent ${agentId}:`, error)
    }
  }

  /**
   * Stop agent (confidence low or error)
   */
  private async stopAgent(agentId: string, reason: string): Promise<void> {
    const state = this.agentStates.get(agentId)
    if (!state) return

    try {
      await this.mcpApi.executeTool('stop_autonomous_operation', {})
      state.isActive = false
      this.agentStates.delete(agentId)
      console.log(`[MessageMonitor] Stopped agent ${agentId}: ${reason}`)
      this.callbacks.onAgentStopped?.(agentId, reason)
    } catch (error: any) {
      console.error(`[MessageMonitor] Error stopping agent ${agentId}:`, error)
    }
  }

  /**
   * Set confidence threshold for automation
   */
  setConfidenceThreshold(threshold: number): void {
    this.confidenceThreshold = threshold
    console.log(`[MessageMonitor] Confidence threshold set to ${threshold}`)
  }

  /**
   * Get monitoring status
   */
  getStatus(): { 
    isMonitoring: boolean
    lastCheckTime: Date | null
    processedCount: number
    activeAgents: number
    waitingAgents: number
    agentStates: Map<string, AgentState>
  } {
    const activeAgents = Array.from(this.agentStates.values()).filter(s => s.isActive).length
    const waitingAgents = Array.from(this.agentStates.values()).filter(s => s.isWaiting).length

    return {
      isMonitoring: this.isMonitoring,
      lastCheckTime: this.lastCheckTime,
      processedCount: this.processedMessageIds.size,
      activeAgents,
      waitingAgents,
      agentStates: new Map(this.agentStates)
    }
  }
}

// Singleton instance
let messageMonitorInstance: MessageMonitorService | null = null

export function getMessageMonitor(): MessageMonitorService {
  if (!messageMonitorInstance) {
    messageMonitorInstance = new MessageMonitorService()
  }
  return messageMonitorInstance
}
