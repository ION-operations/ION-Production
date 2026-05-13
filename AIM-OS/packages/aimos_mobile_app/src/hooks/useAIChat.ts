/**
 * useAIChat Hook for Mobile App
 * Simplified version focusing on chat communication
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { mcpApi, AIMessage } from '../services/mcpApi';

export interface ChatThread {
  thread_id: string;
  topic: string;
  participants: string[];
  last_message?: AIMessage;
  unread_count: number;
}

export function useAIChat(agentId?: string, threadId?: string) {
  const [messages, setMessages] = useState<AIMessage[]>([]);
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [discoveredAgents, setDiscoveredAgents] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(true);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Fetch messages from agents
   */
  const fetchMessages = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch messages via MCP API
      let fetchedMessages: AIMessage[];
      if (agentId) {
        // Fetch messages involving specific agent
        const [fromMessages, toMessages] = await Promise.all([
          mcpApi.getAIMessages(agentId, undefined, threadId),
          mcpApi.getAIMessages(undefined, agentId, threadId)
        ]);
        // Combine and deduplicate
        const messageMap = new Map<string, AIMessage>();
        fromMessages.forEach(msg => messageMap.set(msg.message_id, msg));
        toMessages.forEach(msg => messageMap.set(msg.message_id, msg));
        fetchedMessages = Array.from(messageMap.values());
      } else {
        // Fetch all messages (shared chat)
        fetchedMessages = await mcpApi.getAIMessages(undefined, undefined, threadId);
      }

      // Sort by timestamp (newest first)
      fetchedMessages.sort((a, b) => 
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      );

      setMessages(fetchedMessages);

      // Auto-detect agents from messages
      const agentSet = new Set<string>();
      fetchedMessages.forEach((msg) => {
        if (msg.from_ai && msg.from_ai !== 'electron-app' && msg.from_ai !== 'User') {
          agentSet.add(msg.from_ai);
        }
        if (msg.to_ai && msg.to_ai !== 'electron-app' && msg.to_ai !== 'User') {
          agentSet.add(msg.to_ai);
        }
      });
      setDiscoveredAgents(Array.from(agentSet));

    } catch (err: any) {
      setError(err.message || 'Failed to fetch messages');
      console.error('Error fetching messages:', err);
    } finally {
      setLoading(false);
    }
  }, [agentId, threadId]);

  /**
   * Send message to agent(s)
   */
  const sendMessage = useCallback(async (toAgent: string | undefined, content: string) => {
    try {
      setError(null);

      const result = await mcpApi.sendAIMessage({
        to_ai: toAgent,
        content,
        message_type: 'discussion',
        priority: 'medium'
      });

      if (!result.success) {
        throw new Error(result.error || 'Failed to send message');
      }

      // Refresh messages after sending
      await fetchMessages();

      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
      throw err;
    }
  }, [fetchMessages]);

  /**
   * Send "proceed" command
   * Special function for prompting agents to proceed with work
   */
  const sendProceedCommand = useCallback(async (toAgent?: string, context?: string) => {
    const proceedMessage = context 
      ? `proceed with: ${context}`
      : 'proceed';
    
    return sendMessage(toAgent, proceedMessage);
  }, [sendMessage]);

  /**
   * Start polling for messages
   */
  useEffect(() => {
    if (isPolling) {
      // Initial fetch
      fetchMessages();

      // Poll every 2 seconds (mobile-optimized)
      pollingIntervalRef.current = setInterval(() => {
        fetchMessages();
      }, 2000);
    } else {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    }

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, [isPolling, fetchMessages]);

  return {
    messages,
    threads,
    discoveredAgents,
    loading,
    error,
    isPolling,
    fetchMessages,
    sendMessage,
    sendProceedCommand,
    stopPolling: () => setIsPolling(false),
    resumePolling: () => setIsPolling(true)
  };
}

