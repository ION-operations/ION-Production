import React, { useRef, useState, useEffect, KeyboardEvent } from 'react'
import { Search, Terminal, FileText, Settings, User, Zap, Brain, Code } from 'lucide-react'

interface Command {
  id: string
  label: string
  icon: React.ReactNode
  category: string
  shortcut?: string
  action: () => void
}

export const CommandPalette: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  const commands: Command[] = [
    // Navigation
    {
      id: 'search',
      label: 'Search Memories and Context',
      icon: <Search className="w-4 h-4" />,
      category: 'Navigation',
      shortcut: 'Ctrl+K',
      action: () => console.log('Open search')
    },
    {
      id: 'memory',
      label: 'Open Memory Browser',
      icon: <Brain className="w-4 h-4" />,
      category: 'Navigation',
      action: () => console.log('Open memory browser')
    },
    
    // Files & Workspace
    {
      id: 'new-file',
      label: 'New File',
      icon: <FileText className="w-4 h-4" />,
      category: 'Files',
      shortcut: 'Ctrl+N',
      action: () => console.log('Create new file')
    },
    {
      id: 'terminal',
      label: 'Toggle Terminal',
      icon: <Terminal className="w-4 h-4" />,
      category: 'Files',
      shortcut: 'Ctrl+`',
      action: () => console.log('Toggle terminal')
    },
    
    // AI Features
    {
      id: 'ai-mode',
      label: 'Switch AI Mode',
      icon: <Zap className="w-4 h-4" />,
      category: 'AI',
      shortcut: 'Ctrl+Shift+M',
      action: () => console.log('Switch AI mode')
    },
    {
      id: 'ai-visualize',
      label: 'Visualize AI Process',
      icon: <Code className="w-4 h-4" />,
      category: 'AI',
      action: () => console.log('Visualize AI process')
    },
    
    // Settings
    {
      id: 'settings',
      label: 'Open Settings',
      icon: <Settings className="w-4 h-4" />,
      category: 'Settings',
      shortcut: 'Ctrl+,',
      action: () => console.log('Open settings')
    },
    {
      id: 'profile',
      label: 'User Profile',
      icon: <User className="w-4 h-4" />,
      category: 'Settings',
      action: () => console.log('Open profile')
    }
  ]

  // Filter commands based on query
  const filteredCommands = query
    ? commands.filter(cmd =>
        cmd.label.toLowerCase().includes(query.toLowerCase()) ||
        cmd.category.toLowerCase().includes(query.toLowerCase())
      )
    : commands

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+K or Cmd+K to open palette
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setIsOpen(true)
      }
      
      // Escape to close
      if (e.key === 'Escape') {
        setIsOpen(false)
        setQuery('')
      }
      
      // Arrow keys when open
      if (isOpen) {
        if (e.key === 'ArrowDown') {
          e.preventDefault()
          setSelectedIndex(prev => (prev + 1) % filteredCommands.length)
        } else if (e.key === 'ArrowUp') {
          e.preventDefault()
          setSelectedIndex(prev => (prev - 1 + filteredCommands.length) % filteredCommands.length)
        } else if (e.key === 'Enter') {
          e.preventDefault()
          filteredCommands[selectedIndex]?.action()
          setIsOpen(false)
          setQuery('')
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown as any)
    return () => window.removeEventListener('keydown', handleKeyDown as any)
  }, [isOpen, filteredCommands, selectedIndex])

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
      setSelectedIndex(0)
    }
  }, [isOpen])

  if (!isOpen) return null

  // Group commands by category
  const groupedCommands = filteredCommands.reduce((acc, cmd) => {
    if (!acc[cmd.category]) acc[cmd.category] = []
    acc[cmd.category].push(cmd)
    return acc
  }, {} as Record<string, Command[]>)

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-start justify-center pt-[10%]" onClick={() => setIsOpen(false)}>
      <div className="w-[640px] bg-white rounded-lg shadow-2xl overflow-hidden" onClick={(e) => e.stopPropagation()}>
        {/* Input */}
        <div className="p-4 border-b border-gray-200">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type a command or search..."
              className="w-full pl-10 pr-4 py-3 text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Commands List */}
        <div className="max-h-96 overflow-y-auto">
          {Object.entries(groupedCommands).map(([category, cmds]) => (
            <div key={category} className="py-2">
              <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                {category}
              </div>
              {cmds.map((cmd, index) => {
                const globalIndex = filteredCommands.findIndex(c => c.id === cmd.id)
                return (
                  <button
                    key={cmd.id}
                    onClick={() => {
                      cmd.action()
                      setIsOpen(false)
                      setQuery('')
                    }}
                    className={`w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors flex items-center gap-3 ${
                      globalIndex === selectedIndex ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="text-gray-600">{cmd.icon}</div>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-700">{cmd.label}</div>
                    </div>
                    {cmd.shortcut && (
                      <div className="flex items-center gap-1 text-xs text-gray-400">
                        {cmd.shortcut.split('+').map((key, i) => (
                          <kbd key={i} className="px-2 py-1 bg-gray-100 rounded border border-gray-300">
                            {key.replace('Ctrl', '⌘')}
                          </kbd>
                        ))}
                      </div>
                    )}
                  </button>
                )
              })}
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t border-gray-200 bg-gray-50 flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <kbd className="px-2 py-1 bg-white rounded border border-gray-300">↑</kbd>
              <kbd className="px-2 py-1 bg-white rounded border border-gray-300">↓</kbd>
              Navigate
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-2 py-1 bg-white rounded border border-gray-300">Enter</kbd>
              Select
            </span>
          </div>
          <span className="flex items-center gap-1">
            <kbd className="px-2 py-1 bg-white rounded border border-gray-300">Esc</kbd>
            Close
          </span>
        </div>
      </div>
    </div>
  )
}
