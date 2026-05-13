// Properties Panel - Node configuration with beautiful UI
// Dynamic form generation based on template config schema

import React, { useState, useMemo } from 'react'
import { Node } from 'reactflow'
import { 
  Settings, ChevronDown, ChevronUp, ChevronRight, Save, RotateCcw, 
  Copy, Trash2, Play, Code, ExternalLink, HelpCircle, Check, X,
  Info, AlertTriangle
} from 'lucide-react'
import { TemplateNodeData, ConfigField, Template } from './types'
import { getCategoryConfig, TEMPLATES } from './templates'

interface PropertiesPanelProps {
  selectedNode: Node<TemplateNodeData> | null
  onConfigChange: (nodeId: string, config: Record<string, any>) => void
  onDuplicate?: (nodeId: string) => void
  onDelete?: (nodeId: string) => void
  onTest?: (nodeId: string) => void
  onViewCode?: (nodeId: string) => void
}

export const PropertiesPanel: React.FC<PropertiesPanelProps> = ({
  selectedNode,
  onConfigChange,
  onDuplicate,
  onDelete,
  onTest,
  onViewCode,
}) => {
  const [isExpanded, setIsExpanded] = useState(true)
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set(['all']))
  const [hasChanges, setHasChanges] = useState(false)
  const [localConfig, setLocalConfig] = useState<Record<string, any>>({})

  // Get template definition
  const template = useMemo(() => {
    if (!selectedNode) return null
    return TEMPLATES.find(t => t.id === selectedNode.data.id)
  }, [selectedNode])

  // Sync local config with node config
  React.useEffect(() => {
    if (selectedNode) {
      setLocalConfig(selectedNode.data.config)
      setHasChanges(false)
    }
  }, [selectedNode?.id])

  const handleFieldChange = (key: string, value: any) => {
    setLocalConfig(prev => ({ ...prev, [key]: value }))
    setHasChanges(true)
  }

  const handleApply = () => {
    if (selectedNode) {
      onConfigChange(selectedNode.id, localConfig)
      setHasChanges(false)
    }
  }

  const handleReset = () => {
    if (selectedNode) {
      setLocalConfig(selectedNode.data.config)
      setHasChanges(false)
    }
  }

  const toggleGroup = (groupId: string) => {
    setExpandedGroups(prev => {
      const next = new Set(prev)
      if (next.has(groupId)) {
        next.delete(groupId)
      } else {
        next.add(groupId)
      }
      return next
    })
  }

  if (!selectedNode) {
    return (
      <div className={`bg-gray-900 border-t border-gray-800 transition-all ${isExpanded ? 'h-64' : 'h-12'}`}>
        <div className="h-12 flex items-center justify-between px-4 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <Settings className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-500">No template selected</span>
          </div>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 hover:bg-gray-800 rounded-lg text-gray-400 transition-colors"
          >
            {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
        </div>
        
        {isExpanded && (
          <div className="flex items-center justify-center h-[calc(256px-48px)]">
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl bg-gray-800 flex items-center justify-center mx-auto mb-4">
                <Settings className="w-8 h-8 text-gray-600" />
              </div>
              <p className="text-sm text-gray-400">Select a template</p>
              <p className="text-xs text-gray-600 mt-1">to view and edit its configuration</p>
            </div>
          </div>
        )}
      </div>
    )
  }

  const category = getCategoryConfig(selectedNode.data.type)!
  const Icon = selectedNode.data.icon

  return (
    <div className={`bg-gray-900 border-t border-gray-800 transition-all ${isExpanded ? 'h-64' : 'h-12'}`}>
      {/* Header */}
      <div 
        className="h-12 flex items-center justify-between px-4 border-b border-gray-800"
        style={{
          background: `linear-gradient(90deg, ${category.accentColor}10 0%, transparent 100%)`,
        }}
      >
        <div className="flex items-center gap-3">
          <div 
            className={`w-8 h-8 rounded-lg flex items-center justify-center ${category.bgColor} ${category.borderColor} border`}
            style={{
              background: `linear-gradient(135deg, ${category.accentColor}30 0%, ${category.accentColor}10 100%)`,
            }}
          >
            <Icon className={`w-4 h-4 ${category.color}`} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-gray-100">{selectedNode.data.name}</span>
              <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${
                selectedNode.data.status === 'configured' ? 'bg-green-500/20 text-green-400' :
                selectedNode.data.status === 'incomplete' ? 'bg-yellow-500/20 text-yellow-400' : 
                'bg-red-500/20 text-red-400'
              }`}>
                {selectedNode.data.status}
              </span>
              {hasChanges && (
                <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-blue-500/20 text-blue-400">
                  Modified
                </span>
              )}
            </div>
            <p className="text-[10px] text-gray-500">{selectedNode.data.description}</p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          {/* Quick Actions */}
          {onViewCode && (
            <button
              onClick={() => onViewCode(selectedNode.id)}
              className="p-1.5 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-gray-200 transition-colors"
              title="View Code"
            >
              <Code className="w-4 h-4" />
            </button>
          )}
          {onTest && selectedNode.data.status === 'configured' && (
            <button
              onClick={() => onTest(selectedNode.id)}
              className="p-1.5 hover:bg-green-800/50 rounded-lg text-green-400 hover:text-green-300 transition-colors"
              title="Test"
            >
              <Play className="w-4 h-4" />
            </button>
          )}
          {onDuplicate && (
            <button
              onClick={() => onDuplicate(selectedNode.id)}
              className="p-1.5 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-gray-200 transition-colors"
              title="Duplicate"
            >
              <Copy className="w-4 h-4" />
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(selectedNode.id)}
              className="p-1.5 hover:bg-red-800/50 rounded-lg text-red-400 hover:text-red-300 transition-colors"
              title="Delete"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
          
          <div className="w-px h-4 bg-gray-700 mx-1" />
          
          {/* Apply / Reset */}
          {hasChanges && (
            <>
              <button
                onClick={handleReset}
                className="p-1.5 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-gray-200 transition-colors"
                title="Reset Changes"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
              <button
                onClick={handleApply}
                className="px-2.5 py-1 rounded-lg bg-green-600 hover:bg-green-500 text-white text-xs font-medium flex items-center gap-1.5 transition-colors"
              >
                <Save className="w-3.5 h-3.5" />
                Apply
              </button>
            </>
          )}
          
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 hover:bg-gray-800 rounded-lg text-gray-400 transition-colors ml-2"
          >
            {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Content */}
      {isExpanded && (
        <div className="p-4 overflow-y-auto h-[calc(256px-48px)]">
          {template?.configSchema?.groups ? (
            // Grouped fields
            <div className="space-y-4">
              {template.configSchema.groups.map(group => {
                const isGroupExpanded = expandedGroups.has(group.id) || expandedGroups.has('all')
                return (
                  <div key={group.id} className="space-y-2">
                    <button
                      onClick={() => toggleGroup(group.id)}
                      className="w-full flex items-center gap-2 text-left"
                    >
                      {isGroupExpanded ? (
                        <ChevronDown className="w-4 h-4 text-gray-500" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-gray-500" />
                      )}
                      <span className="text-xs font-semibold text-gray-300 uppercase tracking-wider">
                        {group.name}
                      </span>
                      {group.description && (
                        <span className="text-[10px] text-gray-600 ml-auto">{group.description}</span>
                      )}
                    </button>
                    
                    {isGroupExpanded && (
                      <div className="grid grid-cols-3 gap-3 pl-6">
                        {group.fields.map(fieldKey => {
                          const fieldDef = template.defaultConfig[fieldKey]
                          if (!fieldDef) return null
                          return (
                            <ConfigFieldInput
                              key={fieldKey}
                              fieldKey={fieldKey}
                              field={fieldDef}
                              value={localConfig[fieldKey] ?? fieldDef.value}
                              onChange={(value) => handleFieldChange(fieldKey, value)}
                            />
                          )
                        })}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          ) : (
            // Flat fields
            <div className="grid grid-cols-3 gap-3">
              {Object.entries(localConfig).map(([key, value]) => (
                <ConfigFieldInput
                  key={key}
                  fieldKey={key}
                  field={{ value, type: typeof value === 'boolean' ? 'boolean' : 'string', label: key }}
                  value={value}
                  onChange={(newValue) => handleFieldChange(key, newValue)}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// Config Field Input Component
interface ConfigFieldInputProps {
  fieldKey: string
  field: ConfigField
  value: any
  onChange: (value: any) => void
}

const ConfigFieldInput: React.FC<ConfigFieldInputProps> = ({
  fieldKey,
  field,
  value,
  onChange,
}) => {
  const label = field.label || fieldKey.replace(/([A-Z])/g, ' $1').trim()
  
  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-1">
        <label className="text-[10px] text-gray-500 uppercase tracking-wider font-medium">
          {label}
        </label>
        {field.required && <span className="text-red-400 text-[10px]">*</span>}
        {field.description && (
          <div className="group relative">
            <HelpCircle className="w-3 h-3 text-gray-600 cursor-help" />
            <div className="absolute bottom-full left-0 mb-1 px-2 py-1 bg-gray-800 rounded text-[10px] text-gray-300 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
              {field.description}
            </div>
          </div>
        )}
      </div>
      
      {field.type === 'boolean' ? (
        <button
          onClick={() => onChange(!value)}
          className={`w-10 h-5 rounded-full transition-colors relative ${
            value ? 'bg-blue-600' : 'bg-gray-700'
          }`}
        >
          <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow-sm transition-transform ${
            value ? 'left-5' : 'left-0.5'
          }`} />
        </button>
      ) : field.type === 'select' ? (
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full h-8 px-2 rounded-lg bg-gray-800 border border-gray-700 text-xs text-gray-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/50"
        >
          {field.options?.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      ) : field.type === 'multiselect' ? (
        <div className="flex flex-wrap gap-1">
          {field.options?.map(opt => {
            const isSelected = Array.isArray(value) && value.includes(opt.value)
            return (
              <button
                key={opt.value}
                onClick={() => {
                  const current = Array.isArray(value) ? value : []
                  onChange(
                    isSelected 
                      ? current.filter(v => v !== opt.value)
                      : [...current, opt.value]
                  )
                }}
                className={`px-2 py-1 rounded text-[10px] transition-colors ${
                  isSelected
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {opt.label}
              </button>
            )
          })}
        </div>
      ) : field.type === 'number' ? (
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          min={field.min}
          max={field.max}
          className="w-full h-8 px-2 rounded-lg bg-gray-800 border border-gray-700 text-xs text-gray-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/50"
        />
      ) : (
        <input
          type={field.type === 'password' ? 'password' : 'text'}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={field.placeholder}
          className="w-full h-8 px-2 rounded-lg bg-gray-800 border border-gray-700 text-xs text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/50"
        />
      )}
    </div>
  )
}

export default PropertiesPanel

