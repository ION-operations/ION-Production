// Code Editor Panel (Monaco + VIF + SEG) - Enhanced with Consciousness-Aware Features
import React, { useState, useEffect, useRef } from 'react'
import Editor from '@monaco-editor/react'
import { Brain, AlertTriangle, CheckCircle, ChevronDown, ChevronUp, Play, Pause, RotateCcw } from 'lucide-react'
import { useAIMOS } from '@/hooks/useAIMOS'
import { Panel } from '@/types'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

interface CodeEditorProps {
  panel: Panel
}

const sampleCode = `// Welcome to AIM-OS IDE! 🚀
import { useState, useEffect } from 'react'
import { useCMC, useVIF } from '@/hooks/useAIMOS'

export const Example: React.FC = () => {
  const [count, setCount] = useState(0)
  const { retrieveAtoms } = useCMC()
  const { trackConfidence } = useVIF()
  
  useEffect(() => {
    console.log('Component mounted')
    // VIF confidence tracking
    trackConfidence('Example component', 0.85, ['atom_123'], 'High confidence')
  }, [])
  
  return (
    <div className="example">
      <h1>Count: {count}</h1>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  )
}`

export const CodeEditor: React.FC<CodeEditorProps> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const { cmc, vif, seg, tcs, isLoading, error, isConnected } = useAIMOS()
  const [code, setCode] = useState(sampleCode)
  const [showEvidenceTrail, setShowEvidenceTrail] = useState(false)
  const [showConfidencePanel, setShowConfidencePanel] = useState(false)
  const [relatedMemories, setRelatedMemories] = useState<any[]>([])
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTimelineIndex, setCurrentTimelineIndex] = useState(0)

  useEffect(() => {
    const handleTogglePanel = (e: CustomEvent) => {
      if (e.detail.panelId === panel.id) {
        togglePanelVisibility(panel.id)
      }
    }
    window.addEventListener('togglePanel', handleTogglePanel as EventListener)
    return () => {
      window.removeEventListener('togglePanel', handleTogglePanel as EventListener)
    }
  }, [panel.id, togglePanelVisibility])

  // Load related memories when code changes
  useEffect(() => {
    const loadRelatedMemories = async () => {
      if (code.length > 10) {
        const memories = await cmc.retrieveAtoms(code.substring(0, 50))
        setRelatedMemories(memories.slice(0, 5))
      }
    }
    loadRelatedMemories()
  }, [code, cmc])

  const contradictions = seg.detectContradictions(code)
  const confidence = vif.getConfidence('Code Editor')
  const witnesses = vif.getWitnesses('Code Editor')
  const stats = cmc.getStats()

  // Consciousness health calculation
  const consciousnessHealth = isConnected ? 0.85 : 0.65
  const memoryAwareness = relatedMemories.length
  const goalAlignment = 0.8 // Mock for now

  const headerActions = (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      {/* Consciousness Health Indicator */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          padding: '2px 6px',
          backgroundColor: '#374151',
          borderRadius: '4px',
          fontSize: '10px',
        }}
        title={`Consciousness Health: ${(consciousnessHealth * 100).toFixed(0)}%`}
      >
        <Brain size={12} style={{ color: consciousnessHealth > 0.8 ? '#10B981' : consciousnessHealth > 0.6 ? '#F59E0B' : '#EF4444' }} />
        <span style={{ color: '#9CA3AF' }}>{(consciousnessHealth * 100).toFixed(0)}%</span>
      </div>
      {confidence && (
        <span style={{ fontSize: '11px', color: confidence.confidence > 0.8 ? '#10B981' : confidence.confidence > 0.6 ? '#F59E0B' : '#EF4444' }}>
          {(confidence.confidence * 100).toFixed(0)}%
        </span>
      )}
      {contradictions.length > 0 && (
        <span style={{ fontSize: '11px', color: '#EF4444' }}>⚠️ {contradictions.length}</span>
      )}
    </div>
  )

  return (
    <BasePanel panel={panel} headerActions={headerActions} isLoading={isLoading} error={error || null}>
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Consciousness Health Bar */}
        <div style={{ padding: '8px 12px', backgroundColor: '#111827', borderBottom: '1px solid #374151', display: 'flex', alignItems: 'center', gap: '12px', fontSize: '11px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ color: '#9CA3AF' }}>Memory:</span>
            <span style={{ color: '#3B82F6', fontWeight: 'bold' }}>{memoryAwareness} related</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ color: '#9CA3AF' }}>Goals:</span>
            <span style={{ color: goalAlignment > 0.7 ? '#10B981' : '#F59E0B', fontWeight: 'bold' }}>
              {(goalAlignment * 100).toFixed(0)}% aligned
            </span>
          </div>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px' }}>
            <button
              onClick={() => setShowEvidenceTrail(!showEvidenceTrail)}
              style={{
                padding: '4px 8px',
                fontSize: '10px',
                backgroundColor: showEvidenceTrail ? '#374151' : 'transparent',
                border: '1px solid #374151',
                borderRadius: '4px',
                color: '#F9FAFB',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              Evidence {showEvidenceTrail ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
            </button>
            <button
              onClick={() => setShowConfidencePanel(!showConfidencePanel)}
              style={{
                padding: '4px 8px',
                fontSize: '10px',
                backgroundColor: showConfidencePanel ? '#374151' : 'transparent',
                border: '1px solid #374151',
                borderRadius: '4px',
                color: '#F9FAFB',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              Confidence {showConfidencePanel ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
            </button>
          </div>
        </div>

        {/* Evidence Trail Panel */}
        {showEvidenceTrail && (
          <div style={{ padding: '12px', backgroundColor: '#111827', borderBottom: '1px solid #374151', maxHeight: '150px', overflow: 'auto' }}>
            <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '8px', color: '#F9FAFB' }}>Evidence Trail</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {relatedMemories.length > 0 ? (
                relatedMemories.map((memory, index) => (
                  <div
                    key={memory.id || index}
                    style={{
                      padding: '6px',
                      backgroundColor: '#1F2937',
                      borderRadius: '4px',
                      fontSize: '11px',
                      color: '#D1D5DB',
                    }}
                  >
                    <div style={{ fontWeight: 'bold', marginBottom: '2px' }}>{memory.id}</div>
                    <div style={{ fontSize: '10px', color: '#9CA3AF' }}>{memory.content?.substring(0, 80)}...</div>
                  </div>
                ))
              ) : (
                <div style={{ fontSize: '11px', color: '#9CA3AF', fontStyle: 'italic' }}>No related evidence found</div>
              )}
            </div>
          </div>
        )}

        {/* Confidence Scores Panel */}
        {showConfidencePanel && (
          <div style={{ padding: '12px', backgroundColor: '#111827', borderBottom: '1px solid #374151', maxHeight: '150px', overflow: 'auto' }}>
            <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '8px', color: '#F9FAFB' }}>Confidence Scores</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {confidence ? (
                <div style={{ padding: '6px', backgroundColor: '#1F2937', borderRadius: '4px', fontSize: '11px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ color: '#D1D5DB' }}>Code Editor</span>
                    <span style={{ color: confidence.confidence > 0.8 ? '#10B981' : confidence.confidence > 0.6 ? '#F59E0B' : '#EF4444', fontWeight: 'bold' }}>
                      {(confidence.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  {confidence.reasoning && (
                    <div style={{ fontSize: '10px', color: '#9CA3AF', marginTop: '4px' }}>{confidence.reasoning}</div>
                  )}
                </div>
              ) : (
                <div style={{ fontSize: '11px', color: '#9CA3AF', fontStyle: 'italic' }}>No confidence data available</div>
              )}
              {witnesses.length > 0 && (
                <div style={{ fontSize: '10px', color: '#9CA3AF', marginTop: '4px' }}>
                  {witnesses.length} witness(es) available
                </div>
              )}
            </div>
          </div>
        )}

        {/* Temporal Navigation Bar */}
        <div style={{ padding: '6px 12px', backgroundColor: '#111827', borderBottom: '1px solid #374151', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '10px' }}>
          <span style={{ color: '#9CA3AF' }}>Timeline:</span>
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            style={{
              padding: '4px 6px',
              backgroundColor: '#374151',
              border: 'none',
              borderRadius: '4px',
              color: '#F9FAFB',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            {isPlaying ? <Pause size={12} /> : <Play size={12} />}
          </button>
          <button
            onClick={() => setCurrentTimelineIndex(0)}
            style={{
              padding: '4px 6px',
              backgroundColor: '#374151',
              border: 'none',
              borderRadius: '4px',
              color: '#F9FAFB',
              cursor: 'pointer',
            }}
          >
            <RotateCcw size={12} />
          </button>
          <input
            type="range"
            min={0}
            max={Math.max(0, tcs.entries.length - 1)}
            value={currentTimelineIndex}
            onChange={(e) => setCurrentTimelineIndex(Number(e.target.value))}
            style={{
              flex: 1,
              height: '4px',
              backgroundColor: '#374151',
              borderRadius: '2px',
            }}
          />
          <span style={{ color: '#9CA3AF', minWidth: '50px', textAlign: 'right' }}>
            {currentTimelineIndex + 1}/{tcs.entries.length}
          </span>
        </div>

        {/* Monaco Editor */}
        <div style={{ flex: 1, position: 'relative' }}>
          <Editor
            height="100%"
            defaultLanguage="typescript"
            value={code}
            onChange={(value) => setCode(value || '')}
            theme="vs-dark"
            options={{
              minimap: { enabled: true },
              fontSize: 13,
              lineNumbers: 'on',
              scrollBeyondLastLine: false,
              wordWrap: 'on',
              automaticLayout: true,
            }}
          />
        </div>
      </div>
    </BasePanel>
  )
}

