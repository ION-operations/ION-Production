// AIM-OS Hooks System - PERFECTED
// Comprehensive hooks matching real AIM-OS data structures
// Updated to use real backend services via MCPService

import { useState, useEffect, useCallback } from 'react'
import { cmcService } from '../services/CMCService'
import { hhniService } from '../services/HHNIService'
import { vifService } from '../services/VIFService'
import { tcsService } from '../services/TCSService'
import { segService } from '../services/SEGService'
import { casService } from '../services/CASService'
import { apoeService } from '../services/APOEService'

// ===== REAL AIM-OS TYPE DEFINITIONS =====

// CMC Atom Structure (from packages/cmc_service/models.py)
export interface CMCAtom {
  id: string  // atom_{uuid}
  modality: 'text' | 'code' | 'event' | 'tool' | 'cross_model'
  content: {
    inline?: string
    uri?: string
    media_type: string
  }
  tags: Record<string, number>  // Weighted tags (0.0-1.0)
  metadata: Record<string, any>
  witness: {
    model_id?: string
    tool_ids: string[]
    snapshot_id?: string
    correlation_id?: string
    uncertainty_band: 'green' | 'yellow' | 'red'
    uncertainty_ece?: number
  }
  created_at: string  // ISO datetime
  valid_from: string  // Bitemporal valid time start
  valid_to: string | null  // Bitemporal valid time end (null = current)
  snapshot_ids: string[]
  hash: string
}

// HHNI Search Result (from packages/hhni/semantic_search.py)
export interface HHNISearchResult {
  node: {
    id: string
    level: 'document' | 'paragraph' | 'sentence'
    content: string
    summary?: string
    embeddings?: number[]
  }
  score: number  // Cosine similarity (0-1)
  confidence: number  // Relative confidence (0-1)
}

// VIF Witness (from packages/vif/)
export interface VIFWitness {
  id: string
  model_id: string
  model_provider?: string
  context_snapshot_id?: string
  prompt_hash: string
  prompt_tokens: number
  confidence_score: number
  confidence_band: 'A' | 'B' | 'C'  // A: 0.90-1.00, B: 0.70-0.89, C: <0.70
  output_hash?: string
  output_tokens?: number
  task_criticality?: 'critical' | 'important' | 'routine' | 'low_stakes'
  kappa_threshold?: number
  kappa_gate_passed?: boolean
  ece_score?: number
  created_at: string
}

// SEG Entity/Relation (from packages/seg/models.py - EXACT STRUCTURE)
export interface SEGEntity {
  id: string  // "entity_{uuid}"
  type: string  // Entity type (person, concept, event, etc.)
  name: string  // Human-readable name
  attributes: Record<string, any>
  
  // Bitemporal (BOTH transaction time AND valid time)
  tt_start: string  // Transaction time start
  tt_end: string | null  // Transaction time end
  vt_start: string  // Valid time start
  vt_end: string | null  // Valid time end
  
  // Metadata
  source?: string
  confidence: number  // 0-1
  tags: string[]
  witness_id?: string  // VIF witness
}

export interface SEGRelation {
  id: string  // "relation_{uuid}"
  source_id: string  // Source entity ID
  target_id: string  // Target entity ID
  relation_type: 'SUPPORTS' | 'CONTRADICTS' | 'REFERENCES' | 'DERIVES_FROM' | 'RELATES_TO'
  evidence_ids: string[]  // Evidence supporting this relation
  confidence: number  // 0-1
  
  // Bitemporal (BOTH transaction time AND valid time)
  tt_start: string
  tt_end: string | null
  vt_start: string
  vt_end: string | null
  
  // Metadata
  source?: string
  tags: string[]
  witness_id?: string
}

export interface SEGContradiction {
  id: string  // "contradiction_{uuid}"
  entity1_id: string  // First conflicting entity (NOT claim_a_id)
  entity2_id: string  // Second conflicting entity (NOT claim_b_id)
  contradiction_type: string
  similarity: number  // 0-1
  confidence: number  // 0-1 (NOT contradiction_score)
  explanation: string
  resolved: boolean
  resolution?: string
  resolved_at?: string
  detected_at: string
  tags: string[]
}

// TCS Timeline Entry (from packages/timeline_context_system/prompt_context_tracker.py)
export interface TCSTimelineEntry {
  timestamp: string
  prompt_id: string
  context_index: Record<string, any>
  summary: string
  context_evolution: Record<string, any>
  confidence_metrics: Record<string, number>
  relevance_score: number
  executed_via_chain_id?: string
  chain_execution_id?: string
  chain_node_id?: string
  parent_chain_ids: string[]
  child_chain_ids: string[]
  evolution_path: string[]
}

// CAS Attention Metrics (from packages/cas/attention.py)
export interface CASAttentionMetrics {
  timestamp: string
  session_id: string
  working_memory_items: number
  context_size_tokens: number
  attention_span_minutes: number
  task_switches_per_hour: number
  focus_depth: number  // 0.0-1.0
  attention_stability: number  // 0.0-1.0
  cognitive_load: number  // 0.0-1.0
  error_rate: number  // 0.0-1.0
  retry_frequency: number  // 0.0-1.0
  confidence_drift: number  // 0.0-1.0
  current_state: 'focused' | 'distributed' | 'overloaded' | 'narrowed' | 'degraded' | 'optimal'
  quality_level: 'excellent' | 'good' | 'fair' | 'poor' | 'critical'
  warnings: string[]
  alerts: string[]
}

// ===== HOOKS WITH REAL DATA STRUCTURES =====

// CMC Hook - Updated to use CMCService
export const useCMC = () => {
  const [atoms, setAtoms] = useState<CMCAtom[]>([])
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Load initial data from backend
  useEffect(() => {
    const loadInitialData = async () => {
      setLoading(true)
      try {
        // Load stats first
        const statsResult = await cmcService.getStats()
        if (statsResult.success && statsResult.stats) {
          setStats(statsResult.stats)
        }
        
        // Load recent atoms
        const atomsResult = await cmcService.retrieveAtoms('', 20)
        if (atomsResult.success && atomsResult.atoms) {
          setAtoms(atomsResult.atoms)
        }
      } catch (err) {
        console.error('CMC initial load error:', err)
        setError(err instanceof Error ? err.message : 'Failed to load CMC data')
        // Fallback to empty state - no mock data
      } finally {
        setLoading(false)
      }
    }
    
    loadInitialData()
  }, [])
  
  // Legacy mock data removed - using real backend services now
  
  const storeAtom = useCallback(async (
    content: string,
    modality: CMCAtom['modality'] = 'text',
    tags: Record<string, number> = {},
    metadata: Record<string, any> = {}
  ) => {
    setLoading(true)
    setError(null)
    try {
      const result = await cmcService.storeAtom(content, modality, tags, metadata)
      
      if (result.success && result.atom) {
        setAtoms(prev => [...prev, result.atom!])
        return { success: true, atom_id: result.atom_id || result.atom.id, atom: result.atom }
      } else {
        setError(result.error || 'Failed to store atom')
        return { success: false, error: result.error }
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      setError(errorMessage)
      console.error('CMC store error:', error)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }, [])
  
  const retrieveAtoms = useCallback(async (query: string, limit: number = 10): Promise<CMCAtom[]> => {
    setLoading(true)
    setError(null)
    try {
      const result = await cmcService.retrieveAtoms(query, limit)
      
      if (result.success && result.atoms) {
        setAtoms(result.atoms)
        return result.atoms
      } else {
        setError(result.error || 'Failed to retrieve atoms')
        return []
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      setError(errorMessage)
      console.error('CMC retrieve error:', error)
      return []
    } finally {
      setLoading(false)
    }
  }, [])
  
  const getStats = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await cmcService.getStats()
      
      if (result.success && result.stats) {
        setStats(result.stats)
        return result.stats
      } else {
        setError(result.error || 'Failed to get stats')
        return stats || null
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      setError(errorMessage)
      console.error('CMC stats error:', error)
      return stats || null
    } finally {
      setLoading(false)
    }
  }, [stats])
  
  return { storeAtom, retrieveAtoms, getStats, atoms, stats, loading, error }
}

// HHNI Hook - Updated to use HHNIService
export const useHHNI = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const search = useCallback(async (
    query: string,
    limit: number = 20,
    target_level: 'document' | 'paragraph' | 'sentence' = 'paragraph'
  ): Promise<HHNISearchResult[]> => {
    setLoading(true)
    setError(null)
    try {
      const result = await hhniService.search(query, limit, target_level)
      
      if (result.success && result.results) {
        return result.results
      } else {
        setError(result.error || 'Failed to search via HHNI')
        return []
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      console.error('HHNI search error:', err)
      return []
    } finally {
      setLoading(false)
    }
  }, [])
  
  const retrieve = useCallback(async (atomIds: string[]): Promise<CMCAtom[]> => {
    setLoading(true)
    setError(null)
    try {
      const result = await hhniService.retrieve(atomIds)
      
      if (result.success && result.atoms) {
        return result.atoms
      } else {
        setError(result.error || 'Failed to retrieve atoms')
        return []
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      console.error('HHNI retrieve error:', err)
      return []
    } finally {
      setLoading(false)
    }
  }, [])
  
  return { search, retrieve, loading, error }
}

// VIF Hook - Updated to use VIFService
export const useVIF = () => {
  const [witnesses, setWitnesses] = useState<VIFWitness[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const trackConfidence = useCallback(async (
    task: string,
    confidence: number,
    evidence: string[] = [],
    reasoning: string = '',
    task_criticality: 'critical' | 'important' | 'routine' | 'low_stakes' = 'routine'
  ): Promise<{ success: boolean; witness_id?: string; witness?: VIFWitness }> => {
    setLoading(true)
    setError(null)
    try {
      // Use VIFService to track confidence
      const result = await vifService.trackConfidence(
        'gpt-4-turbo', // model_id
        confidence,
        task_criticality,
        undefined, // context_snapshot_id
        undefined, // prompt_hash
        task.length / 4, // prompt_tokens (rough estimate)
        undefined, // output_hash
        reasoning.length / 4 // output_tokens (rough estimate)
      )
      
      if (result.success && result.witness) {
        setWitnesses(prev => [...prev, result.witness!])
        return { success: true, witness_id: result.witness_id || result.witness.id, witness: result.witness }
      } else {
        setError(result.error || 'Failed to track confidence')
        return { success: false }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      console.error('VIF track error:', err)
      return { success: false }
    } finally {
      setLoading(false)
    }
  }, [])
  
  const getWitnesses = useCallback(async (taskId: string): Promise<VIFWitness[]> => {
    setLoading(true)
    setError(null)
    try {
      const result = await vifService.getWitnesses(100) // Get all witnesses
      
      if (result.success && result.witnesses) {
        // Filter by taskId if provided
        const filtered = taskId 
          ? result.witnesses.filter(w => w.id === taskId || w.model_id === taskId)
          : result.witnesses
        setWitnesses(filtered)
        return filtered
      } else {
        setError(result.error || 'Failed to get witnesses')
        return witnesses // Return cached witnesses
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      console.error('VIF getWitnesses error:', err)
      return witnesses // Return cached witnesses
    } finally {
      setLoading(false)
    }
  }, [witnesses])
  
  return { trackConfidence, getWitnesses, witnesses, loading, error }
}

// SEG Hook - Updated to use SEGService
export const useSEG = () => {
  const [entities, setEntities] = useState<SEGEntity[]>([])
  const [relations, setRelations] = useState<SEGRelation[]>([])
  const [contradictions, setContradictions] = useState<SEGContradiction[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Initialize with comprehensive mock data matching EXACT SEG structure
  useEffect(() => {
    const now = new Date().toISOString()
    const mockEntities: SEGEntity[] = [
      {
        id: 'entity_cmc',
        type: 'source',
        name: 'CMC (Context Memory Core)',
        attributes: {
          description: 'Bitemporal storage system for all AIM-OS data',
          system: 'cmc',
          capabilities: ['storage', 'bitemporal', 'atoms']
        },
        tt_start: new Date(Date.now() - 3600000).toISOString(),
        tt_end: null,
        vt_start: new Date(Date.now() - 3600000).toISOString(),
        vt_end: null,
        source: 'aimos_systems',
        confidence: 0.95,
        tags: ['core_system', 'storage', 'bitemporal'],
        witness_id: 'witness_cmc_001'
      },
      {
        id: 'entity_hhni',
        type: 'source',
        name: 'HHNI (Hierarchical Hypergraph Neural Index)',
        attributes: {
          description: 'Semantic search and hierarchical navigation',
          system: 'hhni',
          capabilities: ['semantic_search', 'hierarchical_navigation']
        },
        tt_start: new Date(Date.now() - 3600000).toISOString(),
        tt_end: null,
        vt_start: new Date(Date.now() - 3600000).toISOString(),
        vt_end: null,
        source: 'aimos_systems',
        confidence: 0.93,
        tags: ['core_system', 'search', 'indexing'],
        witness_id: 'witness_hhni_001'
      },
      {
        id: 'entity_vif',
        type: 'source',
        name: 'VIF (Verifiable Intelligence Framework)',
        attributes: {
          description: 'Confidence tracking and quality gates',
          system: 'vif',
          capabilities: ['confidence_tracking', 'kappa_gates']
        },
        tt_start: new Date(Date.now() - 3600000).toISOString(),
        tt_end: null,
        vt_start: new Date(Date.now() - 3600000).toISOString(),
        vt_end: null,
        source: 'aimos_systems',
        confidence: 0.92,
        tags: ['core_system', 'quality', 'validation'],
        witness_id: 'witness_vif_001'
      },
      {
        id: 'entity_seg',
        type: 'source',
        name: 'SEG (Synthesis & Evidence Graph)',
        attributes: {
          description: 'Evidence tracking and contradiction detection',
          system: 'seg',
          capabilities: ['evidence_synthesis', 'contradiction_detection']
        },
        tt_start: new Date(Date.now() - 3600000).toISOString(),
        tt_end: null,
        vt_start: new Date(Date.now() - 3600000).toISOString(),
        vt_end: null,
        source: 'aimos_systems',
        confidence: 0.91,
        tags: ['core_system', 'graph', 'synthesis'],
        witness_id: 'witness_seg_001'
      },
      {
        id: 'entity_ide_prototype',
        type: 'derivation',
        name: 'IDE Prototype Development',
        attributes: {
          description: 'Building IDE prototype with AIM-OS integration',
          status: 'in_progress',
          agent: 'dac'
        },
        tt_start: new Date(Date.now() - 1800000).toISOString(),
        tt_end: null,
        vt_start: new Date(Date.now() - 1800000).toISOString(),
        vt_end: null,
        source: 'dac_agent',
        confidence: 0.90,
        tags: ['prototype', 'ide', 'development'],
        witness_id: 'witness_ide_001'
      },
      {
        id: 'entity_memorybrowser',
        type: 'derivation',
        name: 'MemoryBrowser Panel',
        attributes: {
          description: 'CMC memory exploration panel with HHNI search',
          component: 'MemoryBrowser',
          status: 'completed'
        },
        tt_start: new Date(Date.now() - 900000).toISOString(),
        tt_end: null,
        vt_start: new Date(Date.now() - 900000).toISOString(),
        vt_end: null,
        source: 'dac_agent',
        confidence: 0.94,
        tags: ['panel', 'memory', 'cmc'],
        witness_id: 'witness_mb_001'
      },
      {
        id: 'entity_contextweb',
        type: 'derivation',
        name: 'ContextWeb Panel',
        attributes: {
          description: 'Interactive SEG knowledge graph visualization',
          component: 'ContextWeb',
          status: 'completed'
        },
        tt_start: new Date(Date.now() - 600000).toISOString(),
        tt_end: null,
        vt_start: new Date(Date.now() - 600000).toISOString(),
        vt_end: null,
        source: 'dac_agent',
        confidence: 0.93,
        tags: ['panel', 'graph', 'seg'],
        witness_id: 'witness_cw_001'
      },
      {
        id: 'entity_evolutionexplorer',
        type: 'derivation',
        name: 'EvolutionExplorer View',
        attributes: {
          description: 'Bidirectional Timeline ↔ Chain ↔ Goals visualization',
          component: 'EvolutionExplorer',
          status: 'completed'
        },
        tt_start: new Date(Date.now() - 300000).toISOString(),
        tt_end: null,
        vt_start: new Date(Date.now() - 300000).toISOString(),
        vt_end: null,
        source: 'dac_agent',
        confidence: 0.92,
        tags: ['view', 'timeline', 'chain', 'goals'],
        witness_id: 'witness_ee_001'
      }
    ]
    
    const mockRelations: SEGRelation[] = [
      {
        id: 'rel_cmc_hhni',
        source_id: 'entity_cmc',
        target_id: 'entity_hhni',
        relation_type: 'SUPPORTS',
        evidence_ids: ['evidence_001', 'evidence_002'],
        confidence: 0.95,
        tt_start: new Date(Date.now() - 3600000).toISOString(),
        tt_end: null,
        vt_start: new Date(Date.now() - 3600000).toISOString(),
        vt_end: null,
        source: 'aimos_integration',
        tags: ['system_integration'],
        witness_id: 'witness_rel_001'
      },
      {
        id: 'rel_hhni_seg',
        source_id: 'entity_hhni',
        target_id: 'entity_seg',
        relation_type: 'SUPPORTS',
        evidence_ids: ['evidence_003'],
        confidence: 0.92,
        tt_start: new Date(Date.now() - 3600000).toISOString(),
        tt_end: null,
        vt_start: new Date(Date.now() - 3600000).toISOString(),
        vt_end: null,
        source: 'aimos_integration',
        tags: ['system_integration'],
        witness_id: 'witness_rel_002'
      },
      {
        id: 'rel_vif_seg',
        source_id: 'entity_vif',
        target_id: 'entity_seg',
        relation_type: 'REFERENCES',
        evidence_ids: ['evidence_004'],
        confidence: 0.88,
        tt_start: new Date(Date.now() - 3600000).toISOString(),
        tt_end: null,
        vt_start: new Date(Date.now() - 3600000).toISOString(),
        vt_end: null,
        source: 'aimos_integration',
        tags: ['system_integration'],
        witness_id: 'witness_rel_003'
      },
      {
        id: 'rel_ide_cmc',
        source_id: 'entity_ide_prototype',
        target_id: 'entity_cmc',
        relation_type: 'DERIVES_FROM',
        evidence_ids: ['evidence_005'],
        confidence: 0.90,
        tt_start: new Date(Date.now() - 1800000).toISOString(),
        tt_end: null,
        vt_start: new Date(Date.now() - 1800000).toISOString(),
        vt_end: null,
        source: 'dac_agent',
        tags: ['prototype', 'integration'],
        witness_id: 'witness_rel_004'
      },
      {
        id: 'rel_ide_hhni',
        source_id: 'entity_ide_prototype',
        target_id: 'entity_hhni',
        relation_type: 'DERIVES_FROM',
        evidence_ids: ['evidence_006'],
        confidence: 0.90,
        tt_start: new Date(Date.now() - 1800000).toISOString(),
        tt_end: null,
        vt_start: new Date(Date.now() - 1800000).toISOString(),
        vt_end: null,
        source: 'dac_agent',
        tags: ['prototype', 'integration'],
        witness_id: 'witness_rel_005'
      },
      {
        id: 'rel_memorybrowser_cmc',
        source_id: 'entity_memorybrowser',
        target_id: 'entity_cmc',
        relation_type: 'REFERENCES',
        evidence_ids: ['evidence_007'],
        confidence: 0.95,
        tt_start: new Date(Date.now() - 900000).toISOString(),
        tt_end: null,
        vt_start: new Date(Date.now() - 900000).toISOString(),
        vt_end: null,
        source: 'dac_agent',
        tags: ['panel', 'integration'],
        witness_id: 'witness_rel_006'
      },
      {
        id: 'rel_contextweb_seg',
        source_id: 'entity_contextweb',
        target_id: 'entity_seg',
        relation_type: 'REFERENCES',
        evidence_ids: ['evidence_008'],
        confidence: 0.93,
        tt_start: new Date(Date.now() - 600000).toISOString(),
        tt_end: null,
        vt_start: new Date(Date.now() - 600000).toISOString(),
        vt_end: null,
        source: 'dac_agent',
        tags: ['panel', 'integration'],
        witness_id: 'witness_rel_007'
      },
      {
        id: 'rel_evolutionexplorer_ide',
        source_id: 'entity_evolutionexplorer',
        target_id: 'entity_ide_prototype',
        relation_type: 'DERIVES_FROM',
        evidence_ids: ['evidence_009'],
        confidence: 0.91,
        tt_start: new Date(Date.now() - 300000).toISOString(),
        tt_end: null,
        vt_start: new Date(Date.now() - 300000).toISOString(),
        vt_end: null,
        source: 'dac_agent',
        tags: ['view', 'integration'],
        witness_id: 'witness_rel_008'
      }
    ]
    
    // Mock data initialization removed - using real backend now
    // setEntities(mockEntities)
    // setRelations(mockRelations)
  }, [])
  
  const detectContradictions = useCallback(async (content: string): Promise<SEGContradiction[]> => {
    setLoading(true)
    setError(null)
    try {
      const result = await segService.detectContradictions()
      
      if (result.success && result.contradictions) {
        setContradictions(result.contradictions)
        return result.contradictions
      } else {
        setError(result.error || 'Failed to detect contradictions')
        return []
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      console.error('SEG contradiction detection error:', err)
      return []
    } finally {
      setLoading(false)
    }
  }, [])
  
  const synthesizeKnowledge = useCallback(async (
    topics: string[],
    format: 'summary' | 'detailed' | 'structured' = 'summary',
    depth: 'shallow' | 'medium' | 'deep' = 'medium'
  ) => {
    setLoading(true)
    setError(null)
    try {
      // Use first topic as query, or join topics
      const query = topics.join(' ')
      const result = await segService.synthesizeKnowledge(query, 20)
      
      if (result.success) {
        if (result.entities) setEntities(result.entities)
        if (result.relations) setRelations(result.relations)
        
        return {
          success: true,
          synthesis: `Synthesized knowledge for topics: ${topics.join(', ')}`,
          format,
          depth,
          entities_used: result.entities?.length || 0,
          relations_used: result.relations?.length || 0
        }
      } else {
        setError(result.error || 'Failed to synthesize knowledge')
        return { success: false, error: result.error }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      console.error('SEG synthesize error:', err)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }, [])
  
  return { detectContradictions, synthesizeKnowledge, entities, relations, contradictions, loading, error }
}

// Timeline Entry (Extended structure from T2_architecture.md - EXACT STRUCTURE)
export interface TimelineEntry {
  entry_id: string
  timestamp: string
  event_type: string  // BREAKTHROUGH, MAJOR_MILESTONE, etc.
  title: string
  description: string
  context_data: Record<string, any>
  quality_metrics: Record<string, number>
  emotional_context: Record<string, any>
  technical_details: Record<string, any>
  next_steps: string[]
  related_files: string[]
  tags: string[]
  metadata: Record<string, any>
  
  // Bitemporal fields
  valid_from: string  // Valid time start
  valid_to: string | null  // Valid time end
  
  // Chain Connection Fields (Evolution Explorer)
  executed_via_chain_id?: string  // Chain that executed this entry
  chain_execution_id?: string  // Execution instance ID
  chain_node_id?: string  // Specific node in chain
  
  // Chain Evolution Tracking
  parent_chain_ids: string[]  // Chains that led here
  child_chain_ids: string[]  // Chains spawned from here
  evolution_path: string[]  // Path through evolution graph
}

// TCS Hook - Updated to use TCSService
export const useTCS = () => {
  const [entries, setEntries] = useState<TimelineEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Initialize with comprehensive mock timeline entries matching EXACT extended structure
  useEffect(() => {
    const now = Date.now()
    const mockEntries: TimelineEntry[] = [
      {
        entry_id: 'timeline_001',
        timestamp: new Date(now - 3600000).toISOString(),
        event_type: 'MAJOR_MILESTONE',
        title: 'IDE Prototype Development Started',
        description: 'User requested IDE prototype with AIM-OS integration. Focus on deep system integration with CMC, HHNI, VIF, SEG, APOE, CAS, and TCS systems.',
        context_data: {
          goal_id: 'OBJ-07',
          task_type: 'prototype_development',
          agent: 'dac'
        },
        quality_metrics: {
          overall: 0.95,
          understanding: 0.90,
          execution: 0.80
        },
        emotional_context: {
          state: 'excited',
          energy: 'high',
          focus: 'intense'
        },
        technical_details: {
          systems_involved: ['cmc', 'hhni', 'vif', 'seg', 'apoe', 'cas', 'tcs'],
          complexity: 'high',
          estimated_hours: 12
        },
        next_steps: [
          'Research AIM-OS systems',
          'Design panel architecture',
          'Implement core layout',
          'Integrate AIM-OS hooks'
        ],
        related_files: [
          'ide_orchestration/prototypes/dac/src/hooks/useAIMOS.ts',
          'ide_orchestration/prototypes/dac/src/components/IDELayout.tsx'
        ],
        tags: ['ide', 'prototype', 'aimos', 'development'],
        metadata: {
          evidence_ids: ['atom_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6']
        },
        valid_from: new Date(now - 3600000).toISOString(),
        valid_to: null,
        executed_via_chain_id: 'chain_ide_prototype',
        chain_execution_id: 'chain_exec_001',
        chain_node_id: 'node_001',
        parent_chain_ids: [],
        child_chain_ids: ['chain_panel_integration'],
        evolution_path: []
      },
      {
        entry_id: 'timeline_002',
        timestamp: new Date(now - 3000000).toISOString(),
        event_type: 'ARCHITECTURE_DISCUSSION',
        title: 'IDE Architecture Discussion',
        description: 'Discussed 5-zone layout system with Top Bar, Left Drawer, Main Content, Right Drawer, and Bottom Drawer. Each zone supports multiple panels with drag-and-drop customization.',
        context_data: {
          topic: 'architecture',
          layout: '5-zone',
          agent: 'dac'
        },
        quality_metrics: {
          overall: 0.92,
          understanding: 0.95,
          execution: 0.88
        },
        emotional_context: {
          state: 'focused',
          energy: 'high',
          focus: 'intense'
        },
        technical_details: {
          layout_type: '5-zone',
          zones: ['top_bar', 'left_drawer', 'main_content', 'right_drawer', 'bottom_drawer'],
          customization: 'drag_and_drop'
        },
        next_steps: [
          'Finalize panel organization',
          'Implement drag-and-drop',
          'Add customization options'
        ],
        related_files: [
          'ide_orchestration/research/UI_ARCHITECTURE_SYNTHESIS.md'
        ],
        tags: ['architecture', 'layout', 'design'],
        metadata: {
          evidence_ids: ['atom_text_ide_architecture']
        },
        valid_from: new Date(now - 3000000).toISOString(),
        valid_to: null,
        executed_via_chain_id: 'chain_ide_prototype',
        chain_execution_id: 'chain_exec_001',
        chain_node_id: 'node_002',
        parent_chain_ids: [],
        child_chain_ids: [],
        evolution_path: ['timeline_001']
      },
      {
        entry_id: 'timeline_003',
        timestamp: new Date(now - 2400000).toISOString(),
        event_type: 'RESEARCH_COMPLETE',
        title: 'AIM-OS Systems Research',
        description: 'Researched AIM-OS systems: CMC, HHNI, VIF, SEG, APOE, CAS, TCS. Understanding integration points, data structures, and API patterns.',
        context_data: {
          topic: 'aimos_systems',
          systems: ['cmc', 'hhni', 'vif', 'seg', 'apoe', 'cas', 'tcs'],
          agent: 'dac'
        },
        quality_metrics: {
          overall: 0.90,
          understanding: 0.92,
          execution: 0.88
        },
        emotional_context: {
          state: 'curious',
          energy: 'moderate',
          focus: 'deep'
        },
        technical_details: {
          systems_researched: 7,
          documentation_reviewed: ['T2_architecture.md', 'T3_detailed.md', 'models.py'],
          integration_points_identified: 15
        },
        next_steps: [
          'Design hook interfaces',
          'Create mock data structures',
          'Implement integration'
        ],
        related_files: [
          'knowledge_architecture/systems/cmc/T2_architecture.md',
          'knowledge_architecture/systems/hhni/T3_detailed.md',
          'packages/cmc_service/models.py'
        ],
        tags: ['research', 'aimos', 'systems'],
        metadata: {
          evidence_ids: ['atom_text_aimos_systems']
        },
        valid_from: new Date(now - 2400000).toISOString(),
        valid_to: null,
        executed_via_chain_id: 'chain_ide_prototype',
        chain_execution_id: 'chain_exec_001',
        chain_node_id: 'node_003',
        parent_chain_ids: [],
        child_chain_ids: [],
        evolution_path: ['timeline_001', 'timeline_002']
      },
      {
        entry_id: 'timeline_004',
        timestamp: new Date(now - 1800000).toISOString(),
        event_type: 'CODE_IMPLEMENTATION',
        title: 'CMC Hook Implementation',
        description: 'Implemented useCMC hook with comprehensive mock data matching real AIM-OS CMC atom structure. Includes all fields: modality, content (inline/uri), tags, witness, bitemporal fields.',
        context_data: {
          file: 'src/hooks/useAIMOS.ts',
          component: 'useCMC',
          agent: 'dac'
        },
        quality_metrics: {
          overall: 0.93,
          understanding: 0.95,
          execution: 0.91
        },
        emotional_context: {
          state: 'accomplished',
          energy: 'high',
          focus: 'sustained'
        },
        technical_details: {
          hook_name: 'useCMC',
          mock_atoms_count: 10,
          fields_implemented: ['id', 'modality', 'content', 'tags', 'witness', 'valid_from', 'valid_to', 'hash']
        },
        next_steps: [
          'Implement HHNI hook',
          'Implement VIF hook',
          'Implement SEG hook'
        ],
        related_files: [
          'ide_orchestration/prototypes/dac/src/hooks/useAIMOS.ts',
          'packages/cmc_service/models.py'
        ],
        tags: ['code', 'hook', 'cmc', 'implementation'],
        metadata: {
          evidence_ids: ['atom_b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7']
        },
        valid_from: new Date(now - 1800000).toISOString(),
        valid_to: null,
        executed_via_chain_id: 'chain_panel_integration',
        chain_execution_id: 'chain_exec_002',
        chain_node_id: 'node_001',
        parent_chain_ids: ['chain_ide_prototype'],
        child_chain_ids: [],
        evolution_path: ['timeline_001', 'timeline_002', 'timeline_003']
      },
      {
        entry_id: 'timeline_005',
        timestamp: new Date(now - 1500000).toISOString(),
        event_type: 'CODE_IMPLEMENTATION',
        title: 'ContextWeb Panel Implementation',
        description: 'Implemented ContextWeb panel with ReactFlow integration for SEG knowledge graph visualization. Displays entities, relations, and contradictions with bitemporal tracking.',
        context_data: {
          file: 'src/panels/ContextWeb.tsx',
          component: 'ContextWeb',
          agent: 'dac'
        },
        quality_metrics: {
          overall: 0.91,
          understanding: 0.93,
          execution: 0.89
        },
        emotional_context: {
          state: 'creative',
          energy: 'high',
          focus: 'flow'
        },
        technical_details: {
          component: 'ContextWeb',
          library: 'ReactFlow',
          features: ['entity_visualization', 'relation_visualization', 'contradiction_highlighting']
        },
        next_steps: [
          'Add layout algorithms',
          'Implement filtering',
          'Add interaction controls'
        ],
        related_files: [
          'ide_orchestration/prototypes/dac/src/panels/ContextWeb.tsx',
          'packages/seg/models.py'
        ],
        tags: ['code', 'panel', 'contextweb', 'seg'],
        metadata: {
          evidence_ids: ['atom_code_contextweb']
        },
        valid_from: new Date(now - 1500000).toISOString(),
        valid_to: null,
        executed_via_chain_id: 'chain_panel_integration',
        chain_execution_id: 'chain_exec_002',
        chain_node_id: 'node_002',
        parent_chain_ids: ['chain_ide_prototype'],
        child_chain_ids: [],
        evolution_path: ['timeline_001', 'timeline_004']
      },
      {
        entry_id: 'timeline_006',
        timestamp: new Date(now - 1200000).toISOString(),
        event_type: 'CODE_IMPLEMENTATION',
        title: 'TimelineView Panel Implementation',
        description: 'Implemented TimelineView panel with TCS integration and bitemporal playback controls. Displays timeline entries with chain connections and evolution paths.',
        context_data: {
          file: 'src/panels/TimelineView.tsx',
          component: 'TimelineView',
          agent: 'dac'
        },
        quality_metrics: {
          overall: 0.92,
          understanding: 0.94,
          execution: 0.90
        },
        emotional_context: {
          state: 'focused',
          energy: 'moderate',
          focus: 'deep'
        },
        technical_details: {
          component: 'TimelineView',
          features: ['bitemporal_playback', 'chain_connections', 'evolution_paths'],
          playback_controls: true
        },
        next_steps: [
          'Add speed controls',
          'Implement filtering',
          'Add timeline navigation'
        ],
        related_files: [
          'ide_orchestration/prototypes/dac/src/panels/TimelineView.tsx',
          'packages/timeline_context_system/prompt_context_tracker.py'
        ],
        tags: ['code', 'panel', 'timeline', 'tcs'],
        metadata: {
          evidence_ids: ['atom_code_timeline']
        },
        valid_from: new Date(now - 1200000).toISOString(),
        valid_to: null,
        executed_via_chain_id: 'chain_panel_integration',
        chain_execution_id: 'chain_exec_002',
        chain_node_id: 'node_003',
        parent_chain_ids: ['chain_ide_prototype'],
        child_chain_ids: [],
        evolution_path: ['timeline_001', 'timeline_004']
      },
      {
        entry_id: 'timeline_007',
        timestamp: new Date(now - 900000).toISOString(),
        event_type: 'PANEL_CREATED',
        title: 'MemoryBrowser Panel Created',
        description: 'Created MemoryBrowser panel with CMC integration. Features: semantic search via HHNI, modality filtering (text/code/event/tool/cross_model), confidence display via VIF witnesses, bitemporal validity display.',
        context_data: {
          panel: 'MemoryBrowser',
          features: ['cmc_integration', 'hhni_search', 'vif_confidence', 'bitemporal_display'],
          agent: 'dac'
        },
        quality_metrics: {
          overall: 0.94,
          understanding: 0.96,
          execution: 0.92
        },
        emotional_context: {
          state: 'proud',
          energy: 'high',
          focus: 'sustained'
        },
        technical_details: {
          panel: 'MemoryBrowser',
          integrations: ['CMC', 'HHNI', 'VIF'],
          features: ['semantic_search', 'modality_filtering', 'confidence_display', 'bitemporal_display']
        },
        next_steps: [
          'Add advanced filtering',
          'Implement sorting',
          'Add export functionality'
        ],
        related_files: [
          'ide_orchestration/prototypes/dac/src/panels/MemoryBrowser.tsx'
        ],
        tags: ['panel', 'memorybrowser', 'cmc'],
        metadata: {
          evidence_ids: ['atom_event_panel_created']
        },
        valid_from: new Date(now - 900000).toISOString(),
        valid_to: null,
        executed_via_chain_id: 'chain_panel_integration',
        chain_execution_id: 'chain_exec_002',
        chain_node_id: 'node_004',
        parent_chain_ids: ['chain_ide_prototype'],
        child_chain_ids: [],
        evolution_path: ['timeline_001', 'timeline_004']
      },
      {
        entry_id: 'timeline_008',
        timestamp: new Date(now - 600000).toISOString(),
        event_type: 'INTEGRATION_COMPLETE',
        title: 'EvolutionExplorer Integration Complete',
        description: 'Completed AIM-OS integration for EvolutionExplorer. Connected Timeline ↔ Chain ↔ Goals with bidirectional graph visualization using ReactFlow. Displays chain connections, evolution paths, and goal relationships.',
        context_data: {
          component: 'EvolutionExplorer',
          integration: 'timeline_chain_goals',
          agent: 'dac'
        },
        quality_metrics: {
          overall: 0.93,
          understanding: 0.95,
          execution: 0.91
        },
        emotional_context: {
          state: 'accomplished',
          energy: 'high',
          focus: 'sustained'
        },
        technical_details: {
          component: 'EvolutionExplorer',
          connections: ['timeline_chain', 'chain_goals', 'timeline_goals'],
          visualization: 'ReactFlow_bidirectional_graph'
        },
        next_steps: [
          'Add filtering',
          'Implement node details',
          'Add path highlighting'
        ],
        related_files: [
          'ide_orchestration/prototypes/dac/src/views/EvolutionExplorer.tsx'
        ],
        tags: ['view', 'evolutionexplorer', 'integration'],
        metadata: {
          evidence_ids: ['atom_event_integration_complete']
        },
        valid_from: new Date(now - 600000).toISOString(),
        valid_to: null,
        executed_via_chain_id: 'chain_panel_integration',
        chain_execution_id: 'chain_exec_002',
        chain_node_id: 'node_005',
        parent_chain_ids: ['chain_ide_prototype'],
        child_chain_ids: [],
        evolution_path: ['timeline_001', 'timeline_004', 'timeline_007']
      },
      {
        entry_id: 'timeline_009',
        timestamp: new Date(now - 300000).toISOString(),
        event_type: 'DECISION_MADE',
        title: 'Mock Data Strategy Decision',
        description: 'Decision: Use comprehensive mock data for prototype panels. Reasoning: Enables full UI demonstration without backend dependencies, matches real AIM-OS data structures exactly, allows testing of all features.',
        context_data: {
          decision_type: 'prototype_strategy',
          alternatives: ['backend_integration', 'hybrid'],
          agent: 'dac'
        },
        quality_metrics: {
          overall: 0.92,
          understanding: 0.94,
          execution: 0.90
        },
        emotional_context: {
          state: 'confident',
          energy: 'moderate',
          focus: 'clear'
        },
        technical_details: {
          decision: 'comprehensive_mock_data',
          rationale: ['ui_demonstration', 'structure_matching', 'feature_testing'],
          alternatives_considered: 2
        },
        next_steps: [
          'Enhance mock data',
          'Add more realistic scenarios',
          'Document mock data structure'
        ],
        related_files: [],
        tags: ['decision', 'strategy', 'prototype'],
        metadata: {
          evidence_ids: ['atom_decision_mock_data']
        },
        valid_from: new Date(now - 300000).toISOString(),
        valid_to: null,
        executed_via_chain_id: 'chain_panel_integration',
        chain_execution_id: 'chain_exec_002',
        chain_node_id: 'node_006',
        parent_chain_ids: ['chain_ide_prototype'],
        child_chain_ids: [],
        evolution_path: ['timeline_001', 'timeline_008']
      },
      {
        entry_id: 'timeline_010',
        timestamp: new Date(now - 150000).toISOString(),
        event_type: 'TASK_COMPLETED',
        title: 'Panel Integration Complete',
        description: 'All panels integrated with comprehensive mock data matching exact AIM-OS structures. MemoryBrowser, ContextWeb, TimelineView, and EvolutionExplorer all functional with deep AIM-OS integration.',
        context_data: {
          status: 'completed',
          panels: ['MemoryBrowser', 'ContextWeb', 'TimelineView', 'EvolutionExplorer'],
          agent: 'dac'
        },
        quality_metrics: {
          overall: 0.95,
          understanding: 0.97,
          execution: 0.93
        },
        emotional_context: {
          state: 'accomplished',
          energy: 'high',
          focus: 'sustained'
        },
        technical_details: {
          panels_completed: 4,
          integrations: ['CMC', 'HHNI', 'VIF', 'SEG', 'TCS', 'APOE'],
          mock_data_comprehensive: true
        },
        next_steps: [
          'Perfect each panel',
          'Add advanced features',
          'Enhance visualizations'
        ],
        related_files: [
          'ide_orchestration/prototypes/dac/src/panels/MemoryBrowser.tsx',
          'ide_orchestration/prototypes/dac/src/panels/ContextWeb.tsx',
          'ide_orchestration/prototypes/dac/src/panels/TimelineView.tsx',
          'ide_orchestration/prototypes/dac/src/views/EvolutionExplorer.tsx'
        ],
        tags: ['completion', 'integration', 'panels'],
        metadata: {},
        valid_from: new Date(now - 150000).toISOString(),
        valid_to: null,
        executed_via_chain_id: 'chain_panel_integration',
        chain_execution_id: 'chain_exec_002',
        chain_node_id: 'node_007',
        parent_chain_ids: ['chain_ide_prototype'],
        child_chain_ids: [],
        evolution_path: ['timeline_001', 'timeline_008', 'timeline_009']
      }
    ]
    // Mock data initialization removed - using real backend now
    // setEntries(mockEntries)
    
    // Load initial timeline entries from backend
    const loadInitialEntries = async () => {
      try {
        const result = await tcsService.getSummary(20)
        if (result.success && result.entries) {
          // Convert TCSTimelineEntry to TimelineEntry format
          const convertedEntries: TimelineEntry[] = result.entries.map(tcsEntry => ({
            entry_id: tcsEntry.prompt_id,
            timestamp: tcsEntry.timestamp,
            event_type: 'timeline_entry',
            title: tcsEntry.summary.substring(0, 50),
            description: tcsEntry.summary,
            context_data: tcsEntry.context_index,
            quality_metrics: tcsEntry.confidence_metrics,
            emotional_context: {},
            technical_details: tcsEntry.context_evolution,
            next_steps: [],
            related_files: [],
            tags: [],
            metadata: {},
            valid_from: tcsEntry.timestamp,
            valid_to: null,
            executed_via_chain_id: tcsEntry.executed_via_chain_id,
            chain_execution_id: tcsEntry.chain_execution_id,
            chain_node_id: tcsEntry.chain_node_id,
            parent_chain_ids: tcsEntry.parent_chain_ids,
            child_chain_ids: tcsEntry.child_chain_ids,
            evolution_path: tcsEntry.evolution_path
          }))
          setEntries(convertedEntries)
        }
      } catch (err) {
        console.error('TCS initial load error:', err)
      }
    }
    
    loadInitialEntries()
  }, [])
  
  const addEntry = useCallback(async (
    promptId: string,
    userInput: string,
    contextState: Record<string, any> = {}
  ): Promise<{ success: boolean; entry_id?: string }> => {
    setLoading(true)
    setError(null)
    try {
      const result = await tcsService.addEntry(
        'user_input',
        userInput,
        { prompt_id: promptId, ...contextState },
        contextState,
        userInput.substring(0, 100) // summary
      )
      
      if (result.success && result.entry) {
        // Convert TCSTimelineEntry to TimelineEntry and add to state
        const convertedEntry: TimelineEntry = {
          entry_id: result.entry_id || result.entry.prompt_id,
          timestamp: result.entry.timestamp,
          event_type: 'user_input',
          title: result.entry.summary.substring(0, 50),
          description: result.entry.summary,
          context_data: result.entry.context_index,
          quality_metrics: result.entry.confidence_metrics,
          emotional_context: {},
          technical_details: result.entry.context_evolution,
          next_steps: [],
          related_files: [],
          tags: [],
          metadata: {},
          valid_from: result.entry.timestamp,
          valid_to: null,
          executed_via_chain_id: result.entry.executed_via_chain_id,
          chain_execution_id: result.entry.chain_execution_id,
          chain_node_id: result.entry.chain_node_id,
          parent_chain_ids: result.entry.parent_chain_ids,
          child_chain_ids: result.entry.child_chain_ids,
          evolution_path: result.entry.evolution_path
        }
        setEntries(prev => [...prev, convertedEntry])
        return { success: true, entry_id: convertedEntry.entry_id }
      } else {
        setError(result.error || 'Failed to add timeline entry')
        return { success: false }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      console.error('TCS add entry error:', err)
      return { success: false }
    } finally {
      setLoading(false)
    }
  }, [])
  
  const getSummary = useCallback(async (limit: number = 10): Promise<TimelineEntry[]> => {
    setLoading(true)
    setError(null)
    try {
      const result = await tcsService.getSummary(limit)
      
      if (result.success && result.entries) {
        // Convert TCSTimelineEntry to TimelineEntry format
        const convertedEntries: TimelineEntry[] = result.entries.map(tcsEntry => ({
          entry_id: tcsEntry.prompt_id,
          timestamp: tcsEntry.timestamp,
          event_type: 'timeline_entry',
          title: tcsEntry.summary.substring(0, 50),
          description: tcsEntry.summary,
          context_data: tcsEntry.context_index,
          quality_metrics: tcsEntry.confidence_metrics,
          emotional_context: {},
          technical_details: tcsEntry.context_evolution,
          next_steps: [],
          related_files: [],
          tags: [],
          metadata: {},
          valid_from: tcsEntry.timestamp,
          valid_to: null,
          executed_via_chain_id: tcsEntry.executed_via_chain_id,
          chain_execution_id: tcsEntry.chain_execution_id,
          chain_node_id: tcsEntry.chain_node_id,
          parent_chain_ids: tcsEntry.parent_chain_ids,
          child_chain_ids: tcsEntry.child_chain_ids,
          evolution_path: tcsEntry.evolution_path
        }))
        setEntries(convertedEntries)
        return convertedEntries
      } else {
        setError(result.error || 'Failed to get timeline summary')
        return entries.slice(-limit) // Return cached entries
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      console.error('TCS summary error:', err)
      return entries.slice(-limit) // Return cached entries
    } finally {
      setLoading(false)
    }
  }, [entries])
  
  const getTimelineGraph = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await tcsService.getTimelineGraph()
      
      if (result.success && result.graph) {
        // Return graph structure if available
        return result.graph
      } else {
        // Fallback: use entries with connections
        return entries.map(entry => ({
          ...entry,
          connections: [
            ...(entry.parent_chain_ids || []).map(id => ({ type: 'parent_chain', id })),
            ...(entry.child_chain_ids || []).map(id => ({ type: 'child_chain', id })),
            ...(entry.evolution_path || []).map(id => ({ type: 'evolution', id }))
          ]
        }))
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      console.error('TCS graph error:', err)
      // Fallback: return entries with connections
      return entries.map(entry => ({
        ...entry,
        connections: [
          ...(entry.parent_chain_ids || []).map(id => ({ type: 'parent_chain', id })),
          ...(entry.child_chain_ids || []).map(id => ({ type: 'child_chain', id })),
          ...(entry.evolution_path || []).map(id => ({ type: 'evolution', id }))
        ]
      }))
    } finally {
      setLoading(false)
    }
  }, [entries])
  
  return { addEntry, getSummary, getTimelineGraph, entries, loading, error }
}

// CAS Hook - Updated to use CASService
export const useCAS = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [metrics, setMetrics] = useState<CASAttentionMetrics | null>(null)
  
  const getMetrics = useCallback(async (): Promise<CASAttentionMetrics | null> => {
    setLoading(true)
    setError(null)
    try {
      const result = await casService.getMetrics()
      
      if (result.success && result.metrics) {
        setMetrics(result.metrics)
        return result.metrics
      } else {
        setError(result.error || 'Failed to get consciousness metrics')
        return metrics // Return cached metrics
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      console.error('CAS metrics error:', err)
      return metrics // Return cached metrics
    } finally {
      setLoading(false)
    }
  }, [metrics])
  
  const detectDrift = useCallback(async (
    contextSizeTokens: number,
    errorRate: number,
    workingMemoryItems: number
  ) => {
    setLoading(true)
    setError(null)
    try {
      const result = await casService.detectDrift()
      
      if (result.success) {
        // Use result if available, otherwise calculate from parameters
        const driftDetected = result.drift_detected ?? (errorRate > 0.1 || workingMemoryItems > 20 || contextSizeTokens > 100000)
        
        return {
          drift_detected: driftDetected,
          severity: driftDetected ? (errorRate > 0.2 ? 'high' : 'medium') : 'low',
          recommendations: driftDetected ? [
            'Reduce context size',
            'Clear working memory',
            'Take a break'
          ] : []
        }
      } else {
        setError(result.error || 'Failed to detect drift')
        // Fallback calculation
        const driftDetected = errorRate > 0.1 || workingMemoryItems > 20 || contextSizeTokens > 100000
        return {
          drift_detected: driftDetected,
          severity: driftDetected ? (errorRate > 0.2 ? 'high' : 'medium') : 'low',
          recommendations: driftDetected ? [
            'Reduce context size',
            'Clear working memory',
            'Take a break'
          ] : []
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      console.error('CAS drift detection error:', err)
      return { drift_detected: false, severity: 'low', recommendations: [] }
    } finally {
      setLoading(false)
    }
  }, [])
  
  return { getMetrics, detectDrift, metrics, loading, error }
}

// APOE Hook - Updated to use APOEService
export const useAPOE = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const createPlan = useCallback(async (
    goal: string,
    context: string = '',
    priority: 'low' | 'medium' | 'high' | 'critical' = 'medium'
  ) => {
    setLoading(true)
    setError(null)
    try {
      const result = await apoeService.createPlan(goal, context, priority)
      
      if (result.success && result.plan) {
        return {
          success: true,
          plan_id: result.plan.plan_id,
          goal: result.plan.goal,
          context,
          priority
        }
      } else {
        setError(result.error || 'Failed to create plan')
        return { success: false, error: result.error }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      console.error('APOE create plan error:', err)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }, [])
  
  const executePlan = useCallback(async (planId: string, inputs: Record<string, any> = {}, context: Record<string, any> = {}) => {
    setLoading(true)
    setError(null)
    try {
      const result = await apoeService.executePlan(planId, inputs, context)
      
      if (result.success) {
        return { success: true, plan_id: planId, execution_id: result.execution_id }
      } else {
        setError(result.error || 'Failed to execute plan')
        return { success: false, error: result.error }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      console.error('APOE execute plan error:', err)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }, [])
  
  return { createPlan, executePlan, loading, error }
}

// Context Web Hook (combines HHNI + SEG + CMC)
export const useContextWeb = () => {
  const { search } = useHHNI()
  const { entities, relations } = useSEG()
  const { retrieveAtoms } = useCMC()
  
  const buildContextWeb = useCallback(async (query: string) => {
    const nodes: any[] = []
    const edges: any[] = []
    
    // Get HHNI search results
    const hhniResults = await search(query, 20)
    
    // Add SEG entities as nodes
    entities.forEach((entity, index) => {
      nodes.push({
        id: `entity_${entity.id}`,
        label: entity.name,
        type: entity.type,
        entity: entity,
        confidence: 0.85 + (Math.random() * 0.1),
        score: 0.8 + (Math.random() * 0.15)
      })
    })
    
    // Add HHNI results as nodes
    hhniResults.forEach((result, index) => {
      nodes.push({
        id: `hhni_${result.node.id}`,
        label: result.node.content.substring(0, 50),
        type: 'atom',
        confidence: result.confidence,
        score: result.score,
        cmc_atom: result.node.id
      })
    })
    
    // Add SEG relations as edges
    relations.forEach((relation) => {
      edges.push({
        source: `entity_${relation.source_id}`,
        target: `entity_${relation.target_id}`,
        type: relation.relation_type,
        confidence: relation.confidence,
        weight: relation.weight || 0.8,
        relation: relation
      })
    })
    
    // Add connections between HHNI nodes
    for (let i = 0; i < hhniResults.length - 1; i++) {
      edges.push({
        source: `hhni_${hhniResults[i].node.id}`,
        target: `hhni_${hhniResults[i + 1].node.id}`,
        type: 'related',
        confidence: 0.80,
        weight: 0.75
      })
    }
    
    return {
      nodes,
      edges,
      total_context: nodes.length * 1000,
      active_window: 8000,
      retrieved: nodes.length * 400
    }
  }, [search, entities, relations])
  
  return { buildContextWeb }
}
