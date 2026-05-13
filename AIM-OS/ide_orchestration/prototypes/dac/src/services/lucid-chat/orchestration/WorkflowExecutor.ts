/**
 * Workflow Executor
 * 
 * Executes multi-step APOE workflows with dependency resolution,
 * parallel execution, budget management, and quality gates
 * 
 * Epic 1.1: Complete APOE Execution
 */

import { RoleDispatcher } from './RoleDispatcher'
import { BudgetTracker, Budget } from './BudgetTracker'
import { QualityGateSystem, QualityGate } from './QualityGates'
import { APOERole, RoleContext, RoleExecutionResult } from './RoleExecutor'
import { LLMService } from '../llm/LLMService'
import { Plan, PlanStep } from './PlannerExecutor'
import { DAGExecutor, DAGNode } from './DAGExecutor'

/**
 * Workflow Configuration
 */
export interface WorkflowConfig {
  id: string
  goal: string
  plan: Plan
  budget?: Budget
  qualityGates?: QualityGate[]
  parallelExecution?: boolean
}

/**
 * Workflow Result
 */
export interface WorkflowResult {
  workflow_id: string
  goal: string
  success: boolean
  steps_executed: RoleExecutionResult[]
  total_tokens: number
  total_time: number
  total_cost: number
  final_confidence: number
  budget_status: any
  error?: string
}

/**
 * Workflow Executor Implementation
 */
export class WorkflowExecutor {
  private dispatcher: RoleDispatcher
  private budgetTracker: BudgetTracker | null = null
  private qualityGates: QualityGateSystem
  private commandServerUrl: string
  private dagExecutor: DAGExecutor

  constructor(llmService: LLMService, commandServerUrl: string = 'http://localhost:5001') {
    this.dispatcher = new RoleDispatcher(llmService, commandServerUrl)
    this.qualityGates = new QualityGateSystem(commandServerUrl)
    this.commandServerUrl = commandServerUrl
    this.dagExecutor = new DAGExecutor()
  }

  /**
   * Execute complete workflow
   */
  async execute(config: WorkflowConfig): Promise<WorkflowResult> {
    // Initialize budget tracker if budget specified
    if (config.budget) {
      this.budgetTracker = new BudgetTracker(config.budget)
    }

    const executedSteps: RoleExecutionResult[] = []
    const stepResults = new Map<string, RoleExecutionResult>()

    try {
      // Use DAG execution if parallel enabled, otherwise sequential
      if (config.parallelExecution) {
        const dagResult = await this.executeWithDAG(config, stepResults, executedSteps)
        
        if (!dagResult.success) {
          throw new Error('DAG execution failed')
        }
      } else {
        // Sequential execution (original logic)
        const executionOrder = this.buildExecutionOrder(config.plan)

        for (const step of executionOrder) {
          // Check budget before executing
          if (this.budgetTracker && this.budgetTracker.isExceeded()) {
            throw new Error('Budget exceeded - stopping workflow')
          }

          // Build context for this step
          const context: RoleContext = {
            goal: config.goal,
            previousSteps: executedSteps,
            workflow: config,
            budget: config.budget,
          }

          // Execute step
          const result = await this.executeStep(step, stepResults, context, config.qualityGates)

          // Track budget
          if (this.budgetTracker) {
            this.budgetTracker.trackStep(result)
          }

          // Store result
          executedSteps.push(result)
          stepResults.set(step.id, result)

          // Check if step failed critically
          if (!result.success && config.qualityGates) {
            const gates = config.qualityGates
            const shouldStop = gates.some(g => g.action === 'stop' && result.confidence < g.threshold)
            
            if (shouldStop) {
              throw new Error(`Step ${step.id} failed quality gate - stopping workflow`)
            }
          }
        }
      }

      // Calculate final metrics
      const totalTokens = executedSteps.reduce((sum, s) => sum + s.tokensUsed, 0)
      const totalTime = executedSteps.reduce((sum, s) => sum + (s.latencyMs / 1000), 0)
      const totalCost = this.budgetTracker?.getStatus().usage.cost || 0
      const finalConfidence = this.calculateFinalConfidence(executedSteps)

      return {
        workflow_id: config.id,
        goal: config.goal,
        success: true,
        steps_executed: executedSteps,
        total_tokens: totalTokens,
        total_time: totalTime,
        total_cost: totalCost,
        final_confidence: finalConfidence,
        budget_status: this.budgetTracker?.getStatus(),
      }
    } catch (error: any) {
      return {
        workflow_id: config.id,
        goal: config.goal,
        success: false,
        steps_executed: executedSteps,
        total_tokens: executedSteps.reduce((sum, s) => sum + s.tokensUsed, 0),
        total_time: executedSteps.reduce((sum, s) => sum + (s.latencyMs / 1000), 0),
        total_cost: this.budgetTracker?.getStatus().usage.cost || 0,
        final_confidence: 0,
        budget_status: this.budgetTracker?.getStatus(),
        error: error.message,
      }
    }
  }

  /**
   * Execute single step
   */
  private async executeStep(
    step: PlanStep,
    previousResults: Map<string, RoleExecutionResult>,
    context: RoleContext,
    gates?: QualityGate[]
  ): Promise<RoleExecutionResult> {
    // Gather dependencies
    const dependencyOutputs = step.dependencies.map(depId => {
      const depResult = previousResults.get(depId)
      return depResult?.output
    }).filter(Boolean)

    // Build step input
    const stepInput = {
      description: step.description,
      inputs: step.inputs,
      dependencies: dependencyOutputs,
      ...context.metadata,
    }

    // Execute with appropriate role
    const result = await this.dispatcher.dispatch(
      step.role as APOERole,
      stepInput,
      context
    )

    // Evaluate quality gates
    if (gates && gates.length > 0) {
      const gateDecision = await this.qualityGates.evaluate(result, gates)

      if (!gateDecision.passed && gateDecision.action === 'retry') {
        // Retry step
        const retryCount = (result.metadata?.retry_count || 0) + 1
        const maxRetries = gateDecision.gate?.max_retries || 2

        if (retryCount <= maxRetries) {
          console.log(`[WorkflowExecutor] Retrying step ${step.id} (attempt ${retryCount + 1})`)
          
          // Retry with adjusted context
          return this.executeStep(step, previousResults, {
            ...context,
            metadata: {
              ...context.metadata,
              retry_count: retryCount,
            },
          }, gates)
        }
      }

      if (!gateDecision.passed && gateDecision.action === 'stop') {
        throw new Error(`Quality gate failed: ${gateDecision.reason}`)
      }
    }

    return result
  }

  /**
   * Build execution order from plan (topological sort)
   */
  /**
   * Execute workflow using DAG for parallel execution
   */
  private async executeWithDAG(
    config: WorkflowConfig,
    stepResults: Map<string, RoleExecutionResult>,
    executedSteps: RoleExecutionResult[]
  ): Promise<{ success: boolean }> {
    // Convert plan steps to DAG nodes
    const dagNodes: DAGNode[] = config.plan.steps.map(step => ({
      id: step.id,
      role: step.role,
      input: step.input,
      dependencies: step.dependencies,
      status: 'pending' as const,
    }))

    // Execute DAG
    const result = await this.dagExecutor.execute(
      dagNodes,
      async (node: DAGNode) => {
        // Check budget before executing
        if (this.budgetTracker && this.budgetTracker.isExceeded()) {
          throw new Error('Budget exceeded')
        }

        // Build context
        const context: RoleContext = {
          goal: config.goal,
          previousSteps: executedSteps,
          workflow: config,
          budget: config.budget,
        }

        // Find original step
        const step = config.plan.steps.find(s => s.id === node.id)!

        // Execute step
        const stepResult = await this.executeStep(step, stepResults, context, config.qualityGates)

        // Track budget
        if (this.budgetTracker) {
          this.budgetTracker.trackStep(stepResult)
        }

        // Store result
        executedSteps.push(stepResult)
        stepResults.set(step.id, stepResult)

        return stepResult
      }
    )

    return { success: result.success }
  }

  private buildExecutionOrder(plan: Plan): PlanStep[] {
    // Simple topological sort
    const sorted: PlanStep[] = []
    const visited = new Set<string>()
    const visiting = new Set<string>()

    const visit = (step: PlanStep) => {
      if (visited.has(step.id)) return
      if (visiting.has(step.id)) {
        throw new Error(`Circular dependency detected: ${step.id}`)
      }

      visiting.add(step.id)

      // Visit dependencies first
      for (const depId of step.dependencies) {
        const depStep = plan.steps.find(s => s.id === depId)
        if (depStep) {
          visit(depStep)
        }
      }

      visiting.delete(step.id)
      visited.add(step.id)
      sorted.push(step)
    }

    // Visit all steps
    for (const step of plan.steps) {
      visit(step)
    }

    return sorted
  }

  /**
   * Calculate final confidence from all steps
   */
  private calculateFinalConfidence(steps: RoleExecutionResult[]): number {
    if (steps.length === 0) return 0

    // Weighted average (later steps weighted more)
    let weightedSum = 0
    let totalWeight = 0

    steps.forEach((step, i) => {
      const weight = i + 1
      weightedSum += step.confidence * weight
      totalWeight += weight
    })

    return weightedSum / totalWeight
  }

  /**
   * Get dispatcher
   */
  getDispatcher(): RoleDispatcher {
    return this.dispatcher
  }
}

