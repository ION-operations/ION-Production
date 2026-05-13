/**
 * Workflow Manager Component
 * Visual interface for managing workflows, prompt chains, and automation
 */

import React, { useState, useEffect } from 'react'
import { 
  Play, 
  Pause, 
  Square, 
  Plus, 
  Settings, 
  GitBranch, 
  Zap, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Activity,
  Workflow as WorkflowIcon,
  Bot,
  Code
} from 'lucide-react'
import { workflowAutomation, Workflow, WorkflowExecution } from '../lib/workflow-automation'
import { promptChainManager, PromptChain } from '../lib/prompt-chain-manager'

export const WorkflowManager: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [chains, setChains] = useState<PromptChain[]>([])
  const [executions, setExecutions] = useState<WorkflowExecution[]>([])
  const [activeTab, setActiveTab] = useState<'workflows' | 'chains' | 'executions'>('workflows')
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null)
  const [isRunning, setIsRunning] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = () => {
    setWorkflows(workflowAutomation.getAllWorkflows())
    setChains(promptChainManager.getAllChains())
    setExecutions(workflowAutomation.getAllExecutions())
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Activity className="w-4 h-4 text-blue-400 animate-pulse" />
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'failed': return <XCircle className="w-4 h-4 text-red-400" />
      case 'cancelled': return <Square className="w-4 h-4 text-gray-400" />
      case 'paused': return <Pause className="w-4 h-4 text-yellow-400" />
      default: return <AlertCircle className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-blue-400'
      case 'completed': return 'text-green-400'
      case 'failed': return 'text-red-400'
      case 'cancelled': return 'text-gray-400'
      case 'paused': return 'text-yellow-400'
      default: return 'text-gray-400'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-900 text-red-100 border-red-700'
      case 'high': return 'bg-orange-900 text-orange-100 border-orange-700'
      case 'medium': return 'bg-blue-900 text-blue-100 border-blue-700'
      case 'low': return 'bg-gray-900 text-gray-100 border-gray-700'
      default: return 'bg-gray-900 text-gray-100 border-gray-700'
    }
  }

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`
    if (ms < 60000) return `${Math.round(ms / 1000)}s`
    return `${Math.round(ms / 60000)}m`
  }

  const formatDate = (date: Date) => {
    return date.toLocaleString([], { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const handleRunWorkflow = async (workflowId: string) => {
    setIsRunning(true)
    try {
      // Simulate triggering a workflow
      await workflowAutomation.triggerWorkflow('manual', { 
        workflowId, 
        triggeredBy: 'user',
        timestamp: new Date()
      })
      loadData()
    } catch (error) {
      console.error('Error running workflow:', error)
    } finally {
      setIsRunning(false)
    }
  }

  const handleRunChain = async (chainId: string) => {
    setIsRunning(true)
    try {
      await promptChainManager.executeChain(chainId, { triggeredBy: 'user' })
      loadData()
    } catch (error) {
      console.error('Error running chain:', error)
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="h-full bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <WorkflowIcon className="w-5 h-5 text-blue-400" />
          <div>
            <h2 className="text-white text-lg font-semibold">Workflow Manager</h2>
            <p className="text-gray-400 text-sm">Automate your development workflow</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button className="p-2 bg-blue-600 hover:bg-blue-700 rounded text-white">
            <Plus className="w-4 h-4" />
          </button>
          <button className="p-2 bg-gray-800 hover:bg-gray-700 rounded text-gray-400 hover:text-white">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-4 py-2 border-b border-gray-700">
        <div className="flex gap-1">
          <button
            onClick={() => setActiveTab('workflows')}
            className={`px-3 py-1 text-sm rounded ${
              activeTab === 'workflows' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            Workflows ({workflows.length})
          </button>
          <button
            onClick={() => setActiveTab('chains')}
            className={`px-3 py-1 text-sm rounded ${
              activeTab === 'chains' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            Prompt Chains ({chains.length})
          </button>
          <button
            onClick={() => setActiveTab('executions')}
            className={`px-3 py-1 text-sm rounded ${
              activeTab === 'executions' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            Executions ({executions.length})
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'workflows' && (
          <div className="space-y-4">
            {workflows.map(workflow => (
              <div key={workflow.id} className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`px-2 py-1 rounded text-xs font-semibold ${getPriorityColor(workflow.priority)}`}>
                      {workflow.priority.toUpperCase()}
                    </div>
                    <h3 className="text-white font-semibold">{workflow.name}</h3>
                    {workflow.enabled ? (
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                    ) : (
                      <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleRunWorkflow(workflow.id)}
                      disabled={isRunning || !workflow.enabled}
                      className="p-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded text-white"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setSelectedWorkflow(selectedWorkflow === workflow.id ? null : workflow.id)}
                      className="p-2 bg-gray-700 hover:bg-gray-600 rounded text-gray-400 hover:text-white"
                    >
                      <Settings className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <p className="text-gray-400 text-sm mb-3">{workflow.description}</p>
                
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <GitBranch className="w-4 h-4" />
                    <span>{workflow.triggers.length} triggers</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Zap className="w-4 h-4" />
                    <span>{workflow.actions.length} actions</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    <span>{formatDate(workflow.updatedAt)}</span>
                  </div>
                </div>

                {selectedWorkflow === workflow.id && (
                  <div className="mt-4 pt-4 border-t border-gray-700">
                    <div className="space-y-3">
                      <div>
                        <h4 className="text-white text-sm font-semibold mb-2">Triggers</h4>
                        {workflow.triggers.map(trigger => (
                          <div key={trigger.id} className="bg-gray-700 p-2 rounded text-sm">
                            <div className="text-white">{trigger.name}</div>
                            <div className="text-gray-400">{trigger.type}</div>
                          </div>
                        ))}
                      </div>
                      <div>
                        <h4 className="text-white text-sm font-semibold mb-2">Actions</h4>
                        {workflow.actions.map(action => (
                          <div key={action.id} className="bg-gray-700 p-2 rounded text-sm">
                            <div className="text-white">{action.name}</div>
                            <div className="text-gray-400">{action.type}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {activeTab === 'chains' && (
          <div className="space-y-4">
            {chains.map(chain => (
              <div key={chain.id} className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <h3 className="text-white font-semibold">{chain.name}</h3>
                    <div className={`px-2 py-1 rounded text-xs ${
                      chain.status === 'active' ? 'bg-green-900 text-green-100' : 'bg-gray-900 text-gray-100'
                    }`}>
                      {chain.status.toUpperCase()}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleRunChain(chain.id)}
                      disabled={isRunning || chain.status !== 'active'}
                      className="p-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded text-white"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                    <button className="p-2 bg-gray-700 hover:bg-gray-600 rounded text-gray-400 hover:text-white">
                      <Settings className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <p className="text-gray-400 text-sm mb-3">{chain.description}</p>
                
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <Code className="w-4 h-4" />
                    <span>{chain.steps.length} steps</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Bot className="w-4 h-4" />
                    <span>v{chain.version}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    <span>{formatDate(chain.updatedAt)}</span>
                  </div>
                </div>

                {/* Steps Preview */}
                <div className="mt-3">
                  <div className="flex gap-2">
                    {chain.steps.slice(0, 5).map((step, index) => (
                      <div key={step.id} className="flex items-center gap-1 bg-gray-700 px-2 py-1 rounded text-xs">
                        <span className="text-gray-400">{index + 1}</span>
                        <span className="text-white">{step.name}</span>
                      </div>
                    ))}
                    {chain.steps.length > 5 && (
                      <div className="text-xs text-gray-400 px-2 py-1">
                        +{chain.steps.length - 5} more
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'executions' && (
          <div className="space-y-4">
            {executions.length === 0 ? (
              <div className="text-center text-gray-400 py-8">
                <Activity className="w-8 h-8 mx-auto mb-2" />
                <p>No executions yet</p>
                <p className="text-sm">Run a workflow or chain to see executions here</p>
              </div>
            ) : (
              executions.map(execution => (
                <div key={execution.id} className="bg-gray-800 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(execution.status)}
                      <h3 className="text-white font-semibold">
                        {workflows.find(w => w.id === execution.workflowId)?.name || 'Unknown Workflow'}
                      </h3>
                      <div className={`text-sm ${getStatusColor(execution.status)}`}>
                        {execution.status.toUpperCase()}
                      </div>
                    </div>
                    <div className="text-sm text-gray-400">
                      {formatDate(execution.startedAt)}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                    <div className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      <span>
                        {execution.completedAt 
                          ? formatDuration(execution.completedAt.getTime() - execution.startedAt.getTime())
                          : 'Running...'
                        }
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Zap className="w-4 h-4" />
                      <span>{execution.results.length} actions</span>
                    </div>
                  </div>

                  {/* Action Results */}
                  <div className="space-y-2">
                    {execution.results.map((result, index) => (
                      <div key={result.actionId} className="flex items-center gap-3 bg-gray-700 p-2 rounded">
                        <div className="w-6 h-6 rounded-full bg-gray-600 flex items-center justify-center text-xs">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <div className="text-white text-sm">{result.actionId}</div>
                          <div className="text-gray-400 text-xs">
                            {result.duration ? formatDuration(result.duration) : 'Pending'}
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          {getStatusIcon(result.status)}
                          <span className={`text-xs ${getStatusColor(result.status)}`}>
                            {result.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {execution.error && (
                    <div className="mt-3 p-2 bg-red-900 text-red-100 rounded text-sm">
                      <strong>Error:</strong> {execution.error}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  )
}
