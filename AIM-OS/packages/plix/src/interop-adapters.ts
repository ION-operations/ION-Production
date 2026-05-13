/**
 * PLIx Interop Adapters
 * 
 * Compile PLIx to/from external systems (Temporal, OPA, PROV, PDDL)
 */

import { PLIxIntent, PLIxPlanStep } from './models/schema';

export interface TemporalWorkflow {
  workflowId: string;
  taskQueue: string;
  activities: Array<{
    name: string;
    type: string;
    input: any;
    retryPolicy?: any;
    timeout?: string;
  }>;
}

export interface OPAPolicy {
  package: string;
  rules: Array<{
    name: string;
    query: string;
  }>;
}

export interface PROVEntity {
  id: string;
  type: string;
  attributes: Record<string, any>;
}

export interface PROVActivity {
  id: string;
  type: string;
  startedAtTime: string;
  endedAtTime?: string;
  used: string[];
  generated: string[];
}

/**
 * PLIx → Temporal Adapter
 */
export class PLIxToTemporalAdapter {
  /**
   * Compile PLIx plan to Temporal workflow
   */
  static compile(plix: PLIxIntent): TemporalWorkflow {
    const activities = plix.plan.steps.map((step, index) => ({
      name: `${step.agent}_${step.tool}`,
      type: 'activity',
      input: {
        stepId: step.id,
        agent: step.agent,
        tool: step.tool,
        target: step.target,
        args: step.args,
      },
      retryPolicy: step.retry ? {
        maximumAttempts: step.retry.max_attempts,
        backoffCoefficient: step.retry.backoff === 'exponential' ? 2.0 : 1.0,
        initialInterval: `${step.retry.backoff_ms}ms`,
      } : undefined,
      timeout: `${plix.telemetry.timeouts.step}ms`,
    }));

    return {
      workflowId: `plix-${Date.now()}`,
      taskQueue: 'plix-tasks',
      activities,
    };
  }
}

/**
 * PLIx → OPA Adapter
 */
export class PLIxToOPAAdapter {
  /**
   * Compile PLIx contract to OPA Rego policy
   */
  static compile(plix: PLIxIntent): OPAPolicy {
    const rules: OPAPolicy['rules'] = [];

    // Compile preconditions
    for (let i = 0; i < plix.contract.pre.length; i++) {
      rules.push({
        name: `precondition_${i}`,
        query: `precondition_${i} { ${plix.contract.pre[i]} }`,
      });
    }

    // Compile postconditions
    for (let i = 0; i < plix.contract.post.length; i++) {
      rules.push({
        name: `postcondition_${i}`,
        query: `postcondition_${i} { ${plix.contract.post[i]} }`,
      });
    }

    // Compile policies
    for (let i = 0; i < plix.contract.policies.length; i++) {
      rules.push({
        name: `policy_${i}`,
        query: `policy_${i} { ${plix.contract.policies[i]} }`,
      });
    }

    return {
      package: 'plix.contract',
      rules,
    };
  }
}

/**
 * PLIx → PROV Adapter
 */
export class PLIxToPROVAdapter {
  /**
   * Compile PLIx execution to PROV entities and activities
   */
  static compile(plix: PLIxIntent, executionResult?: any): {
    entities: PROVEntity[];
    activities: PROVActivity[];
  } {
    const entities: PROVEntity[] = [];
    const activities: PROVActivity[] = [];

    // Create entity for the intent
    entities.push({
      id: `plix-intent-${plix.provenance.when}`,
      type: 'plix:Intent',
      attributes: {
        intent: plix.intent,
        scope: plix.context.scope,
        risk: plix.context.risk,
      },
    });

    // Create activities for each plan step
    for (const step of plix.plan.steps) {
      const activityId = `plix-step-${step.id}`;
      
      activities.push({
        id: activityId,
        type: 'plix:PlanStep',
        startedAtTime: plix.provenance.when,
        used: [`plix-intent-${plix.provenance.when}`],
        generated: plix.evidence.produce.map((e, i) => `evidence-${step.id}-${i}`),
      });

      // Create entities for evidence
      for (let i = 0; i < plix.evidence.produce.length; i++) {
        entities.push({
          id: `evidence-${step.id}-${i}`,
          type: `plix:Evidence:${plix.evidence.produce[i].type}`,
          attributes: {
            description: plix.evidence.produce[i].description,
            stepId: step.id,
          },
        });
      }
    }

    return { entities, activities };
  }
}

/**
 * PLIx → PDDL Adapter
 */
export class PLIxToPDDLAdapter {
  /**
   * Compile PLIx plan to PDDL domain/problem
   */
  static compile(plix: PLIxIntent): {
    domain: string;
    problem: string;
  } {
    // TODO: Implement PDDL compilation
    // For now, return stub
    return {
      domain: `(define (domain plix-domain)
  (:requirements :strips :typing)
  (:types agent tool target)
  (:predicates (can-execute ?a - agent ?t - tool))
)`,
      problem: `(define (problem plix-problem)
  (:domain plix-domain)
  (:objects ${plix.plan.steps.map(s => s.agent).join(' ')} - agent)
  (:init)
  (:goal (and ${plix.contract.post.join(' ')}))
)`,
    };
  }
}

