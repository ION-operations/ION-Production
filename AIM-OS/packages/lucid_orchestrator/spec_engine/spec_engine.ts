/**
 * Lucid Orchestrator - Spec Engine
 * 
 * This module implements the main Spec Engine that manages spec blocks,
 * detects drift, and maintains the conscience of the system.
 */

import { SpecBlock, SpecEngine, SpecEngineBuilder, SpecEngineUtils } from './spec_model';
import { DriftDetector, DriftDetectionResult } from './drift_detector';
import { IRNode, IRGraph } from '../graph_engine/ir_model';

export interface SpecEngineConfig {
  /** Enable automatic drift detection */
  enableDriftDetection: boolean;
  
  /** Drift detection interval in milliseconds */
  driftDetectionInterval: number;
  
  /** Enable automatic spec generation from IR nodes */
  enableAutoGeneration: boolean;
  
  /** Security level threshold for auto-generation */
  securityThreshold: 'low' | 'medium' | 'high' | 'critical';
}

export interface SpecEngineStatus {
  /** Current spec engine state */
  status: 'running' | 'stopped' | 'error';
  
  /** Last drift detection timestamp */
  lastDriftDetection?: string;
  
  /** Number of active drift detection cycles */
  activeCycles: number;
  
  /** Error message if status is error */
  error?: string;
}

export class SpecEngineService {
  private specEngine: SpecEngine;
  private builder: SpecEngineBuilder;
  private driftDetector: DriftDetector;
  private config: SpecEngineConfig;
  private status: SpecEngineStatus;
  private driftDetectionInterval?: NodeJS.Timeout;
  
  constructor(config: Partial<SpecEngineConfig> = {}) {
    this.config = {
      enableDriftDetection: true,
      driftDetectionInterval: 30000, // 30 seconds
      enableAutoGeneration: true,
      securityThreshold: 'medium',
      ...config
    };
    
    this.builder = new SpecEngineBuilder();
    this.driftDetector = new DriftDetector();
    this.specEngine = this.builder.getSpecEngine();
    this.status = {
      status: 'stopped',
      activeCycles: 0
    };
  }
  
  /**
   * Start the spec engine
   */
  async start(): Promise<void> {
    try {
      this.status.status = 'running';
      
      if (this.config.enableDriftDetection) {
        this.startDriftDetection();
      }
      
      console.log('Spec Engine started successfully');
    } catch (error) {
      this.status.status = 'error';
      this.status.error = error instanceof Error ? error.message : 'Unknown error';
      throw error;
    }
  }
  
  /**
   * Stop the spec engine
   */
  async stop(): Promise<void> {
    this.status.status = 'stopped';
    
    if (this.driftDetectionInterval) {
      clearInterval(this.driftDetectionInterval);
      this.driftDetectionInterval = undefined;
    }
    
    console.log('Spec Engine stopped');
  }
  
  /**
   * Add a spec block
   */
  addSpecBlock(specBlock: SpecBlock): void {
    this.builder.addSpecBlock(specBlock);
    this.specEngine = this.builder.getSpecEngine();
  }
  
  /**
   * Update a spec block
   */
  updateSpecBlock(specBlock: SpecBlock): void {
    this.builder.updateSpecBlock(specBlock);
    this.specEngine = this.builder.getSpecEngine();
  }
  
  /**
   * Remove a spec block
   */
  removeSpecBlock(specId: string): void {
    this.builder.removeSpecBlock(specId);
    this.specEngine = this.builder.getSpecEngine();
  }
  
  /**
   * Get a spec block by ID
   */
  getSpecBlock(specId: string): SpecBlock | undefined {
    return this.builder.getSpecBlock(specId);
  }
  
  /**
   * Get all spec blocks
   */
  getAllSpecBlocks(): SpecBlock[] {
    return this.builder.getAllSpecBlocks();
  }
  
  /**
   * Generate spec blocks from IR nodes
   */
  generateSpecsFromIR(irGraph: IRGraph): SpecBlock[] {
    if (!this.config.enableAutoGeneration) {
      return [];
    }
    
    const generatedSpecs: SpecBlock[] = [];
    
    for (const node of irGraph.nodes.values()) {
      // Skip if spec already exists
      const existingSpec = this.findSpecByNodeId(node.id);
      if (existingSpec) continue;
      
      // Generate spec based on node characteristics
      const specBlock = SpecEngineUtils.generateSpecFromIRNode(
        node.id,
        node.name,
        node.filePath,
        node.kind
      );
      
      // Link to the IR node
      specBlock.linked_nodes = [node.id];
      
      // Set performance budget based on node characteristics
      if (node.performance) {
        specBlock.perf_budget_ms = this.calculatePerformanceBudget(node);
      }
      
      // Set security level based on node analysis
      specBlock.security_level = this.determineSecurityLevel(node);
      
      generatedSpecs.push(specBlock);
      this.addSpecBlock(specBlock);
    }
    
    return generatedSpecs;
  }
  
  /**
   * Run drift detection manually
   */
  async runDriftDetection(irGraph: IRGraph): Promise<DriftDetectionResult> {
    const specBlocks = this.getAllSpecBlocks();
    const result = this.driftDetector.detectDrift(specBlocks, irGraph);
    
    // Update spec blocks with detected drift
    for (const driftedSpec of result.driftedSpecs) {
      this.updateSpecBlock(driftedSpec);
    }
    
    for (const violatedSpec of result.violatedSpecs) {
      this.updateSpecBlock(violatedSpec);
    }
    
    this.status.lastDriftDetection = new Date().toISOString();
    
    return result;
  }
  
  /**
   * Get spec engine health metrics
   */
  getHealthMetrics(): {
    specEngine: ReturnType<typeof SpecEngineUtils.getSpecEngineHealth>;
    status: SpecEngineStatus;
    config: SpecEngineConfig;
  } {
    return {
      specEngine: SpecEngineUtils.getSpecEngineHealth(this.specEngine),
      status: this.status,
      config: this.config
    };
  }
  
  /**
   * Get spec blocks needing attention
   */
  getSpecsNeedingAttention(): SpecBlock[] {
    return SpecEngineUtils.getSpecsNeedingAttention(this.specEngine);
  }
  
  /**
   * Export spec engine data
   */
  exportData(): string {
    return this.builder.exportToJSON();
  }
  
  /**
   * Import spec engine data
   */
  importData(json: string): void {
    this.builder.importFromJSON(json);
    this.specEngine = this.builder.getSpecEngine();
  }
  
  /**
   * Start automatic drift detection
   */
  private startDriftDetection(): void {
    this.driftDetectionInterval = setInterval(async () => {
      try {
        this.status.activeCycles++;
        // Note: In a real implementation, we'd need access to the IR graph
        // For now, we'll just log that drift detection would run
        console.log(`Drift detection cycle ${this.status.activeCycles} - would run with IR graph`);
      } catch (error) {
        console.error('Drift detection error:', error);
        this.status.status = 'error';
        this.status.error = error instanceof Error ? error.message : 'Unknown error';
      }
    }, this.config.driftDetectionInterval);
  }
  
  /**
   * Find spec block by linked node ID
   */
  private findSpecByNodeId(nodeId: string): SpecBlock | undefined {
    return this.getAllSpecBlocks().find(spec => 
      spec.linked_nodes.includes(nodeId)
    );
  }
  
  /**
   * Calculate performance budget based on node characteristics
   */
  private calculatePerformanceBudget(node: IRNode): number {
    // Base budget on complexity and node type
    let baseBudget = 100; // 100ms default
    
    if (node.performance?.isAsync) {
      baseBudget *= 2; // Async operations get more time
    }
    
    if (node.performance?.hasSideEffects) {
      baseBudget *= 1.5; // Side effects get more time
    }
    
    // Adjust based on complexity
    const complexity = node.metadata.complexity;
    if (complexity > 10) {
      baseBudget *= 2;
    } else if (complexity > 5) {
      baseBudget *= 1.5;
    }
    
    // Adjust based on node kind
    switch (node.kind) {
      case 'apiHandler':
        baseBudget = 1000; // API handlers get 1 second
        break;
      case 'reactComponent':
        baseBudget = 16; // React components should be fast (60fps)
        break;
      case 'service':
        baseBudget = 500; // Services get 500ms
        break;
      case 'function':
        baseBudget = 50; // Functions should be fast
        break;
    }
    
    return Math.round(baseBudget);
  }
  
  /**
   * Determine security level based on node analysis
   */
  private determineSecurityLevel(node: IRNode): 'low' | 'medium' | 'high' | 'critical' {
    // Check for sensitive keywords in name
    const sensitiveKeywords = ['password', 'token', 'auth', 'secret', 'key', 'credential'];
    const hasSensitiveKeywords = sensitiveKeywords.some(keyword => 
      node.name.toLowerCase().includes(keyword)
    );
    
    if (hasSensitiveKeywords) {
      return 'critical';
    }
    
    // Check security tags
    if (node.security?.level === 'critical') {
      return 'critical';
    }
    
    if (node.security?.level === 'high') {
      return 'high';
    }
    
    // Check for security-sensitive side effects
    const securitySideEffects = ['localStorage', 'sessionStorage', 'cookies', 'network'];
    const hasSecuritySideEffects = securitySideEffects.some(effect => 
      node.sideEffects.includes(effect)
    );
    
    if (hasSecuritySideEffects) {
      return 'medium';
    }
    
    // Check node kind
    switch (node.kind) {
      case 'apiHandler':
        return 'high';
      case 'service':
        return 'medium';
      default:
        return 'low';
    }
  }
}

/**
 * Factory function to create a spec engine service
 */
export function createSpecEngineService(config?: Partial<SpecEngineConfig>): SpecEngineService {
  return new SpecEngineService(config);
}

/**
 * Utility function to create a spec block from a simple description
 */
export function createSimpleSpecBlock(
  symbol: string,
  filePath: string,
  responsibility: string,
  mustNever: string[] = [],
  dependencies: string[] = [],
  outputs: string[] = []
): SpecBlock {
  return SpecEngineUtils.createSpecBlock(symbol, filePath, responsibility);
}
