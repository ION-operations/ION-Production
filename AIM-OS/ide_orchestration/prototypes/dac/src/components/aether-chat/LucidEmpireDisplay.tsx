/**
 * LUCID Empire Display Component
 * Displays the 5-layer recursive meta-reasoning trace
 * 
 * Phase 3 Week 13-14: LUCID Empire Integration
 */

import React, { useState } from 'react'
import { Brain, ChevronDown, ChevronUp, Layers, TrendingUp, Infinity, Clock, Search } from 'lucide-react'
import type { ReasoningTrace } from '../../types/aetherChatTypes'

// LUCID Layers type (matches ThinkingResult.lucidLayers)
export type LucidLayers = {
  layer1: any // Thought Articulation
  layer2: any // Reasoning Reflection
  layer3: any // Pattern Identification
  layer4: any // Temporal Lucidity
  layer5: any // Infinite Lucidity
}

export interface LucidEmpireDisplayProps {
  reasoningTrace: ReasoningTrace
  lucidLayers?: {
    layer1?: any
    layer2?: any
    layer3?: any
    layer4?: any
    layer5?: any
  }
  onExploreLayer?: (layer: number, data: any) => void
  className?: string
}

export const LucidEmpireDisplay: React.FC<LucidEmpireDisplayProps> = ({
  reasoningTrace,
  lucidLayers,
  onExploreLayer,
  className = ''
}) => {
  const [expandedLayers, setExpandedLayers] = useState<Set<number>>(new Set([1]))
  const [selectedLayer, setSelectedLayer] = useState<number | null>(null)

  const toggleLayer = (layer: number) => {
    const updated = new Set(expandedLayers)
    if (updated.has(layer)) {
      updated.delete(layer)
    } else {
      updated.add(layer)
    }
    setExpandedLayers(updated)
  }

  const handleLayerClick = (layer: number, data: any) => {
    setSelectedLayer(layer)
    onExploreLayer?.(layer, data)
  }

  const getLayerInfo = (layer: number) => {
    switch (layer) {
      case 1:
        return {
          name: 'Thought Articulation',
          icon: <Brain className="w-4 h-4" />,
          description: 'Force implicit reasoning to become explicit',
          color: 'text-blue-400 border-blue-500/30 bg-blue-500/10'
        }
      case 2:
        return {
          name: 'Reasoning Reflection',
          icon: <Layers className="w-4 h-4" />,
          description: 'Reflect on prior reasoning traces',
          color: 'text-purple-400 border-purple-500/30 bg-purple-500/10'
        }
      case 3:
        return {
          name: 'Pattern Identification',
          icon: <Search className="w-4 h-4" />,
          description: 'Identify patterns in reasoning across traces',
          color: 'text-green-400 border-green-500/30 bg-green-500/10'
        }
      case 4:
        return {
          name: 'Temporal Lucidity',
          icon: <Clock className="w-4 h-4" />,
          description: 'Observe evolution over time',
          color: 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10'
        }
      case 5:
        return {
          name: 'Infinite Lucidity',
          icon: <Infinity className="w-4 h-4" />,
          description: 'Recursive meta-cognition',
          color: 'text-pink-400 border-pink-500/30 bg-pink-500/10'
        }
      default:
        return {
          name: 'Unknown Layer',
          icon: <Brain className="w-4 h-4" />,
          description: '',
          color: 'text-gray-400 border-gray-500/30 bg-gray-500/10'
        }
    }
  }

  const renderLayerContent = (layer: number, data: any) => {
    if (!data || Object.keys(data).length === 0) {
      return (
        <div className="text-xs text-gray-500 italic p-2">
          No data available for this layer
        </div>
      )
    }

    switch (layer) {
      case 1: // Thought Articulation
        return (
          <div className="space-y-2 text-sm">
            {data.knowledge_domains && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Knowledge Domains</div>
                <div className="flex flex-wrap gap-1">
                  {data.knowledge_domains.map((domain: string, i: number) => (
                    <span key={i} className="px-2 py-0.5 bg-gray-800 rounded text-xs text-gray-300">
                      {domain}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {data.key_concepts && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Key Concepts</div>
                <div className="flex flex-wrap gap-1">
                  {data.key_concepts.slice(0, 5).map((concept: string, i: number) => (
                    <span key={i} className="px-2 py-0.5 bg-gray-800 rounded text-xs text-gray-300">
                      {concept}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {data.reasoning_process && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Reasoning Process</div>
                <div className="text-gray-300 text-xs">
                  <div className="font-medium">{data.reasoning_process.approach}</div>
                  {data.reasoning_process.steps && (
                    <ul className="list-disc list-inside mt-1 space-y-0.5">
                      {data.reasoning_process.steps.slice(0, 3).map((step: string, i: number) => (
                        <li key={i}>{step}</li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            )}
            {data.confidence_assessment && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Confidence Assessment</div>
                <div className="text-gray-300 text-xs">
                  Overall: {(data.confidence_assessment.overall_κ * 100).toFixed(0)}%
                  {data.confidence_assessment.confident_areas && (
                    <div className="mt-1">
                      Confident: {data.confidence_assessment.confident_areas.join(', ')}
                    </div>
                  )}
                  {data.confidence_assessment.uncertain_areas && (
                    <div className="mt-1 text-yellow-400">
                      Uncertain: {data.confidence_assessment.uncertain_areas.join(', ')}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )

      case 2: // Reasoning Reflection
        return (
          <div className="space-y-2 text-sm">
            {data.comparison && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Comparison</div>
                <div className="text-gray-300 text-xs">{data.comparison}</div>
              </div>
            )}
            {data.evolution && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Evolution</div>
                <div className="text-gray-300 text-xs">{data.evolution}</div>
              </div>
            )}
            {data.corrections && data.corrections.length > 0 && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Corrections</div>
                <ul className="list-disc list-inside text-xs text-gray-300 space-y-0.5">
                  {data.corrections.map((correction: string, i: number) => (
                    <li key={i}>{correction}</li>
                  ))}
                </ul>
              </div>
            )}
            {data.patterns && data.patterns.length > 0 && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Patterns</div>
                <div className="flex flex-wrap gap-1">
                  {data.patterns.map((pattern: string, i: number) => (
                    <span key={i} className="px-2 py-0.5 bg-gray-800 rounded text-xs text-gray-300">
                      {pattern}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )

      case 3: // Pattern Identification
        return (
          <div className="space-y-2 text-sm">
            {data.recurring_assumptions && data.recurring_assumptions.length > 0 && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Recurring Assumptions</div>
                <ul className="list-disc list-inside text-xs text-gray-300 space-y-0.5">
                  {data.recurring_assumptions.map((assumption: string, i: number) => (
                    <li key={i}>{assumption}</li>
                  ))}
                </ul>
              </div>
            )}
            {data.confidence_patterns && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Confidence Patterns</div>
                <div className="text-gray-300 text-xs">{data.confidence_patterns}</div>
              </div>
            )}
            {data.blind_spots && data.blind_spots.length > 0 && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Blind Spots</div>
                <ul className="list-disc list-inside text-xs text-yellow-300 space-y-0.5">
                  {data.blind_spots.map((spot: string, i: number) => (
                    <li key={i}>{spot}</li>
                  ))}
                </ul>
              </div>
            )}
            {data.domain_expertise && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Domain Expertise</div>
                <div className="text-gray-300 text-xs">
                  {data.domain_expertise.strengths && (
                    <div className="mb-1">
                      <span className="text-green-400">Strengths:</span> {data.domain_expertise.strengths.join(', ')}
                    </div>
                  )}
                  {data.domain_expertise.gaps && (
                    <div>
                      <span className="text-red-400">Gaps:</span> {data.domain_expertise.gaps.join(', ')}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )

      case 4: // Temporal Lucidity
        return (
          <div className="space-y-2 text-sm">
            {data.data_points && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Data Points</div>
                <div className="text-gray-300 text-xs">{data.data_points} reasoning traces analyzed</div>
              </div>
            )}
            {data.confidence_trend && data.confidence_trend.length > 0 && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Confidence Trend</div>
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-green-400" />
                  <div className="text-gray-300 text-xs">
                    {data.confidence_trend.length > 1 && (
                      <span>
                        {(data.confidence_trend[0] * 100).toFixed(0)}% → {(data.confidence_trend[data.confidence_trend.length - 1] * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                </div>
              </div>
            )}
            {data.complexity_trend && data.complexity_trend.length > 0 && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Complexity Trend</div>
                <div className="text-gray-300 text-xs">
                  {data.complexity_trend.length > 1 && (
                    <span>
                      {data.complexity_trend[0]} → {data.complexity_trend[data.complexity_trend.length - 1]} concepts
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        )

      case 5: // Infinite Lucidity
        return (
          <div className="space-y-2 text-sm">
            {data.meta_observation && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Meta Observation</div>
                <div className="text-gray-300 text-xs">{data.meta_observation}</div>
              </div>
            )}
            {data.pattern_changes && data.pattern_changes.length > 0 && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Pattern Changes</div>
                <ul className="list-disc list-inside text-xs text-gray-300 space-y-0.5">
                  {data.pattern_changes.map((change: string, i: number) => (
                    <li key={i}>{change}</li>
                  ))}
                </ul>
              </div>
            )}
            {data.learning_velocity && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Learning Velocity</div>
                <div className="text-gray-300 text-xs capitalize">{data.learning_velocity}</div>
              </div>
            )}
            {data.convergence && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Convergence</div>
                <div className="text-gray-300 text-xs capitalize">{data.convergence}</div>
              </div>
            )}
            {data.meta_patterns && data.meta_patterns.length > 0 && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Meta Patterns</div>
                <div className="flex flex-wrap gap-1">
                  {data.meta_patterns.map((pattern: string, i: number) => (
                    <span key={i} className="px-2 py-0.5 bg-gray-800 rounded text-xs text-gray-300">
                      {pattern}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {data.depth && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Recursion Depth</div>
                <div className="text-gray-300 text-xs">Depth: {data.depth}</div>
              </div>
            )}
            {data.deeper && (
              <div className="mt-2 pt-2 border-t border-gray-700">
                <div className="text-xs text-gray-400 mb-1">Deeper Meta-Reasoning</div>
                <div className="text-xs text-gray-500 italic">
                  Recursive analysis at depth {data.depth + 1}
                </div>
              </div>
            )}
          </div>
        )

      default:
        return (
          <div className="text-xs text-gray-500 p-2">
            <pre className="whitespace-pre-wrap">{JSON.stringify(data, null, 2)}</pre>
          </div>
        )
    }
  }

  return (
    <div className={`bg-gray-900/50 border border-gray-700 rounded-lg p-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Brain className="w-5 h-5 text-blue-400" />
        <h3 className="text-sm font-semibold text-gray-200">LUCID Empire Reasoning</h3>
        {reasoningTrace.confidenceSelfReport !== undefined && (
          <div className="ml-auto text-xs text-gray-400">
            Confidence: {(reasoningTrace.confidenceSelfReport * 100).toFixed(0)}%
          </div>
        )}
      </div>

      {/* Reasoning Summary */}
      {reasoningTrace.summary && (
        <div className="mb-4 p-2 bg-gray-800/50 rounded border border-gray-700">
          <div className="text-xs text-gray-400 mb-1">Summary</div>
          <div className="text-sm text-gray-300">{reasoningTrace.summary}</div>
        </div>
      )}

      {/* Domains */}
      {reasoningTrace.domains && reasoningTrace.domains.length > 0 && (
        <div className="mb-4">
          <div className="text-xs text-gray-400 mb-1">Knowledge Domains</div>
          <div className="flex flex-wrap gap-1">
            {reasoningTrace.domains.map((domain, i) => (
              <span key={i} className="px-2 py-0.5 bg-blue-500/20 border border-blue-500/30 rounded text-xs text-blue-300">
                {domain}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* LUCID Layers */}
      {lucidLayers && (
        <div className="space-y-2">
          {[1, 2, 3, 4, 5].map((layerNum) => {
            const layerInfo = getLayerInfo(layerNum)
            const layerData = lucidLayers[`layer${layerNum}` as keyof LucidLayers]
            const isExpanded = expandedLayers.has(layerNum)
            const isSelected = selectedLayer === layerNum

            if (!layerData || Object.keys(layerData).length === 0) {
              return null
            }

            return (
              <div
                key={layerNum}
                className={`border rounded-lg transition-colors ${
                  isSelected
                    ? 'border-blue-500 bg-blue-500/10'
                    : layerInfo.color
                }`}
              >
                <button
                  onClick={() => {
                    toggleLayer(layerNum)
                    handleLayerClick(layerNum, layerData)
                  }}
                  className="w-full flex items-center justify-between p-3 hover:bg-gray-800/50 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    {layerInfo.icon}
                    <div className="text-left">
                      <div className="text-sm font-medium text-gray-200">
                        Layer {layerNum}: {layerInfo.name}
                      </div>
                      <div className="text-xs text-gray-400">{layerInfo.description}</div>
                    </div>
                  </div>
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  )}
                </button>
                {isExpanded && (
                  <div className="border-t border-gray-700 p-3 bg-gray-800/30">
                    {renderLayerContent(layerNum, layerData)}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Assumptions */}
      {reasoningTrace.assumptions && reasoningTrace.assumptions.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="text-xs text-gray-400 mb-2">Assumptions</div>
          <ul className="list-disc list-inside text-xs text-gray-300 space-y-1">
            {reasoningTrace.assumptions.map((assumption, i) => (
              <li key={i}>{assumption}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

