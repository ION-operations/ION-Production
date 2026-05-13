/**
 * TLA+ Backend Compiler
 * 
 * Compiles Core-PLIx to TLA+ modules for formal verification
 * Based on pipeline_specification.md
 */

import type { PLIxIntent } from '../models/schema';
import type { TypeJudgment } from '../semantics/annotated-typing';

/**
 * TLA+ Module
 */
export interface TLAPlusModule {
  /** Module name */
  name: string;
  
  /** EXTENDS declarations */
  extends: string[];
  
  /** VARIABLES declarations */
  variables: string[];
  
  /** Init predicate */
  init: string[];
  
  /** Actions */
  actions: TLAPlusAction[];
  
  /** Invariants */
  invariants: TLAPlusInvariant[];
  
  /** Temporal properties */
  properties: TLAPlusProperty[];
  
  /** Spec formula */
  spec: string;
  
  /** Theorems */
  theorems: TLAPlusTheorem[];
}

export interface TLAPlusAction {
  name: string;
  definition: string[];
}

export interface TLAPlusInvariant {
  name: string;
  formula: string;
}

export interface TLAPlusProperty {
  name: string;
  formula: string;
  type: 'safety' | 'liveness';
}

export interface TLAPlusTheorem {
  name: string;
  formula: string;
}

/**
 * TLA+ Backend Compiler
 */
export class TLAPlusBackend {
  /**
   * Compile PLIx intent to TLA+ module
   */
  compile(intent: PLIxIntent, typeJudgment?: TypeJudgment): TLAPlusModule {
    const moduleName = this.generateModuleName(intent);
    const variables = this.extractVariables(intent);
    const init = this.generateInit(intent, variables);
    const actions = this.generateActions(intent);
    const invariants = this.generateInvariants(intent);
    const properties = this.generateProperties(intent);
    const spec = this.generateSpec(intent, actions);
    const theorems = this.generateTheorems(intent);
    
    return {
      name: moduleName,
      extends: ['Naturals', 'Sequences', 'FiniteSets'],
      variables,
      init,
      actions,
      invariants,
      properties,
      spec,
      theorems
    };
  }
  
  /**
   * Generate module name from intent
   */
  private generateModuleName(intent: PLIxIntent): string {
    // Extract meaningful name from entity tag
    const entity = (intent as any).entity || 'Intent';
    const parts = entity.split('/');
    const name = parts[parts.length - 1] || 'Intent';
    
    // Capitalize and remove special characters
    return name
      .replace(/[^a-zA-Z0-9]/g, '_')
      .replace(/^[a-z]/, (c: string) => c.toUpperCase()) + 'Spec';
  }
  
  /**
   * Extract variables from intent
   */
  private extractVariables(intent: PLIxIntent): string[] {
    const variables = new Set<string>();
    
    // Extract from contract (preconditions + postconditions)
    for (const pre of intent.contract.pre) {
      const vars = this.extractVariablesFromConstraint(pre);
      vars.forEach(v => variables.add(v));
    }
    
    for (const post of intent.contract.post) {
      const vars = this.extractVariablesFromConstraint(post);
      vars.forEach(v => variables.add(v));
    }
    
    // Extract from plan steps
    for (const step of intent.plan.steps) {
      const stepId = step.id || step.step;
      variables.add(stepId + '_state');
      variables.add(stepId + '_result');
    }
    
    return Array.from(variables);
  }
  
  /**
   * Extract variables from constraint
   */
  private extractVariablesFromConstraint(constraint: any): string[] {
    if (typeof constraint === 'string') {
      // Extract identifiers from string constraint
      const matches = constraint.match(/[a-zA-Z_][a-zA-Z0-9_]*/g);
      return matches || [];
    } else if (constraint.expr) {
      return [constraint.expr];
    }
    
    return [];
  }
  
  /**
   * Generate Init predicate
   */
  private generateInit(intent: PLIxIntent, variables: string[]): string[] {
    const init: string[] = [];
    
    // Initialize preconditions as TRUE
    for (const pre of intent.contract.pre) {
      if (typeof pre === 'string') {
        const varName = pre.split(/[=<>]/)[0].trim();
        init.push(`${varName} = TRUE`);
      } else if (pre.expr) {
        init.push(`${pre.expr} = TRUE`);
      }
    }
    
    // Initialize step states
    for (const step of intent.plan.steps) {
      const stepId = step.id || step.step;
      init.push(`${stepId}_state = "pending"`);
      init.push(`${stepId}_result = NULL`);
    }
    
    return init;
  }
  
  /**
   * Generate actions from plan steps
   */
  private generateActions(intent: PLIxIntent): TLAPlusAction[] {
    const actions: TLAPlusAction[] = [];
    
    for (const step of intent.plan.steps) {
      const stepId = step.id || step.step;
      const actionDef: string[] = [];
      
      // Action precondition (dependencies satisfied)
      if (step.depends_on && step.depends_on.length > 0) {
        const depConditions = step.depends_on.map(dep => `${dep}_state = "completed"`);
        actionDef.push(`/\\ ${depConditions.join(' /\\ ')}`);
      } else {
        actionDef.push(`/\\ ${stepId}_state = "pending"`);
      }
      
      // Action execution
      actionDef.push(`/\\ ${stepId}_state' = "completed"`);
      actionDef.push(`/\\ ${stepId}_result' = Execute_${stepId}`);
      
      // UNCHANGED for other variables
      const unchangedVars = this.extractVariables(intent)
        .filter(v => !v.startsWith(stepId))
        .map(v => v);
      
      if (unchangedVars.length > 0) {
        actionDef.push(`/\\ UNCHANGED <<${unchangedVars.join(', ')}>>`);
      }
      
      actions.push({
        name: `${stepId}Action`,
        definition: actionDef
      });
    }
    
    return actions;
  }
  
  /**
   * Generate invariants from contract
   */
  private generateInvariants(intent: PLIxIntent): TLAPlusInvariant[] {
    const invariants: TLAPlusInvariant[] = [];
    
    // Precondition invariant
    if (intent.contract.pre.length > 0) {
      const preconditions = intent.contract.pre.map(pre => 
        typeof pre === 'string' ? pre : pre.expr || 'TRUE'
      );
      invariants.push({
        name: 'PreconditionInvariant',
        formula: preconditions.join(' /\\ ')
      });
    }
    
    // Postcondition safety property
    if (intent.contract.post.length > 0) {
      const postconditions = intent.contract.post.map(post => 
        typeof post === 'string' ? post : post.expr || 'TRUE'
      );
      invariants.push({
        name: 'PostconditionSafety',
        formula: `AllStepsCompleted => (${postconditions.join(' /\\ ')})`
      });
    }
    
    return invariants;
  }
  
  /**
   * Generate temporal properties
   */
  private generateProperties(intent: PLIxIntent): TLAPlusProperty[] {
    const properties: TLAPlusProperty[] = [];
    
    // Liveness: Eventually all steps complete
    properties.push({
      name: 'EventualCompletion',
      formula: '<>AllStepsCompleted',
      type: 'liveness'
    });
    
    // Safety: No step fails
    properties.push({
      name: 'NoFailures',
      formula: '[]NoStepFailed',
      type: 'safety'
    });
    
    return properties;
  }
  
  /**
   * Generate spec formula
   */
  private generateSpec(intent: PLIxIntent, actions: TLAPlusAction[]): string {
    const actionNames = actions.map(a => a.name).join(' \\/ ');
    const weakFairness = actions.map(a => `WF_vars(${a.name})`).join(' /\\ ');
    
    return `Init /\\ [][${actionNames}]_vars /\\ ${weakFairness}`;
  }
  
  /**
   * Generate theorems
   */
  private generateTheorems(intent: PLIxIntent): TLAPlusTheorem[] {
    const theorems: TLAPlusTheorem[] = [];
    
    // Main correctness theorem
    if (intent.contract.post.length > 0) {
      const postconditions = intent.contract.post.map(post => 
        typeof post === 'string' ? post : post.expr || 'TRUE'
      );
      
      theorems.push({
        name: 'Correctness',
        formula: `Spec => [](AllStepsCompleted => (${postconditions.join(' /\\ ')}))`
      });
    }
    
    return theorems;
  }
  
  /**
   * Serialize TLA+ module to text
   */
  serializeModule(module: TLAPlusModule): string {
    const lines: string[] = [];
    
    // Module header
    lines.push(`---- MODULE ${module.name} ----`);
    lines.push('');
    
    // EXTENDS
    lines.push(`EXTENDS ${module.extends.join(', ')}`);
    lines.push('');
    
    // VARIABLES
    lines.push(`VARIABLES ${module.variables.join(', ')}`);
    lines.push('');
    
    // Init
    lines.push('Init ==');
    for (const initLine of module.init) {
      lines.push(`  /\\ ${initLine}`);
    }
    lines.push('');
    
    // Actions
    for (const action of module.actions) {
      lines.push(`${action.name} ==`);
      for (const line of action.definition) {
        lines.push(`  ${line}`);
      }
      lines.push('');
    }
    
    // Helper predicates
    lines.push('AllStepsCompleted ==');
    for (let i = 0; i < module.actions.length; i++) {
      const stepVar = module.variables.find(v => v.includes('state'));
      if (stepVar) {
        const prefix = i === 0 ? '  ' : '  /\\ ';
        lines.push(`${prefix}${stepVar} = "completed"`);
      }
    }
    lines.push('');
    
    lines.push('NoStepFailed ==');
    lines.push('  /\\ \\A v \\in DOMAIN variables: v # "failed"');
    lines.push('');
    
    // Invariants
    for (const inv of module.invariants) {
      lines.push(`${inv.name} == ${inv.formula}`);
      lines.push('');
    }
    
    // Spec
    lines.push(`Spec == ${module.spec}`);
    lines.push('');
    
    // Theorems
    for (const thm of module.theorems) {
      lines.push(`THEOREM ${thm.name} == ${thm.formula}`);
      lines.push('');
    }
    
    lines.push('====');
    
    return lines.join('\n');
  }
}

