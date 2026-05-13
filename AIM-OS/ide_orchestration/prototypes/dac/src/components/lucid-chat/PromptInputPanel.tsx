/**
 * Prompt Input Panel Component
 * Text input with art style selector and negative prompt
 */

import React, { useState } from 'react'
import { Send, X } from 'lucide-react'

export interface PromptInputPanelProps {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  artStyles?: string[]
  showNegativePrompt?: boolean
  negativePrompt?: string
  onNegativePromptChange?: (value: string) => void
  placeholder?: string
  maxLength?: number
  disabled?: boolean
}

export const PromptInputPanel: React.FC<PromptInputPanelProps> = ({
  value,
  onChange,
  onSubmit,
  artStyles = [],
  showNegativePrompt = false,
  negativePrompt = '',
  onNegativePromptChange,
  placeholder = 'Enter your prompt...',
  maxLength = 500,
  disabled = false,
}) => {
  const [selectedArtStyle, setSelectedArtStyle] = useState<string>('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (value.trim() && !disabled) {
      onSubmit()
    }
  }

  const characterCount = value.length
  const remainingChars = maxLength - characterCount

  return (
    <div className="space-y-3">
      {/* Art Style Selector */}
      {artStyles.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Art Style (Optional)
          </label>
          <select
            value={selectedArtStyle}
            onChange={(e) => setSelectedArtStyle(e.target.value)}
            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={disabled}
          >
            <option value="">None</option>
            {artStyles.map((style) => (
              <option key={style} value={style}>
                {style}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Main Prompt Input */}
      <form onSubmit={handleSubmit}>
        <div className="relative">
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            maxLength={maxLength}
            disabled={disabled}
            rows={4}
            className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <div className="absolute bottom-2 right-2 flex items-center gap-2">
            <span
              className={`text-xs ${
                remainingChars < 50 ? 'text-red-400' : 'text-gray-500'
              }`}
            >
              {characterCount}/{maxLength}
            </span>
            <button
              type="submit"
              disabled={!value.trim() || disabled || characterCount >= maxLength}
              className="p-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Generate"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </form>

      {/* Negative Prompt */}
      {showNegativePrompt && (
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="block text-sm font-medium text-gray-300">
              Negative Prompt (What to avoid)
            </label>
            {negativePrompt && (
              <button
                onClick={() => onNegativePromptChange?.('')}
                className="text-xs text-gray-500 hover:text-gray-400"
              >
                <X className="w-3 h-3" />
              </button>
            )}
          </div>
          <input
            type="text"
            value={negativePrompt}
            onChange={(e) => onNegativePromptChange?.(e.target.value)}
            placeholder="e.g., blurry, low quality, distorted"
            disabled={disabled}
            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-gray-200 placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
          />
        </div>
      )}
    </div>
  )
}

