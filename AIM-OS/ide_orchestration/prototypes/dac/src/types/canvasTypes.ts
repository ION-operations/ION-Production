// Canvas Document Types
// Living document system for evolving content

export interface CanvasSection {
  id: string
  type: 'text' | 'code' | 'image' | 'table' | 'math' | 'component' | 'chat-reference'
  content: any
  metadata: {
    createdBy: 'user' | 'ai' | 'chat'
    createdFrom?: string  // Chat message ID or other source
    editedBy: string[]
    confidence?: number
    evidence?: Evidence[]
    timestamp: Date
    version: number
  }
  editable: boolean
  aiSuggestions?: AISuggestion[]
  chatReferences?: string[]  // Related chat message IDs
}

export interface AISuggestion {
  id: string
  type: 'expand' | 'refine' | 'restructure' | 'summarize' | 'enhance'
  content: string
  confidence: number
  reasoning?: string
  timestamp: Date
}

export interface Evidence {
  id: string
  type: 'cmc_atom' | 'vif_witness' | 'file' | 'memory' | 'knowledge_graph'
  source: string
  relevance: number
  summary?: string
}

export interface CanvasVersion {
  id: string
  version: number
  timestamp: Date
  author: string
  changes: CanvasChange[]
  snapshot: CanvasDocument
}

export interface CanvasChange {
  type: 'add' | 'update' | 'delete' | 'reorder'
  sectionId: string
  oldContent?: any
  newContent?: any
  position?: number
}

export interface CanvasBranch {
  id: string
  name: string
  createdAt: Date
  createdBy: string
  baseVersion: number
  sections: CanvasSection[]
}

export interface MemoryReference {
  id: string
  type: 'cmc_atom' | 'summary_atom'
  atomId: string
  relevance: number
}

export interface KnowledgeNode {
  id: string
  label: string
  type: string
  connections: string[]
}

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

export interface CanvasDocument {
  id: string
  title: string
  content: CanvasSection[]
  metadata: {
    createdAt: Date
    updatedAt: Date
    version: number
    author: string
    createdFrom?: string  // Chat message ID that created this
    relatedMessages?: string[]  // Chat messages related to this canvas
    collaborators: string[]
    tags?: string[]
  }
  history: CanvasVersion[]
  branches: CanvasBranch[]
  aimos: {
    confidence: number
    evidence: Evidence[]
    memory: MemoryReference[]
    knowledgeGraph: KnowledgeNode[]
    workReferences?: WorkReference
    evidenceTrail?: EvidenceTrail
    goalAlignment?: GoalAlignment
  }
  chatIntegration: {
    relatedChannel?: string
    relatedMessages: string[]
    lastSyncedAt: Date
  }
}

// Canvas editing operations
export interface CanvasEditOperation {
  type: 'add_section' | 'update_section' | 'delete_section' | 'reorder_sections' | 'update_title'
  canvasId: string
  sectionId?: string
  data?: any
  position?: number
}

// Canvas AI enhancement request
export interface CanvasEnhancementRequest {
  canvasId: string
  sectionId: string
  enhancementType: 'expand' | 'refine' | 'restructure' | 'summarize' | 'enhance'
  context?: string
  userInstructions?: string
}

