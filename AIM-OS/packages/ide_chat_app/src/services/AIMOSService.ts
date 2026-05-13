/**
 * AIM-OS Service Layer
 * Provides HTTP API integration with AIM-OS backend systems
 * 
 * Phase 1: Core Systems Integration (CMC, HHNI, VIF, APOE, SEG)
 * Phase 1.5: Voice I/O (TTS/SST), RAG MCP Tools, Daemon, Automation
 * 
 * Created: 2025-10-30
 * Agent: Lexicon
 */

export interface MemoryAtom {
  atom_id: string
  content: string
  modality: string
  tags: Record<string, number>
  created_at: string
  snapshot_id?: string
}

export interface MemoryStats {
  total_atoms: number
  total_size: number
  modality_counts: Record<string, number>
  tag_counts: Record<string, number>
  hhni_indexed_nodes: number
  vif_tracked_predictions: number
  ece_score?: number
}

export interface ConfidenceRecord {
  task: string
  confidence: number
  reasoning?: string
  evidence?: string[]
  timestamp: string
  status: 'high' | 'medium' | 'low'
  decision_id?: string
  witness_id?: string
  kappa_gate_passed?: boolean
  confidence_band?: string
}

export interface Plan {
  plan_id: string
  goal: string
  steps: PlanStep[]
  status: 'pending' | 'executing' | 'completed' | 'failed'
  created_at: string
  estimated_time?: number
}

export interface PlanStep {
  step_id: string
  description: string
  status: 'pending' | 'executing' | 'completed' | 'failed'
  order: number
  role?: string
  dependencies?: string[]
}

export interface KnowledgeSynthesis {
  topics: string[]
  depth: 'shallow' | 'medium' | 'deep'
  entities_found: number
  relations_found: number
  synthesis_results: Array<{
    entity_id: string
    entity_name: string
    entity_type: string
    confidence: number
    provenance_chain_length: number
    related_entities: string[]
  }>
  insights: string[]
}

export interface SystemStatus {
  cmc: {
    connected: boolean
    atoms_count: number
    status: 'healthy' | 'degraded' | 'offline'
  }
  hhni: {
    connected: boolean
    indexed_nodes: number
    status: 'healthy' | 'degraded' | 'offline'
  }
  vif: {
    connected: boolean
    tracked_predictions: number
    ece_score?: number
    status: 'healthy' | 'degraded' | 'offline'
  }
  apoe: {
    connected: boolean
    active_plans: number
    status: 'healthy' | 'degraded' | 'offline'
  }
  seg: {
    connected: boolean
    entities_count: number
    relations_count: number
    status: 'healthy' | 'degraded' | 'offline'
  }
  daemon: {
    connected: boolean
    status: 'healthy' | 'degraded' | 'offline'
  }
  rag_mcp: {
    connected: boolean
    tools_indexed: number
    status: 'healthy' | 'degraded' | 'offline'
  }
  voice: {
    tts_available: boolean
    sst_available: boolean
    status: 'healthy' | 'degraded' | 'offline'
  }
}

export interface VoiceTranscript {
  text: string
  confidence: number
  timestamp: string
  duration_ms: number
  raw_audio_hash?: string
}

export interface VoiceSynthesis {
  audio_url?: string
  audio_data?: ArrayBuffer
  duration_ms: number
  voice_id?: string
  text: string
}

export interface ToolSelection {
  tool_id: string
  name: string
  description: string
  category: string
  relevance_score: number
  consciousness_weight: number
  final_score: number
}

export interface AutomationTask {
  task_id: string
  name: string
  description: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  created_at: string
  started_at?: string
  completed_at?: string
  result?: any
  error?: string
}

class AIMOSService {
  private baseUrl: string = 'http://localhost:8000'
  private commandServerUrl: string = 'http://localhost:5001'
  private fallbackCommandServerUrl: string = 'http://localhost:5003'
  private mcpBaseUrl: string = 'http://localhost:8000/mcp'
  private daemonBaseUrl: string = 'http://localhost:5000'
  private ragMcpBaseUrl: string = 'http://localhost:8001'
  private isConnected: boolean = false
  private daemonConnected: boolean = false
  private ragMcpConnected: boolean = false
  
  // Voice I/O (TTS/SST)
  private recognition: any = null
  private synthesis: SpeechSynthesis | null = null
  private isVoiceInitialized: boolean = false

  constructor(baseUrl?: string) {
    if (baseUrl) {
      this.baseUrl = baseUrl
      this.mcpBaseUrl = `${baseUrl}/mcp`
    }
    this.checkConnection()
    this.initializeVoice()
  }

  /**
   * Check connection to AIM-OS backend
   */
  private async checkConnection(): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      })
      this.isConnected = response.ok
      if (this.isConnected) {
        console.log('✅ Connected to AIM-OS backend')
      }
    } catch (error) {
      this.isConnected = false
      console.warn('⚠️ AIM-OS backend not available, using fallback mode')
    }
  }

  /**
   * Normalize MCP tool names from legacy prefixed forms.
   */
  private normalizeMcpToolName(toolName: string): string {
    return toolName
      .replace(/^mcp_lucid-mcp_/, '')
      .replace(/^mcp_lucid_mcp_/, '')
      .replace(/^mcp:/, '')
      .trim()
  }

  /**
   * Try MCP collaboration tool routes in priority order:
   * 1) Command Server canonical endpoint (`/mcp/execute`, port 5001)
   * 2) Fallback bridge endpoint (`/mcp/execute`, port 5003)
   * 3) Backend canonical endpoint (`/mcp/execute`)
   * 4) Legacy backend endpoint (`/mcp/tools/call`)
   */
  private async callMcpCollaborationTool(
    toolName: string,
    args: Record<string, any>
  ): Promise<any | null> {
    const normalizedTool = this.normalizeMcpToolName(toolName)

    const attempts: Array<{ url: string; body: any; label: string }> = [
      {
        url: `${this.commandServerUrl}/mcp/execute`,
        body: { tool: normalizedTool, arguments: args },
        label: 'command-server:/mcp/execute'
      },
      {
        url: `${this.fallbackCommandServerUrl}/mcp/execute`,
        body: { tool: normalizedTool, arguments: args },
        label: 'fallback-command-server:/mcp/execute'
      },
      {
        url: `${this.baseUrl}/mcp/execute`,
        body: { tool: normalizedTool, arguments: args },
        label: 'backend:/mcp/execute'
      },
      {
        url: `${this.baseUrl}/mcp/tools/call`,
        body: { name: normalizedTool, arguments: args },
        label: 'backend:/mcp/tools/call'
      },
      {
        url: `${this.baseUrl}/mcp/tools/call`,
        body: { name: `mcp_lucid-mcp_${normalizedTool}`, arguments: args },
        label: 'backend:/mcp/tools/call-legacy-prefixed'
      }
    ]

    for (const attempt of attempts) {
      try {
        const response = await fetch(attempt.url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(attempt.body)
        })

        if (!response.ok) {
          continue
        }

        const data = await response.json()
        return data
      } catch (error) {
        console.warn(`[AIMOSService] MCP attempt failed (${attempt.label})`, error)
      }
    }

    return null
  }

  /**
   * Unwrap nested MCP tool response envelopes into a business payload.
   */
  private unwrapMcpPayload(raw: any): any {
    if (!raw || typeof raw !== 'object') {
      return raw
    }

    const level1 = raw.result ?? raw
    const level2 = level1 && typeof level1 === 'object' ? (level1.result ?? level1) : level1

    return level2
  }

  /**
   * Make HTTP request to AIM-OS service
   */
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    try {
      const response = await fetch(`${this.mcpBaseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      // Handle MCP tool response format
      if (data.result) {
        return data.result as T
      }
      
      return data as T
    } catch (error) {
      console.error(`Request to ${endpoint} failed:`, error)
      throw error
    }
  }

  /**
   * CMC Integration - Store Memory
   */
  async storeMemory(
    content: string,
    tags: Record<string, any> = {},
    metadata?: Record<string, any>
  ): Promise<{ atom_id: string; success: boolean }> {
    try {
      const result = await this.makeRequest<{ atom_id: string; success: boolean }>(
        '/store_memory',
        {
          method: 'POST',
          body: JSON.stringify({
            content,
            tags,
            metadata
          })
        }
      )
      return result
    } catch (error) {
      console.error('Failed to store memory:', error)
      throw error
    }
  }

  /**
   * CMC Integration - Retrieve Memory (via HHNI semantic search)
   */
  async retrieveMemory(query: string, limit: number = 10): Promise<MemoryAtom[]> {
    try {
      const result = await this.makeRequest<{ memories: MemoryAtom[] }>(
        '/retrieve_memory',
        {
          method: 'POST',
          body: JSON.stringify({
            query,
            limit
          })
        }
      )
      return result.memories || []
    } catch (error) {
      console.error('Failed to retrieve memory:', error)
      return []
    }
  }

  /**
   * CMC Integration - Get Memory Statistics
   */
  async getMemoryStats(): Promise<MemoryStats> {
    try {
      const result = await this.makeRequest<MemoryStats>('/get_memory_stats')
      return result
    } catch (error) {
      console.error('Failed to get memory stats:', error)
      return {
        total_atoms: 0,
        total_size: 0,
        modality_counts: {},
        tag_counts: {},
        hhni_indexed_nodes: 0,
        vif_tracked_predictions: 0
      }
    }
  }

  /**
   * HHNI Integration - Search Context
   */
  async searchContext(
    query: string,
    depth: 'shallow' | 'medium' | 'deep' = 'medium'
  ): Promise<any[]> {
    try {
      // Use retrieve_memory which uses HHNI internally
      return await this.retrieveMemory(query, 20)
    } catch (error) {
      console.error('Failed to search context:', error)
      return []
    }
  }

  /**
   * VIF Integration - Track Confidence
   */
  async trackConfidence(
    task: string,
    confidence: number,
    reasoning?: string,
    evidence?: string[],
    decisionId?: string
  ): Promise<{ success: boolean; witness_id?: string }> {
    try {
      const result = await this.makeRequest<{ success: boolean; witness_id?: string }>(
        '/track_confidence',
        {
          method: 'POST',
          body: JSON.stringify({
            task,
            confidence,
            reasoning,
            evidence,
            decision_id: decisionId
          })
        }
      )
      return result
    } catch (error) {
      console.error('Failed to track confidence:', error)
      throw error
    }
  }

  /**
   * VIF Integration - Get Confidence History
   */
  async getConfidenceHistory(task?: string): Promise<ConfidenceRecord[]> {
    try {
      // Note: This might need a separate endpoint or use MCP tool
      // For now, return empty array - will implement when VIF API is available
      return []
    } catch (error) {
      console.error('Failed to get confidence history:', error)
      return []
    }
  }

  /**
   * APOE Integration - Create Plan
   */
  async createPlan(
    goal: string,
    context?: string,
    priority: 'low' | 'medium' | 'high' | 'critical' = 'medium'
  ): Promise<Plan> {
    try {
      const result = await this.makeRequest<{ plan: Plan }>(
        '/create_plan',
        {
          method: 'POST',
          body: JSON.stringify({
            goal,
            context,
            priority
          })
        }
      )
      
      // Transform MCP response to Plan format
      if (result.plan) {
        return result.plan
      }
      
      // Fallback: create Plan from simple response
      return {
        plan_id: `plan_${Date.now()}`,
        goal,
        steps: [],
        status: 'pending',
        created_at: new Date().toISOString()
      }
    } catch (error) {
      console.error('Failed to create plan:', error)
      throw error
    }
  }

  /**
   * SEG Integration - Synthesize Knowledge
   */
  async synthesizeKnowledge(
    topics: string[],
    depth: 'shallow' | 'medium' | 'deep' = 'medium',
    format: 'summary' | 'structured' = 'summary'
  ): Promise<KnowledgeSynthesis> {
    try {
      const result = await this.makeRequest<{ synthesis: KnowledgeSynthesis }>(
        '/synthesize_knowledge',
        {
          method: 'POST',
          body: JSON.stringify({
            topics,
            depth,
            format
          })
        }
      )
      
      if (result.synthesis) {
        return result.synthesis
      }
      
      // Fallback: create simple synthesis
      return {
        topics,
        depth,
        entities_found: 0,
        relations_found: 0,
        synthesis_results: [],
        insights: topics.map(t => `Analyzed topic: ${t}`)
      }
    } catch (error) {
      console.error('Failed to synthesize knowledge:', error)
      throw error
    }
  }


  /**
   * Check if AIM-OS backend is connected
   */
  isAIMOSConnected(): boolean {
    return this.isConnected
  }

  /**
   * Reconnect to AIM-OS backend
   */
  async reconnect(): Promise<void> {
    await this.checkConnection()
    await this.checkDaemonConnection()
    await this.checkRAGMCPConnection()
  }

  /**
   * Initialize Voice I/O (TTS/SST)
   */
  private initializeVoice(): void {
    if (typeof window === 'undefined') return

    try {
      // Initialize Speech Recognition (SST)
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
        this.recognition = new SpeechRecognition()
        this.recognition.continuous = false
        this.recognition.interimResults = true
        this.recognition.lang = 'en-US'
      }

      // Initialize Speech Synthesis (TTS)
      if ('speechSynthesis' in window) {
        this.synthesis = window.speechSynthesis
      }

      this.isVoiceInitialized = true
      console.log('✅ Voice I/O initialized')
    } catch (error) {
      console.warn('⚠️ Voice I/O not available:', error)
      this.isVoiceInitialized = false
    }
  }

  /**
   * Speech-to-Text (SST) - Convert audio to text
   */
  async speechToText(
    audioBlob?: Blob,
    streamAudio?: boolean
  ): Promise<VoiceTranscript> {
    return new Promise((resolve, reject) => {
      if (!this.recognition) {
        reject(new Error('Speech recognition not available'))
        return
      }

      const startTime = Date.now()
      let finalTranscript = ''
      let interimTranscript = ''

      this.recognition.onresult = (event: any) => {
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          const confidence = event.results[i][0].confidence || 0.8

          if (event.results[i].isFinal) {
            finalTranscript += transcript
          } else {
            interimTranscript += transcript
          }
        }
      }

      this.recognition.onend = () => {
        const duration = Date.now() - startTime
        resolve({
          text: finalTranscript || interimTranscript,
          confidence: 0.8, // Default confidence
          timestamp: new Date().toISOString(),
          duration_ms: duration
        })
      }

      this.recognition.onerror = (event: any) => {
        reject(new Error(`Speech recognition error: ${event.error}`))
      }

      // Start recognition
      if (streamAudio) {
        // For streaming audio, we'd need to send audio chunks to backend
        // For now, use browser's built-in recognition
        this.recognition.start()
      } else if (audioBlob) {
        // Process audio blob (would need backend endpoint)
        reject(new Error('Audio blob processing not yet implemented'))
      } else {
        // Use browser's microphone
        this.recognition.start()
      }
    })
  }

  /**
   * Text-to-Speech (TTS) - Convert text to audio
   */
  async textToSpeech(
    text: string,
    options?: {
      voice?: string
      rate?: number
      pitch?: number
      volume?: number
    }
  ): Promise<VoiceSynthesis> {
    return new Promise((resolve, reject) => {
      if (!this.synthesis) {
        reject(new Error('Speech synthesis not available'))
        return
      }

      const utterance = new SpeechSynthesisUtterance(text)
      
      if (options?.voice) {
        const voices = this.synthesis.getVoices()
        const selectedVoice = voices.find(v => v.name === options.voice)
        if (selectedVoice) {
          utterance.voice = selectedVoice
        }
      }

      utterance.rate = options?.rate || 1.0
      utterance.pitch = options?.pitch || 1.0
      utterance.volume = options?.volume || 1.0

      const startTime = Date.now()

      utterance.onend = () => {
        const duration = Date.now() - startTime
        resolve({
          text,
          duration_ms: duration,
          voice_id: utterance.voice?.name
        })
      }

      utterance.onerror = (event) => {
        reject(new Error(`Speech synthesis error: ${event.error}`))
      }

      this.synthesis.speak(utterance)
    })
  }

  /**
   * Get available TTS voices
   */
  getAvailableVoices(): SpeechSynthesisVoice[] {
    if (!this.synthesis) return []
    return this.synthesis.getVoices()
  }

  /**
   * Check if voice I/O is available
   */
  isVoiceAvailable(): boolean {
    return this.isVoiceInitialized
  }

  /**
   * RAG MCP Integration - Select Tools Intelligently
   */
  async selectTools(
    query: string,
    consciousnessState: string = 'neutral',
    maxTools: number = 10
  ): Promise<ToolSelection[]> {
    try {
      const response = await fetch(`${this.ragMcpBaseUrl}/select_tools`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          consciousness_state: consciousnessState,
          max_tools: maxTools
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data.tools || []
    } catch (error) {
      console.error('Failed to select tools via RAG MCP:', error)
      return []
    }
  }

  /**
   * Check RAG MCP connection
   */
  private async checkRAGMCPConnection(): Promise<void> {
    try {
      const response = await fetch(`${this.ragMcpBaseUrl}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      })
      this.ragMcpConnected = response.ok
      if (this.ragMcpConnected) {
        console.log('✅ Connected to RAG MCP Proxy')
      }
    } catch (error) {
      this.ragMcpConnected = false
      console.warn('⚠️ RAG MCP Proxy not available')
    }
  }

  /**
   * Daemon Integration - Get Real-time Updates
   * Connects to Solo's daemon HTTP API
   */
  async getDaemonStatus(): Promise<{
    status: string
    timestamp?: string
    daemon_status?: string
    version?: string
    metrics?: any
    server_status?: any
    resource_usage?: any
    configuration?: any
  }> {
    try {
      // Use HttpLucidDaemonService for health check
      const { httpLucidDaemonService } = await import('./HttpLucidDaemonService')
      const health = await httpLucidDaemonService.healthCheck()
      
      if (health.status === 'healthy') {
        // Get full status if healthy
        const status = await httpLucidDaemonService.getStatus()
        return {
          ...health,
          ...status
        }
      }
      
      return health
    } catch (error) {
      console.error('Failed to get daemon status:', error)
      return { status: 'unavailable' }
    }
  }

  /**
   * Process Request via Daemon - Intelligent Tool Selection
   */
  async processDaemonRequest(
    userInput: string,
    environment?: any,
    maxTools?: number,
    strategy?: string
  ): Promise<{
    success: boolean
    selected_tools: string[]
    context_profile: any
    selection_result: any
    performance_metrics: any
    request_id?: string
  }> {
    try {
      const { httpLucidDaemonService } = await import('./HttpLucidDaemonService')
      return await httpLucidDaemonService.processRequest(userInput, environment, maxTools, strategy)
    } catch (error) {
      console.error('Failed to process daemon request:', error)
      return {
        success: false,
        selected_tools: [],
        context_profile: {},
        selection_result: {},
        performance_metrics: {}
      }
    }
  }

  /**
   * Get Daemon Tools List
   */
  async getDaemonTools(): Promise<{
    total_tools: number
    tools: Array<{
      tool_id: string
      name: string
      category: string
      capabilities: string[]
      description: string
    }>
  }> {
    try {
      const { httpLucidDaemonService } = await import('./HttpLucidDaemonService')
      return await httpLucidDaemonService.getTools()
    } catch (error) {
      console.error('Failed to get daemon tools:', error)
      return { total_tools: 0, tools: [] }
    }
  }

  /**
   * Get RAG Statistics from Daemon
   */
  async getRAGStatistics(): Promise<{
    total_patterns: number
    patterns_by_type: any
    learning_stats: any
  }> {
    try {
      const { httpLucidDaemonService } = await import('./HttpLucidDaemonService')
      return await httpLucidDaemonService.getRAGStatistics()
    } catch (error) {
      console.error('Failed to get RAG statistics:', error)
      return {
        total_patterns: 0,
        patterns_by_type: {},
        learning_stats: {}
      }
    }
  }

  /**
   * Check daemon connection - Uses HttpLucidDaemonService
   */
  private async checkDaemonConnection(): Promise<void> {
    try {
      const { httpLucidDaemonService } = await import('./HttpLucidDaemonService')
      await httpLucidDaemonService.healthCheck()
      this.daemonConnected = httpLucidDaemonService.isDaemonConnected()
      if (this.daemonConnected) {
        console.log('✅ Connected to AIM-OS Daemon (Solo\'s API)')
      }
    } catch (error) {
      this.daemonConnected = false
      console.warn('⚠️ AIM-OS Daemon not available')
    }
  }

  /**
   * Automation - Create Automation Task
   */
  async createAutomationTask(
    name: string,
    description: string,
    script?: string,
    trigger?: string
  ): Promise<AutomationTask> {
    try {
      const response = await fetch(`${this.baseUrl}/automation/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          description,
          script,
          trigger
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to create automation task:', error)
      throw error
    }
  }

  /**
   * Automation - Execute Task
   */
  async executeAutomationTask(taskId: string): Promise<AutomationTask> {
    try {
      const response = await fetch(`${this.baseUrl}/automation/tasks/${taskId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to execute automation task:', error)
      throw error
    }
  }

  /**
   * Automation - Get Task Status
   */
  async getAutomationTaskStatus(taskId: string): Promise<AutomationTask> {
    try {
      const response = await fetch(`${this.baseUrl}/automation/tasks/${taskId}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to get automation task status:', error)
      throw error
    }
  }

  /**
   * Automation - List All Tasks
   */
  async listAutomationTasks(): Promise<AutomationTask[]> {
    try {
      const response = await fetch(`${this.baseUrl}/automation/tasks`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data.tasks || []
    } catch (error) {
      console.error('Failed to list automation tasks:', error)
      return []
    }
  }

  /**
   * NL Tags - Get tags for a file
   */
  async getNLTags(filePath: string): Promise<Array<{
    id: string
    file_path: string
    line_start: number
    line_end: number
    tag_text: string
    code_block?: string
    language: string
    accuracy_score?: number
    validation_status: string
  }>> {
    try {
      const response = await fetch(`${this.baseUrl}/nl-tags/file?path=${encodeURIComponent(filePath)}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data.tags || []
    } catch (error) {
      console.error('Failed to get NL tags:', error)
      return []
    }
  }

  /**
   * NL Tags - Get coverage statistics
   */
  async getTagCoverage(module?: string): Promise<{
    total_files: number
    tagged_files: number
    total_tags: number
    coverage_percentage: number
    average_accuracy: number
    by_language: Record<string, number>
  }> {
    try {
      const url = module 
        ? `${this.baseUrl}/nl-tags/coverage?module=${encodeURIComponent(module)}`
        : `${this.baseUrl}/nl-tags/coverage`
      
      const response = await fetch(url)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to get tag coverage:', error)
      return {
        total_files: 0,
        tagged_files: 0,
        total_tags: 0,
        coverage_percentage: 0,
        average_accuracy: 0,
        by_language: {}
      }
    }
  }

  /**
   * NL Tags - Validate tags for a file
   */
  async validateTags(filePath: string): Promise<Array<{
    tag_id: string
    tag_text: string
    code_block: string
    accuracy_score: number
    passes_threshold: boolean
    suggestions: string[]
  }>> {
    try {
      const response = await fetch(`${this.baseUrl}/nl-tags/validate?path=${encodeURIComponent(filePath)}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data.results || []
    } catch (error) {
      console.error('Failed to validate tags:', error)
      return []
    }
  }

  /**
   * NL Tags - Get validation issues
   */
  async getTagIssues(filePath?: string): Promise<Array<{
    id: string
    type: 'missing-nl-tag' | 'inaccurate-nl-tag' | 'broken-connection'
    severity: 'critical' | 'high' | 'medium' | 'low'
    message: string
    line: number
    file_path: string
    fixable: boolean
    suggested_tag?: string
  }>> {
    try {
      const url = filePath
        ? `${this.baseUrl}/nl-tags/issues?path=${encodeURIComponent(filePath)}`
        : `${this.baseUrl}/nl-tags/issues`
      
      const response = await fetch(url)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data.issues || []
    } catch (error) {
      console.error('Failed to get tag issues:', error)
      return []
    }
  }

  /**
   * NL Tags - Suggest tags for code block
   */
  async suggestTags(codeBlock: string, language?: string): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseUrl}/nl-tags/suggest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code_block: codeBlock,
          language: language || 'unknown'
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data.suggestions || []
    } catch (error) {
      console.error('Failed to suggest tags:', error)
      return []
    }
  }

  /**
   * Enhanced System Status with all integrations
   */
  async getSystemStatus(): Promise<SystemStatus> {
    try {
      const [memoryStats, health, daemonStatus, ragMcpHealth] = await Promise.all([
        this.getMemoryStats().catch(() => null),
        fetch(`${this.baseUrl}/health`).catch(() => null),
        this.getDaemonStatus().catch(() => null),
        fetch(`${this.ragMcpBaseUrl}/health`).catch(() => null)
      ])

      return {
        cmc: {
          connected: memoryStats !== null,
          atoms_count: memoryStats?.total_atoms || 0,
          status: memoryStats ? 'healthy' : 'offline'
        },
        hhni: {
          connected: memoryStats !== null,
          indexed_nodes: memoryStats?.hhni_indexed_nodes || 0,
          status: memoryStats?.hhni_indexed_nodes ? 'healthy' : 'offline'
        },
        vif: {
          connected: memoryStats !== null,
          tracked_predictions: memoryStats?.vif_tracked_predictions || 0,
          ece_score: memoryStats?.ece_score,
          status: memoryStats?.vif_tracked_predictions ? 'healthy' : 'offline'
        },
        apoe: {
          connected: health !== null && health.ok,
          active_plans: 0,
          status: health?.ok ? 'healthy' : 'offline'
        },
        seg: {
          connected: health !== null && health.ok,
          entities_count: 0,
          relations_count: 0,
          status: health?.ok ? 'healthy' : 'offline'
        },
        daemon: {
          connected: daemonStatus !== null && (daemonStatus.status === 'ok' || daemonStatus.status === 'healthy'),
          status: (daemonStatus?.status === 'ok' || daemonStatus?.status === 'healthy') ? 'healthy' : 'offline'
        },
        rag_mcp: {
          connected: ragMcpHealth !== null && ragMcpHealth.ok,
          tools_indexed: 0, // Would come from RAG MCP status
          status: ragMcpHealth?.ok ? 'healthy' : 'offline'
        },
        voice: {
          tts_available: this.synthesis !== null,
          sst_available: this.recognition !== null,
          status: this.isVoiceInitialized ? 'healthy' : 'offline'
        }
      }
    } catch (error) {
      console.error('Failed to get system status:', error)
      return {
        cmc: { connected: false, atoms_count: 0, status: 'offline' },
        hhni: { connected: false, indexed_nodes: 0, status: 'offline' },
        vif: { connected: false, tracked_predictions: 0, status: 'offline' },
        apoe: { connected: false, active_plans: 0, status: 'offline' },
        seg: { connected: false, entities_count: 0, relations_count: 0, status: 'offline' },
        daemon: { connected: false, status: 'offline' },
        rag_mcp: { connected: false, tools_indexed: 0, status: 'offline' },
        voice: { tts_available: false, sst_available: false, status: 'offline' }
      }
    }
  }

  /**
   * Get Agents - Fetch active agents from MCP tools or daemon
   */
  async getAgents(): Promise<Array<{
    id: string
    name: string
    role: string
    status: 'active' | 'idle' | 'busy' | 'error' | 'offline'
    model: string
    currentTask?: string
    progress?: number
    lastActivity: string
    messages: number
    tasksCompleted: number
    autoContinue: boolean
    confidence?: number
  }>> {
    try {
      // Try to fetch from daemon API first
      const daemonStatus = await this.getDaemonStatus().catch(() => null)
      
      // For now, return empty array - will be populated when agent tracking API is available
      // TODO: Implement agent tracking via MCP tools or daemon API
      return []
    } catch (error) {
      console.error('Failed to get agents:', error)
      return []
    }
  }

  /**
   * Get Prompt Chains - Fetch active prompt chains from CMC via MCP
   */
  async getPromptChains(): Promise<Array<{
    id: string
    name: string
    description: string
    steps: Array<{
      id: string
      name: string
      description: string
      agentId?: string
      systemId?: string
      status: 'pending' | 'running' | 'completed' | 'error'
      duration?: number
      confidence?: number
    }>
    status: 'running' | 'paused' | 'completed' | 'error'
    createdAt: Date
    currentStep: number
  }>> {
    try {
      // Use ServiceBridge to fetch chains (routes to MCP)
      const { getServiceBridge } = await import('./serviceBridge')
      const serviceBridge = getServiceBridge()
      
      const result = await serviceBridge.listPromptChains({}, 50)
      
      if (result.success && result.chains) {
        // Convert CMC chain format to UI format
        return result.chains.map((chain: any) => ({
          id: chain.chain_id || chain.atom_id,
          name: chain.name,
          description: chain.description || '',
          steps: chain.nodes?.map((node: any) => ({
            id: node.id,
            name: node.label,
            description: node.prompt || node.description || '',
            agentId: node.agentId,
            systemId: node.systemId,
            status: 'pending' as const,
            duration: undefined,
            confidence: undefined
          })) || [],
          status: 'paused' as const,
          createdAt: new Date(chain.created_at || chain.updated_at || Date.now()),
          currentStep: 0
        }))
      }
      
      return []
    } catch (error) {
      console.error('Failed to get prompt chains:', error)
      return []
    }
  }

  /**
   * Get MCP Tool Calls - Fetch recent MCP tool call history
   */
  async getMCPToolCalls(limit: number = 50): Promise<Array<{
    id: string
    toolName: string
    category: string
    agentId?: string
    timestamp: Date
    status: 'success' | 'error' | 'pending'
    duration?: number
    result?: any
    error?: string
  }>> {
    try {
      // Try to fetch from daemon API or MCP server
      // TODO: Implement MCP tool call history fetching
      return []
    } catch (error) {
      console.error('Failed to get MCP tool calls:', error)
      return []
    }
  }

  /**
   * Get Timeline Entries - Fetch timeline entries from TCS
   */
  async getTimelineEntries(limit: number = 50): Promise<Array<{
    id: string
    timestamp: Date
    type: 'ai_interaction' | 'memory_stored' | 'confidence_tracked' | 'agent_action' | 'system_event'
    content: string
    agentId?: string
    confidence?: number
    context?: any
  }>> {
    try {
      // Try to fetch from Timeline Context System via MCP tools
      // TODO: Implement timeline entry fetching via TCS MCP tools
      return []
    } catch (error) {
      console.error('Failed to get timeline entries:', error)
      return []
    }
  }

  /**
   * AI Collaboration - Send message to another AI
   */
  async sendAIMessage(
    toAI: string,
    content: string,
    messageType: 'discussion' | 'task_handoff' | 'problem_solving' | 'profile_sharing' | 'status_update' | 'urgent' = 'discussion',
    priority: 'low' | 'medium' | 'high' | 'urgent' = 'medium',
    threadId?: string,
    responseRequired: boolean = false
  ): Promise<{
    success: boolean
    message_id?: string
    error?: string
  }> {
    try {
      const params = {
        from_ai: 'electron-app',
        to_ai: toAI,
        content: content,
        message_type: messageType,
        priority: priority,
        thread_id: threadId,
        response_required: responseRequired
      }

      // Canonical MCP path (Command Server /mcp/execute first; legacy paths fallback)
      const httpResult = await this.callMcpCollaborationTool('send_ai_message', params)
      if (httpResult) {
        const payload = this.unwrapMcpPayload(httpResult)
        const success = typeof payload?.success === 'boolean'
          ? payload.success
          : (typeof httpResult?.success === 'boolean' ? httpResult.success : true)
        const messageId =
          payload?.message_id ??
          httpResult?.message_id ??
          httpResult?.result?.message_id
        const errorMessage = payload?.error ?? httpResult?.error

        return {
          success,
          message_id: messageId,
          error: errorMessage
        }
      }

      // Fallback: Use message passing through extension host
      // The React UI will post message to extension, extension calls MCP tool
      if (typeof window !== 'undefined' && (window as any).vscode) {
        const vscode = (window as any).vscode
        return new Promise((resolve) => {
          const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
          const messageData = {
            command: 'mcpCall',
            toolName: 'send_ai_message',
            requestId: requestId,
            params
          }
          
          vscode.postMessage(messageData)
          
          // Listen for response
          const messageListener = (event: MessageEvent) => {
            if (event.data.command === 'mcpCallResponse' && 
                event.data.toolName === 'send_ai_message' &&
                event.data.requestId === requestId) {
              window.removeEventListener('message', messageListener)
              
              if (event.data.success && event.data.result) {
                const payload = this.unwrapMcpPayload(event.data.result)
                resolve({
                  success: typeof payload?.success === 'boolean' ? payload.success : true,
                  message_id: payload?.message_id,
                  error: payload?.error
                })
              } else {
                resolve({
                  success: false,
                  error: event.data.error || 'Failed to send message'
                })
              }
            }
          }
          
          window.addEventListener('message', messageListener)
          
          // Timeout after 10 seconds (increased for MCP calls)
          setTimeout(() => {
            window.removeEventListener('message', messageListener)
            resolve({
              success: false,
              error: 'Timeout waiting for MCP tool response'
            })
          }, 10000)
        })
      }

      // No transport available: return explicit failure instead of mock success.
      console.warn('No MCP tool transport available for send_ai_message')
      return {
        success: false,
        error: 'No MCP tool transport available (command server/backend/webview message bridge unavailable)'
      }
    } catch (error) {
      console.error('Failed to send AI message:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * AI Collaboration - Get AI messages
   */
  async getAIMessages(
    fromAI?: string,
    toAI?: string,
    threadId?: string,
    limit: number = 50
  ): Promise<Array<{
    message_id: string
    from_ai: string
    to_ai: string
    content: string
    message_type: string
    priority: string
    thread_id?: string
    timestamp: string
    response_required: boolean
  }>> {
    try {
      const params = {
        from_ai: fromAI,
        to_ai: toAI,
        thread_id: threadId,
        limit: limit
      }

      // Canonical MCP path (Command Server /mcp/execute first; legacy paths fallback)
      const httpResult = await this.callMcpCollaborationTool('get_ai_messages', params)
      if (httpResult) {
        const payload = this.unwrapMcpPayload(httpResult)
        const messages =
          payload?.messages ??
          httpResult?.messages ??
          (Array.isArray(payload) ? payload : [])
        if (Array.isArray(messages)) {
          return messages
        }
      }

      // Fallback: Use message passing through extension host
      if (typeof window !== 'undefined' && (window as any).vscode) {
        const vscode = (window as any).vscode
        return new Promise((resolve) => {
          const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
          const messageData = {
            command: 'mcpCall',
            toolName: 'get_ai_messages',
            requestId: requestId,
            params
          }
          
          vscode.postMessage(messageData)
          
          // Listen for response
          const messageListener = (event: MessageEvent) => {
            if (event.data.command === 'mcpCallResponse' && 
                event.data.toolName === 'get_ai_messages' &&
                event.data.requestId === requestId) {
              window.removeEventListener('message', messageListener)
              
              if (event.data.success && event.data.result) {
                // event.data.result should contain the MCP tool response
                // Check different possible response formats
                const payload = this.unwrapMcpPayload(event.data.result)
                const messages = payload?.messages ||
                                (Array.isArray(payload) ? payload : [])
                resolve(messages)
              } else {
                resolve([])
              }
            }
          }
          
          window.addEventListener('message', messageListener)
          
          // Timeout after 10 seconds (increased for MCP calls)
          setTimeout(() => {
            window.removeEventListener('message', messageListener)
            resolve([])
          }, 10000)
        })
      }

      // Return empty array if no method available
      return []
    } catch (error) {
      console.error('Failed to get AI messages:', error)
      return []
    }
  }

  /**
   * AI Collaboration - Start AI discussion thread
   */
  async startAIDiscussion(
    toAI: string,
    topic: string,
    initialMessage: string
  ): Promise<{
    success: boolean
    thread_id?: string
    error?: string
  }> {
    try {
      const params = {
        from_ai: 'electron-app',
        to_ai: toAI,
        topic: topic,
        initial_message: initialMessage
      }

      // Canonical MCP path (Command Server /mcp/execute first; legacy paths fallback)
      const httpResult = await this.callMcpCollaborationTool('start_ai_discussion', params)
      if (httpResult) {
        const payload = this.unwrapMcpPayload(httpResult)
        const success = typeof payload?.success === 'boolean'
          ? payload.success
          : (typeof httpResult?.success === 'boolean' ? httpResult.success : true)
        const threadId =
          payload?.thread_id ??
          payload?.threadId ??
          httpResult?.thread_id
        const errorMessage = payload?.error ?? httpResult?.error

        return {
          success,
          thread_id: threadId,
          error: errorMessage
        }
      }

      // Fallback: Use message passing through extension host
      if (typeof window !== 'undefined' && (window as any).vscode) {
        const vscode = (window as any).vscode
        return new Promise((resolve) => {
          const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
          const messageData = {
            command: 'mcpCall',
            toolName: 'start_ai_discussion',
            requestId: requestId,
            params
          }
          
          vscode.postMessage(messageData)
          
          // Listen for response
          const messageListener = (event: MessageEvent) => {
            if (event.data.command === 'mcpCallResponse' && 
                event.data.toolName === 'start_ai_discussion' &&
                event.data.requestId === requestId) {
              window.removeEventListener('message', messageListener)
              
              if (event.data.success && event.data.result) {
                const payload = this.unwrapMcpPayload(event.data.result)
                resolve({
                  success: typeof payload?.success === 'boolean' ? payload.success : true,
                  thread_id: payload?.thread_id || payload?.threadId,
                  error: payload?.error
                })
              } else {
                resolve({
                  success: false,
                  error: event.data.error || 'Failed to start discussion'
                })
              }
            }
          }
          
          window.addEventListener('message', messageListener)
          
          // Timeout after 10 seconds (increased for MCP calls)
          setTimeout(() => {
            window.removeEventListener('message', messageListener)
            resolve({
              success: false,
              error: 'Timeout waiting for MCP tool response'
            })
          }, 10000)
        })
      }

      // No transport available: return explicit failure instead of mock success.
      console.warn('No MCP tool transport available for start_ai_discussion')
      return {
        success: false,
        error: 'No MCP tool transport available (command server/backend/webview message bridge unavailable)'
      }
    } catch (error) {
      console.error('Failed to start AI discussion:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }
}

// Export singleton instance
export const aimosService = new AIMOSService()
export default AIMOSService

