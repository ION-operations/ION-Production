/**
 * OPA (Open Policy Agent) Backend Compiler
 * 
 * Compiles Core-PLIx to OPA/Rego policies for runtime enforcement
 * Based on pipeline_specification.md
 */

import type { PLIxIntent } from '../models/schema';
import type { EffectRow } from '../semantics/annotated-typing';

/**
 * OPA Policy Module
 */
export interface OPAPolicyModule {
  /** Package name */
  package: string;
  
  /** Import statements */
  imports: string[];
  
  /** Rules */
  rules: OPARule[];
  
  /** Helper functions */
  helpers: OPAHelper[];
}

export interface OPARule {
  name: string;
  path: string[]; // Rule path (e.g., ['allow', 'execute', 'step'])
  conditions: string[];
  result?: any; // Rule result (true/false/object)
}

export interface OPAHelper {
  name: string;
  params: string[];
  body: string[];
}

/**
 * OPA Backend Compiler
 */
export class OPABackend {
  /**
   * Compile PLIx intent to OPA policy
   */
  compile(intent: PLIxIntent, effectRow?: EffectRow): OPAPolicyModule {
    const packageName = this.generatePackageName(intent);
    const rules = this.generateRules(intent, effectRow);
    const helpers = this.generateHelpers(intent);
    
    return {
      package: packageName,
      imports: ['data.plix', 'future.keywords.if', 'future.keywords.contains'],
      rules,
      helpers
    };
  }
  
  /**
   * Generate package name
   */
  private generatePackageName(intent: PLIxIntent): string {
    const entity = (intent as any).entity || 'intent';
    const parts = entity.split('/').filter((p: string) => p);
    const name = parts.join('.').replace(/[^a-zA-Z0-9.]/g, '_');
    
    return `plix.${name}`;
  }
  
  /**
   * Generate OPA rules from intent
   */
  private generateRules(intent: PLIxIntent, effectRow?: EffectRow): OPARule[] {
    const rules: OPARule[] = [];
    
    // Rule 1: Allow execution if preconditions met
    const preconditionChecks = intent.contract.pre.map(pre => 
      this.constraintToRego(pre, 'input.state')
    );
    
    rules.push({
      name: 'allow_execution',
      path: ['allow', 'execute'],
      conditions: preconditionChecks,
      result: true
    });
    
    // Rule 2: Check capabilities
    if (effectRow) {
      const capabilityChecks = this.effectRowToCapabilityChecks(effectRow);
      
      rules.push({
        name: 'check_capabilities',
        path: ['allow', 'capabilities'],
        conditions: capabilityChecks,
        result: true
      });
    }
    
    // Rule 3: Allow step execution based on dependencies
    for (const step of intent.plan.steps) {
      const stepId = step.id || step.step;
      const conditions: string[] = [];
      
      // Check dependencies
      if (step.depends_on && step.depends_on.length > 0) {
        for (const dep of step.depends_on) {
          conditions.push(`input.step_states["${dep}"] == "completed"`);
        }
      } else {
        conditions.push(`input.step_states["${stepId}"] == "pending"`);
      }
      
      rules.push({
        name: `allow_step_${stepId}`,
        path: ['allow', 'step', stepId],
        conditions,
        result: true
      });
    }
    
    // Rule 4: Validate postconditions
    const postconditionChecks = intent.contract.post.map(post => 
      this.constraintToRego(post, 'input.result_state')
    );
    
    rules.push({
      name: 'validate_postconditions',
      path: ['valid', 'postconditions'],
      conditions: postconditionChecks,
      result: true
    });
    
    // Rule 5: Policy compliance
    rules.push({
      name: 'policy_compliant',
      path: ['allow', 'policy'],
      conditions: [
        'input.user.authenticated == true',
        'input.user.authorized == true',
        'not denied_by_policy'
      ],
      result: true
    });
    
    return rules;
  }
  
  /**
   * Generate helper functions
   */
  private generateHelpers(intent: PLIxIntent): OPAHelper[] {
    const helpers: OPAHelper[] = [];
    
    // Helper: Check if all dependencies satisfied
    helpers.push({
      name: 'dependencies_satisfied',
      params: ['step_id'],
      body: [
        'deps := data.dependencies[step_id]',
        'satisfied := {dep | dep := deps[_]; input.step_states[dep] == "completed"}',
        'count(satisfied) == count(deps)'
      ]
    });
    
    // Helper: Check if step can compensate
    helpers.push({
      name: 'can_compensate',
      params: ['step_id'],
      body: [
        'step_state := input.step_states[step_id]',
        'step_state == "failed"',
        'data.compensations[step_id]'
      ]
    });
    
    // Helper: Policy denial check
    helpers.push({
      name: 'denied_by_policy',
      params: [],
      body: [
        'some violation in data.policy_violations',
        'violation.applies_to(input)'
      ]
    });
    
    return helpers;
  }
  
  /**
   * Generate assertions
   */
  private generateAssertions(intent: PLIxIntent): OPAAssertion[] {
    const assertions: OPAAssertion[] = [];
    
    // Assert postconditions after execution
    if (intent.contract.post.length > 0) {
      const postconditions = intent.contract.post.map(post => 
        this.constraintToRego(post, 'result_state')
      );
      
      assertions.push({
        name: 'postconditions_hold',
        formula: `all_steps_completed => (${postconditions.join(' && ')})`
      });
    }
    
    return assertions;
  }
  
  /**
   * Generate commands
   */
  private generateCommands(intent: PLIxIntent): AlloyCommand[] {
    return [
      { type: 'run', target: 'allow.execute', scope: '' },
      { type: 'check', target: 'valid.postconditions', scope: '' }
    ];
  }
  
  /**
   * Convert constraint to Rego expression
   */
  private constraintToRego(constraint: any, stateVar: string): string {
    if (typeof constraint === 'string') {
      // Replace variable references with state access
      return constraint.replace(/([a-zA-Z_][a-zA-Z0-9_]*)/g, `${stateVar}["$1"]`);
    } else if (constraint.expr) {
      return `${stateVar}["${constraint.expr}"] == true`;
    }
    
    return 'true';
  }
  
  /**
   * Convert effect row to capability checks
   */
  private effectRowToCapabilityChecks(effects: EffectRow): string[] {
    const checks: string[] = [];
    
    for (const [effect, present] of Object.entries(effects)) {
      if (present === true) {
        checks.push(`input.capabilities["${effect}"] == true`);
      }
    }
    
    return checks;
  }
  
  /**
   * Serialize OPA policy to Rego
   */
  serializePolicy(policy: OPAPolicyModule): string {
    const lines: string[] = [];
    
    // Package declaration
    lines.push(`package ${policy.package}`);
    lines.push('');
    
    // Imports
    for (const imp of policy.imports) {
      lines.push(`import ${imp}`);
    }
    lines.push('');
    
    // Default deny
    lines.push('default allow = false');
    lines.push('');
    
    // Rules
    for (const rule of policy.rules) {
      const path = rule.path.join('.');
      lines.push(`${path} {`);
      
      for (const condition of rule.conditions) {
        lines.push(`  ${condition}`);
      }
      
      lines.push('}');
      lines.push('');
    }
    
    // Helpers
    for (const helper of policy.helpers) {
      const params = helper.params.join(', ');
      lines.push(`${helper.name}(${params}) {`);
      
      for (const line of helper.body) {
        lines.push(`  ${line}`);
      }
      
      lines.push('}');
      lines.push('');
    }
    
    return lines.join('\n');
  }
}

