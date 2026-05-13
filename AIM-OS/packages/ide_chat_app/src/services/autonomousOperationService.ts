/**
 * Autonomous Operation Service
 * Manages continuous autonomous agent operation with self-prompting loops
 * 
 * Features:
 * - Start/Stop/Pause/Resume autonomous operation
 * - Self-prompting loop for continuous task generation
 * - Status monitoring and control
 * - Session persistence
 */

import { getMCPAPI } from './mcpApi'
import { getServiceBridge } from './serviceBridge'

export interface AutonomousStatus {
  isActive: boolean
  isPaused: boolean
  currentTask: string | null
  confidence: number
  startTime: string | null
  pauseTime: string | null
  tasksCompleted: number
  tasksFailed: number
  uptime: number
  qualityScore: number
  lastCheckTime: string | null
  shouldContinue: boolean
  reason?: string
}

export interface AutonomousTask {
  task: string
  confidence: number
  priority: string
  goal_id?: string
  task_atom_id?: string
}

export interface AutonomousOperationCallbacks {
  onStatusChange?: (status: AutonomousStatus) => void
  onTaskComplete?: (task: AutonomousTask) => void
  onTaskError?: (task: AutonomousTask, error: any) => void
  onLog?: (level: 'log' | 'warn' | 'error', message: string) => void
}

class AutonomousOperationService {
  private mcpApi = getMCPAPI()
  private serviceBridge = getServiceBridge()
  private isActive: boolean = false
  private isPaused: boolean = false
  private currentTask: AutonomousTask | null = null
  private status: AutonomousStatus
  private loopInterval: NodeJS.Timeout | null = null
  private statusInterval: NodeJS.Timeout | null = null
  private callbacks: AutonomousOperationCallbacks = {}
  private tasksCompleted: number = 0
  private tasksFailed: number = 0
  private startTime: Date | null = null

  constructor() {
    this.status = {
      isActive: false,
      isPaused: false,
      currentTask: null,
      confidence: 0.0,
      startTime: null,
      pauseTime: null,
      tasksCompleted: 0,
      tasksFailed: 0,
      uptime: 0,
      qualityScore: 0.0,
      lastCheckTime: null,
      shouldContinue: false
    }
  }

  /**
   * Set callbacks for status updates
   */
  setCallbacks(callbacks: AutonomousOperationCallbacks): void {
    this.callbacks = callbacks
  }

  /**
   * Start autonomous operation
   */
  async start(task: string, confidence: number = 0.70): Promise<{ success: boolean; error?: string }> {
    try {
      this.callbacks.onLog?.('log', `Starting autonomous operation: ${task}`)

      // Call MCP tool to start autonomous operation
      const result = await this.mcpApi.executeTool('start_autonomous_operation', {
        task,
        confidence
      })

      if (!result.success || !result.result?.success) {
        const error = result.error || result.result?.message || 'Failed to start autonomous operation'
        this.callbacks.onLog?.('error', error)
        return { success: false, error }
      }

      // Initialize state
      this.isActive = true
      this.isPaused = false
      this.startTime = new Date()
      this.tasksCompleted = 0
      this.tasksFailed = 0

      this.status = {
        isActive: true,
        isPaused: false,
        currentTask: task,
        confidence,
        startTime: this.startTime.toISOString(),
        pauseTime: null,
        tasksCompleted: 0,
        tasksFailed: 0,
        uptime: 0,
        qualityScore: 0.0,
        lastCheckTime: new Date().toISOString(),
        shouldContinue: true
      }

      this.currentTask = {
        task,
        confidence,
        priority: 'medium'
      }

      // Start self-prompting loop
      this.startLoop()

      // Start status monitoring
      this.startStatusMonitoring()

      this.callbacks.onStatusChange?.(this.status)
      this.callbacks.onLog?.('log', 'Autonomous operation started successfully')

      return { success: true }
    } catch (error: any) {
      const errorMsg = error.message || 'Failed to start autonomous operation'
      this.callbacks.onLog?.('error', errorMsg)
      return { success: false, error: errorMsg }
    }
  }

  /**
   * Pause autonomous operation
   */
  async pause(): Promise<{ success: boolean; error?: string }> {
    try {
      this.callbacks.onLog?.('log', 'Pausing autonomous operation...')

      const result = await this.mcpApi.executeTool('pause_autonomous_operation', {})

      if (!result.success || !result.result?.success) {
        const error = result.error || result.result?.error || 'Failed to pause autonomous operation'
        this.callbacks.onLog?.('error', error)
        return { success: false, error }
      }

      this.isPaused = true
      this.status.isPaused = true
      this.status.pauseTime = new Date().toISOString()

      this.stopLoop()

      this.callbacks.onStatusChange?.(this.status)
      this.callbacks.onLog?.('log', 'Autonomous operation paused')

      return { success: true }
    } catch (error: any) {
      const errorMsg = error.message || 'Failed to pause autonomous operation'
      this.callbacks.onLog?.('error', errorMsg)
      return { success: false, error: errorMsg }
    }
  }

  /**
   * Resume autonomous operation
   */
  async resume(): Promise<{ success: boolean; error?: string }> {
    try {
      this.callbacks.onLog?.('log', 'Resuming autonomous operation...')

      const result = await this.mcpApi.executeTool('resume_autonomous_operation', {})

      if (!result.success || !result.result?.success) {
        const error = result.error || result.result?.error || 'Failed to resume autonomous operation'
        this.callbacks.onLog?.('error', error)
        return { success: false, error }
      }

      this.isPaused = false
      this.status.isPaused = false
      this.status.pauseTime = null

      this.startLoop()

      this.callbacks.onStatusChange?.(this.status)
      this.callbacks.onLog?.('log', 'Autonomous operation resumed')

      return { success: true }
    } catch (error: any) {
      const errorMsg = error.message || 'Failed to resume autonomous operation'
      this.callbacks.onLog?.('error', errorMsg)
      return { success: false, error: errorMsg }
    }
  }

  /**
   * Stop autonomous operation
   */
  async stop(): Promise<{ success: boolean; error?: string }> {
    try {
      this.callbacks.onLog?.('log', 'Stopping autonomous operation...')

      const result = await this.mcpApi.executeTool('stop_autonomous_operation', {})

      if (!result.success || !result.result?.success) {
        const error = result.error || result.result?.error || 'Failed to stop autonomous operation'
        this.callbacks.onLog?.('error', error)
      }

      this.isActive = false
      this.isPaused = false
      this.status.isActive = false
      this.status.isPaused = false
      this.status.currentTask = null
      this.currentTask = null

      this.stopLoop()
      this.stopStatusMonitoring()

      this.callbacks.onStatusChange?.(this.status)
      this.callbacks.onLog?.('log', 'Autonomous operation stopped')

      return { success: true }
    } catch (error: any) {
      const errorMsg = error.message || 'Failed to stop autonomous operation'
      this.callbacks.onLog?.('error', errorMsg)
      return { success: false, error: errorMsg }
    }
  }

  /**
   * Get current status
   */
  async getStatus(): Promise<AutonomousStatus> {
    try {
      const result = await this.mcpApi.executeTool('get_autonomous_status', {})

      if (result.success && result.result?.success) {
        const statusData = result.result
        this.status = {
          ...this.status,
          isActive: statusData.is_active || false,
          isPaused: statusData.is_paused || false,
          currentTask: statusData.current_task || null,
          confidence: statusData.confidence_level || 0.0,
          startTime: statusData.start_time || null,
          pauseTime: statusData.pause_time || null,
          tasksCompleted: this.tasksCompleted,
          tasksFailed: this.tasksFailed,
          uptime: this.startTime ? Math.floor((Date.now() - this.startTime.getTime()) / 1000) : 0,
          qualityScore: statusData.quality_score || 0.0,
          lastCheckTime: new Date().toISOString(),
          shouldContinue: statusData.should_continue || false,
          reason: statusData.reason
        }
      }

      return this.status
    } catch (error: any) {
      this.callbacks.onLog?.('error', `Failed to get status: ${error.message}`)
      return this.status
    }
  }

  /**
   * Start self-prompting loop
   */
  private startLoop(): void {
    if (this.loopInterval) {
      clearInterval(this.loopInterval)
    }

    this.loopInterval = setInterval(async () => {
      if (!this.isActive || this.isPaused) {
        return
      }

      try {
        await this.runLoopIteration()
      } catch (error: any) {
        this.callbacks.onLog?.('error', `Loop iteration error: ${error.message}`)
      }
    }, 5000) // Run every 5 seconds
  }

  /**
   * Stop self-prompting loop
   */
  private stopLoop(): void {
    if (this.loopInterval) {
      clearInterval(this.loopInterval)
      this.loopInterval = null
    }
  }

  /**
   * Start status monitoring
   */
  private startStatusMonitoring(): void {
    if (this.statusInterval) {
      clearInterval(this.statusInterval)
    }

    this.statusInterval = setInterval(async () => {
      if (!this.isActive) {
        return
      }

      try {
        const status = await this.getStatus()
        this.callbacks.onStatusChange?.(status)
      } catch (error: any) {
        this.callbacks.onLog?.('error', `Status monitoring error: ${error.message}`)
      }
    }, 10000) // Update status every 10 seconds
  }

  /**
   * Stop status monitoring
   */
  private stopStatusMonitoring(): void {
    if (this.statusInterval) {
      clearInterval(this.statusInterval)
      this.statusInterval = null
    }
  }

  /**
   * Run one iteration of the self-prompting loop
   */
  private async runLoopIteration(): Promise<void> {
    // 1. Check if should continue
    const shouldContinueResult = await this.mcpApi.executeTool('should_continue_autonomous', {})
    
    if (!shouldContinueResult.success || !shouldContinueResult.result?.should_continue) {
      const reason = shouldContinueResult.result?.reason || 'Checklist failed'
      this.callbacks.onLog?.('warn', `Should not continue: ${reason}`)
      
      if (this.isActive && !this.isPaused) {
        await this.pause()
      }
      return
    }

    // 2. Generate next task
    const taskResult = await this.mcpApi.executeTool('generate_next_autonomous_task', {})
    
    if (!taskResult.success || !taskResult.result?.success) {
      this.callbacks.onLog?.('warn', 'Failed to generate next task, retrying...')
      return
    }

    const nextTask: AutonomousTask = {
      task: taskResult.result.next_task || 'Continue current work',
      confidence: taskResult.result.confidence || 0.70,
      priority: taskResult.result.priority || 'medium',
      goal_id: taskResult.result.goal_id,
      task_atom_id: taskResult.result.task_atom_id
    }

    // 3. Validate confidence
    if (nextTask.confidence < 0.70) {
      this.callbacks.onLog?.('warn', `Task confidence too low (${nextTask.confidence}), skipping...`)
      return
    }

    // 4. Update current task
    this.currentTask = nextTask
    this.status.currentTask = nextTask.task
    this.status.confidence = nextTask.confidence

    // 5. Execute task (simplified - actual execution would be more complex)
    try {
      this.callbacks.onLog?.('log', `Executing task: ${nextTask.task}`)
      
      // Track confidence
      await this.serviceBridge.trackConfidence(
        nextTask.task,
        nextTask.confidence,
        `Autonomous operation task: ${nextTask.task}`
      )

      // Store completion in memory
      await this.serviceBridge.storeMemory(
        `Completed autonomous task: ${nextTask.task}`,
        ['autonomous_task', 'task_completion']
      )

      this.tasksCompleted++
      this.status.tasksCompleted = this.tasksCompleted

      this.callbacks.onTaskComplete?.(nextTask)
      this.callbacks.onLog?.('log', `Task completed: ${nextTask.task}`)
    } catch (error: any) {
      this.tasksFailed++
      this.status.tasksFailed = this.tasksFailed
      this.callbacks.onTaskError?.(nextTask, error)
      this.callbacks.onLog?.('error', `Task failed: ${nextTask.task} - ${error.message}`)

      // Try to fix issues
      try {
        await this.mcpApi.executeTool('fix_autonomous_issues', {})
      } catch (fixError) {
        this.callbacks.onLog?.('error', `Failed to fix issues: ${fixError}`)
      }
    }

    // 6. Update status
    this.status.lastCheckTime = new Date().toISOString()
    this.status.uptime = this.startTime ? Math.floor((Date.now() - this.startTime.getTime()) / 1000) : 0
    this.callbacks.onStatusChange?.(this.status)
  }

  /**
   * Get current status synchronously
   */
  getCurrentStatus(): AutonomousStatus {
    return { ...this.status }
  }
}

// Singleton instance
let autonomousOperationServiceInstance: AutonomousOperationService | null = null

export function getAutonomousOperationService(): AutonomousOperationService {
  if (!autonomousOperationServiceInstance) {
    autonomousOperationServiceInstance = new AutonomousOperationService()
  }
  return autonomousOperationServiceInstance
}

export default AutonomousOperationService

