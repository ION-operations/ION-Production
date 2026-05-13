// Shared types for AI Chat System
// Prevents circular dependencies between AIChatManagement and AIChatContext

export interface WorkReference {
  files?: Array<{
    path: string
    operation: 'created' | 'modified' | 'deleted'
    lines?: number[]
    commit_hash?: string
  }>
  cmc_atoms?: string[]
  vif_witnesses?: string[]
  goals?: string[]
  timeline_entries?: string[]
  git_commits?: string[]
}

export interface EvidenceTrail {
  cmc_atom_id?: string
  vif_witness_id?: string
  supporting_files?: Array<{
    path: string
    lines: number[]
    relevance: number
  }>
}

export interface GoalAlignment {
  objective?: string
  key_result?: string
  progress?: number
}

export interface ToolCall {
  id: string
  tool_name: string
  arguments: Record<string, any>
  result?: any
  status: 'success' | 'error' | 'pending'
  duration_ms?: number
  timestamp: Date
}

export interface PingContext {
  from_channel: string
  reason: string
  connected_at: Date
}

export interface ChatMessage {
  id: string
  timestamp: Date
  role: 'user' | 'assistant' | 'system'
  content: string
  agent?: string
  agent_id?: string
  confidence?: number
  work_references?: WorkReference
  evidence_trail?: EvidenceTrail
  goal_alignment?: GoalAlignment
  tool_calls?: ToolCall[]
  connected_channel?: string
  multi_selected_channel?: string  // Channel this message came from (for multi-selected channels)
  context_summary?: string  // Context summary dumped every prompt
  ping_context?: PingContext
  // Enhancement: Summary Atom (optional for backward compatibility)
  summary_atom?: import('../utils/summaryAtoms').SummaryAtom
  context_info?: import('../utils/summaryAtoms').MessageContextInfo
  override?: import('../utils/summaryAtoms').ContextOverride
}

