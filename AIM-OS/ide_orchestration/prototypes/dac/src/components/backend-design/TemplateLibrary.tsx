// Template Library - Sidebar with all available templates
// Beautiful categorized list with drag-and-drop

import React, { useState, useMemo } from 'react'
import { Search, ChevronDown, ChevronRight, Star, Download, Package, Sparkles } from 'lucide-react'
import { Template, TemplateCategory } from './types'
import { TEMPLATES, CATEGORIES, getCategoryConfig, searchTemplates } from './templates'

interface TemplateLibraryProps {
  onDragStart: (e: React.DragEvent, template: Template) => void
  searchQuery: string
  onSearchChange: (query: string) => void
  selectedCategory: TemplateCategory | 'all'
  onCategoryChange: (category: TemplateCategory | 'all') => void
}

export const TemplateLibrary: React.FC<TemplateLibraryProps> = ({
  onDragStart,
  searchQuery,
  onSearchChange,
  selectedCategory,
  onCategoryChange,
}) => {
  const [collapsedCategories, setCollapsedCategories] = useState<Set<string>>(new Set())
  const [hoveredTemplate, setHoveredTemplate] = useState<string | null>(null)

  const filteredTemplates = useMemo(() => {
    if (searchQuery) {
      return searchTemplates(searchQuery, selectedCategory === 'all' ? undefined : selectedCategory)
    }
    if (selectedCategory !== 'all') {
      return TEMPLATES.filter(t => t.type === selectedCategory)
    }
    return TEMPLATES
  }, [searchQuery, selectedCategory])

  // Group templates by category
  const templatesByCategory = useMemo(() => {
    const grouped: Record<string, Template[]> = {}
    filteredTemplates.forEach(t => {
      if (!grouped[t.type]) grouped[t.type] = []
      grouped[t.type].push(t)
    })
    return grouped
  }, [filteredTemplates])

  const toggleCategory = (categoryId: string) => {
    setCollapsedCategories(prev => {
      const next = new Set(prev)
      if (next.has(categoryId)) {
        next.delete(categoryId)
      } else {
        next.add(categoryId)
      }
      return next
    })
  }

  return (
    <div className="h-full flex flex-col bg-gray-900/95 backdrop-blur-xl">
      {/* Header */}
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Package className="w-4 h-4 text-white" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-gray-100">Templates</h2>
              <p className="text-[10px] text-gray-500">{TEMPLATES.length} available</p>
            </div>
          </div>
          <button className="p-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-gray-200 transition-colors">
            <Sparkles className="w-4 h-4" />
          </button>
        </div>
        
        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full h-9 pl-9 pr-3 rounded-lg bg-gray-800 border border-gray-700 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/50 transition-all"
          />
        </div>
      </div>

      {/* Category Pills */}
      <div className="p-3 border-b border-gray-800 overflow-x-auto">
        <div className="flex gap-1.5">
          <button
            onClick={() => onCategoryChange('all')}
            className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all ${
              selectedCategory === 'all'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-200'
            }`}
          >
            All ({TEMPLATES.length})
          </button>
          {CATEGORIES.slice(0, 6).map(cat => {
            const count = TEMPLATES.filter(t => t.type === cat.id).length
            const Icon = cat.icon
            return (
              <button
                key={cat.id}
                onClick={() => onCategoryChange(cat.id)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all flex items-center gap-1.5 ${
                  selectedCategory === cat.id
                    ? `text-white shadow-lg`
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-200'
                }`}
                style={{
                  backgroundColor: selectedCategory === cat.id ? cat.accentColor : undefined,
                  boxShadow: selectedCategory === cat.id ? `0 4px 15px ${cat.accentColor}40` : undefined,
                }}
              >
                <Icon className="w-3 h-3" />
                {cat.name}
              </button>
            )
          })}
        </div>
      </div>

      {/* Template List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {selectedCategory === 'all' ? (
          // Grouped by category
          Object.entries(templatesByCategory).map(([categoryId, templates]) => {
            const category = getCategoryConfig(categoryId as TemplateCategory)
            if (!category) return null
            const isCollapsed = collapsedCategories.has(categoryId)
            const Icon = category.icon

            return (
              <div key={categoryId} className="space-y-1">
                {/* Category Header */}
                <button
                  onClick={() => toggleCategory(categoryId)}
                  className="w-full flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-gray-800/50 transition-colors"
                >
                  {isCollapsed ? (
                    <ChevronRight className="w-4 h-4 text-gray-500" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-500" />
                  )}
                  <Icon className={`w-4 h-4 ${category.color}`} />
                  <span className="text-sm font-medium text-gray-200">{category.name}</span>
                  <span className="text-xs text-gray-500 ml-auto">{templates.length}</span>
                </button>

                {/* Templates */}
                {!isCollapsed && (
                  <div className="space-y-1 ml-4">
                    {templates.map(template => (
                      <TemplateCard
                        key={template.id}
                        template={template}
                        category={category}
                        isHovered={hoveredTemplate === template.id}
                        onHover={(id) => setHoveredTemplate(id)}
                        onDragStart={onDragStart}
                      />
                    ))}
                  </div>
                )}
              </div>
            )
          })
        ) : (
          // Flat list for selected category
          <div className="space-y-1">
            {filteredTemplates.map(template => {
              const category = getCategoryConfig(template.type)!
              return (
                <TemplateCard
                  key={template.id}
                  template={template}
                  category={category}
                  isHovered={hoveredTemplate === template.id}
                  onHover={(id) => setHoveredTemplate(id)}
                  onDragStart={onDragStart}
                />
              )
            })}
          </div>
        )}

        {filteredTemplates.length === 0 && (
          <div className="text-center py-12">
            <Search className="w-10 h-10 text-gray-600 mx-auto mb-3" />
            <p className="text-sm text-gray-400">No templates found</p>
            <p className="text-xs text-gray-600 mt-1">Try a different search term</p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-800 bg-gray-900/50">
        <div className="flex items-center justify-between text-[10px] text-gray-500">
          <span>Drag templates to canvas</span>
          <button className="flex items-center gap-1 text-blue-400 hover:text-blue-300">
            <Download className="w-3 h-3" />
            Import
          </button>
        </div>
      </div>
    </div>
  )
}

// Template Card Component
interface TemplateCardProps {
  template: Template
  category: ReturnType<typeof getCategoryConfig>
  isHovered: boolean
  onHover: (id: string | null) => void
  onDragStart: (e: React.DragEvent, template: Template) => void
}

const TemplateCard: React.FC<TemplateCardProps> = ({
  template,
  category,
  isHovered,
  onHover,
  onDragStart,
}) => {
  if (!category) return null
  const Icon = template.icon

  return (
    <div
      draggable
      onDragStart={(e) => {
        e.dataTransfer.setData('application/reactflow', JSON.stringify(template))
        e.dataTransfer.effectAllowed = 'move'
        onDragStart(e, template)
      }}
      onMouseEnter={() => onHover(template.id)}
      onMouseLeave={() => onHover(null)}
      className={`
        group p-2.5 rounded-lg cursor-grab active:cursor-grabbing
        transition-all duration-200 border
        ${isHovered 
          ? `${category.bgColor} ${category.borderColor} shadow-lg` 
          : 'bg-gray-800/30 border-transparent hover:bg-gray-800/50 hover:border-gray-700'
        }
      `}
      style={{
        boxShadow: isHovered ? `0 4px 20px ${category.accentColor}20` : undefined,
      }}
    >
      <div className="flex items-start gap-2.5">
        {/* Icon */}
        <div 
          className={`
            w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0
            ${category.bgColor} border ${category.borderColor}
            transition-transform duration-200
            ${isHovered ? 'scale-110' : ''}
          `}
          style={{
            background: `linear-gradient(135deg, ${category.accentColor}30 0%, ${category.accentColor}10 100%)`,
          }}
        >
          <Icon className={`w-4 h-4 ${category.color}`} />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-medium text-gray-200 truncate">{template.name}</span>
            {template.tags.includes('popular') && (
              <Star className="w-3 h-3 text-yellow-500 fill-yellow-500" />
            )}
          </div>
          <p className="text-[10px] text-gray-500 mt-0.5 line-clamp-1">{template.description}</p>
          <div className="flex items-center gap-2 mt-1.5">
            <span className="text-[10px] text-gray-600">{template.lines} lines</span>
            <span className="text-[10px] text-gray-700">•</span>
            <span className="text-[10px] text-gray-600">{template.coverage}% coverage</span>
            {template.dependencies.length > 0 && (
              <>
                <span className="text-[10px] text-gray-700">•</span>
                <span className="text-[10px] text-orange-400">{template.dependencies.length} deps</span>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default TemplateLibrary

