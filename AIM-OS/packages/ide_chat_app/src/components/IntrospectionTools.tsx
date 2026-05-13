import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import {
  Brain,
  Activity,
  Zap,
  Target,
  Eye,
  EyeOff,
  Maximize2,
  Minimize2,
  RotateCcw,
  Play,
  Pause,
  Square,
  Settings,
  Filter,
  Search,
  RefreshCw,
  Download,
  Upload,
  Save,
  FilePen as Open,
  X as Close,
  Plus,
  Minus,
  X,
  Check,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ChevronUp,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  MoreHorizontal,
  MoreVertical,
  Menu,
  Home,
  User,
  Users,
  UserPlus,
  UserMinus,
  UserCheck,
  UserX,
  LogIn,
  LogOut,
  Key,
  KeyRound,
  LockKeyhole,
  UnlockKeyhole,
  Fingerprint,
  Scan,
  QrCode,
  Barcode,
  CreditCard,
  Wallet,
  Coins,
  DollarSign,
  Euro,
  PoundSterling,
  DollarSign as Yen,
  Bitcoin,
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  LineChart,
  Clock,
  FileText,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info,
  Sparkles,
  Network,
  Layers,
  Cpu,
  HardDrive as Memory,
  HardDrive,
  Wifi,
  Shield,
  Lock,
  Unlock,
  Globe,
  Database,
  Server,
  Cloud,
  Smartphone,
  Monitor,
  Laptop,
  Tablet,
  Watch,
  Headphones,
  Camera,
  Mic,
  Speaker,
  WifiOff,
  Signal,
  Battery,
  BatteryLow,
  BatteryMedium,
  Battery as BatteryHigh,
  BatteryFull,
  Power,
  PowerOff,
  Zap as Lightning,
  Sun,
  Moon,
  Star,
  Heart,
  ThumbsUp,
  ThumbsDown,
  MessageCircle,
  Mail,
  Phone,
  Video,
  Image,
  File,
  Folder,
  FolderOpen,
  Archive,
  Trash2,
  Edit,
  Copy,
  Scissors as Cut,
  Clipboard as Paste,
  Save as SaveIcon,
  Save as SaveAsIcon,
  FilePen as OpenIcon,
  X as CloseIcon,
  Plus as PlusIcon,
  Minus as MinusIcon,
  X as XIcon,
  Check as CheckIcon,
  ArrowUp as ArrowUpIcon,
  ArrowDown as ArrowDownIcon,
  ArrowLeft as ArrowLeftIcon,
  ArrowRight as ArrowRightIcon,
  ChevronUp as ChevronUpIcon,
  ChevronDown as ChevronDownIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  MoreHorizontal as MoreHorizontalIcon,
  MoreVertical as MoreVerticalIcon,
  Menu as MenuIcon,
  Home as HomeIcon,
  User as UserIcon,
  Users as UsersIcon,
  UserPlus as UserPlusIcon,
  UserMinus as UserMinusIcon,
  UserCheck as UserCheckIcon,
  UserX as UserXIcon,
  LogIn as LogInIcon,
  LogOut as LogOutIcon,
  Key as KeyIcon,
  KeyRound as KeyRoundIcon,
  LockKeyhole as LockKeyholeIcon,
  UnlockKeyhole as UnlockKeyholeIcon,
  Fingerprint as FingerprintIcon,
  Scan as ScanIcon,
  QrCode as QrCodeIcon,
  Barcode as BarcodeIcon,
  CreditCard as CreditCardIcon,
  Wallet as WalletIcon,
  Coins as CoinsIcon,
  DollarSign as DollarSignIcon,
  Euro as EuroIcon,
  PoundSterling as PoundSterlingIcon,
  DollarSign as YenIcon,
  Bitcoin as BitcoinIcon,
  List,
  Grid3X3,
} from 'lucide-react'

interface IntrospectionData {
  id: string
  timestamp: string
  type: 'thought' | 'emotion' | 'decision' | 'pattern' | 'memory' | 'insight'
  content: string
  intensity: number
  confidence: number
  metadata: {
    source: string
    context: string
    tags: string[]
    related: string[]
    influence: number
    stability: number
  }
}

interface IntrospectionToolsProps {
  className?: string
  data?: IntrospectionData[]
  onDataSelect?: (dataId: string) => void
  onDataUpdate?: (data: IntrospectionData) => void
  onDataDelete?: (dataId: string) => void
  enableRealTimeUpdates?: boolean
  enableAnalysis?: boolean
  enableVisualization?: boolean
  theme?: 'dark' | 'light' | 'auto'
  layout?: 'grid' | 'list' | 'timeline' | 'network'
  filters?: {
    type?: string[]
    intensity?: { min: number; max: number }
    confidence?: { min: number; max: number }
    timeRange?: { start: Date; end: Date }
    searchQuery?: string
  }
}

export default function IntrospectionTools({
  className = '',
  data = [],
  onDataSelect,
  onDataUpdate,
  onDataDelete,
  enableRealTimeUpdates = true,
  enableAnalysis = true,
  enableVisualization = true,
  theme = 'dark',
  layout = 'grid',
  filters = {},
}: IntrospectionToolsProps) {
  const [introspectionData, setIntrospectionData] = useState<IntrospectionData[]>(data)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedTab, setSelectedTab] = useState<'overview' | 'thoughts' | 'emotions' | 'decisions' | 'patterns' | 'memories' | 'insights' | 'analysis' | 'visualization'>('overview')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'timestamp' | 'intensity' | 'confidence' | 'type'>('timestamp')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [viewMode, setViewMode] = useState<'grid' | 'list' | 'timeline' | 'network'>('grid')
  const [selectedData, setSelectedData] = useState<Set<string>>(new Set())
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview', 'thoughts']))
  const [showFilters, setShowFilters] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'reconnecting'>('connected')
  const [analysisResults, setAnalysisResults] = useState<{
    patterns: any[]
    insights: any[]
    trends: any[]
    correlations: any[]
  } | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isVisualizing, setIsVisualizing] = useState(false)

  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const analysisWorkerRef = useRef<Worker | null>(null)

  // Generate mock data if none provided
  const mockData = useMemo(() => {
    if (data.length > 0) return data
    
    const types = ['thought', 'emotion', 'decision', 'pattern', 'memory', 'insight']
    const sources = ['consciousness', 'subconscious', 'memory', 'pattern', 'analysis']
    const contexts = ['work', 'personal', 'creative', 'analytical', 'reflective']
    const mockData: IntrospectionData[] = []
    
    for (let i = 0; i < 100; i++) {
      const type = types[Math.floor(Math.random() * types.length)]
      const intensity = Math.random()
      const confidence = Math.random()
      const timestamp = new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000)
      
      mockData.push({
        id: `introspection-${i}`,
        timestamp: timestamp.toISOString(),
        type: type as any,
        content: generateMockContent(type, intensity),
        intensity,
        confidence,
        metadata: {
          source: sources[Math.floor(Math.random() * sources.length)],
          context: contexts[Math.floor(Math.random() * contexts.length)],
          tags: generateMockTags(type),
          related: [],
          influence: Math.random(),
          stability: Math.random()
        }
      })
    }
    
    return mockData
  }, [data])

  // Filter data based on filters
  const filteredData = useMemo(() => {
    let filtered = mockData
    
    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(item => 
        item.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.metadata.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    }
    
    // Apply type filter
    if (filters.type && filters.type.length > 0) {
      filtered = filtered.filter(item => filters.type!.includes(item.type))
    }
    
    // Apply intensity filter
    if (filters.intensity) {
      filtered = filtered.filter(item => 
        item.intensity >= filters.intensity!.min && item.intensity <= filters.intensity!.max
      )
    }
    
    // Apply confidence filter
    if (filters.confidence) {
      filtered = filtered.filter(item => 
        item.confidence >= filters.confidence!.min && item.confidence <= filters.confidence!.max
      )
    }
    
    // Apply time range filter
    if (filters.timeRange) {
      filtered = filtered.filter(item => {
        const itemTime = new Date(item.timestamp)
        return itemTime >= filters.timeRange!.start && itemTime <= filters.timeRange!.end
      })
    }
    
    // Apply sorting
    filtered.sort((a, b) => {
      let comparison = 0
      
      switch (sortBy) {
        case 'timestamp':
          comparison = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
          break
        case 'intensity':
          comparison = a.intensity - b.intensity
          break
        case 'confidence':
          comparison = a.confidence - b.confidence
          break
        case 'type':
          comparison = a.type.localeCompare(b.type)
          break
      }
      
      return sortOrder === 'asc' ? comparison : -comparison
    })
    
    return filtered
  }, [mockData, searchQuery, filters, sortBy, sortOrder])

  // Run analysis
  const runAnalysis = useCallback(async () => {
    if (!enableAnalysis) return
    
    setIsAnalyzing(true)
    setError(null)
    
    try {
      // Simulate analysis
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const patterns = analyzePatterns(filteredData)
      const insights = generateInsights(filteredData)
      const trends = analyzeTrends(filteredData)
      const correlations = analyzeCorrelations(filteredData)
      
      setAnalysisResults({
        patterns,
        insights,
        trends,
        correlations
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setIsAnalyzing(false)
    }
  }, [enableAnalysis, filteredData])

  // Auto-refresh functionality
  useEffect(() => {
    if (enableRealTimeUpdates) {
      refreshIntervalRef.current = setInterval(() => {
        // Simulate new data
        const newData: IntrospectionData = {
          id: `introspection-${Date.now()}`,
          timestamp: new Date().toISOString(),
          type: 'thought',
          content: 'New introspection data...',
          intensity: Math.random(),
          confidence: Math.random(),
          metadata: {
            source: 'consciousness',
            context: 'real-time',
            tags: ['auto-generated'],
            related: [],
            influence: Math.random(),
            stability: Math.random()
          }
        }
        
        setIntrospectionData(prev => [newData, ...prev])
        setLastUpdate(new Date())
      }, 5000)
    }
    
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current)
      }
    }
  }, [enableRealTimeUpdates])

  // Run initial analysis
  useEffect(() => {
    if (enableAnalysis && filteredData.length > 0) {
      runAnalysis()
    }
  }, [enableAnalysis, filteredData.length, runAnalysis])

  const handleDataClick = useCallback((dataId: string) => {
    if (onDataSelect) {
      onDataSelect(dataId)
    }
    
    setSelectedData(prev => {
      const newSet = new Set(prev)
      if (newSet.has(dataId)) {
        newSet.delete(dataId)
      } else {
        newSet.add(dataId)
      }
      return newSet
    })
  }, [onDataSelect])

  const handleDataUpdate = useCallback((data: IntrospectionData) => {
    setIntrospectionData(prev => 
      prev.map(item => item.id === data.id ? data : item)
    )
    
    if (onDataUpdate) {
      onDataUpdate(data)
    }
  }, [onDataUpdate])

  const handleDataDelete = useCallback((dataId: string) => {
    setIntrospectionData(prev => prev.filter(item => item.id !== dataId))
    
    if (onDataDelete) {
      onDataDelete(dataId)
    }
  }, [onDataDelete])

  const toggleSection = useCallback((section: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev)
      if (newSet.has(section)) {
        newSet.delete(section)
      } else {
        newSet.add(section)
      }
      return newSet
    })
  }, [])

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-400">
            {filteredData.filter(d => d.type === 'thought').length}
          </div>
          <div className="text-sm text-gray-400">Thoughts</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-red-400">
            {filteredData.filter(d => d.type === 'emotion').length}
          </div>
          <div className="text-sm text-gray-400">Emotions</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-400">
            {filteredData.filter(d => d.type === 'decision').length}
          </div>
          <div className="text-sm text-gray-400">Decisions</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-purple-400">
            {filteredData.filter(d => d.type === 'pattern').length}
          </div>
          <div className="text-sm text-gray-400">Patterns</div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-gray-800/50 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
        <div className="space-y-2">
          {filteredData.slice(0, 5).map((item) => (
            <div key={item.id} className="flex items-center justify-between p-2 bg-gray-700/50 rounded">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${
                  item.type === 'thought' ? 'bg-blue-400' :
                  item.type === 'emotion' ? 'bg-red-400' :
                  item.type === 'decision' ? 'bg-green-400' :
                  'bg-purple-400'
                }`} />
                <span className="text-white text-sm">{item.content.substring(0, 50)}...</span>
              </div>
              <span className="text-xs text-gray-400">
                {new Date(item.timestamp).toLocaleTimeString()}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Analysis Results */}
      {analysisResults && (
        <div className="bg-gray-800/50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-white mb-4">Analysis Results</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-xl font-bold text-yellow-400">
                {analysisResults.patterns.length}
              </div>
              <div className="text-sm text-gray-400">Patterns</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-orange-400">
                {analysisResults.insights.length}
              </div>
              <div className="text-sm text-gray-400">Insights</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-cyan-400">
                {analysisResults.trends.length}
              </div>
              <div className="text-sm text-gray-400">Trends</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-pink-400">
                {analysisResults.correlations.length}
              </div>
              <div className="text-sm text-gray-400">Correlations</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )

  const renderDataList = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">
          {selectedTab.charAt(0).toUpperCase() + selectedTab.slice(1)} ({filteredData.length})
        </h3>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white"
          >
            {viewMode === 'grid' ? <List className="w-4 h-4" /> : <Grid3X3 className="w-4 h-4" />}
          </button>
        </div>
      </div>
      
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredData.map((item) => {
            const isSelected = selectedData.has(item.id)
            
            return (
              <div
                key={item.id}
                onClick={() => handleDataClick(item.id)}
                className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 ${
                  isSelected 
                    ? 'bg-blue-900/30 border-blue-500' 
                    : 'bg-gray-800/50 border-gray-700 hover:bg-gray-700/50'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-medium text-white text-sm">{item.type}</h4>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      item.intensity > 0.7 ? 'bg-red-400' :
                      item.intensity > 0.4 ? 'bg-yellow-400' : 'bg-green-400'
                    }`} />
                    <span className="text-xs text-gray-400">
                      {(item.intensity * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-300 mb-2">{item.content}</p>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{new Date(item.timestamp).toLocaleDateString()}</span>
                  <span>{(item.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        <div className="space-y-2">
          {filteredData.map((item) => {
            const isSelected = selectedData.has(item.id)
            
            return (
              <div
                key={item.id}
                onClick={() => handleDataClick(item.id)}
                className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 ${
                  isSelected 
                    ? 'bg-blue-900/30 border-blue-500' 
                    : 'bg-gray-800/50 border-gray-700 hover:bg-gray-700/50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      item.intensity > 0.7 ? 'bg-red-400' :
                      item.intensity > 0.4 ? 'bg-yellow-400' : 'bg-green-400'
                    }`} />
                    <div>
                      <h4 className="font-medium text-white">{item.type}</h4>
                      <p className="text-sm text-gray-300">{item.content}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">
                      {(item.intensity * 100).toFixed(0)}%
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(item.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )

  const renderAnalysis = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Analysis</h3>
        <button
          onClick={runAnalysis}
          disabled={isAnalyzing}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg flex items-center gap-2"
        >
          {isAnalyzing ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Activity className="w-4 h-4" />
          )}
          {isAnalyzing ? 'Analyzing...' : 'Run Analysis'}
        </button>
      </div>
      
      {analysisResults ? (
        <div className="space-y-4">
          {/* Patterns */}
          <div className="bg-gray-800/50 rounded-lg p-4">
            <h4 className="text-md font-semibold text-white mb-4">Patterns</h4>
            <div className="space-y-2">
              {analysisResults.patterns.map((pattern, index) => (
                <div key={index} className="p-3 bg-gray-700/50 rounded">
                  <div className="text-white text-sm">{pattern.description}</div>
                  <div className="text-xs text-gray-400 mt-1">
                    Confidence: {(pattern.confidence * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Insights */}
          <div className="bg-gray-800/50 rounded-lg p-4">
            <h4 className="text-md font-semibold text-white mb-4">Insights</h4>
            <div className="space-y-2">
              {analysisResults.insights.map((insight, index) => (
                <div key={index} className="p-3 bg-gray-700/50 rounded">
                  <div className="text-white text-sm">{insight.description}</div>
                  <div className="text-xs text-gray-400 mt-1">
                    Impact: {(insight.impact * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Trends */}
          <div className="bg-gray-800/50 rounded-lg p-4">
            <h4 className="text-md font-semibold text-white mb-4">Trends</h4>
            <div className="space-y-2">
              {analysisResults.trends.map((trend, index) => (
                <div key={index} className="p-3 bg-gray-700/50 rounded">
                  <div className="text-white text-sm">{trend.description}</div>
                  <div className="text-xs text-gray-400 mt-1">
                    Direction: {trend.direction}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Correlations */}
          <div className="bg-gray-800/50 rounded-lg p-4">
            <h4 className="text-md font-semibold text-white mb-4">Correlations</h4>
            <div className="space-y-2">
              {analysisResults.correlations.map((correlation, index) => (
                <div key={index} className="p-3 bg-gray-700/50 rounded">
                  <div className="text-white text-sm">{correlation.description}</div>
                  <div className="text-xs text-gray-400 mt-1">
                    Strength: {(correlation.strength * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-400">No analysis results available</p>
          <p className="text-sm text-gray-500 mt-2">Click "Run Analysis" to analyze your introspection data</p>
        </div>
      )}
    </div>
  )

  const renderVisualization = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-white">Visualization</h3>
      
      <div className="h-96 bg-gray-800/50 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <Brain className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-400">Consciousness visualization would go here</p>
          <p className="text-sm text-gray-500 mt-2">
            Interactive 3D visualization of introspection data
          </p>
        </div>
      </div>
    </div>
  )

  return (
    <div className={`bg-gray-900 text-white ${isFullscreen ? 'fixed inset-0 z-50' : ''} ${className}`}>
      {/* Header */}
      <div className="border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Brain className="w-6 h-6 text-purple-400" />
              Introspection Tools
            </h2>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                connectionStatus === 'connected' ? 'bg-green-400' : 
                connectionStatus === 'reconnecting' ? 'bg-yellow-400' : 'bg-red-400'
              }`} />
              <span className="text-sm text-gray-400 capitalize">{connectionStatus}</span>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search introspection data..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
              />
            </div>
            
            {/* Refresh */}
            <button
              onClick={() => setLastUpdate(new Date())}
              className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white"
              title="Refresh data"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            
            {/* Settings */}
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white"
              title="Settings"
            >
              <Settings className="w-4 h-4" />
            </button>
            
            {/* Fullscreen */}
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white"
              title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>
          </div>
        </div>
        
        {/* Tabs */}
        <div className="flex items-center gap-1 mt-4">
          {[
            { id: 'overview', label: 'Overview', icon: Activity },
            { id: 'thoughts', label: 'Thoughts', icon: Brain },
            { id: 'emotions', label: 'Emotions', icon: Heart },
            { id: 'decisions', label: 'Decisions', icon: Target },
            { id: 'patterns', label: 'Patterns', icon: Network },
            { id: 'memories', label: 'Memories', icon: Clock },
            { id: 'insights', label: 'Insights', icon: Sparkles },
            { id: 'analysis', label: 'Analysis', icon: BarChart3 },
            { id: 'visualization', label: 'Visualization', icon: Eye },
          ].map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setSelectedTab(tab.id as any)}
                className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                  selectedTab === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            )
          })}
        </div>
      </div>
      
      {/* Content */}
      <div className="p-4 h-full overflow-auto">
        {selectedTab === 'overview' && renderOverview()}
        {selectedTab === 'thoughts' && renderDataList()}
        {selectedTab === 'emotions' && renderDataList()}
        {selectedTab === 'decisions' && renderDataList()}
        {selectedTab === 'patterns' && renderDataList()}
        {selectedTab === 'memories' && renderDataList()}
        {selectedTab === 'insights' && renderDataList()}
        {selectedTab === 'analysis' && renderAnalysis()}
        {selectedTab === 'visualization' && renderVisualization()}
      </div>
    </div>
  )
}

// Helper functions
function generateMockContent(type: string, intensity: number): string {
  const contentTemplates = {
    thought: [
      "I'm thinking about the nature of consciousness and how it emerges from complex systems.",
      "The relationship between mind and matter seems to be more intricate than I initially thought.",
      "What if consciousness is not binary but exists on a spectrum?",
      "I wonder how my thoughts influence my decisions and vice versa."
    ],
    emotion: [
      "I feel a deep sense of wonder when contemplating the mysteries of existence.",
      "There's a subtle joy in discovering new patterns in my own thinking.",
      "I experience a sense of connection when I realize how everything is interconnected.",
      "Sometimes I feel overwhelmed by the complexity of my own consciousness."
    ],
    decision: [
      "I've decided to focus more on understanding my own thought processes.",
      "I choose to approach this problem from a different angle.",
      "I'm going to prioritize learning over immediate results.",
      "I've made the decision to be more mindful of my mental patterns."
    ],
    pattern: [
      "I notice that my most creative thoughts often come during moments of relaxation.",
      "There's a pattern where my emotions influence my decision-making process.",
      "I see a correlation between my energy levels and my problem-solving ability.",
      "I've identified a recurring pattern in how I process new information."
    ],
    memory: [
      "I remember a time when I had a similar insight about consciousness.",
      "This reminds me of a previous experience where I felt deeply connected to something greater.",
      "I recall a moment when I first understood the concept of self-awareness.",
      "I have a memory of feeling completely present and aware."
    ],
    insight: [
      "I've gained a new understanding of how my mind works.",
      "I've had a breakthrough realization about the nature of consciousness.",
      "I've discovered a new way of thinking about my own thought processes.",
      "I've achieved a deeper level of self-awareness."
    ]
  }
  
  const templates = contentTemplates[type as keyof typeof contentTemplates] || contentTemplates.thought
  return templates[Math.floor(Math.random() * templates.length)]
}

function generateMockTags(type: string): string[] {
  const tagSets = {
    thought: ['philosophy', 'consciousness', 'thinking', 'reflection'],
    emotion: ['feeling', 'mood', 'sensation', 'experience'],
    decision: ['choice', 'action', 'commitment', 'direction'],
    pattern: ['recurring', 'systematic', 'regular', 'predictable'],
    memory: ['past', 'recall', 'nostalgia', 'experience'],
    insight: ['understanding', 'realization', 'breakthrough', 'awareness']
  }
  
  const tags = tagSets[type as keyof typeof tagSets] || tagSets.thought
  return tags.slice(0, Math.floor(Math.random() * 3) + 1)
}

function analyzePatterns(data: IntrospectionData[]): any[] {
  // Mock pattern analysis
  return [
    {
      description: "High intensity thoughts often occur during morning hours",
      confidence: 0.85,
      frequency: 0.7
    },
    {
      description: "Emotional states correlate with decision-making patterns",
      confidence: 0.72,
      frequency: 0.6
    }
  ]
}

function generateInsights(data: IntrospectionData[]): any[] {
  // Mock insight generation
  return [
    {
      description: "Your consciousness shows signs of increasing self-awareness",
      impact: 0.9,
      category: "growth"
    },
    {
      description: "There's a strong connection between your thoughts and emotions",
      impact: 0.8,
      category: "integration"
    }
  ]
}

function analyzeTrends(data: IntrospectionData[]): any[] {
  // Mock trend analysis
  return [
    {
      description: "Increasing frequency of introspective thoughts over time",
      direction: "upward",
      strength: 0.75
    },
    {
      description: "Decreasing intensity of negative emotions",
      direction: "downward",
      strength: 0.65
    }
  ]
}

function analyzeCorrelations(data: IntrospectionData[]): any[] {
  // Mock correlation analysis
  return [
    {
      description: "Thought intensity correlates with emotional intensity",
      strength: 0.8,
      significance: 0.95
    },
    {
      description: "Decision confidence correlates with pattern recognition",
      strength: 0.7,
      significance: 0.85
    }
  ]
}
