// Debug Console Panel - AIM-OS Native Debugging Infrastructure
// Built in tandem with application - never an afterthought

export const DebugConsolePanel: React.FC<{
  console: any[]
  logsBySystem: any
  analysis: any
  infrastructure: any
}> = ({ console, logsBySystem, analysis, infrastructure }) => {
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null)
  const [filterLevel, setFilterLevel] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'error': return 'text-red-400'
      case 'warn': return 'text-yellow-400'
      case 'info': return 'text-blue-400'
      case 'log': return 'text-gray-300'
      case 'debug': return 'text-purple-400'
      default: return 'text-gray-400'
    }
  }

  const getLevelBg = (level: string) => {
    switch (level) {
      case 'error': return 'bg-red-900/30 border-red-700'
      case 'warn': return 'bg-yellow-900/30 border-yellow-700'
      case 'info': return 'bg-blue-900/30 border-blue-700'
      case 'log': return 'bg-gray-800 border-gray-700'
      case 'debug': return 'bg-purple-900/30 border-purple-700'
      default: return 'bg-gray-800 border-gray-700'
    }
  }

  const filteredConsole = console.filter((entry) => {
    if (filterLevel !== 'all' && entry.level !== filterLevel) return false
    if (searchQuery && !entry.message.toLowerCase().includes(searchQuery.toLowerCase())) return false
    if (selectedSystem && entry.source !== selectedSystem) return false
    return true
  })

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Header */}
      <div className="p-3 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center justify-between mb-2">
          <div>
            <div className="text-xs font-semibold text-purple-400 mb-1 flex items-center gap-2">
              <Bug className="w-4 h-4" />
              Debug Console
            </div>
            <div className="text-xs text-gray-500">
              AIM-OS Native Debugging • CMC-Backed Logs • HHNI Analysis • VIF Validation
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 text-xs text-gray-400">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <span>Infrastructure: Active</span>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2 mt-2">
          <div className="flex items-center gap-1 bg-gray-700 rounded px-2 py-1">
            <Filter className="w-3 h-3 text-gray-400" />
            <select
              value={filterLevel}
              onChange={(e) => setFilterLevel(e.target.value)}
              className="bg-transparent text-xs text-gray-300 border-none outline-none"
            >
              <option value="all">All Levels</option>
              <option value="log">Log</option>
              <option value="info">Info</option>
              <option value="warn">Warn</option>
              <option value="error">Error</option>
              <option value="debug">Debug</option>
            </select>
          </div>
          <div className="flex items-center gap-1 bg-gray-700 rounded px-2 py-1 flex-1">
            <Search className="w-3 h-3 text-gray-400" />
            <input
              type="text"
              placeholder="Search logs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent text-xs text-gray-300 border-none outline-none flex-1"
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="grid grid-cols-4 gap-4 p-3">
          {/* Console Logs */}
          <div className="col-span-3">
            <div className="mb-2 flex items-center justify-between">
              <div className="text-xs font-semibold text-gray-300">Console Logs ({filteredConsole.length})</div>
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <span>CMC-Backed</span>
                <span>•</span>
                <span>Bitemporal</span>
                <span>•</span>
                <span>Evidence-Linked</span>
              </div>
            </div>
            <div className="space-y-2">
              {filteredConsole.map((entry) => (
                <div
                  key={entry.id}
                  className={`rounded p-2 border ${getLevelBg(entry.level)}`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-semibold ${getLevelColor(entry.level)}`}>
                        [{entry.level.toUpperCase()}]
                      </span>
                      <span className="text-xs text-gray-400">{entry.source}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <span>Conf: {(entry.confidence * 100).toFixed(0)}%</span>
                      <span>{new Date(entry.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>
                  <div className="text-xs text-gray-300 mb-1">{entry.message}</div>
                  {entry.context && (
                    <div className="text-xs text-gray-500 mt-1">
                      Context: {JSON.stringify(entry.context, null, 2)}
                    </div>
                  )}
                  <div className="flex items-center gap-2 text-xs text-gray-600 mt-1">
                    <span>Evidence: {entry.evidence.join(', ')}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Sidebar */}
          <div className="col-span-1 space-y-3">
            {/* System Logs */}
            <div className="bg-gray-800 rounded p-2 border border-gray-700">
              <div className="text-xs font-semibold text-gray-300 mb-2">By System</div>
              <div className="space-y-1">
                {Object.entries(logsBySystem).map(([system, logs]: [string, any]) => (
                  <button
                    key={system}
                    onClick={() => setSelectedSystem(selectedSystem === system ? null : system)}
                    className={`w-full text-left px-2 py-1 rounded text-xs transition-colors ${
                      selectedSystem === system
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span>{system}</span>
                      <span className="text-xs opacity-75">{logs.length}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Infrastructure Status */}
            <div className="bg-gray-800 rounded p-2 border border-gray-700">
              <div className="text-xs font-semibold text-gray-300 mb-2">Infrastructure</div>
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Logging</span>
                  <span className={`${infrastructure.logging.enabled ? 'text-green-400' : 'text-red-400'}`}>
                    {infrastructure.logging.enabled ? '✓' : '✗'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Analysis</span>
                  <span className={`${infrastructure.analysis.enabled ? 'text-green-400' : 'text-red-400'}`}>
                    {infrastructure.analysis.enabled ? '✓' : '✗'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">CMC Integration</span>
                  <span className={`${infrastructure.integration.cmc.enabled ? 'text-green-400' : 'text-red-400'}`}>
                    {infrastructure.integration.cmc.enabled ? '✓' : '✗'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">HHNI Analysis</span>
                  <span className={`${infrastructure.integration.hhni.enabled ? 'text-green-400' : 'text-red-400'}`}>
                    {infrastructure.integration.hhni.enabled ? '✓' : '✗'}
                  </span>
                </div>
              </div>
            </div>

            {/* Analysis Insights */}
            <div className="bg-gray-800 rounded p-2 border border-gray-700">
              <div className="text-xs font-semibold text-gray-300 mb-2">Insights</div>
              <div className="space-y-2">
                {analysis.insights.slice(0, 3).map((insight: any, idx: number) => (
                  <div key={idx} className="text-xs text-gray-400">
                    <div className="text-gray-300 mb-1">{insight.insight}</div>
                    <div className="text-gray-500">Conf: {(insight.confidence * 100).toFixed(0)}%</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

