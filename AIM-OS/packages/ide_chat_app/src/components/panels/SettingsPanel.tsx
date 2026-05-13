/**
 * Settings Panel Component
 * 
 * Phase 1.3: Basic Panel Components
 * 
 * IDE settings and preferences management.
 * Features:
 * - Theme selection (Dark, Light, High Contrast)
 * - Editor settings (font size, word wrap, etc.)
 * - Keyboard shortcuts configuration
 * - Panel visibility preferences
 * - AIM-OS integration settings
 * - Settings persistence (localStorage)
 */

import React, { useState, useEffect } from 'react'
import { Settings, Moon, Sun, Monitor, Type, Keyboard, Layout, Brain, Save, RotateCcw } from 'lucide-react'
import { useAIMOS } from '../../hooks/useAIMOS'
import { LoadingState } from '../LoadingState'
import { ErrorBoundary } from '../ErrorBoundary'

interface SettingsPanelProps {
  onSettingsChange?: (settings: IDESettings) => void
}

export interface IDESettings {
  theme: 'dark' | 'light' | 'high-contrast'
  editor: {
    fontSize: number
    fontFamily: string
    wordWrap: 'on' | 'off' | 'wordWrapColumn' | 'bounded'
    lineNumbers: 'on' | 'off' | 'relative' | 'interval'
    minimap: boolean
    tabSize: number
    insertSpaces: boolean
  }
  panels: {
    autoHideLeft: boolean
    autoHideRight: boolean
    autoHideBottom: boolean
  }
  keyboard: {
    shortcuts: Record<string, string>
  }
  aimos: {
    enableCMC: boolean
    enableHHNI: boolean
    enableVIF: boolean
    enableSEG: boolean
    enableAPOE: boolean
    enableCAS: boolean
    enableTCS: boolean
  }
}

const DEFAULT_SETTINGS: IDESettings = {
  theme: 'dark',
  editor: {
    fontSize: 14,
    fontFamily: 'Consolas, "Courier New", monospace',
    wordWrap: 'on',
    lineNumbers: 'on',
    minimap: true,
    tabSize: 2,
    insertSpaces: true,
  },
  panels: {
    autoHideLeft: false,
    autoHideRight: false,
    autoHideBottom: false,
  },
  keyboard: {
    shortcuts: {
      'commandPalette': 'Ctrl+K',
      'toggleTerminal': 'Ctrl+`',
      'toggleFileExplorer': 'Ctrl+Shift+E',
      'toggleOutline': 'Ctrl+Shift+O',
      'toggleAIMemory': 'Ctrl+Shift+M',
    },
  },
  aimos: {
    enableCMC: true,
    enableHHNI: true,
    enableVIF: true,
    enableSEG: true,
    enableAPOE: true,
    enableCAS: true,
    enableTCS: true,
  },
}

export const SettingsPanel: React.FC<SettingsPanelProps> = React.memo(({ onSettingsChange }) => {
  const [settings, setSettings] = useState<IDESettings>(DEFAULT_SETTINGS)
  const [activeTab, setActiveTab] = useState<'general' | 'editor' | 'panels' | 'keyboard' | 'aimos'>('general')
  const [hasChanges, setHasChanges] = useState(false)

  // AIM-OS integration (for syncing settings to CMC)
  const { cmc, isConnected, useMockData, loading } = useAIMOS()

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('rev-ide-settings')
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings)
        setSettings({ ...DEFAULT_SETTINGS, ...parsed })
      } catch (error) {
        console.error('Failed to load settings:', error)
      }
    }
  }, [])

  // Sync settings to CMC when connected
  useEffect(() => {
    const syncToCMC = async () => {
      if (!useMockData && isConnected && hasChanges) {
        try {
          await cmc.storeAtom({
            content: { inline: JSON.stringify(settings) },
            modality: 'config',
            metadata: { type: 'ide_settings', version: '1.0' },
          })
        } catch (error) {
          console.warn('Failed to sync settings to CMC', error)
        }
      }
    }
    
    if (hasChanges) {
      syncToCMC()
    }
  }, [settings, cmc, isConnected, useMockData, hasChanges])

  // Notify parent of settings changes
  useEffect(() => {
    if (onSettingsChange) {
      onSettingsChange(settings)
    }
  }, [settings, onSettingsChange])

  const updateSettings = (updates: Partial<IDESettings>) => {
    setSettings(prev => ({ ...prev, ...updates }))
    setHasChanges(true)
  }

  const saveSettings = () => {
    localStorage.setItem('rev-ide-settings', JSON.stringify(settings))
    setHasChanges(false)
    // Apply theme
    document.documentElement.setAttribute('data-theme', settings.theme)
  }

  const resetSettings = () => {
    setSettings(DEFAULT_SETTINGS)
    setHasChanges(true)
  }

  const renderGeneralTab = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Theme
        </label>
        <div className="flex gap-3">
          <button
            onClick={() => updateSettings({ theme: 'dark' })}
            className={`flex items-center gap-2 px-4 py-2 rounded border transition-colors ${
              settings.theme === 'dark'
                ? 'bg-blue-600 border-blue-500 text-white'
                : 'bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700'
            }`}
          >
            <Moon className="w-4 h-4" />
            Dark
          </button>
          <button
            onClick={() => updateSettings({ theme: 'light' })}
            className={`flex items-center gap-2 px-4 py-2 rounded border transition-colors ${
              settings.theme === 'light'
                ? 'bg-blue-600 border-blue-500 text-white'
                : 'bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700'
            }`}
          >
            <Sun className="w-4 h-4" />
            Light
          </button>
          <button
            onClick={() => updateSettings({ theme: 'high-contrast' })}
            className={`flex items-center gap-2 px-4 py-2 rounded border transition-colors ${
              settings.theme === 'high-contrast'
                ? 'bg-blue-600 border-blue-500 text-white'
                : 'bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700'
            }`}
          >
            <Monitor className="w-4 h-4" />
            High Contrast
          </button>
        </div>
      </div>
    </div>
  )

  const renderEditorTab = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Font Size
        </label>
        <input
          type="number"
          min="8"
          max="24"
          value={settings.editor.fontSize}
          onChange={(e) => updateSettings({
            editor: { ...settings.editor, fontSize: parseInt(e.target.value) || 14 }
          })}
          className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-gray-300 focus:outline-none focus:border-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Font Family
        </label>
        <select
          value={settings.editor.fontFamily}
          onChange={(e) => updateSettings({
            editor: { ...settings.editor, fontFamily: e.target.value }
          })}
          className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-gray-300 focus:outline-none focus:border-blue-500"
        >
          <option value="Consolas, 'Courier New', monospace">Consolas</option>
          <option value="'Fira Code', monospace">Fira Code</option>
          <option value="'JetBrains Mono', monospace">JetBrains Mono</option>
          <option value="'Source Code Pro', monospace">Source Code Pro</option>
          <option value="Monaco, monospace">Monaco</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Word Wrap
        </label>
        <select
          value={settings.editor.wordWrap}
          onChange={(e) => updateSettings({
            editor: { ...settings.editor, wordWrap: e.target.value as IDESettings['editor']['wordWrap'] }
          })}
          className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-gray-300 focus:outline-none focus:border-blue-500"
        >
          <option value="on">On</option>
          <option value="off">Off</option>
          <option value="wordWrapColumn">Word Wrap Column</option>
          <option value="bounded">Bounded</option>
        </select>
      </div>

      <div>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={settings.editor.minimap}
            onChange={(e) => updateSettings({
              editor: { ...settings.editor, minimap: e.target.checked }
            })}
            className="w-4 h-4 text-blue-600 bg-gray-900 border-gray-700 rounded focus:ring-blue-500"
          />
          <span className="text-sm text-gray-300">Show Minimap</span>
        </label>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Tab Size
        </label>
        <input
          type="number"
          min="1"
          max="8"
          value={settings.editor.tabSize}
          onChange={(e) => updateSettings({
            editor: { ...settings.editor, tabSize: parseInt(e.target.value) || 2 }
          })}
          className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-gray-300 focus:outline-none focus:border-blue-500"
        />
      </div>

      <div>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={settings.editor.insertSpaces}
            onChange={(e) => updateSettings({
              editor: { ...settings.editor, insertSpaces: e.target.checked }
            })}
            className="w-4 h-4 text-blue-600 bg-gray-900 border-gray-700 rounded focus:ring-blue-500"
          />
          <span className="text-sm text-gray-300">Insert Spaces</span>
        </label>
      </div>
    </div>
  )

  const renderPanelsTab = () => (
    <div className="space-y-4">
      <div>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={settings.panels.autoHideLeft}
            onChange={(e) => updateSettings({
              panels: { ...settings.panels, autoHideLeft: e.target.checked }
            })}
            className="w-4 h-4 text-blue-600 bg-gray-900 border-gray-700 rounded focus:ring-blue-500"
          />
          <span className="text-sm text-gray-300">Auto-hide Left Panel</span>
        </label>
      </div>

      <div>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={settings.panels.autoHideRight}
            onChange={(e) => updateSettings({
              panels: { ...settings.panels, autoHideRight: e.target.checked }
            })}
            className="w-4 h-4 text-blue-600 bg-gray-900 border-gray-700 rounded focus:ring-blue-500"
          />
          <span className="text-sm text-gray-300">Auto-hide Right Panel</span>
        </label>
      </div>

      <div>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={settings.panels.autoHideBottom}
            onChange={(e) => updateSettings({
              panels: { ...settings.panels, autoHideBottom: e.target.checked }
            })}
            className="w-4 h-4 text-blue-600 bg-gray-900 border-gray-700 rounded focus:ring-blue-500"
          />
          <span className="text-sm text-gray-300">Auto-hide Bottom Panel</span>
        </label>
      </div>
    </div>
  )

  const renderKeyboardTab = () => (
    <div className="space-y-4">
      <p className="text-sm text-gray-400 mb-4">
        Configure keyboard shortcuts for IDE actions.
      </p>
      {Object.entries(settings.keyboard.shortcuts).map(([action, shortcut]) => (
        <div key={action} className="flex items-center justify-between">
          <span className="text-sm text-gray-300 capitalize">
            {action.replace(/([A-Z])/g, ' $1').trim()}
          </span>
          <input
            type="text"
            value={shortcut}
            onChange={(e) => updateSettings({
              keyboard: {
                shortcuts: {
                  ...settings.keyboard.shortcuts,
                  [action]: e.target.value
                }
              }
            })}
            className="px-3 py-1 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 focus:outline-none focus:border-blue-500 w-32"
            placeholder="Ctrl+K"
          />
        </div>
      ))}
    </div>
  )

  const renderAIMOSTab = () => (
    <div className="space-y-4">
      <p className="text-sm text-gray-400 mb-4">
        Enable or disable AIM-OS system integrations.
      </p>
      {Object.entries(settings.aimos).map(([system, enabled]) => (
        <div key={system} className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-300 uppercase">{system}</span>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={enabled}
              onChange={(e) => updateSettings({
                aimos: {
                  ...settings.aimos,
                  [system]: e.target.checked
                }
              })}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>
      ))}
    </div>
  )

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-800" role="complementary" aria-label="Settings Panel">
        {loading.cmc ? (
          <LoadingState message="Syncing settings..." />
        ) : (
          <>
      {/* Header */}
      <div className="h-10 bg-gray-900 border-b border-gray-700 flex items-center px-3 shrink-0">
        <Settings className="w-4 h-4 mr-2 text-gray-400" />
        <span className="text-sm font-semibold text-gray-300">Settings</span>
        {hasChanges && (
          <span className="ml-auto text-xs text-yellow-400">Unsaved changes</span>
        )}
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-700 shrink-0">
        {(['general', 'editor', 'panels', 'keyboard', 'aimos'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium transition-colors capitalize ${
              activeTab === tab
                ? 'text-blue-400 border-b-2 border-blue-400 bg-gray-800'
                : 'text-gray-400 hover:text-gray-300 hover:bg-gray-800'
            }`}
            aria-label={`${tab} settings`}
          >
            {tab === 'general' && <Monitor className="w-4 h-4 inline mr-1" />}
            {tab === 'editor' && <Type className="w-4 h-4 inline mr-1" />}
            {tab === 'panels' && <Layout className="w-4 h-4 inline mr-1" />}
            {tab === 'keyboard' && <Keyboard className="w-4 h-4 inline mr-1" />}
            {tab === 'aimos' && <Brain className="w-4 h-4 inline mr-1" />}
            {tab}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'general' && renderGeneralTab()}
        {activeTab === 'editor' && renderEditorTab()}
        {activeTab === 'panels' && renderPanelsTab()}
        {activeTab === 'keyboard' && renderKeyboardTab()}
        {activeTab === 'aimos' && renderAIMOSTab()}
      </div>

      {/* Footer */}
      <div className="h-12 bg-gray-900 border-t border-gray-700 flex items-center justify-end gap-2 px-4 shrink-0">
        <button
          onClick={resetSettings}
          className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded transition-colors"
          aria-label="Reset to defaults"
        >
          <RotateCcw className="w-4 h-4" />
          Reset
        </button>
        <button
          onClick={saveSettings}
          disabled={!hasChanges}
          className={`flex items-center gap-2 px-4 py-1.5 text-sm rounded transition-colors ${
            hasChanges
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-700 text-gray-500 cursor-not-allowed'
          }`}
          aria-label="Save settings"
        >
          <Save className="w-4 h-4" />
          Save
        </button>
      </div>
          </>
        )}
      </div>
    </ErrorBoundary>
  )
})

