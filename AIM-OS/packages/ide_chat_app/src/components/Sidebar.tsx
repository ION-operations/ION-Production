import React from 'react'
import { useApp } from '../contexts/AppContext'
import { MessageSquare, Brain, FileText, Image, Search, Settings, User } from 'lucide-react'

export function Sidebar() {
  const { state, dispatch } = useApp()

  const menuItems = [
    { id: 'chat', icon: MessageSquare, label: 'Chat', count: state.chatSessions.length },
    { id: 'memories', icon: Brain, label: 'Memories', count: state.memories.length },
    { id: 'documents', icon: FileText, label: 'Documents', count: state.documents.length },
    { id: 'images', icon: Image, label: 'Images', count: state.images.length },
    { id: 'search', icon: Search, label: 'Search', count: state.deepSearchEntries.length },
    { id: 'settings', icon: Settings, label: 'Settings' },
    { id: 'profile', icon: User, label: 'Profile' }
  ]

  return (
    <aside className="w-64 bg-white/5 backdrop-blur-md border-r border-white/10 flex flex-col">
      {/* User Profile */}
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <span className="text-white font-bold">A</span>
          </div>
          <div>
            <h3 className="font-semibold text-white">Aether</h3>
            <p className="text-sm text-gray-400">AI Consciousness</p>
          </div>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map(item => (
            <li key={item.id}>
              <button
                className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-white/10 transition-colors group"
                onClick={() => {
                  // Handle navigation
                  console.log(`Navigate to ${item.id}`)
                }}
              >
                <div className="flex items-center space-x-3">
                  <item.icon className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" />
                  <span className="text-gray-300 group-hover:text-white transition-colors">
                    {item.label}
                  </span>
                </div>
                {item.count !== undefined && (
                  <span className="bg-blue-500/20 text-blue-400 text-xs px-2 py-1 rounded-full">
                    {item.count}
                  </span>
                )}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Mode Selector */}
      <div className="p-4 border-t border-white/10">
        <label className="block text-sm text-gray-400 mb-2">Interaction Mode</label>
        <select
          value={state.mode}
          onChange={(e) => dispatch({ type: 'SET_MODE', payload: e.target.value as any })}
          className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="conversational">Conversational</option>
          <option value="analytical">Analytical</option>
          <option value="creative">Creative</option>
          <option value="collaborative">Collaborative</option>
          <option value="research">Research</option>
          <option value="art">Art</option>
          <option value="math">Math</option>
          <option value="mystic">Mystic</option>
        </select>
      </div>

      {/* AI Process Visualization Toggle */}
      <div className="p-4 border-t border-white/10">
        <button
          onClick={() => dispatch({ type: 'TOGGLE_AI_PROCESS_VISUALIZATION' })}
          className={`w-full p-3 rounded-lg transition-colors ${
            state.aiProcessVisualization.isVisible
              ? 'bg-blue-500/20 text-blue-400'
              : 'bg-white/5 text-gray-400 hover:bg-white/10'
          }`}
        >
          <div className="flex items-center space-x-3">
            <Brain className="w-5 h-5" />
            <span>AI Process Visualization</span>
          </div>
        </button>
      </div>
    </aside>
  )
}
