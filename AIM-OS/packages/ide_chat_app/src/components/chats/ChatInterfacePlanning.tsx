/**
 * Chat Interface for Planning Agent
 * Right drawer - Strategic, analytical, big-picture focused AI agent
 */

import React, { useState, useRef, useEffect } from 'react'
import { 
  Sparkles, 
  Send, 
  Bot, 
  Target, 
  Calendar, 
  AlertTriangle, 
  CheckCircle, 
  TrendingUp,
  Users,
  Clock,
  Settings,
  GitBranch,
  BarChart3,
  Lightbulb,
  Shield,
  Zap
} from 'lucide-react'
import { ChatMessage } from './ChatMessage'
import { usePlanningAgent } from '../../contexts/PlanningAgentContext'
import { crossChatBridge, createCrossAgentMessage } from '../../lib/cross-chat-bridge'
import { enhancedAIService } from '../../lib/ai-service-enhanced'
import { performanceMonitor } from '../../lib/performance-monitor'

interface ChatInterfacePlanningProps {
  className?: string
}

export const ChatInterfacePlanning: React.FC<ChatInterfacePlanningProps> = ({ className = '' }) => {
  const { 
    state, 
    addMessage, 
    setTyping, 
    addGoal, 
    addMilestone, 
    addArchitectureDecision,
    addRisk,
    getActiveGoals,
    getHighPriorityGoals,
    getProjectProgress
  } = usePlanningAgent()
  
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showQuickActions, setShowQuickActions] = useState(false)
  const [activeTab, setActiveTab] = useState<'chat' | 'goals' | 'architecture' | 'risks'>('chat')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [state.messages])

  // Subscribe to cross-agent messages
  useEffect(() => {
    const unsubscribe = crossChatBridge.subscribe('planning', (crossMessage) => {
      const chatMessage = crossChatBridge.convertToChatMessage(crossMessage)
      addMessage(chatMessage)
    })

    return unsubscribe
  }, [addMessage])

  // Handle send message
  const handleSendMessage = async () => {
    if (inputValue.trim() === '' || isLoading) return

    const userMessage = inputValue.trim()
    setInputValue('')
    setIsLoading(true)
    setTyping(true)

    // Add user message
    addMessage({
      content: userMessage,
      role: 'user',
      agent: 'planning',
      type: 'message'
    })

    try {
      // Generate AI response
      const response = await enhancedAIService.generateAgentResponse('planning', {
        prompt: userMessage,
        provider: 'planning' as any
      })

      // Add AI response
      addMessage({
        content: response.content,
        role: 'assistant',
        agent: 'planning',
        type: 'message',
        metadata: {
          confidence: response.metadata.confidence
        }
      })

      // Track performance
      performanceMonitor.recordAIMOSOperation('planning_agent_response', response.metadata.responseTime)

    } catch (error) {
      console.error('Failed to generate response:', error)
      
      addMessage({
        content: `I encountered an error while processing your request: ${(error as Error).message}. Let me help you with strategic planning instead.`,
        role: 'assistant',
        agent: 'planning',
        type: 'message',
        metadata: {
          confidence: 0.3
        }
      })
    } finally {
      setIsLoading(false)
      setTyping(false)
    }
  }

  // Handle quick actions
  const handleQuickAction = async (action: string) => {
    const actionPrompts: Record<string, string> = {
      'analyze': 'Analyze the current project architecture and provide strategic recommendations',
      'plan': 'Create a detailed project plan with milestones and goals',
      'review': 'Review the current project status and identify potential issues',
      'optimize': 'Suggest optimizations for project efficiency and delivery',
      'risks': 'Identify and analyze potential project risks',
      'roadmap': 'Create a high-level project roadmap'
    }

    const prompt = actionPrompts[action] || action
    setInputValue(prompt)
    setShowQuickActions(false)
  }

  // Handle cross-agent response
  const handleCrossAgentResponse = (messageId: string, response: string) => {
    // Send response back to coding agent
    crossChatBridge.sendMessage(createCrossAgentMessage(
      'planning',
      'coding',
      'consensus',
      response,
      { conversationId: messageId },
      true
    ))
  }

  // Quick action buttons
  const quickActions = [
    { id: 'analyze', label: 'Analyze', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'plan', label: 'Plan', icon: <Target className="w-4 h-4" /> },
    { id: 'review', label: 'Review', icon: <CheckCircle className="w-4 h-4" /> },
    { id: 'optimize', label: 'Optimize', icon: <Zap className="w-4 h-4" /> },
    { id: 'risks', label: 'Risks', icon: <Shield className="w-4 h-4" /> },
    { id: 'roadmap', label: 'Roadmap', icon: <TrendingUp className="w-4 h-4" /> }
  ]

  // Render goals tab
  const renderGoalsTab = () => {
    const activeGoals = getActiveGoals()
    const highPriorityGoals = getHighPriorityGoals()
    const projectProgress = getProjectProgress()

    return (
      <div className="space-y-4">
        {/* Project Progress */}
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-white">Project Progress</h3>
            <span className="text-xs text-gray-400">{projectProgress}%</span>
          </div>
          <div className="w-full bg-gray-600 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${projectProgress}%` }}
            />
          </div>
        </div>

        {/* High Priority Goals */}
        <div>
          <h3 className="text-sm font-semibold text-white mb-2">High Priority Goals</h3>
          <div className="space-y-2">
            {highPriorityGoals.slice(0, 3).map(goal => (
              <div key={goal.id} className="bg-gray-700 rounded p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-white">{goal.title}</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    goal.priority === 'critical' ? 'bg-red-900 text-red-300' :
                    goal.priority === 'high' ? 'bg-orange-900 text-orange-300' :
                    'bg-yellow-900 text-yellow-300'
                  }`}>
                    {goal.priority}
                  </span>
                </div>
                <div className="text-xs text-gray-400">{goal.description}</div>
                <div className="mt-2">
                  <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                    <span>Progress</span>
                    <span>{goal.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-600 rounded-full h-1">
                    <div 
                      className="bg-green-600 h-1 rounded-full"
                      style={{ width: `${goal.progress}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Active Goals */}
        <div>
          <h3 className="text-sm font-semibold text-white mb-2">Active Goals</h3>
          <div className="space-y-2">
            {activeGoals.slice(0, 5).map(goal => (
              <div key={goal.id} className="bg-gray-700 rounded p-3">
                <div className="text-sm text-white">{goal.title}</div>
                <div className="text-xs text-gray-400 mt-1">{goal.description}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  // Render architecture tab
  const renderArchitectureTab = () => {
    return (
      <div className="space-y-4">
        {/* Technologies */}
        <div>
          <h3 className="text-sm font-semibold text-white mb-2">Technologies</h3>
          <div className="flex flex-wrap gap-2">
            {state.architecture.technologies.map((tech, index) => (
              <span key={index} className="px-2 py-1 bg-blue-900 text-blue-300 text-xs rounded">
                {tech}
              </span>
            ))}
          </div>
        </div>

        {/* Patterns */}
        <div>
          <h3 className="text-sm font-semibold text-white mb-2">Architecture Patterns</h3>
          <div className="flex flex-wrap gap-2">
            {state.architecture.patterns.map((pattern, index) => (
              <span key={index} className="px-2 py-1 bg-purple-900 text-purple-300 text-xs rounded">
                {pattern}
              </span>
            ))}
          </div>
        </div>

        {/* Recent Decisions */}
        <div>
          <h3 className="text-sm font-semibold text-white mb-2">Recent Decisions</h3>
          <div className="space-y-2">
            {state.architecture.decisions.slice(-3).map(decision => (
              <div key={decision.id} className="bg-gray-700 rounded p-3">
                <div className="text-sm text-white">{decision.decision}</div>
                <div className="text-xs text-gray-400 mt-1">{decision.rationale}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {decision.date.toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  // Render risks tab
  const renderRisksTab = () => {
    return (
      <div className="space-y-4">
        <div>
          <h3 className="text-sm font-semibold text-white mb-2">Project Risks</h3>
          <div className="space-y-2">
            {state.architecture.risks.map(risk => (
              <div key={risk.id} className="bg-gray-700 rounded p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-white">{risk.risk}</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    risk.probability === 'high' ? 'bg-red-900 text-red-300' :
                    risk.probability === 'medium' ? 'bg-yellow-900 text-yellow-300' :
                    'bg-green-900 text-green-300'
                  }`}>
                    {risk.probability} probability
                  </span>
                </div>
                <div className="text-xs text-gray-400">{risk.mitigation}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`h-full bg-gray-800 flex flex-col ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-400" />
            <div>
              <div className="text-white text-sm font-semibold">AI Planning Agent</div>
              <div className="text-xs text-gray-500">
                Strategic planning & architecture
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${state.isTyping ? 'bg-purple-500 animate-pulse' : 'bg-green-500'}`} />
            <span className="text-xs text-gray-400">
              {state.isTyping ? 'Thinking...' : 'Ready'}
            </span>
            
            <button
              onClick={() => setShowQuickActions(!showQuickActions)}
              className="p-1 hover:bg-gray-700 rounded"
            >
              <Settings className="w-4 h-4 text-gray-400" />
            </button>
          </div>
        </div>

        {/* Project Context */}
        {state.context.projectName && (
          <div className="mt-2 text-xs text-gray-400">
            <Target className="w-3 h-3 inline mr-1" />
            {state.context.projectName}
            {state.context.teamSize > 1 && (
              <span className="ml-2">
                <Users className="w-3 h-3 inline mr-1" />
                {state.context.teamSize} team members
              </span>
            )}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      {showQuickActions && (
        <div className="px-4 py-2 border-b border-gray-700">
          <div className="text-xs text-gray-400 mb-2">Quick Actions</div>
          <div className="grid grid-cols-3 gap-2">
            {quickActions.map(action => (
              <button
                key={action.id}
                onClick={() => handleQuickAction(action.id)}
                className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded"
              >
                {action.icon}
                {action.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="px-4 py-2 border-b border-gray-700">
        <div className="flex gap-4">
          {[
            { id: 'chat', label: 'Chat', icon: <Bot className="w-4 h-4" /> },
            { id: 'goals', label: 'Goals', icon: <Target className="w-4 h-4" /> },
            { id: 'architecture', label: 'Architecture', icon: <BarChart3 className="w-4 h-4" /> },
            { id: 'risks', label: 'Risks', icon: <Shield className="w-4 h-4" /> }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-1 px-3 py-1 text-xs rounded ${
                activeTab === tab.id 
                  ? 'bg-purple-600 text-white' 
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'chat' ? (
          <div className="space-y-3">
            {state.messages.map(message => (
              <ChatMessage
                key={message.id}
                message={message}
                onCrossAgentResponse={handleCrossAgentResponse}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>
        ) : activeTab === 'goals' ? (
          renderGoalsTab()
        ) : activeTab === 'architecture' ? (
          renderArchitectureTab()
        ) : activeTab === 'risks' ? (
          renderRisksTab()
        ) : null}
      </div>

      {/* Input (only show in chat tab) */}
      {activeTab === 'chat' && (
        <div className="p-4 border-t border-gray-700">
          <div className="flex gap-2">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask me about strategy, architecture, planning, or project management..."
              className="flex-1 bg-gray-700 text-white text-sm rounded p-3 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
              rows={2}
              disabled={isLoading}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSendMessage()
                }
              }}
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || inputValue.trim() === ''}
              className="p-3 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white rounded"
            >
              {isLoading ? (
                <Clock className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
