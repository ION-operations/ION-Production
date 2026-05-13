/**
 * Landing Page Component
 * 
 * Welcome screen for AIM-OS Dashboard
 * Shows status, helpful info, and entry point to dashboard
 * 
 * Created: 2025-01-27
 * Purpose: Better UX - no blank screens, clear errors, helpful guidance
 */

import React, { useState, useEffect } from 'react'
import { Sparkles, Bot, MessageSquare, Link, Wrench, Calendar, Tag, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react'

interface LandingPageProps {
  onEnterDashboard: () => void
  systemStatus?: {
    extensionLoaded: boolean
    reactUILoaded: boolean
    mcpToolsAvailable: boolean
    daemonConnected: boolean
    extensionCommandServer?: boolean
  }
}

export const LandingPage: React.FC<LandingPageProps> = ({ onEnterDashboard, systemStatus }) => {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Simulate loading check
    const timer = setTimeout(() => {
      setLoading(false)
      
      // Check for errors
      if (typeof window === 'undefined') {
        setError('Window object not available - webview may not be initialized')
      } else if (!document.getElementById('root')) {
        setError('Root element not found - HTML structure issue')
      }
    }, 500)

    return () => clearTimeout(timer)
  }, [])

  const tabs = [
    { id: 'agents', label: 'Agents', icon: Bot, description: 'Manage AI agents and their tasks' },
    { id: 'chat', label: 'Chat', icon: MessageSquare, description: 'Communicate with agents' },
    { id: 'chains', label: 'Chains', icon: Link, description: 'Visualize prompt chains' },
    { id: 'tools', label: 'Tools', icon: Wrench, description: 'MCP tools and integrations' },
    { id: 'timeline', label: 'Timeline', icon: Calendar, description: 'View activity timeline' },
    { id: 'nl-tags', label: 'NL Tags', icon: Tag, description: 'Natural language tags' }
  ]

  if (loading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-purple-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">Loading AIM-OS Dashboard...</h2>
          <p className="text-gray-400">Initializing systems</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-gradient-to-br from-red-900/20 via-gray-800 to-gray-900 p-8">
        <div className="max-w-2xl w-full bg-gray-800/90 border border-red-500/50 rounded-lg p-6 shadow-xl">
          <div className="flex items-center gap-3 mb-4">
            <AlertCircle className="w-8 h-8 text-red-500" />
            <h2 className="text-2xl font-bold text-white">Error Loading Dashboard</h2>
          </div>
          
          <div className="bg-red-900/20 border border-red-500/30 rounded p-4 mb-4">
            <p className="text-red-200 font-mono text-sm">{error}</p>
          </div>

          <div className="space-y-3 text-gray-300">
            <h3 className="font-semibold text-white">Troubleshooting Steps:</h3>
            <ol className="list-decimal list-inside space-y-2 ml-2">
              <li>Check Developer Console (Help → Toggle Developer Tools)</li>
              <li>Look for <code className="bg-gray-700 px-1 rounded">[AIM-OS]</code> messages</li>
              <li>Check Extension Host console for detailed errors</li>
              <li>Verify extension is installed (v1.2.0+)</li>
              <li>Try reloading the extension</li>
            </ol>
          </div>

          <button
            onClick={() => {
              setError(null)
              setLoading(true)
              setTimeout(() => {
                setLoading(false)
                onEnterDashboard()
              }, 500)
            }}
            className="mt-6 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen w-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 overflow-y-auto">
      {/* Header */}
      <div className="border-b border-gray-700 bg-gray-800/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-purple-500" />
            <div>
              <h1 className="text-2xl font-bold text-white">AIM-OS Dashboard</h1>
              <p className="text-sm text-gray-400">AI Consciousness Development Environment</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">Welcome to AIM-OS</h2>
          <p className="text-gray-400 text-lg">
            Your integrated dashboard for AI consciousness development, agent management, and MCP tools.
          </p>
        </div>

        {/* System Status */}
        {systemStatus && (
          <div className="mb-8 bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-500" />
              System Status
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <StatusItem
                label="Extension API"
                status={systemStatus.extensionCommandServer || false}
              />
              <StatusItem
                label="React UI"
                status={systemStatus.reactUILoaded}
              />
              <StatusItem
                label="MCP Tools"
                status={systemStatus.mcpToolsAvailable}
              />
              <StatusItem
                label="Daemon"
                status={systemStatus.daemonConnected}
              />
              <StatusItem
                label="Extension"
                status={systemStatus.extensionLoaded}
              />
            </div>
          </div>
        )}

        {/* Dashboard Features */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-white mb-4">Dashboard Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <div
                  key={tab.id}
                  className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 hover:border-purple-500/50 transition-colors cursor-pointer"
                  onClick={onEnterDashboard}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <Icon className="w-5 h-5 text-purple-500" />
                    <h4 className="font-semibold text-white">{tab.label}</h4>
                  </div>
                  <p className="text-sm text-gray-400">{tab.description}</p>
                </div>
              )
            })}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-purple-500/30 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Ready to Start?</h3>
          <p className="text-gray-300 mb-6">
            Enter the dashboard to access all features including agent management, chat, prompt chains, and more.
          </p>
          <button
            onClick={onEnterDashboard}
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold rounded-lg transition-all transform hover:scale-105 shadow-lg"
          >
            Enter Dashboard
          </button>
        </div>

        {/* Debug Info */}
        <div className="mt-8 bg-gray-800/30 border border-gray-700 rounded-lg p-4">
          <details className="cursor-pointer">
            <summary className="text-sm text-gray-400 hover:text-gray-300">
              Debug Information
            </summary>
            <div className="mt-4 space-y-2 text-xs font-mono text-gray-500">
              <div>Extension Version: 1.2.0</div>
              <div>React UI: Loaded</div>
              <div>Document Ready: {document.readyState}</div>
              <div>Window Location: {window.location.href.substring(0, 50)}...</div>
              <div>Root Element: {document.getElementById('root') ? 'Found' : 'Not Found'}</div>
            </div>
          </details>
        </div>
      </div>
    </div>
  )
}

interface StatusItemProps {
  label: string
  status: boolean
}

const StatusItem: React.FC<StatusItemProps> = ({ label, status }) => (
  <div className="flex items-center gap-2">
    {status ? (
      <CheckCircle2 className="w-4 h-4 text-green-500" />
    ) : (
      <AlertCircle className="w-4 h-4 text-yellow-500" />
    )}
    <span className="text-sm text-gray-300">{label}</span>
  </div>
)

