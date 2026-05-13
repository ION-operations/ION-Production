/**
 * PLIX Phase 4 Evolution Framework Tests
 * 
 * Tests for GGP system, pattern mining, and deprecation proof validation
 */

import { describe, it, expect } from 'vitest';
import { PLIXGGPSystem } from '../evolution/ggp-system';
import type { PLIxIntent, GrammarPattern, DeprecationProof } from '../evolution/ggp-system';

describe('PLIX Phase 4 Evolution Framework Tests', () => {
  
  describe('Pattern Mining', () => {
    it('should mine patterns from historical traces', async () => {
      const ggpSystem = new PLIXGGPSystem();
      
      const traces: PLIxIntent[] = [
        {
          intent: 'ensure',
          context: { entities: [], scope: 'default', risk: 0.5 },
          contract: {
            pre: ['schema_intact == h_prev', 'rowcount_stable <= 0'],
            post: ['schema_fingerprint == h_next'],
            capabilities: [],
            policies: []
          },
          plan: { steps: [], deps: [] },
          conditions: { onTestFail: 'retry', onLowConfidence: 'escalate', onPolicyBreach: 'fail' },
          evidence: { required: [], produce: [] },
          telemetry: { confidenceThresholds: { minimum: 0.70, warning: 0.80, critical: 0.90 }, timeouts: { step: 30000, plan: 300000 } },
          provenance: { who: 'system', when: new Date().toISOString(), lineage: [] }
        }
      ];
      
      const result = await ggpSystem.minePatterns(traces);
      
      expect(result.patterns.length).toBeGreaterThan(0);
      expect(result.confidence).toBeGreaterThanOrEqual(0);
      expect(result.recommendations.length).toBeGreaterThanOrEqual(0);
    });
    
    it('should extract constraint patterns', async () => {
      const ggpSystem = new PLIXGGPSystem();
      
      const traces: PLIxIntent[] = [
        {
          intent: 'ensure',
          context: { entities: [], scope: 'default', risk: 0.5 },
          contract: {
            pre: ['a == 1', 'b == 2', 'c == 3'],
            post: [],
            capabilities: [],
            policies: []
          },
          plan: { steps: [], deps: [] },
          conditions: { onTestFail: 'retry', onLowConfidence: 'escalate', onPolicyBreach: 'fail' },
          evidence: { required: [], produce: [] },
          telemetry: { confidenceThresholds: { minimum: 0.70, warning: 0.80, critical: 0.90 }, timeouts: { step: 30000, plan: 300000 } },
          provenance: { who: 'system', when: new Date().toISOString(), lineage: [] }
        }
      ];
      
      const result = await ggpSystem.minePatterns(traces);
      
      const constraintPatterns = result.patterns.filter(p => p.syntax.includes('constraint'));
      expect(constraintPatterns.length).toBeGreaterThan(0);
    });
  });
  
  describe('GGP Proposal Creation', () => {
    it('should create GGP proposal', async () => {
      const ggpSystem = new PLIXGGPSystem();
      
      const pattern: GrammarPattern = {
        id: 'pattern_001',
        description: 'Test pattern',
        syntax: 'test_syntax',
        frequency: 10,
        confidence: 0.5,
        examples: ['example1', 'example2'],
        firstSeen: new Date().toISOString(),
        lastSeen: new Date().toISOString()
      };
      
      const deprecationProof: DeprecationProof = {
        conformanceTests: [
          {
            name: 'Test 1',
            input: 'input',
            expectedOutput: {},
            description: 'Test description'
          }
        ],
        backwardCompatibility: [],
        migrationGuide: { from: 'old', to: 'new', steps: [], examples: [] },
        validationStatus: 'passing'
      };
      
      const proposal = await ggpSystem.createGGPProposal(
        pattern,
        {
          problem: 'Test problem',
          solution: 'Test solution',
          benefits: ['benefit1'],
          risks: ['risk1']
        },
        deprecationProof,
        {
          tier: 'A',
          required: 2
        },
        'system'
      );
      
      expect(proposal.id).toMatch(/^GGP-\d{3}$/);
      expect(proposal.status).toBe('draft');
      expect(proposal.authorityQuorum.required).toBe(2);
    });
    
    it('should validate deprecation proof before submission', async () => {
      const ggpSystem = new PLIXGGPSystem();
      
      const pattern: GrammarPattern = {
        id: 'pattern_001',
        description: 'Test',
        syntax: 'test',
        frequency: 10,
        confidence: 0.5,
        examples: [],
        firstSeen: new Date().toISOString(),
        lastSeen: new Date().toISOString()
      };
      
      const invalidProof: DeprecationProof = {
        conformanceTests: [],
        backwardCompatibility: [],
        migrationGuide: { from: 'old', to: 'new', steps: [], examples: [] },
        validationStatus: 'failing',
        validationErrors: ['Missing conformance tests']
      };
      
      const proposal = await ggpSystem.createGGPProposal(
        pattern,
        { problem: 'test', solution: 'test', benefits: [], risks: [] },
        invalidProof,
        { tier: 'A', required: 1 },
        'system'
      );
      
      await expect(ggpSystem.submitProposal(proposal.id)).rejects.toThrow(
        'Deprecation proof must pass validation'
      );
    });
  });
  
  describe('GGP Approval', () => {
    it('should approve GGP proposal with sufficient authority', async () => {
      const ggpSystem = new PLIXGGPSystem();
      
      const pattern: GrammarPattern = {
        id: 'pattern_001',
        description: 'Test',
        syntax: 'test',
        frequency: 10,
        confidence: 0.5,
        examples: [],
        firstSeen: new Date().toISOString(),
        lastSeen: new Date().toISOString()
      };
      
      const deprecationProof: DeprecationProof = {
        conformanceTests: [
          { name: 'Test', input: 'input', expectedOutput: {}, description: 'desc' }
        ],
        backwardCompatibility: [],
        migrationGuide: { from: 'old', to: 'new', steps: [], examples: [] },
        validationStatus: 'passing'
      };
      
      const proposal = await ggpSystem.createGGPProposal(
        pattern,
        { problem: 'test', solution: 'test', benefits: [], risks: [] },
        deprecationProof,
        { tier: 'A', required: 1 },
        'system'
      );
      
      await ggpSystem.submitProposal(proposal.id);
      await ggpSystem.approveProposal(proposal.id, 'admin', 'A', 'Approved');
      
      const updated = ggpSystem.getProposal(proposal.id);
      expect(updated?.status).toBe('approved');
      expect(updated?.authorityQuorum.approvals.length).toBe(1);
    });
    
    it('should reject approval with insufficient authority', async () => {
      const ggpSystem = new PLIXGGPSystem();
      
      const pattern: GrammarPattern = {
        id: 'pattern_001',
        description: 'Test',
        syntax: 'test',
        frequency: 10,
        confidence: 0.5,
        examples: [],
        firstSeen: new Date().toISOString(),
        lastSeen: new Date().toISOString()
      };
      
      const deprecationProof: DeprecationProof = {
        conformanceTests: [
          { name: 'Test', input: 'input', expectedOutput: {}, description: 'desc' }
        ],
        backwardCompatibility: [],
        migrationGuide: { from: 'old', to: 'new', steps: [], examples: [] },
        validationStatus: 'passing'
      };
      
      const proposal = await ggpSystem.createGGPProposal(
        pattern,
        { problem: 'test', solution: 'test', benefits: [], risks: [] },
        deprecationProof,
        { tier: 'A', required: 1 },
        'system'
      );
      
      await ggpSystem.submitProposal(proposal.id);
      
      await expect(
        ggpSystem.approveProposal(proposal.id, 'user', 'B', 'Trying to approve')
      ).rejects.toThrow('Insufficient authority tier');
    });
    
    it('should require quorum for approval', async () => {
      const ggpSystem = new PLIXGGPSystem();
      
      const pattern: GrammarPattern = {
        id: 'pattern_001',
        description: 'Test',
        syntax: 'test',
        frequency: 10,
        confidence: 0.5,
        examples: [],
        firstSeen: new Date().toISOString(),
        lastSeen: new Date().toISOString()
      };
      
      const deprecationProof: DeprecationProof = {
        conformanceTests: [
          { name: 'Test', input: 'input', expectedOutput: {}, description: 'desc' }
        ],
        backwardCompatibility: [],
        migrationGuide: { from: 'old', to: 'new', steps: [], examples: [] },
        validationStatus: 'passing'
      };
      
      const proposal = await ggpSystem.createGGPProposal(
        pattern,
        { problem: 'test', solution: 'test', benefits: [], risks: [] },
        deprecationProof,
        { tier: 'A', required: 2 },
        'system'
      );
      
      await ggpSystem.submitProposal(proposal.id);
      
      // First approval (not enough)
      await ggpSystem.approveProposal(proposal.id, 'admin1', 'A');
      const afterFirst = ggpSystem.getProposal(proposal.id);
      expect(afterFirst?.status).toBe('proposed'); // Still proposed
      
      // Second approval (quorum met)
      await ggpSystem.approveProposal(proposal.id, 'admin2', 'A');
      const afterSecond = ggpSystem.getProposal(proposal.id);
      expect(afterSecond?.status).toBe('approved'); // Now approved
    });
  });
  
  describe('Deprecation Proof Validation', () => {
    it('should validate deprecation proof', async () => {
      const ggpSystem = new PLIXGGPSystem();
      
      const proof: DeprecationProof = {
        conformanceTests: [
          {
            name: 'Test 1',
            input: 'input1',
            expectedOutput: { result: 'output1' },
            description: 'Test description'
          }
        ],
        backwardCompatibility: [],
        migrationGuide: {
          from: 'old',
          to: 'new',
          steps: ['step1', 'step2'],
          examples: ['example1']
        },
        validationStatus: 'pending'
      };
      
      const validation = await ggpSystem.validateDeprecationProof(proof);
      
      expect(validation.valid).toBe(true);
      expect(proof.validationStatus).toBe('passing');
    });
    
    it('should reject proof without conformance tests', async () => {
      const ggpSystem = new PLIXGGPSystem();
      
      const proof: DeprecationProof = {
        conformanceTests: [],
        backwardCompatibility: [],
        migrationGuide: { from: 'old', to: 'new', steps: [], examples: [] },
        validationStatus: 'pending'
      };
      
      const validation = await ggpSystem.validateDeprecationProof(proof);
      
      expect(validation.valid).toBe(false);
      expect(validation.errors).toContain('Deprecation proof must include at least one conformance test');
      expect(proof.validationStatus).toBe('failing');
    });
    
    it('should require migration guide for breaking changes', async () => {
      const ggpSystem = new PLIXGGPSystem();
      
      const proof: DeprecationProof = {
        conformanceTests: [
          { name: 'Test', input: 'input', expectedOutput: {}, description: 'desc' }
        ],
        backwardCompatibility: [
          {
            oldPattern: 'old',
            newPattern: 'new',
            migrationPath: '',
            breaking: true
          }
        ],
        migrationGuide: {
          from: 'old',
          to: 'new',
          steps: [], // Empty steps
          examples: []
        },
        validationStatus: 'pending'
      };
      
      const validation = await ggpSystem.validateDeprecationProof(proof);
      
      expect(validation.valid).toBe(false);
      expect(validation.errors).toContain('Breaking changes require migration guide');
    });
  });
  
  describe('Proposal Management', () => {
    it('should get proposals by status', async () => {
      const ggpSystem = new PLIXGGPSystem();
      
      // Create multiple proposals with different statuses
      const pattern: GrammarPattern = {
        id: 'pattern_001',
        description: 'Test',
        syntax: 'test',
        frequency: 10,
        confidence: 0.5,
        examples: [],
        firstSeen: new Date().toISOString(),
        lastSeen: new Date().toISOString()
      };
      
      const deprecationProof: DeprecationProof = {
        conformanceTests: [
          { name: 'Test', input: 'input', expectedOutput: {}, description: 'desc' }
        ],
        backwardCompatibility: [],
        migrationGuide: { from: 'old', to: 'new', steps: [], examples: [] },
        validationStatus: 'passing'
      };
      
      const proposal1 = await ggpSystem.createGGPProposal(
        pattern,
        { problem: 'test', solution: 'test', benefits: [], risks: [] },
        deprecationProof,
        { tier: 'A', required: 1 },
        'system'
      );
      
      await ggpSystem.submitProposal(proposal1.id);
      
      const proposal2 = await ggpSystem.createGGPProposal(
        { ...pattern, id: 'pattern_002' },
        { problem: 'test', solution: 'test', benefits: [], risks: [] },
        deprecationProof,
        { tier: 'A', required: 1 },
        'system'
      );
      
      const draftProposals = ggpSystem.getProposals('draft');
      const proposedProposals = ggpSystem.getProposals('proposed');
      
      expect(draftProposals.length).toBe(1);
      expect(proposedProposals.length).toBe(1);
    });
    
    it('should reject proposal', async () => {
      const ggpSystem = new PLIXGGPSystem();
      
      const pattern: GrammarPattern = {
        id: 'pattern_001',
        description: 'Test',
        syntax: 'test',
        frequency: 10,
        confidence: 0.5,
        examples: [],
        firstSeen: new Date().toISOString(),
        lastSeen: new Date().toISOString()
      };
      
      const deprecationProof: DeprecationProof = {
        conformanceTests: [
          { name: 'Test', input: 'input', expectedOutput: {}, description: 'desc' }
        ],
        backwardCompatibility: [],
        migrationGuide: { from: 'old', to: 'new', steps: [], examples: [] },
        validationStatus: 'passing'
      };
      
      const proposal = await ggpSystem.createGGPProposal(
        pattern,
        { problem: 'test', solution: 'test', benefits: [], risks: [] },
        deprecationProof,
        { tier: 'A', required: 1 },
        'system'
      );
      
      await ggpSystem.submitProposal(proposal.id);
      await ggpSystem.rejectProposal(proposal.id, 'Not needed');
      
      const updated = ggpSystem.getProposal(proposal.id);
      expect(updated?.status).toBe('rejected');
      expect(updated?.metadata?.rejectionReason).toBe('Not needed');
    });
  });
});

