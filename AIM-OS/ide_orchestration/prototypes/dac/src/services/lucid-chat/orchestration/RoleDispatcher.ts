/**
 * Role Dispatcher
 * 
 * Routes workflow steps to appropriate role executors
 * Manages role instances and execution
 * 
 * Epic 1.1: Complete APOE Execution
 */

import { RoleExecutor, APOERole, RoleContext, RoleExecutionResult } from './RoleExecutor'
import { PlannerExecutor } from './PlannerExecutor'
import { RetrieverExecutor } from './RetrieverExecutor'
import { ReasonerExecutor } from './ReasonerExecutor'
import { VerifierExecutor } from './VerifierExecutor'
import { BuilderExecutor } from './BuilderExecutor'
import { CriticExecutor } from './CriticExecutor'
import { OperatorExecutor } from './OperatorExecutor'
import { WitnessExecutor } from './WitnessExecutor'
import { LLMService } from '../llm/LLMService'

/**
 * Role Dispatcher
 * 
 * Central routing system for APOE roles
 */
export class RoleDispatcher {
  private executors: Map<APOERole, RoleExecutor>
  private llmService: LLMService
  private commandServerUrl: string

  constructor(llmService: LLMService, commandServerUrl: string = 'http://localhost:5001') {
    this.llmService = llmService
    this.commandServerUrl = commandServerUrl
    this.executors = new Map()
    
    this.initializeExecutors()
  }

  /**
   * Initialize all role executors
   */
  private initializeExecutors(): void {
    this.executors.set('planner', new PlannerExecutor(this.llmService, this.commandServerUrl))
    this.executors.set('retriever', new RetrieverExecutor(this.llmService, this.commandServerUrl))
    this.executors.set('reasoner', new ReasonerExecutor(this.llmService, this.commandServerUrl))
    this.executors.set('verifier', new VerifierExecutor(this.llmService, this.commandServerUrl))
    this.executors.set('builder', new BuilderExecutor(this.llmService, this.commandServerUrl))
    this.executors.set('critic', new CriticExecutor(this.llmService, this.commandServerUrl))
    this.executors.set('operator', new OperatorExecutor(this.llmService, this.commandServerUrl))
    this.executors.set('witness', new WitnessExecutor(this.llmService, this.commandServerUrl))
  }

  /**
   * Dispatch step to appropriate role
   */
  async dispatch(
    role: APOERole,
    input: any,
    context: RoleContext
  ): Promise<RoleExecutionResult> {
    const executor = this.executors.get(role)
    
    if (!executor) {
      throw new Error(`No executor found for role: ${role}`)
    }
    
    // Execute with role
    const result = await executor.execute(input, context)
    
    // Log dispatch
    console.log(`[RoleDispatcher] ${role} executed in ${result.latencyMs}ms (confidence: ${result.confidence.toFixed(2)})`)
    
    return result
  }

  /**
   * Get executor for role
   */
  getExecutor(role: APOERole): RoleExecutor | undefined {
    return this.executors.get(role)
  }

  /**
   * Get all available roles
   */
  getAvailableRoles(): APOERole[] {
    return Array.from(this.executors.keys())
  }

  /**
   * Validate role exists
   */
  hasRole(role: APOERole): boolean {
    return this.executors.has(role)
  }
}

