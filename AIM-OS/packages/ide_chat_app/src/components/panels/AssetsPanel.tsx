/**
 * Assets Panel Component
 * 
 * Phase 2.2: Right Drawer Panels
 * 
 * Asset management (images, fonts, icons, media).
 * Features:
 * - Asset library browser
 * - Asset preview
 * - Asset upload
 * - Asset search/filter
 * - Asset metadata
 * - AIM-OS integration (CMC storage, HHNI indexing)
 */

import React, { useState, useCallback, useMemo } from 'react'
import { BookOpen, Image, FileText, Music, Video, Search, Upload, Grid, List, Download, Trash2, Info, Eye, X, ExternalLink, Brain, Shield, Copy, Maximize2, Minimize2 } from 'lucide-react'
import { useAIMOS } from '../../hooks/useAIMOS'
import { useDebounce } from '../../hooks/useDebounce'
import { ErrorBoundary } from '../ErrorBoundary'
import { LoadingState } from '../LoadingState'

interface Asset {
  id: string
  name: string
  type: 'image' | 'font' | 'icon' | 'video' | 'audio' | 'document'
  url: string
  size: number
  createdAt: string
  tags: string[]
  metadata?: Record<string, any>
  usageCount?: number
  lastUsed?: string
  cmcAtomId?: string // CMC integration
  hhniTags?: string[] // HHNI semantic tags
  vifConfidence?: number // VIF confidence
  optimized?: boolean
  optimizationSize?: number // Size after optimization
}

const mockAssets: Asset[] = [
  {
    id: 'asset-1',
    name: 'logo.png',
    type: 'image',
    url: '/assets/logo.png',
    size: 24580,
    createdAt: '2025-11-07T10:00:00Z',
    tags: ['logo', 'branding'],
    metadata: { width: 512, height: 512, format: 'PNG' },
    usageCount: 45,
    lastUsed: '2025-11-07T10:30:00Z',
    hhniTags: ['logo', 'branding', 'ui'],
    vifConfidence: 0.98,
    optimized: true,
    optimizationSize: 18240,
    cmcAtomId: 'cmc-asset-001',
  },
  {
    id: 'asset-2',
    name: 'Inter-Regular.woff2',
    type: 'font',
    url: '/assets/fonts/Inter-Regular.woff2',
    size: 45620,
    createdAt: '2025-11-07T09:30:00Z',
    tags: ['font', 'typography'],
    metadata: { family: 'Inter', weight: 400, style: 'normal' },
    usageCount: 123,
    lastUsed: '2025-11-07T10:25:00Z',
    hhniTags: ['font', 'typography', 'text'],
    vifConfidence: 0.99,
    cmcAtomId: 'cmc-asset-002',
  },
  {
    id: 'asset-3',
    name: 'icon-check.svg',
    type: 'icon',
    url: '/assets/icons/icon-check.svg',
    size: 234,
    createdAt: '2025-11-07T09:00:00Z',
    tags: ['icon', 'ui'],
    metadata: { viewBox: '0 0 24 24' },
    usageCount: 89,
    lastUsed: '2025-11-07T10:20:00Z',
    hhniTags: ['icon', 'ui', 'check'],
    vifConfidence: 0.97,
    optimized: true,
    optimizationSize: 189,
  },
  {
    id: 'asset-4',
    name: 'background-video.mp4',
    type: 'video',
    url: '/assets/videos/background-video.mp4',
    size: 2456780,
    createdAt: '2025-11-07T08:00:00Z',
    tags: ['video', 'background'],
    metadata: { duration: 30, resolution: '1920x1080' },
    usageCount: 12,
    lastUsed: '2025-11-07T09:15:00Z',
    hhniTags: ['video', 'background', 'media'],
    vifConfidence: 0.95,
    optimized: false,
  },
  {
    id: 'asset-5',
    name: 'notification-sound.mp3',
    type: 'audio',
    url: '/assets/audio/notification-sound.mp3',
    size: 45678,
    createdAt: '2025-11-07T07:30:00Z',
    tags: ['audio', 'notification'],
    metadata: { duration: 2, format: 'MP3' },
    usageCount: 34,
    lastUsed: '2025-11-07T10:10:00Z',
    hhniTags: ['audio', 'notification', 'sound'],
    vifConfidence: 0.96,
    optimized: true,
    optimizationSize: 32100,
  },
]

export const AssetsPanel: React.FC = () => {
  const [assets, setAssets] = useState<Asset[]>(mockAssets)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState<'all' | Asset['type']>('all')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null)
  const [showPreview, setShowPreview] = useState(false)
  const [showOptimizedOnly, setShowOptimizedOnly] = useState(false)

  // Debounce search query for performance
  const debouncedSearchQuery = useDebounce(searchQuery, 300)

  // AIM-OS integration
  const { hhni, cmc, vif, isConnected, useMockData, loading } = useAIMOS()

  const filteredAssets = useMemo(() => {
    return assets.filter((asset) => {
      const matchesSearch =
        asset.name.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        asset.tags.some((tag) => tag.toLowerCase().includes(debouncedSearchQuery.toLowerCase())) ||
        asset.hhniTags?.some(tag => tag.toLowerCase().includes(debouncedSearchQuery.toLowerCase()))
      const matchesType = selectedType === 'all' || asset.type === selectedType
      const matchesOptimized = !showOptimizedOnly || asset.optimized
      return matchesSearch && matchesType && matchesOptimized
    })
  }, [assets, debouncedSearchQuery, selectedType, showOptimizedOnly])

  const totalSize = useMemo(() => assets.reduce((sum, a) => sum + a.size, 0), [assets])
  const optimizedSize = useMemo(() => assets.filter(a => a.optimized).reduce((sum, a) => sum + (a.optimizationSize || a.size), 0), [assets])
  const savings = totalSize - optimizedSize
  const savingsPercent = totalSize > 0 ? (savings / totalSize) * 100 : 0

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const getAssetIcon = (type: Asset['type']) => {
    switch (type) {
      case 'image':
        return <Image className="w-5 h-5 text-blue-400" />
      case 'font':
        return <FileText className="w-5 h-5 text-purple-400" />
      case 'icon':
        return <FileText className="w-5 h-5 text-green-400" />
      case 'video':
        return <Video className="w-5 h-5 text-red-400" />
      case 'audio':
        return <Music className="w-5 h-5 text-yellow-400" />
      case 'document':
        return <FileText className="w-5 h-5 text-gray-400" />
      default:
        return <FileText className="w-5 h-5 text-gray-400" />
    }
  }

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-800" role="complementary" aria-label="Assets Panel">
        {loading.hhni ? (
          <LoadingState message="Loading assets..." />
        ) : (
          <>
      {/* Header */}
      <div className="h-10 bg-gray-900 border-b border-gray-700 flex items-center justify-between px-3 shrink-0">
        <div className="flex items-center">
          <BookOpen className="w-4 h-4 mr-2 text-gray-400" />
          <span className="text-sm font-semibold text-gray-300">Assets</span>
          <span className="ml-2 px-2 py-0.5 bg-gray-700 text-gray-400 text-xs rounded">
            {filteredAssets.length} {filteredAssets.length === 1 ? 'asset' : 'assets'}
          </span>
        </div>
        <div className="flex gap-1">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-1 rounded ${viewMode === 'grid' ? 'bg-gray-700' : 'hover:bg-gray-700'}`}
            aria-label="Grid view"
            title="Grid view"
          >
            <Grid className="w-4 h-4 text-gray-400" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-1 rounded ${viewMode === 'list' ? 'bg-gray-700' : 'hover:bg-gray-700'}`}
            aria-label="List view"
            title="List view"
          >
            <List className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="p-2 border-b border-gray-700 space-y-2 shrink-0">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search assets..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-2 py-1.5 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500"
            aria-label="Search assets"
          />
        </div>
        <div className="flex gap-1 overflow-x-auto">
          {['all', 'image', 'font', 'icon', 'video', 'audio', 'document'].map((type) => (
            <button
              key={type}
              onClick={() => setSelectedType(type as any)}
              className={`px-2 py-1 text-xs rounded whitespace-nowrap ${
                selectedType === type
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
          <button
            onClick={() => setShowOptimizedOnly(!showOptimizedOnly)}
            className={`px-2 py-1 text-xs rounded whitespace-nowrap flex items-center gap-1 ${
              showOptimizedOnly
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <Shield className="w-3 h-3" />
            Optimized
          </button>
        </div>
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>Total: {formatFileSize(totalSize)}</span>
          {savings > 0 && (
            <span className="text-green-400">
              Savings: {formatFileSize(savings)} ({savingsPercent.toFixed(1)}%)
            </span>
          )}
        </div>
      </div>

      {/* Assets List/Grid */}
      <div className="flex-1 overflow-y-auto p-2">
        {filteredAssets.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
            <BookOpen className="w-8 h-8 mb-2 opacity-50" />
            <p>No assets found</p>
            {(searchQuery || selectedType !== 'all' || showOptimizedOnly) && (
              <button
                onClick={() => {
                  setSearchQuery('')
                  setSelectedType('all')
                  setShowOptimizedOnly(false)
                }}
                className="mt-2 px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 rounded text-white"
              >
                Clear Filters
              </button>
            )}
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-2 gap-2">
            {filteredAssets.map((asset) => (
              <div
                key={asset.id}
                onClick={() => setSelectedAsset(asset)}
                className={`p-2 rounded border cursor-pointer transition-colors ${
                  selectedAsset?.id === asset.id
                    ? 'bg-blue-600/20 border-blue-500'
                    : 'bg-gray-700 border-gray-600 hover:bg-gray-600'
                }`}
              >
                <div className="flex items-center justify-center h-16 mb-2 bg-gray-800 rounded relative">
                  {getAssetIcon(asset.type)}
                  {asset.optimized && (
                    <span className="absolute top-1 right-1 px-1 py-0.5 bg-green-600/20 text-green-400 text-xs rounded flex items-center gap-0.5">
                      <Shield className="w-2.5 h-2.5" />
                    </span>
                  )}
                  {asset.vifConfidence !== undefined && (
                    <span className={`absolute bottom-1 left-1 px-1 py-0.5 text-xs rounded flex items-center gap-0.5 ${
                      asset.vifConfidence >= 0.95 ? 'bg-green-600/20 text-green-400' :
                      asset.vifConfidence >= 0.90 ? 'bg-yellow-600/20 text-yellow-400' :
                      'bg-red-600/20 text-red-400'
                    }`} title="VIF Confidence">
                      <Shield className="w-2.5 h-2.5" />
                      {(asset.vifConfidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
                <div className="text-xs text-gray-300 truncate mb-1" title={asset.name}>
                  {asset.name}
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-500">
                    {asset.optimized && asset.optimizationSize ? formatFileSize(asset.optimizationSize) : formatFileSize(asset.size)}
                  </span>
                  {asset.usageCount !== undefined && (
                    <span className="text-gray-500">{asset.usageCount} uses</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-1">
            {filteredAssets.map((asset) => (
              <div
                key={asset.id}
                onClick={() => setSelectedAsset(asset)}
                className={`flex items-center gap-2 p-2 rounded cursor-pointer transition-colors ${
                  selectedAsset?.id === asset.id
                    ? 'bg-blue-600/20 border border-blue-500'
                    : 'bg-gray-700 hover:bg-gray-600 border border-transparent'
                }`}
              >
                {getAssetIcon(asset.type)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="text-sm text-gray-300 truncate" title={asset.name}>
                      {asset.name}
                    </div>
                    {asset.optimized && (
                      <span className="px-1 py-0.5 bg-green-600/20 text-green-400 text-xs rounded flex items-center gap-0.5">
                        <Shield className="w-2.5 h-2.5" />
                        Optimized
                      </span>
                    )}
                    {asset.vifConfidence !== undefined && (
                      <span className={`px-1 py-0.5 text-xs rounded flex items-center gap-0.5 ${
                        asset.vifConfidence >= 0.95 ? 'bg-green-600/20 text-green-400' :
                        asset.vifConfidence >= 0.90 ? 'bg-yellow-600/20 text-yellow-400' :
                        'bg-red-600/20 text-red-400'
                      }`} title="VIF Confidence">
                        <Shield className="w-2.5 h-2.5" />
                        {(asset.vifConfidence * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span>
                      {asset.optimized && asset.optimizationSize ? formatFileSize(asset.optimizationSize) : formatFileSize(asset.size)}
                      {asset.optimized && asset.optimizationSize && (
                        <span className="line-through text-gray-600 ml-1">{formatFileSize(asset.size)}</span>
                      )}
                    </span>
                    {asset.usageCount !== undefined && (
                      <>
                        <span>•</span>
                        <span>{asset.usageCount} uses</span>
                      </>
                    )}
                    {asset.lastUsed && (
                      <>
                        <span>•</span>
                        <span>{new Date(asset.lastUsed).toLocaleDateString()}</span>
                      </>
                    )}
                  </div>
                </div>
                <div className="flex gap-1">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setShowPreview(true)
                    }}
                    className="p-1 text-gray-400 hover:text-gray-300 hover:bg-gray-600 rounded"
                    aria-label="Preview asset"
                    title="Preview"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      navigator.clipboard.writeText(asset.url)
                    }}
                    className="p-1 text-gray-400 hover:text-gray-300 hover:bg-gray-600 rounded"
                    aria-label="Copy URL"
                    title="Copy URL"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Asset Detail / Footer */}
      {selectedAsset && (
        <div className="p-3 border-t border-gray-700 bg-gray-900 shrink-0 max-h-96 overflow-y-auto">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-white">{selectedAsset.name}</h3>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setShowPreview(true)}
                className="p-1 text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded"
                title="Preview"
              >
                <Eye className="w-3 h-3" />
              </button>
              <button
                onClick={() => setSelectedAsset(null)}
                className="text-gray-400 hover:text-gray-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
          <div className="space-y-1 text-xs text-gray-400">
            <div className="flex justify-between">
              <span>Type:</span>
              <span className="text-gray-300 capitalize">{selectedAsset.type}</span>
            </div>
            <div className="flex justify-between">
              <span>Size:</span>
              <div className="flex items-center gap-2">
                {selectedAsset.optimized && selectedAsset.optimizationSize ? (
                  <>
                    <span className="text-green-400">{formatFileSize(selectedAsset.optimizationSize)}</span>
                    <span className="line-through text-gray-600">{formatFileSize(selectedAsset.size)}</span>
                    <span className="text-green-400">
                      ({Math.round(((selectedAsset.size - selectedAsset.optimizationSize) / selectedAsset.size) * 100)}% saved)
                    </span>
                  </>
                ) : (
                  <span className="text-gray-300">{formatFileSize(selectedAsset.size)}</span>
                )}
              </div>
            </div>
            <div className="flex justify-between">
              <span>Created:</span>
              <span className="text-gray-300">{new Date(selectedAsset.createdAt).toLocaleString()}</span>
            </div>
            {selectedAsset.lastUsed && (
              <div className="flex justify-between">
                <span>Last Used:</span>
                <span className="text-gray-300">{new Date(selectedAsset.lastUsed).toLocaleString()}</span>
              </div>
            )}
            {selectedAsset.usageCount !== undefined && (
              <div className="flex justify-between">
                <span>Usage Count:</span>
                <span className="text-gray-300">{selectedAsset.usageCount}</span>
              </div>
            )}
            {selectedAsset.vifConfidence !== undefined && (
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-1">
                  <Shield className="w-3 h-3" />
                  VIF Confidence:
                </span>
                <span className={`${
                  selectedAsset.vifConfidence >= 0.95 ? 'text-green-400' :
                  selectedAsset.vifConfidence >= 0.90 ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {(selectedAsset.vifConfidence * 100).toFixed(0)}%
                </span>
              </div>
            )}
            {selectedAsset.cmcAtomId && (
              <div className="flex justify-between">
                <span>CMC Atom:</span>
                <span className="text-purple-400 font-mono text-xs">{selectedAsset.cmcAtomId.substring(0, 12)}...</span>
              </div>
            )}
            {selectedAsset.metadata && (
              <div className="mt-2 pt-2 border-t border-gray-700">
                <div className="font-semibold mb-1">Metadata:</div>
                {Object.entries(selectedAsset.metadata).map(([key, value]) => (
                  <div key={key} className="text-gray-400">
                    <span className="text-gray-500">{key}:</span> {String(value)}
                  </div>
                ))}
              </div>
            )}
            <div className="mt-2 pt-2 border-t border-gray-700">
              <div className="font-semibold mb-1">Tags:</div>
              <div className="flex flex-wrap gap-1 mb-1">
                {selectedAsset.tags.map((tag) => (
                  <span key={tag} className="px-2 py-0.5 bg-blue-600/20 text-blue-300 rounded text-xs">
                    {tag}
                  </span>
                ))}
              </div>
              {selectedAsset.hhniTags && selectedAsset.hhniTags.length > 0 && (
                <>
                  <div className="font-semibold mb-1 mt-2 flex items-center gap-1">
                    <Brain className="w-3 h-3" />
                    HHNI Tags:
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {selectedAsset.hhniTags.map((tag) => (
                      <span key={tag} className="px-2 py-0.5 bg-purple-600/20 text-purple-300 rounded text-xs">
                        {tag}
                      </span>
                    ))}
                  </div>
                </>
              )}
            </div>
            <div className="flex gap-2 pt-2 border-t border-gray-700">
              <button
                onClick={() => navigator.clipboard.writeText(selectedAsset.url)}
                className="flex-1 px-2 py-1 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded text-xs flex items-center justify-center gap-1"
              >
                <Copy className="w-3 h-3" />
                Copy URL
              </button>
              <button
                onClick={() => {
                  const a = document.createElement('a')
                  a.href = selectedAsset.url
                  a.download = selectedAsset.name
                  a.click()
                }}
                className="flex-1 px-2 py-1 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded text-xs flex items-center justify-center gap-1"
              >
                <Download className="w-3 h-3" />
                Download
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {showPreview && selectedAsset && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4" onClick={() => setShowPreview(false)}>
          <div className="bg-gray-900 rounded-lg border border-gray-700 max-w-4xl max-h-[90vh] overflow-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between p-4 border-b border-gray-700">
              <h3 className="text-lg font-semibold text-white">{selectedAsset.name}</h3>
              <button
                onClick={() => setShowPreview(false)}
                className="text-gray-400 hover:text-gray-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-4">
              {selectedAsset.type === 'image' && (
                <img src={selectedAsset.url} alt={selectedAsset.name} className="max-w-full h-auto rounded" />
              )}
              {selectedAsset.type === 'video' && (
                <video src={selectedAsset.url} controls className="max-w-full rounded" />
              )}
              {selectedAsset.type === 'audio' && (
                <audio src={selectedAsset.url} controls className="w-full" />
              )}
              {!['image', 'video', 'audio'].includes(selectedAsset.type) && (
                <div className="text-center text-gray-400 py-8">
                  Preview not available for {selectedAsset.type} files
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Footer Actions */}
      <div className="h-10 bg-gray-900 border-t border-gray-700 flex items-center justify-between px-3 shrink-0">
        <button
          className="flex items-center gap-1 px-2 py-1 text-xs text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded transition-colors"
          aria-label="Upload asset"
          title="Upload asset"
        >
          <Upload className="w-4 h-4" />
          Upload
        </button>
        <div className="text-xs text-gray-500">
          {filteredAssets.length} {filteredAssets.length === 1 ? 'asset' : 'assets'}
          {savings > 0 && (
            <span className="ml-2 text-green-400">
              • {formatFileSize(savings)} saved
            </span>
          )}
        </div>
      </div>
          </>
        )}
      </div>
    </ErrorBoundary>
  )
}

