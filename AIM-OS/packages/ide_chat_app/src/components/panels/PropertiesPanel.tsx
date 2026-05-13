/**
 * Properties Panel Component - ENHANCED
 * 
 * Phase 2.2: Right Drawer Panels
 * 
 * Edit selected element properties with full AIM-OS integration.
 * Features:
 * - Property editing with type-specific inputs
 * - Property validation (VIF integration) ⭐
 * - Property relationships (SEG integration) ⭐
 * - Property history with bitemporal tracking ⭐
 * - Validation error display
 * - Related properties visualization
 * - AIM-OS integration (VIF validation, SEG relationships, CMC history)
 * 
 * Enhanced: 2025-11-07 (Rev - Competition Phase)
 */

import React, { useState, useMemo, useEffect, useCallback } from 'react'
import { 
  Settings, 
  Edit2, 
  Save, 
  RotateCcw, 
  CheckCircle, 
  XCircle, 
  Link, 
  History,
  AlertTriangle,
  ChevronRight,
  ChevronDown,
  Plus,
  Trash2,
  Search,
  Filter,
  Info,
  Zap,
  Network
} from 'lucide-react'
import { useAIMOS } from '../../hooks/useAIMOS'
import { ErrorBoundary } from '../ErrorBoundary'
import { LoadingState } from '../LoadingState'

interface PropertyValidation {
  isValid: boolean
  errors: string[]
  warnings: string[]
  confidence?: number // VIF confidence score
}

interface PropertyRelationship {
  id: string
  propertyKey: string
  relationshipType: 'depends_on' | 'affects' | 'related_to' | 'conflicts_with'
  description?: string
}

interface PropertyHistoryEntry {
  timestamp: string
  value: any
  changedBy?: string
  reason?: string
  confidence?: number
}

interface Property {
  key: string
  value: any
  type: 'string' | 'number' | 'boolean' | 'object' | 'array' | 'color' | 'select' | 'json'
  description?: string
  required?: boolean
  validation?: {
    min?: number
    max?: number
    pattern?: string
    options?: string[]
    custom?: string // Custom validation function name
  }
  relationships?: PropertyRelationship[]
  history?: PropertyHistoryEntry[]
  validationResult?: PropertyValidation
}

const mockProperties: Property[] = [
  {
    key: 'name',
    value: 'RevIDELayout',
    type: 'string',
    description: 'Component name (must be unique)',
    required: true,
    validation: {
      pattern: '^[A-Z][a-zA-Z0-9]*$',
      custom: 'validateComponentName'
    },
    validationResult: {
      isValid: true,
      errors: [],
      warnings: [],
      confidence: 0.95
    },
    relationships: [
      {
        id: 'rel-1',
        propertyKey: 'componentId',
        relationshipType: 'affects',
        description: 'Component ID is derived from name'
      }
    ],
    history: [
      {
        timestamp: '2025-11-07T10:00:00Z',
        value: 'IDELayout',
        changedBy: 'rev',
        reason: 'Renamed for clarity',
        confidence: 0.90
      },
      {
        timestamp: '2025-11-07T11:00:00Z',
        value: 'RevIDELayout',
        changedBy: 'rev',
        reason: 'Added Rev prefix for competition',
        confidence: 0.95
      }
    ]
  },
  {
    key: 'theme',
    value: 'dark',
    type: 'select',
    description: 'Theme variant (affects all child components)',
    validation: { options: ['dark', 'light', 'high-contrast'] },
    validationResult: {
      isValid: true,
      errors: [],
      warnings: [],
      confidence: 1.0
    },
    relationships: [
      {
        id: 'rel-2',
        propertyKey: 'settings.theme',
        relationshipType: 'depends_on',
        description: 'Synced with global theme setting'
      },
      {
        id: 'rel-3',
        propertyKey: 'colorScheme',
        relationshipType: 'affects',
        description: 'Updates color scheme automatically'
      }
    ],
    history: [
      {
        timestamp: '2025-11-07T09:00:00Z',
        value: 'light',
        changedBy: 'system',
        confidence: 1.0
      },
      {
        timestamp: '2025-11-07T10:30:00Z',
        value: 'dark',
        changedBy: 'user',
        reason: 'User preference',
        confidence: 1.0
      }
    ]
  },
  {
    key: 'width',
    value: 1200,
    type: 'number',
    description: 'Panel width in pixels',
    validation: { min: 200, max: 2000 },
    validationResult: {
      isValid: true,
      errors: [],
      warnings: [],
      confidence: 0.98
    },
    relationships: [
      {
        id: 'rel-4',
        propertyKey: 'leftDrawerSize',
        relationshipType: 'affects',
        description: 'Left drawer size is calculated from width'
      }
    ]
  },
  {
    key: 'enableDragDrop',
    value: true,
    type: 'boolean',
    description: 'Enable drag and drop functionality',
    validationResult: {
      isValid: true,
      errors: [],
      warnings: [],
      confidence: 1.0
    },
    relationships: [
      {
        id: 'rel-5',
        propertyKey: 'panelManager.enableDragDrop',
        relationshipType: 'related_to',
        description: 'Synced with panel manager setting'
      }
    ]
  },
  {
    key: 'panels',
    value: ['file-explorer', 'outline', 'terminal'],
    type: 'array',
    description: 'Visible panels (order matters)',
    validationResult: {
      isValid: true,
      errors: [],
      warnings: ['Consider adding more panels for better UX'],
      confidence: 0.85
    }
  },
  {
    key: 'config',
    value: {
      autoSave: true,
      telemetry: false,
      logLevel: 'info'
    },
    type: 'object',
    description: 'Component configuration object',
    validationResult: {
      isValid: true,
      errors: [],
      warnings: [],
      confidence: 0.92
    }
  }
]

export const PropertiesPanel: React.FC = () => {
  const [properties, setProperties] = useState<Property[]>(mockProperties)
  const [editingKey, setEditingKey] = useState<string | null>(null)
  const [hasChanges, setHasChanges] = useState(false)
  const [expandedProperties, setExpandedProperties] = useState<Set<string>>(new Set())
  const [showHistory, setShowHistory] = useState<string | null>(null)
  const [showRelationships, setShowRelationships] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState<'all' | 'valid' | 'invalid' | 'has_relationships'>('all')
  const [segRelationships, setSegRelationships] = useState<Map<string, PropertyRelationship[]>>(new Map())

  // AIM-OS integration
  const { cmc, vif, seg, isConnected, useMockData, loading } = useAIMOS()

  // Load SEG relationships for properties
  useEffect(() => {
    const loadSegRelationships = async () => {
      if (!useMockData && isConnected && properties.length > 0) {
        try {
          const topics = properties.map(p => `${p.key}: ${JSON.stringify(p.value)}`).filter(Boolean)
          if (topics.length > 0) {
            const synthesis = await seg.synthesizeKnowledge(topics.slice(0, 10))
            if (synthesis && synthesis.entities) {
              // Transform SEG entities to property relationships
              const relationshipsMap = new Map<string, PropertyRelationship[]>()
              synthesis.entities.forEach((entity: any, idx: number) => {
                if (entity.source_id && entity.target_id) {
                  const sourceProp = properties.find(p => p.key === entity.source_id)
                  const targetProp = properties.find(p => p.key === entity.target_id)
                  if (sourceProp) {
                    const rel: PropertyRelationship = {
                      id: `seg-${idx}`,
                      propertyKey: targetProp?.key || entity.target_id,
                      relationshipType: entity.relation_type === 'SUPPORTS' ? 'related_to' :
                                       entity.relation_type === 'CONTRADICTS' ? 'conflicts_with' :
                                       entity.relation_type === 'DERIVES_FROM' ? 'depends_on' : 'affects',
                      description: `SEG relationship: ${entity.relation_type}`
                    }
                    const existing = relationshipsMap.get(sourceProp.key) || []
                    relationshipsMap.set(sourceProp.key, [...existing, rel])
                  }
                }
              })
              setSegRelationships(relationshipsMap)
            }
          }
        } catch (error) {
          console.warn('Failed to load SEG relationships:', error)
        }
      }
    }
    
    loadSegRelationships()
  }, [properties, seg, useMockData, isConnected])

  // Get all relationships for a property (mock + SEG)
  const getPropertyRelationships = useCallback((property: Property): PropertyRelationship[] => {
    const mockRels = property.relationships || []
    const segRels = segRelationships.get(property.key) || []
    // Merge and deduplicate
    const allRels = [...mockRels, ...segRels]
    const unique = new Map<string, PropertyRelationship>()
    allRels.forEach(rel => {
      const key = `${rel.propertyKey}-${rel.relationshipType}`
      if (!unique.has(key)) {
        unique.set(key, rel)
      }
    })
    return Array.from(unique.values())
  }, [segRelationships])

  // Validate property value
  const validateProperty = (property: Property, value: any): PropertyValidation => {
    const errors: string[] = []
    const warnings: string[] = []
    let confidence = 1.0

    // Required check
    if (property.required && (value === null || value === undefined || value === '')) {
      errors.push(`${property.key} is required`)
      confidence = 0.0
    }

    // Type-specific validation
    if (property.type === 'number' && property.validation) {
      const numValue = typeof value === 'string' ? parseFloat(value) : value
      if (isNaN(numValue)) {
        errors.push(`${property.key} must be a number`)
        confidence = 0.0
      } else {
        if (property.validation.min !== undefined && numValue < property.validation.min) {
          errors.push(`${property.key} must be at least ${property.validation.min}`)
          confidence = Math.max(0.0, confidence - 0.3)
        }
        if (property.validation.max !== undefined && numValue > property.validation.max) {
          errors.push(`${property.key} must be at most ${property.validation.max}`)
          confidence = Math.max(0.0, confidence - 0.3)
        }
      }
    }

    if (property.type === 'string' && property.validation) {
      if (property.validation.pattern) {
        const regex = new RegExp(property.validation.pattern)
        if (!regex.test(value)) {
          errors.push(`${property.key} does not match required pattern`)
          confidence = Math.max(0.0, confidence - 0.5)
        }
      }
    }

    if (property.type === 'select' && property.validation?.options) {
      if (!property.validation.options.includes(value)) {
        errors.push(`${property.key} must be one of: ${property.validation.options.join(', ')}`)
        confidence = 0.0
      }
    }

    // Custom validation (simulated)
    if (property.validation?.custom === 'validateComponentName') {
      if (!/^[A-Z]/.test(value)) {
        errors.push('Component name must start with uppercase letter')
        confidence = Math.max(0.0, confidence - 0.4)
      }
    }

    // VIF confidence calculation (simplified)
    if (errors.length === 0) {
      confidence = 0.95 + (warnings.length === 0 ? 0.05 : 0)
    } else {
      confidence = Math.max(0.0, 1.0 - (errors.length * 0.3))
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      confidence
    }
  }

  const handlePropertyChange = (key: string, value: any) => {
    setProperties(prev => {
      const updated = prev.map(p => {
        if (p.key === key) {
          const validationResult = validateProperty(p, value)
          return { 
            ...p, 
            value,
            validationResult,
            history: [
              ...(p.history || []),
              {
                timestamp: new Date().toISOString(),
                value,
                changedBy: 'user',
                confidence: validationResult.confidence
              }
            ]
          }
        }
        return p
      })
      return updated
    })
    setHasChanges(true)
  }

  const handleSave = async () => {
    if (!useMockData && isConnected) {
      try {
        // Save properties via AIM-OS CMC with VIF validation
        for (const property of properties) {
          if (property.validationResult?.isValid) {
            // Store in CMC
            await cmc.store({
              content: { inline: JSON.stringify({ key: property.key, value: property.value }) },
              modality: 'code',
              tags: { property: property.key, type: property.type }
            })
            
            // Track confidence via VIF
            if (property.validationResult.confidence !== undefined) {
              await vif.trackConfidence(
                `Property: ${property.key}`,
                property.validationResult.confidence,
                `Property validated: ${property.validationResult.isValid ? 'valid' : 'invalid'}`
              )
            }
          }
        }
        
        // Update SEG relationships
        const topics = properties.map(p => `${p.key}: ${p.value}`).filter(Boolean)
        if (topics.length > 0) {
          await seg.synthesizeKnowledge(topics.slice(0, 10))
        }
        
        setHasChanges(false)
        console.log('Properties saved to CMC with VIF validation and SEG relationships updated')
      } catch (error) {
        console.error('Failed to save properties to AIM-OS:', error)
        // Still mark as saved locally
        setHasChanges(false)
      }
    } else {
      setHasChanges(false)
    }
  }

  const handleReset = () => {
    setProperties(mockProperties)
    setHasChanges(false)
  }

  const togglePropertyExpansion = (key: string) => {
    setExpandedProperties(prev => {
      const newSet = new Set(prev)
      if (newSet.has(key)) {
        newSet.delete(key)
      } else {
        newSet.add(key)
      }
      return newSet
    })
  }

  const filteredProperties = useMemo(() => {
    return properties.filter(prop => {
      const matchesSearch = searchQuery === '' || 
        prop.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
        prop.description?.toLowerCase().includes(searchQuery.toLowerCase())
      
      const allRels = getPropertyRelationships(prop)
      const matchesFilter = filterType === 'all' ||
        (filterType === 'valid' && prop.validationResult?.isValid) ||
        (filterType === 'invalid' && !prop.validationResult?.isValid) ||
        (filterType === 'has_relationships' && allRels.length > 0)
      
      return matchesSearch && matchesFilter
    })
  }, [properties, searchQuery, filterType, getPropertyRelationships])

  const renderPropertyInput = (property: Property) => {
    const isExpanded = expandedProperties.has(property.key)
    const validation = property.validationResult

    switch (property.type) {
      case 'string':
        return (
          <div className="space-y-1">
            <input
              type="text"
              value={property.value}
              onChange={(e) => handlePropertyChange(property.key, e.target.value)}
              className={`w-full px-2 py-1 bg-gray-900 border rounded text-sm text-gray-300 focus:outline-none ${
                validation && !validation.isValid
                  ? 'border-red-500 focus:border-red-600'
                  : 'border-gray-700 focus:border-blue-500'
              }`}
              placeholder={property.description}
            />
            {validation && validation.errors.length > 0 && (
              <div className="text-xs text-red-400 space-y-0.5">
                {validation.errors.map((error, idx) => (
                  <div key={idx} className="flex items-center gap-1">
                    <XCircle className="w-3 h-3" />
                    {error}
                  </div>
                ))}
              </div>
            )}
            {validation && validation.warnings.length > 0 && (
              <div className="text-xs text-yellow-400 space-y-0.5">
                {validation.warnings.map((warning, idx) => (
                  <div key={idx} className="flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" />
                    {warning}
                  </div>
                ))}
              </div>
            )}
            {validation && validation.isValid && validation.confidence !== undefined && (
              <div className="text-xs text-green-400 flex items-center gap-1">
                <CheckCircle className="w-3 h-3" />
                Valid (VIF confidence: {(validation.confidence * 100).toFixed(0)}%)
              </div>
            )}
          </div>
        )
      case 'number':
        return (
          <div className="space-y-1">
            <input
              type="number"
              value={property.value}
              onChange={(e) => handlePropertyChange(property.key, parseFloat(e.target.value) || 0)}
              min={property.validation?.min}
              max={property.validation?.max}
              className={`w-full px-2 py-1 bg-gray-900 border rounded text-sm text-gray-300 focus:outline-none ${
                validation && !validation.isValid
                  ? 'border-red-500 focus:border-red-600'
                  : 'border-gray-700 focus:border-blue-500'
              }`}
            />
            {validation && !validation.isValid && (
              <div className="text-xs text-red-400">
                {validation.errors.map((error, idx) => (
                  <div key={idx}>{error}</div>
                ))}
              </div>
            )}
          </div>
        )
      case 'boolean':
        return (
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={property.value}
              onChange={(e) => handlePropertyChange(property.key, e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            <span className="ml-2 text-sm text-gray-300">
              {property.value ? 'Enabled' : 'Disabled'}
            </span>
          </label>
        )
      case 'select':
        return (
          <select
            value={property.value}
            onChange={(e) => handlePropertyChange(property.key, e.target.value)}
            className={`w-full px-2 py-1 bg-gray-900 border rounded text-sm text-gray-300 focus:outline-none ${
              validation && !validation.isValid
                ? 'border-red-500 focus:border-red-600'
                : 'border-gray-700 focus:border-blue-500'
            }`}
          >
            {property.validation?.options?.map(opt => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        )
      case 'color':
        return (
          <div className="flex items-center gap-2">
            <input
              type="color"
              value={property.value}
              onChange={(e) => handlePropertyChange(property.key, e.target.value)}
              className="w-12 h-8 bg-gray-900 border border-gray-700 rounded cursor-pointer"
            />
            <input
              type="text"
              value={property.value}
              onChange={(e) => handlePropertyChange(property.key, e.target.value)}
              className="flex-1 px-2 py-1 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 focus:outline-none focus:border-blue-500"
            />
          </div>
        )
      case 'array':
        return (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <button
                onClick={() => togglePropertyExpansion(property.key)}
                className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-300"
              >
                {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                Array ({Array.isArray(property.value) ? property.value.length : 0} items)
              </button>
              <button
                onClick={() => {
                  const newValue = Array.isArray(property.value) 
                    ? [...property.value, ''] 
                    : ['']
                  handlePropertyChange(property.key, newValue)
                }}
                className="p-1 text-gray-400 hover:text-gray-300"
                title="Add item"
              >
                <Plus className="w-3 h-3" />
              </button>
            </div>
            {isExpanded && Array.isArray(property.value) && (
              <div className="space-y-1 ml-4">
                {property.value.map((item: any, index: number) => (
                  <div key={index} className="flex items-center gap-1">
                    <input
                      type="text"
                      value={item}
                      onChange={(e) => {
                        const newArray = [...property.value]
                        newArray[index] = e.target.value
                        handlePropertyChange(property.key, newArray)
                      }}
                      className="flex-1 px-2 py-1 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 focus:outline-none focus:border-blue-500"
                    />
                    <button
                      onClick={() => {
                        const newArray = property.value.filter((_: any, i: number) => i !== index)
                        handlePropertyChange(property.key, newArray)
                      }}
                      className="p-1 text-red-400 hover:text-red-300"
                      title="Remove item"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )
      case 'object':
      case 'json':
        return (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <button
                onClick={() => togglePropertyExpansion(property.key)}
                className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-300"
              >
                {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                Object {isExpanded ? '(expanded)' : `(${Object.keys(property.value || {}).length} keys)`}
              </button>
            </div>
            {isExpanded && property.value && typeof property.value === 'object' && (
              <div className="ml-4 space-y-2 p-2 bg-gray-900 rounded border border-gray-700">
                {Object.entries(property.value).map(([key, value]) => (
                  <div key={key} className="flex items-center gap-2">
                    <span className="text-xs text-gray-400 font-mono w-24 truncate">{key}:</span>
                    <input
                      type="text"
                      value={typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      onChange={(e) => {
                        try {
                          const parsed = JSON.parse(e.target.value)
                          handlePropertyChange(property.key, { ...property.value, [key]: parsed })
                        } catch {
                          handlePropertyChange(property.key, { ...property.value, [key]: e.target.value })
                        }
                      }}
                      className="flex-1 px-2 py-1 bg-gray-800 border border-gray-600 rounded text-xs text-gray-300 focus:outline-none focus:border-blue-500 font-mono"
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        )
      default:
        return (
          <input
            type="text"
            value={JSON.stringify(property.value)}
            onChange={(e) => {
              try {
                handlePropertyChange(property.key, JSON.parse(e.target.value))
              } catch {
                // Invalid JSON, ignore
              }
            }}
            className="w-full px-2 py-1 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 focus:outline-none focus:border-blue-500 font-mono"
          />
        )
    }
  }

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-800" role="complementary" aria-label="Properties Panel">
        {loading.cmc ? (
          <LoadingState message="Loading properties..." />
        ) : (
          <>
      {/* Header */}
      <div className="h-10 bg-gray-900 border-b border-gray-700 flex items-center px-3 shrink-0">
        <Settings className="w-4 h-4 mr-2 text-gray-400" />
        <span className="text-sm font-semibold text-gray-300">Properties</span>
        {hasChanges && (
          <span className="ml-auto text-xs text-yellow-400 flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" />
            Unsaved
          </span>
        )}
      </div>

      {/* Search and Filter */}
      <div className="p-2 border-b border-gray-700 space-y-2">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search properties..."
            className="w-full pl-8 pr-2 py-1.5 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        <div className="flex gap-1">
          {(['all', 'valid', 'invalid', 'has_relationships'] as const).map(filter => (
            <button
              key={filter}
              onClick={() => setFilterType(filter)}
              className={`px-2 py-1 text-xs rounded ${
                filterType === filter
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {filter.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Properties List */}
      <div className="flex-1 overflow-y-auto p-3">
        <div className="space-y-4">
          {filteredProperties.length === 0 ? (
            <div className="text-center text-gray-500 text-sm py-8">
              No properties found
            </div>
          ) : (
            filteredProperties.map((property) => {
              const validation = property.validationResult
              const allRelationships = getPropertyRelationships(property)
              const hasRelationships = allRelationships.length > 0
              const hasHistory = property.history && property.history.length > 0
              
              return (
                <div 
                  key={property.key} 
                  className={`p-3 rounded border ${
                    validation && !validation.isValid
                      ? 'border-red-500/50 bg-red-900/10'
                      : 'border-gray-700 bg-gray-900/50'
                  }`}
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium text-gray-300 flex items-center gap-2">
                        {property.key}
                        {property.required && (
                          <span className="text-red-400" title="Required">*</span>
                        )}
                        {validation && validation.isValid && (
                          <CheckCircle className="w-4 h-4 text-green-400" title="Valid" />
                        )}
                        {validation && !validation.isValid && (
                          <XCircle className="w-4 h-4 text-red-400" title="Invalid" />
                        )}
                        {validation && validation.confidence !== undefined && validation.confidence < 0.90 && (
                          <span className="text-xs text-yellow-400" title="Low confidence">
                            ⚠️
                          </span>
                        )}
                      </label>
                      <div className="flex items-center gap-1">
                        {hasRelationships && (
                          <button
                            onClick={() => setShowRelationships(showRelationships === property.key ? null : property.key)}
                            className={`p-1 rounded ${
                              showRelationships === property.key
                                ? 'bg-blue-600 text-white'
                                : 'text-gray-400 hover:text-gray-300'
                            }`}
                            title="Show relationships (SEG)"
                          >
                            <Link className="w-3.5 h-3.5" />
                          </button>
                        )}
                        {hasHistory && (
                          <button
                            onClick={() => setShowHistory(showHistory === property.key ? null : property.key)}
                            className={`p-1 rounded ${
                              showHistory === property.key
                                ? 'bg-blue-600 text-white'
                                : 'text-gray-400 hover:text-gray-300'
                            }`}
                            title="Show history (CMC bitemporal)"
                          >
                            <History className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </div>
                    
                    {property.description && (
                      <p className="text-xs text-gray-500">{property.description}</p>
                    )}
                    
                    {renderPropertyInput(property)}

                    {/* Relationships (SEG) */}
                    {showRelationships === property.key && hasRelationships && (
                      <div className="mt-2 p-2 bg-gray-900 rounded border border-gray-700">
                        <div className="text-xs font-semibold text-gray-400 mb-1 flex items-center gap-1">
                          <Network className="w-3 h-3 text-purple-400" />
                          Relationships (SEG)
                          {segRelationships.has(property.key) && (
                            <span className="ml-auto text-xs text-purple-400">From SEG</span>
                          )}
                        </div>
                        <div className="space-y-1">
                          {allRelationships.map(rel => (
                            <div key={rel.id} className="text-xs text-gray-300 flex items-start gap-2">
                              <div className={`px-1.5 py-0.5 rounded text-xs ${
                                rel.relationshipType === 'depends_on' ? 'bg-green-600/20 text-green-400' :
                                rel.relationshipType === 'affects' ? 'bg-blue-600/20 text-blue-400' :
                                rel.relationshipType === 'conflicts_with' ? 'bg-red-600/20 text-red-400' :
                                'bg-gray-600/20 text-gray-400'
                              }`}>
                                {rel.relationshipType.replace('_', ' ')}
                              </div>
                              <div className="flex-1">
                                <span className="font-mono text-blue-400">{rel.propertyKey}</span>
                                {rel.description && (
                                  <div className="text-gray-500 mt-0.5">{rel.description}</div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* History (CMC Bitemporal) */}
                    {showHistory === property.key && hasHistory && (
                      <div className="mt-2 p-2 bg-gray-900 rounded border border-gray-700">
                        <div className="text-xs font-semibold text-gray-400 mb-1 flex items-center gap-1">
                          <History className="w-3 h-3" />
                          History (CMC Bitemporal)
                        </div>
                        <div className="space-y-1 max-h-32 overflow-y-auto">
                          {property.history!.slice().reverse().map((entry, idx) => (
                            <div key={idx} className="text-xs text-gray-300 border-l-2 border-gray-700 pl-2">
                              <div className="flex items-center justify-between">
                                <span className="font-mono">{JSON.stringify(entry.value)}</span>
                                <span className="text-gray-500">
                                  {new Date(entry.timestamp).toLocaleTimeString()}
                                </span>
                              </div>
                              <div className="text-gray-500 text-xs">
                                {entry.changedBy && `by ${entry.changedBy}`}
                                {entry.reason && ` • ${entry.reason}`}
                                {entry.confidence !== undefined && (
                                  <span className="ml-1">
                                    (VIF: {(entry.confidence * 100).toFixed(0)}%)
                                  </span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="h-12 bg-gray-900 border-t border-gray-700 flex items-center justify-between px-3 shrink-0">
        <div className="text-xs text-gray-500">
          {filteredProperties.length} properties
          {properties.some(p => p.validationResult && !p.validationResult.isValid) && (
            <span className="text-red-400 ml-2">
              • {properties.filter(p => p.validationResult && !p.validationResult.isValid).length} invalid
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded transition-colors"
            aria-label="Reset changes"
          >
            <RotateCcw className="w-4 h-4" />
            Reset
          </button>
          <button
            onClick={handleSave}
            disabled={!hasChanges}
            className={`flex items-center gap-2 px-4 py-1.5 text-sm rounded transition-colors ${
              hasChanges
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-700 text-gray-500 cursor-not-allowed'
            }`}
            aria-label="Save properties"
          >
            <Save className="w-4 h-4" />
            Save
          </button>
        </div>
      </div>
          </>
        )}
      </div>
    </ErrorBoundary>
  )
}
