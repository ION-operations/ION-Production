// Command Palette Component
// Quick command access

import React, { useState, useEffect } from 'react'
import { Search } from 'lucide-react'

export const CommandPalette: React.FC = () => {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setOpen(true)
      }
      if (e.key === 'Escape') {
        setOpen(false)
      }
    }
    
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])
  
  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="px-3 py-1 rounded text-sm bg-gray-700 text-gray-300 hover:bg-gray-600 flex items-center gap-2"
      >
        <Search className="w-4 h-4" />
        <span>Ctrl+K</span>
      </button>
    )
  }
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-start justify-center pt-20 z-50" onClick={() => setOpen(false)}>
      <div className="w-96 bg-gray-800 rounded-lg shadow-xl border border-gray-700" onClick={(e) => e.stopPropagation()}>
        <div className="p-3 border-b border-gray-700">
          <div className="flex items-center gap-2 text-gray-400">
            <Search className="w-4 h-4" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type a command..."
              className="flex-1 bg-transparent text-white placeholder-gray-500 outline-none"
              autoFocus
            />
          </div>
        </div>
        
        <div className="p-2">
          <div className="text-xs text-gray-500 mb-2 px-2">Commands</div>
          <div className="space-y-1">
            <div className="px-3 py-2 rounded hover:bg-gray-700 cursor-pointer text-sm text-gray-300">
              Open File
            </div>
            <div className="px-3 py-2 rounded hover:bg-gray-700 cursor-pointer text-sm text-gray-300">
              New File
            </div>
            <div className="px-3 py-2 rounded hover:bg-gray-700 cursor-pointer text-sm text-gray-300">
              Search Files
            </div>
            <div className="px-3 py-2 rounded hover:bg-gray-700 cursor-pointer text-sm text-gray-300">
              Toggle Terminal
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

