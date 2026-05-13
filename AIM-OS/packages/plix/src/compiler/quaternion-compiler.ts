/**
 * PLIX Quaternion Compiler Extensions
 * 
 * Compiles PLIX geometric operations to quaternion-native syscalls
 * Phase 2, Week 7: Compiler Extensions
 */

import type {
  PlaceOperation,
  MoveOperation,
  SenseOperation,
  EmitOperation,
  QuantumContextBlock,
  GeometricOperation,
  QAddrLiteral,
  QuantumContext,
  SelectionRules
} from '../models/quaternion-types';
import type { PLIxIntent } from '../models/schema';
import type { TagResolutionResult } from './aip-compiler';
import { PLIXTypeChecker } from '../type-checker/quaternion-type-checker';
import type { HHNIClient } from './hhni-client';
import type { SEGClient } from './seg-client';

/**
 * QAddr Resolution Result
 */
export interface QAddrResolutionResult {
  tag: string;
  qaddr: QAddrLiteral | null;
  source: 'hhni' | 'seg' | 'cmc' | 'cache' | 'computed' | 'not_found';
  confidence: number;
  metadata?: Record<string, any>;
}

/**
 * Geometric Syscall
 */
export interface GeometricSyscall {
  type: 'place' | 'move' | 'sense' | 'emit';
  entityId?: string;
  qaddr?: QAddrLiteral;
  position?: any; // Vec4 or QPose
  orientation?: any; // QQuat or AngleAxis
  deltaPose?: any; // DualQuat or ScrewMotion
  region?: any; // Region for sense
  filters?: any[]; // Filters for sense
  event?: string; // Event for emit
  quantumContext?: QuantumContext;
  selection?: SelectionRules;
  hamiltonianCost?: number;
  metadata?: Record<string, any>;
}

/**
 * Compilation Result
 */
export interface GeometricCompilationResult {
  syscalls: GeometricSyscall[];
  resolvedQAddrs: Map<string, QAddrLiteral>;
  totalHamiltonianCost: number;
  errors: string[];
  warnings: string[];
}

/**
 * PLIX Quaternion Compiler
 * 
 * Compiles PLIX geometric operations to quaternion-native syscalls
 */
export class PLIXQuaternionCompiler {
  private tagCache: Map<string, QAddrResolutionResult>;
  private hhniClient: HHNIClient | null;
  private segClient: SEGClient | null;
  private cmcClient: any; // CMC client (to be injected)
  private typeChecker: PLIXTypeChecker;
  
  constructor(options?: {
    hhniClient?: HHNIClient;
    segClient?: SEGClient;
    cmcClient?: any;
  }) {
    this.tagCache = new Map();
    this.hhniClient = options?.hhniClient || null;
    this.segClient = options?.segClient || null;
    this.cmcClient = options?.cmcClient;
    this.typeChecker = new PLIXTypeChecker();
  }
  
  /**
   * Resolve PLIX tag to QAddr
   * 
   * Uses HHNI/SEG/CMC to resolve tags to QAddr
   */
  async resolveTagToQAddr(tag: string, quantumContext?: QuantumContext): Promise<QAddrResolutionResult> {
    // Check cache first
    const cacheKey = `${tag}:${JSON.stringify(quantumContext || {})}`;
    if (this.tagCache.has(cacheKey)) {
      const cached = this.tagCache.get(cacheKey)!;
      return { ...cached, source: 'cache' };
    }
    
    // Try HHNI first
    if (this.hhniClient) {
      try {
        const hhniResult = await this.queryHHNIForQAddr(tag);
        if (hhniResult.qaddr) {
          this.tagCache.set(cacheKey, hhniResult);
          return { ...hhniResult, source: 'hhni' };
        }
      } catch (error) {
        // Fall through to next method
      }
    }
    
    // Try SEG for tag lineage
    if (this.segClient) {
      try {
        const segResult = await this.querySEGForQAddr(tag);
        if (segResult.qaddr) {
          this.tagCache.set(cacheKey, segResult);
          return { ...segResult, source: 'seg' };
        }
      } catch (error) {
        // Fall through to next method
      }
    }
    
    // Try CMC for entity state
    if (this.cmcClient) {
      try {
        const cmcResult = await this.queryCMCForQAddr(tag);
        if (cmcResult.qaddr) {
          this.tagCache.set(cacheKey, cmcResult);
          return { ...cmcResult, source: 'cmc' };
        }
      } catch (error) {
        // Fall through to computed
      }
    }
    
    // Compute QAddr from quantum context if provided
    if (quantumContext) {
      const computedQAddr = this.computeQAddrFromContext(quantumContext);
      const result: QAddrResolutionResult = {
        tag,
        qaddr: computedQAddr,
        source: 'computed',
        confidence: 0.7, // Lower confidence for computed
        metadata: { computed: true }
      };
      this.tagCache.set(cacheKey, result);
      return result;
    }
    
    // Not found
    return {
      tag,
      qaddr: null,
      source: 'not_found',
      confidence: 0.0
    };
  }
  
  /**
   * Query HHNI for QAddr
   */
  private async queryHHNIForQAddr(tag: string): Promise<QAddrResolutionResult> {
    if (!this.hhniClient) {
      return {
        tag,
        qaddr: null,
        source: 'hhni',
        confidence: 0.0
      };
    }
    
    try {
      const qaddr = await this.hhniClient.resolveTagToQAddr(tag);
      
      if (qaddr) {
        return {
          tag,
          qaddr: qaddr,
          source: 'hhni',
          confidence: 0.9, // High confidence for HHNI results
          metadata: { resolved: true }
        };
      }
      
      return {
        tag,
        qaddr: null,
        source: 'hhni',
        confidence: 0.0
      };
    } catch (error: any) {
      return {
        tag,
        qaddr: null,
        source: 'hhni',
        confidence: 0.0,
        metadata: { error: error.message }
      };
    }
  }
  
  /**
   * Query SEG for QAddr
   */
  private async querySEGForQAddr(tag: string): Promise<QAddrResolutionResult> {
    if (!this.segClient) {
      return {
        tag,
        qaddr: null,
        source: 'seg',
        confidence: 0.0
      };
    }
    
    try {
      // Get entity lineage from SEG
      const lineage = await this.segClient.getEntityLineage(tag);
      
      // Look for QAddr in entity attributes
      for (const entity of lineage) {
        if (entity.attributes?.qaddr) {
          return {
            tag,
            qaddr: entity.attributes.qaddr,
            source: 'seg',
            confidence: 0.8, // Good confidence for SEG results
            metadata: { entity_id: entity.id, lineage_length: lineage.length }
          };
        }
      }
      
      return {
        tag,
        qaddr: null,
        source: 'seg',
        confidence: 0.0
      };
    } catch (error: any) {
      return {
        tag,
        qaddr: null,
        source: 'seg',
        confidence: 0.0,
        metadata: { error: error.message }
      };
    }
  }
  
  /**
   * Query CMC for QAddr
   */
  private async queryCMCForQAddr(tag: string): Promise<QAddrResolutionResult> {
    // TODO: Implement CMC query
    // This would query the CMC bitemporal store
    // for entity state and QAddr
    return {
      tag,
      qaddr: null,
      source: 'cmc',
      confidence: 0.0
    };
  }
  
  /**
   * Compute QAddr from quantum context
   */
  private computeQAddrFromContext(context: QuantumContext): QAddrLiteral {
    const qaddr: QAddrLiteral = {
      type: 'qaddr'
    };
    
    if (context.n !== undefined) qaddr.n = context.n;
    if (context.l !== undefined) qaddr.l = context.l;
    if (context.m !== undefined) qaddr.m = context.m;
    if (context.s !== undefined) qaddr.s = context.s;
    if (context.morton4d !== undefined) qaddr.morton4d = context.morton4d;
    if (context.s3bin !== undefined) qaddr.s3bin = context.s3bin;
    
    return qaddr;
  }
  
  /**
   * Compile PLIX intent with geometric operations to syscalls
   */
  async compileGeometricOperations(intent: PLIxIntent): Promise<GeometricCompilationResult> {
    const syscalls: GeometricSyscall[] = [];
    const resolvedQAddrs = new Map<string, QAddrLiteral>();
    const errors: string[] = [];
    const warnings: string[] = [];
    
    if (!intent.geometric || !intent.geometric.operations) {
      return {
        syscalls: [],
        resolvedQAddrs,
        totalHamiltonianCost: 0,
        errors: ['No geometric operations found in intent'],
        warnings: []
      };
    }
    
    // Resolve quantum context if present
    let globalQuantumContext: QuantumContext | undefined = intent.geometric.quantumContext;
    
    // Compile each geometric operation
    for (const operation of intent.geometric.operations) {
      try {
        // Type check operation before compilation (Phase 2, Week 6 integration)
        const typeResult = this.typeChecker.checkGeometricOperation(operation);
        if (typeResult.errors.length > 0) {
          errors.push(...typeResult.errors.map(e => `Type error in ${operation.type}: ${e}`));
          continue; // Skip invalid operations
        }
        if (typeResult.warnings.length > 0) {
          warnings.push(...typeResult.warnings.map(w => `Type warning in ${operation.type}: ${w}`));
        }
        
        const syscall = await this.compileGeometricOperation(operation, globalQuantumContext);
        if (syscall) {
          syscalls.push(syscall);
          
          // Resolve QAddr for entity if present
          if (syscall.entityId) {
            const qaddrResult = await this.resolveTagToQAddr(syscall.entityId, syscall.quantumContext);
            if (qaddrResult.qaddr) {
              resolvedQAddrs.set(syscall.entityId, qaddrResult.qaddr);
              syscall.qaddr = qaddrResult.qaddr;
            } else {
              warnings.push(`Could not resolve QAddr for entity: ${syscall.entityId}`);
            }
          }
          
          // Calculate Hamiltonian cost
          syscall.hamiltonianCost = this.calculateHamiltonianCost(syscall);
        }
      } catch (error: any) {
        errors.push(`Error compiling operation ${operation.type}: ${error.message}`);
      }
    }
    
    // Calculate total Hamiltonian cost
    const totalHamiltonianCost = syscalls.reduce((sum, s) => sum + (s.hamiltonianCost || 0), 0);
    
    return {
      syscalls,
      resolvedQAddrs,
      totalHamiltonianCost,
      errors,
      warnings
    };
  }
  
  /**
   * Compile single geometric operation to syscall
   */
  private async compileGeometricOperation(
    operation: GeometricOperation,
    globalQuantumContext?: QuantumContext
  ): Promise<GeometricSyscall | null> {
    switch (operation.type) {
      case 'place_op':
        return this.compilePlaceOperation(operation, globalQuantumContext);
      case 'move_op':
        return this.compileMoveOperation(operation, globalQuantumContext);
      case 'sense_op':
        return this.compileSenseOperation(operation, globalQuantumContext);
      case 'emit_op':
        return this.compileEmitOperation(operation, globalQuantumContext);
      case 'quantum_context':
        // Handle quantum context block
        return null; // Will be handled separately
      default:
        throw new Error(`Unknown geometric operation type: ${(operation as any).type}`);
    }
  }
  
  /**
   * Compile place operation
   */
  private compilePlaceOperation(
    operation: PlaceOperation,
    globalQuantumContext?: QuantumContext
  ): GeometricSyscall {
    const quantumContext = operation.quantumContext || globalQuantumContext;
    
    return {
      type: 'place',
      entityId: operation.entity,
      position: operation.position,
      orientation: operation.orientation,
      quantumContext,
      selection: operation.selection,
      metadata: {
        guards: operation.guards,
        witness: operation.witness
      }
    };
  }
  
  /**
   * Compile move operation
   */
  private compileMoveOperation(
    operation: MoveOperation,
    globalQuantumContext?: QuantumContext
  ): GeometricSyscall {
    const quantumContext = operation.quantumContext || globalQuantumContext;
    
    return {
      type: 'move',
      entityId: operation.entity,
      deltaPose: operation.deltaPose,
      quantumContext,
      selection: operation.selection,
      metadata: {
        guards: operation.guards,
        witness: operation.witness
      }
    };
  }
  
  /**
   * Compile sense operation
   */
  private compileSenseOperation(
    operation: SenseOperation,
    globalQuantumContext?: QuantumContext
  ): GeometricSyscall {
    const quantumContext = operation.quantumContext || globalQuantumContext;
    
    return {
      type: 'sense',
      region: operation.region,
      filters: operation.filters,
      quantumContext,
      metadata: {
        guards: operation.guards
      }
    };
  }
  
  /**
   * Compile emit operation
   */
  private compileEmitOperation(
    operation: EmitOperation,
    globalQuantumContext?: QuantumContext
  ): GeometricSyscall {
    const quantumContext = operation.quantumContext || globalQuantumContext;
    
    return {
      type: 'emit',
      event: operation.event,
      quantumContext,
      selection: operation.selection,
      metadata: {
        guards: operation.guards,
        witness: operation.witness,
        effect: operation.effect
      }
    };
  }
  
  /**
   * Calculate Hamiltonian cost for syscall
   * 
   * H = α·CPU + β·IO + γ·VRAM + δ·|∇κ| + ε·Latency + ζ·Risk
   */
  calculateHamiltonianCost(syscall: GeometricSyscall): number {
    // Base costs per operation type
    const baseCosts: Record<string, number> = {
      place: 10.0,
      move: 15.0,
      sense: 5.0,
      emit: 8.0
    };
    
    let cost = baseCosts[syscall.type] || 10.0;
    
    // Adjust for quantum context (n-tier affects cost)
    if (syscall.quantumContext?.n !== undefined) {
      // Lower n (higher privilege) = lower cost multiplier
      const nTierMultiplier = 1.0 + (syscall.quantumContext.n * 0.1);
      cost *= nTierMultiplier;
    }
    
    // Adjust for selection rules (more restrictive = higher cost)
    if (syscall.selection) {
      const selectionComplexity = this.calculateSelectionComplexity(syscall.selection);
      cost *= (1.0 + selectionComplexity * 0.05);
    }
    
    // Adjust for region size (sense operations)
    if (syscall.type === 'sense' && syscall.region) {
      if (syscall.region.type === 'radius' && syscall.region.radius) {
        const radiusMultiplier = 1.0 + (syscall.region.radius / 100.0);
        cost *= radiusMultiplier;
      }
    }
    
    // Adjust for delta pose complexity (move operations)
    if (syscall.type === 'move' && syscall.deltaPose) {
      const poseComplexity = this.calculatePoseComplexity(syscall.deltaPose);
      cost *= (1.0 + poseComplexity * 0.1);
    }
    
    return cost;
  }
  
  /**
   * Calculate selection rule complexity
   */
  private calculateSelectionComplexity(selection: SelectionRules): number {
    let complexity = 0;
    
    if (selection.deltaN !== undefined) complexity += 1;
    if (selection.deltaL !== undefined) complexity += 1;
    if (selection.deltaM !== undefined) complexity += 1;
    if (selection.deltaS !== undefined) complexity += 1;
    
    return complexity;
  }
  
  /**
   * Calculate pose complexity
   */
  private calculatePoseComplexity(pose: any): number {
    // Simplified: screw motion is more complex than simple translation
    if (pose.type === 'screw_motion') {
      return 2.0;
    } else if (pose.type === 'dualquat') {
      return 1.5;
    }
    return 1.0;
  }
  
  /**
   * Validate Hamiltonian cost against n-tier budget
   */
  validateHamiltonianBudget(
    syscall: GeometricSyscall,
    budget: number
  ): { valid: boolean; cost: number; budget: number; remaining: number } {
    const cost = syscall.hamiltonianCost || this.calculateHamiltonianCost(syscall);
    const valid = cost <= budget;
    const remaining = budget - cost;
    
    return {
      valid,
      cost,
      budget,
      remaining
    };
  }
  
  /**
   * Clear tag cache
   */
  clearCache(): void {
    this.tagCache.clear();
  }
  
  /**
   * Invalidate cache entry for tag
   */
  invalidateCache(tag: string): void {
    // Remove all cache entries matching tag prefix
    for (const key of this.tagCache.keys()) {
      if (key.startsWith(tag)) {
        this.tagCache.delete(key);
      }
    }
  }
}

