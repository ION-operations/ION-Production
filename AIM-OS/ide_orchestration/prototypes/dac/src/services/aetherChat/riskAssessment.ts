/**
 * Risk Assessment Service
 * Enhanced risk calculation for Dynamic κ-Gating
 * 
 * Phase 1 Week 4: Dynamic κ-Gating Enhancement
 */

import { CASService } from '../CASService'
import type { ChatIntent, ChatMode, EnrichedContext } from '../../types/aetherChatTypes'

export interface RiskAssessment {
  riskScore: number // 0.0 to 1.0
  riskLevel: 'low' | 'medium' | 'high' | 'critical'
  factors: string[]
  category: 'casual' | 'informational' | 'modification' | 'destructive' | 'critical'
}

/**
 * Risk categories with base risk scores
 */
const RISK_CATEGORIES: Record<string, { baseScore: number; category: RiskAssessment['category'] }> = {
  // Casual chat - very low risk
  'meta_chat': { baseScore: 0.1, category: 'casual' },
  'ask_explain': { baseScore: 0.2, category: 'informational' },
  
  // Informational - low risk
  'planning': { baseScore: 0.3, category: 'informational' },
  'design_arch': { baseScore: 0.4, category: 'informational' },
  
  // Modification - medium risk
  'code_edit': { baseScore: 0.6, category: 'modification' },
  'debug_error': { baseScore: 0.7, category: 'modification' },
  
  // Destructive - high risk
  'file_delete': { baseScore: 0.85, category: 'destructive' },
  'system_config': { baseScore: 0.8, category: 'destructive' },
  
  // Critical - very high risk
  'deploy': { baseScore: 0.9, category: 'critical' },
  'production_change': { baseScore: 0.95, category: 'critical' }
}

/**
 * Assess risk for a chat operation
 */
export async function assessRisk(
  intent: ChatIntent,
  mode: ChatMode,
  enrichedContext: EnrichedContext,
  message: string,
  casService?: CASService
): Promise<RiskAssessment> {
  const factors: string[] = []
  let riskScore = 0.0
  
  // 1. Base risk from intent category
  const categoryInfo = RISK_CATEGORIES[intent] || { baseScore: 0.5, category: 'modification' as const }
  riskScore = categoryInfo.baseScore
  factors.push(`Intent: ${intent} (${categoryInfo.category})`)
  
  // 2. Mode-based risk adjustment
  if (mode === 'deep' || mode === 'research') {
    riskScore += 0.1 // Deeper analysis = slightly higher risk
    factors.push('Deep mode analysis')
  }
  
  // 3. Context-based risk factors
  if (enrichedContext.sourceCount === 0) {
    riskScore += 0.15 // No context = higher risk
    factors.push('No supporting context found')
  } else if (enrichedContext.sourceCount > 10) {
    riskScore += 0.05 // Too much context = complexity risk
    factors.push('High context complexity')
  }
  
  // 4. Message content analysis
  const destructiveKeywords = ['delete', 'remove', 'destroy', 'wipe', 'clear', 'drop', 'truncate']
  const criticalKeywords = ['deploy', 'release', 'publish', 'production', 'live', 'commit']
  const messageLower = message.toLowerCase()
  
  if (destructiveKeywords.some(kw => messageLower.includes(kw))) {
    riskScore += 0.2
    factors.push('Destructive operation detected')
  }
  
  if (criticalKeywords.some(kw => messageLower.includes(kw))) {
    riskScore += 0.25
    factors.push('Critical operation detected')
  }
  
  // 5. CAS-based risk assessment (if available)
  if (casService) {
    try {
      const metrics = await casService.getMetrics()
      // Use CAS metrics to adjust risk
      if (metrics && metrics.errorRate && metrics.errorRate > 0.1) {
        riskScore += 0.1
        factors.push('High error rate detected')
      }
    } catch (error) {
      // CAS unavailable - continue without it
      console.warn('[RiskAssessment] CAS unavailable, using basic assessment')
    }
  }
  
  // 6. Cap risk score to 1.0
  riskScore = Math.min(1.0, riskScore)
  
  // 7. Determine risk level
  let riskLevel: RiskAssessment['riskLevel']
  if (riskScore >= 0.8) {
    riskLevel = 'critical'
  } else if (riskScore >= 0.6) {
    riskLevel = 'high'
  } else if (riskScore >= 0.4) {
    riskLevel = 'medium'
  } else {
    riskLevel = 'low'
  }
  
  return {
    riskScore,
    riskLevel,
    factors,
    category: categoryInfo.category
  }
}

/**
 * Get risk category color for UI
 */
export function getRiskCategoryColor(category: RiskAssessment['category']): string {
  switch (category) {
    case 'casual':
      return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
    case 'informational':
      return 'bg-green-500/20 text-green-400 border-green-500/30'
    case 'modification':
      return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
    case 'destructive':
      return 'bg-orange-500/20 text-orange-400 border-orange-500/30'
    case 'critical':
      return 'bg-red-500/20 text-red-400 border-red-500/30'
  }
}

/**
 * Get risk level color for UI
 */
export function getRiskLevelColor(riskLevel: RiskAssessment['riskLevel']): string {
  switch (riskLevel) {
    case 'low':
      return 'text-green-400'
    case 'medium':
      return 'text-yellow-400'
    case 'high':
      return 'text-orange-400'
    case 'critical':
      return 'text-red-400'
  }
}

