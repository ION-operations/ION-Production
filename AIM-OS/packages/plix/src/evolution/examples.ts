/**
 * PLIX Phase 4 Evolution Framework Examples
 * 
 * Examples of GGP proposals, pattern mining, and deprecation proof validation
 */

import { PLIXGGPSystem } from '../evolution/ggp-system';
import type { GGPProposal, GrammarPattern, DeprecationProof } from '../evolution/ggp-system';
import type { PLIxIntent } from '../models/schema';

/**
 * Example 1: Mine Patterns from Historical Traces
 */
export async function example1_PatternMining() {
  const ggpSystem = new PLIXGGPSystem();
  
  // Simulate historical traces
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
  
  console.log('Discovered patterns:', result.patterns.length);
  console.log('Confidence:', result.confidence);
  console.log('Recommendations:', result.recommendations);
  
  return result;
}

/**
 * Example 2: Create GGP Proposal
 */
export async function example2_CreateGGPProposal() {
  const ggpSystem = new PLIXGGPSystem();
  
  // Create pattern from mining
  const pattern: GrammarPattern = {
    id: 'pattern_001',
    description: 'Logical AND constraint pattern',
    syntax: 'constraint AND constraint',
    frequency: 50,
    confidence: 0.75,
    examples: [
      '(schema_intact == h_prev) AND (rowcount_stable <= 0)',
      '(user_exists == true) AND (permissions_valid == true)'
    ],
    firstSeen: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    lastSeen: new Date().toISOString()
  };
  
  // Create deprecation proof
  const deprecationProof: DeprecationProof = {
    conformanceTests: [
      {
        name: 'Test AND constraint parsing',
        input: '(a == 1) AND (b == 2)',
        expectedOutput: { type: 'logical', operator: 'and', left: 'a == 1', right: 'b == 2' },
        description: 'Verify AND constraint is parsed correctly'
      }
    ],
    backwardCompatibility: [
      {
        oldPattern: 'constraint',
        newPattern: 'constraint AND constraint',
        migrationPath: 'Combine multiple constraints with AND',
        breaking: false
      }
    ],
    migrationGuide: {
      from: 'Multiple separate constraints',
      to: 'Single AND constraint',
      steps: [
        'Combine constraints with AND operator',
        'Update parser to handle AND',
        'Update constraint evaluator'
      ],
      examples: [
        'Before: con:a == 1\ncon:b == 2',
        'After: con:(a == 1) AND (b == 2)'
      ]
    },
    validationStatus: 'passing'
  };
  
  // Create GGP proposal
  const proposal = await ggpSystem.createGGPProposal(
    pattern,
    {
      problem: 'Multiple constraints are verbose and hard to read',
      solution: 'Add AND operator to combine constraints',
      benefits: ['More readable', 'More expressive', 'Better performance'],
      risks: ['Parser complexity', 'Breaking changes']
    },
    deprecationProof,
    {
      tier: 'A',
      required: 2
    },
    'system'
  );
  
  console.log('Created GGP:', proposal.id);
  console.log('Status:', proposal.status);
  
  return proposal;
}

/**
 * Example 3: Validate Deprecation Proof
 */
export async function example3_ValidateDeprecationProof() {
  const ggpSystem = new PLIXGGPSystem();
  
  const deprecationProof: DeprecationProof = {
    conformanceTests: [
      {
        name: 'Test constraint parsing',
        input: 'a == 1',
        expectedOutput: { type: 'simple', expr: 'a', op: '==', value: 1 },
        description: 'Verify constraint parsing'
      }
    ],
    backwardCompatibility: [],
    migrationGuide: {
      from: 'old',
      to: 'new',
      steps: [],
      examples: []
    },
    validationStatus: 'pending'
  };
  
  const validation = await ggpSystem.validateDeprecationProof(deprecationProof);
  
  console.log('Validation valid:', validation.valid);
  console.log('Validation errors:', validation.errors);
  console.log('Proof status:', deprecationProof.validationStatus);
  
  return validation;
}

/**
 * Example 4: Approve GGP Proposal
 */
export async function example4_ApproveGGP() {
  const ggpSystem = new PLIXGGPSystem();
  
  // Create and submit proposal
  const pattern: GrammarPattern = {
    id: 'pattern_002',
    description: 'Quantified constraint pattern',
    syntax: 'forall variable in collection: constraint',
    frequency: 30,
    confidence: 0.60,
    examples: ['forall row in users: unique_email'],
    firstSeen: new Date().toISOString(),
    lastSeen: new Date().toISOString()
  };
  
  const deprecationProof: DeprecationProof = {
    conformanceTests: [
      {
        name: 'Test quantified constraint',
        input: 'forall row in users: unique_email',
        expectedOutput: { type: 'quantified', quantifier: 'forall', variable: 'row', collection: 'users' },
        description: 'Verify quantified constraint parsing'
      }
    ],
    backwardCompatibility: [],
    migrationGuide: { from: 'old', to: 'new', steps: [], examples: [] },
    validationStatus: 'passing'
  };
  
  const proposal = await ggpSystem.createGGPProposal(
    pattern,
    {
      problem: 'Need to express constraints over collections',
      solution: 'Add quantified constraints (forall/exists)',
      benefits: ['More expressive', 'Better validation'],
      risks: ['Parser complexity']
    },
    deprecationProof,
    {
      tier: 'A',
      required: 2
    },
    'system'
  );
  
  // Submit for review
  await ggpSystem.submitProposal(proposal.id);
  
  // Approve by first authority
  await ggpSystem.approveProposal(proposal.id, 'admin1', 'A', 'Looks good');
  
  // Approve by second authority (should trigger approval)
  await ggpSystem.approveProposal(proposal.id, 'admin2', 'A', 'Agreed');
  
  const updatedProposal = ggpSystem.getProposal(proposal.id);
  console.log('Final status:', updatedProposal?.status);
  console.log('Approvals:', updatedProposal?.authorityQuorum.approvals.length);
  
  return updatedProposal;
}

/**
 * Example 5: Full GGP Workflow
 */
export async function example5_FullGGPWorkflow() {
  const ggpSystem = new PLIXGGPSystem();
  
  // Step 1: Mine patterns from historical traces
  const traces: PLIxIntent[] = []; // Would load from CMC/Timeline
  const miningResult = await ggpSystem.minePatterns(traces);
  
  console.log('Mined patterns:', miningResult.patterns.length);
  
  // Step 2: Create GGP proposal for high-confidence pattern
  const highConfidencePattern = miningResult.patterns.find(p => p.confidence >= 0.7);
  
  if (highConfidencePattern) {
    const deprecationProof: DeprecationProof = {
      conformanceTests: [
        {
          name: 'Test pattern',
          input: highConfidencePattern.examples[0],
          expectedOutput: {},
          description: 'Verify pattern works'
        }
      ],
      backwardCompatibility: [],
      migrationGuide: { from: 'old', to: 'new', steps: [], examples: [] },
      validationStatus: 'pending'
    };
    
    // Validate deprecation proof
    await ggpSystem.validateDeprecationProof(deprecationProof);
    
    // Create proposal
    const proposal = await ggpSystem.createGGPProposal(
      highConfidencePattern,
      {
        problem: 'Pattern is frequently used but not in grammar',
        solution: 'Add pattern to official grammar',
        benefits: ['Standardization', 'Better tooling'],
        risks: ['Breaking changes']
      },
      deprecationProof,
      {
        tier: 'A',
        required: 2
      },
      'system'
    );
    
    // Submit for review
    await ggpSystem.submitProposal(proposal.id);
    
    // Get pending proposals
    const pendingProposals = ggpSystem.getProposals('proposed');
    console.log('Pending proposals:', pendingProposals.length);
    
    return {
      miningResult,
      proposal,
      pendingProposals
    };
  }
  
  return { miningResult };
}

