/**
 * MIGE Time-Lapse Service
 * Phase 5 Week 19: MIGE Time-Lapse
 * 
 * Implements:
 * - CMC bitemporal storage integration (Transaction Time vs. Valid Time)
 * - retrieve_memory with valid_time filters
 * - IdeaEvolutionTimeline interface
 * - MIGE stage mapping (SEED, VISION_TENSOR, TRUNK_INDEX, DEPLOYED)
 * - Snapshot array with context states
 * - SEG anchor tracking per snapshot
 * - State restoration logic
 */

import { CMCService } from '../CMCService'
import { TCSService } from '../TCSService'
import { SEGService } from '../SEGService'
import type { 
  MigeTimelineData,
  ContextWeb,
  EvidencePack
} from '../../types/aetherChatTypes'

const cmcService = new CMCService()
const tcsService = new TCSService()
const segService = new SEGService()

/**
 * MIGE Stage types
 */
export type MigeStage = 'SEED' | 'VISION_TENSOR' | 'TRUNK_INDEX' | 'DEPLOYED'

/**
 * Idea snapshot at a point in time
 */
export interface IdeaSnapshot {
  timestamp: Date
  validTime: Date // When this state was valid
  transactionTime: Date // When this was recorded
  stage: MigeStage
  contextState: {
    openFiles: string[]
    activeConstraints: string[]
    vifConfidence: number
    contextWeb?: ContextWeb
    evidencePack?: EvidencePack
  }
  segAnchors: string[] // SEG anchor IDs at this snapshot
  ideaAtomId: string // CMC atom ID for this idea
}

/**
 * Idea evolution timeline
 */
export interface IdeaEvolutionTimeline {
  ideaAtomId: string
  ideaLabel: string
  snapshots: IdeaSnapshot[]
  currentStage: MigeStage
  createdAt: Date
  lastUpdated: Date
}

/**
 * Retrieve MIGE timeline for an idea
 */
export async function retrieveMigeTimeline(
  ideaAtomId: string,
  validTime?: Date
): Promise<IdeaEvolutionTimeline | null> {
  try {
    // 1. Retrieve idea atom from CMC
    const ideaResult = await cmcService.retrieveAtoms(`id:${ideaAtomId}`, 1)
    
    if (!ideaResult.success || !ideaResult.atoms || ideaResult.atoms.length === 0) {
      return null
    }
    
    const ideaAtom = ideaResult.atoms[0]
    const ideaLabel = ideaAtom.metadata?.label || ideaAtom.content.substring(0, 50)
    
    // 2. Retrieve all snapshots for this idea (using valid_time if provided)
    const snapshots = await retrieveIdeaSnapshots(ideaAtomId, validTime)
    
    // 3. Determine current stage
    const currentStage = snapshots.length > 0 
      ? snapshots[snapshots.length - 1].stage 
      : 'SEED'
    
    return {
      ideaAtomId,
      ideaLabel,
      snapshots,
      currentStage,
      createdAt: snapshots.length > 0 ? snapshots[0].timestamp : new Date(),
      lastUpdated: snapshots.length > 0 ? snapshots[snapshots.length - 1].timestamp : new Date()
    }
  } catch (error) {
    console.warn(`[MIGE Time-Lapse] Failed to retrieve timeline for ${ideaAtomId}:`, error)
    return null
  }
}

/**
 * Retrieve idea snapshots with bitemporal filtering
 */
async function retrieveIdeaSnapshots(
  ideaAtomId: string,
  validTime?: Date
): Promise<IdeaSnapshot[]> {
  try {
    // Query CMC for all snapshots related to this idea
    // In a full implementation, this would use valid_time filtering
    const query = validTime 
      ? `idea_id:${ideaAtomId} valid_time:${validTime.toISOString()}`
      : `idea_id:${ideaAtomId} type:snapshot`
    
    const result = await cmcService.retrieveAtoms(query, 100) // Get up to 100 snapshots
    
    if (!result.success || !result.atoms) {
      return []
    }
    
    // Parse snapshots from atoms
    const snapshots: IdeaSnapshot[] = []
    
    for (const atom of result.atoms) {
      try {
        const snapshot = parseSnapshotFromAtom(atom)
        if (snapshot) {
          snapshots.push(snapshot)
        }
      } catch (parseError) {
        console.warn(`[MIGE Time-Lapse] Failed to parse snapshot from atom ${atom.id}:`, parseError)
      }
    }
    
    // Sort by timestamp (oldest first)
    return snapshots.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
  } catch (error) {
    console.warn('[MIGE Time-Lapse] Failed to retrieve snapshots:', error)
    return []
  }
}

/**
 * Parse snapshot from CMC atom
 */
function parseSnapshotFromAtom(atom: any): IdeaSnapshot | null {
  try {
    const metadata = atom.metadata || {}
    const content = typeof atom.content === 'string' 
      ? JSON.parse(atom.content) 
      : atom.content
    
    return {
      timestamp: new Date(metadata.timestamp || atom.timestamp || Date.now()),
      validTime: new Date(metadata.valid_time || metadata.timestamp || atom.timestamp || Date.now()),
      transactionTime: new Date(metadata.transaction_time || atom.timestamp || Date.now()),
      stage: (metadata.stage || content.stage || 'SEED') as MigeStage,
      contextState: {
        openFiles: metadata.openFiles || content.openFiles || [],
        activeConstraints: metadata.activeConstraints || content.activeConstraints || [],
        vifConfidence: metadata.vifConfidence || content.vifConfidence || 0.5,
        contextWeb: metadata.contextWeb || content.contextWeb,
        evidencePack: metadata.evidencePack || content.evidencePack
      },
      segAnchors: metadata.segAnchors || content.segAnchors || [],
      ideaAtomId: metadata.ideaId || content.ideaId || atom.id
    }
  } catch (error) {
    console.warn('[MIGE Time-Lapse] Failed to parse snapshot:', error)
    return null
  }
}

/**
 * Create snapshot for current idea state
 */
export async function createIdeaSnapshot(
  ideaAtomId: string,
  stage: MigeStage,
  contextState: IdeaSnapshot['contextState'],
  segAnchors: string[] = []
): Promise<{ success: boolean; snapshotId?: string; error?: string }> {
  try {
    const snapshot: Omit<IdeaSnapshot, 'timestamp' | 'validTime' | 'transactionTime'> = {
      stage,
      contextState,
      segAnchors,
      ideaAtomId
    }
    
    const now = new Date()
    const snapshotContent = JSON.stringify(snapshot)
    
    // Store snapshot in CMC with bitemporal metadata
    const result = await cmcService.storeAtom(
      snapshotContent,
      'event',
      {
        idea_id: 1.0,
        snapshot: 1.0,
        stage: getStageWeight(stage)
      },
      {
        ideaId: ideaAtomId,
        stage,
        timestamp: now.toISOString(),
        valid_time: now.toISOString(),
        transaction_time: now.toISOString(),
        openFiles: contextState.openFiles,
        activeConstraints: contextState.activeConstraints,
        vifConfidence: contextState.vifConfidence,
        segAnchors,
        type: 'idea_snapshot'
      }
    )
    
    if (result.success && result.atom_id) {
      return {
        success: true,
        snapshotId: result.atom_id
      }
    } else {
      return {
        success: false,
        error: result.error || 'Failed to store snapshot'
      }
    }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    }
  }
}

/**
 * Get stage weight for tagging
 */
function getStageWeight(stage: MigeStage): number {
  const weights = {
    'SEED': 0.25,
    'VISION_TENSOR': 0.5,
    'TRUNK_INDEX': 0.75,
    'DEPLOYED': 1.0
  }
  return weights[stage]
}

/**
 * Restore state from snapshot
 * Can accept either IdeaSnapshot or snapshot data from MigeTimelineData
 */
export async function restoreStateFromSnapshot(
  snapshot: IdeaSnapshot | {
    timestamp: Date
    stage: MigeStage
    contextState: IdeaSnapshot['contextState']
    segAnchors: string[]
    ideaAtomId: string
  }
): Promise<{
  success: boolean
  contextWeb?: ContextWeb
  evidencePack?: EvidencePack
  error?: string
}> {
  try {
    // Normalize snapshot data
    const normalizedSnapshot: IdeaSnapshot = 'validTime' in snapshot
      ? snapshot
      : {
          timestamp: snapshot.timestamp,
          validTime: snapshot.timestamp,
          transactionTime: snapshot.timestamp,
          stage: snapshot.stage,
          contextState: snapshot.contextState,
          segAnchors: snapshot.segAnchors,
          ideaAtomId: snapshot.ideaAtomId
        }
    
    // Restore context web if available
    let contextWeb = normalizedSnapshot.contextState.contextWeb
    
    // If not in snapshot, try to reconstruct from SEG anchors
    if (!contextWeb && normalizedSnapshot.segAnchors.length > 0) {
      contextWeb = await reconstructContextWebFromSEG(normalizedSnapshot.segAnchors)
    }
    
    // Restore evidence pack if available
    let evidencePack = normalizedSnapshot.contextState.evidencePack
    
    // If not in snapshot, try to reconstruct from CMC atoms
    if (!evidencePack) {
      evidencePack = await reconstructEvidencePackFromCMC(
        normalizedSnapshot.ideaAtomId, 
        normalizedSnapshot.timestamp
      )
    }
    
    return {
      success: true,
      contextWeb,
      evidencePack
    }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    }
  }
}

/**
 * Reconstruct context web from SEG anchors
 */
async function reconstructContextWebFromSEG(
  segAnchors: string[]
): Promise<ContextWeb | undefined> {
  try {
    // Query SEG for entities and relations using anchors
    const nodes: ContextWeb['nodes'] = []
    const edges: ContextWeb['edges'] = []
    
    for (const anchorId of segAnchors.slice(0, 20)) { // Limit to 20 anchors
      try {
        const segResult = await segService.synthesizeKnowledge(anchorId, 5)
        if (segResult.success && segResult.entities) {
          segResult.entities.forEach(entity => {
            nodes.push({
              id: entity.id,
              label: entity.label || entity.id,
              type: entity.type || 'concept',
              relevance: 0.5,
              importance: 0.5
            })
          })
        }
        if (segResult.success && segResult.relations) {
          segResult.relations.forEach(relation => {
            edges.push({
              from: relation.from,
              to: relation.to,
              type: relation.type || 'related',
              strength: 0.5
            })
          })
        }
      } catch (anchorError) {
        console.warn(`[MIGE Time-Lapse] Failed to query SEG for anchor ${anchorId}:`, anchorError)
      }
    }
    
    if (nodes.length > 0) {
      return {
        nodes,
        edges,
        metadata: {
          reconstructed: true,
          source: 'seg_anchors',
          anchorCount: segAnchors.length
        }
      }
    }
  } catch (error) {
    console.warn('[MIGE Time-Lapse] Failed to reconstruct context web from SEG:', error)
  }
  
  return undefined
}

/**
 * Reconstruct evidence pack from CMC atoms
 */
async function reconstructEvidencePackFromCMC(
  ideaAtomId: string,
  timestamp: Date
): Promise<EvidencePack | undefined> {
  try {
    // Query CMC for evidence atoms related to this idea at this timestamp
    const query = `idea_id:${ideaAtomId} type:evidence valid_time:${timestamp.toISOString()}`
    const result = await cmcService.retrieveAtoms(query, 50)
    
    if (result.success && result.atoms && result.atoms.length > 0) {
      const items = result.atoms.map(atom => ({
        id: atom.id,
        kind: (atom.metadata?.kind || 'doc_snippet') as 'file_snippet' | 'doc_snippet' | 'prior_msg' | 'test_output',
        excerpt: atom.content.substring(0, 200),
        location: atom.metadata?.location || '',
        trust: atom.metadata?.trust || 0.5,
        timestamp: new Date(atom.metadata?.timestamp || atom.timestamp || Date.now()),
        segAnchorId: atom.metadata?.segAnchorId
      }))
      
      return {
        items,
        overallTrust: items.reduce((sum, item) => sum + item.trust, 0) / items.length,
        completeness: items.length > 0 ? Math.min(1.0, items.length / 10) : 0
      }
    }
  } catch (error) {
    console.warn('[MIGE Time-Lapse] Failed to reconstruct evidence pack from CMC:', error)
  }
  
  return undefined
}

/**
 * Convert IdeaEvolutionTimeline to MigeTimelineData format
 */
export function convertToMigeTimelineData(
  timeline: IdeaEvolutionTimeline
): MigeTimelineData {
  return {
    ideaAtomId: timeline.ideaAtomId,
    snapshots: timeline.snapshots.map(snapshot => ({
      timestamp: snapshot.timestamp,
      stage: snapshot.stage,
      contextState: {
        openFiles: snapshot.contextState.openFiles,
        activeConstraints: snapshot.contextState.activeConstraints,
        vifConfidence: snapshot.contextState.vifConfidence
      },
      segAnchors: snapshot.segAnchors
    })),
    restoreState: async (snapshotIndex: number) => {
      if (snapshotIndex >= 0 && snapshotIndex < timeline.snapshots.length) {
        const snapshot = timeline.snapshots[snapshotIndex]
        const restored = await restoreStateFromSnapshot(snapshot)
        if (restored.success) {
          // State restoration logic would be handled by the UI component
          return
        }
      }
      throw new Error(`Invalid snapshot index: ${snapshotIndex}`)
    }
  }
}

