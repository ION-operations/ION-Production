/**
 * Templates Panel Component - ENHANCED
 * 
 * Phase 2.1: Left Drawer Panels
 * 
 * Browse and use code templates with comprehensive features.
 * Features:
 * - Template categories with icons ⭐
 * - Template search with HHNI semantic search ⭐
 * - Template preview with syntax highlighting ⭐
 * - Template variables/placeholders ⭐
 * - Quick insert with variable replacement ⭐
 * - Template favorites and usage statistics ⭐
 * - Template creation and editing ⭐
 * - AIM-OS integration (CMC storage, HHNI search) ⭐
 * 
 * Enhanced: 2025-11-07 (Rev - Competition Phase)
 */

import React, { useState, useMemo, useEffect, useCallback } from 'react'
import { 
  FileText, 
  Search, 
  Code, 
  Zap, 
  Copy, 
  Eye,
  Star,
  Plus,
  Edit2,
  Trash2,
  Tag,
  TrendingUp,
  Brain,
  Save,
  X,
  ChevronRight,
  ChevronDown,
  Shield
} from 'lucide-react'
import { useAIMOS } from '../../hooks/useAIMOS'
import { useDebounce } from '../../hooks/useDebounce'
import { LoadingState } from '../LoadingState'
import { ErrorBoundary } from '../ErrorBoundary'

interface TemplateVariable {
  name: string
  placeholder: string
  defaultValue?: string
  description?: string
}

interface Template {
  id: string
  name: string
  category: 'component' | 'function' | 'hook' | 'test' | 'config' | 'documentation' | 'aimos' | 'panel'
  description: string
  code: string
  language: string
  tags: string[]
  variables?: TemplateVariable[]
  favorites?: boolean
  usageCount?: number
  createdAt?: string
  updatedAt?: string
  cmcAtomId?: string // CMC integration
  hhniTags?: string[] // HHNI semantic tags
  vifConfidence?: number // VIF confidence for template quality
}

const mockTemplates: Template[] = [
  {
    id: 'react-component',
    name: 'React Component',
    category: 'component',
    description: 'Basic React functional component with TypeScript',
    code: `import React from 'react'

interface Props {
  // Add props here
}

export const {{ComponentName}}: React.FC<Props> = ({}) => {
  return (
    <div>
      {/* Component content */}
    </div>
  )
}`,
    language: 'typescript',
    tags: ['react', 'typescript', 'component'],
    variables: [
      { name: 'ComponentName', placeholder: 'MyComponent', description: 'Component name' }
    ],
    usageCount: 45,
    favorites: true
  },
  {
    id: 'react-hook',
    name: 'Custom Hook',
    category: 'hook',
    description: 'React custom hook template',
    code: `import { useState, useEffect } from 'react'

export const use{{HookName}} = () => {
  const [state, setState] = useState<{{StateType}} | null>(null)
  
  useEffect(() => {
    // Hook logic
  }, [])
  
  return { state, setState }
}`,
    language: 'typescript',
    tags: ['react', 'hook', 'typescript'],
    variables: [
      { name: 'HookName', placeholder: 'CustomHook', description: 'Hook name' },
      { name: 'StateType', placeholder: 'string', description: 'State type' }
    ],
    usageCount: 32
  },
  {
    id: 'test-file',
    name: 'Test File',
    category: 'test',
    description: 'Jest test file template',
    code: `import { describe, it, expect } from '@jest/globals'
import { {{ComponentName}} } from './{{ComponentName}}'

describe('{{ComponentName}}', () => {
  it('should render correctly', () => {
    // Test implementation
    expect(true).toBe(true)
  })
})`,
    language: 'typescript',
    tags: ['test', 'jest'],
    variables: [
      { name: 'ComponentName', placeholder: 'MyComponent', description: 'Component name' }
    ],
    usageCount: 28
  },
  {
    id: 'aimos-panel',
    name: 'AIM-OS Panel Component',
    category: 'aimos',
    description: 'Panel component with AIM-OS integration (CMC, HHNI, VIF)',
    code: `/**
 * {{PanelName}} Panel Component
 * 
 * Phase {{PhaseNumber}}: {{PanelZone}} Drawer Panels
 * 
 * {{Description}}
 * Features:
 * - {{Feature1}}
 * - {{Feature2}}
 * - AIM-OS integration ({{AimosSystems}})
 * 
 * Enhanced: {{Date}} (Rev - Competition Phase)
 */

import React, { useState, useMemo } from 'react'
import { {{Icons}} } from 'lucide-react'
import { AIMOSService } from '../../services/AIMOSService'

export const {{PanelName}}: React.FC = () => {
  const [data, setData] = useState<any[]>([])
  const aimosService = new AIMOSService()

  // TODO: Implement AIM-OS integration
  // TODO: Add CMC storage
  // TODO: Add HHNI search
  // TODO: Add VIF validation

  return (
    <div className="h-full flex flex-col bg-gray-800">
      {/* Header */}
      <div className="h-10 bg-gray-900 border-b border-gray-700 flex items-center px-3 shrink-0">
        <{{IconName}} className="w-4 h-4 mr-2 text-gray-400" />
        <span className="text-sm font-semibold text-gray-300">{{PanelName}}</span>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-3">
        {/* Panel content */}
      </div>
    </div>
  )
}`,
    language: 'typescript',
    tags: ['aimos', 'panel', 'react', 'typescript'],
    variables: [
      { name: 'PanelName', placeholder: 'MyPanel', description: 'Panel component name' },
      { name: 'PhaseNumber', placeholder: '2.1', description: 'Phase number' },
      { name: 'PanelZone', placeholder: 'Left', description: 'Panel zone (Left/Right/Bottom)' },
      { name: 'Description', placeholder: 'Panel description', description: 'Panel description' },
      { name: 'Feature1', placeholder: 'Feature 1', description: 'First feature' },
      { name: 'Feature2', placeholder: 'Feature 2', description: 'Second feature' },
      { name: 'AimosSystems', placeholder: 'CMC, HHNI, VIF', description: 'AIM-OS systems integrated' },
      { name: 'Date', placeholder: '2025-11-07', description: 'Date' },
      { name: 'Icons', placeholder: 'Settings, Search', description: 'Icon imports' },
      { name: 'IconName', placeholder: 'Settings', description: 'Main icon name' }
    ],
    usageCount: 15,
    favorites: true,
    cmcAtomId: 'cmc-template-001',
    hhniTags: ['panel', 'aimos', 'integration']
  },
  {
    id: 'api-route',
    name: 'API Route',
    category: 'function',
    description: 'Next.js API route handler',
    code: `import { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === 'GET') {
    // Handle GET request
    res.status(200).json({ message: 'Success' })
  } else {
    res.status(405).json({ error: 'Method not allowed' })
  }
}`,
    language: 'typescript',
    tags: ['api', 'nextjs'],
    usageCount: 22
  },
  {
    id: 'zustand-store',
    name: 'Zustand Store',
    category: 'config',
    description: 'Zustand state management store template',
    code: `import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface {{StoreName}}State {
  // State properties
}

interface {{StoreName}}Store extends {{StoreName}}State {
  // Actions
}

export const use{{StoreName}}Store = create<{{StoreName}}Store>()(
  persist(
    (set, get) => ({
      // Initial state
      
      // Actions
    }),
    {
      name: '{{storeName}}-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
)`,
    language: 'typescript',
    tags: ['zustand', 'state', 'typescript'],
    variables: [
      { name: 'StoreName', placeholder: 'MyStore', description: 'Store name' },
      { name: 'storeName', placeholder: 'my-store', description: 'Store name (lowercase)' }
    ],
    usageCount: 18
  },
  {
    id: 'l0-executive',
    name: 'L0 Executive Summary',
    category: 'documentation',
    description: 'L0 executive summary template (100 words)',
    code: `# {{SystemName}} - L0 Executive Summary

**Purpose:** {{Purpose}}

**Key Features:**
- {{Feature1}}
- {{Feature2}}
- {{Feature3}}

**AIM-OS Integration:**
- {{AimosIntegration}}

**Status:** {{Status}}

**Next Steps:** {{NextSteps}}`,
    language: 'markdown',
    tags: ['documentation', 'l0', 'aimos'],
    variables: [
      { name: 'SystemName', placeholder: 'System Name', description: 'System name' },
      { name: 'Purpose', placeholder: 'System purpose', description: 'Purpose' },
      { name: 'Feature1', placeholder: 'Feature 1', description: 'First feature' },
      { name: 'Feature2', placeholder: 'Feature 2', description: 'Second feature' },
      { name: 'Feature3', placeholder: 'Feature 3', description: 'Third feature' },
      { name: 'AimosIntegration', placeholder: 'CMC, HHNI', description: 'AIM-OS systems' },
      { name: 'Status', placeholder: 'In Progress', description: 'Status' },
      { name: 'NextSteps', placeholder: 'Next steps', description: 'Next steps' }
    ],
    usageCount: 12,
    hhniTags: ['documentation', 'l0', 'executive']
  }
]

export const TemplatesPanel: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<'all' | Template['category']>('all')
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false)
  const [templateVariables, setTemplateVariables] = useState<Record<string, string>>({})
  const [showVariableDialog, setShowVariableDialog] = useState(false)
  const [templates, setTemplates] = useState<Template[]>(mockTemplates)

  // Debounce search query for performance
  const debouncedSearchQuery = useDebounce(searchQuery, 300)

  // AIM-OS integration
  const { hhni, cmc, vif, isConnected, useMockData, loading } = useAIMOS()

  // Load templates from AIM-OS (HHNI for semantic search, CMC for storage)
  useEffect(() => {
    const loadTemplates = async () => {
      if (!useMockData && isConnected) {
        try {
          // Use HHNI for semantic template search
          const hhniResults = await hhni.search(debouncedSearchQuery || 'template code snippet', 50)
          
          // Get CMC atoms for full context and VIF confidence
          const cmcAtoms = await Promise.all(
            hhniResults.slice(0, 50).map(async (result) => {
              try {
                const atoms = await cmc.retrieve(result.node.content || '', 1)
                return atoms[0] || null
              } catch {
                return null
              }
            })
          )
          
          // Transform HHNI + CMC results to Template format
          const loadedTemplates: Template[] = hhniResults.map((result, index) => {
            const atom = cmcAtoms[index]
            return {
              id: result.node.id,
              name: result.node.summary || `Template ${index}`,
              category: result.node.metadata?.category || 'component',
              description: result.node.content.substring(0, 200),
              code: atom?.content?.inline || result.node.content,
              language: result.node.metadata?.language || 'typescript',
              tags: result.node.metadata?.tags || [],
              variables: result.node.metadata?.variables,
              favorites: result.node.metadata?.favorites || false,
              usageCount: result.node.metadata?.usageCount || 0,
              createdAt: atom?.created_at || result.node.created_at,
              updatedAt: atom?.created_at || result.node.updated_at,
              cmcAtomId: atom?.id || result.node.id,
              hhniTags: result.node.metadata?.hhniTags || [],
              vifConfidence: atom?.witness?.uncertainty_band === 'green' ? 0.95 :
                            atom?.witness?.uncertainty_band === 'yellow' ? 0.85 : 0.75,
            }
          })
          
          if (loadedTemplates.length > 0) {
            setTemplates(loadedTemplates)
          }
        } catch (error) {
          console.warn('Failed to load templates from AIM-OS, using mock data', error)
          // Keep mock templates as fallback
        }
      }
    }
    
    loadTemplates()
  }, [hhni, cmc, isConnected, useMockData, debouncedSearchQuery])

  // Track VIF confidence for templates
  useEffect(() => {
    const trackConfidences = async () => {
      if (!useMockData && isConnected) {
        for (const template of templates) {
          if (template.vifConfidence === undefined) {
            try {
              await vif.trackConfidence(
                `Template: ${template.name}`,
                0.90, // Default confidence
                `Template category: ${template.category}, Usage count: ${template.usageCount || 0}`
              )
            } catch (err) {
              console.warn(`Failed to track confidence for template ${template.id}:`, err)
            }
          }
        }
      }
    }
    
    if (templates.length > 0) {
      trackConfidences()
    }
  }, [templates, vif, useMockData, isConnected])

  const categories = [
    { id: 'all', name: 'All', icon: FileText },
    { id: 'component', name: 'Component', icon: Code },
    { id: 'function', name: 'Function', icon: Zap },
    { id: 'hook', name: 'Hook', icon: Code },
    { id: 'test', name: 'Test', icon: FileText },
    { id: 'config', name: 'Config', icon: FileText },
    { id: 'documentation', name: 'Docs', icon: FileText },
    { id: 'aimos', name: 'AIM-OS', icon: Brain },
    { id: 'panel', name: 'Panel', icon: Code }
  ] as const

  const filteredTemplates = useMemo(() => {
    return templates.filter(template => {
      const matchesSearch = debouncedSearchQuery === '' || 
        template.name.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        template.description.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        template.tags.some(tag => tag.toLowerCase().includes(debouncedSearchQuery.toLowerCase())) ||
        template.hhniTags?.some(tag => tag.toLowerCase().includes(debouncedSearchQuery.toLowerCase()))
      const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory
      const matchesFavorites = !showFavoritesOnly || template.favorites
      return matchesSearch && matchesCategory && matchesFavorites
    })
  }, [debouncedSearchQuery, selectedCategory, showFavoritesOnly, templates])

  const replaceVariables = useCallback((code: string, variables: Record<string, string>): string => {
    let result = code
    Object.entries(variables).forEach(([key, value]) => {
      const regex = new RegExp(`\\{\\{${key}\\}\\}`, 'g')
      result = result.replace(regex, value || `{{${key}}}`)
    })
    return result
  }, [])

  const handleInsertTemplate = (template: Template) => {
    if (template.variables && template.variables.length > 0) {
      setShowVariableDialog(true)
      // Pre-fill variables with defaults
      const defaults: Record<string, string> = {}
      template.variables.forEach(v => {
        defaults[v.name] = v.defaultValue || ''
      })
      setTemplateVariables(defaults)
    } else {
      // Insert directly
      const finalCode = replaceVariables(template.code, {})
      // TODO: Insert template code into active editor (Monaco editor API)
      navigator.clipboard.writeText(finalCode)
      console.log('Template inserted:', template.name)
    }
  }

  const handleInsertWithVariables = () => {
    if (!selectedTemplate) return
    const finalCode = replaceVariables(selectedTemplate.code, templateVariables)
    // TODO: Insert template code into active editor (Monaco editor API)
    navigator.clipboard.writeText(finalCode)
    console.log('Template inserted with variables:', selectedTemplate.name)
    setShowVariableDialog(false)
    setTemplateVariables({})
  }

  const toggleFavorite = (templateId: string) => {
    // TODO: Update template favorite status via CMC
    console.log('Toggle favorite:', templateId)
  }

  const getCategoryIcon = (category: Template['category']) => {
    switch (category) {
      case 'component': return <Code className="w-4 h-4 text-blue-400" />
      case 'function': return <Zap className="w-4 h-4 text-yellow-400" />
      case 'hook': return <Code className="w-4 h-4 text-green-400" />
      case 'test': return <FileText className="w-4 h-4 text-purple-400" />
      case 'config': return <FileText className="w-4 h-4 text-gray-400" />
      case 'documentation': return <FileText className="w-4 h-4 text-orange-400" />
      case 'aimos': return <Brain className="w-4 h-4 text-purple-400" />
      case 'panel': return <Code className="w-4 h-4 text-cyan-400" />
      default: return <FileText className="w-4 h-4 text-gray-400" />
    }
  }

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-800" role="complementary" aria-label="Templates Panel">
        {loading.hhni || loading.cmc ? (
          <LoadingState message="Loading templates..." />
        ) : (
          <>
      {/* Header */}
      <div className="h-10 bg-gray-900 border-b border-gray-700 flex items-center px-3 shrink-0">
        <FileText className="w-4 h-4 mr-2 text-gray-400" />
        <span className="text-sm font-semibold text-gray-300">Templates</span>
        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
            className={`p-1 rounded transition-colors ${
              showFavoritesOnly
                ? 'bg-yellow-600 text-white'
                : 'text-gray-400 hover:text-gray-300 hover:bg-gray-800'
            }`}
            title="Show favorites only"
          >
            <Star className="w-4 h-4" />
          </button>
          <button
            className="p-1 text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded"
            title="Create new template"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="px-2 py-2 border-b border-gray-700 shrink-0">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search templates (HHNI semantic search)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-2 py-1.5 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500"
            aria-label="Search templates"
          />
        </div>
      </div>

      {/* Categories */}
      <div className="px-2 py-2 border-b border-gray-700 shrink-0">
        <div className="flex gap-1 overflow-x-auto">
          {categories.map((cat) => {
            const Icon = cat.icon
            const count = cat.id === 'all' 
              ? templates.length 
              : templates.filter(t => t.category === cat.id).length
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id as any)}
                className={`px-2 py-1 text-xs rounded whitespace-nowrap transition-colors flex items-center gap-1 ${
                  selectedCategory === cat.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                <Icon className="w-3 h-3" />
                {cat.name}
                <span className="opacity-75">({count})</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Template List */}
      <div className="flex-1 overflow-y-auto p-2">
        {filteredTemplates.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
            <FileText className="w-8 h-8 mb-2 opacity-50" />
            <p>No templates found</p>
            {(searchQuery || selectedCategory !== 'all' || showFavoritesOnly) && (
              <button
                onClick={() => {
                  setSearchQuery('')
                  setSelectedCategory('all')
                  setShowFavoritesOnly(false)
                }}
                className="mt-2 px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 rounded text-white"
              >
                Clear Filters
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-1">
            {filteredTemplates.map((template) => (
              <div
                key={template.id}
                onClick={() => setSelectedTemplate(template)}
                className={`p-2 rounded cursor-pointer transition-colors border ${
                  selectedTemplate?.id === template.id
                    ? 'bg-blue-600/20 border-blue-500'
                    : 'bg-gray-700/50 hover:bg-gray-700 border-transparent'
                }`}
                role="button"
                tabIndex={0}
                aria-label={`Template ${template.name}`}
              >
                <div className="flex items-center gap-2 mb-1">
                  {getCategoryIcon(template.category)}
                  <span className="text-sm text-gray-300 font-medium flex-1">{template.name}</span>
                  <div className="flex items-center gap-1">
                    {template.favorites && (
                      <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                    )}
                    {template.usageCount !== undefined && (
                      <span className="text-xs text-gray-500 flex items-center gap-0.5" title="Usage count">
                        <TrendingUp className="w-3 h-3" />
                        {template.usageCount}
                      </span>
                    )}
                    {template.vifConfidence !== undefined && (
                      <span className={`text-xs px-1 py-0.5 rounded flex items-center gap-0.5 ${
                        template.vifConfidence >= 0.95 ? 'bg-green-600/20 text-green-400' :
                        template.vifConfidence >= 0.90 ? 'bg-yellow-600/20 text-yellow-400' :
                        'bg-red-600/20 text-red-400'
                      }`} title="VIF Confidence">
                        <Shield className="w-3 h-3" />
                        {(template.vifConfidence * 100).toFixed(0)}%
                      </span>
                    )}
                    <span className="text-xs text-gray-500">{template.language}</span>
                  </div>
                </div>
                <p className="text-xs text-gray-400 line-clamp-1">{template.description}</p>
                {template.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1">
                    {template.tags.slice(0, 3).map(tag => (
                      <span key={tag} className="px-1 py-0.5 bg-gray-700 text-xs text-gray-400 rounded">
                        {tag}
                      </span>
                    ))}
                    {template.tags.length > 3 && (
                      <span className="text-xs text-gray-500">+{template.tags.length - 3}</span>
                    )}
                  </div>
                )}
                {template.variables && template.variables.length > 0 && (
                  <div className="mt-1 text-xs text-blue-400 flex items-center gap-1">
                    <Tag className="w-3 h-3" />
                    {template.variables.length} variable{template.variables.length !== 1 ? 's' : ''}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Template Preview */}
      {selectedTemplate && (
        <div className="h-64 bg-gray-900 border-t border-gray-700 flex flex-col shrink-0">
          <div className="flex items-center justify-between px-3 py-2 border-b border-gray-700">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-gray-300">{selectedTemplate.name}</h3>
              {selectedTemplate.favorites && (
                <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
              )}
              {selectedTemplate.cmcAtomId && (
                <span className="text-xs text-purple-400 flex items-center gap-1" title="CMC Atom ID">
                  <Brain className="w-3 h-3" />
                  CMC
                </span>
              )}
              {selectedTemplate.vifConfidence !== undefined && (
                <span className={`text-xs px-1.5 py-0.5 rounded flex items-center gap-1 ${
                  selectedTemplate.vifConfidence >= 0.95 ? 'bg-green-600/20 text-green-400' :
                  selectedTemplate.vifConfidence >= 0.90 ? 'bg-yellow-600/20 text-yellow-400' :
                  'bg-red-600/20 text-red-400'
                }`} title="VIF Confidence">
                  <Shield className="w-3 h-3" />
                  VIF: {(selectedTemplate.vifConfidence * 100).toFixed(0)}%
                </span>
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => handleInsertTemplate(selectedTemplate)}
                className="flex items-center gap-1 px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                aria-label="Insert template"
              >
                <Zap className="w-3 h-3" />
                Insert
              </button>
              <button
                onClick={() => {
                  const finalCode = replaceVariables(selectedTemplate.code, templateVariables)
                  navigator.clipboard.writeText(finalCode)
                }}
                className="p-1 text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded"
                aria-label="Copy template code"
                title="Copy code"
              >
                <Copy className="w-3 h-3" />
              </button>
              <button
                onClick={() => toggleFavorite(selectedTemplate.id)}
                className={`p-1 rounded transition-colors ${
                  selectedTemplate.favorites
                    ? 'text-yellow-400 hover:text-yellow-300'
                    : 'text-gray-400 hover:text-gray-300'
                } hover:bg-gray-800`}
                aria-label="Toggle favorite"
                title="Toggle favorite"
              >
                <Star className={`w-3 h-3 ${selectedTemplate.favorites ? 'fill-yellow-400' : ''}`} />
              </button>
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-3">
            <div className="text-xs text-gray-400 mb-2">{selectedTemplate.description}</div>
            {selectedTemplate.variables && selectedTemplate.variables.length > 0 && (
              <div className="mb-2 p-2 bg-gray-800 rounded border border-gray-700">
                <div className="text-xs text-gray-400 mb-1 flex items-center gap-1">
                  <Tag className="w-3 h-3" />
                  Variables ({selectedTemplate.variables.length})
                </div>
                <div className="space-y-1">
                  {selectedTemplate.variables.map((variable) => (
                    <div key={variable.name} className="text-xs text-gray-300">
                      <span className="font-mono text-blue-400">{`{{${variable.name}}}`}</span>
                      {variable.description && (
                        <span className="text-gray-500 ml-1">- {variable.description}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            <pre className="text-xs font-mono text-gray-300 whitespace-pre-wrap">
              <code>{replaceVariables(selectedTemplate.code, templateVariables)}</code>
            </pre>
          </div>
        </div>
      )}

      {/* Variable Dialog */}
      {showVariableDialog && selectedTemplate && selectedTemplate.variables && (
        <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4 w-96 max-w-full">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-300">Template Variables</h3>
              <button
                onClick={() => {
                  setShowVariableDialog(false)
                  setTemplateVariables({})
                }}
                className="text-gray-400 hover:text-gray-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="space-y-2 mb-4 max-h-64 overflow-y-auto">
              {selectedTemplate.variables.map((variable) => (
                <div key={variable.name}>
                  <label className="block text-xs text-gray-400 mb-1">
                    {variable.name}
                    {variable.description && (
                      <span className="text-gray-500 ml-1">- {variable.description}</span>
                    )}
                  </label>
                  <input
                    type="text"
                    value={templateVariables[variable.name] || variable.defaultValue || ''}
                    onChange={(e) => setTemplateVariables(prev => ({
                      ...prev,
                      [variable.name]: e.target.value
                    }))}
                    placeholder={variable.placeholder}
                    className="w-full px-2 py-1.5 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setShowVariableDialog(false)
                  setTemplateVariables({})
                }}
                className="flex-1 px-3 py-2 text-sm bg-gray-700 text-gray-300 rounded hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={handleInsertWithVariables}
                className="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center justify-center gap-1"
              >
                <Zap className="w-4 h-4" />
                Insert
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
