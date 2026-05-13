import React, { useState, useEffect, useRef } from 'react'
import { Search, X } from 'lucide-react'
import { aimosClient } from '../lib/aimos-client'

interface SearchResult {
  id: string
  type: 'message' | 'memory' | 'context'
  content: string
  timestamp?: Date
}

export const SearchBar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const searchRef = useRef<HTMLDivElement>(null)

  // Close search on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  // Search when query changes
  useEffect(() => {
    if (!query.trim()) {
      setResults([])
      return
    }

    const performSearch = async () => {
      setIsSearching(true)
      
      try {
        // Search AIM-OS memory
        const memoryResults = await aimosClient.retrieveMemory(query)
        
        // Search AIM-OS context
        const contextResults = await aimosClient.searchContext(query)
        
        const allResults: SearchResult[] = [
          ...memoryResults.map((item: any, index: number) => ({
            id: `memory-${index}`,
            type: 'memory' as const,
            content: item.content || item.text || '',
            timestamp: item.timestamp ? new Date(item.timestamp) : undefined
          })),
          ...contextResults.map((item: any, index: number) => ({
            id: `context-${index}`,
            type: 'context' as const,
            content: item.content || item.text || '',
            timestamp: item.timestamp ? new Date(item.timestamp) : undefined
          }))
        ]
        
        setResults(allResults)
      } catch (error) {
        console.error('Search failed:', error)
        setResults([])
      } finally {
        setIsSearching(false)
      }
    }

    const debounceTimer = setTimeout(performSearch, 300)
    return () => clearTimeout(debounceTimer)
  }, [query])

  const handleSearchKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      setIsOpen(false)
      setQuery('')
    } else if (e.key === 'Enter' && results.length > 0) {
      // Navigate to first result or handle selection
      console.log('Navigate to:', results[0])
    }
  }

  return (
    <div ref={searchRef} className="relative">
      {/* Search Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 hover:bg-white/10 rounded-lg transition-colors relative"
        aria-label="Search"
      >
        <Search className="w-5 h-5 text-gray-600" />
        {query && (
          <span className="absolute top-0 right-0 w-2 h-2 bg-blue-500 rounded-full"></span>
        )}
      </button>

      {/* Search Panel */}
      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
          {/* Search Input */}
          <div className="p-3 border-b border-gray-200">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleSearchKey}
                placeholder="Search memories, context, messages..."
                className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
              />
              {query && (
                <button
                  onClick={() => setQuery('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          {/* Search Results */}
          <div className="max-h-96 overflow-y-auto">
            {isSearching && (
              <div className="p-4 text-center text-gray-500 text-sm">
                Searching...
              </div>
            )}

            {!isSearching && query && results.length === 0 && (
              <div className="p-4 text-center text-gray-500 text-sm">
                No results found
              </div>
            )}

            {!isSearching && results.length > 0 && (
              <div className="py-2">
                {results.slice(0, 10).map((result) => (
                  <button
                    key={result.id}
                    className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0"
                    onClick={() => {
                      console.log('Selected result:', result)
                      setIsOpen(false)
                    }}
                  >
                    <div className="flex items-start gap-3">
                      <div className="mt-1">
                        {result.type === 'memory' && (
                          <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                        )}
                        {result.type === 'context' && (
                          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-700 truncate">
                          {result.content}
                        </div>
                        {result.timestamp && (
                          <div className="text-xs text-gray-400 mt-1">
                            {result.timestamp.toLocaleString()}
                          </div>
                        )}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {!isSearching && !query && (
              <div className="p-4 text-center text-gray-500 text-sm">
                Start typing to search...
              </div>
            )}
          </div>

          {/* Keyboard Shortcuts */}
          <div className="px-4 py-2 border-t border-gray-200 bg-gray-50 flex items-center justify-between text-xs text-gray-500">
            <span>Press Enter to navigate</span>
            <span>ESC to close</span>
          </div>
        </div>
      )}
    </div>
  )
}
