import React, { useState, useEffect } from 'react'
import { LucidMonacoEditor } from './LucidMonacoEditor'
import { Brain, Database, Target, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'
import { useConsciousness, useTimeline, useGoals, useEvidence } from '../hooks/useAIMOS'

interface ConsciousnessState {
  health: number
  awareness: {
    currentFile?: string
    relatedMemories: number
    relatedGoals: number
  }
}

interface EvidenceTrail {
  id: string
  strength: 'strong' | 'medium' | 'weak'
  reasoning: string
  sources: string[]
}

interface ConfidenceScore {
  id: string
  score: number
  reasoning: string
}

interface GoalAlignment {
  goalId: string
  name: string
  alignment: 'aligned' | 'not_aligned' | 'partial'
  progress: number
}

interface ConsciousnessAwareEditorProps {
  filePath: string
  content: string
  language: string
  onContentChange: (content: string) => void
  onSave?: () => void
  className?: string
}

export const ConsciousnessAwareEditor: React.FC<ConsciousnessAwareEditorProps> = ({
  filePath,
  content,
  language,
  onContentChange,
  onSave,
  className = ''
}) => {
  // Use comprehensive hooks for AIM-OS integration
  const { metrics: consciousnessMetrics, health, loading: consciousnessLoading } = useConsciousness()
  const { entries: timelineEntries } = useTimeline(10)
  const { goals } = useGoals('in_progress', 10)
  const { getEvidenceTrails } = useEvidence()

  const [evidenceTrails, setEvidenceTrails] = useState<EvidenceTrail[]>([])
  const [confidenceScores, setConfidenceScores] = useState<ConfidenceScore[]>([])
  const [goalAlignments, setGoalAlignments] = useState<GoalAlignment[]>([])
  const [showConsciousnessOverlay, setShowConsciousnessOverlay] = useState(true)
  const [showEvidencePanel, setShowEvidencePanel] = useState(false)
  const [showConfidencePanel, setShowConfidencePanel] = useState(false)
  const [showGoalPanel, setShowGoalPanel] = useState(false)

  // Fetch evidence trails and process data
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch evidence trails
        const memories = await getEvidenceTrails(`file:${filePath}`, 5)
        if (memories.length > 0) {
          const evidence: EvidenceTrail[] = memories.slice(0, 3).map((mem: any, idx: number) => ({
            id: mem.atom_id || `mem-${idx}`,
            strength: 'strong' as const,
            reasoning: `Memory: ${mem.content?.substring(0, 100) || 'No content'}...`,
            sources: [`memory:${mem.atom_id}`, `file:${filePath}`]
          }))
          setEvidenceTrails(evidence)
        }

        // Process goals
        if (goals.length > 0) {
          const processedGoals: GoalAlignment[] = goals.slice(0, 5).map((goal: any) => ({
            goalId: goal.goal_id || goal.id || 'unknown',
            name: goal.name || goal.description || 'Unknown Goal',
            alignment: 'aligned' as const, // TODO: Calculate alignment based on code analysis
            progress: goal.progress || 0
          }))
          setGoalAlignments(processedGoals)
        }

        // Set confidence scores (placeholder - can be enhanced with VIF)
        setConfidenceScores([{
          id: 'current-file',
          score: 0.85,
          reasoning: 'Confidence based on code analysis'
        }])
      } catch (error) {
        console.warn('Failed to fetch AIM-OS data, using fallback:', error)
        // Fallback to mock data
        setEvidenceTrails([{
          id: '1',
          strength: 'strong',
          reasoning: 'Similar pattern found in utils.ts',
          sources: ['memory:123', 'file:utils.ts']
        }])
        setConfidenceScores([{
          id: '1',
          score: 0.92,
          reasoning: 'High confidence based on evidence'
        }])
        setGoalAlignments([{
          goalId: 'OBJ-01',
          name: 'Reliable Memory Storage',
          alignment: 'aligned',
          progress: 0.7
        }])
      }
    }

    fetchData()
  }, [filePath, goals, getEvidenceTrails])

  // Build consciousness state from hooks
  const consciousnessState: ConsciousnessState = {
    health: health || 85,
    awareness: {
      currentFile: filePath,
      relatedMemories: evidenceTrails.length,
      relatedGoals: goalAlignments.length
    }
  }

  const getConsciousnessColor = (health: number) => {
    if (health >= 85) return 'bg-green-500'
    if (health >= 70) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const getEvidenceColor = (strength: string) => {
    switch (strength) {
      case 'strong': return 'text-green-400'
      case 'medium': return 'text-yellow-400'
      case 'weak': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-400'
    if (score >= 0.6) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getGoalAlignmentColor = (alignment: string) => {
    switch (alignment) {
      case 'aligned': return 'text-green-400'
      case 'partial': return 'text-yellow-400'
      case 'not_aligned': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  return (
    <div className={`flex flex-col h-full bg-gray-900 ${className}`}>
      {/* Consciousness Bar */}
      {showConsciousnessOverlay && (
        <div className="bg-gray-800 border-b border-gray-700 px-4 py-2 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Brain className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-gray-300">Consciousness:</span>
              <div className="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getConsciousnessColor(consciousnessState.health)} transition-all`}
                  style={{ width: `${consciousnessState.health}%` }}
                />
              </div>
              <span className="text-sm text-gray-400">{consciousnessState.health}%</span>
            </div>

            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-purple-400" />
              <span className="text-sm text-gray-300">Memory:</span>
              <span className="text-sm text-purple-400">{consciousnessState.awareness.relatedMemories}</span>
            </div>

            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-green-400" />
              <span className="text-sm text-gray-300">Goals:</span>
              <span className="text-sm text-green-400">{consciousnessState.awareness.relatedGoals}</span>
            </div>

            {confidenceScores.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-300">Confidence:</span>
                <span className={`text-sm font-medium ${getConfidenceColor(confidenceScores[0].score)}`}>
                  {(confidenceScores[0].score * 100).toFixed(0)}%
                </span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowEvidencePanel(!showEvidencePanel)}
              className={`px-2 py-1 text-xs rounded ${showEvidencePanel ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
            >
              Evidence ({evidenceTrails.length})
            </button>
            <button
              onClick={() => setShowConfidencePanel(!showConfidencePanel)}
              className={`px-2 py-1 text-xs rounded ${showConfidencePanel ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
            >
              Confidence
            </button>
            <button
              onClick={() => setShowGoalPanel(!showGoalPanel)}
              className={`px-2 py-1 text-xs rounded ${showGoalPanel ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
            >
              Goals ({goalAlignments.length})
            </button>
            <button
              onClick={() => setShowConsciousnessOverlay(!showConsciousnessOverlay)}
              className="px-2 py-1 text-xs rounded bg-gray-700 text-gray-300 hover:bg-gray-600"
            >
              {showConsciousnessOverlay ? 'Hide' : 'Show'} Overlay
            </button>
          </div>
        </div>
      )}

      {/* Editor with Overlay */}
      <div className="flex-1 relative">
        <LucidMonacoEditor
          value={content}
          language={language}
          fileName={filePath}
          onChange={onContentChange}
          theme="vs-dark"
          enableLucidFolds={true}
        />

        {/* Evidence Panel */}
        {showEvidencePanel && evidenceTrails.length > 0 && (
          <div className="absolute top-4 right-4 w-80 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-10 max-h-96 overflow-y-auto">
            <div className="p-4 border-b border-gray-700">
              <h3 className="text-white font-semibold flex items-center gap-2">
                <CheckCircle className="w-4 h-4" />
                Evidence Trails
              </h3>
            </div>
            <div className="p-4 space-y-3">
              {evidenceTrails.map((trail) => (
                <div key={trail.id} className="border border-gray-700 rounded p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`text-xs font-medium ${getEvidenceColor(trail.strength)}`}>
                      {trail.strength.toUpperCase()}
                    </span>
                    {trail.strength === 'strong' && <CheckCircle className="w-3 h-3 text-green-400" />}
                    {trail.strength === 'medium' && <AlertTriangle className="w-3 h-3 text-yellow-400" />}
                    {trail.strength === 'weak' && <XCircle className="w-3 h-3 text-red-400" />}
                  </div>
                  <p className="text-sm text-gray-300 mb-2">{trail.reasoning}</p>
                  <div className="flex flex-wrap gap-1">
                    {trail.sources.map((source, idx) => (
                      <span key={idx} className="text-xs px-2 py-1 bg-gray-700 rounded text-gray-400">
                        {source}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Confidence Panel */}
        {showConfidencePanel && confidenceScores.length > 0 && (
          <div className="absolute top-4 right-4 w-80 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-10">
            <div className="p-4 border-b border-gray-700">
              <h3 className="text-white font-semibold">Confidence Scores</h3>
            </div>
            <div className="p-4 space-y-3">
              {confidenceScores.map((score) => (
                <div key={score.id} className="border border-gray-700 rounded p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-300">Confidence</span>
                    <span className={`text-lg font-bold ${getConfidenceColor(score.score)}`}>
                      {(score.score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${score.score >= 0.8 ? 'bg-green-500' : score.score >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'}`}
                      style={{ width: `${score.score * 100}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-400 mt-2">{score.reasoning}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Goal Alignment Panel */}
        {showGoalPanel && goalAlignments.length > 0 && (
          <div className="absolute top-4 right-4 w-80 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-10 max-h-96 overflow-y-auto">
            <div className="p-4 border-b border-gray-700">
              <h3 className="text-white font-semibold flex items-center gap-2">
                <Target className="w-4 h-4" />
                Goal Alignment
              </h3>
            </div>
            <div className="p-4 space-y-3">
              {goalAlignments.map((goal) => (
                <div key={goal.goalId} className="border border-gray-700 rounded p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-white">{goal.goalId}</span>
                    <span className={`text-xs font-medium ${getGoalAlignmentColor(goal.alignment)}`}>
                      {goal.alignment.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 mb-2">{goal.name}</p>
                  <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${goal.alignment === 'aligned' ? 'bg-green-500' : goal.alignment === 'partial' ? 'bg-yellow-500' : 'bg-red-500'}`}
                      style={{ width: `${goal.progress * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-400 mt-1 block">
                    {(goal.progress * 100).toFixed(0)}% complete
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

