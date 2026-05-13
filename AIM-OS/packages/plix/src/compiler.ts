/**
 * PLIx Compiler
 * 
 * Compiles NL intents to PLIx contracts and plans
 * Phase 2: Compiler to AIP integration
 */

import { PLIxIntent, PLIxPlanStep } from './models/schema';
export { PLIXToAIPCompiler } from './compiler/aip-compiler';
export type { AIPGraph, AIPGraphNode, AIPGraphEdge, APOECompilationResult, VIFWitnessRequirement, TagResolutionResult } from './compiler/aip-compiler';

export interface CompilationOptions {
  /** Confidence threshold for compilation */
  confidenceThreshold?: number;
  
  /** Include evidence requirements */
  includeEvidence?: boolean;
  
  /** Include telemetry */
  includeTelemetry?: boolean;
  
  /** Target interop format */
  interopTarget?: 'temporal' | 'opa' | 'prov' | 'pddl' | 'none';
}

export class PLIxCompiler {
  /**
   * Compile natural language intent to PLIx contract
   */
  static async compileIntent(
    nlIntent: string,
    context?: {
      entities?: string[];
      scope?: string;
      risk?: number;
    },
    options: CompilationOptions = {}
  ): Promise<PLIxIntent> {
    // TODO: Implement LLM-based compilation
    // For now, return a stub structure
    
    const intent: PLIxIntent = {
      intent: nlIntent,
      context: {
        entities: context?.entities || [],
        scope: context?.scope || 'unknown',
        risk: context?.risk || 0.5,
      },
      contract: {
        pre: [],
        post: [],
        capabilities: [],
        policies: [],
      },
      plan: {
        steps: [],
        deps: [],
      },
      conditions: {
        onTestFail: 'retry',
        onLowConfidence: 'escalate',
        onPolicyBreach: 'fail',
      },
      evidence: {
        required: [],
        produce: [],
      },
      telemetry: {
        confidenceThresholds: {
          minimum: options.confidenceThreshold || 0.70,
          warning: 0.80,
          critical: 0.90,
        },
        timeouts: {
          step: 30000,
          plan: 300000,
        },
      },
      provenance: {
        who: 'system',
        when: new Date().toISOString(),
        lineage: [],
      },
    };

    return intent;
  }

  /**
   * Generate plan steps from contract
   */
  static async generatePlan(
    contract: PLIxIntent['contract'],
    availableAgents: string[],
    availableTools: string[]
  ): Promise<PLIxPlanStep[]> {
    // TODO: Implement plan generation logic
    // For now, return empty steps
    return [];
  }

  /**
   * Validate PLIx intent
   */
  static validateIntent(intent: PLIxIntent): {
    valid: boolean;
    errors: string[];
    warnings: string[];
  } {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Validate required fields
    if (!intent.intent || intent.intent.trim().length === 0) {
      errors.push('Intent description is required');
    }

    if (!intent.contract.pre || intent.contract.pre.length === 0) {
      warnings.push('No preconditions specified');
    }

    if (!intent.contract.post || intent.contract.post.length === 0) {
      warnings.push('No postconditions specified');
    }

    if (!intent.plan.steps || intent.plan.steps.length === 0) {
      warnings.push('No plan steps specified');
    }

    // Validate plan step IDs are unique
    const stepIds = intent.plan.steps.map(s => s.id);
    const duplicateIds = stepIds.filter((id, index) => stepIds.indexOf(id) !== index);
    if (duplicateIds.length > 0) {
      errors.push(`Duplicate step IDs: ${duplicateIds.join(', ')}`);
    }

    // Validate dependencies reference existing steps
    const validStepIds = new Set(stepIds);
    for (const dep of intent.plan.deps) {
      if (!validStepIds.has(dep.step)) {
        errors.push(`Dependency references non-existent step: ${dep.step}`);
      }
      for (const depId of dep.depends_on) {
        if (!validStepIds.has(depId)) {
          errors.push(`Dependency references non-existent step: ${depId}`);
        }
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
    };
  }
}

