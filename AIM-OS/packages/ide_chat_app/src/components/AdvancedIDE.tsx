/**
 * Advanced IDE Component
 * Integrates all advanced IDE features including code intelligence, collaboration, and AI assistance
 */

import React, { useState, useEffect, useRef } from 'react'
import { 
  Code, 
  Users, 
  Brain, 
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Lightbulb,
  Workflow,
  Bot
} from 'lucide-react'
import { codeIntelligence, CodeAnalysis } from '../lib/code-intelligence'
import { collaborationEngine, CollaborationSession, AISuggestion } from '../lib/collaboration-engine'
import { aimosClient } from '../lib/aimos-client'

interface AdvancedIDEProps {
  className?: string
}

interface IDEState {
  currentFile: string
  currentContent: string
  analysis: CodeAnalysis | null
  collaborationSession: CollaborationSession | null
  aiSuggestions: AISuggestion[]
  isAnalyzing: boolean
  isCollaborating: boolean
  showCodeIntelligence: boolean
  showCollaboration: boolean
  showAIAssistance: boolean
  activeTab: 'code' | 'analysis' | 'collaboration' | 'ai' | 'workflow'
}

export const AdvancedIDE: React.FC<AdvancedIDEProps> = ({ className = '' }) => {
  const [state, setState] = useState<IDEState>({
    currentFile: 'main.tsx',
    currentContent: `import React from 'react'

interface ComponentProps {
  title: string
  children: React.ReactNode
}

export const MyComponent: React.FC<ComponentProps> = ({ title, children }) => {
  const [count, setCount] = useState(0)
  
  const handleClick = () => {
    setCount(count + 1)
  }
  
  return (
    <div className="component">
      <h1>{title}</h1>
      <button onClick={handleClick}>
        Count: {count}
      </button>
      {children}
    </div>
  )
}`,
    analysis: null,
    collaborationSession: null,
    aiSuggestions: [],
    isAnalyzing: false,
    isCollaborating: false,
    showCodeIntelligence: true,
    showCollaboration: false,
    showAIAssistance: true,
    activeTab: 'code'
  })

  const editorRef = useRef<HTMLTextAreaElement>(null)
  const analysisIntervalRef = useRef<NodeJS.Timeout | null>(null)

  // Initialize collaboration session
  useEffect(() => {
    const session = collaborationEngine.createSession(
      'Advanced IDE Session',
      'user-1',
      'Braden'
    )
    
    // Add AI agents to the session
    collaborationEngine.joinSession(session.id, 'coding-agent', 'CodeMaster', 'ai_agent')
    collaborationEngine.joinSession(session.id, 'planning-agent', 'StrategyMind', 'ai_agent')
    
    setState(prev => ({
      ...prev,
      collaborationSession: session,
      isCollaborating: true
    }))

    // Add document to collaboration session
    collaborationEngine.addDocument(
      session.id,
      'main-tsx',
      state.currentFile,
      state.currentContent,
      'user-1'
    )

    return () => {
      if (analysisIntervalRef.current) {
        clearInterval(analysisIntervalRef.current)
      }
    }
  }, [])

  // Auto-analyze code when content changes
  useEffect(() => {
    if (analysisIntervalRef.current) {
      clearInterval(analysisIntervalRef.current)
    }

    analysisIntervalRef.current = setTimeout(async () => {
      await analyzeCode()
    }, 1000) // Debounce analysis

    return () => {
      if (analysisIntervalRef.current) {
        clearInterval(analysisIntervalRef.current)
      }
    }
  }, [state.currentContent])

  const analyzeCode = async () => {
    if (state.isAnalyzing) return

    setState(prev => ({ ...prev, isAnalyzing: true }))

    try {
      const analysis = await codeIntelligence.analyzeCode(
        state.currentContent,
        state.currentFile,
        'typescript'
      )

      setState(prev => ({ ...prev, analysis, isAnalyzing: false }))

      // Store analysis in AIM-OS
      await aimosClient.storeMemory(
        `Code analysis completed for ${state.currentFile}`,
        { 
          'code_analysis': 1.0, 
          'file_type': 0.8, 
          'complexity': analysis.metrics.cyclomaticComplexity / 100 
        }
      )
    } catch (error) {
      console.error('Code analysis failed:', error)
      setState(prev => ({ ...prev, isAnalyzing: false }))
    }
  }

  const handleContentChange = (newContent: string) => {
    setState(prev => ({ ...prev, currentContent: newContent }))

    // Update collaboration session
    if (state.collaborationSession) {
      const changes = [{
        id: `change_${Date.now()}`,
        documentId: 'main-tsx',
        participantId: 'user-1',
        type: 'replace' as const,
        position: 0,
        length: state.currentContent.length,
        text: newContent,
        timestamp: new Date(),
        version: 1,
        applied: true
      }]

      collaborationEngine.updateDocument(
        state.collaborationSession.id,
        'main-tsx',
        changes,
        'user-1'
      )
    }
  }

  const handleAISuggestionAccept = async (suggestionId: string) => {
    if (state.collaborationSession) {
      const success = collaborationEngine.acceptAISuggestion(
        state.collaborationSession.id,
        suggestionId,
        'user-1'
      )

      if (success) {
        setState(prev => ({
          ...prev,
          aiSuggestions: prev.aiSuggestions.filter(s => s.id !== suggestionId)
        }))
      }
    }
  }

  const handleAISuggestionReject = async (suggestionId: string) => {
    if (state.collaborationSession) {
      const success = collaborationEngine.rejectAISuggestion(
        state.collaborationSession.id,
        suggestionId,
        'user-1'
      )

      if (success) {
        setState(prev => ({
          ...prev,
          aiSuggestions: prev.aiSuggestions.filter(s => s.id !== suggestionId)
        }))
      }
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-500'
      case 'high': return 'text-orange-500'
      case 'medium': return 'text-yellow-500'
      case 'low': return 'text-blue-500'
      default: return 'text-gray-500'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <AlertCircle className="w-4 h-4" />
      case 'high': return <AlertCircle className="w-4 h-4" />
      case 'medium': return <AlertCircle className="w-4 h-4" />
      case 'low': return <CheckCircle className="w-4 h-4" />
      default: return <CheckCircle className="w-4 h-4" />
    }
  }

  const renderCodeEditor = () => (
    <div className="flex-1 flex flex-col">
      <div className="flex items-center justify-between p-3 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <Code className="w-5 h-5 text-blue-400" />
          <span className="text-sm font-medium text-white">{state.currentFile}</span>
          {state.isAnalyzing && (
            <RefreshCw className="w-4 h-4 animate-spin text-blue-400" />
          )}
        </div>
        <div className="flex items-center gap-2">
          {state.analysis && (
            <div className="flex items-center gap-1 text-xs text-gray-400">
              <span>Complexity: {state.analysis.metrics.cyclomaticComplexity}</span>
              <span>•</span>
              <span>Issues: {state.analysis.issues.length}</span>
              <span>•</span>
              <span>Suggestions: {state.analysis.suggestions.length}</span>
            </div>
          )}
        </div>
      </div>
      
      <div className="flex-1 relative">
        <textarea
          ref={editorRef}
          value={state.currentContent}
          onChange={(e) => handleContentChange(e.target.value)}
          className="w-full h-full p-4 bg-gray-900 text-white font-mono text-sm resize-none focus:outline-none"
          placeholder="Start typing your code..."
          spellCheck={false}
        />
        
        {/* Line numbers */}
        <div className="absolute left-0 top-0 bottom-0 w-12 bg-gray-800 border-r border-gray-700 text-gray-500 text-xs font-mono p-4 select-none">
          {state.currentContent.split('\n').map((_, index) => (
            <div key={index} className="leading-6">
              {index + 1}
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  const renderCodeIntelligence = () => (
    <div className="w-80 bg-gray-800 border-l border-gray-700 flex flex-col">
      <div className="p-3 border-b border-gray-700">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <Brain className="w-4 h-4 text-purple-400" />
          Code Intelligence
        </h3>
      </div>
      
      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {state.analysis ? (
          <>
            {/* Metrics */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-gray-400 uppercase">Metrics</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-gray-700 p-2 rounded">
                  <div className="text-gray-400">Lines of Code</div>
                  <div className="text-white font-semibold">{state.analysis.metrics.linesOfCode}</div>
                </div>
                <div className="bg-gray-700 p-2 rounded">
                  <div className="text-gray-400">Complexity</div>
                  <div className="text-white font-semibold">{state.analysis.metrics.cyclomaticComplexity}</div>
                </div>
                <div className="bg-gray-700 p-2 rounded">
                  <div className="text-gray-400">Maintainability</div>
                  <div className="text-white font-semibold">{state.analysis.metrics.maintainabilityIndex.toFixed(1)}</div>
                </div>
                <div className="bg-gray-700 p-2 rounded">
                  <div className="text-gray-400">Test Coverage</div>
                  <div className="text-white font-semibold">{state.analysis.metrics.testCoverage.toFixed(1)}%</div>
                </div>
              </div>
            </div>

            {/* Issues */}
            {state.analysis.issues.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-gray-400 uppercase">Issues</h4>
                <div className="space-y-2">
                  {state.analysis.issues.slice(0, 5).map((issue) => (
                    <div key={issue.id} className="bg-gray-700 p-2 rounded text-xs">
                      <div className="flex items-center gap-2 mb-1">
                        {getSeverityIcon(issue.severity)}
                        <span className={`font-semibold ${getSeverityColor(issue.severity)}`}>
                          {issue.severity.toUpperCase()}
                        </span>
                        <span className="text-gray-400">Line {issue.line}</span>
                      </div>
                      <div className="text-gray-300">{issue.message}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Suggestions */}
            {state.analysis.suggestions.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-gray-400 uppercase">Suggestions</h4>
                <div className="space-y-2">
                  {state.analysis.suggestions.slice(0, 3).map((suggestion) => (
                    <div key={suggestion.id} className="bg-gray-700 p-2 rounded text-xs">
                      <div className="flex items-center gap-2 mb-1">
                        <Lightbulb className="w-4 h-4 text-yellow-400" />
                        <span className="font-semibold text-yellow-400">
                          {suggestion.type.toUpperCase()}
                        </span>
                        <span className="text-gray-400">Line {suggestion.line}</span>
                      </div>
                      <div className="text-gray-300">{suggestion.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="text-center text-gray-400 text-sm py-8">
            {state.isAnalyzing ? 'Analyzing code...' : 'No analysis available'}
          </div>
        )}
      </div>
    </div>
  )

  const renderCollaboration = () => (
    <div className="w-80 bg-gray-800 border-l border-gray-700 flex flex-col">
      <div className="p-3 border-b border-gray-700">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <Users className="w-4 h-4 text-green-400" />
          Collaboration
        </h3>
      </div>
      
      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {state.collaborationSession ? (
          <>
            {/* Participants */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-gray-400 uppercase">Participants</h4>
              <div className="space-y-2">
                {state.collaborationSession.participants.map((participant) => (
                  <div key={participant.id} className="flex items-center gap-2 text-sm">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: participant.color }}
                    />
                    <span className="text-white">{participant.name}</span>
                    <span className="text-gray-400">({participant.role})</span>
                    {participant.isOnline && (
                      <div className="w-2 h-2 bg-green-500 rounded-full" />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* AI Suggestions */}
            {state.aiSuggestions.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-gray-400 uppercase">AI Suggestions</h4>
                <div className="space-y-2">
                  {state.aiSuggestions.map((suggestion) => (
                    <div key={suggestion.id} className="bg-gray-700 p-2 rounded text-xs">
                      <div className="flex items-center gap-2 mb-1">
                        <Bot className="w-4 h-4 text-blue-400" />
                        <span className="font-semibold text-blue-400">
                          {suggestion.type.toUpperCase()}
                        </span>
                        <span className="text-gray-400">
                          {Math.round(suggestion.confidence * 100)}%
                        </span>
                      </div>
                      <div className="text-gray-300 mb-2">{suggestion.description}</div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleAISuggestionAccept(suggestion.id)}
                          className="px-2 py-1 bg-green-600 hover:bg-green-700 text-white text-xs rounded"
                        >
                          Accept
                        </button>
                        <button
                          onClick={() => handleAISuggestionReject(suggestion.id)}
                          className="px-2 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded"
                        >
                          Reject
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="text-center text-gray-400 text-sm py-8">
            No collaboration session
          </div>
        )}
      </div>
    </div>
  )

  const renderTabBar = () => (
    <div className="flex border-b border-gray-700">
      {[
        { id: 'code', label: 'Code', icon: Code },
        { id: 'analysis', label: 'Analysis', icon: Brain },
        { id: 'collaboration', label: 'Collaboration', icon: Users },
        { id: 'ai', label: 'AI Assistant', icon: Bot },
        { id: 'workflow', label: 'Workflow', icon: Workflow }
      ].map((tab) => (
        <button
          key={tab.id}
          onClick={() => setState(prev => ({ ...prev, activeTab: tab.id as any }))}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            state.activeTab === tab.id
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-gray-400 hover:text-white'
          }`}
        >
          <tab.icon className="w-4 h-4" />
          {tab.label}
        </button>
      ))}
    </div>
  )

  const renderMainContent = () => {
    switch (state.activeTab) {
      case 'code':
        return (
          <div className="flex flex-1">
            {renderCodeEditor()}
            {state.showCodeIntelligence && renderCodeIntelligence()}
          </div>
        )
      case 'analysis':
        return (
          <div className="flex-1 p-6">
            <div className="text-center text-gray-400">
              <Brain className="w-16 h-16 mx-auto mb-4 text-purple-400" />
              <h2 className="text-xl font-semibold mb-2">Code Analysis</h2>
              <p>Detailed code analysis and metrics will be displayed here</p>
            </div>
          </div>
        )
      case 'collaboration':
        return (
          <div className="flex flex-1">
            <div className="flex-1 p-6">
              <div className="text-center text-gray-400">
                <Users className="w-16 h-16 mx-auto mb-4 text-green-400" />
                <h2 className="text-xl font-semibold mb-2">Real-time Collaboration</h2>
                <p>Collaborate with team members and AI agents in real-time</p>
              </div>
            </div>
            {renderCollaboration()}
          </div>
        )
      case 'ai':
        return (
          <div className="flex-1 p-6">
            <div className="text-center text-gray-400">
              <Bot className="w-16 h-16 mx-auto mb-4 text-blue-400" />
              <h2 className="text-xl font-semibold mb-2">AI Assistant</h2>
              <p>Get intelligent assistance from AI agents</p>
            </div>
          </div>
        )
      case 'workflow':
        return (
          <div className="flex-1 p-6">
            <div className="text-center text-gray-400">
              <Workflow className="w-16 h-16 mx-auto mb-4 text-orange-400" />
              <h2 className="text-xl font-semibold mb-2">Workflow Automation</h2>
              <p>Automate your development workflow with intelligent agents</p>
            </div>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className={`h-full flex flex-col bg-gray-900 text-white ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold text-white">Advanced IDE</h1>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span>Online</span>
            </div>
            {state.collaborationSession && (
              <div className="flex items-center gap-1">
                <Users className="w-4 h-4" />
                <span>{state.collaborationSession.participants.length} participants</span>
              </div>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setState(prev => ({ ...prev, showCodeIntelligence: !prev.showCodeIntelligence }))}
            className={`p-2 rounded ${state.showCodeIntelligence ? 'bg-blue-600' : 'bg-gray-700'} hover:bg-blue-700`}
            title="Toggle Code Intelligence"
          >
            <Brain className="w-4 h-4" />
          </button>
          <button
            onClick={() => setState(prev => ({ ...prev, showCollaboration: !prev.showCollaboration }))}
            className={`p-2 rounded ${state.showCollaboration ? 'bg-green-600' : 'bg-gray-700'} hover:bg-green-700`}
            title="Toggle Collaboration"
          >
            <Users className="w-4 h-4" />
          </button>
          <button
            onClick={() => setState(prev => ({ ...prev, showAIAssistance: !prev.showAIAssistance }))}
            className={`p-2 rounded ${state.showAIAssistance ? 'bg-purple-600' : 'bg-gray-700'} hover:bg-purple-700`}
            title="Toggle AI Assistance"
          >
            <Bot className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Tab Bar */}
      {renderTabBar()}

      {/* Main Content */}
      {renderMainContent()}
    </div>
  )
}
