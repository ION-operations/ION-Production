/**
 * Budget Tracker
 * 
 * Tracks token, time, and cost budgets for APOE workflows
 * Enforces budget limits and generates warnings
 * 
 * Epic 1.1: Complete APOE Execution
 */

import { RoleExecutionResult } from './RoleExecutor'
import { CostCalculator } from './CostCalculator'
import { TokenCounter } from './TokenCounter'

/**
 * Budget Configuration
 */
export interface Budget {
  tokens?: number // Max tokens
  time?: number // Max seconds
  cost?: number // Max dollars
}

/**
 * Budget Usage
 */
export interface BudgetUsage {
  tokens: number
  time: number // seconds
  cost: number // dollars
}

/**
 * Budget Status
 */
export interface BudgetStatus {
  exceeded: boolean
  remaining: BudgetUsage
  usage: BudgetUsage
  budget: Budget
  warnings: string[]
  percentage: {
    tokens: number
    time: number
    cost: number
  }
}

/**
 * Budget Tracker Implementation
 */
export class BudgetTracker {
  private budget: Budget
  private usage: BudgetUsage
  private warnings: string[]

  constructor(budget: Budget) {
    this.budget = budget
    this.usage = {
      tokens: 0,
      time: 0,
      cost: 0,
    }
    this.warnings = []
  }

  /**
   * Track step execution
   */
  trackStep(step: RoleExecutionResult): void {
    // Update usage
    this.usage.tokens += step.tokensUsed || 0
    this.usage.time += (step.latencyMs / 1000) || 0
    this.usage.cost += this.calculateStepCost(step)

    // Check for warnings
    this.generateWarnings()
  }

  /**
   * Calculate cost for a single step (REAL implementation)
   */
  private calculateStepCost(step: RoleExecutionResult): number {
    // Use real cost calculation
    const tokensUsed = step.tokensUsed || 0
    
    // Extract model from metadata (if available)
    const model = (step as any).model || 'gpt-3.5-turbo'  // Default fallback
    
    // Split tokens into input/output (rough 50/50 split if not specified)
    const inputTokens = (step as any).inputTokens || Math.ceil(tokensUsed * 0.4)
    const outputTokens = (step as any).outputTokens || Math.ceil(tokensUsed * 0.6)
    
    // Calculate cost using real pricing
    return CostCalculator.calculateCost(model, inputTokens, outputTokens)
  }

  /**
   * Check if budget is exceeded
   */
  isExceeded(): boolean {
    if (this.budget.tokens && this.usage.tokens > this.budget.tokens) {
      return true
    }
    
    if (this.budget.time && this.usage.time > this.budget.time) {
      return true
    }
    
    if (this.budget.cost && this.usage.cost > this.budget.cost) {
      return true
    }
    
    return false
  }

  /**
   * Get budget status
   */
  getStatus(): BudgetStatus {
    return {
      exceeded: this.isExceeded(),
      remaining: this.calculateRemaining(),
      usage: { ...this.usage },
      budget: { ...this.budget },
      warnings: [...this.warnings],
      percentage: this.calculatePercentages(),
    }
  }

  /**
   * Calculate remaining budget
   */
  private calculateRemaining(): BudgetUsage {
    return {
      tokens: (this.budget.tokens || Infinity) - this.usage.tokens,
      time: (this.budget.time || Infinity) - this.usage.time,
      cost: (this.budget.cost || Infinity) - this.usage.cost,
    }
  }

  /**
   * Calculate budget usage percentages
   */
  private calculatePercentages(): { tokens: number; time: number; cost: number } {
    return {
      tokens: this.budget.tokens
        ? (this.usage.tokens / this.budget.tokens) * 100
        : 0,
      time: this.budget.time
        ? (this.usage.time / this.budget.time) * 100
        : 0,
      cost: this.budget.cost
        ? (this.usage.cost / this.budget.cost) * 100
        : 0,
    }
  }

  /**
   * Generate budget warnings
   */
  private generateWarnings(): void {
    const percentages = this.calculatePercentages()
    this.warnings = []

    // 80% warning
    if (percentages.tokens > 80) {
      this.warnings.push(`Token budget at ${percentages.tokens.toFixed(1)}%`)
    }
    if (percentages.time > 80) {
      this.warnings.push(`Time budget at ${percentages.time.toFixed(1)}%`)
    }
    if (percentages.cost > 80) {
      this.warnings.push(`Cost budget at ${percentages.cost.toFixed(1)}%`)
    }

    // 100% exceeded
    if (this.isExceeded()) {
      this.warnings.push('⚠️ BUDGET EXCEEDED')
    }
  }

  /**
   * Get warnings
   */
  getWarnings(): string[] {
    return [...this.warnings]
  }

  /**
   * Reset tracker
   */
  reset(): void {
    this.usage = {
      tokens: 0,
      time: 0,
      cost: 0,
    }
    this.warnings = []
  }

  /**
   * Get usage summary
   */
  getSummary(): string {
    const status = this.getStatus()
    
    let summary = '**Budget Usage:**\n'
    summary += `- Tokens: ${this.usage.tokens}/${this.budget.tokens || '∞'} (${status.percentage.tokens.toFixed(1)}%)\n`
    summary += `- Time: ${this.usage.time.toFixed(1)}s/${this.budget.time || '∞'}s (${status.percentage.time.toFixed(1)}%)\n`
    summary += `- Cost: $${this.usage.cost.toFixed(4)}/$${this.budget.cost || '∞'} (${status.percentage.cost.toFixed(1)}%)\n`
    
    if (this.warnings.length > 0) {
      summary += `\n**Warnings:**\n`
      this.warnings.forEach(w => summary += `- ${w}\n`)
    }
    
    return summary
  }
}

