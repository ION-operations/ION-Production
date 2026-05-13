import React from 'react'
import { useApp } from '../contexts/AppContext'
import { Settings, User, Bell, Search } from 'lucide-react'
import type { Theme } from '../types'

export function TopBar() {
  const { state, dispatch } = useApp()

  const themes: Theme[] = ['space', 'cyberpunk', 'matrix', 'aurora', 'blade-runner', 'retro', 'mist']

  return (
    <header className="h-16 bg-white/10 backdrop-blur-md border-b border-white/20 flex items-center justify-between px-6">
      {/* Logo and Title */}
      <div className="flex items-center space-x-4">
        <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-sm">AI</span>
        </div>
        <h1 className="text-xl font-bold text-gradient">
          [SAM] IDE/Chat App
        </h1>
        <span className="text-sm text-gray-500">
          AI Consciousness Development Environment
        </span>
      </div>

      {/* Theme Selector */}
      <div className="flex items-center space-x-2">
        <span className="text-sm text-gray-600">Theme:</span>
        <select
          value={state.theme}
          onChange={(e) => dispatch({ type: 'SET_THEME', payload: e.target.value as Theme })}
          className="bg-white/10 border border-white/20 rounded-lg px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {themes.map(theme => (
            <option key={theme} value={theme}>
              {theme.charAt(0).toUpperCase() + theme.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Right Side Actions */}
      <div className="flex items-center space-x-4">
        <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
          <Search className="w-5 h-5 text-gray-600" />
        </button>
        <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
          <Bell className="w-5 h-5 text-gray-600" />
        </button>
        <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
          <Settings className="w-5 h-5 text-gray-600" />
        </button>
        <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
          <User className="w-5 h-5 text-gray-600" />
        </button>
      </div>
    </header>
  )
}
