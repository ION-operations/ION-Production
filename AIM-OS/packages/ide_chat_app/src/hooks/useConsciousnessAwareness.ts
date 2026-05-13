/**
 * Consciousness Awareness Hook
 * 
 * Phase 4.3: Enhanced Consciousness Awareness
 * 
 * Features:
 * - Real-time consciousness health metrics
 * - Memory awareness indicators
 * - Goal alignment tracking
 * - Cognitive metrics
 * - Connection density monitoring
 */

import { useState, useEffect, useMemo } from 'react'
import { useAIMOS } from './useAIMOS'

export interface ConsciousnessHealth {
  score: number // 0-1 overall health score
  confidence: number // Average confidence across systems
  intensity: number // Activity level
  stability: number // Consistency of metrics
  connectionDensity: number // Number of connections
  status: 'excellent' | 'good' | 'fair' | 'poor'
}

export interface MemoryAwareness {
  count: number
  ratio: number // Memory nodes / total nodes
  avgInfluence: number
  status: 'high' | 'medium' | 'low'
}

export interface GoalAlignment {
  score: number // 0-1 alignment score
  alignedGoals: number
  totalGoals: number
  recentProgress: number
  status: 'aligned' | 'partial' | 'misaligned'
}

export interface CognitiveMetrics {
  thoughtRatio: number
  decisionRatio: number
  insightRatio: number
  patternRatio: number
  cognitiveDiversity: number // 0-1 diversity score
}

export interface ConsciousnessAwareness {
  health: ConsciousnessHealth
  memory: MemoryAwareness
  goals: GoalAlignment
  cognitive: CognitiveMetrics
  timestamp: string
}

export const useConsciousnessAwareness = () => {
  const { cmc, hhni, vif, apoe, seg, isConnected, useMockData, loading } = useAIMOS()
  const [awareness, setAwareness] = useState<ConsciousnessAwareness | null>(null)

  // Calculate consciousness health
  const calculateHealth = useMemo((): ConsciousnessHealth => {
    // Mock calculation - would use real AIM-OS data
    const confidence = 0.85 // Average from VIF
    const intensity = 0.75 // Activity level
    const stability = 0.80 // Consistency
    const connectionDensity = 0.70 // Connection density
    
    const score = (confidence * 0.4) + (intensity * 0.2) + (stability * 0.2) + (connectionDensity * 0.2)
    
    let status: ConsciousnessHealth['status'] = 'good'
    if (score >= 0.9) status = 'excellent'
    else if (score >= 0.7) status = 'good'
    else if (score >= 0.5) status = 'fair'
    else status = 'poor'
    
    return {
      score,
      confidence,
      intensity,
      stability,
      connectionDensity,
      status,
    }
  }, [])

  // Calculate memory awareness
  const calculateMemoryAwareness = useMemo((): MemoryAwareness => {
    // Mock calculation - would use real CMC/HHNI data
    const count = 150 // Total memory atoms
    const totalNodes = 200 // Total nodes
    const ratio = count / totalNodes
    const avgInfluence = 0.65
    
    let status: MemoryAwareness['status'] = 'medium'
    if (ratio >= 0.7) status = 'high'
    else if (ratio >= 0.4) status = 'medium'
    else status = 'low'
    
    return {
      count,
      ratio,
      avgInfluence,
      status,
    }
  }, [])

  // Calculate goal alignment
  const calculateGoalAlignment = useMemo((): GoalAlignment => {
    // Mock calculation - would use real APOE data
    const alignedGoals = 5
    const totalGoals = 8
    const score = alignedGoals / totalGoals
    const recentProgress = 0.75
    
    let status: GoalAlignment['status'] = 'partial'
    if (score >= 0.8) status = 'aligned'
    else if (score >= 0.5) status = 'partial'
    else status = 'misaligned'
    
    return {
      score,
      alignedGoals,
      totalGoals,
      recentProgress,
      status,
    }
  }, [])

  // Calculate cognitive metrics
  const calculateCognitiveMetrics = useMemo((): CognitiveMetrics => {
    // Mock calculation - would use real CAS/SEG data
    const thoughtRatio = 0.35
    const decisionRatio = 0.25
    const insightRatio = 0.20
    const patternRatio = 0.20
    
    // Cognitive diversity: how evenly distributed the ratios are
    const ratios = [thoughtRatio, decisionRatio, insightRatio, patternRatio]
    const mean = ratios.reduce((a, b) => a + b, 0) / ratios.length
    const variance = ratios.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / ratios.length
    const cognitiveDiversity = 1 - Math.sqrt(variance) // Higher diversity = lower variance
    
    return {
      thoughtRatio,
      decisionRatio,
      insightRatio,
      patternRatio,
      cognitiveDiversity,
    }
  }, [])

  // Update awareness periodically
  useEffect(() => {
    const updateAwareness = async () => {
      if (!useMockData && isConnected) {
        try {
          // Load real data from AIM-OS
          // For now, use calculated values
          const newAwareness: ConsciousnessAwareness = {
            health: calculateHealth,
            memory: calculateMemoryAwareness,
            goals: calculateGoalAlignment,
            cognitive: calculateCognitiveMetrics,
            timestamp: new Date().toISOString(),
          }
          
          setAwareness(newAwareness)
        } catch (error) {
          console.warn('Failed to load consciousness awareness data', error)
        }
      } else {
        // Use mock data
        const newAwareness: ConsciousnessAwareness = {
          health: calculateHealth,
          memory: calculateMemoryAwareness,
          goals: calculateGoalAlignment,
          cognitive: calculateCognitiveMetrics,
          timestamp: new Date().toISOString(),
        }
        
        setAwareness(newAwareness)
      }
    }

    updateAwareness()
    const interval = setInterval(updateAwareness, 5000) // Update every 5 seconds
    return () => clearInterval(interval)
  }, [useMockData, isConnected, calculateHealth, calculateMemoryAwareness, calculateGoalAlignment, calculateCognitiveMetrics])

  return {
    awareness,
    loading: loading.cmc || loading.vif || loading.apoe,
    isConnected,
    useMockData,
  }
}

