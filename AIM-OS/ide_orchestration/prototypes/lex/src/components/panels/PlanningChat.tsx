// Planning Chat Panel (APOE Integration)
import React, { useState, useEffect } from 'react'
import { MessageSquare, Send, Brain } from 'lucide-react'
import { Panel } from '@/types'
import { useVIF, useAPOE } from '@/hooks/useAIMOS'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

interface PlanningChatProps {
  panel: Panel
}

const mockPlanningMessages = [
  {
    id: 'msg-1',
    role: 'user' as const,
    content: 'Let\'s plan the next phase of the IDE prototype',
    timestamp: '2025-11-07T17:00:00Z',
  },
  {
    id: 'msg-2',
    role: 'assistant' as const,
    content: 'Great! Based on our current progress, I recommend:\n\n1. Complete remaining panels (8 panels)\n2. Add panel customization features\n3. Polish UI/UX\n4. Add layout saving/loading\n\nWould you like me to create an APOE plan for this?',
    timestamp: '2025-11-07T17:00:05Z',
    confidence: 0.92,
    planId: 'plan-123',
  },
  {
    id: 'msg-3',
    role: 'user' as const,
    content: 'Yes, create a plan',
    timestamp: '2025-11-07T17:00:10Z',
  },
  {
    id: 'msg-4',
    role: 'assistant' as const,
    content: 'APOE Plan Created:\n\n**Phase 1: Panel Implementation**\n- Task 1: Component Library Panel\n- Task 2: Documentation Viewer\n- Task 3: UI Editor\n- Task 4: Search Panel\n- Task 5: Git Panel\n\n**Phase 2: Customization**\n- Task 6: Panel drag-and-drop\n- Task 7: Layout presets\n- Task 8: Custom layouts\n\n**Phase 3: Polish**\n- Task 9: UI improvements\n- Task 10: Performance optimization\n\nConfidence: 0.88',
    timestamp: '2025-11-07T17:00:15Z',
    confidence: 0.88,
    planId: 'plan-123',
  },
]

export const PlanningChat: React.FC<PlanningChatProps> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const [messages, setMessages] = useState(mockPlanningMessages)
  const [input, setInput] = useState('')
  const { getConfidence } = useVIF()
  const { tasks } = useAPOE()

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

  const handleSend = () => {
    if (!input.trim()) return

    const userMessage = {
      id: `msg-${Date.now()}`,
      role: 'user' as const,
      content: input,
      timestamp: new Date().toISOString(),
    }

    setMessages([...messages, userMessage])
    setInput('')

    // Simulate AI response
    setTimeout(() => {
      const confidence = getConfidence('Planning Chat')?.confidence || 0.85
      const aiMessage = {
        id: `msg-${Date.now()}`,
        role: 'assistant' as const,
        content: `I understand you want to: ${input}\n\nLet me analyze this and create a plan...`,
        timestamp: new Date().toISOString(),
        confidence,
      }
      setMessages((prev) => [...prev, aiMessage])
    }, 500)
  }

  const headerActions = tasks.length > 0 ? (
    <span style={{ fontSize: '11px', color: '#9CA3AF' }}>{tasks.length} active plan(s)</span>
  ) : undefined

  return (
    <BasePanel panel={panel} headerActions={headerActions}>
      <div style={{ flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column', gap: '12px', padding: '16px' }}>
        {messages.map((message) => (
          <div
            key={message.id}
            style={{
              padding: '12px',
              backgroundColor: message.role === 'user' ? '#374151' : '#111827',
              borderRadius: '4px',
              alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%',
            }}
          >
            <div style={{ fontSize: '12px', whiteSpace: 'pre-wrap', marginBottom: message.confidence ? '4px' : '0' }}>
              {message.content}
            </div>
            {message.confidence && (
              <div style={{ fontSize: '10px', color: '#9CA3AF', marginTop: '4px' }}>
                Confidence: {(message.confidence * 100).toFixed(0)}%
              </div>
            )}
            {message.planId && (
              <div style={{ fontSize: '10px', color: '#3B82F6', marginTop: '4px', cursor: 'pointer' }}>
                View Plan: {message.planId}
              </div>
            )}
          </div>
        ))}
      </div>
      <div style={{ padding: '12px', borderTop: '1px solid #374151', display: 'flex', gap: '8px' }}>
        <input
          type="text"
          placeholder="Plan something..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          style={{
            flex: 1,
            padding: '8px',
            backgroundColor: '#374151',
            border: '1px solid #4B5563',
            borderRadius: '4px',
            color: '#F9FAFB',
            fontSize: '12px',
          }}
        />
        <button
          onClick={handleSend}
          style={{
            padding: '8px 16px',
            backgroundColor: '#3B82F6',
            border: 'none',
            borderRadius: '4px',
            color: '#F9FAFB',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}
        >
          <Send size={14} />
        </button>
      </div>
    </BasePanel>
  )
}

