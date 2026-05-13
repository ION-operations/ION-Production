/**
 * Code Generation Input Component
 * Input interface for code generation requests
 * Created by Sage - Frontend Integration Specialist
 * Integrates with Nova's useICIP hook
 */

import React, { useState } from 'react'
import { Send, Code, FileCode, TestTube, Book, Sparkles, RefreshCw } from 'lucide-react'
import { LoadingSpinner } from '../shared'

export type GenerationType = 
  | 'function'
  | 'class'
  | 'test'
  | 'documentation'
  | 'completion'
  | 'refactoring'

export interface CodeGenerationInputProps {
  onGenerate: (type: GenerationType, prompt: string, language?: string, context?: string) => Promise<void>
  generating?: boolean
  language?: string
  defaultLanguage?: string
  className?: string
}

export const CodeGenerationInput: React.FC<CodeGenerationInputProps> = ({
  onGenerate,
  generating = false,
  language,
  defaultLanguage = 'typescript',
  className = '',
}) => {
  const [prompt, setPrompt] = useState('')
  const [selectedType, setSelectedType] = useState<GenerationType>('function')
  const [selectedLanguage, setSelectedLanguage] = useState(language || defaultLanguage)
  const [context, setContext] = useState('')

  const generationTypes: Array<{ type: GenerationType; label: string; icon: React.ElementType; description: string }> = [
    { type: 'function', label: 'Function', icon: Code, description: 'Generate a function' },
    { type: 'class', label: 'Class', icon: FileCode, description: 'Generate a class' },
    { type: 'test', label: 'Test', icon: TestTube, description: 'Generate tests' },
    { type: 'documentation', label: 'Documentation', icon: Book, description: 'Generate documentation' },
    { type: 'completion', label: 'Completion', icon: Sparkles, description: 'Complete code' },
    { type: 'refactoring', label: 'Refactor', icon: RefreshCw, description: 'Refactor code' },
  ]

  const languages = ['typescript', 'javascript', 'python', 'rust', 'go', 'java', 'cpp', 'other']

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!prompt.trim() || generating) return

    await onGenerate(selectedType, prompt.trim(), selectedLanguage, context.trim() || undefined)
    setPrompt('')
    setContext('')
  }

  const Icon = generationTypes.find(t => t.type === selectedType)?.icon || Code

  return (
    <div className={`flex flex-col gap-4 ${className}`}>
      {/* Generation Type Selector */}
      <div className="flex flex-wrap gap-2">
        {generationTypes.map(({ type, label, icon: TypeIcon, description }) => (
          <button
            key={type}
            type="button"
            onClick={() => setSelectedType(type)}
            className={`flex items-center gap-2 px-3 py-2 rounded text-sm font-medium transition-colors ${
              selectedType === type
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
            title={description}
          >
            <TypeIcon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        {/* Language Selector */}
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-400">Language:</label>
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            className="px-3 py-1.5 rounded bg-gray-800 text-gray-200 border border-gray-700 text-sm focus:outline-none focus:border-blue-500"
            disabled={generating}
          >
            {languages.map((lang) => (
              <option key={lang} value={lang}>
                {lang.charAt(0).toUpperCase() + lang.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Prompt Input */}
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-gray-300 flex items-center gap-2">
            <Icon className="w-4 h-4" />
            Prompt
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={`Describe the ${selectedType} you want to generate...`}
            className="w-full px-4 py-3 rounded bg-gray-800 text-gray-200 border border-gray-700 focus:outline-none focus:border-blue-500 resize-none"
            rows={4}
            disabled={generating}
          />
        </div>

        {/* Context Input (Optional) */}
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-gray-300">
            Context (Optional)
          </label>
          <textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Additional context, existing code, or requirements..."
            className="w-full px-4 py-3 rounded bg-gray-800 text-gray-200 border border-gray-700 focus:outline-none focus:border-blue-500 resize-none"
            rows={3}
            disabled={generating}
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!prompt.trim() || generating}
          className="flex items-center justify-center gap-2 px-4 py-3 rounded bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {generating ? (
            <>
              <LoadingSpinner size="sm" />
              <span>Generating...</span>
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              <span>Generate {generationTypes.find(t => t.type === selectedType)?.label}</span>
            </>
          )}
        </button>
      </form>
    </div>
  )
}

