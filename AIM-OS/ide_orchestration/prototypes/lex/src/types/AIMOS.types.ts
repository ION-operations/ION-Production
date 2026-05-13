// AIM-OS System Types
import { TimelineEntry } from './Panel.types'

export interface CMCStats {
  totalAtoms: number
  activeSessions: number
  storage: string
}

export interface HHNISearchResult {
  atomIds: string[]
  relevance: number[]
  query: string
}

export interface VIFConfidence {
  task: string
  confidence: number
  evidence: string[]
  reasoning: string
}

export interface APOEPlan {
  id: string
  goal: string
  tasks: APOETask[]
  status: 'planned' | 'in_progress' | 'completed'
}

export interface APOETask {
  id: string
  description: string
  status: 'pending' | 'in_progress' | 'completed'
  dependencies: string[]
}

export interface SEGKnowledge {
  topics: string[]
  nodes: SEGNode[]
  relationships: SEGRelationship[]
}

export interface SEGNode {
  id: string
  type: string
  content: string
  confidence: number
}

export interface SEGRelationship {
  source: string
  target: string
  type: string
  strength: number
}

export interface TCSContext {
  entries: TimelineEntry[]
  summary: string
  totalEntries: number
}

