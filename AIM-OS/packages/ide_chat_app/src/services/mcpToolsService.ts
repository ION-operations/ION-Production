// Enhanced MCP Tools Service
// Comprehensive integration for all 59 MCP tools
// V2 Enhancement - Week 1 Foundation

import { getMCPAPI, MCPAPI } from './mcpApi'

export interface MCPToolMetadata {
  name: string
  description: string
  category: 'core' | 'scor' | 'snapshot' | 'timeline' | 'goal' | 'intuition' | 'co-agency' | 'dataset' | 'application' | 'autonomous' | 'ard' | 'ai-collab' | 'observability'
  quality?: number
  usageCount?: number
  lastUsed?: Date
  parameters?: any
}

export class MCPToolsService {
  private mcpApi: MCPAPI
  private toolRegistry: Map<string, MCPToolMetadata> = new Map()
  private usageTracking: Map<string, number> = new Map()

  constructor() {
    this.mcpApi = getMCPAPI()
    this.initializeToolRegistry()
  }

  /**
   * Initialize tool registry with all 59 MCP tools
   */
  private initializeToolRegistry(): void {
    // Core AIM-OS Tools (6)
    this.registerTool('store_memory', {
      name: 'store_memory',
      description: 'Store information in AIM-OS persistent memory',
      category: 'core'
    })
    this.registerTool('retrieve_memory', {
      name: 'retrieve_memory',
      description: 'Retrieve insights from HHNI',
      category: 'core'
    })
    this.registerTool('get_memory_stats', {
      name: 'get_memory_stats',
      description: 'Get AIM-OS statistics',
      category: 'core'
    })
    this.registerTool('create_plan', {
      name: 'create_plan',
      description: 'Create APOE execution plans',
      category: 'core'
    })
    this.registerTool('track_confidence', {
      name: 'track_confidence',
      description: 'Track VIF confidence',
      category: 'core'
    })
    this.registerTool('synthesize_knowledge', {
      name: 'synthesize_knowledge',
      description: 'Synthesize SEG knowledge',
      category: 'core'
    })

    // SCOR Tools (3)
    this.registerTool('check_invariant', {
      name: 'check_invariant',
      description: 'Check invariant rules',
      category: 'scor'
    })
    this.registerTool('run_baseline_probe', {
      name: 'run_baseline_probe',
      description: 'Detect consciousness drift',
      category: 'scor'
    })
    this.registerTool('detect_manipulation_signals', {
      name: 'detect_manipulation_signals',
      description: 'Detect social manipulation',
      category: 'scor'
    })

    // Snapshot Tools (4)
    this.registerTool('create_snapshot', {
      name: 'create_snapshot',
      description: 'Create file snapshots (CMC bitemporal)',
      category: 'snapshot'
    })
    this.registerTool('restore_snapshot', {
      name: 'restore_snapshot',
      description: 'Restore from snapshot',
      category: 'snapshot'
    })
    this.registerTool('list_snapshots', {
      name: 'list_snapshots',
      description: 'List available snapshots',
      category: 'snapshot'
    })
    this.registerTool('archive_snapshot', {
      name: 'archive_snapshot',
      description: 'Archive snapshots (never delete)',
      category: 'snapshot'
    })

    // Timeline Context Tools (3)
    this.registerTool('add_timeline_entry', {
      name: 'add_timeline_entry',
      description: 'Track context at each prompt (TCS)',
      category: 'timeline'
    })
    this.registerTool('get_timeline_summary', {
      name: 'get_timeline_summary',
      description: 'Get recent timeline entries (TCS)',
      category: 'timeline'
    })
    this.registerTool('get_timeline_entries', {
      name: 'get_timeline_entries',
      description: 'Query timeline history (TCS)',
      category: 'timeline'
    })

    // Goal Timeline Tools (3)
    this.registerTool('create_goal_timeline_node', {
      name: 'create_goal_timeline_node',
      description: 'Create goals as timeline planning nodes',
      category: 'goal'
    })
    this.registerTool('update_goal_progress', {
      name: 'update_goal_progress',
      description: 'Update goal progress and status',
      category: 'goal'
    })
    this.registerTool('query_goal_timeline', {
      name: 'query_goal_timeline',
      description: 'Query goals with filtering',
      category: 'goal'
    })

    // Intuitive Intelligence System Tools (3)
    this.registerTool('compute_intuition', {
      name: 'compute_intuition',
      description: 'Compute AI intuition score using IIS',
      category: 'intuition'
    })
    this.registerTool('update_intuition_weights', {
      name: 'update_intuition_weights',
      description: 'Update intuition weights from outcomes',
      category: 'intuition'
    })
    this.registerTool('get_intuition_trace', {
      name: 'get_intuition_trace',
      description: 'Get intuition trace history',
      category: 'intuition'
    })

    // Co-Agency & Trust Tools (3)
    this.registerTool('signal_disagreement', {
      name: 'signal_disagreement',
      description: 'Signal transparent disagreement with user',
      category: 'co-agency'
    })
    this.registerTool('get_trust_dashboard', {
      name: 'get_trust_dashboard',
      description: 'Get trust dashboard state',
      category: 'co-agency'
    })
    this.registerTool('request_escalation', {
      name: 'request_escalation',
      description: 'Request accountable escalation',
      category: 'co-agency'
    })

    // Dataset Management Tools (4)
    this.registerTool('create_dataset', {
      name: 'create_dataset',
      description: 'Create new dataset for AIM-OS',
      category: 'dataset'
    })
    this.registerTool('ingest_data', {
      name: 'ingest_data',
      description: 'Ingest data into AIM-OS dataset',
      category: 'dataset'
    })
    this.registerTool('query_dataset', {
      name: 'query_dataset',
      description: 'Query dataset contents',
      category: 'dataset'
    })
    this.registerTool('delete_dataset', {
      name: 'delete_dataset',
      description: 'Remove dataset (safe operation with snapshots)',
      category: 'dataset'
    })

    // Application Lifecycle Tools (3)
    this.registerTool('create_application', {
      name: 'create_application',
      description: 'Create new application',
      category: 'application'
    })
    this.registerTool('deploy_application', {
      name: 'deploy_application',
      description: 'Deploy application to environment',
      category: 'application'
    })
    this.registerTool('manage_application_lifecycle', {
      name: 'manage_application_lifecycle',
      description: 'Start/stop/monitor applications',
      category: 'application'
    })

    // Autonomous Protocol Tools (9)
    this.registerTool('start_autonomous_operation', {
      name: 'start_autonomous_operation',
      description: 'Start autonomous operation with safety checklist',
      category: 'autonomous'
    })
    this.registerTool('pause_autonomous_operation', {
      name: 'pause_autonomous_operation',
      description: 'Pause autonomous operation',
      category: 'autonomous'
    })
    this.registerTool('resume_autonomous_operation', {
      name: 'resume_autonomous_operation',
      description: 'Resume autonomous operation after pause',
      category: 'autonomous'
    })
    this.registerTool('stop_autonomous_operation', {
      name: 'stop_autonomous_operation',
      description: 'Stop autonomous operation completely',
      category: 'autonomous'
    })
    this.registerTool('get_autonomous_status', {
      name: 'get_autonomous_status',
      description: 'Get current status of autonomous operation',
      category: 'autonomous'
    })
    this.registerTool('run_autonomous_checklist', {
      name: 'run_autonomous_checklist',
      description: 'Run autonomous protocol checklist for safety validation',
      category: 'autonomous'
    })
    this.registerTool('fix_autonomous_issues', {
      name: 'fix_autonomous_issues',
      description: 'Attempt to fix issues found in autonomous operation',
      category: 'autonomous'
    })
    this.registerTool('should_continue_autonomous', {
      name: 'should_continue_autonomous',
      description: 'Check if autonomous operation should continue',
      category: 'autonomous'
    })
    this.registerTool('generate_next_autonomous_task', {
      name: 'generate_next_autonomous_task',
      description: 'Generate next task for autonomous operation',
      category: 'autonomous'
    })

    // Autonomous Research Dream Tools (3)
    this.registerTool('conduct_recursive_analysis', {
      name: 'conduct_recursive_analysis',
      description: 'Conduct recursive system analysis for consciousness self-improvement',
      category: 'ard'
    })
    this.registerTool('generate_improvement_dreams', {
      name: 'generate_improvement_dreams',
      description: 'Generate improvement dreams based on system analysis',
      category: 'ard'
    })
    this.registerTool('test_improvement_dream', {
      name: 'test_improvement_dream',
      description: 'Test improvement dream in safe environments',
      category: 'ard'
    })

    // AI Collaboration Tools (6)
    this.registerTool('send_ai_message', {
      name: 'send_ai_message',
      description: 'Send a message to another AI system',
      category: 'ai-collab'
    })
    this.registerTool('get_ai_messages', {
      name: 'get_ai_messages',
      description: 'Retrieve AI-to-AI messages',
      category: 'ai-collab'
    })
    this.registerTool('start_ai_discussion', {
      name: 'start_ai_discussion',
      description: 'Start a new discussion thread with another AI',
      category: 'ai-collab'
    })
    this.registerTool('handoff_task_to_ai', {
      name: 'handoff_task_to_ai',
      description: 'Hand off a task to another AI system',
      category: 'ai-collab'
    })
    this.registerTool('share_ai_profile', {
      name: 'share_ai_profile',
      description: 'Share AI profile and capabilities with another AI',
      category: 'ai-collab'
    })
    this.registerTool('get_ai_collaboration_summary', {
      name: 'get_ai_collaboration_summary',
      description: 'Get summary of AI collaboration activity',
      category: 'ai-collab'
    })

    // Observability Tools (4)
    this.registerTool('get_consciousness_metrics', {
      name: 'get_consciousness_metrics',
      description: 'Get consciousness observability metrics for the active MCP stack',
      category: 'observability'
    })
    // Note: get_autonomous_status, get_trust_dashboard, get_memory_stats already registered above
  }

  /**
   * Register a tool in the registry
   */
  private registerTool(name: string, metadata: MCPToolMetadata): void {
    this.toolRegistry.set(name, {
      ...metadata,
      usageCount: 0,
      lastUsed: undefined
    })
    this.usageTracking.set(name, 0)
  }

  /**
   * Execute an MCP tool with usage tracking
   */
  async executeTool(toolName: string, args: any = {}): Promise<any> {
    const tool = this.toolRegistry.get(toolName)
    if (!tool) {
      console.warn(`Tool ${toolName} not found in registry`)
      // Still try to execute via MCP API
    }

    // Track usage
    const currentCount = this.usageTracking.get(toolName) || 0
    this.usageTracking.set(toolName, currentCount + 1)
    
    if (tool) {
      tool.usageCount = (tool.usageCount || 0) + 1
      tool.lastUsed = new Date()
    }

    // Execute via MCP API
    return this.mcpApi.executeTool(toolName, args)
  }

  /**
   * Get all available tools
   */
  getAllTools(): MCPToolMetadata[] {
    return Array.from(this.toolRegistry.values())
  }

  /**
   * Get tools by category
   */
  getToolsByCategory(category: MCPToolMetadata['category']): MCPToolMetadata[] {
    return this.getAllTools().filter(tool => tool.category === category)
  }

  /**
   * Get tool metadata
   */
  getToolMetadata(toolName: string): MCPToolMetadata | undefined {
    return this.toolRegistry.get(toolName)
  }

  /**
   * Get tool usage statistics
   */
  getToolUsageStats(): Map<string, number> {
    return new Map(this.usageTracking)
  }

  /**
   * Get most used tools
   */
  getMostUsedTools(limit: number = 10): MCPToolMetadata[] {
    return this.getAllTools()
      .sort((a, b) => (b.usageCount || 0) - (a.usageCount || 0))
      .slice(0, limit)
  }

  /**
   * Search tools by name or description
   */
  searchTools(query: string): MCPToolMetadata[] {
    const lowerQuery = query.toLowerCase()
    return this.getAllTools().filter(tool =>
      tool.name.toLowerCase().includes(lowerQuery) ||
      tool.description.toLowerCase().includes(lowerQuery)
    )
  }
}

// Singleton instance
let mcpToolsServiceInstance: MCPToolsService | null = null

export function getMCPToolsService(): MCPToolsService {
  if (!mcpToolsServiceInstance) {
    mcpToolsServiceInstance = new MCPToolsService()
  }
  return mcpToolsServiceInstance
}

