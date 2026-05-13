// AIM-OS Service - Real Integration with MCP Tools
// Pattern: HTTP API first, graceful fallback to mock

const BASE_URL = 'http://localhost:8000'

interface MCPToolCall {
  name: string
  arguments: Record<string, any>
}

interface MCPToolResponse<T = any> {
  success: boolean
  result?: T
  error?: string
}

class AIMOSService {
  private async callMCPTool<T = any>(toolName: string, args: Record<string, any>): Promise<MCPToolResponse<T>> {
    try {
      // Try HTTP API first
      const response = await fetch(`${BASE_URL}/mcp/tools/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: toolName,
          arguments: args,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        return {
          success: data.success !== false,
          result: data.result || data,
          error: data.error,
        }
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
    } catch (error) {
      console.warn(`[AIMOSService] MCP tool ${toolName} failed, will use mock:`, error)
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error),
      }
    }
  }

  // CMC Operations
  async storeMemory(content: string, tags: Record<string, any> = {}): Promise<{ success: boolean; atom_id?: string; error?: string }> {
    const result = await this.callMCPTool('mcp_lucid-mcp_store_memory', { content, tags })
    if (result.success && result.result) {
      return {
        success: true,
        atom_id: result.result.atom_id || result.result.message?.match(/atom_id: ([a-f0-9-]+)/)?.[1],
      }
    }
    return { success: false, error: result.error || 'Failed to store memory' }
  }

  async retrieveMemory(query: string, limit: number = 10, tags?: Record<string, any>): Promise<any[]> {
    const result = await this.callMCPTool('mcp_lucid-mcp_retrieve_memory', { query, limit, tags })
    if (result.success && result.result) {
      return Array.isArray(result.result) ? result.result : []
    }
    return []
  }

  async getMemoryStats(): Promise<any> {
    const result = await this.callMCPTool('mcp_lucid-mcp_get_memory_stats', {})
    return result.success ? result.result || {} : {}
  }

  // VIF Operations
  async trackConfidence(task: string, confidence: number, evidence: string[] = [], reasoning: string = ''): Promise<{ success: boolean; error?: string }> {
    const result = await this.callMCPTool('mcp_lucid-mcp_track_confidence', {
      task,
      confidence,
      evidence,
      reasoning,
    })
    return { success: result.success || false, error: result.error }
  }

  // Timeline Operations
  async addTimelineEntry(promptId: string, userInput: string, contextState: Record<string, any> = {}): Promise<{ success: boolean; error?: string }> {
    const result = await this.callMCPTool('mcp_lucid-mcp_add_timeline_entry', {
      prompt_id: promptId,
      user_input: userInput,
      context_state: contextState,
    })
    return { success: result.success || false, error: result.error }
  }

  async getTimelineSummary(limit: number = 10): Promise<any[]> {
    const result = await this.callMCPTool('mcp_lucid-mcp_get_timeline_summary', { limit })
    if (result.success && result.result) {
      return Array.isArray(result.result) ? result.result : []
    }
    return []
  }

  async getTimelineEntries(startTime?: string, endTime?: string, limit: number = 50): Promise<any[]> {
    const result = await this.callMCPTool('mcp_lucid-mcp_get_timeline_entries', {
      start_time: startTime,
      end_time: endTime,
      limit,
    })
    if (result.success && result.result) {
      return Array.isArray(result.result) ? result.result : []
    }
    return []
  }

  // Goal Operations
  async updateGoalProgress(goalId: string, progress: number, status?: string, milestone?: string): Promise<{ success: boolean; error?: string }> {
    const result = await this.callMCPTool('mcp_lucid-mcp_update_goal_progress', {
      goal_id: goalId,
      progress,
      status,
      milestone,
    })
    return { success: result.success || false, error: result.error }
  }

  async queryGoalTimeline(status?: string, priority?: string, limit: number = 50): Promise<any[]> {
    const result = await this.callMCPTool('mcp_lucid-mcp_query_goal_timeline', {
      status,
      priority,
      limit,
    })
    if (result.success && result.result) {
      return Array.isArray(result.result) ? result.result : []
    }
    return []
  }

  // SEG Operations
  async synthesizeKnowledge(topics: string[], depth: string = 'medium', format: string = 'summary'): Promise<{ success: boolean; result?: any; error?: string }> {
    const result = await this.callMCPTool('mcp_lucid-mcp_synthesize_knowledge', {
      topics,
      depth,
      format,
    })
    return {
      success: result.success || false,
      result: result.result,
      error: result.error,
    }
  }

  // APOE Operations
  async createPlan(goal: string, context: string = '', priority: string = 'medium'): Promise<{ success: boolean; result?: any; error?: string }> {
    const result = await this.callMCPTool('mcp_lucid-mcp_create_plan', {
      goal,
      context,
      priority,
    })
    return {
      success: result.success || false,
      result: result.result,
      error: result.error,
    }
  }

  // AI Collaboration Operations
  async sendAIMessage(
    toAI: string,
    content: string,
    messageType: 'discussion' | 'task_handoff' | 'problem_solving' | 'profile_sharing' | 'status_update' | 'urgent' = 'discussion',
    priority: 'low' | 'medium' | 'high' | 'urgent' = 'medium',
    threadId?: string
  ): Promise<{ success: boolean; message_id?: string; error?: string }> {
    const result = await this.callMCPTool('mcp_lucid-mcp_send_ai_message', {
      from_ai: 'Lex',
      to_ai: toAI,
      content,
      message_type: messageType,
      priority,
      thread_id: threadId,
    })
    if (result.success && result.result) {
      return {
        success: true,
        message_id: result.result.message_id || result.result.atom_id,
      }
    }
    return { success: false, error: result.error || 'Failed to send message' }
  }

  async getAIMessages(fromAI?: string, toAI?: string, threadId?: string, limit: number = 50): Promise<any[]> {
    const result = await this.callMCPTool('mcp_lucid-mcp_get_ai_messages', {
      from_ai: fromAI,
      to_ai: toAI,
      thread_id: threadId,
      limit,
    })
    if (result.success && result.result) {
      return Array.isArray(result.result) ? result.result : []
    }
    return []
  }
}

export const aimosService = new AIMOSService()

