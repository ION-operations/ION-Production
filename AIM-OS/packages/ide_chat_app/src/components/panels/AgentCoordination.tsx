// Multi-Agent Coordination Panel
// Visualizes and manages coordination between multiple AI agents
// V2 Enhancement - Week 4 Preview

import React, { useState, useEffect, useCallback, useMemo } from 'react'
import {
  Users,
  MessageSquare,
  Activity,
  CheckCircle,
  Clock,
  AlertCircle,
  Send,
  RefreshCw,
  Filter,
  Search,
  ArrowRight,
} from 'lucide-react'
import { useAIMOS } from '../../hooks/useAIMOS'
import { LoadingState } from '../LoadingState'

interface Agent {
  id: string
  name: string
  status: 'active' | 'idle' | 'waiting' | 'error'
  currentTask?: string
  confidence: number
  lastActivity: Date
  capabilities: string[]
}

interface AgentMessage {
  id: string
  from: string
  to: string
  content: string
  timestamp: Date
  type: 'discussion' | 'task_handoff' | 'status_update' | 'urgent'
  priority: 'low' | 'medium' | 'high' | 'urgent'
}

interface AgentCoordinationProps {
  onAgentClick?: (agent: Agent) => void
  onMessageClick?: (message: AgentMessage) => void
}

export const AgentCoordination: React.FC<AgentCoordinationProps> = ({
  onAgentClick,
  onMessageClick
}) => {
  const [agents, setAgents] = useState<Agent[]>([])
  const [messages, setMessages] = useState<AgentMessage[]>([])
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<'all' | Agent['status']>('all')
  const [filterPriority, setFilterPriority] = useState<'all' | AgentMessage['priority']>('all')
  const [isLoading, setIsLoading] = useState(false)
  const [isConnected, setIsConnected] = useState(false)

  // AIM-OS integration
  const { mcpTools } = useAIMOS()

  // Load agent coordination data
  const loadCoordinationData = useCallback(async () => {
    setIsLoading(true)
    try {
      // Try to get AI collaboration data from MCP tools
      if (mcpTools) {
        try {
          const collaborationResponse = await mcpTools.executeTool('get_ai_collaboration_summary', {})
          if (collaborationResponse?.success) {
            // Transform collaboration data to agents
            const collaborationData = collaborationResponse.result || {}
            
            // Mock agents based on collaboration data
            const mockAgents: Agent[] = [
              {
                id: 'aether',
                name: 'Aether',
                status: 'active',
                currentTask: 'V2 Development',
                confidence: 0.95,
                lastActivity: new Date(),
                capabilities: ['development', 'planning', 'documentation']
              },
              {
                id: 'sam',
                name: 'Sam',
                status: 'active',
                currentTask: 'IDE Orchestration',
                confidence: 0.90,
                lastActivity: new Date(Date.now() - 5 * 60 * 1000),
                capabilities: ['research', 'prototyping', 'visualization']
              },
              {
                id: 'max',
                name: 'Max',
                status: 'idle',
                confidence: 0.85,
                lastActivity: new Date(Date.now() - 30 * 60 * 1000),
                capabilities: ['architecture', 'design', 'customization']
              }
            ]

            setAgents(mockAgents)
            setIsConnected(true)

            // Try to get messages
            try {
              const messagesResponse = await mcpTools.executeTool('get_ai_messages', { limit: 20 })
              if (messagesResponse?.success && Array.isArray(messagesResponse.result)) {
                const agentMessages: AgentMessage[] = messagesResponse.result.map((msg: any) => ({
                  id: msg.message_id || msg.id || `msg-${Date.now()}`,
                  from: msg.from_ai || 'unknown',
                  to: msg.to_ai || 'unknown',
                  content: msg.content || '',
                  timestamp: new Date(msg.timestamp || msg.created_at || Date.now()),
                  type: msg.message_type || 'discussion',
                  priority: msg.priority || 'medium'
                }))
                setMessages(agentMessages)
              }
            } catch (err) {
              console.warn('Failed to load messages:', err)
            }
          }
        } catch (err) {
          console.warn('Failed to load collaboration data:', err)
          // Fallback to mock data
          const mockData = generateMockCoordinationData()
          setAgents(mockData.agents)
          setMessages(mockData.messages)
          setIsConnected(false)
        }
      } else {
        // Fallback to mock data
        const mockData = generateMockCoordinationData()
        setAgents(mockData.agents)
        setMessages(mockData.messages)
        setIsConnected(false)
      }
    } catch (error) {
      console.error('Failed to load coordination data:', error)
      const mockData = generateMockCoordinationData()
      setAgents(mockData.agents)
      setMessages(mockData.messages)
      setIsConnected(false)
    } finally {
      setIsLoading(false)
    }
  }, [mcpTools])

  useEffect(() => {
    loadCoordinationData()
  }, [loadCoordinationData])

  const filteredAgents = useMemo(() => {
    return agents.filter(agent => {
      const matchesSearch = searchTerm === '' ||
                            agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            agent.currentTask?.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesStatus = filterStatus === 'all' || agent.status === filterStatus
      return matchesSearch && matchesStatus
    })
  }, [agents, searchTerm, filterStatus])

  const filteredMessages = useMemo(() => {
    return messages.filter(msg => {
      const matchesSearch = searchTerm === '' ||
                            msg.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            msg.from.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            msg.to.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesPriority = filterPriority === 'all' || msg.priority === filterPriority
      return matchesSearch && matchesPriority
    }).sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
  }, [messages, searchTerm, filterPriority])

  const handleAgentClick = useCallback((agent: Agent) => {
    setSelectedAgent(agent)
    onAgentClick?.(agent)
  }, [onAgentClick])

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400 border-green-500'
      case 'idle': return 'bg-gray-500/20 text-gray-400 border-gray-500'
      case 'waiting': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500'
      case 'error': return 'bg-red-500/20 text-red-400 border-red-500'
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500'
    }
  }

  const getPriorityColor = (priority: AgentMessage['priority']) => {
    switch (priority) {
      case 'urgent': return 'text-red-400'
      case 'high': return 'text-orange-400'
      case 'medium': return 'text-yellow-400'
      case 'low': return 'text-gray-400'
      default: return 'text-gray-400'
    }
  }

  if (isLoading) {
    return <LoadingState message="Loading agent coordination..." />
  }

  return (
    <div className="h-full flex flex-col bg-gray-900 text-gray-200">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex items-center gap-2 shrink-0">
        <Users className="w-5 h-5 text-blue-400" />
        <div>
          <div className="text-white text-sm font-semibold">Multi-Agent Coordination ⭐</div>
          <div className="text-xs text-gray-500">AI Collaboration & Communication</div>
        </div>
        <span
          className={`ml-auto px-2 py-1 rounded-full text-xs font-medium ${
            isConnected ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
          }`}
        >
          {isConnected ? 'Connected' : 'Mock Mode'}
        </span>
        <button onClick={loadCoordinationData} className="text-gray-400 hover:text-white p-1 rounded">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Search and Filters */}
      <div className="p-3 border-b border-gray-700 shrink-0 space-y-2">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search agents or messages..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-gray-800 text-white text-sm px-9 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700"
          />
        </div>

        <div className="flex gap-2 overflow-x-auto pb-1">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as any)}
            className="px-3 py-1 text-xs rounded bg-gray-700 text-gray-300 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="idle">Idle</option>
            <option value="waiting">Waiting</option>
            <option value="error">Error</option>
          </select>

          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value as any)}
            className="px-3 py-1 text-xs rounded bg-gray-700 text-gray-300 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Priorities</option>
            <option value="urgent">Urgent</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden flex">
        {/* Agents List */}
        <div className="w-1/3 border-r border-gray-700 overflow-y-auto p-3">
          <h3 className="text-sm font-semibold text-gray-300 mb-2">Agents ({filteredAgents.length})</h3>
          <div className="space-y-2">
            {filteredAgents.map((agent) => (
              <div
                key={agent.id}
                onClick={() => handleAgentClick(agent)}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  selectedAgent?.id === agent.id
                    ? 'bg-blue-500/20 border-blue-500'
                    : 'bg-gray-800 border-gray-700 hover:bg-gray-750'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-300">{agent.name}</span>
                  <span className={`text-xs px-2 py-1 rounded border ${getStatusColor(agent.status)}`}>
                    {agent.status}
                  </span>
                </div>
                {agent.currentTask && (
                  <div className="text-xs text-gray-400 mb-1">{agent.currentTask}</div>
                )}
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-gray-500">
                    Confidence: {(agent.confidence * 100).toFixed(0)}%
                  </span>
                  <span className="text-xs text-gray-500">
                    {Math.floor((Date.now() - agent.lastActivity.getTime()) / 60000)}m ago
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-3">
          <h3 className="text-sm font-semibold text-gray-300 mb-2">
            Messages ({filteredMessages.length})
          </h3>
          <div className="space-y-2">
            {filteredMessages.length === 0 ? (
              <div className="text-center text-gray-400 py-8">
                <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No messages found</p>
              </div>
            ) : (
              filteredMessages.map((message) => (
                <div
                  key={message.id}
                  onClick={() => onMessageClick?.(message)}
                  className="p-3 bg-gray-800 border border-gray-700 rounded cursor-pointer hover:bg-gray-750 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-blue-400">{message.from}</span>
                      <ArrowRight className="w-3 h-3 text-gray-500" />
                      <span className="text-xs font-medium text-green-400">{message.to}</span>
                    </div>
                    <span className={`text-xs font-medium ${getPriorityColor(message.priority)}`}>
                      {message.priority}
                    </span>
                  </div>
                  <div className="text-xs text-gray-300 mb-1">{message.content}</div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">{message.type}</span>
                    <span className="text-xs text-gray-500">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Selected Agent Details */}
      {selectedAgent && (
        <div className="border-t border-gray-700 p-4 bg-gray-800 shrink-0 max-h-48 overflow-auto">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold text-gray-300">Agent Details</h4>
            <button
              onClick={() => setSelectedAgent(null)}
              className="text-gray-400 hover:text-gray-200"
            >
              ×
            </button>
          </div>
          <div className="text-xs text-gray-400 space-y-1">
            <div>Name: {selectedAgent.name}</div>
            <div>Status: {selectedAgent.status}</div>
            <div>Confidence: {(selectedAgent.confidence * 100).toFixed(0)}%</div>
            {selectedAgent.currentTask && (
              <div>Current Task: {selectedAgent.currentTask}</div>
            )}
            <div className="mt-2">
              <div className="font-medium text-gray-300 mb-1">Capabilities:</div>
              <div className="flex gap-1 flex-wrap">
                {selectedAgent.capabilities.map(cap => (
                  <span key={cap} className="px-1 py-0.5 bg-gray-700 rounded text-gray-400">
                    {cap}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Mock data generator
function generateMockCoordinationData(): { agents: Agent[]; messages: AgentMessage[] } {
  const agents: Agent[] = [
    {
      id: 'aether',
      name: 'Aether',
      status: 'active',
      currentTask: 'V2 Development',
      confidence: 0.95,
      lastActivity: new Date(),
      capabilities: ['development', 'planning', 'documentation']
    },
    {
      id: 'sam',
      name: 'Sam',
      status: 'active',
      currentTask: 'IDE Orchestration',
      confidence: 0.90,
      lastActivity: new Date(Date.now() - 5 * 60 * 1000),
      capabilities: ['research', 'prototyping', 'visualization']
    },
    {
      id: 'max',
      name: 'Max',
      status: 'idle',
      confidence: 0.85,
      lastActivity: new Date(Date.now() - 30 * 60 * 1000),
      capabilities: ['architecture', 'design', 'customization']
    }
  ]

  const messages: AgentMessage[] = [
    {
      id: 'msg-001',
      from: 'Aether',
      to: 'Sam',
      content: 'Week 3 integration complete. Ready for Week 4.',
      timestamp: new Date(Date.now() - 10 * 60 * 1000),
      type: 'status_update',
      priority: 'medium'
    },
    {
      id: 'msg-002',
      from: 'Sam',
      to: 'Aether',
      content: 'Evolution Explorer panel created. Context Web enhanced.',
      timestamp: new Date(Date.now() - 5 * 60 * 1000),
      type: 'status_update',
      priority: 'medium'
    }
  ]

  return { agents, messages }
}

