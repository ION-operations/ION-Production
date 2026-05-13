/**
 * MCP API Client for Mobile App
 * Simplified version - focuses on chat communication, not tool execution
 */

import { connectionManager } from './connectionManager';

export interface AIMessage {
  message_id: string;
  from_ai: string;
  to_ai: string;
  content: string;
  message_type: string;
  priority: string;
  thread_id?: string;
  timestamp: string;
  response_required: boolean;
}

export interface SendMessageRequest {
  to_ai?: string; // undefined = broadcast to all
  content: string;
  message_type?: string;
  priority?: string;
  thread_id?: string;
}

export class MCPAPI {
  private baseUrl: string;

  constructor() {
    this.baseUrl = connectionManager.getCommandServerUrl();
  }

  /**
   * Check if extension command server is available
   */
  async checkExtension(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000)
      });
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  /**
   * Send message to agent(s)
   * Primary function: Send chat messages and "proceed" prompts
   */
  async sendAIMessage(request: SendMessageRequest): Promise<{ success: boolean; message_id?: string; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/mcp/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool: 'send_ai_message',
          arguments: {
            to_ai: request.to_ai,
            content: request.content,
            message_type: request.message_type || 'discussion',
            priority: request.priority || 'medium',
            thread_id: request.thread_id
          }
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Extract message_id from result
      if (result.success && result.result) {
        return {
          success: true,
          message_id: result.result.message_id
        };
      }
      
      return {
        success: result.success || false,
        error: result.error || 'Unknown error'
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to send message'
      };
    }
  }

  /**
   * Get AI messages
   * Fetches messages from agents for display in chat
   */
  async getAIMessages(from_ai?: string, to_ai?: string, thread_id?: string): Promise<AIMessage[]> {
    try {
      const response = await fetch(`${this.baseUrl}/mcp/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool: 'get_ai_messages',
          arguments: {
            from_ai,
            to_ai,
            thread_id,
            limit: 100
          }
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success && result.result && Array.isArray(result.result.messages)) {
        return result.result.messages;
      }
      
      return [];
    } catch (error) {
      console.error('Failed to get AI messages:', error);
      return [];
    }
  }

  /**
   * Get collaboration summary
   * Shows which agents are active
   */
  async getAICollaborationSummary(): Promise<{ total_messages: number; active_agents: string[] }> {
    try {
      const response = await fetch(`${this.baseUrl}/mcp/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool: 'get_ai_collaboration_summary',
          arguments: {}
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success && result.result) {
        return result.result;
      }
      
      return { total_messages: 0, active_agents: [] };
    } catch (error) {
      console.error('Failed to get collaboration summary:', error);
      return { total_messages: 0, active_agents: [] };
    }
  }
}

export const mcpApi = new MCPAPI();

