/**
 * LUCID Empire - 5-Layer Recursive Meta-Reasoning
 * 
 * Phase 1 Week 2: Thinking Mode Enhancements
 * 
 * Implements the 5 layers of lucidity:
 * 1. Thought Articulation - Force implicit reasoning explicit
 * 2. Reasoning Reflection - Reflect on prior reasoning
 * 3. Pattern Identification - Identify patterns in reasoning
 * 4. Temporal Lucidity - Observe evolution over time
 * 5. Infinite Lucidity - Recursive meta-cognition
 */

import { LLMService } from '../lucid-chat/llm/LLMService'
import { CMCService } from '../CMCService'
import { TCSService } from '../TCSService'
import { CASService } from '../CASService'
import { getActiveModel } from '../../config/modelRegistry'
import type { 
  RawUserTurn, 
  EnrichedContext, 
  EvidencePack, 
  ReasoningTrace,
  DraftResponse
} from '../../types/aetherChatTypes'

const llmService = new LLMService()
const cmcService = new CMCService()
const tcsService = new TCSService()
const casService = new CASService()

/**
 * Layer 1: Thought Articulation
 * Force implicit reasoning to become explicit
 */
export async function articulateThought(
  question: string,
  context: EnrichedContext,
  evidence: EvidencePack
): Promise<{
  articulation: any
  reasoningTrace: ReasoningTrace
}> {
  try {
    const model = getActiveModel('ask_explain', 'medium', 0.02, 2000)
    
    if (!model) {
      // Fallback: simple articulation
      return {
        articulation: {
          knowledge_domains: context.hhniResults.map(r => r.domain),
          key_concepts: context.hhniResults.map(r => r.title).filter(Boolean),
          reasoning_process: { approach: 'context-based', steps: [] },
          assumptions: [],
          confidence_assessment: { overall_κ: 0.7, confident_areas: [], uncertain_areas: [] },
          alternatives_considered: []
        },
        reasoningTrace: {
          id: `trace_${Date.now()}`,
          rawText: `Reasoning about: ${question}`,
          domains: context.hhniResults.map(r => r.domain),
          assumptions: [],
          confidenceSelfReport: 0.7,
          summary: 'Basic reasoning without LLM articulation'
        }
      }
    }

    const systemPrompt = `You are a reasoning system. BEFORE answering a question, you must explicitly articulate your reasoning process.

Respond with JSON:
{
  "knowledge_domains": ["domain1", "domain2"],
  "key_concepts": ["concept1", "concept2"],
  "reasoning_process": {
    "approach": "description of your approach",
    "steps": ["step1", "step2", "step3"],
    "dependencies": ["what depends on what"]
  },
  "assumptions": [
    {
      "assumption": "what you're assuming",
      "confidence": 0.8,
      "if_wrong": "what would break if this is wrong"
    }
  ],
  "confidence_assessment": {
    "overall_κ": 0.75,
    "confident_areas": ["where you're confident"],
    "uncertain_areas": ["where unsure"],
    "missing_information": ["what would increase confidence"]
  },
  "alternatives_considered": [
    {
      "alternative": "other approach",
      "why_chosen": "why your approach is better",
      "trade_offs": "trade-offs"
    }
  ]
}

THEN provide your actual answer informed by this articulation.`

    const userPrompt = `Question: "${question}"

Available context:
${context.hhniResults.slice(0, 3).map((r, i) => `${i + 1}. ${r.title || r.domain}: ${r.content.substring(0, 150)}...`).join('\n')}

Evidence items: ${evidence.items.length}

Articulate your reasoning process, then provide your answer.`

    const response = await llmService.chatCompletion({
      provider: model.provider as any,
      model: model.model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.7,
      maxTokens: 1500
    })

    // Parse JSON from response
    let articulation: any = {}
    try {
      const jsonMatch = response.text.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        articulation = JSON.parse(jsonMatch[0])
      }
    } catch (parseError) {
      console.warn('[LUCID Empire] Failed to parse articulation JSON:', parseError)
    }

    // Store reasoning trace in CMC
    const reasoningTrace: ReasoningTrace = {
      id: `trace_${Date.now()}`,
      rawText: response.text,
      domains: articulation.knowledge_domains || context.hhniResults.map(r => r.domain),
      assumptions: articulation.assumptions?.map((a: any) => a.assumption || a) || [],
      confidenceSelfReport: articulation.confidence_assessment?.overall_κ || 0.7,
      summary: `Articulated reasoning with ${articulation.key_concepts?.length || 0} key concepts`
    }

    // Store in CMC with proper modality (Phase 3 Week 13)
    try {
      await cmcService.storeAtom(
        JSON.stringify(articulation),
        'llm_reasoning_trace', // Proper modality for reasoning traces
        { reasoning: 1, trace: 1, lucid_empire: 1, layer: 1, articulation: 1 },
        {
          trace_id: reasoningTrace.id,
          question,
          confidence: articulation.confidence_assessment?.overall_κ || 0.7,
          timestamp: new Date().toISOString(),
          layer_type: 'thought_articulation'
        }
      )
    } catch (error) {
      console.warn('[LUCID Empire] Failed to store reasoning trace:', error)
    }

    return { articulation, reasoningTrace }
  } catch (error) {
    console.error('[LUCID Empire] Thought articulation failed:', error)
    // Fallback
    return {
      articulation: {},
      reasoningTrace: {
        id: `trace_${Date.now()}`,
        rawText: `Error articulating reasoning: ${error}`,
        domains: [],
        assumptions: [],
        confidenceSelfReport: 0.5,
        summary: 'Articulation failed'
      }
    }
  }
}

/**
 * Layer 2: Reasoning Reflection
 * Reflect on prior reasoning traces
 */
export async function reflectOnPriorReasoning(
  question: string,
  currentArticulation: any,
  sessionId: string
): Promise<{
  reflection: any
  evolvedReasoning: ReasoningTrace
}> {
  try {
    // Retrieve prior reasoning traces from CMC
    const priorTraces = await cmcService.retrieveAtoms(
      `reasoning trace session:${sessionId}`,
      3
    )

    if (!priorTraces.success || !priorTraces.atoms || priorTraces.atoms.length === 0) {
      // No prior reasoning to reflect on
      return {
        reflection: { has_prior_reasoning: false },
        evolvedReasoning: currentArticulation.reasoningTrace
      }
    }

    const model = getActiveModel('ask_explain', 'medium', 0.02, 2000)
    if (!model) {
      return {
        reflection: { has_prior_reasoning: true, prior_count: priorTraces.atoms.length },
        evolvedReasoning: currentArticulation.reasoningTrace
      }
    }

    const priorReasoningText = priorTraces.atoms
      .map((atom: any, i: number) => {
        const content = typeof atom.content === 'string' ? JSON.parse(atom.content) : atom.content
        return `Prior reasoning ${i + 1}:\n${JSON.stringify(content, null, 2)}`
      })
      .join('\n\n')

    const systemPrompt = `You are a reasoning system that reflects on your own prior reasoning.

Compare your current reasoning to your prior reasoning on similar topics:
1. COMPARE: How does this question relate to your prior thinking?
2. EVOLVE: How has your understanding changed or evolved?
3. CORRECT: What would you revise from your prior reasoning?
4. PATTERN: What patterns emerge in HOW you reason about this domain?

Respond with JSON:
{
  "comparison": "how current relates to prior",
  "evolution": "how understanding changed",
  "corrections": ["what to revise"],
  "patterns": ["patterns in reasoning"],
  "meta_insights": ["insights about your reasoning process"]
}`

    const userPrompt = `New Question: "${question}"

Your current reasoning:
${JSON.stringify(currentArticulation.articulation, null, 2)}

Your prior reasoning on this topic:
${priorReasoningText}

Reflect on how your reasoning has evolved.`

    const response = await llmService.chatCompletion({
      provider: model.provider as any,
      model: model.model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.7,
      maxTokens: 1000
    })

    let reflection: any = {}
    try {
      const jsonMatch = response.text.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        reflection = JSON.parse(jsonMatch[0])
      }
    } catch (parseError) {
      console.warn('[LUCID Empire] Failed to parse reflection JSON:', parseError)
    }

    // Create evolved reasoning trace
    const evolvedReasoning: ReasoningTrace = {
      id: `trace_${Date.now()}_evolved`,
      rawText: response.text,
      domains: currentArticulation.reasoningTrace.domains,
      assumptions: [
        ...currentArticulation.reasoningTrace.assumptions,
        ...(reflection.corrections || [])
      ],
      confidenceSelfReport: currentArticulation.reasoningTrace.confidenceSelfReport,
      summary: `Evolved reasoning with reflection on ${priorTraces.atoms.length} prior traces`
    }

    // Store reflection in CMC with proper modality (Phase 3 Week 13)
    try {
      await cmcService.storeAtom(
        JSON.stringify(reflection),
        'llm_reasoning_trace', // Proper modality for reasoning traces
        { reasoning: 1, reflection: 1, lucid_empire: 1, layer: 2, meta_reasoning: 1 },
        {
          trace_id: evolvedReasoning.id,
          reflects_on: priorTraces.atoms.map((a: any) => a.id),
          question,
          timestamp: new Date().toISOString(),
          layer_type: 'reasoning_reflection'
        }
      )
    } catch (error) {
      console.warn('[LUCID Empire] Failed to store reflection:', error)
    }

    return { reflection, evolvedReasoning }
  } catch (error) {
    console.error('[LUCID Empire] Reasoning reflection failed:', error)
    return {
      reflection: { error: 'Reflection failed' },
      evolvedReasoning: currentArticulation.reasoningTrace
    }
  }
}

/**
 * Layer 3: Pattern Identification
 * Identify patterns in reasoning across multiple traces
 */
export async function identifyReasoningPatterns(
  domain: string,
  sessionId: string
): Promise<{
  patterns: any
  insights: string[]
}> {
  try {
    // Retrieve all reasoning traces for this domain
    const traces = await cmcService.retrieveAtoms(
      `reasoning trace domain:${domain}`,
      10
    )

    if (!traces.success || !traces.atoms || traces.atoms.length < 2) {
      return {
        patterns: { insufficient_data: true },
        insights: []
      }
    }

    const model = getActiveModel('ask_explain', 'medium', 0.02, 2000)
    if (!model) {
      return {
        patterns: { trace_count: traces.atoms.length },
        insights: []
      }
    }

    const tracesText = traces.atoms
      .map((atom: any, i: number) => {
        const content = typeof atom.content === 'string' ? JSON.parse(atom.content) : atom.content
        return `Trace ${i + 1}:\n${JSON.stringify(content, null, 2)}`
      })
      .join('\n\n')

    const systemPrompt = `You are a pattern analysis system. Analyze reasoning traces to identify patterns.

Look for:
- Recurring assumptions
- Confidence patterns
- Alternative approaches considered
- Blind spots
- Domain expertise gaps

Respond with JSON:
{
  "recurring_assumptions": ["assumption1", "assumption2"],
  "confidence_patterns": "description of confidence trends",
  "blind_spots": ["area1", "area2"],
  "domain_expertise": {
    "strengths": ["strength1"],
    "gaps": ["gap1"]
  }
}`

    const userPrompt = `Domain: ${domain}

Reasoning traces:
${tracesText}

Identify patterns in how reasoning is done in this domain.`

    const response = await llmService.chatCompletion({
      provider: model.provider as any,
      model: model.model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.5,
      maxTokens: 800
    })

    let patterns: any = {}
    try {
      const jsonMatch = response.text.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        patterns = JSON.parse(jsonMatch[0])
      }
    } catch (parseError) {
      console.warn('[LUCID Empire] Failed to parse patterns JSON:', parseError)
    }

    const insights = [
      ...(patterns.recurring_assumptions || []),
      patterns.confidence_patterns,
      ...(patterns.blind_spots || [])
    ].filter(Boolean)

    return { patterns, insights }
  } catch (error) {
    console.error('[LUCID Empire] Pattern identification failed:', error)
    return {
      patterns: { error: 'Pattern identification failed' },
      insights: []
    }
  }
}

/**
 * Layer 4: Temporal Lucidity
 * Observe evolution over time
 */
export async function observeTemporalEvolution(
  domain: string,
  sessionId: string,
  dateRange?: [Date, Date]
): Promise<{
  evolution: any
  trends: string[]
}> {
  try {
    // Query timeline for reasoning evolution
    const traces = await cmcService.retrieveAtoms(
      `reasoning trace domain:${domain} session:${sessionId}`,
      20
    )

    if (!traces.success || !traces.atoms || traces.atoms.length < 2) {
      return {
        evolution: { insufficient_data: true },
        trends: []
      }
    }

    // Analyze confidence and complexity over time
    const evolutionData = traces.atoms.map((atom: any) => {
      const content = typeof atom.content === 'string' ? JSON.parse(atom.content) : atom.content
      return {
        timestamp: new Date(atom.metadata?.timestamp || Date.now()),
        confidence: content.confidence_assessment?.overall_κ || 0.7,
        concepts: content.key_concepts?.length || 0,
        assumptions: content.assumptions?.length || 0
      }
    }).sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())

    const trends: string[] = []
    
    if (evolutionData.length >= 2) {
      const first = evolutionData[0]
      const last = evolutionData[evolutionData.length - 1]
      
      if (last.confidence > first.confidence) {
        trends.push(`Confidence increased from ${(first.confidence * 100).toFixed(0)}% to ${(last.confidence * 100).toFixed(0)}%`)
      }
      
      if (last.concepts > first.concepts) {
        trends.push(`Reasoning complexity increased (${first.concepts} → ${last.concepts} concepts)`)
      }
    }

    const evolutionResult = {
      evolution: {
        data_points: evolutionData.length,
        confidence_trend: evolutionData.map(d => d.confidence),
        complexity_trend: evolutionData.map(d => d.concepts),
        time_span: evolutionData.length > 0 
          ? evolutionData[evolutionData.length - 1].timestamp.getTime() - evolutionData[0].timestamp.getTime()
          : 0
      },
      trends
    }

    // Store temporal evolution in CMC and TCS (Phase 3 Week 14)
    try {
      // Store in CMC
      await cmcService.storeAtom(
        JSON.stringify(evolutionResult),
        'llm_reasoning_trace',
        { reasoning: 1, temporal: 1, lucid_empire: 1, layer: 4, evolution: 1 },
        {
          domain,
          session_id: sessionId,
          trends_count: trends.length,
          timestamp: new Date().toISOString(),
          layer_type: 'temporal_lucidity'
        }
      )

      // Store in TCS for timeline tracking (Phase 3 Week 14)
      await tcsService.addEntry({
        prompt_id: `lucid_temporal_${Date.now()}`,
        user_input: `Temporal evolution analysis for domain: ${domain}`,
        context_state: {
          domain,
          trends: trends,
          confidence_trend: evolutionResult.evolution.confidence_trend,
          complexity_trend: evolutionResult.evolution.complexity_trend
        }
      })
    } catch (error) {
      console.warn('[LUCID Empire] Failed to store temporal evolution:', error)
    }

    return evolutionResult
  } catch (error) {
    console.error('[LUCID Empire] Temporal evolution observation failed:', error)
    return {
      evolution: { error: 'Evolution observation failed' },
      trends: []
    }
  }
}

/**
 * Layer 5: Infinite Lucidity
 * Recursive meta-cognition (with depth limit)
 */
export async function infiniteLucidity(
  question: string,
  currentReasoning: ReasoningTrace,
  depth: number = 1,
  maxDepth: number = 3
): Promise<{
  metaReasoning: any
  depth: number
}> {
  if (depth > maxDepth) {
    return {
      metaReasoning: { max_depth_reached: true },
      depth
    }
  }

  try {
    const model = getActiveModel('ask_explain', 'medium', 0.02, 2000)
    if (!model) {
      return {
        metaReasoning: { depth, no_model: true },
        depth
      }
    }

    const systemPrompt = `You are a meta-reasoning system. You reason about reasoning itself.

At depth ${depth}, you are observing reasoning at depth ${depth - 1}.

Questions to consider:
- Are the reasoning PATTERNS changing?
- Is the learning velocity increasing or plateauing?
- Am I converging on better reasoning or diverging?
- What meta-patterns emerge in how I observe reasoning?

Respond with JSON:
{
  "meta_observation": "what you observe about the reasoning",
  "pattern_changes": ["pattern1", "pattern2"],
  "learning_velocity": "increasing | plateauing | decreasing",
  "convergence": "converging | diverging | stable",
  "meta_patterns": ["pattern1", "pattern2"]
}`

    const userPrompt = `Question: "${question}"

Reasoning at depth ${depth - 1}:
${JSON.stringify(currentReasoning, null, 2)}

Observe this reasoning. What patterns do you see in HOW the reasoning was done?`

    const response = await llmService.chatCompletion({
      provider: model.provider as any,
      model: model.model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.6,
      maxTokens: 800
    })

    let metaReasoning: any = {}
    try {
      const jsonMatch = response.text.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        metaReasoning = JSON.parse(jsonMatch[0])
      }
    } catch (parseError) {
      console.warn('[LUCID Empire] Failed to parse meta-reasoning JSON:', parseError)
    }

    // Store meta-reasoning in CMC (Phase 3 Week 14)
    try {
      await cmcService.storeAtom(
        JSON.stringify(metaReasoning),
        'llm_reasoning_trace',
        { reasoning: 1, meta: 1, lucid_empire: 1, layer: 5, infinite: 1 },
        {
          trace_id: currentReasoning.id,
          question,
          depth,
          timestamp: new Date().toISOString(),
          layer_type: 'infinite_lucidity'
        }
      )

      // CAS introspection for infinite lucidity (Phase 3 Week 14)
      if (depth === 1) {
        try {
          const casMetrics = await casService.getMetrics()
          if (casMetrics.success && casMetrics.metrics) {
            metaReasoning.cas_introspection = {
              cognitive_load: casMetrics.metrics.cognitiveLoad,
              attention_span: casMetrics.metrics.attentionSpan,
              drift_score: casMetrics.metrics.driftScore
            }
          }
        } catch (casError) {
          console.warn('[LUCID Empire] CAS introspection failed:', casError)
        }
      }
    } catch (error) {
      console.warn('[LUCID Empire] Failed to store meta-reasoning:', error)
    }

    // Recursively go deeper if not at max depth
    if (depth < maxDepth && metaReasoning.meta_patterns && metaReasoning.meta_patterns.length > 0) {
      const deeperReasoning: ReasoningTrace = {
        id: `${currentReasoning.id}_meta_${depth}`,
        rawText: response.text,
        domains: currentReasoning.domains,
        assumptions: [...currentReasoning.assumptions, ...(metaReasoning.meta_patterns || [])],
        confidenceSelfReport: currentReasoning.confidenceSelfReport,
        summary: `Meta-reasoning at depth ${depth}`
      }

      const deeper = await infiniteLucidity(question, deeperReasoning, depth + 1, maxDepth)
      return {
        metaReasoning: {
          ...metaReasoning,
          deeper: deeper.metaReasoning
        },
        depth: deeper.depth
      }
    }

    return { metaReasoning, depth }
  } catch (error) {
    console.error('[LUCID Empire] Infinite lucidity failed:', error)
    return {
      metaReasoning: { error: 'Infinite lucidity failed', depth },
      depth
    }
  }
}

/**
 * Run complete LUCID Empire 5-layer reasoning
 */
export async function runLucidEmpireReasoning(
  question: string,
  context: EnrichedContext,
  evidence: EvidencePack,
  sessionId: string
): Promise<{
  reasoningTrace: ReasoningTrace
  draft: DraftResponse
  lucidLayers: {
    layer1: any
    layer2: any
    layer3: any
    layer4: any
    layer5: any
  }
}> {
  // Layer 1: Thought Articulation
  const layer1 = await articulateThought(question, context, evidence)
  
  // Layer 2: Reasoning Reflection
  const layer2 = await reflectOnPriorReasoning(question, layer1, sessionId)
  
  // Layer 3: Pattern Identification (if we have a domain)
  const domain = context.hhniResults[0]?.domain || 'general'
  const layer3 = await identifyReasoningPatterns(domain, sessionId)
  
  // Layer 4: Temporal Lucidity
  const layer4 = await observeTemporalEvolution(domain, sessionId)
  
  // Layer 5: Infinite Lucidity (with depth limit)
  const layer5 = await infiniteLucidity(question, layer2.evolvedReasoning, 1, 3)
  
  // Build final reasoning trace
  const finalReasoningTrace: ReasoningTrace = {
    id: layer2.evolvedReasoning.id,
    rawText: layer2.evolvedReasoning.rawText,
    domains: layer2.evolvedReasoning.domains,
    assumptions: layer2.evolvedReasoning.assumptions,
    confidenceSelfReport: layer2.evolvedReasoning.confidenceSelfReport,
    summary: `LUCID Empire reasoning: ${layer1.reasoningTrace.summary} | Patterns: ${layer3.insights.length} | Evolution: ${layer4.trends.length} trends`
  }
  
  // Generate draft response
  const draft: DraftResponse = {
    userFacingText: `Based on my reasoning process:\n\n${layer1.reasoningTrace.summary}\n\n${layer2.reflection.evolution || ''}\n\nAnswer: [Generated from reasoning]`,
    actions: [],
    rationale: `Reasoned through ${layer1.reasoningTrace.domains.length} domains with ${layer3.insights.length} pattern insights`,
    citedEvidenceIds: evidence.items.slice(0, 5).map(item => item.id),
    selfEstimatedConfidence: finalReasoningTrace.confidenceSelfReport
  }
  
  return {
    reasoningTrace: finalReasoningTrace,
    draft,
    lucidLayers: {
      layer1: layer1.articulation,
      layer2: layer2.reflection,
      layer3: layer3.patterns,
      layer4: layer4.evolution,
      layer5: layer5.metaReasoning
    }
  }
}

