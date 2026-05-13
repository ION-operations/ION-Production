// Organization Systems Panel - Demo
// Displays master system map, integration map, consolidation documents, and organization systems

import React, { useState, useMemo, useCallback, useEffect } from 'react'
import { BasePanel } from '../components/BasePanel'
import { 
  Search, 
  Network, 
  FileText, 
  Layers, 
  GitBranch, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  BookOpen,
  Map,
  Link2,
  BarChart3,
  FolderTree,
  Target
} from 'lucide-react'
import { consolidationService, ConsolidationDocument, SystemMapEntry, PhaseStatus, ConsolidationStats } from '../services/ConsolidationService'

// Types are imported from ConsolidationService

// ===== MAIN COMPONENT =====

export const OrganizationSystemsPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'system-map' | 'integration-map' | 'consolidation-docs' | 'phases'>('overview')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Data state
  const [documents, setDocuments] = useState<ConsolidationDocument[]>([])
  const [systems, setSystems] = useState<SystemMapEntry[]>([])
  const [phases, setPhases] = useState<PhaseStatus[]>([])
  const [stats, setStats] = useState<ConsolidationStats | null>(null)
  
  // Load data on mount
  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      setError(null)
      
      try {
        const [docsResult, systemsResult, phasesResult, statsResult] = await Promise.all([
          consolidationService.loadConsolidationDocuments(),
          consolidationService.loadSystemMap(),
          consolidationService.loadPhaseStatus(),
          consolidationService.getStats(),
        ])
        
        if (docsResult.success && docsResult.documents) {
          setDocuments(docsResult.documents)
        }
        
        if (systemsResult.success && systemsResult.systems) {
          setSystems(systemsResult.systems)
        }
        
        if (phasesResult.success && phasesResult.phases) {
          setPhases(phasesResult.phases)
        }
        
        if (statsResult.success && statsResult.stats) {
          setStats(statsResult.stats)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
      } finally {
        setLoading(false)
      }
    }
    
    loadData()
  }, [])

  // Filter consolidation docs
  const filteredDocs = useMemo(() => {
    let docs = documents
    
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      docs = docs.filter(doc =>
        doc.title.toLowerCase().includes(query) ||
        doc.path.toLowerCase().includes(query) ||
        doc.description?.toLowerCase().includes(query)
      )
    }
    
    if (selectedCategory) {
      docs = docs.filter(doc => doc.category === selectedCategory)
    }
    
    return docs
  }, [searchQuery, selectedCategory, documents])

  // Filter system map
  const filteredSystems = useMemo(() => {
    if (!searchQuery.trim()) return systems
    
    const query = searchQuery.toLowerCase()
    return systems.filter(system =>
      system.name.toLowerCase().includes(query) ||
      system.type === query ||
      system.description?.toLowerCase().includes(query)
    )
  }, [searchQuery, systems])

  const overallConfidence = 0.90
  const confidenceBand: 'A' | 'B' | 'C' = overallConfidence >= 0.90 ? 'A' : overallConfidence >= 0.70 ? 'B' : 'C'

  return (
    <BasePanel
      id="organization-systems-panel"
      title="Organization Systems"
      icon={Layers}
      description="Master system map, integration map, consolidation documents, and organization systems"
      loading={loading}
      error={error}
      empty={false}
      confidence={overallConfidence}
      confidenceBand={confidenceBand}
      showFooter={true}
      footerContent={
        stats ? (
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>{stats.completePhases}/{stats.totalPhases} phases complete</span>
            <span>{stats.completeSystems}/{stats.totalSystems} systems complete</span>
            <span>{stats.integrationPercentage}% integrations</span>
          </div>
        ) : null
      }
    >
      {/* Tabs */}
      <div className="mb-4 border-b border-gray-700">
        <div className="flex gap-1">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'system-map', label: 'System Map', icon: Network },
            { id: 'integration-map', label: 'Integration Map', icon: Link2 },
            { id: 'consolidation-docs', label: 'Consolidation Docs', icon: FileText },
            { id: 'phases', label: 'Phases', icon: Target },
          ].map(tab => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors flex items-center gap-1 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Search Bar */}
      <div className="mb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search..."
            className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {activeTab === 'overview' && (
          <div className="space-y-4">
            {/* Statistics Cards */}
            {stats && (
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-800 border border-gray-700 rounded p-4">
                  <div className="text-sm text-gray-400 mb-1">Systems</div>
                  <div className="text-2xl font-bold text-gray-200">{stats.completeSystems}/{stats.totalSystems}</div>
                  <div className="text-xs text-gray-500 mt-1">{stats.coreSystems} core systems</div>
                </div>
                <div className="bg-gray-800 border border-gray-700 rounded p-4">
                  <div className="text-sm text-gray-400 mb-1">Integrations</div>
                  <div className="text-2xl font-bold text-gray-200">{stats.integrationPercentage}%</div>
                  <div className="text-xs text-gray-500 mt-1">{stats.totalIntegrations}/{stats.totalPossibleIntegrations} complete</div>
                </div>
                <div className="bg-gray-800 border border-gray-700 rounded p-4">
                  <div className="text-sm text-gray-400 mb-1">Phases</div>
                  <div className="text-2xl font-bold text-gray-200">{stats.completePhases}/{stats.totalPhases}</div>
                  <div className="text-xs text-gray-500 mt-1">All phases complete</div>
                </div>
                <div className="bg-gray-800 border border-gray-700 rounded p-4">
                  <div className="text-sm text-gray-400 mb-1">Documents</div>
                  <div className="text-2xl font-bold text-gray-200">{stats.totalDocuments}</div>
                  <div className="text-xs text-gray-500 mt-1">Consolidation docs</div>
                </div>
              </div>
            )}

            {/* Quick Links */}
            <div>
              <h3 className="text-sm font-semibold text-gray-300 mb-2">Quick Links</h3>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { id: 'system-map', label: 'System Map', icon: Network },
                  { id: 'integration-map', label: 'Integration Map', icon: Link2 },
                  { id: 'consolidation-docs', label: 'Consolidation Docs', icon: FileText },
                  { id: 'phases', label: 'Phases', icon: Target },
                ].map(link => {
                  const Icon = link.icon
                  return (
                    <button
                      key={link.id}
                      onClick={() => setActiveTab(link.id as any)}
                      className="flex items-center gap-2 p-3 bg-gray-800 border border-gray-700 rounded hover:border-gray-600 transition-colors text-left"
                    >
                      <Icon className="w-4 h-4 text-blue-400" />
                      <span className="text-sm text-gray-300">{link.label}</span>
                    </button>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'system-map' && (
          <div className="space-y-2">
            {filteredSystems.map(system => (
              <div
                key={system.id}
                className="p-3 bg-gray-800 border border-gray-700 rounded hover:border-gray-600 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <div className="text-sm font-semibold text-gray-200">{system.name}</div>
                    <div className="text-xs text-gray-400 mt-1">
                      {system.integrations}/{system.totalIntegrations} integrations
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 text-xs rounded ${
                      system.type === 'core' ? 'bg-blue-900/30 text-blue-300' :
                      system.type === 'enhancement' ? 'bg-purple-900/30 text-purple-300' :
                      system.type === 'integration' ? 'bg-green-900/30 text-green-300' :
                      'bg-gray-700 text-gray-300'
                    }`}>
                      {system.type}
                    </span>
                    <span className={`px-2 py-1 text-xs rounded ${
                      system.status === 'complete' ? 'bg-green-900/30 text-green-300' :
                      system.status === 'partial' ? 'bg-yellow-900/30 text-yellow-300' :
                      'bg-red-900/30 text-red-300'
                    }`}>
                      {system.status}
                    </span>
                  </div>
                </div>
                <div className="mt-2">
                  <div className="w-full bg-gray-900 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        system.integrations === system.totalIntegrations ? 'bg-green-500' :
                        system.integrations > 0 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${(system.integrations / system.totalIntegrations) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'integration-map' && (
          <div className="space-y-4">
            <div className="text-sm text-gray-400">
              Integration map visualization would go here. This would show connections between systems.
            </div>
            <div className="grid grid-cols-2 gap-2">
              {mockSystemMap.map(system => (
                <div key={system.id} className="p-3 bg-gray-800 border border-gray-700 rounded">
                  <div className="text-sm font-semibold text-gray-200 mb-1">{system.name}</div>
                  <div className="text-xs text-gray-400">
                    {system.integrations} of {system.totalIntegrations} integrations
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'consolidation-docs' && (
          <div className="space-y-2">
            {/* Category Filter */}
            <div className="flex flex-wrap gap-1 mb-4">
              <button
                onClick={() => setSelectedCategory(null)}
                className={`px-2 py-1 text-xs rounded ${
                  !selectedCategory
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                All
              </button>
              {Array.from(new Set(documents.map(d => d.category))).map(category => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(selectedCategory === category ? null : category)}
                  className={`px-2 py-1 text-xs rounded capitalize ${
                    selectedCategory === category
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>

            {/* Documents */}
            {filteredDocs.map(doc => (
              <div
                key={doc.id}
                className="p-3 bg-gray-800 border border-gray-700 rounded hover:border-gray-600 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="text-sm font-semibold text-gray-200 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-blue-400" />
                      {doc.title}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">{doc.path}</div>
                    {doc.description && (
                      <div className="text-xs text-gray-500 mt-1">{doc.description}</div>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 text-xs rounded capitalize ${
                      doc.category === 'status' ? 'bg-blue-900/30 text-blue-300' :
                      doc.category === 'map' ? 'bg-green-900/30 text-green-300' :
                      doc.category === 'phase' ? 'bg-purple-900/30 text-purple-300' :
                      doc.category === 'index' ? 'bg-yellow-900/30 text-yellow-300' :
                      'bg-gray-700 text-gray-300'
                    }`}>
                      {doc.category}
                    </span>
                    {doc.status && (
                      <span className={`px-2 py-1 text-xs rounded ${
                        doc.status === 'complete' ? 'bg-green-900/30 text-green-300' :
                        doc.status === 'in-progress' ? 'bg-yellow-900/30 text-yellow-300' :
                        'bg-gray-700 text-gray-300'
                      }`}>
                        {doc.status === 'complete' ? <CheckCircle className="w-3 h-3 inline" /> :
                         doc.status === 'in-progress' ? <Clock className="w-3 h-3 inline" /> :
                         <AlertCircle className="w-3 h-3 inline" />}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'phases' && (
          <div className="space-y-3">
            {phases.map(phase => (
              <div
                key={phase.phase}
                className="p-4 bg-gray-800 border border-gray-700 rounded"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <div className="text-sm font-semibold text-gray-200">
                      Phase {phase.phase}: {phase.name}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">{phase.description}</div>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded ${
                    phase.status === 'complete' ? 'bg-green-900/30 text-green-300' :
                    phase.status === 'in-progress' ? 'bg-yellow-900/30 text-yellow-300' :
                    'bg-gray-700 text-gray-300'
                  }`}>
                    {phase.status === 'complete' ? <CheckCircle className="w-3 h-3 inline mr-1" /> :
                     phase.status === 'in-progress' ? <Clock className="w-3 h-3 inline mr-1" /> :
                     <AlertCircle className="w-3 h-3 inline mr-1" />}
                    {phase.status}
                  </span>
                </div>
                <div className="mt-3">
                  <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                    <span>Progress</span>
                    <span>{phase.completion}%</span>
                  </div>
                  <div className="w-full bg-gray-900 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        phase.status === 'complete' ? 'bg-green-500' :
                        phase.status === 'in-progress' ? 'bg-yellow-500' :
                        'bg-gray-600'
                      }`}
                      style={{ width: `${phase.completion}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </BasePanel>
  )
}

