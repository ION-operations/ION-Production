/**
 * Advanced Chat Panel
 * Full integration with Lucid Chat backend services (AdvancedLLMService, APOE, etc.)
 */

import React, { useState, useEffect } from 'react'
import {
  Brain,
  Search,
  GitBranch,
  Zap,
  Settings,
  DollarSign,
  Clock,
  TrendingUp,
  AlertCircle,
} from 'lucide-react'
import { AdvancedChatInterface } from './chat/AdvancedChatInterface'
import { AdvancedLLMService } from '../../services/lucid-chat/llm/AdvancedLLMService'
import { useAdvancedLLMStore } from '../../store/lucid-chat/advancedLLMStore'
import type {
  ThinkingMode,
  OutputFormat,
  OutputStyle,
  OutputTone,
  AdvancedLLMRequest,
} from '../../services/lucid-chat/llm/AdvancedLLMService'
import {
  IntegrationTagContext,
  setActiveIntegrationContext
} from '../../utils/integrationTags'

export const AdvancedChatPanel: React.FC = () => {
  const store = useAdvancedLLMStore()
  const [error, setError] = useState<string | null>(null)
  const [showSettings, setShowSettings] = useState(false)

  // Initialize AdvancedLLMService
  const advancedLLMService = new AdvancedLLMService('http://localhost:5001')

  const handleSend = async (message: string) => {
    if (!message.trim()) {
      setError('Please enter a message')
      return
    }

    setError(null)

    // Add user message
    store.addMessage({
      role: 'user',
      content: message,
      timestamp: new Date(),
    })

    store.setInput('')
    store.setStreaming(true)
    store.setStreamingMessage('')
    store.setStreamingProtocol(undefined)

    try {
      const integrationContext: IntegrationTagContext = {
        system: {
          name: store.apoeEnabled ? 'apoe' : 'advanced_llm',
          priority: store.apoeEnabled ? 'p0' : 'routine'
        },
        integrationType: store.apoeEnabled ? 'plan_execution' : 'chat_completion',
        connection: store.apoeEnabled ? 'chat->apoe' : 'chat->llm',
        modality: store.deepSearchEnabled ? 'text+code' : 'text',
        action: store.deepSearchEnabled ? 'research_chat' : 'chat_message',
        mode: store.thinkingMode,
        agent: store.apoeEnabled ? 'planning' : 'coding',
        extras: [
          store.deepSearchEnabled ? 'deep_search' : undefined,
          store.branchReasoningEnabled ? 'branch_reasoning' : undefined
        ].filter(Boolean) as string[]
      }
      setActiveIntegrationContext(integrationContext)

      // Build AdvancedLLMRequest
      const request: AdvancedLLMRequest = {
        provider: store.provider,
        model: store.model,
        messages: [
          ...store.messages.map((m) => ({
            role: m.role as 'system' | 'user' | 'assistant',
            content: m.content,
          })),
          {
            role: 'user',
            content: message,
          },
        ],
        temperature: 0.7,
        maxTokens: 2000,
        stream: false, // TODO: Implement streaming

        // Thinking mode
        thinkingMode: {
          mode: store.thinkingMode,
        },

        // Deep search
        deepSearch: store.deepSearchEnabled
          ? store.deepSearchConfig
          : undefined,

        // Branch reasoning (auto-enabled for analytical/reasoning modes)
        // Will be handled by AdvancedLLMService

        // APOE
        apoe: store.apoeEnabled
          ? {
              useAPOE: true,
              orchestrationStrategy: 'adaptive',
              budget: store.budgetLimit,
            }
          : undefined,

        // Output format
        promptConfig: {
          outputFormat: store.outputFormat,
          outputStyle: store.outputStyle,
          outputTone: store.outputTone,
          enableDiagrams: true,
          enableMath: true,
          enableTables: true,
        },
        integrationContext
      }

      // Call AdvancedLLMService
      const response = await advancedLLMService.advancedChatCompletion(request)

      if (!response.success || !response.data) {
        setError(response.error || 'Failed to get response')
        store.setStreaming(false)
        return
      }

      // Add assistant message
      store.addMessage({
        role: 'assistant',
        content: response.data.text,
        timestamp: new Date(),
        outputProtocol: response.data.outputProtocol,
        aimos: response.data.aimos,
        reasoning: response.data.reasoning,
        sources: response.data.sources,
        tokensUsed: response.data.tokensUsed,
        latencyMs: response.data.latencyMs,
      })

      // Update budget
      if (response.data.tokensUsed) {
        store.updateBudget({
          tokens: store.budget.tokens + response.data.tokensUsed,
          cost: store.budget.cost + (response.data.tokensUsed * 0.00001), // Rough estimate
        })
      }

      store.setStreaming(false)
      store.setStreamingMessage('')
      store.setStreamingProtocol(undefined)
    } catch (err: any) {
      setError(err.message || 'An error occurred')
      store.setStreaming(false)
    }
  }

  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Header with Controls */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-800 bg-gray-900">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold text-gray-200">Lucid Chat</h2>
          <div className="flex items-center gap-1 text-xs">
            {store.thinkingMode && (
              <div className="flex items-center gap-1 px-2 py-0.5 bg-blue-900/30 rounded text-blue-400">
                <Brain className="w-3 h-3" />
                <span className="capitalize">{store.thinkingMode}</span>
              </div>
            )}
            {store.deepSearchEnabled && (
              <div className="flex items-center gap-1 px-2 py-0.5 bg-purple-900/30 rounded text-purple-400">
                <Search className="w-3 h-3" />
                <span>Deep Search</span>
              </div>
            )}
            {store.branchReasoningEnabled && (
              <div className="flex items-center gap-1 px-2 py-0.5 bg-yellow-900/30 rounded text-yellow-400">
                <GitBranch className="w-3 h-3" />
                <span>Branch</span>
              </div>
            )}
            {store.apoeEnabled && (
              <div className="flex items-center gap-1 px-2 py-0.5 bg-green-900/30 rounded text-green-400">
                <Zap className="w-3 h-3" />
                <span>APOE</span>
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {/* Budget Display */}
          <div className="flex items-center gap-1 text-xs text-gray-400">
            <DollarSign className="w-3 h-3" />
            <span>${store.budget.cost.toFixed(2)}</span>
          </div>
          <div className="flex items-center gap-1 text-xs text-gray-400">
            <TrendingUp className="w-3 h-3" />
            <span>{store.budget.tokens.toLocaleString()} tokens</span>
          </div>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-1.5 text-gray-400 hover:text-gray-300 transition-colors"
            title="Settings"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="px-4 py-3 border-b border-gray-800 bg-gray-900 space-y-3">
          {/* Thinking Mode */}
          <div>
            <label className="text-xs font-medium text-gray-400 mb-1 block">
              Thinking Mode
            </label>
            <select
              value={store.thinkingMode}
              onChange={(e) => store.setThinkingMode(e.target.value as ThinkingMode)}
              className="w-full px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-sm text-gray-200"
            >
              <option value="creative">Creative</option>
              <option value="analytical">Analytical</option>
              <option value="balanced">Balanced</option>
              <option value="reasoning">Reasoning</option>
              <option value="intuitive">Intuitive</option>
            </select>
          </div>

          {/* Deep Search */}
          <div className="flex items-center justify-between">
            <label className="text-xs font-medium text-gray-400">
              Deep Search
            </label>
            <input
              type="checkbox"
              checked={store.deepSearchEnabled}
              onChange={(e) => store.setDeepSearchEnabled(e.target.checked)}
              className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-700 rounded"
            />
          </div>

          {/* Branch Reasoning */}
          <div className="flex items-center justify-between">
            <label className="text-xs font-medium text-gray-400">
              Branch Reasoning
            </label>
            <input
              type="checkbox"
              checked={store.branchReasoningEnabled}
              onChange={(e) => store.setBranchReasoningEnabled(e.target.checked)}
              className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-700 rounded"
            />
          </div>

          {/* APOE */}
          <div className="flex items-center justify-between">
            <label className="text-xs font-medium text-gray-400">APOE</label>
            <input
              type="checkbox"
              checked={store.apoeEnabled}
              onChange={(e) => store.setAPOEEnabled(e.target.checked)}
              className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-700 rounded"
            />
          </div>

          {/* Output Format */}
          <div>
            <label className="text-xs font-medium text-gray-400 mb-1 block">
              Output Format
            </label>
            <select
              value={store.outputFormat}
              onChange={(e) => store.setOutputFormat(e.target.value as OutputFormat)}
              className="w-full px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-sm text-gray-200"
            >
              <option value="markdown">Markdown</option>
              <option value="code">Code</option>
              <option value="json">JSON</option>
              <option value="table">Table</option>
              <option value="diagram">Diagram</option>
              <option value="mixed">Mixed</option>
            </select>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="px-4 py-2 bg-red-900/20 border-b border-red-700/50">
          <div className="flex items-center gap-2 text-sm text-red-300">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Chat Interface */}
      <div className="flex-1 overflow-hidden">
        <AdvancedChatInterface
          messages={store.messages}
          streamingMessage={store.streamingMessage}
          streamingProtocol={store.streamingProtocol}
          isStreaming={store.isStreaming}
          onSend={handleSend}
          input={store.input}
          onInputChange={store.setInput}
          placeholder="Ask me anything with advanced AI capabilities..."
          maxLength={4000}
          disabled={store.isStreaming}
          thinkingMode={store.thinkingMode}
          deepSearchEnabled={store.deepSearchEnabled}
          branchReasoningEnabled={store.branchReasoningEnabled}
          apoeEnabled={store.apoeEnabled}
        />
      </div>
    </div>
  )
}

