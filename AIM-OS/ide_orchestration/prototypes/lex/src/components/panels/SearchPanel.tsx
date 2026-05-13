// Search Panel (HHNI-Powered Semantic Search)
import React, { useState, useEffect } from 'react'
import { Search, File, Code, Book, AlertCircle } from 'lucide-react'
import { Panel } from '@/types'
import { useHHNI, useCMC } from '@/hooks/useAIMOS'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

interface SearchPanelProps {
  panel: Panel
}

interface SearchResult {
  id: string
  type: 'file' | 'code' | 'documentation' | 'atom'
  title: string
  content: string
  path?: string
  relevance: number
  confidence: number
}

const mockSearchResults: SearchResult[] = [
  {
    id: 'result-1',
    type: 'file',
    title: 'IDELayout.tsx',
    content: 'Core layout component with panel management',
    path: 'src/components/Layout/IDELayout.tsx',
    relevance: 0.95,
    confidence: 0.92,
  },
  {
    id: 'result-2',
    type: 'code',
    title: 'useCMC hook',
    content: 'Hook for accessing CMC atoms and statistics',
    path: 'src/hooks/useAIMOS.ts',
    relevance: 0.88,
    confidence: 0.90,
  },
  {
    id: 'result-3',
    type: 'atom',
    title: 'CMC Atom: ide-layout-design',
    content: 'Design document for IDE layout architecture',
    relevance: 0.82,
    confidence: 0.85,
  },
  {
    id: 'result-4',
    type: 'documentation',
    title: 'IDE Architecture Guide',
    content: 'Complete guide to IDE architecture and panel system',
    path: 'docs/IDE_ARCHITECTURE.md',
    relevance: 0.75,
    confidence: 0.88,
  },
]

export const SearchPanel: React.FC<SearchPanelProps> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const { search } = useHHNI()
  const { atoms } = useCMC()

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

  const handleSearch = (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([])
      return
    }

    setIsSearching(true)
    // Simulate HHNI semantic search
    setTimeout(() => {
      const hhniResults = search(searchQuery)
      const filteredResults = mockSearchResults.filter((result) =>
        result.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        result.content.toLowerCase().includes(searchQuery.toLowerCase())
      )
      setResults(filteredResults)
      setIsSearching(false)
    }, 300)
  }

  const getTypeIcon = (type: SearchResult['type']) => {
    switch (type) {
      case 'file':
        return <File size={14} />
      case 'code':
        return <Code size={14} />
      case 'documentation':
        return <Book size={14} />
      default:
        return <AlertCircle size={14} />
    }
  }

  return (
    <BasePanel panel={panel}>
      <div style={{ padding: '12px', borderBottom: '1px solid #374151' }}>
        <div style={{ position: 'relative' }}>
          <Search size={16} style={{ position: 'absolute', left: '8px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }} />
          <input
            type="text"
            placeholder="Search files, code, documentation, atoms..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value)
              handleSearch(e.target.value)
            }}
            style={{
              width: '100%',
              padding: '8px 8px 8px 32px',
              backgroundColor: '#111827',
              border: '1px solid #374151',
              borderRadius: '4px',
              color: '#F9FAFB',
              fontSize: '12px',
            }}
          />
        </div>
      </div>
      <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
        {isSearching && (
          <div style={{ padding: '20px', textAlign: 'center', color: '#9CA3AF', fontSize: '12px' }}>Searching...</div>
        )}
        {!isSearching && results.length === 0 && query && (
          <div style={{ padding: '20px', textAlign: 'center', color: '#9CA3AF', fontSize: '12px' }}>No results found</div>
        )}
        {!isSearching && results.length === 0 && !query && (
          <div style={{ padding: '20px', textAlign: 'center', color: '#9CA3AF', fontSize: '12px' }}>
            Enter a search query to find files, code, documentation, or CMC atoms
          </div>
        )}
        {!isSearching && results.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {results.map((result) => (
              <div
                key={result.id}
                style={{
                  padding: '10px',
                  backgroundColor: '#111827',
                  border: '1px solid #374151',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span style={{ color: '#9CA3AF' }}>{getTypeIcon(result.type)}</span>
                  <span style={{ fontWeight: 'bold', fontSize: '13px' }}>{result.title}</span>
                  <span style={{ marginLeft: 'auto', fontSize: '10px', color: '#9CA3AF' }}>
                    {(result.relevance * 100).toFixed(0)}% match
                  </span>
                </div>
                {result.path && (
                  <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>{result.path}</div>
                )}
                <div style={{ fontSize: '12px', color: '#D1D5DB' }}>{result.content}</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                  <span style={{ fontSize: '10px', color: '#9CA3AF' }}>Confidence:</span>
                  <span
                    style={{
                      fontSize: '10px',
                      color: result.confidence > 0.8 ? '#10B981' : result.confidence > 0.6 ? '#F59E0B' : '#EF4444',
                    }}
                  >
                    {(result.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </BasePanel>
  )
}

