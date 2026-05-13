// Documentation Viewer Panel (Code + Docs Viewer)
import React, { useState, useEffect } from 'react'
import { Book, FileText, Code, Eye } from 'lucide-react'
import { Panel } from '@/types'
import { useVIF, useSEG } from '@/hooks/useAIMOS'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

interface DocumentationViewerProps {
  panel: Panel
}

interface Documentation {
  id: string
  title: string
  type: 'markdown' | 'code' | 'api'
  content: string
  path: string
  confidence: number
  contradictions?: string[]
}

const mockDocumentation: Documentation[] = [
  {
    id: 'doc-1',
    title: 'IDE Layout Architecture',
    type: 'markdown',
    content: `# IDE Layout Architecture

## Overview
The IDE layout system provides a flexible, resizable panel system with deep AIM-OS integration.

## Key Features
- Resizable panels
- Panel management
- AIM-OS integration
- Customizable layouts

## Components
- \`IDELayout\` - Main layout component
- \`Panel\` - Individual panel component
- \`useLayoutStore\` - Layout state management`,
    path: 'docs/IDE_ARCHITECTURE.md',
    confidence: 0.95,
  },
  {
    id: 'doc-2',
    title: 'PDAS System',
    type: 'markdown',
    content: `# Proactive Debugging & Auditing System (PDAS)

## Core Concept
Debugging infrastructure built INTO the development process from day one.

## Components
1. **Audit Layer** - Pre-execution auditing
2. **Observability Layer** - Always-on monitoring
3. **Debug Layer** - Durable debugging applications`,
    path: 'docs/PDAS.md',
    confidence: 0.92,
  },
]

export const DocumentationViewer: React.FC<DocumentationViewerProps> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const [selectedDoc, setSelectedDoc] = useState<Documentation | null>(mockDocumentation[0])
  const [viewMode, setViewMode] = useState<'preview' | 'source'>('preview')
  const { getConfidence } = useVIF()
  const { detectContradictions } = useSEG()

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

  const contradictions = selectedDoc ? detectContradictions(selectedDoc.content) : []
  const confidence = selectedDoc ? selectedDoc.confidence : 0.85

  const headerActions = selectedDoc ? (
    <div style={{ display: 'flex', gap: '4px' }}>
      <button
        onClick={() => setViewMode('preview')}
        style={{
          padding: '4px 8px',
          fontSize: '11px',
          backgroundColor: viewMode === 'preview' ? '#374151' : 'transparent',
          border: '1px solid #374151',
          borderRadius: '4px',
          color: '#F9FAFB',
          cursor: 'pointer',
        }}
      >
        Preview
      </button>
      <button
        onClick={() => setViewMode('source')}
        style={{
          padding: '4px 8px',
          fontSize: '11px',
          backgroundColor: viewMode === 'source' ? '#374151' : 'transparent',
          border: '1px solid #374151',
          borderRadius: '4px',
          color: '#F9FAFB',
          cursor: 'pointer',
        }}
      >
        Source
      </button>
    </div>
  ) : undefined

  return (
    <BasePanel panel={panel} headerActions={headerActions}>
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Sidebar */}
        <div style={{ width: '200px', borderRight: '1px solid #374151', overflow: 'auto', backgroundColor: '#111827' }}>
          <div style={{ padding: '8px', fontSize: '11px', color: '#9CA3AF', fontWeight: 'bold' }}>Documents</div>
          {mockDocumentation.map((doc) => (
            <div
              key={doc.id}
              onClick={() => setSelectedDoc(doc)}
              style={{
                padding: '8px 12px',
                backgroundColor: selectedDoc?.id === doc.id ? '#374151' : 'transparent',
                cursor: 'pointer',
                fontSize: '12px',
                borderBottom: '1px solid #374151',
              }}
            >
              <div style={{ fontWeight: selectedDoc?.id === doc.id ? 'bold' : 'normal' }}>{doc.title}</div>
              <div style={{ fontSize: '10px', color: '#6B7280', marginTop: '2px' }}>{doc.path}</div>
            </div>
          ))}
        </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: 'auto', padding: '16px', display: 'flex', flexDirection: 'column' }}>
          {selectedDoc ? (
            <>
              <div style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '4px' }}>{selectedDoc.title}</div>
                  <div style={{ fontSize: '11px', color: '#9CA3AF' }}>{selectedDoc.path}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {contradictions.length > 0 && (
                    <span style={{ fontSize: '11px', color: '#EF4444' }}>⚠️ {contradictions.length} contradiction(s)</span>
                  )}
                  <span
                    style={{
                      fontSize: '11px',
                      color: confidence > 0.8 ? '#10B981' : confidence > 0.6 ? '#F59E0B' : '#EF4444',
                    }}
                  >
                    {(confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              {viewMode === 'preview' ? (
                <div style={{ fontSize: '13px', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>{selectedDoc.content}</div>
              ) : (
                <div style={{ fontFamily: 'monospace', fontSize: '12px', backgroundColor: '#000', padding: '12px', borderRadius: '4px', overflow: 'auto' }}>
                  {selectedDoc.content}
                </div>
              )}
            </>
          ) : (
            <div style={{ textAlign: 'center', color: '#9CA3AF', padding: '40px' }}>Select a document to view</div>
          )}
        </div>
      </div>
    </BasePanel>
  )
}

