/**
 * Model Registry - Centralized LLM Provider Configuration
 * 
 * Manages configuration for multiple LLM providers with API-specific calibration
 * Supports: OpenAI, Anthropic, Google, Meta, Groq, and local models
 * 
 * Gap 3: Configuration & Environment Management
 */

import type { ModelConfig, ModelTier, EnvironmentConfig, ChatIntent } from '../types/aetherChatTypes'

// ============================================================================
// MODEL CONFIGURATIONS
// ============================================================================

/**
 * Model Registry - All available models organized by tier
 */
export const MODEL_TIERS: Record<string, ModelTier> = {
  'fast': {
    name: 'Fast Response',
    models: [
      {
        provider: 'groq',
        model: 'llama-3.1-70b',
        endpoint: 'https://api.groq.com/openai/v1/chat/completions',
        apiKey: process.env.GROQ_API_KEY || '',
        costPer1kTokens: { input: 0.0007, output: 0.0008 },
        capabilities: {
          maxContextWindow: 8192,
          supportsFunctionCalling: false,
          supportsStreaming: true,
          supportsVision: false,
          supportsAudio: false
        },
        performance: {
          avgLatency: 200,
          maxLatency: 500,
          throughput: 100
        },
        limits: {
          rateLimit: 30,
          dailyLimit: 10000
        }
      },
      {
        provider: 'openai',
        model: 'gpt-3.5-turbo',
        endpoint: 'https://api.openai.com/v1/chat/completions',
        apiKey: process.env.OPENAI_API_KEY || '',
        costPer1kTokens: { input: 0.0005, output: 0.0015 },
        capabilities: {
          maxContextWindow: 16385,
          supportsFunctionCalling: true,
          supportsStreaming: true,
          supportsVision: false,
          supportsAudio: false
        },
        performance: {
          avgLatency: 500,
          maxLatency: 2000,
          throughput: 50
        },
        limits: {
          rateLimit: 500,
          dailyLimit: 1000000
        }
      }
    ],
    selectionCriteria: {
      complexity: ['simple', 'medium'],
      intent: ['ask_explain', 'meta_chat'],
      maxCost: 0.01,
      maxLatency: 1000
    }
  },
  'reasoning': {
    name: 'Deep Reasoning',
    models: [
      {
        provider: 'anthropic',
        model: 'claude-3-5-sonnet-20241022',
        endpoint: 'https://api.anthropic.com/v1/messages',
        apiKey: process.env.ANTHROPIC_API_KEY || '',
        costPer1kTokens: { input: 0.003, output: 0.015 },
        capabilities: {
          maxContextWindow: 200000,
          supportsFunctionCalling: true,
          supportsStreaming: true,
          supportsVision: true,
          supportsAudio: false
        },
        performance: {
          avgLatency: 2000,
          maxLatency: 5000,
          throughput: 20
        },
        limits: {
          rateLimit: 50
        }
      },
      {
        provider: 'openai',
        model: 'gpt-4o',
        endpoint: 'https://api.openai.com/v1/chat/completions',
        apiKey: process.env.OPENAI_API_KEY || '',
        costPer1kTokens: { input: 0.005, output: 0.015 },
        capabilities: {
          maxContextWindow: 128000,
          supportsFunctionCalling: true,
          supportsStreaming: true,
          supportsVision: true,
          supportsAudio: true
        },
        performance: {
          avgLatency: 1500,
          maxLatency: 4000,
          throughput: 30
        },
        limits: {
          rateLimit: 10000,
          dailyLimit: 1000000
        }
      }
    ],
    selectionCriteria: {
      complexity: ['complex', 'very_complex'],
      intent: ['design_arch', 'planning', 'debug_error'],
      maxCost: 0.10,
      maxLatency: 5000
    }
  },
  'creative': {
    name: 'Creative Generation',
    models: [
      {
        provider: 'openai',
        model: 'gpt-4o',
        endpoint: 'https://api.openai.com/v1/chat/completions',
        apiKey: process.env.OPENAI_API_KEY || '',
        costPer1kTokens: { input: 0.005, output: 0.015 },
        capabilities: {
          maxContextWindow: 128000,
          supportsFunctionCalling: true,
          supportsStreaming: true,
          supportsVision: true,
          supportsAudio: true
        },
        performance: {
          avgLatency: 1500,
          maxLatency: 4000,
          throughput: 30
        },
        limits: {
          rateLimit: 10000,
          dailyLimit: 1000000
        }
      },
      {
        provider: 'google',
        model: 'gemini-2.0-flash-exp',
        endpoint: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent',
        apiKey: process.env.GOOGLE_API_KEY || '',
        costPer1kTokens: { input: 0.000125, output: 0.0005 },
        capabilities: {
          maxContextWindow: 1000000,
          supportsFunctionCalling: true,
          supportsStreaming: true,
          supportsVision: true,
          supportsAudio: false
        },
        performance: {
          avgLatency: 1000,
          maxLatency: 3000,
          throughput: 40
        },
        limits: {
          rateLimit: 60
        }
      }
    ],
    selectionCriteria: {
      complexity: ['medium', 'complex'],
      intent: ['code_edit', 'creative_brainstorm'],
      maxCost: 0.05,
      maxLatency: 3000
    }
  },
  'local': {
    name: 'Local Model',
    models: [
      {
        provider: 'local',
        model: 'llama-3.1-8b',
        endpoint: process.env.LOCAL_MODEL_ENDPOINT || 'http://localhost:8080/v1/chat/completions',
        apiKey: '', // Not needed for local
        costPer1kTokens: { input: 0, output: 0 }, // Free
        capabilities: {
          maxContextWindow: 8192,
          supportsFunctionCalling: false,
          supportsStreaming: true,
          supportsVision: false,
          supportsAudio: false
        },
        performance: {
          avgLatency: 500,
          maxLatency: 2000,
          throughput: 10
        },
        limits: {
          rateLimit: 1000
        }
      }
    ],
    selectionCriteria: {
      complexity: ['simple'],
      intent: ['ask_explain', 'meta_chat'],
      maxCost: 0,
      maxLatency: 2000
    }
  }
}

// ============================================================================
// PROVIDER SELECTION LOGIC
// ============================================================================

/**
 * Select optimal model based on task characteristics
 */
export function getActiveModel(
  intent: ChatIntent,
  complexity: 'simple' | 'medium' | 'complex' | 'very_complex',
  budget: number,
  latencyRequirement?: number
): ModelConfig | null {
  // Find matching tier
  const matchingTiers = Object.values(MODEL_TIERS).filter(tier =>
    tier.selectionCriteria.complexity.includes(complexity) &&
    tier.selectionCriteria.intent.includes(intent) &&
    (!tier.selectionCriteria.maxCost || tier.selectionCriteria.maxCost <= budget) &&
    (!latencyRequirement || !tier.selectionCriteria.maxLatency || tier.selectionCriteria.maxLatency <= latencyRequirement)
  )
  
  if (matchingTiers.length === 0) {
    return null // No matching model
  }
  
  // Select best model from matching tier (first one for now, can add ranking)
  const selectedTier = matchingTiers[0]
  const selectedModel = selectedTier.models[0]
  
  // Verify API key is available
  if (selectedModel.apiKey === '' && selectedModel.provider !== 'local') {
    console.warn(`API key missing for ${selectedModel.provider}/${selectedModel.model}`)
    // Try next model in tier
    if (selectedTier.models.length > 1) {
      return selectedTier.models[1]
    }
    return null
  }
  
  return selectedModel
}

/**
 * Get all available models for a given tier
 */
export function getModelsForTier(tierName: string): ModelConfig[] {
  return MODEL_TIERS[tierName]?.models || []
}

/**
 * Get tier name for a model
 */
export function getTierForModel(provider: string, model: string): string | null {
  for (const [tierName, tier] of Object.entries(MODEL_TIERS)) {
    if (tier.models.some(m => m.provider === provider && m.model === model)) {
      return tierName
    }
  }
  return null
}

// ============================================================================
// ENVIRONMENT CONFIGURATION
// ============================================================================

/**
 * Load environment configuration
 */
export function loadEnvironmentConfig(): EnvironmentConfig {
  return {
    nodeEnv: (process.env.NODE_ENV || 'development') as 'development' | 'production' | 'test',
    aimosSystems: {
      cmc: {
        enabled: process.env.AIMOS_CMC_ENABLED !== 'false',
        endpoint: process.env.AIMOS_CMC_ENDPOINT || 'http://localhost:5001'
      },
      hhni: {
        enabled: process.env.AIMOS_HHNI_ENABLED !== 'false',
        endpoint: process.env.AIMOS_HHNI_ENDPOINT || 'http://localhost:5001'
      },
      vif: {
        enabled: process.env.AIMOS_VIF_ENABLED !== 'false',
        endpoint: process.env.AIMOS_VIF_ENDPOINT || 'http://localhost:5001'
      },
      apoe: {
        enabled: process.env.AIMOS_APOE_ENABLED !== 'false',
        endpoint: process.env.AIMOS_APOE_ENDPOINT || 'http://localhost:5001'
      },
      seg: {
        enabled: process.env.AIMOS_SEG_ENABLED !== 'false',
        endpoint: process.env.AIMOS_SEG_ENDPOINT || 'http://localhost:5001'
      },
      cas: {
        enabled: process.env.AIMOS_CAS_ENABLED !== 'false',
        endpoint: process.env.AIMOS_CAS_ENDPOINT || 'http://localhost:5001'
      },
      tcs: {
        enabled: process.env.AIMOS_TCS_ENABLED !== 'false',
        endpoint: process.env.AIMOS_TCS_ENDPOINT || 'http://localhost:5001'
      },
      mige: {
        enabled: process.env.AIMOS_MIGE_ENABLED !== 'false',
        endpoint: process.env.AIMOS_MIGE_ENDPOINT || 'http://localhost:5001'
      }
    },
    defaultModel: {
      provider: process.env.DEFAULT_MODEL_PROVIDER || 'openai',
      model: process.env.DEFAULT_MODEL_NAME || 'gpt-4o'
    },
    costTracking: {
      enabled: process.env.COST_TRACKING_ENABLED !== 'false',
      budgetLimit: process.env.COST_BUDGET_LIMIT ? parseFloat(process.env.COST_BUDGET_LIMIT) : undefined,
      alertThreshold: process.env.COST_ALERT_THRESHOLD ? parseFloat(process.env.COST_ALERT_THRESHOLD) : undefined
    }
  }
}

// ============================================================================
// COST CALCULATION
// ============================================================================

/**
 * Estimate cost for a request
 */
export function estimateCost(
  model: ModelConfig,
  inputTokens: number,
  outputTokens: number
): number {
  const inputCost = (inputTokens / 1000) * model.costPer1kTokens.input
  const outputCost = (outputTokens / 1000) * model.costPer1kTokens.output
  return inputCost + outputCost
}

/**
 * Check if request is within budget
 */
export function isWithinBudget(
  model: ModelConfig,
  inputTokens: number,
  outputTokens: number,
  budget: number
): boolean {
  const cost = estimateCost(model, inputTokens, outputTokens)
  return cost <= budget
}

