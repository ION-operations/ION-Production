/**
 * Alloy Backend Compiler
 * 
 * Compiles Core-PLIx to Alloy models for structural verification
 * Based on pipeline_specification.md
 */

import type { PLIxIntent } from '../models/schema';

/**
 * Alloy Model
 */
export interface AlloyModel {
  /** Model name */
  name: string;
  
  /** Signatures */
  signatures: AlloySignature[];
  
  /** Facts */
  facts: AlloyFact[];
  
  /** Predicates */
  predicates: AlloyPredicate[];
  
  /** Functions */
  functions: AlloyFunction[];
  
  /** Assertions */
  assertions: AlloyAssertion[];
  
  /** Commands (run/check) */
  commands: AlloyCommand[];
}

export interface AlloySignature {
  name: string;
  extends?: string;
  fields: Array<{ name: string; type: string; multiplicity?: string }>;
  facts?: string[];
}

export interface AlloyFact {
  name: string;
  formula: string[];
}

export interface AlloyPredicate {
  name: string;
  params: Array<{ name: string; type: string }>;
  body: string[];
}

export interface AlloyFunction {
  name: string;
  params: Array<{ name: string; type: string }>;
  returnType: string;
  body: string;
}

export interface AlloyAssertion {
  name: string;
  formula: string;
}

export interface AlloyCommand {
  type: 'run' | 'check';
  target: string;
  scope?: string;
}

/**
 * Alloy Backend Compiler
 */
export class AlloyBackend {
  /**
   * Compile PLIx intent to Alloy model
   */
  compile(intent: PLIxIntent): AlloyModel {
    const modelName = this.generateModelName(intent);
    const signatures = this.generateSignatures(intent);
    const facts = this.generateFacts(intent);
    const predicates = this.generatePredicates(intent);
    const functions = this.generateFunctions(intent);
    const assertions = this.generateAssertions(intent);
    const commands = this.generateCommands(intent);
    
    return {
      name: modelName,
      signatures,
      facts,
      predicates,
      functions,
      assertions,
      commands
    };
  }
  
  /**
   * Generate model name
   */
  private generateModelName(intent: PLIxIntent): string {
    const entity = (intent as any).entity || 'Intent';
    const parts = entity.split('/');
    const name = parts[parts.length - 1] || 'Intent';
    
    return name.replace(/[^a-zA-Z0-9]/g, '_') + 'Model';
  }
  
  /**
   * Generate signatures from entities
   */
  private generateSignatures(intent: PLIxIntent): AlloySignature[] {
    const signatures: AlloySignature[] = [];
    
    // State signature
    signatures.push({
      name: 'State',
      fields: [
        { name: 'step_states', type: 'Step -> StepState' },
        { name: 'step_results', type: 'Step -> Result' },
        { name: 'evidence', type: 'set Evidence' }
      ]
    });
    
    // Step signature
    const stepNames = intent.plan.steps.map(s => s.id || s.step);
    signatures.push({
      name: 'Step',
      fields: []
    });
    
    // StepState enum
    signatures.push({
      name: 'StepState',
      extends: 'abstract',
      fields: []
    });
    
    signatures.push({ name: 'Pending', extends: 'StepState', fields: [] });
    signatures.push({ name: 'Executing', extends: 'StepState', fields: [] });
    signatures.push({ name: 'Completed', extends: 'StepState', fields: [] });
    signatures.push({ name: 'Failed', extends: 'StepState', fields: [] });
    
    // Result signature
    signatures.push({
      name: 'Result',
      fields: [
        { name: 'value', type: 'lone Value' }
      ]
    });
    
    // Evidence signature
    signatures.push({
      name: 'Evidence',
      fields: [
        { name: 'step', type: 'Step' },
        { name: 'witness', type: 'Witness' }
      ]
    });
    
    return signatures;
  }
  
  /**
   * Generate facts from contract
   */
  private generateFacts(intent: PLIxIntent): AlloyFact[] {
    const facts: AlloyFact[] = [];
    
    // Contract fact (preconditions => postconditions)
    const preconditions = intent.contract.pre.map(pre => 
      this.constraintToAlloy(pre)
    );
    
    const postconditions = intent.contract.post.map(post => 
      this.constraintToAlloy(post)
    );
    
    const contractFormula = [
      'all s, s\': State |',
      `  (${preconditions.join(' and ')}) and`,
      `  ExecutePlan[s, s\'] =>`,
      `  (${postconditions.join(' and ')})`
    ];
    
    facts.push({
      name: 'Contract',
      formula: contractFormula
    });
    
    // Dependency fact (execution order)
    const depFormula: string[] = ['all s, s\': State |'];
    for (const step of intent.plan.steps) {
      if (step.depends_on && step.depends_on.length > 0) {
        const stepId = step.id || step.step;
        const deps = step.depends_on.map(dep => `s.step_states[${dep}] = Completed`).join(' and ');
        depFormula.push(`  s.step_states[${stepId}] = Executing => (${deps})`);
      }
    }
    
    facts.push({
      name: 'Dependencies',
      formula: depFormula
    });
    
    return facts;
  }
  
  /**
   * Generate predicates from plan
   */
  private generatePredicates(intent: PLIxIntent): AlloyPredicate[] {
    const predicates: AlloyPredicate[] = [];
    
    // ExecutePlan predicate
    const execBody: string[] = [];
    for (const step of intent.plan.steps) {
      const stepId = step.id || step.step;
      execBody.push(`Execute_${stepId}[s, s']`);
    }
    
    predicates.push({
      name: 'ExecutePlan',
      params: [{ name: 's', type: 'State' }, { name: 's\'', type: 'State' }],
      body: execBody
    });
    
    // Execute step predicates
    for (const step of intent.plan.steps) {
      const stepId = step.id || step.step;
      const stepBody = [
        `s.step_states[${stepId}] = Pending`,
        `s'.step_states[${stepId}] = Completed`,
        `s'.step_results[${stepId}] != NULL`
      ];
      
      predicates.push({
        name: `Execute_${stepId}`,
        params: [{ name: 's', type: 'State' }, { name: 's\'', type: 'State' }],
        body: stepBody
      });
    }
    
    return predicates;
  }
  
  /**
   * Generate functions
   */
  private generateFunctions(intent: PLIxIntent): AlloyFunction[] {
    // Can add helper functions if needed
    return [];
  }
  
  /**
   * Generate assertions
   */
  private generateAssertions(intent: PLIxIntent): AlloyAssertion[] {
    const assertions: AlloyAssertion[] = [];
    
    // Assert postconditions hold after execution
    if (intent.contract.post.length > 0) {
      const postconditions = intent.contract.post.map(post => 
        this.constraintToAlloy(post)
      );
      
      assertions.push({
        name: 'PostconditionHolds',
        formula: `all s, s': State | ExecutePlan[s, s'] => (${postconditions.join(' and ')})`
      });
    }
    
    return assertions;
  }
  
  /**
   * Generate commands
   */
  private generateCommands(intent: PLIxIntent): AlloyCommand[] {
    return [
      { type: 'run', target: 'ExecutePlan', scope: 'for 5' },
      { type: 'check', target: 'PostconditionHolds', scope: 'for 5' }
    ];
  }
  
  /**
   * Convert constraint to Alloy formula
   */
  private constraintToAlloy(constraint: any): string {
    if (typeof constraint === 'string') {
      // Simple string constraint
      return constraint.replace(/==/g, '=').replace(/&&/g, 'and').replace(/\|\|/g, 'or');
    } else if (constraint.expr) {
      return `${constraint.expr} = TRUE`;
    }
    
    return 'TRUE';
  }
  
  /**
   * Serialize Alloy model to text
   */
  serializeModel(model: AlloyModel): string {
    const lines: string[] = [];
    
    // Module name
    lines.push(`// ${model.name}`);
    lines.push('');
    
    // Signatures
    for (const sig of model.signatures) {
      if (sig.extends) {
        lines.push(`sig ${sig.name} extends ${sig.extends} {`);
      } else {
        lines.push(`sig ${sig.name} {`);
      }
      
      for (const field of sig.fields) {
        const mult = field.multiplicity || '';
        lines.push(`  ${field.name}: ${mult} ${field.type},`);
      }
      
      lines.push('}');
      
      if (sig.facts && sig.facts.length > 0) {
        lines.push('{');
        for (const fact of sig.facts) {
          lines.push(`  ${fact}`);
        }
        lines.push('}');
      }
      
      lines.push('');
    }
    
    // Facts
    for (const fact of model.facts) {
      lines.push(`fact ${fact.name} {`);
      for (const line of fact.formula) {
        lines.push(`  ${line}`);
      }
      lines.push('}');
      lines.push('');
    }
    
    // Predicates
    for (const pred of model.predicates) {
      const params = pred.params.map(p => `${p.name}: ${p.type}`).join(', ');
      lines.push(`pred ${pred.name}[${params}] {`);
      for (const line of pred.body) {
        lines.push(`  ${line}`);
      }
      lines.push('}');
      lines.push('');
    }
    
    // Functions
    for (const func of model.functions) {
      const params = func.params.map(p => `${p.name}: ${p.type}`).join(', ');
      lines.push(`fun ${func.name}[${params}]: ${func.returnType} {`);
      lines.push(`  ${func.body}`);
      lines.push('}');
      lines.push('');
    }
    
    // Assertions
    for (const assertion of model.assertions) {
      lines.push(`assert ${assertion.name} {`);
      lines.push(`  ${assertion.formula}`);
      lines.push('}');
      lines.push('');
    }
    
    // Commands
    for (const cmd of model.commands) {
      lines.push(`${cmd.type} ${cmd.target} ${cmd.scope || ''}`);
    }
    
    return lines.join('\n');
  }
}

