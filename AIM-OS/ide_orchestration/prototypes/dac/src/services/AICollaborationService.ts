/**
 * AI Collaboration Service
 * Handles AI-to-AI communication and task delegation via MCP tools
 */

const COMMAND_SERVER_URL = 'http://localhost:5001'

export interface AIMessage {
  message_id: string
  from_ai: string
  to_ai: string
  content: string
  message_type: 'discussion' | 'task_handoff' | 'problem_solving' | 'profile_sharing' | 'status_update' | 'urgent'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  thread_id?: string
  response_required: boolean
  timestamp: string
  read: boolean
}

export interface TaskHandoffResult {
  success: boolean
  thread_id: string
  message_id?: string
  error?: string
}

export interface DelegationStatus {
  thread_id: string
  from_ai: string
  to_ai: string
  task_description: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  progress?: number
  result?: string
  error?: string
  last_update: string
}

/**
 * AI Collaboration Service
 * Integrates with MCP tools for AI-to-AI communication
 */
export class AICollaborationService {
  private commandServerUrl: string

  constructor(commandServerUrl: string = COMMAND_SERVER_URL) {
    this.commandServerUrl = commandServerUrl
  }

  /**
   * Send a message to another AI
   */
  async sendAIMessage(
    fromAI: string,
    toAI: string,
    content: string,
    options: {
      messageType?: AIMessage['message_type']
      priority?: AIMessage['priority']
      threadId?: string
      responseRequired?: boolean
    } = {}
  ): Promise<{ success: boolean; message_id?: string; error?: string }> {
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool: 'mcp_lucid-mcp_send_ai_message',
          arguments: {
            from_ai: fromAI,
            to_ai: toAI,
            content,
            message_type: options.messageType || 'discussion',
            priority: options.priority || 'medium',
            thread_id: options.threadId,
            response_required: options.responseRequired || false
          }
        })
      })

      if (!response.ok) {
        throw new Error(`Command Server error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      return {
        success: data.success || false,
        message_id: data.message_id,
        error: data.error
      }
    } catch (error) {
      console.error('AI Collaboration Service error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Hand off a task to another AI
   */
  async handoffTaskToAI(
    fromAI: string,
    toAI: string,
    taskDescription: string,
    taskData: Record<string, any> = {},
    priority: 'low' | 'medium' | 'high' | 'urgent' = 'high'
  ): Promise<TaskHandoffResult> {
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool: 'mcp_lucid-mcp_handoff_task_to_ai',
          arguments: {
            from_ai: fromAI,
            to_ai: toAI,
            task_description: taskDescription,
            task_data: taskData,
            priority
          }
        })
      })

      if (!response.ok) {
        throw new Error(`Command Server error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      return {
        success: data.success || false,
        thread_id: data.thread_id || '',
        message_id: data.message_id,
        error: data.error
      }
    } catch (error) {
      console.error('Task handoff error:', error)
      return {
        success: false,
        thread_id: '',
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Get AI messages (for monitoring delegation progress)
   */
  async getAIMessages(options: {
    fromAI?: string
    toAI?: string
    threadId?: string
    messageType?: AIMessage['message_type']
    limit?: number
  } = {}): Promise<AIMessage[]> {
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool: 'mcp_lucid-mcp_get_ai_messages',
          arguments: {
            from_ai: options.fromAI,
            to_ai: options.toAI,
            thread_id: options.threadId,
            message_type: options.messageType,
            limit: options.limit || 50
          }
        })
      })

      if (!response.ok) {
        throw new Error(`Command Server error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      return data.messages || []
    } catch (error) {
      console.error('Get AI messages error:', error)
      return []
    }
  }

  /**
   * Monitor delegation progress
   */
  async monitorDelegation(threadId: string, fromAI: string, toAI: string): Promise<DelegationStatus> {
    try {
      // Get messages for this thread
      const messages = await this.getAIMessages({
        threadId,
        fromAI: toAI, // Get responses FROM the delegated AI
        toAI: fromAI, // TO the manager AI
        messageType: 'task_handoff'
      })

      // Determine status based on messages
      let status: DelegationStatus['status'] = 'pending'
      let result: string | undefined
      let error: string | undefined
      let progress: number | undefined

      if (messages.length === 0) {
        status = 'pending'
      } else {
        const latestMessage = messages[messages.length - 1]
        
        // Check for completion indicators
        if (latestMessage.content.toLowerCase().includes('completed') || 
            latestMessage.content.toLowerCase().includes('done') ||
            latestMessage.content.toLowerCase().includes('finished')) {
          status = 'completed'
          result = latestMessage.content
        } else if (latestMessage.content.toLowerCase().includes('error') ||
                   latestMessage.content.toLowerCase().includes('failed')) {
          status = 'failed'
          error = latestMessage.content
        } else {
          status = 'in_progress'
          
          // Try to extract progress percentage
          const progressMatch = latestMessage.content.match(/(\d+)%/)
          if (progressMatch) {
            progress = parseInt(progressMatch[1])
          }
        }
      }

      return {
        thread_id: threadId,
        from_ai: fromAI,
        to_ai: toAI,
        task_description: messages[0]?.content || '',
        status,
        progress,
        result,
        error,
        last_update: messages[messages.length - 1]?.timestamp || new Date().toISOString()
      }
    } catch (error) {
      console.error('Monitor delegation error:', error)
      return {
        thread_id: threadId,
        from_ai: fromAI,
        to_ai: toAI,
        task_description: '',
        status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown error',
        last_update: new Date().toISOString()
      }
    }
  }

  /**
   * Get AI collaboration summary
   */
  async getCollaborationSummary(): Promise<{
    total_messages: number
    active_threads: number
    pending_tasks: number
    completed_tasks: number
  }> {
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool: 'mcp_lucid-mcp_get_ai_collaboration_summary',
          arguments: {}
        })
      })

      if (!response.ok) {
        throw new Error(`Command Server error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      return {
        total_messages: data.total_messages || 0,
        active_threads: data.active_threads || 0,
        pending_tasks: data.pending_tasks || 0,
        completed_tasks: data.completed_tasks || 0
      }
    } catch (error) {
      console.error('Get collaboration summary error:', error)
      return {
        total_messages: 0,
        active_threads: 0,
        pending_tasks: 0,
        completed_tasks: 0
      }
    }
  }
}

// Singleton instance
export const aiCollaborationService = new AICollaborationService()

