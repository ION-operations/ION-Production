/**
 * Cost Calculator - Calculate API costs based on token usage
 * 
 * Pricing as of 2025-01-27
 */

export interface ModelPricing {
  inputPer1M: number // Cost per 1M input tokens
  outputPer1M: number // Cost per 1M output tokens
}

export class CostCalculator {
  // Pricing table (USD per 1M tokens)
  private static PRICING: Record<string, ModelPricing> = {
    // OpenAI
    'gpt-4': { inputPer1M: 30, outputPer1M: 60 },
    'gpt-4-turbo': { inputPer1M: 10, outputPer1M: 30 },
    'gpt-4-turbo-preview': { inputPer1M: 10, outputPer1M: 30 },
    'gpt-3.5-turbo': { inputPer1M: 0.5, outputPer1M: 1.5 },
    
    // Anthropic Claude
    'claude-3-5-sonnet-20241022': { inputPer1M: 3, outputPer1M: 15 },
    'claude-3-opus': { inputPer1M: 15, outputPer1M: 75 },
    'claude-3-sonnet': { inputPer1M: 3, outputPer1M: 15 },
    'claude-3-haiku': { inputPer1M: 0.25, outputPer1M: 1.25 },
    
    // Google Gemini
    'gemini-1.5-pro': { inputPer1M: 3.5, outputPer1M: 10.5 },
    'gemini-1.5-flash': { inputPer1M: 0.075, outputPer1M: 0.3 },
    'gemini-pro': { inputPer1M: 0.5, outputPer1M: 1.5 },
    
    // DeepSeek
    'deepseek-chat': { inputPer1M: 0.14, outputPer1M: 0.28 },
    'deepseek-coder': { inputPer1M: 0.14, outputPer1M: 0.28 },
    
    // Cerebras (Free)
    'llama-3.3-70b': { inputPer1M: 0, outputPer1M: 0 },
    
    // Meta Llama
    'llama-3.1-70b': { inputPer1M: 0.35, outputPer1M: 0.40 },
    'llama-3.1-8b': { inputPer1M: 0.05, outputPer1M: 0.08 },
    
    // Mistral
    'mistral-large': { inputPer1M: 4, outputPer1M: 12 },
    'mistral-medium': { inputPer1M: 2.7, outputPer1M: 8.1 },
    
    // Cohere
    'command-r-plus': { inputPer1M: 3, outputPer1M: 15 },
    'command-r': { inputPer1M: 0.5, outputPer1M: 1.5 },
  }

  /**
   * Calculate cost for API call
   */
  static calculateCost(
    model: string,
    inputTokens: number,
    outputTokens: number
  ): number {
    const pricing = this.getPricing(model)
    
    const inputCost = (inputTokens / 1_000_000) * pricing.inputPer1M
    const outputCost = (outputTokens / 1_000_000) * pricing.outputPer1M
    
    return inputCost + outputCost
  }

  /**
   * Get pricing for model
   */
  private static getPricing(model: string): ModelPricing {
    // Exact match
    if (model in this.PRICING) {
      return this.PRICING[model]
    }
    
    // Fuzzy match (e.g., "gpt-4-0125-preview" → "gpt-4")
    for (const [key, pricing] of Object.entries(this.PRICING)) {
      if (model.includes(key) || key.includes(model)) {
        return pricing
      }
    }
    
    // Default: Assume GPT-3.5 pricing (conservative)
    console.warn(`[CostCalculator] Unknown model "${model}", using GPT-3.5 pricing`)
    return this.PRICING['gpt-3.5-turbo']
  }

  /**
   * Estimate cost for request (before execution)
   */
  static estimateCost(
    model: string,
    inputTokens: number,
    estimatedOutputTokens: number
  ): number {
    return this.calculateCost(model, inputTokens, estimatedOutputTokens)
  }

  /**
   * Format cost as string
   */
  static formatCost(cost: number): string {
    if (cost < 0.01) {
      return `$${(cost * 100).toFixed(4)}¢`
    }
    return `$${cost.toFixed(4)}`
  }

  /**
   * Get all supported models and pricing
   */
  static getAllPricing(): Record<string, ModelPricing> {
    return { ...this.PRICING }
  }

  /**
   * Add custom pricing (for new models)
   */
  static addPricing(model: string, pricing: ModelPricing): void {
    this.PRICING[model] = pricing
  }
}

