/**
 * Prompt Chains Tab Component
 * Tab 3: Visual prompt chain builder and viewer
 * 
 * Created: 2025-10-31
 * Agent: Aether
 */

import React, { useState, useEffect, useCallback } from 'react'
import { Link, Play, Pause, Square, Plus, RefreshCw, Eye, EyeOff, Edit2, Trash2, Save, X } from 'lucide-react'
import { getServiceBridge } from '../../services/serviceBridge'
import { PromptChainEditor } from './PromptChainEditor'

const serviceBridge = getServiceBridge()

interface PromptStep {
  id: string
  name: string
  description: string
  agentId?: string
  systemId?: string
  status: 'pending' | 'running' | 'completed' | 'error'
  duration?: number
  confidence?: number
}

interface PromptChain {
  id: string
  atom_id?: string // CMC atom ID
  chain_id?: string // Chain ID
  name: string
  description: string
  steps: PromptStep[]
  nodes?: any[] // Full node data from CMC
  edges?: any[] // Full edge data from CMC
  status: 'running' | 'paused' | 'completed' | 'error'
  createdAt: Date
  currentStep: number
  created_by?: string
  updated_by?: string
  version?: number
  isTemplate?: boolean
}

export const PromptChainsTab: React.FC = () => {
  const [chains, setChains] = useState<PromptChain[]>([])
  const [selectedChain, setSelectedChain] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [editingChain, setEditingChain] = useState<string | null>(null)
  const [showEditor, setShowEditor] = useState(false)
  const [editorChainId, setEditorChainId] = useState<string | undefined>(undefined)

  // Fetch chains from ServiceBridge (routes to MCP)
  const loadChains = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      console.log('[PromptChainsTab] Loading chains...')
      const result = await serviceBridge.listPromptChains({}, 50)
      console.log('[PromptChainsTab] listPromptChains result:', result)
      
      if (result.success) {
        if (result.chains && Array.isArray(result.chains) && result.chains.length > 0) {
          console.log(`[PromptChainsTab] Found ${result.chains.length} chains`)
          // Convert CMC chain format to UI format
          const convertedChains: PromptChain[] = result.chains.map((chain: any) => {
            console.log('[PromptChainsTab] Processing chain:', chain.chain_id || chain.atom_id, chain.name)
            return {
              id: chain.chain_id || chain.atom_id || `chain_${Date.now()}`,
              atom_id: chain.atom_id,
              chain_id: chain.chain_id,
              name: chain.name,
              description: chain.description || '',
              steps: chain.nodes?.map((node: any) => ({
                id: node.id,
                name: node.label,
                description: node.prompt || node.description || '',
                agentId: node.agentId,
                systemId: node.systemId,
                status: 'pending' as const,
                duration: undefined,
                confidence: undefined
              })) || [],
              nodes: chain.nodes || [],
              edges: chain.edges || [],
              status: 'paused' as const,
              createdAt: new Date(chain.created_at || chain.updated_at || Date.now()),
              currentStep: 0,
              created_by: chain.created_by,
              updated_by: chain.updated_by,
              version: chain.version,
              isTemplate: chain.isTemplate || false
            }
          })
          
          console.log(`[PromptChainsTab] Converted ${convertedChains.length} chains for UI`)
          setChains(convertedChains)
        } else {
          console.log('[PromptChainsTab] No chains found (empty array or null)')
          setChains([])
          // Don't set error if chains array is just empty - that's valid
        }
      } else {
        const errorMsg = result.error || 'Failed to load chains'
        console.error('[PromptChainsTab] Failed to load chains:', errorMsg)
        setError(errorMsg)
      }
    } catch (err) {
      console.error('[PromptChainsTab] Exception loading prompt chains:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadChains()
    // Poll every 5 seconds for real-time updates
    const interval = setInterval(loadChains, 5000)
    return () => clearInterval(interval)
  }, [loadChains])

  // Handle chain update (sync to CMC)
  const handleChainUpdate = useCallback(async (chainId: string, updates: any) => {
    const chain = chains.find(c => c.id === chainId)
    if (!chain || !chain.atom_id) {
      console.error('Chain not found or missing atom_id')
      return
    }

    try {
      setLoading(true)
      const result = await serviceBridge.updatePromptChain(
        chain.atom_id,
        updates,
        'User manually edited chain',
        'user'
      )

      if (result.success) {
        // Refresh chains
        await loadChains()
        setEditingChain(null)
      } else {
        setError(result.error || 'Failed to update chain')
      }
    } catch (err) {
      console.error('Failed to update chain:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [chains, loadChains])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-400 bg-green-900/30'
      case 'paused': return 'text-yellow-400 bg-yellow-900/30'
      case 'completed': return 'text-blue-400 bg-blue-900/30'
      case 'error': return 'text-red-400 bg-red-900/30'
      default: return 'text-gray-400 bg-gray-900/30'
    }
  }

  const getStepStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-600'
      case 'running': return 'bg-yellow-600 animate-pulse'
      case 'error': return 'bg-red-600'
      default: return 'bg-cursor-input-bg'
    }
  }

  return (
    <div className="h-full flex flex-col bg-cursor-bg text-cursor-text">
      {/* Header */}
      <div className="p-2 border-b border-cursor-border">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Link className="w-5 h-5 text-cursor-status-bar" />
            <div>
              <h1 className="text-base font-semibold" style={{ fontSize: '15px' }}>Prompt Chains</h1>
              <p className="text-xs text-cursor-text-secondary">Visual prompt chain builder and execution monitor</p>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <button 
              onClick={() => {
                setShowEditor(true)
                setEditorChainId(undefined)
              }}
              disabled={loading}
              className="px-2 py-1 bg-cursor-status-bar hover:bg-cursor-status-bar/80 disabled:opacity-50 rounded flex items-center gap-1.5 text-xs cursor-button" 
              style={{ fontSize: '12px' }}
              title="Create new chain"
            >
              <Plus className="w-3.5 h-3.5" />
              New Chain
            </button>
            <button 
              onClick={loadChains}
              disabled={loading}
              className={`p-1.5 bg-cursor-hover hover:bg-cursor-active rounded cursor-button ${loading ? 'animate-spin' : ''}`}
              title="Refresh chains"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
          {error && (
            <div className="text-xs text-red-400 mt-1">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Chains List */}
      <div className="flex-1 overflow-y-auto p-2 cursor-scrollbar">
        {loading && chains.length === 0 && (
          <div className="flex items-center justify-center p-4">
            <RefreshCw className="w-5 h-5 animate-spin text-cursor-text-secondary" />
            <span className="ml-2 text-xs text-cursor-text-secondary">Loading chains...</span>
          </div>
        )}
        {!loading && chains.length === 0 && (
          <div className="flex flex-col items-center justify-center p-8 text-center">
            <Link className="w-12 h-12 text-cursor-text-secondary mb-2 opacity-50" />
            <p className="text-sm text-cursor-text-secondary mb-1">No prompt chains found</p>
            <p className="text-xs text-cursor-text-muted">
              Chains created via MCP tools will appear here automatically
            </p>
          </div>
        )}
        <div className="space-y-2">
          {chains.map((chain) => (
            <div
              key={chain.id}
              className={`bg-cursor-sidebar rounded p-2 border transition-all cursor-pointer cursor-list-item ${
                selectedChain === chain.id ? 'border-cursor-status-bar' : 'border-cursor-border'
              }`}
              onClick={() => setSelectedChain(chain.id === selectedChain ? null : chain.id)}
            >
              {/* Chain Header */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-1.5 mb-1">
                    <h3 className="text-sm font-semibold" style={{ fontSize: '13px' }}>{chain.name}</h3>
                    <span className={`px-1.5 py-0.5 text-xs rounded ${getStatusColor(chain.status)}`} style={{ fontSize: '10px' }}>
                      {chain.status.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-xs text-cursor-text-secondary mb-1">{chain.description}</p>
                  <div className="flex items-center gap-2 text-xs text-cursor-text-secondary">
                    <span>Step {chain.currentStep} of {chain.steps.length}</span>
                    <span>•</span>
                    <span>Created {Math.round((Date.now() - chain.createdAt.getTime()) / 1000)}s ago</span>
                    {chain.created_by && (
                      <>
                        <span>•</span>
                        <span className="text-cursor-status-bar">Created by: {chain.created_by}</span>
                      </>
                    )}
                    {chain.version && (
                      <>
                        <span>•</span>
                        <span className="text-cursor-text-muted">v{chain.version}</span>
                      </>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-1.5">
                  {chain.isTemplate && (
                    <span className="px-1.5 py-0.5 text-xs rounded bg-purple-900/30 text-purple-300" style={{ fontSize: '10px' }}>
                      📋 Template
                    </span>
                  )}
                  {chain.created_by === 'ai' && (
                    <span className="px-1.5 py-0.5 text-xs rounded bg-blue-900/30 text-blue-300" style={{ fontSize: '10px' }}>
                      🤖 AI Created
                    </span>
                  )}
                  {editingChain === chain.id ? (
                    <>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setEditingChain(null)
                        }}
                        className="p-1.5 bg-green-600 hover:bg-green-700 rounded cursor-button"
                        title="Save changes"
                      >
                        <Save className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setEditingChain(null)
                        }}
                        className="p-1.5 bg-gray-600 hover:bg-gray-700 rounded cursor-button"
                        title="Cancel editing"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setShowEditor(true)
                          setEditorChainId(chain.atom_id || chain.chain_id || chain.id)
                        }}
                        className="p-1.5 bg-blue-600 hover:bg-blue-700 rounded cursor-button"
                        title="Edit chain in visual editor"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      {chain.status === 'running' && (
                        <button className="p-1.5 bg-yellow-600 hover:bg-yellow-700 rounded cursor-button">
                          <Pause className="w-3.5 h-3.5" />
                        </button>
                      )}
                      {chain.status === 'paused' && (
                        <button className="p-1.5 bg-green-600 hover:bg-green-700 rounded cursor-button">
                          <Play className="w-3.5 h-3.5" />
                        </button>
                      )}
                      <button className="p-1.5 bg-red-600 hover:bg-red-700 rounded cursor-button" title="Delete chain (coming soon)">
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </>
                  )}
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-cursor-input-bg rounded-full h-1.5 mb-2">
                <div
                  className="bg-cursor-status-bar h-1.5 rounded-full transition-all duration-300"
                  style={{ width: `${(chain.currentStep / chain.steps.length) * 100}%` }}
                />
              </div>

              {/* Steps */}
              <div className="space-y-1.5">
                {chain.steps.map((step, index) => (
                  <div
                    key={step.id}
                    className={`flex items-center gap-2 p-2 rounded ${
                      index < chain.currentStep
                        ? 'bg-green-900/30 border border-green-700'
                        : index === chain.currentStep
                        ? 'bg-yellow-900/30 border border-yellow-700'
                        : 'bg-cursor-input-bg border border-cursor-border'
                    }`}
                  >
                    {/* Step Number */}
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold ${getStepStatusColor(step.status)}`}>
                      {index + 1}
                    </div>

                    {/* Step Info */}
                    <div className="flex-1">
                      <div className="flex items-center gap-1.5 mb-0.5">
                        <span className="font-semibold text-xs" style={{ fontSize: '12px' }}>{step.name}</span>
                        {step.confidence !== undefined && (
                          <span className={`text-xs px-1.5 py-0.5 rounded ${
                            step.confidence >= 0.90 ? 'bg-green-900/50 text-green-300' :
                            step.confidence >= 0.70 ? 'bg-yellow-900/50 text-yellow-300' :
                            'bg-red-900/50 text-red-300'
                          }`} style={{ fontSize: '10px' }}>
                            {(step.confidence * 100).toFixed(0)}% confidence
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-cursor-text-secondary">{step.description}</p>
                      {step.agentId && (
                        <span className="text-xs text-cursor-status-bar mt-0.5">Agent: {step.agentId}</span>
                      )}
                      {step.systemId && (
                        <span className="text-xs text-purple-400 mt-0.5">System: {step.systemId}</span>
                      )}
                      {step.duration && (
                        <span className="text-xs text-cursor-text-muted mt-0.5 ml-1">• {step.duration}ms</span>
                      )}
                    </div>

                    {/* Step Status */}
                    <div className={`text-xs px-1.5 py-0.5 rounded ${getStatusColor(step.status)}`} style={{ fontSize: '10px' }}>
                      {step.status.toUpperCase()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Visual Editor Modal */}
      {showEditor && (
        <div className="absolute inset-0 z-50 bg-cursor-bg border border-cursor-border">
          <PromptChainEditor
            chainId={editorChainId}
            onSave={(chain) => {
              setShowEditor(false)
              setEditorChainId(undefined)
              loadChains()
            }}
            onClose={() => {
              setShowEditor(false)
              setEditorChainId(undefined)
            }}
          />
        </div>
      )}
    </div>
  )
}

export default PromptChainsTab
