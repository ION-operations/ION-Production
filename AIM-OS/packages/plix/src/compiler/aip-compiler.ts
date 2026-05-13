/**
 * PLIX to AIP Compiler
 * 
 * Phase 2: Compiles PLIX contracts to AIP graph, resolves tags via HHNI/SEG,
 * compiles to APOE execution plans, and generates VIF witness requirements
 */

import type { PLIxIntent, PLIxPlanStep } from '../models/schema';
import type { PLIXConstraint } from '../models/constraints';
import type { ErrorClause } from '../models/errors';
import type { PLIXTagRegistry } from '../registry/tag-registry';

export interface AIPGraphNode {
  id: string;
  type: 'entity' | 'action' | 'capability' | 'constraint' | 'test' | 'evidence';
  tag?: string;
  resolved?: any; // Resolved entity/action from HHNI/SEG
  metadata?: Record<string, any>;
}

export interface AIPGraphEdge {
  source: string;
  target: string;
  type: 'depends_on' | 'compensates' | 'requires' | 'produces' | 'validates';
  metadata?: Record<string, any>;
}

export interface AIPGraph {
  nodes: AIPGraphNode[];
  edges: AIPGraphEdge[];
  metadata?: Record<string, any>;
}

export interface APOECompilationResult {
  plan: any; // APOE ExecutionPlan structure
  witnessRequirements: VIFWitnessRequirement[];
  resolvedTags: Map<string, any>;
  errors: string[];
  warnings: string[];
}

export interface VIFWitnessRequirement {
  operation: string;
  stepId?: string;
  requiredConfidence: number;
  evidenceTypes: string[];
  metadata?: Record<string, any>;
}

export interface TagResolutionResult {
  tag: string;
  resolved: any | null;
  source: 'hhni' | 'seg' | 'cmc' | 'cache' | 'not_found';
  confidence: number;
  metadata?: Record<string, any>;
}

export class PLIXToAIPCompiler {
  private tagCache: Map<string, TagResolutionResult>;
  private hhniClient: any; // HHNI client (to be injected)
  private segClient: any; // SEG client (to be injected)
  private cmcClient: any; // CMC client (to be injected)
  private tagRegistry: PLIXTagRegistry | null; // Tag registry (to be injected)
  
  constructor(options?: {
    hhniClient?: any;
    segClient?: any;
    cmcClient?: any;
    tagRegistry?: PLIXTagRegistry;
  }) {
    this.tagCache = new Map();
    this.hhniClient = options?.hhniClient;
    this.segClient = options?.segClient;
    this.cmcClient = options?.cmcClient;
    this.tagRegistry = options?.tagRegistry || null;
  }
  
  /**
   * Compile PLIX intent to AIP graph
   */
  async compileToAIPGraph(intent: PLIxIntent): Promise<AIPGraph> {
    const nodes: AIPGraphNode[] = [];
    const edges: AIPGraphEdge[] = [];
    
    // Resolve entity tag
    const entityTag = (intent as any).entity;
    if (entityTag) {
      const entityResolved = await this.resolveTag(entityTag);
      nodes.push({
        id: 'entity',
        type: 'entity',
        tag: entityTag,
        resolved: entityResolved.resolved,
        metadata: {
          source: entityResolved.source,
          confidence: entityResolved.confidence
        }
      });
    }
    
    // Resolve action/capability tag
    const actionTag = (intent as any).action?.value;
    if (actionTag) {
      const actionResolved = await this.resolveTag(actionTag);
      nodes.push({
        id: 'action',
        type: (intent as any).action?.type === 'capability' ? 'capability' : 'action',
        tag: actionTag,
        resolved: actionResolved.resolved,
        metadata: {
          source: actionResolved.source,
          confidence: actionResolved.confidence
        }
      });
      
      // Link action to entity
      if (entityTag) {
        edges.push({
          source: 'entity',
          target: 'action',
          type: 'requires'
        });
      }
    }
    
    // Add constraint nodes
    let constraintIndex = 0;
    for (const pre of intent.contract.pre) {
      const constraintId = `pre_${constraintIndex++}`;
      nodes.push({
        id: constraintId,
        type: 'constraint',
        metadata: {
          constraint: pre,
          type: 'precondition'
        }
      });
      
      // Link constraint to action
      if (actionTag) {
        edges.push({
          source: constraintId,
          target: 'action',
          type: 'validates'
        });
      }
    }
    
    constraintIndex = 0;
    for (const post of intent.contract.post) {
      const constraintId = `post_${constraintIndex++}`;
      nodes.push({
        id: constraintId,
        type: 'constraint',
        metadata: {
          constraint: post,
          type: 'postcondition'
        }
      });
      
      // Link constraint to action
      if (actionTag) {
        edges.push({
          source: 'action',
          target: constraintId,
          type: 'produces'
        });
      }
    }
    
    // Add test nodes
    let testIndex = 0;
    for (const test of (intent as any).tests || []) {
      const testId = `test_${testIndex++}`;
      nodes.push({
        id: testId,
        type: 'test',
        metadata: {
          test: test.test || test
        }
      });
      
      // Link test to action
      if (actionTag) {
        edges.push({
          source: 'action',
          target: testId,
          type: 'validates'
        });
      }
    }
    
    // Add evidence nodes
    let evidenceIndex = 0;
    for (const ev of (intent as any).evidence || []) {
      const evId = `evidence_${evidenceIndex++}`;
      const evTag = typeof ev === 'string' ? ev : ev;
      const evResolved = await this.resolveTag(evTag);
      
      nodes.push({
        id: evId,
        type: 'evidence',
        tag: evTag,
        resolved: evResolved.resolved,
        metadata: {
          source: evResolved.source,
          confidence: evResolved.confidence
        }
      });
      
      // Link evidence to action
      if (actionTag) {
        edges.push({
          source: evId,
          target: 'action',
          type: 'requires'
        });
      }
    }
    
    // Add plan step nodes and dependencies
    for (const step of intent.plan.steps) {
      const stepId = step.id || step.step;
      nodes.push({
        id: stepId,
        type: 'action',
        metadata: {
          step: step.step,
          tool: step.tool,
          agent: step.agent,
          target: step.target,
          args: step.args
        }
      });
      
      // Add dependencies
      if (step.depends_on) {
        for (const dep of step.depends_on) {
          edges.push({
            source: dep,
            target: stepId,
            type: 'depends_on'
          });
        }
      }
      
      // Add compensation edges
      if (step.compensate) {
        const compensateId = `${stepId}_compensate`;
        nodes.push({
          id: compensateId,
          type: 'action',
          metadata: {
            action: step.compensate.action,
            tool: step.compensate.tool,
            args: step.compensate.args
          }
        });
        
        edges.push({
          source: stepId,
          target: compensateId,
          type: 'compensates'
        });
      }
    }
    
    return {
      nodes,
      edges,
      metadata: {
        intent: intent.intent,
        compiledAt: new Date().toISOString()
      }
    };
  }
  
  /**
   * Resolve tag via Tag Registry (preferred) or HHNI/SEG/CMC
   */
  async resolveTag(tag: string): Promise<TagResolutionResult> {
    // Check cache first
    if (this.tagCache.has(tag)) {
      const cached = this.tagCache.get(tag)!;
      return {
        ...cached,
        source: 'cache' as const
      };
    }
    
    // Try tag registry first (Phase 3)
    if (this.tagRegistry) {
      try {
        const registryResult = await this.tagRegistry.resolveTag(tag);
        if (registryResult) {
          const result: TagResolutionResult = {
            tag,
            resolved: registryResult.resolved,
            source: 'cache', // Registry has its own caching
            confidence: 0.90, // Registry tags are authoritative
            metadata: {
              namespace: registryResult.namespace,
              path: registryResult.path,
              revision: registryResult.revision,
              authorityTier: registryResult.authorityTier
            }
          };
          this.tagCache.set(tag, result);
          return result;
        }
      } catch (error) {
        // Fall through to other resolution methods
      }
    }
    
    // Extract tag components
    const tagMatch = tag.match(/^plix:\/\/([^#]+)(?:#rev@(.+))?$/);
    if (!tagMatch) {
      return {
        tag,
        resolved: null,
        source: 'not_found',
        confidence: 0.0
      };
    }
    
    const [, path, revision] = tagMatch;
    const [namespace, ...pathParts] = path.split('/');
    
    // Try HHNI first (for entity/action resolution)
    if (this.hhniClient) {
      try {
        const hhniResult = await this.queryHHNI(tag, namespace, pathParts);
        if (hhniResult) {
          const result: TagResolutionResult = {
            tag,
            resolved: hhniResult,
            source: 'hhni',
            confidence: 0.85, // HHNI confidence
            metadata: {
              namespace,
              path: pathParts.join('/'),
              revision
            }
          };
          this.tagCache.set(tag, result);
          return result;
        }
      } catch (error) {
        // Fall through to next resolution method
      }
    }
    
    // Try SEG (for evidence/lineage)
    if (this.segClient) {
      try {
        const segResult = await this.querySEG(tag, namespace, pathParts);
        if (segResult) {
          const result: TagResolutionResult = {
            tag,
            resolved: segResult,
            source: 'seg',
            confidence: 0.80, // SEG confidence
            metadata: {
              namespace,
              path: pathParts.join('/'),
              revision
            }
          };
          this.tagCache.set(tag, result);
          return result;
        }
      } catch (error) {
        // Fall through to next resolution method
      }
    }
    
    // Try CMC (for general atom lookup)
    if (this.cmcClient) {
      try {
        const cmcResult = await this.queryCMC(tag, namespace, pathParts);
        if (cmcResult) {
          const result: TagResolutionResult = {
            tag,
            resolved: cmcResult,
            source: 'cmc',
            confidence: 0.75, // CMC confidence
            metadata: {
              namespace,
              path: pathParts.join('/'),
              revision
            }
          };
          this.tagCache.set(tag, result);
          return result;
        }
      } catch (error) {
        // Fall through
      }
    }
    
    // Not found
    const result: TagResolutionResult = {
      tag,
      resolved: null,
      source: 'not_found',
      confidence: 0.0,
      metadata: {
        namespace,
        path: pathParts.join('/'),
        revision
      }
    };
    
    this.tagCache.set(tag, result);
    return result;
  }
  
  /**
   * Query HHNI for tag resolution
   */
  private async queryHHNI(tag: string, namespace: string, pathParts: string[]): Promise<any> {
    // Simplified - actual implementation would use HHNI retrieval
    // Query by tag pattern: plix://namespace/path
    const query = `tag:${tag}`;
    
    if (this.hhniClient && typeof this.hhniClient.retrieve === 'function') {
      const result = await this.hhniClient.retrieve(query, { top_k: 1 });
      if (result && result.selected_items && result.selected_items.length > 0) {
        return result.selected_items[0];
      }
    }
    
    return null;
  }
  
  /**
   * Query SEG for tag resolution
   */
  private async querySEG(tag: string, namespace: string, pathParts: string[]): Promise<any> {
    // Simplified - actual implementation would use SEG query
    // Query by tag pattern for evidence/lineage
    if (this.segClient && typeof this.segClient.query === 'function') {
      const result = await this.segClient.query({
        tag: tag,
        limit: 1
      });
      if (result && result.length > 0) {
        return result[0];
      }
    }
    
    return null;
  }
  
  /**
   * Query CMC for tag resolution
   */
  private async queryCMC(tag: string, namespace: string, pathParts: string[]): Promise<any> {
    // Simplified - actual implementation would use CMC retrieve_memory
    // Query by tag pattern
    if (this.cmcClient && typeof this.cmcClient.retrieve === 'function') {
      const result = await this.cmcClient.retrieve({
        query: tag,
        tags: { tag: tag },
        limit: 1
      });
      if (result && result.results && result.results.length > 0) {
        return result.results[0];
      }
    }
    
    return null;
  }
  
  /**
   * Compile PLIX intent to APOE execution plan
   */
  async compileToAPOE(intent: PLIxIntent): Promise<APOECompilationResult> {
    const errors: string[] = [];
    const warnings: string[] = [];
    const resolvedTags = new Map<string, any>();
    const witnessRequirements: VIFWitnessRequirement[] = [];
    
    // Build AIP graph first
    const aipGraph = await this.compileToAIPGraph(intent);
    
    // Convert to APOE ExecutionPlan structure
    const planSteps: any[] = [];
    const planRoles: Record<string, any> = {};
    const planDependencies: Record<string, string[]> = {};
    const planGates: any[] = [];
    
    // Process plan steps
    for (const step of intent.plan.steps) {
      const stepId = step.id || step.step;
      
      // Create role if needed
      if (step.agent && !planRoles[step.agent]) {
        planRoles[step.agent] = {
          type: 'llm', // Default - could be inferred from agent type
          model: 'gpt-4-turbo', // Default
          temperature: 0.7
        };
      }
      
      // Convert step to APOE Step format
      const apoeStep: any = {
        id: stepId,
        name: step.step,
        role: step.agent || 'operator',
        role_name: step.agent,
        description: step.step,
        budget: step.retry ? {
          tokens: 10000, // Default
          time: step.retry.backoff_ms || 30000,
          tools: 10
        } : undefined,
        gates: []
      };
      
      // Add confidence gate if specified
      if (step.confidence_threshold) {
        planGates.push({
          id: `${stepId}_confidence`,
          step_id: stepId,
          condition: `confidence >= ${step.confidence_threshold}`,
          on_fail: 'fail'
        });
      }
      
      // Add error handling gates
      if (step.errors) {
        for (const errorClause of step.errors) {
          planGates.push({
            id: `${stepId}_${errorClause.error}`,
            step_id: stepId,
            condition: `error_type == "${errorClause.error}"`,
            on_fail: errorClause.action,
            config: errorClause.config
          });
        }
      }
      
      planSteps.push(apoeStep);
      
      // Add dependencies
      if (step.depends_on && step.depends_on.length > 0) {
        planDependencies[stepId] = step.depends_on;
      }
      
      // Generate witness requirements
      witnessRequirements.push({
        operation: `execute_step:${stepId}`,
        stepId: stepId,
        requiredConfidence: step.confidence_threshold || intent.telemetry.confidenceThresholds.minimum,
        evidenceTypes: step.evidence_required || [],
        metadata: {
          step: step.step,
          tool: step.tool,
          agent: step.agent
        }
      });
    }
    
    // Add plan-level witness requirement
    witnessRequirements.push({
      operation: `execute_plan:${intent.intent}`,
      requiredConfidence: intent.telemetry.confidenceThresholds.minimum,
      evidenceTypes: (intent as any).evidence?.map((ev: any) => typeof ev === 'string' ? ev : ev) || [],
      metadata: {
        intent: intent.intent,
        totalSteps: planSteps.length
      }
    });
    
    // Build APOE ExecutionPlan structure
    const apoePlan = {
      name: intent.intent,
      roles: planRoles,
      steps: planSteps,
      gates: planGates,
      dependencies: planDependencies,
      metadata: {
        compiled_from: 'plix',
        compiled_at: new Date().toISOString(),
        aip_graph: aipGraph
      }
    };
    
    return {
      plan: apoePlan,
      witnessRequirements,
      resolvedTags,
      errors,
      warnings
    };
  }
  
  /**
   * Generate VIF witness requirements from PLIX evidence clauses
   */
  generateWitnessRequirements(intent: PLIxIntent): VIFWitnessRequirement[] {
    const requirements: VIFWitnessRequirement[] = [];
    
    // Plan-level witness requirement
    requirements.push({
      operation: `execute_plan:${intent.intent}`,
      requiredConfidence: intent.telemetry.confidenceThresholds.minimum,
      evidenceTypes: (intent as any).evidence?.map((ev: any) => typeof ev === 'string' ? ev : ev) || [],
      metadata: {
        intent: intent.intent,
        preconditions: intent.contract.pre.length,
        postconditions: intent.contract.post.length
      }
    });
    
    // Step-level witness requirements
    for (const step of intent.plan.steps) {
      const stepId = step.id || step.step;
      
      requirements.push({
        operation: `execute_step:${stepId}`,
        stepId: stepId,
        requiredConfidence: step.confidence_threshold || intent.telemetry.confidenceThresholds.minimum,
        evidenceTypes: step.evidence_required || [],
        metadata: {
          step: step.step,
          tool: step.tool,
          agent: step.agent,
          hasCompensation: !!step.compensate,
          hasRetry: !!step.retry
        }
      });
    }
    
    return requirements;
  }
  
  /**
   * Clear tag cache
   */
  clearCache(): void {
    this.tagCache.clear();
  }
  
  /**
   * Get cache statistics
   */
  getCacheStats(): { size: number; hits: number; misses: number } {
    return {
      size: this.tagCache.size,
      hits: 0, // Would track hits in production
      misses: 0 // Would track misses in production
    };
  }
}

