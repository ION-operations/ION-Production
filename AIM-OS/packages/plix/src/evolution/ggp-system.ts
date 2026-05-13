/**
 * PLIX Grammar Growth Proposal (GGP) System
 * 
 * Phase 4: Evolution Framework for PLIX grammar
 * - Auto-discoverer for pattern mining
 * - Deprecation proof requirements
 * - Authority quorum for GGP acceptance
 * - Integration with AIM-OS governance
 */

import type { PLIxIntent } from '../models/schema';
import type { AuthorityTier } from '../registry/tag-registry';

export type GGPStatus = 'draft' | 'proposed' | 'review' | 'approved' | 'rejected' | 'deprecated';

export interface GrammarPattern {
  /** Pattern identifier */
  id: string;
  
  /** Pattern description */
  description: string;
  
  /** Pattern syntax (EBNF or example) */
  syntax: string;
  
  /** Frequency in historical traces */
  frequency: number;
  
  /** Confidence score (0-1) */
  confidence: number;
  
  /** Examples from traces */
  examples: string[];
  
  /** First seen timestamp */
  firstSeen: string;
  
  /** Last seen timestamp */
  lastSeen: string;
}

export interface DeprecationProof {
  /** Conformance test suite */
  conformanceTests: {
    name: string;
    input: string;
    expectedOutput: any;
    description: string;
  }[];
  
  /** Backward compatibility checks */
  backwardCompatibility: {
    oldPattern: string;
    newPattern: string;
    migrationPath: string;
    breaking: boolean;
  }[];
  
  /** Migration guide */
  migrationGuide: {
    from: string;
    to: string;
    steps: string[];
    examples: string[];
  };
  
  /** Validation status */
  validationStatus: 'pending' | 'passing' | 'failing';
  
  /** Validation errors if failing */
  validationErrors?: string[];
}

export interface GGPProposal {
  /** GGP identifier (e.g., GGP-001) */
  id: string;
  
  /** Proposal title */
  title: string;
  
  /** Detailed description */
  description: string;
  
  /** Proposed grammar pattern */
  pattern: GrammarPattern;
  
  /** Rationale for proposal */
  rationale: {
    problem: string;
    solution: string;
    benefits: string[];
    risks: string[];
  };
  
  /** Deprecation proof */
  deprecationProof: DeprecationProof;
  
  /** Authority quorum required */
  authorityQuorum: {
    tier: AuthorityTier;
    required: number; // Number of approvals required
    approvals: Array<{
      authority: string;
      tier: AuthorityTier;
      timestamp: string;
      comment?: string;
    }>;
  };
  
  /** Status */
  status: GGPStatus;
  
  /** Created by */
  createdBy: string;
  
  /** Created timestamp */
  createdAt: string;
  
  /** Updated timestamp */
  updatedAt: string;
  
  /** Timeline entry ID (for governance integration) */
  timelineEntryId?: string;
  
  /** Track ID (for AIM-OS governance) */
  trackId?: string;
  
  /** Metadata */
  metadata?: Record<string, any>;
}

export interface PatternMiningResult {
  patterns: GrammarPattern[];
  confidence: number;
  recommendations: string[];
  metadata?: Record<string, any>;
}

/**
 * PLIX Grammar Growth Proposal System
 */
export class PLIXGGPSystem {
  private proposals: Map<string, GGPProposal>;
  private patterns: Map<string, GrammarPattern>;
  private historicalTraces: PLIxIntent[];
  private cmcClient: any; // CMC client (to be injected)
  private timelineClient: any; // Timeline client (to be injected)
  
  constructor(options?: {
    cmcClient?: any;
    timelineClient?: any;
  }) {
    this.proposals = new Map();
    this.patterns = new Map();
    this.historicalTraces = [];
    this.cmcClient = options?.cmcClient;
    this.timelineClient = options?.timelineClient;
  }
  
  /**
   * Mine grammar patterns from historical PLIX traces
   */
  async minePatterns(traces: PLIxIntent[]): Promise<PatternMiningResult> {
    this.historicalTraces = traces;
    
    const patterns: GrammarPattern[] = [];
    const patternFrequency = new Map<string, number>();
    const patternExamples = new Map<string, string[]>();
    const patternFirstSeen = new Map<string, string>();
    const patternLastSeen = new Map<string, string>();
    
    // Analyze traces for patterns
    for (const trace of traces) {
      // Extract constraint patterns
      for (const pre of trace.contract.pre) {
        const pattern = this.extractPattern(pre);
        if (pattern) {
          patternFrequency.set(pattern, (patternFrequency.get(pattern) || 0) + 1);
          
          if (!patternExamples.has(pattern)) {
            patternExamples.set(pattern, []);
            patternFirstSeen.set(pattern, trace.provenance.when);
          }
          
          patternExamples.get(pattern)!.push(String(pre));
          patternLastSeen.set(pattern, trace.provenance.when);
        }
      }
      
      // Extract plan step patterns
      for (const step of trace.plan.steps) {
        const stepPattern = this.extractStepPattern(step);
        if (stepPattern) {
          patternFrequency.set(stepPattern, (patternFrequency.get(stepPattern) || 0) + 1);
          
          if (!patternExamples.has(stepPattern)) {
            patternExamples.set(stepPattern, []);
            patternFirstSeen.set(stepPattern, trace.provenance.when);
          }
          
          patternExamples.get(stepPattern)!.push(step.step);
          patternLastSeen.set(stepPattern, trace.provenance.when);
        }
      }
    }
    
    // Convert to GrammarPattern objects
    for (const [patternStr, frequency] of patternFrequency.entries()) {
      const totalTraces = traces.length;
      const confidence = Math.min(1.0, frequency / totalTraces);
      
      if (confidence >= 0.1) { // Only include patterns seen in at least 10% of traces
        const pattern: GrammarPattern = {
          id: `pattern_${patterns.length + 1}`,
          description: `Pattern discovered from ${frequency} occurrences`,
          syntax: patternStr,
          frequency,
          confidence,
          examples: patternExamples.get(patternStr)!.slice(0, 5), // Top 5 examples
          firstSeen: patternFirstSeen.get(patternStr)!,
          lastSeen: patternLastSeen.get(patternStr)!
        };
        
        patterns.push(pattern);
        this.patterns.set(pattern.id, pattern);
      }
    }
    
    // Generate recommendations
    const recommendations = this.generateRecommendations(patterns);
    
    return {
      patterns,
      confidence: patterns.length > 0 ? patterns.reduce((sum, p) => sum + p.confidence, 0) / patterns.length : 0,
      recommendations
    };
  }
  
  /**
   * Extract pattern from constraint
   */
  private extractPattern(constraint: string | any): string | null {
    if (typeof constraint === 'string') {
      // Extract operator pattern
      const operators = ['==', '!=', '<=', '>=', '<', '>', 'AND', 'OR', 'NOT'];
      for (const op of operators) {
        if (constraint.includes(op)) {
          return `constraint_${op.toLowerCase()}`;
        }
      }
      return 'constraint_simple';
    }
    
    // Extract constraint type pattern
    if (typeof constraint === 'object' && constraint.type) {
      return `constraint_${constraint.type}`;
    }
    
    return null;
  }
  
  /**
   * Extract pattern from plan step
   */
  private extractStepPattern(step: any): string | null {
    const features: string[] = [];
    
    if (step.retry) features.push('has_retry');
    if (step.compensate) features.push('has_compensate');
    if (step.errors && step.errors.length > 0) features.push('has_errors');
    if (step.depends_on && step.depends_on.length > 0) features.push('has_deps');
    if (step.confidence_threshold) features.push('has_confidence');
    
    return features.length > 0 ? `step_${features.join('_')}` : 'step_basic';
  }
  
  /**
   * Generate recommendations from patterns
   */
  private generateRecommendations(patterns: GrammarPattern[]): string[] {
    const recommendations: string[] = [];
    
    // Check for high-frequency patterns that aren't in grammar
    const highFrequencyPatterns = patterns.filter(p => p.confidence >= 0.5);
    if (highFrequencyPatterns.length > 0) {
      recommendations.push(
        `Consider adding ${highFrequencyPatterns.length} high-frequency patterns to official grammar`
      );
    }
    
    // Check for emerging patterns
    const recentPatterns = patterns.filter(p => {
      const daysSinceFirstSeen = (Date.now() - new Date(p.firstSeen).getTime()) / (1000 * 60 * 60 * 24);
      return daysSinceFirstSeen < 30; // Patterns seen in last 30 days
    });
    
    if (recentPatterns.length > 0) {
      recommendations.push(
        `${recentPatterns.length} emerging patterns detected - monitor for GGP proposals`
      );
    }
    
    // Check for deprecated patterns
    const deprecatedPatterns = patterns.filter(p => {
      const daysSinceLastSeen = (Date.now() - new Date(p.lastSeen).getTime()) / (1000 * 60 * 60 * 24);
      return daysSinceLastSeen > 90; // Not seen in 90 days
    });
    
    if (deprecatedPatterns.length > 0) {
      recommendations.push(
        `${deprecatedPatterns.length} patterns may be deprecated - consider removal proposals`
      );
    }
    
    return recommendations;
  }
  
  /**
   * Create a GGP proposal
   */
  async createGGPProposal(
    pattern: GrammarPattern,
    rationale: {
      problem: string;
      solution: string;
      benefits: string[];
      risks: string[];
    },
    deprecationProof: DeprecationProof,
    authorityQuorum: {
      tier: AuthorityTier;
      required: number;
    },
    createdBy: string
  ): Promise<GGPProposal> {
    const ggpId = `GGP-${String(this.proposals.size + 1).padStart(3, '0')}`;
    
    const proposal: GGPProposal = {
      id: ggpId,
      title: `Grammar Growth Proposal: ${pattern.description}`,
      description: `Proposal to add pattern: ${pattern.syntax}`,
      pattern,
      rationale,
      deprecationProof,
      authorityQuorum: {
        ...authorityQuorum,
        approvals: []
      },
      status: 'draft',
      createdBy,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    this.proposals.set(ggpId, proposal);
    
    // Persist to CMC if available
    if (this.cmcClient) {
      await this.persistGGPToCMC(proposal);
    }
    
    return proposal;
  }
  
  /**
   * Submit GGP proposal for review
   */
  async submitProposal(ggpId: string): Promise<void> {
    const proposal = this.proposals.get(ggpId);
    if (!proposal) {
      throw new Error(`GGP proposal not found: ${ggpId}`);
    }
    
    // Validate deprecation proof
    if (proposal.deprecationProof.validationStatus !== 'passing') {
      throw new Error('Deprecation proof must pass validation before submission');
    }
    
    // Create timeline entry for governance
    if (this.timelineClient) {
      const timelineEntry = await this.createTimelineEntry(proposal);
      proposal.timelineEntryId = timelineEntry.id;
    }
    
    // Update status
    proposal.status = 'proposed';
    proposal.updatedAt = new Date().toISOString();
    
    // Persist to CMC if available
    if (this.cmcClient) {
      await this.persistGGPToCMC(proposal);
    }
  }
  
  /**
   * Approve GGP proposal (by authority)
   */
  async approveProposal(
    ggpId: string,
    authority: string,
    tier: AuthorityTier,
    comment?: string
  ): Promise<void> {
    const proposal = this.proposals.get(ggpId);
    if (!proposal) {
      throw new Error(`GGP proposal not found: ${ggpId}`);
    }
    
    // Verify authority tier is sufficient
    if (!this.hasAuthority(tier, proposal.authorityQuorum.tier)) {
      throw new Error(`Insufficient authority tier: ${tier} < ${proposal.authorityQuorum.tier}`);
    }
    
    // Add approval
    proposal.authorityQuorum.approvals.push({
      authority,
      tier,
      timestamp: new Date().toISOString(),
      comment
    });
    
    // Check if quorum is met
    const approvalsForTier = proposal.authorityQuorum.approvals.filter(
      a => this.hasAuthority(a.tier, proposal.authorityQuorum.tier)
    );
    
    if (approvalsForTier.length >= proposal.authorityQuorum.required) {
      proposal.status = 'approved';
      proposal.updatedAt = new Date().toISOString();
      
      // Apply GGP to grammar
      await this.applyGGP(proposal);
    }
    
    // Persist to CMC if available
    if (this.cmcClient) {
      await this.persistGGPToCMC(proposal);
    }
  }
  
  /**
   * Reject GGP proposal
   */
  async rejectProposal(ggpId: string, reason: string): Promise<void> {
    const proposal = this.proposals.get(ggpId);
    if (!proposal) {
      throw new Error(`GGP proposal not found: ${ggpId}`);
    }
    
    proposal.status = 'rejected';
    proposal.updatedAt = new Date().toISOString();
    proposal.metadata = {
      ...proposal.metadata,
      rejectionReason: reason
    };
    
    // Persist to CMC if available
    if (this.cmcClient) {
      await this.persistGGPToCMC(proposal);
    }
  }
  
  /**
   * Validate deprecation proof
   */
  async validateDeprecationProof(proof: DeprecationProof): Promise<{
    valid: boolean;
    errors: string[];
  }> {
    const errors: string[] = [];
    
    // Check conformance tests
    if (proof.conformanceTests.length === 0) {
      errors.push('Deprecation proof must include at least one conformance test');
    }
    
    // Check backward compatibility
    const breakingChanges = proof.backwardCompatibility.filter(bc => bc.breaking);
    if (breakingChanges.length > 0 && proof.migrationGuide.steps.length === 0) {
      errors.push('Breaking changes require migration guide');
    }
    
    // Run conformance tests (simplified - would run actual tests)
    for (const test of proof.conformanceTests) {
      // In production, would actually run the test
      // For now, just validate structure
      if (!test.input || !test.expectedOutput) {
        errors.push(`Conformance test "${test.name}" is incomplete`);
      }
    }
    
    proof.validationStatus = errors.length === 0 ? 'passing' : 'failing';
    if (errors.length > 0) {
      proof.validationErrors = errors;
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
  
  /**
   * Apply approved GGP to grammar
   */
  private async applyGGP(proposal: GGPProposal): Promise<void> {
    // In production, this would update the grammar specification
    // For now, just mark pattern as official
    if (this.patterns.has(proposal.pattern.id)) {
      const pattern = this.patterns.get(proposal.pattern.id)!;
      pattern.description = `[OFFICIAL] ${pattern.description}`;
    }
    
    // Create timeline entry for application
    if (this.timelineClient) {
      await this.createTimelineEntry({
        ...proposal,
        status: 'approved'
      });
    }
  }
  
  /**
   * Check if authority tier is sufficient
   */
  private hasAuthority(provided: AuthorityTier, required: AuthorityTier): boolean {
    const tiers: AuthorityTier[] = ['C', 'B', 'A', 'S'];
    const providedIndex = tiers.indexOf(provided);
    const requiredIndex = tiers.indexOf(required);
    return providedIndex >= requiredIndex;
  }
  
  /**
   * Create timeline entry for governance
   */
  private async createTimelineEntry(proposal: GGPProposal): Promise<any> {
    if (!this.timelineClient || typeof this.timelineClient.add_timeline_entry !== 'function') {
      return { id: `timeline_${Date.now()}` };
    }
    
    try {
      const entry = await this.timelineClient.add_timeline_entry({
        prompt_id: `ggp_${proposal.id}`,
        user_input: `GGP Proposal: ${proposal.title}`,
        context_state: {
          ggp_id: proposal.id,
          status: proposal.status,
          pattern: proposal.pattern.syntax,
          authority_quorum: proposal.authorityQuorum
        }
      });
      
      return entry;
    } catch (error) {
      console.error('Failed to create timeline entry:', error);
      return { id: `timeline_${Date.now()}` };
    }
  }
  
  /**
   * Persist GGP to CMC
   */
  private async persistGGPToCMC(proposal: GGPProposal): Promise<void> {
    if (!this.cmcClient || typeof this.cmcClient.store_memory !== 'function') {
      return;
    }
    
    try {
      await this.cmcClient.store_memory({
        content: JSON.stringify(proposal),
        tags: {
          type: 'plix_ggp',
          ggp_id: proposal.id,
          status: proposal.status,
          authority_tier: proposal.authorityQuorum.tier
        }
      });
    } catch (error) {
      console.error('Failed to persist GGP to CMC:', error);
    }
  }
  
  /**
   * Get all proposals
   */
  getProposals(status?: GGPStatus): GGPProposal[] {
    const proposals = Array.from(this.proposals.values());
    return status ? proposals.filter(p => p.status === status) : proposals;
  }
  
  /**
   * Get proposal by ID
   */
  getProposal(ggpId: string): GGPProposal | null {
    return this.proposals.get(ggpId) || null;
  }
  
  /**
   * Get discovered patterns
   */
  getPatterns(): GrammarPattern[] {
    return Array.from(this.patterns.values());
  }
}

