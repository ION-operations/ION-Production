/**
 * Lucid Orchestrator - Drift Detector
 * 
 * This module implements automatic drift detection by comparing Spec promises
 * against Timeline reality and static code analysis.
 */

import { SpecBlock, SpecStatus, SpecViolation, SpecEngineUtils } from './spec_model';
import { IRNode, IRGraph } from '../graph_engine/ir_model';

export interface DriftDetectionResult {
  /** Spec blocks that have drifted */
  driftedSpecs: SpecBlock[];
  
  /** Spec blocks with violations */
  violatedSpecs: SpecBlock[];
  
  /** New violations detected */
  newViolations: SpecViolation[];
  
  /** Summary statistics */
  summary: {
    totalSpecs: number;
    driftedCount: number;
    violatedCount: number;
    newViolationCount: number;
    healthScore: number;
  };
}

export interface TimelineEvent {
  /** Event identifier */
  id: string;
  
  /** Node ID this event relates to */
  nodeId: string;
  
  /** Event type */
  type: 'function_call' | 'performance' | 'error' | 'side_effect' | 'security';
  
  /** Event timestamp */
  timestamp: string;
  
  /** Event duration in milliseconds */
  durationMs?: number;
  
  /** Event metadata */
  metadata: {
    functionName?: string;
    errorMessage?: string;
    performanceData?: any;
    sideEffects?: string[];
    securityFlags?: string[];
  };
}

export interface PerformanceData {
  /** Average execution time in milliseconds */
  averageTime: number;
  
  /** Maximum execution time in milliseconds */
  maxTime: number;
  
  /** Minimum execution time in milliseconds */
  minTime: number;
  
  /** Number of executions */
  executionCount: number;
  
  /** Performance budget in milliseconds */
  budget: number;
}

export class DriftDetector {
  private timelineEvents: Map<string, TimelineEvent[]> = new Map();
  
  /**
   * Add timeline events for analysis
   */
  addTimelineEvents(nodeId: string, events: TimelineEvent[]): void {
    const existing = this.timelineEvents.get(nodeId) || [];
    this.timelineEvents.set(nodeId, [...existing, ...events]);
  }
  
  /**
   * Detect drift across all spec blocks
   */
  detectDrift(specBlocks: SpecBlock[], irGraph: IRGraph): DriftDetectionResult {
    const driftedSpecs: SpecBlock[] = [];
    const violatedSpecs: SpecBlock[] = [];
    const newViolations: SpecViolation[] = [];
    
    for (const specBlock of specBlocks) {
      const updatedSpec = this.analyzeSpecBlock(specBlock, irGraph);
      
      if (updatedSpec.status === 'drift' && specBlock.status !== 'drift') {
        driftedSpecs.push(updatedSpec);
      }
      
      if (updatedSpec.status === 'violation' && specBlock.status !== 'violation') {
        violatedSpecs.push(updatedSpec);
      }
      
      // Check for new violations
      const newViolationsForSpec = this.detectNewViolations(specBlock, updatedSpec);
      newViolations.push(...newViolationsForSpec);
    }
    
    const totalSpecs = specBlocks.length;
    const healthScore = this.calculateHealthScore(specBlocks);
    
    return {
      driftedSpecs,
      violatedSpecs,
      newViolations,
      summary: {
        totalSpecs,
        driftedCount: driftedSpecs.length,
        violatedCount: violatedSpecs.length,
        newViolationCount: newViolations.length,
        healthScore
      }
    };
  }
  
  /**
   * Analyze a single spec block for drift
   */
  private analyzeSpecBlock(specBlock: SpecBlock, irGraph: IRGraph): SpecBlock {
    let updatedSpec = { ...specBlock };
    
    // Check performance budget violations
    updatedSpec = this.checkPerformanceBudget(updatedSpec, irGraph);
    
    // Check must_never violations
    updatedSpec = this.checkMustNeverViolations(updatedSpec, irGraph);
    
    // Check dependency violations
    updatedSpec = this.checkDependencyViolations(updatedSpec, irGraph);
    
    // Check security violations
    updatedSpec = this.checkSecurityViolations(updatedSpec, irGraph);
    
    return updatedSpec;
  }
  
  /**
   * Check performance budget violations
   */
  private checkPerformanceBudget(specBlock: SpecBlock, irGraph: IRGraph): SpecBlock {
    if (!specBlock.perf_budget_ms) return specBlock;
    
    const performanceData = this.getPerformanceData(specBlock.linked_nodes[0]);
    if (!performanceData) return specBlock;
    
    if (performanceData.averageTime > specBlock.perf_budget_ms) {
      const violation: SpecViolation = {
        id: `perf_violation_${Date.now()}`,
        type: 'perf_budget',
        description: `Average execution time ${performanceData.averageTime}ms exceeds budget of ${specBlock.perf_budget_ms}ms`,
        severity: performanceData.averageTime > specBlock.perf_budget_ms * 2 ? 'high' : 'medium',
        detectedAt: new Date().toISOString(),
        evidence: {
          timeline_events: [],
          code_locations: [specBlock.filePath],
          performance_data: performanceData
        },
        status: 'open'
      };
      
      return SpecEngineUtils.addViolation(
        specBlock,
        'perf_budget',
        violation.description,
        violation.severity,
        violation.evidence
      );
    }
    
    return specBlock;
  }
  
  /**
   * Check must_never violations
   */
  private checkMustNeverViolations(specBlock: SpecBlock, irGraph: IRGraph): SpecBlock {
    const nodeId = specBlock.linked_nodes[0];
    if (!nodeId) return specBlock;
    
    const node = irGraph.nodes.get(nodeId);
    if (!node) return specBlock;
    
    const timelineEvents = this.timelineEvents.get(nodeId) || [];
    
    for (const mustNever of specBlock.must_never) {
      const violations = this.checkMustNeverRule(mustNever, node, timelineEvents);
      
      for (const violation of violations) {
        specBlock = SpecEngineUtils.addViolation(
          specBlock,
          'must_never',
          violation.description,
          violation.severity,
          violation.evidence
        );
      }
    }
    
    return specBlock;
  }
  
  /**
   * Check a specific must_never rule
   */
  private checkMustNeverRule(
    rule: string,
    node: IRNode,
    timelineEvents: TimelineEvent[]
  ): SpecViolation[] {
    const violations: SpecViolation[] = [];
    
    // Check for common must_never patterns
    if (rule.includes('Throw uncaught exceptions')) {
      const errorEvents = timelineEvents.filter(e => e.type === 'error');
      if (errorEvents.length > 0) {
        violations.push({
          id: `must_never_violation_${Date.now()}`,
          type: 'must_never',
          description: `Function threw uncaught exceptions: ${errorEvents.length} times`,
          severity: 'high',
          detectedAt: new Date().toISOString(),
          evidence: {
            timeline_events: errorEvents.map(e => e.id),
            code_locations: [node.filePath]
          },
          status: 'open'
        });
      }
    }
    
    if (rule.includes('Access undefined or null values')) {
      const nullAccessEvents = timelineEvents.filter(e => 
        e.metadata.errorMessage?.includes('undefined') || 
        e.metadata.errorMessage?.includes('null')
      );
      if (nullAccessEvents.length > 0) {
        violations.push({
          id: `must_never_violation_${Date.now()}`,
          type: 'must_never',
          description: `Function accessed undefined/null values: ${nullAccessEvents.length} times`,
          severity: 'medium',
          detectedAt: new Date().toISOString(),
          evidence: {
            timeline_events: nullAccessEvents.map(e => e.id),
            code_locations: [node.filePath]
          },
          status: 'open'
        });
      }
    }
    
    if (rule.includes('Expose sensitive data')) {
      const sensitiveDataEvents = timelineEvents.filter(e => 
        e.metadata.securityFlags?.includes('sensitive_data_exposed')
      );
      if (sensitiveDataEvents.length > 0) {
        violations.push({
          id: `must_never_violation_${Date.now()}`,
          type: 'must_never',
          description: `Function exposed sensitive data: ${sensitiveDataEvents.length} times`,
          severity: 'critical',
          detectedAt: new Date().toISOString(),
          evidence: {
            timeline_events: sensitiveDataEvents.map(e => e.id),
            code_locations: [node.filePath]
          },
          status: 'open'
        });
      }
    }
    
    return violations;
  }
  
  /**
   * Check dependency violations
   */
  private checkDependencyViolations(specBlock: SpecBlock, irGraph: IRGraph): SpecBlock {
    // This would check if declared dependencies are actually being used
    // and if undeclared dependencies are being used
    // Implementation would depend on specific dependency analysis needs
    return specBlock;
  }
  
  /**
   * Check security violations
   */
  private checkSecurityViolations(specBlock: SpecBlock, irGraph: IRGraph): SpecBlock {
    const nodeId = specBlock.linked_nodes[0];
    if (!nodeId) return specBlock;
    
    const timelineEvents = this.timelineEvents.get(nodeId) || [];
    const securityEvents = timelineEvents.filter(e => e.type === 'security');
    
    if (securityEvents.length > 0) {
      const criticalSecurityEvents = securityEvents.filter(e => 
        e.metadata.securityFlags?.includes('critical')
      );
      
      if (criticalSecurityEvents.length > 0) {
        return SpecEngineUtils.addViolation(
          specBlock,
          'security',
          `Critical security events detected: ${criticalSecurityEvents.length} times`,
          'critical',
          {
            timeline_events: criticalSecurityEvents.map(e => e.id),
            code_locations: [specBlock.filePath]
          }
        );
      }
    }
    
    return specBlock;
  }
  
  /**
   * Get performance data for a node
   */
  private getPerformanceData(nodeId: string): PerformanceData | null {
    const events = this.timelineEvents.get(nodeId) || [];
    const performanceEvents = events.filter(e => e.type === 'performance' && e.durationMs);
    
    if (performanceEvents.length === 0) return null;
    
    const durations = performanceEvents.map(e => e.durationMs!);
    const averageTime = durations.reduce((sum, d) => sum + d, 0) / durations.length;
    const maxTime = Math.max(...durations);
    const minTime = Math.min(...durations);
    
    return {
      averageTime,
      maxTime,
      minTime,
      executionCount: durations.length,
      budget: 0 // This would be set based on spec block
    };
  }
  
  /**
   * Detect new violations in an updated spec block
   */
  private detectNewViolations(originalSpec: SpecBlock, updatedSpec: SpecBlock): SpecViolation[] {
    const originalViolationCount = originalSpec.governance.violations.length;
    const updatedViolationCount = updatedSpec.governance.violations.length;
    
    if (updatedViolationCount > originalViolationCount) {
      return updatedSpec.governance.violations.slice(originalViolationCount);
    }
    
    return [];
  }
  
  /**
   * Calculate overall health score
   */
  private calculateHealthScore(specBlocks: SpecBlock[]): number {
    if (specBlocks.length === 0) return 100;
    
    const cleanSpecs = specBlocks.filter(s => s.status === 'clean').length;
    return (cleanSpecs / specBlocks.length) * 100;
  }
  
  /**
   * Generate drift report
   */
  generateDriftReport(result: DriftDetectionResult): string {
    const { summary, driftedSpecs, violatedSpecs, newViolations } = result;
    
    let report = `# Drift Detection Report\n\n`;
    report += `**Generated:** ${new Date().toISOString()}\n\n`;
    
    report += `## Summary\n`;
    report += `- Total Specs: ${summary.totalSpecs}\n`;
    report += `- Drifted Specs: ${summary.driftedCount}\n`;
    report += `- Violated Specs: ${summary.violatedCount}\n`;
    report += `- New Violations: ${summary.newViolationCount}\n`;
    report += `- Health Score: ${summary.healthScore.toFixed(1)}%\n\n`;
    
    if (driftedSpecs.length > 0) {
      report += `## Drifted Specs\n`;
      for (const spec of driftedSpecs) {
        report += `- **${spec.symbol}** (${spec.filePath}): ${spec.drift_reason}\n`;
      }
      report += `\n`;
    }
    
    if (violatedSpecs.length > 0) {
      report += `## Violated Specs\n`;
      for (const spec of violatedSpecs) {
        report += `- **${spec.symbol}** (${spec.filePath}): ${spec.drift_reason}\n`;
      }
      report += `\n`;
    }
    
    if (newViolations.length > 0) {
      report += `## New Violations\n`;
      for (const violation of newViolations) {
        report += `- **${violation.type}**: ${violation.description} (${violation.severity})\n`;
      }
    }
    
    return report;
  }
}
