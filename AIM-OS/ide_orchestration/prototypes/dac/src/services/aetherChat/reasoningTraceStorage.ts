/**
 * Enhanced Reasoning Trace Storage Service
 * Stores all 5 LUCID Empire layers with cross-session linking
 * 
 * Phase 1 Week 2: Thinking Mode Enhancements (Task 3)
 */

import { CMCService } from '../CMCService'
import { TCSService } from '../TCSService'
import type { 
  ReasoningTrace,
  RawUserTurn
} from '../../types/aetherChatTypes'

const cmcService = new CMCService()
const tcsService = new TCSService()

/**
 * Complete LUCID Empire reasoning trace structure
 */
export interface LucidEmpireTrace {
  traceId: string
  sessionId: string
  messageId?: string
  question: string
  timestamp: Date
  
  // All 5 layers
  layer1: {
    articulation: any
    reasoningTrace: ReasoningTrace
    atomId?: string
  }
  layer2: {
    reflection: any
    evolvedReasoning: ReasoningTrace
    atomId?: string
    reflectsOn?: string[] // Atom IDs of prior traces
  }
  layer3: {
    patterns: any
    insights: string[]
    atomId?: string
    domain?: string
  }
  layer4: {
    evolution: any
    trends: string[]
    atomId?: string
  }
  layer5: {
    metaReasoning: any
    depth: number
    atomId?: string
  }
  
  // Final synthesized trace
  finalReasoningTrace: ReasoningTrace
  finalAtomId?: string
  
  // Cross-session linking
  relatedTraces?: string[] // Trace IDs from other sessions
  domain?: string
  topics?: string[]
}

/**
 * Store complete LUCID Empire trace with all 5 layers
 */
export async function storeLucidEmpireTrace(
  trace: LucidEmpireTrace
): Promise<{
  success: boolean
  atomIds: {
    layer1?: string
    layer2?: string
    layer3?: string
    layer4?: string
    layer5?: string
    final?: string
  }
  error?: string
}> {
  const atomIds: {
    layer1?: string
    layer2?: string
    layer3?: string
    layer4?: string
    layer5?: string
    final?: string
  } = {}
  
  try {
    // Build tags for all layers
    const baseTags = [
      'reasoning',
      'trace',
      'lucid_empire',
      `session:${trace.sessionId}`,
      trace.domain ? `domain:${trace.domain}` : 'domain:general'
    ]
    
    // Store Layer 1: Thought Articulation
    if (trace.layer1.articulation) {
      try {
        const layer1Atom = await cmcService.storeAtom(
          JSON.stringify({
            layer: 1,
            layerName: 'thought_articulation',
            articulation: trace.layer1.articulation,
            reasoningTrace: trace.layer1.reasoningTrace,
            traceId: trace.traceId,
            question: trace.question
          }),
          'text',
          {
            ...baseTags.reduce((acc, tag) => ({ ...acc, [tag]: 1 }), {}),
            layer: 1,
            thought_articulation: 1
          },
          {
            traceId: trace.traceId,
            sessionId: trace.sessionId,
            messageId: trace.messageId,
            layer: '1',
            layerName: 'thought_articulation',
            question: trace.question,
            confidence: trace.layer1.reasoningTrace.confidenceSelfReport.toString(),
            timestamp: trace.timestamp.toISOString(),
            domains: trace.layer1.reasoningTrace.domains.join(',')
          }
        )
        atomIds.layer1 = layer1Atom.id
        trace.layer1.atomId = layer1Atom.id
      } catch (error) {
        console.warn('[ReasoningTraceStorage] Failed to store Layer 1:', error)
      }
    }
    
    // Store Layer 2: Reasoning Reflection
    if (trace.layer2.reflection) {
      try {
        const layer2Atom = await cmcService.storeAtom(
          JSON.stringify({
            layer: 2,
            layerName: 'reasoning_reflection',
            reflection: trace.layer2.reflection,
            evolvedReasoning: trace.layer2.evolvedReasoning,
            traceId: trace.traceId,
            question: trace.question,
            reflectsOn: trace.layer2.reflectsOn || []
          }),
          'text',
          {
            ...baseTags.reduce((acc, tag) => ({ ...acc, [tag]: 1 }), {}),
            layer: 2,
            reasoning_reflection: 1
          },
          {
            traceId: trace.traceId,
            sessionId: trace.sessionId,
            messageId: trace.messageId,
            layer: '2',
            layerName: 'reasoning_reflection',
            question: trace.question,
            confidence: trace.layer2.evolvedReasoning.confidenceSelfReport.toString(),
            timestamp: trace.timestamp.toISOString(),
            reflectsOn: (trace.layer2.reflectsOn || []).join(','),
            domains: trace.layer2.evolvedReasoning.domains.join(',')
          }
        )
        atomIds.layer2 = layer2Atom.id
        trace.layer2.atomId = layer2Atom.id
        
        // Link to Layer 1
        if (atomIds.layer1) {
          await linkTraces(atomIds.layer1, atomIds.layer2, 'layer1_to_layer2')
        }
      } catch (error) {
        console.warn('[ReasoningTraceStorage] Failed to store Layer 2:', error)
      }
    }
    
    // Store Layer 3: Pattern Identification
    if (trace.layer3.patterns) {
      try {
        const layer3Atom = await cmcService.storeAtom(
          JSON.stringify({
            layer: 3,
            layerName: 'pattern_identification',
            patterns: trace.layer3.patterns,
            insights: trace.layer3.insights,
            traceId: trace.traceId,
            domain: trace.layer3.domain || trace.domain
          }),
          'text',
          {
            ...baseTags.reduce((acc, tag) => ({ ...acc, [tag]: 1 }), {}),
            layer: 3,
            pattern_identification: 1
          },
          {
            traceId: trace.traceId,
            sessionId: trace.sessionId,
            messageId: trace.messageId,
            layer: '3',
            layerName: 'pattern_identification',
            domain: trace.layer3.domain || trace.domain || 'general',
            timestamp: trace.timestamp.toISOString(),
            insightCount: trace.layer3.insights.length.toString()
          }
        )
        atomIds.layer3 = layer3Atom.id
        trace.layer3.atomId = layer3Atom.id
        
        // Link to Layer 2
        if (atomIds.layer2) {
          await linkTraces(atomIds.layer2, atomIds.layer3, 'layer2_to_layer3')
        }
      } catch (error) {
        console.warn('[ReasoningTraceStorage] Failed to store Layer 3:', error)
      }
    }
    
    // Store Layer 4: Temporal Lucidity
    if (trace.layer4.evolution) {
      try {
        const layer4Atom = await cmcService.storeAtom(
          JSON.stringify({
            layer: 4,
            layerName: 'temporal_lucidity',
            evolution: trace.layer4.evolution,
            trends: trace.layer4.trends,
            traceId: trace.traceId,
            domain: trace.domain
          }),
          'text',
          {
            ...baseTags.reduce((acc, tag) => ({ ...acc, [tag]: 1 }), {}),
            layer: 4,
            temporal_lucidity: 1
          },
          {
            traceId: trace.traceId,
            sessionId: trace.sessionId,
            messageId: trace.messageId,
            layer: '4',
            layerName: 'temporal_lucidity',
            domain: trace.domain || 'general',
            timestamp: trace.timestamp.toISOString(),
            trendCount: trace.layer4.trends.length.toString()
          }
        )
        atomIds.layer4 = layer4Atom.id
        trace.layer4.atomId = layer4Atom.id
        
        // Link to Layer 3
        if (atomIds.layer3) {
          await linkTraces(atomIds.layer3, atomIds.layer4, 'layer3_to_layer4')
        }
      } catch (error) {
        console.warn('[ReasoningTraceStorage] Failed to store Layer 4:', error)
      }
    }
    
    // Store Layer 5: Infinite Lucidity
    if (trace.layer5.metaReasoning) {
      try {
        const layer5Atom = await cmcService.storeAtom(
          JSON.stringify({
            layer: 5,
            layerName: 'infinite_lucidity',
            metaReasoning: trace.layer5.metaReasoning,
            depth: trace.layer5.depth,
            traceId: trace.traceId
          }),
          'text',
          {
            ...baseTags.reduce((acc, tag) => ({ ...acc, [tag]: 1 }), {}),
            layer: 5,
            infinite_lucidity: 1
          },
          {
            traceId: trace.traceId,
            sessionId: trace.sessionId,
            messageId: trace.messageId,
            layer: '5',
            layerName: 'infinite_lucidity',
            depth: trace.layer5.depth.toString(),
            timestamp: trace.timestamp.toISOString()
          }
        )
        atomIds.layer5 = layer5Atom.id
        trace.layer5.atomId = layer5Atom.id
        
        // Link to Layer 4
        if (atomIds.layer4) {
          await linkTraces(atomIds.layer4, atomIds.layer5, 'layer4_to_layer5')
        }
      } catch (error) {
        console.warn('[ReasoningTraceStorage] Failed to store Layer 5:', error)
      }
    }
    
    // Store final synthesized trace
    if (trace.finalReasoningTrace) {
      try {
        const finalAtom = await cmcService.storeAtom(
          JSON.stringify({
            traceId: trace.traceId,
            finalReasoningTrace: trace.finalReasoningTrace,
            layerAtomIds: {
              layer1: atomIds.layer1,
              layer2: atomIds.layer2,
              layer3: atomIds.layer3,
              layer4: atomIds.layer4,
              layer5: atomIds.layer5
            },
            question: trace.question,
            relatedTraces: trace.relatedTraces || []
          }),
          'text',
          {
            ...baseTags.reduce((acc, tag) => ({ ...acc, [tag]: 1 }), {}),
            final: 1,
            synthesized: 1
          },
          {
            traceId: trace.traceId,
            sessionId: trace.sessionId,
            messageId: trace.messageId,
            layer: 'final',
            question: trace.question,
            confidence: trace.finalReasoningTrace.confidenceSelfReport.toString(),
            timestamp: trace.timestamp.toISOString(),
            domains: trace.finalReasoningTrace.domains.join(','),
            relatedTraces: (trace.relatedTraces || []).join(','),
            layer1AtomId: atomIds.layer1 || '',
            layer2AtomId: atomIds.layer2 || '',
            layer3AtomId: atomIds.layer3 || '',
            layer4AtomId: atomIds.layer4 || '',
            layer5AtomId: atomIds.layer5 || ''
          }
        )
        atomIds.final = finalAtom.id
        trace.finalAtomId = finalAtom.id
        
        // Link final to all layers
        if (atomIds.layer1) await linkTraces(atomIds.layer1, finalAtom.id, 'layer1_to_final')
        if (atomIds.layer2) await linkTraces(atomIds.layer2, finalAtom.id, 'layer2_to_final')
        if (atomIds.layer3) await linkTraces(atomIds.layer3, finalAtom.id, 'layer3_to_final')
        if (atomIds.layer4) await linkTraces(atomIds.layer4, finalAtom.id, 'layer4_to_final')
        if (atomIds.layer5) await linkTraces(atomIds.layer5, finalAtom.id, 'layer5_to_final')
      } catch (error) {
        console.warn('[ReasoningTraceStorage] Failed to store final trace:', error)
      }
    }
    
    // Store TCS timeline entry for trace completion
    try {
      await tcsService.addEntry(
        'lucid_empire_trace_complete',
        `Completed LUCID Empire reasoning trace: ${trace.traceId}`,
        {
          traceId: trace.traceId,
          sessionId: trace.sessionId,
          messageId: trace.messageId,
          question: trace.question,
          domain: trace.domain || 'general',
          confidence: trace.finalReasoningTrace.confidenceSelfReport.toString(),
          layerCount: '5',
          finalAtomId: atomIds.final || ''
        }
      )
    } catch (error) {
      console.warn('[ReasoningTraceStorage] Failed to store TCS entry:', error)
    }
    
    return { success: true, atomIds }
  } catch (error) {
    console.error('[ReasoningTraceStorage] Failed to store LUCID Empire trace:', error)
    return {
      success: false,
      atomIds,
      error: error instanceof Error ? error.message : 'Unknown error'
    }
  }
}

/**
 * Link two traces in CMC (for cross-layer and cross-session linking)
 */
async function linkTraces(
  fromAtomId: string,
  toAtomId: string,
  relationType: string
): Promise<void> {
  try {
    // Store a relationship atom
    await cmcService.storeAtom(
      JSON.stringify({
        relationType,
        fromAtomId,
        toAtomId,
        timestamp: new Date().toISOString()
      }),
      'text',
      {
        trace_link: 1,
        relation: 1
      },
      {
        fromAtomId,
        toAtomId,
        relationType,
        timestamp: new Date().toISOString()
      }
    )
  } catch (error) {
    console.warn('[ReasoningTraceStorage] Failed to link traces:', error)
  }
}

/**
 * Retrieve related traces across sessions
 */
export async function retrieveRelatedTraces(
  traceId: string,
  domain?: string,
  sessionId?: string
): Promise<{
  success: boolean
  traces: Array<{
    traceId: string
    sessionId: string
    question: string
    timestamp: Date
    confidence: number
    atomId: string
  }>
  error?: string
}> {
  try {
    const query = domain 
      ? `reasoning trace domain:${domain}`
      : sessionId
      ? `reasoning trace session:${sessionId}`
      : `reasoning trace`
    
    const result = await cmcService.retrieveAtoms(query, 10)
    
    if (!result.success || !result.atoms) {
      return { success: false, traces: [], error: 'Failed to retrieve traces' }
    }
    
    const traces = result.atoms
      .filter(atom => {
        // Exclude the current trace
        const content = typeof atom.content === 'string' 
          ? JSON.parse(atom.content) 
          : atom.content
        return content.traceId !== traceId
      })
      .map(atom => {
        const content = typeof atom.content === 'string' 
          ? JSON.parse(atom.content) 
          : atom.content
        
        return {
          traceId: content.traceId || atom.id,
          sessionId: atom.metadata?.sessionId || 'unknown',
          question: content.question || atom.metadata?.question || '',
          timestamp: new Date(atom.metadata?.timestamp || Date.now()),
          confidence: parseFloat(atom.metadata?.confidence || '0.7'),
          atomId: atom.id
        }
      })
    
    return { success: true, traces }
  } catch (error) {
    console.error('[ReasoningTraceStorage] Failed to retrieve related traces:', error)
    return {
      success: false,
      traces: [],
      error: error instanceof Error ? error.message : 'Unknown error'
    }
  }
}

/**
 * Retrieve complete LUCID Empire trace by trace ID
 */
export async function retrieveLucidEmpireTrace(
  traceId: string
): Promise<{
  success: boolean
  trace?: LucidEmpireTrace
  error?: string
}> {
  try {
    // Retrieve final trace first
    const finalResult = await cmcService.retrieveAtoms(
      `reasoning trace final traceId:${traceId}`,
      1
    )
    
    if (!finalResult.success || !finalResult.atoms || finalResult.atoms.length === 0) {
      return { success: false, error: 'Trace not found' }
    }
    
    const finalAtom = finalResult.atoms[0]
    const finalContent = typeof finalAtom.content === 'string'
      ? JSON.parse(finalAtom.content)
      : finalAtom.content
    
    // Retrieve all layer atoms
    const layerAtomIds = finalContent.layerAtomIds || {}
    
    const trace: LucidEmpireTrace = {
      traceId: finalContent.traceId || traceId,
      sessionId: finalAtom.metadata?.sessionId || '',
      messageId: finalAtom.metadata?.messageId,
      question: finalContent.question || finalAtom.metadata?.question || '',
      timestamp: new Date(finalAtom.metadata?.timestamp || Date.now()),
      layer1: { articulation: {}, reasoningTrace: {} as ReasoningTrace },
      layer2: { reflection: {}, evolvedReasoning: {} as ReasoningTrace },
      layer3: { patterns: {}, insights: [] },
      layer4: { evolution: {}, trends: [] },
      layer5: { metaReasoning: {}, depth: 0 },
      finalReasoningTrace: finalContent.finalReasoningTrace || {} as ReasoningTrace,
      finalAtomId: finalAtom.id,
      domain: finalAtom.metadata?.domain,
      relatedTraces: finalContent.relatedTraces || []
    }
    
    // Retrieve each layer
    if (layerAtomIds.layer1) {
      const layer1Result = await cmcService.retrieveAtoms(`atom:${layerAtomIds.layer1}`, 1)
      if (layer1Result.success && layer1Result.atoms && layer1Result.atoms.length > 0) {
        const layer1Content = typeof layer1Result.atoms[0].content === 'string'
          ? JSON.parse(layer1Result.atoms[0].content)
          : layer1Result.atoms[0].content
        trace.layer1 = {
          articulation: layer1Content.articulation,
          reasoningTrace: layer1Content.reasoningTrace,
          atomId: layerAtomIds.layer1
        }
      }
    }
    
    if (layerAtomIds.layer2) {
      const layer2Result = await cmcService.retrieveAtoms(`atom:${layerAtomIds.layer2}`, 1)
      if (layer2Result.success && layer2Result.atoms && layer2Result.atoms.length > 0) {
        const layer2Content = typeof layer2Result.atoms[0].content === 'string'
          ? JSON.parse(layer2Result.atoms[0].content)
          : layer2Result.atoms[0].content
        trace.layer2 = {
          reflection: layer2Content.reflection,
          evolvedReasoning: layer2Content.evolvedReasoning,
          atomId: layerAtomIds.layer2,
          reflectsOn: layer2Content.reflectsOn
        }
      }
    }
    
    if (layerAtomIds.layer3) {
      const layer3Result = await cmcService.retrieveAtoms(`atom:${layerAtomIds.layer3}`, 1)
      if (layer3Result.success && layer3Result.atoms && layer3Result.atoms.length > 0) {
        const layer3Content = typeof layer3Result.atoms[0].content === 'string'
          ? JSON.parse(layer3Result.atoms[0].content)
          : layer3Result.atoms[0].content
        trace.layer3 = {
          patterns: layer3Content.patterns,
          insights: layer3Content.insights || [],
          atomId: layerAtomIds.layer3,
          domain: layer3Content.domain
        }
      }
    }
    
    if (layerAtomIds.layer4) {
      const layer4Result = await cmcService.retrieveAtoms(`atom:${layerAtomIds.layer4}`, 1)
      if (layer4Result.success && layer4Result.atoms && layer4Result.atoms.length > 0) {
        const layer4Content = typeof layer4Result.atoms[0].content === 'string'
          ? JSON.parse(layer4Result.atoms[0].content)
          : layer4Result.atoms[0].content
        trace.layer4 = {
          evolution: layer4Content.evolution,
          trends: layer4Content.trends || [],
          atomId: layerAtomIds.layer4
        }
      }
    }
    
    if (layerAtomIds.layer5) {
      const layer5Result = await cmcService.retrieveAtoms(`atom:${layerAtomIds.layer5}`, 1)
      if (layer5Result.success && layer5Result.atoms && layer5Result.atoms.length > 0) {
        const layer5Content = typeof layer5Result.atoms[0].content === 'string'
          ? JSON.parse(layer5Result.atoms[0].content)
          : layer5Result.atoms[0].content
        trace.layer5 = {
          metaReasoning: layer5Content.metaReasoning,
          depth: layer5Content.depth || 0,
          atomId: layerAtomIds.layer5
        }
      }
    }
    
    return { success: true, trace }
  } catch (error) {
    console.error('[ReasoningTraceStorage] Failed to retrieve LUCID Empire trace:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    }
  }
}

