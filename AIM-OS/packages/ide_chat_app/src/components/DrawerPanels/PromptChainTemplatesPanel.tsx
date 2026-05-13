/**
 * Prompt Chain Templates Panel
 * Left drawer panel for Prompt Chains tab
 * Provides template library, template creation, and chain building assistance
 */

import React, { useState, useEffect, useCallback } from 'react'
import { 
  FileText, 
  Plus, 
  Search, 
  Star, 
  Filter,
  Play,
  Edit2,
  Trash2,
  Copy,
  Eye,
  Download,
  Upload,
  Layers,
  Zap,
  Code,
  Database,
  Link as LinkIcon,
  GitBranch,
  CheckCircle,
  RefreshCw
} from 'lucide-react'
import { getServiceBridge } from '../../services/serviceBridge'

const serviceBridge = getServiceBridge()

interface ChainTemplate {
  id: string
  atom_id?: string
  chain_id?: string
  name: string
  description: string
  category: string
  tags: string[]
  nodes: any[]
  edges: any[]
  usageCount: number
  rating?: number
  createdAt: Date
  createdBy: string
  isSystemTemplate: boolean
}

interface PromptChainTemplatesPanelProps {
  onSelectTemplate?: (template: ChainTemplate) => void
  onUseTemplate?: (template: ChainTemplate) => void
}

export const PromptChainTemplatesPanel: React.FC<PromptChainTemplatesPanelProps> = ({
  onSelectTemplate,
  onUseTemplate
}) => {
  const [templates, setTemplates] = useState<ChainTemplate[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)

  // Categories for templates
  const categories = [
    { id: 'all', label: 'All Templates', icon: Layers },
    { id: 'foundation', label: 'Foundation', icon: Database },
    { id: 'orchestration', label: 'Orchestration', icon: GitBranch },
    { id: 'development', label: 'Development', icon: Code },
    { id: 'quality', label: 'Quality', icon: CheckCircle },
    { id: 'system', label: 'System', icon: Zap }
  ]

  // Load templates (filter for isTemplate: true)
  const loadTemplates = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const result = await serviceBridge.listPromptChains({
        isTemplate: true
      }, 100)
      
      if (result.success && result.chains) {
        const convertedTemplates: ChainTemplate[] = result.chains.map((chain: any) => ({
          id: chain.chain_id || chain.atom_id || `template_${Date.now()}`,
          atom_id: chain.atom_id,
          chain_id: chain.chain_id,
          name: chain.name,
          description: chain.description || '',
          category: chain.metadata?.category || 'general',
          tags: chain.metadata?.tags || [],
          nodes: chain.nodes || [],
          edges: chain.edges || [],
          usageCount: chain.metadata?.usageCount || 0,
          rating: chain.metadata?.rating,
          createdAt: new Date(chain.created_at || chain.updated_at || Date.now()),
          createdBy: chain.created_by || 'unknown',
          isSystemTemplate: chain.created_by === 'system' || chain.metadata?.isSystemTemplate === true
        }))
        
        setTemplates(convertedTemplates)
      } else {
        setError(result.error || 'Failed to load templates')
      }
    } catch (err) {
      console.error('Failed to load templates:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadTemplates()
    // Poll every 10 seconds for new templates
    const interval = setInterval(loadTemplates, 10000)
    return () => clearInterval(interval)
  }, [loadTemplates])

  // Filter templates
  const filteredTemplates = templates.filter(template => {
    const matchesSearch = searchQuery === '' || 
      template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    
    const matchesCategory = selectedCategory === null || 
      selectedCategory === 'all' || 
      template.category === selectedCategory
    
    return matchesSearch && matchesCategory
  })

  const handleUseTemplate = (template: ChainTemplate) => {
    if (onUseTemplate) {
      onUseTemplate(template)
    } else if (onSelectTemplate) {
      onSelectTemplate(template)
    }
    // TODO: Instantiate template as new chain
  }

  const handleSaveTemplate = async (chainData: any) => {
    try {
      setLoading(true)
      const result = await serviceBridge.createPromptChain({
        name: chainData.name || 'Untitled Template',
        description: chainData.description || '',
        nodes: chainData.nodes || [],
        edges: chainData.edges || [],
        executionType: chainData.executionType || 'sequential',
        entryPoint: chainData.entryPoint,
        metadata: {
          ...chainData.metadata,
          isTemplate: true,
          category: chainData.category || 'general',
          tags: chainData.tags || [],
        },
        created_by: 'user'
      })
      
      if (result.success) {
        await loadTemplates() // Refresh templates list
        return result
      } else {
        throw new Error(result.error || 'Failed to save template')
      }
    } catch (err) {
      console.error('Failed to save template:', err)
      setError(err instanceof Error ? err.message : 'Failed to save template')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const handleLoadTemplate = async (templateId: string) => {
    try {
      setLoading(true)
      const result = await serviceBridge.getPromptChain(templateId)
      
      if (result.success && result.chain) {
        // Emit event for chain editor to load this template
        window.dispatchEvent(new CustomEvent('chain-template-loaded', {
          detail: { template: result.chain }
        }))
        return result.chain
      } else {
        throw new Error(result.error || 'Failed to load template')
      }
    } catch (err) {
      console.error('Failed to load template:', err)
      setError(err instanceof Error ? err.message : 'Failed to load template')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteTemplate = async (templateId: string) => {
    if (!confirm('Are you sure you want to delete this template?')) {
      return
    }
    
    try {
      setLoading(true)
      // TODO: Implement delete template via MCP
      // For now, just remove from local state
      setTemplates(prev => prev.filter(t => t.id !== templateId))
      await loadTemplates() // Refresh
    } catch (err) {
      console.error('Failed to delete template:', err)
      setError(err instanceof Error ? err.message : 'Failed to delete template')
    } finally {
      setLoading(false)
    }
  }

  const getCategoryIcon = (categoryId: string) => {
    const category = categories.find(c => c.id === categoryId)
    return category?.icon || Layers
  }

  return (
    <div className="h-full flex flex-col bg-cursor-sidebar text-cursor-text" style={{ backgroundColor: '#252526' }}>
      {/* Header */}
      <div className="p-2 border-b border-cursor-border">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-cursor-status-bar" />
            <h2 className="text-sm font-semibold" style={{ fontSize: '13px' }}>Chain Templates</h2>
          </div>
          <button
            onClick={handleCreateTemplate}
            className="p-1 bg-cursor-status-bar hover:bg-cursor-status-bar/80 rounded cursor-button"
            title="Create new template"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Search */}
        <div className="relative mb-2">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3.5 h-3.5 text-cursor-text-secondary" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search templates..."
            className="w-full bg-cursor-input-bg text-cursor-text px-7 py-1 rounded border border-cursor-border focus:outline-none focus:border-cursor-status-bar cursor-input"
            style={{ fontSize: '11px' }}
          />
        </div>

        {/* Category Filter */}
        <div className="flex gap-1 overflow-x-auto cursor-scrollbar pb-1">
          {categories.map((category) => {
            const Icon = category.icon
            const isActive = selectedCategory === category.id || (category.id === 'all' && selectedCategory === null)
            return (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id === 'all' ? null : category.id)}
                className={`flex items-center gap-1 px-2 py-1 rounded text-xs whitespace-nowrap transition-colors ${
                  isActive
                    ? 'bg-cursor-status-bar text-white'
                    : 'bg-cursor-sidebar text-cursor-text-secondary hover:bg-cursor-hover'
                }`}
                style={{ fontSize: '11px' }}
              >
                <Icon className="w-3 h-3" />
                <span>{category.label}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Templates List */}
      <div className="flex-1 overflow-y-auto p-2 cursor-scrollbar">
        {loading && templates.length === 0 && (
          <div className="flex items-center justify-center p-4">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-cursor-status-bar"></div>
          </div>
        )}

        {error && (
          <div className="text-xs text-red-400 p-2 mb-2 bg-red-900/20 rounded">
            {error}
          </div>
        )}

        {!loading && filteredTemplates.length === 0 && (
          <div className="flex flex-col items-center justify-center p-8 text-center">
            <FileText className="w-12 h-12 text-cursor-text-secondary mb-2 opacity-50" />
            <p className="text-sm text-cursor-text-secondary mb-1">No templates found</p>
            <p className="text-xs text-cursor-text-muted">
              {searchQuery ? 'Try a different search' : 'Create your first template'}
            </p>
          </div>
        )}

        <div className="space-y-2">
          {filteredTemplates.map((template) => {
            const CategoryIcon = getCategoryIcon(template.category)
            const isSelected = selectedTemplate === template.id
            
            return (
              <div
                key={template.id}
                className={`bg-cursor-sidebar rounded p-2 border transition-all cursor-pointer cursor-list-item ${
                  isSelected ? 'border-cursor-status-bar' : 'border-cursor-border'
                }`}
                onClick={() => {
                  setSelectedTemplate(template.id === selectedTemplate ? null : template.id)
                  if (onSelectTemplate) {
                    onSelectTemplate(template)
                  }
                }}
              >
                {/* Template Header */}
                <div className="flex items-start justify-between mb-1.5">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 mb-1">
                      <CategoryIcon className="w-3.5 h-3.5 text-cursor-status-bar flex-shrink-0" />
                      <h3 className="text-xs font-semibold text-cursor-text truncate" style={{ fontSize: '12px' }}>
                        {template.name}
                      </h3>
                      {template.isSystemTemplate && (
                        <span className="px-1 py-0.5 text-[10px] rounded bg-blue-900/30 text-blue-300 flex-shrink-0">
                          System
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-cursor-text-secondary mb-1 line-clamp-2" style={{ fontSize: '11px' }}>
                      {template.description}
                    </p>
                  </div>
                </div>

                {/* Template Metadata */}
                <div className="flex items-center gap-2 text-xs text-cursor-text-secondary mb-1.5" style={{ fontSize: '10px' }}>
                  <span>{template.nodes?.length || 0} nodes</span>
                  <span>•</span>
                  <span>{template.edges?.length || 0} edges</span>
                  {template.usageCount > 0 && (
                    <>
                      <span>•</span>
                      <span>{template.usageCount} uses</span>
                    </>
                  )}
                  {template.rating && (
                    <>
                      <span>•</span>
                      <div className="flex items-center gap-0.5">
                        <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                        <span>{template.rating.toFixed(1)}</span>
                      </div>
                    </>
                  )}
                </div>

                {/* Tags */}
                {template.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-1.5">
                    {template.tags.slice(0, 3).map((tag) => (
                      <span
                        key={tag}
                        className="px-1.5 py-0.5 text-[10px] rounded bg-cursor-input-bg text-cursor-text-secondary"
                        style={{ fontSize: '9px' }}
                      >
                        {tag}
                      </span>
                    ))}
                    {template.tags.length > 3 && (
                      <span className="text-xs text-cursor-text-muted" style={{ fontSize: '9px' }}>
                        +{template.tags.length - 3}
                      </span>
                    )}
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center gap-1 pt-1 border-t border-cursor-border">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleUseTemplate(template)
                          }}
                          className="flex-1 px-2 py-1 bg-cursor-status-bar hover:bg-cursor-status-bar/80 rounded text-xs cursor-button flex items-center justify-center gap-1"
                          style={{ fontSize: '11px' }}
                          title="Use this template"
                        >
                          <Play className="w-3 h-3" />
                          Use
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleLoadTemplate(template.id)
                          }}
                          className="px-2 py-1 bg-cursor-hover hover:bg-cursor-active rounded cursor-button"
                          title="Load template into editor"
                        >
                          <Eye className="w-3 h-3" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteTemplate(template.id)
                          }}
                          className="px-2 py-1 bg-cursor-hover hover:bg-red-600 rounded cursor-button"
                          title="Delete template"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="p-2 border-t border-cursor-border">
        <div className="flex items-center justify-between text-xs text-cursor-text-secondary">
          <span style={{ fontSize: '10px' }}>
            {filteredTemplates.length} template{filteredTemplates.length !== 1 ? 's' : ''}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => loadTemplates()}
              className="p-1 hover:bg-cursor-hover rounded cursor-button"
              title="Refresh templates"
            >
              <RefreshCw className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PromptChainTemplatesPanel

