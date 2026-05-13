/**
 * Lucid Orchestrator - Spec Engine Model
 * 
 * This module defines the SpecBlock model and related structures for the
 * Spec Engine that powers the Spec Pane of the Lucid Orchestrator.
 */

export type SpecStatus = 'clean' | 'drift' | 'violation' | 'proposed' | 'orphan';

export type SecurityLevel = 'low' | 'medium' | 'high' | 'critical';

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface SpecBlock {
  /** Unique identifier for this spec block */
  id: string;
  
  /** Version of this spec block */
  version: number;
  
  /** Symbol this spec block describes */
  symbol: string;
  
  /** File path where the symbol is defined */
  filePath: string;
  
  /** What this symbol is responsible for doing */
  responsibility: string;
  
  /** What this symbol must never do */
  must_never: string[];
  
  /** What this symbol depends on */
  dependencies: string[];
  
  /** What this symbol outputs or mutates */
  outputs: string[];
  
  /** Security level of this symbol */
  security_level: SecurityLevel;
  
  /** Performance budget in milliseconds */
  perf_budget_ms?: number;
  
  /** Risk level of this symbol */
  risk_level: RiskLevel;
  
  /** Current status of this spec block */
  status: SpecStatus;
  
  /** Reason for current status */
  drift_reason?: string;
  
  /** Nodes linked to this spec block */
  linked_nodes: string[];
  
  /** Metadata about this spec block */
  metadata: {
    createdAt: string;
    lastModified: string;
    author?: string;
    lastReviewed?: string;
    reviewCount: number;
  };
  
  /** Governance history */
  governance: {
    changes: SpecChange[];
    approvals: SpecApproval[];
    violations: SpecViolation[];
  };
}

export interface SpecChange {
  /** Unique identifier for this change */
  id: string;
  
  /** Type of change made */
  type: 'created' | 'updated' | 'deprecated' | 'removed';
  
  /** Description of the change */
  description: string;
  
  /** Author of the change */
  author: string;
  
  /** Timestamp of the change */
  timestamp: string;
  
  /** Rationale for the change */
  rationale?: string;
  
  /** Impact assessment */
  impact: {
    blast_radius: number;
    risk_level: RiskLevel;
    affected_nodes: string[];
  };
}

export interface SpecApproval {
  /** Unique identifier for this approval */
  id: string;
  
  /** Spec change being approved */
  changeId: string;
  
  /** Approver identifier */
  approver: string;
  
  /** Timestamp of approval */
  timestamp: string;
  
  /** Approval rationale */
  rationale: string;
  
  /** Conditions attached to approval */
  conditions?: string[];
}

export interface SpecViolation {
  /** Unique identifier for this violation */
  id: string;
  
  /** Type of violation */
  type: 'must_never' | 'perf_budget' | 'dependency' | 'output' | 'security';
  
  /** Description of the violation */
  description: string;
  
  /** Severity of the violation */
  severity: 'low' | 'medium' | 'high' | 'critical';
  
  /** Timestamp when violation was detected */
  detectedAt: string;
  
  /** Evidence of the violation */
  evidence: {
    timeline_events: string[];
    code_locations: string[];
    performance_data?: any;
  };
  
  /** Status of the violation */
  status: 'open' | 'acknowledged' | 'resolved' | 'ignored';
  
  /** Resolution details */
  resolution?: {
    resolvedAt: string;
    resolvedBy: string;
    resolution: string;
  };
}

export interface SpecEngine {
  /** All spec blocks */
  specBlocks: Map<string, SpecBlock>;
  
  /** Spec block metadata */
  metadata: {
    totalSpecs: number;
    cleanSpecs: number;
    driftSpecs: number;
    violationSpecs: number;
    lastUpdated: string;
  };
}

/**
 * Utility functions for working with spec blocks
 */
export class SpecEngineUtils {
  /**
   * Create a new spec block
   */
  static createSpecBlock(
    symbol: string,
    filePath: string,
    responsibility: string,
    author?: string
  ): SpecBlock {
    const id = `${filePath}:${symbol}_spec_v1`;
    
    return {
      id,
      version: 1,
      symbol,
      filePath,
      responsibility,
      must_never: [],
      dependencies: [],
      outputs: [],
      security_level: 'low',
      risk_level: 'low',
      status: 'clean',
      linked_nodes: [],
      metadata: {
        createdAt: new Date().toISOString(),
        lastModified: new Date().toISOString(),
        author,
        reviewCount: 0
      },
      governance: {
        changes: [],
        approvals: [],
        violations: []
      }
    };
  }
  
  /**
   * Update spec block status based on analysis
   */
  static updateSpecStatus(
    specBlock: SpecBlock,
    status: SpecStatus,
    reason?: string
  ): SpecBlock {
    const updated = { ...specBlock };
    
    if (updated.status !== status) {
      updated.status = status;
      updated.drift_reason = reason;
      updated.metadata.lastModified = new Date().toISOString();
      
      // Add to governance history
      updated.governance.changes.push({
        id: `change_${Date.now()}`,
        type: 'updated',
        description: `Status changed from ${specBlock.status} to ${status}`,
        author: 'system',
        timestamp: new Date().toISOString(),
        rationale: reason,
        impact: {
          blast_radius: 0,
          risk_level: 'low',
          affected_nodes: []
        }
      });
    }
    
    return updated;
  }
  
  /**
   * Add a violation to a spec block
   */
  static addViolation(
    specBlock: SpecBlock,
    type: SpecViolation['type'],
    description: string,
    severity: SpecViolation['severity'],
    evidence: SpecViolation['evidence']
  ): SpecBlock {
    const updated = { ...specBlock };
    
    const violation: SpecViolation = {
      id: `violation_${Date.now()}`,
      type,
      description,
      severity,
      detectedAt: new Date().toISOString(),
      evidence,
      status: 'open'
    };
    
    updated.governance.violations.push(violation);
    
    // Update status based on violation severity
    if (severity === 'critical' || severity === 'high') {
      updated.status = 'violation';
    } else if (updated.status === 'clean') {
      updated.status = 'drift';
    }
    
    updated.metadata.lastModified = new Date().toISOString();
    
    return updated;
  }
  
  /**
   * Get spec blocks by status
   */
  static getSpecsByStatus(specEngine: SpecEngine, status: SpecStatus): SpecBlock[] {
    return Array.from(specEngine.specBlocks.values())
      .filter(spec => spec.status === status);
  }
  
  /**
   * Get spec blocks by security level
   */
  static getSpecsBySecurityLevel(
    specEngine: SpecEngine, 
    level: SecurityLevel
  ): SpecBlock[] {
    return Array.from(specEngine.specBlocks.values())
      .filter(spec => spec.security_level === level);
  }
  
  /**
   * Get spec blocks with violations
   */
  static getSpecsWithViolations(specEngine: SpecEngine): SpecBlock[] {
    return Array.from(specEngine.specBlocks.values())
      .filter(spec => spec.governance.violations.length > 0);
  }
  
  /**
   * Calculate spec engine health metrics
   */
  static getSpecEngineHealth(specEngine: SpecEngine): {
    totalSpecs: number;
    cleanSpecs: number;
    driftSpecs: number;
    violationSpecs: number;
    healthScore: number;
    criticalViolations: number;
  } {
    const specs = Array.from(specEngine.specBlocks.values());
    const cleanSpecs = specs.filter(s => s.status === 'clean').length;
    const driftSpecs = specs.filter(s => s.status === 'drift').length;
    const violationSpecs = specs.filter(s => s.status === 'violation').length;
    
    const criticalViolations = specs.reduce((count, spec) => {
      return count + spec.governance.violations.filter(v => v.severity === 'critical').length;
    }, 0);
    
    const healthScore = specs.length > 0 
      ? (cleanSpecs / specs.length) * 100 
      : 100;
    
    return {
      totalSpecs: specs.length,
      cleanSpecs,
      driftSpecs,
      violationSpecs,
      healthScore,
      criticalViolations
    };
  }
  
  /**
   * Find spec blocks that need attention
   */
  static getSpecsNeedingAttention(specEngine: SpecEngine): SpecBlock[] {
    return Array.from(specEngine.specBlocks.values())
      .filter(spec => 
        spec.status === 'violation' || 
        spec.status === 'drift' ||
        spec.governance.violations.some(v => v.status === 'open')
      );
  }
  
  /**
   * Generate spec block from IR node
   */
  static generateSpecFromIRNode(
    nodeId: string,
    nodeName: string,
    filePath: string,
    nodeKind: string,
    author?: string
  ): SpecBlock {
    const responsibility = this.generateResponsibility(nodeName, nodeKind);
    const must_never = this.generateMustNever(nodeKind);
    const security_level = this.determineSecurityLevel(nodeName, nodeKind);
    const risk_level = this.determineRiskLevel(nodeName, nodeKind);
    
    return this.createSpecBlock(nodeName, filePath, responsibility, author);
  }
  
  /**
   * Generate responsibility description based on node
   */
  private static generateResponsibility(nodeName: string, nodeKind: string): string {
    const baseResponsibility = `Handles ${nodeName} functionality`;
    
    switch (nodeKind) {
      case 'function':
        return `${baseResponsibility} with proper input validation and error handling`;
      case 'reactComponent':
        return `${baseResponsibility} with proper state management and user interaction`;
      case 'apiHandler':
        return `${baseResponsibility} with proper authentication and response formatting`;
      case 'service':
        return `${baseResponsibility} with proper error handling and logging`;
      case 'hook':
        return `${baseResponsibility} with proper state management and side effects`;
      default:
        return baseResponsibility;
    }
  }
  
  /**
   * Generate must_never rules based on node kind
   */
  private static generateMustNever(nodeKind: string): string[] {
    const commonRules = [
      'Throw uncaught exceptions',
      'Access undefined or null values without checking',
      'Perform side effects without proper error handling'
    ];
    
    switch (nodeKind) {
      case 'function':
        return [...commonRules, 'Return inconsistent data types'];
      case 'reactComponent':
        return [...commonRules, 'Mutate props directly', 'Cause infinite re-renders'];
      case 'apiHandler':
        return [...commonRules, 'Expose sensitive data in responses', 'Allow unauthorized access'];
      case 'service':
        return [...commonRules, 'Log sensitive information', 'Fail silently without logging'];
      case 'hook':
        return [...commonRules, 'Call hooks conditionally', 'Cause memory leaks'];
      default:
        return commonRules;
    }
  }
  
  /**
   * Determine security level based on node
   */
  private static determineSecurityLevel(nodeName: string, nodeKind: string): SecurityLevel {
    const sensitiveKeywords = ['password', 'token', 'auth', 'secret', 'key', 'credential'];
    const hasSensitiveKeywords = sensitiveKeywords.some(keyword => 
      nodeName.toLowerCase().includes(keyword)
    );
    
    if (hasSensitiveKeywords || nodeKind === 'apiHandler') {
      return 'high';
    }
    
    if (nodeKind === 'service' || nodeKind === 'function') {
      return 'medium';
    }
    
    return 'low';
  }
  
  /**
   * Determine risk level based on node
   */
  private static determineRiskLevel(nodeName: string, nodeKind: string): RiskLevel {
    const highRiskKeywords = ['delete', 'remove', 'destroy', 'clear', 'reset'];
    const hasHighRiskKeywords = highRiskKeywords.some(keyword => 
      nodeName.toLowerCase().includes(keyword)
    );
    
    if (hasHighRiskKeywords) {
      return 'high';
    }
    
    if (nodeKind === 'apiHandler' || nodeKind === 'service') {
      return 'medium';
    }
    
    return 'low';
  }
}

/**
 * Spec Engine Builder for managing spec blocks
 */
export class SpecEngineBuilder {
  private specEngine: SpecEngine;
  
  constructor() {
    this.specEngine = {
      specBlocks: new Map(),
      metadata: {
        totalSpecs: 0,
        cleanSpecs: 0,
        driftSpecs: 0,
        violationSpecs: 0,
        lastUpdated: new Date().toISOString()
      }
    };
  }
  
  /**
   * Add a spec block to the engine
   */
  addSpecBlock(specBlock: SpecBlock): void {
    this.specEngine.specBlocks.set(specBlock.id, specBlock);
    this.updateMetadata();
  }
  
  /**
   * Update an existing spec block
   */
  updateSpecBlock(specBlock: SpecBlock): void {
    this.specEngine.specBlocks.set(specBlock.id, specBlock);
    this.updateMetadata();
  }
  
  /**
   * Remove a spec block
   */
  removeSpecBlock(specId: string): void {
    this.specEngine.specBlocks.delete(specId);
    this.updateMetadata();
  }
  
  /**
   * Get a spec block by ID
   */
  getSpecBlock(specId: string): SpecBlock | undefined {
    return this.specEngine.specBlocks.get(specId);
  }
  
  /**
   * Get all spec blocks
   */
  getAllSpecBlocks(): SpecBlock[] {
    return Array.from(this.specEngine.specBlocks.values());
  }
  
  /**
   * Update metadata based on current spec blocks
   */
  private updateMetadata(): void {
    const specs = Array.from(this.specEngine.specBlocks.values());
    
    this.specEngine.metadata = {
      totalSpecs: specs.length,
      cleanSpecs: specs.filter(s => s.status === 'clean').length,
      driftSpecs: specs.filter(s => s.status === 'drift').length,
      violationSpecs: specs.filter(s => s.status === 'violation').length,
      lastUpdated: new Date().toISOString()
    };
  }
  
  /**
   * Get the current spec engine
   */
  getSpecEngine(): SpecEngine {
    return this.specEngine;
  }
  
  /**
   * Export spec engine to JSON
   */
  exportToJSON(): string {
    return JSON.stringify({
      specBlocks: Array.from(this.specEngine.specBlocks.entries()),
      metadata: this.specEngine.metadata
    }, null, 2);
  }
  
  /**
   * Import spec engine from JSON
   */
  importFromJSON(json: string): void {
    const data = JSON.parse(json);
    this.specEngine.specBlocks = new Map(data.specBlocks);
    this.specEngine.metadata = data.metadata;
  }
}
