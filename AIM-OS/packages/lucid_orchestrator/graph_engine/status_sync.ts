/**
 * Status Sync for Lucid Orchestrator
 * 
 * This module provides status synchronization between IR nodes and SpecBlocks,
 * ensuring that drift detection and violation status are properly maintained.
 */

import { IRNode, IREdge, NodeStatus, IRGraph } from './ir_model';
import { SpecBlock, SpecStatus } from '../spec_engine/spec_model';

export interface StatusSyncOptions {
  /** Enable automatic status updates */
  autoUpdate: boolean;
  /** Update interval in milliseconds */
  updateInterval: number;
  /** Include performance-based status updates */
  includePerformance: boolean;
  /** Include security-based status updates */
  includeSecurity: boolean;
  /** Include dependency-based status updates */
  includeDependencies: boolean;
}

export const DEFAULT_STATUS_SYNC_OPTIONS: StatusSyncOptions = {
  autoUpdate: true,
  updateInterval: 5000, // 5 seconds
  includePerformance: true,
  includeSecurity: true,
  includeDependencies: true
};

export interface StatusUpdate {
  nodeId: string;
  oldStatus: NodeStatus;
  newStatus: NodeStatus;
  reason: string;
  timestamp: string;
  metadata?: any;
}

export class StatusSync {
  private options: StatusSyncOptions;
  private statusHistory: StatusUpdate[] = [];
  private updateTimer: NodeJS.Timeout | null = null;

  constructor(options: Partial<StatusSyncOptions> = {}) {
    this.options = { ...DEFAULT_STATUS_SYNC_OPTIONS, ...options };
    
    if (this.options.autoUpdate) {
      this.startAutoUpdate();
    }
  }

  /**
   * Sync status between IR nodes and SpecBlocks
   */
  syncStatus(irGraph: IRGraph, specBlocks: Map<string, SpecBlock>): StatusUpdate[] {
    const updates: StatusUpdate[] = [];
    
    for (const node of irGraph.nodes.values()) {
      const specBlock = specBlocks.get(node.id);
      if (!specBlock) {
        // Node has no spec - mark as orphan
        if (node.status !== 'orphan') {
          updates.push(this.updateNodeStatus(node, 'orphan', 'No corresponding spec block found'));
        }
        continue;
      }
      
      // Check for violations
      const violations = this.checkViolations(node, specBlock);
      if (violations.length > 0) {
        if (node.status !== 'violation') {
          updates.push(this.updateNodeStatus(node, 'violation', `Violations: ${violations.join(', ')}`));
        }
        continue;
      }
      
      // Check for drift
      const driftReasons = this.checkDrift(node, specBlock);
      if (driftReasons.length > 0) {
        if (node.status !== 'drift') {
          updates.push(this.updateNodeStatus(node, 'drift', `Drift detected: ${driftReasons.join(', ')}`));
        }
        continue;
      }
      
      // Check performance issues
      if (this.options.includePerformance) {
        const performanceIssues = this.checkPerformance(node, specBlock);
        if (performanceIssues.length > 0) {
          if (node.status !== 'drift') {
            updates.push(this.updateNodeStatus(node, 'drift', `Performance issues: ${performanceIssues.join(', ')}`));
          }
          continue;
        }
      }
      
      // Check security issues
      if (this.options.includeSecurity) {
        const securityIssues = this.checkSecurity(node, specBlock);
        if (securityIssues.length > 0) {
          if (node.status !== 'violation') {
            updates.push(this.updateNodeStatus(node, 'violation', `Security issues: ${securityIssues.join(', ')}`));
          }
          continue;
        }
      }
      
      // Check dependency issues
      if (this.options.includeDependencies) {
        const dependencyIssues = this.checkDependencies(node, specBlock, irGraph);
        if (dependencyIssues.length > 0) {
          if (node.status !== 'drift') {
            updates.push(this.updateNodeStatus(node, 'drift', `Dependency issues: ${dependencyIssues.join(', ')}`));
          }
          continue;
        }
      }
      
      // If no issues found, mark as clean
      if (node.status !== 'clean') {
        updates.push(this.updateNodeStatus(node, 'clean', 'All checks passed'));
      }
    }
    
    // Update spec block statuses based on IR node statuses
    for (const [nodeId, specBlock] of specBlocks.entries()) {
      const node = irGraph.nodes.get(nodeId);
      if (node) {
        const specStatus = this.mapNodeStatusToSpecStatus(node.status);
        if (specBlock.status !== specStatus) {
          specBlock.status = specStatus;
          specBlock.lastUpdated = new Date().toISOString();
        }
      }
    }
    
    return updates;
  }

  /**
   * Check for violations in a node
   */
  private checkViolations(node: IRNode, specBlock: SpecBlock): string[] {
    const violations: string[] = [];
    
    // Check must_never rules
    for (const rule of specBlock.must_never || []) {
      if (this.evaluateRule(node, rule)) {
        violations.push(`Violates must_never rule: ${rule}`);
      }
    }
    
    // Check required outputs
    for (const output of specBlock.outputs || []) {
      if (!node.outputs.includes(output)) {
        violations.push(`Missing required output: ${output}`);
      }
    }
    
    // Check forbidden side effects
    for (const sideEffect of specBlock.forbidden_side_effects || []) {
      if (node.sideEffects.includes(sideEffect)) {
        violations.push(`Has forbidden side effect: ${sideEffect}`);
      }
    }
    
    return violations;
  }

  /**
   * Check for drift in a node
   */
  private checkDrift(node: IRNode, specBlock: SpecBlock): string[] {
    const driftReasons: string[] = [];
    
    // Check if node kind matches spec
    if (specBlock.node_kind && node.kind !== specBlock.node_kind) {
      driftReasons.push(`Node kind changed from ${specBlock.node_kind} to ${node.kind}`);
    }
    
    // Check if inputs match spec
    const specInputs = specBlock.inputs || [];
    const missingInputs = specInputs.filter(input => !node.inputs.includes(input));
    if (missingInputs.length > 0) {
      driftReasons.push(`Missing expected inputs: ${missingInputs.join(', ')}`);
    }
    
    const unexpectedInputs = node.inputs.filter(input => !specInputs.includes(input));
    if (unexpectedInputs.length > 0) {
      driftReasons.push(`Unexpected inputs: ${unexpectedInputs.join(', ')}`);
    }
    
    // Check if outputs match spec
    const specOutputs = specBlock.outputs || [];
    const missingOutputs = specOutputs.filter(output => !node.outputs.includes(output));
    if (missingOutputs.length > 0) {
      driftReasons.push(`Missing expected outputs: ${missingOutputs.join(', ')}`);
    }
    
    const unexpectedOutputs = node.outputs.filter(output => !specOutputs.includes(output));
    if (unexpectedOutputs.length > 0) {
      driftReasons.push(`Unexpected outputs: ${unexpectedOutputs.join(', ')}`);
    }
    
    return driftReasons;
  }

  /**
   * Check for performance issues
   */
  private checkPerformance(node: IRNode, specBlock: SpecBlock): string[] {
    const issues: string[] = [];
    
    if (!node.performance || !specBlock.perf_budget) {
      return issues;
    }
    
    // Check complexity budget
    if (specBlock.perf_budget.max_complexity && 
        node.performance.estimatedComplexity > specBlock.perf_budget.max_complexity) {
      issues.push(`Complexity exceeds budget: ${node.performance.estimatedComplexity} > ${specBlock.perf_budget.max_complexity}`);
    }
    
    // Check execution time budget
    if (specBlock.perf_budget.max_execution_time && 
        node.performance.estimatedExecutionTime > specBlock.perf_budget.max_execution_time) {
      issues.push(`Execution time exceeds budget: ${node.performance.estimatedExecutionTime}ms > ${specBlock.perf_budget.max_execution_time}ms`);
    }
    
    // Check memory budget
    if (specBlock.perf_budget.max_memory && 
        node.performance.memoryUsage > specBlock.perf_budget.max_memory) {
      issues.push(`Memory usage exceeds budget: ${node.performance.memoryUsage}MB > ${specBlock.perf_budget.max_memory}MB`);
    }
    
    return issues;
  }

  /**
   * Check for security issues
   */
  private checkSecurity(node: IRNode, specBlock: SpecBlock): string[] {
    const issues: string[] = [];
    
    if (!node.security || !specBlock.security) {
      return issues;
    }
    
    // Check security level
    if (specBlock.security.required_level && 
        this.getSecurityLevelValue(node.security.level) < this.getSecurityLevelValue(specBlock.security.required_level)) {
      issues.push(`Security level too low: ${node.security.level} < ${specBlock.security.required_level}`);
    }
    
    // Check for forbidden patterns
    for (const pattern of specBlock.security.forbidden_patterns || []) {
      if (this.containsPattern(node, pattern)) {
        issues.push(`Contains forbidden security pattern: ${pattern}`);
      }
    }
    
    return issues;
  }

  /**
   * Check for dependency issues
   */
  private checkDependencies(node: IRNode, specBlock: SpecBlock, irGraph: IRGraph): string[] {
    const issues: string[] = [];
    
    // Check required dependencies
    const requiredDeps = specBlock.dependencies?.required || [];
    for (const dep of requiredDeps) {
      if (!this.hasDependency(node, dep, irGraph)) {
        issues.push(`Missing required dependency: ${dep}`);
      }
    }
    
    // Check forbidden dependencies
    const forbiddenDeps = specBlock.dependencies?.forbidden || [];
    for (const dep of forbiddenDeps) {
      if (this.hasDependency(node, dep, irGraph)) {
        issues.push(`Has forbidden dependency: ${dep}`);
      }
    }
    
    return issues;
  }

  /**
   * Update node status
   */
  private updateNodeStatus(node: IRNode, newStatus: NodeStatus, reason: string): StatusUpdate {
    const oldStatus = node.status;
    node.status = newStatus;
    node.statusReason = reason;
    node.metadata.lastModified = new Date().toISOString();
    
    const update: StatusUpdate = {
      nodeId: node.id,
      oldStatus,
      newStatus,
      reason,
      timestamp: new Date().toISOString()
    };
    
    this.statusHistory.push(update);
    return update;
  }

  /**
   * Map node status to spec status
   */
  private mapNodeStatusToSpecStatus(nodeStatus: NodeStatus): SpecStatus {
    const statusMap: Record<NodeStatus, SpecStatus> = {
      'clean': 'compliant',
      'drift': 'drift',
      'violation': 'violation',
      'proposed': 'proposed',
      'orphan': 'orphan'
    };
    
    return statusMap[nodeStatus] || 'unknown';
  }

  /**
   * Evaluate a rule against a node
   */
  private evaluateRule(node: IRNode, rule: string): boolean {
    // Simple rule evaluation - in a real implementation, this would be more sophisticated
    const ruleLower = rule.toLowerCase();
    
    if (ruleLower.includes('no console.log') && this.containsPattern(node, 'console.log')) {
      return true;
    }
    
    if (ruleLower.includes('no eval') && this.containsPattern(node, 'eval(')) {
      return true;
    }
    
    if (ruleLower.includes('no innerhtml') && this.containsPattern(node, 'innerHTML')) {
      return true;
    }
    
    return false;
  }

  /**
   * Check if node contains a pattern
   */
  private containsPattern(node: IRNode, pattern: string): boolean {
    // This would need access to the actual source code
    // For now, we'll check metadata and other available information
    return node.metadata?.sourceCode?.includes(pattern) || false;
  }

  /**
   * Check if node has a dependency
   */
  private hasDependency(node: IRNode, dependency: string, irGraph: IRGraph): boolean {
    // Check incoming edges for the dependency
    for (const edge of irGraph.edges.values()) {
      if (edge.to === node.id && edge.from.includes(dependency)) {
        return true;
      }
    }
    return false;
  }

  /**
   * Get security level value for comparison
   */
  private getSecurityLevelValue(level: string): number {
    const levels = { 'low': 1, 'medium': 2, 'high': 3, 'critical': 4 };
    return levels[level as keyof typeof levels] || 0;
  }

  /**
   * Start automatic status updates
   */
  private startAutoUpdate(): void {
    this.updateTimer = setInterval(() => {
      // This would be called with actual IR graph and spec blocks
      // For now, it's just a placeholder
    }, this.options.updateInterval);
  }

  /**
   * Stop automatic status updates
   */
  stopAutoUpdate(): void {
    if (this.updateTimer) {
      clearInterval(this.updateTimer);
      this.updateTimer = null;
    }
  }

  /**
   * Get status history
   */
  getStatusHistory(): StatusUpdate[] {
    return [...this.statusHistory];
  }

  /**
   * Get status history for a specific node
   */
  getNodeStatusHistory(nodeId: string): StatusUpdate[] {
    return this.statusHistory.filter(update => update.nodeId === nodeId);
  }

  /**
   * Clear status history
   */
  clearStatusHistory(): void {
    this.statusHistory = [];
  }

  /**
   * Get status statistics
   */
  getStatusStats(): {
    totalUpdates: number;
    updatesByStatus: Record<NodeStatus, number>;
    updatesByReason: Record<string, number>;
  } {
    const updatesByStatus: Record<NodeStatus, number> = {
      'clean': 0,
      'drift': 0,
      'violation': 0,
      'proposed': 0,
      'orphan': 0
    };
    
    const updatesByReason: Record<string, number> = {};
    
    for (const update of this.statusHistory) {
      updatesByStatus[update.newStatus]++;
      updatesByReason[update.reason] = (updatesByReason[update.reason] || 0) + 1;
    }
    
    return {
      totalUpdates: this.statusHistory.length,
      updatesByStatus,
      updatesByReason
    };
  }

  /**
   * Cleanup resources
   */
  destroy(): void {
    this.stopAutoUpdate();
    this.clearStatusHistory();
  }
}
