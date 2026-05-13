/**
 * All Backends Integration Tests
 * 
 * Comprehensive tests for TLA+, Alloy, OPA, and IRPlan backends
 */

import { TLAPlusBackend } from '../tlaplus-backend';
import { AlloyBackend } from '../alloy-backend';
import { OPABackend } from '../opa-backend';
import { IRPlanBackend } from '../irplan-backend';
import type { PLIxIntent } from '../../models/schema';

// Golden example: Meeting room reservation
const meetingRoomIntent: PLIxIntent = {
  intent: 'ensure',
  context: {
    entities: ['plix://room/reservation'],
    scope: 'application',
    risk: 0.5
  },
  contract: {
    pre: ['room_available == true'],
    post: ['room_reserved == true'],
    capabilities: [],
    policies: []
  },
  plan: {
    steps: [
      {
        id: 'check',
        step: 'check_availability',
        agent: 'operator',
        tool: 'api.check_room_availability',
        target: 'room',
        args: { date: 'today', duration: '1h' }
      },
      {
        id: 'reserve',
        step: 'reserve_room',
        agent: 'operator',
        tool: 'api.reserve_room',
        target: 'room',
        args: {},
        depends_on: ['check'],
        compensate: {
          action: 'api.cancel_reservation',
          args: {}
        }
      }
    ],
    deps: [{ step: 'reserve', depends_on: ['check'] }]
  },
  conditions: {
    onTestFail: 'retry',
    onLowConfidence: 'escalate',
    onPolicyBreach: 'fail'
  },
  evidence: {
    required: [],
    produce: []
  },
  telemetry: {
    confidenceThresholds: {
      minimum: 0.70,
      warning: 0.80,
      critical: 0.90
    },
    timeouts: {
      step: 30000,
      plan: 300000
    }
  },
  provenance: {
    who: 'system',
    when: new Date().toISOString(),
    lineage: []
  }
};

describe('TLA+ Backend', () => {
  let backend: TLAPlusBackend;
  
  beforeEach(() => {
    backend = new TLAPlusBackend();
  });
  
  test('should compile to TLA+ module', () => {
    const module = backend.compile(meetingRoomIntent);
    
    expect(module.name).toBeTruthy();
    expect(module.variables.length).toBeGreaterThan(0);
    expect(module.actions.length).toBeGreaterThan(0);
  });
  
  test('should generate Init predicate', () => {
    const module = backend.compile(meetingRoomIntent);
    
    expect(module.init).toBeDefined();
    expect(module.init.length).toBeGreaterThan(0);
  });
  
  test('should generate actions from plan steps', () => {
    const module = backend.compile(meetingRoomIntent);
    
    expect(module.actions.length).toBe(2); // check and reserve
    expect(module.actions[0].name).toBe('checkAction');
    expect(module.actions[1].name).toBe('reserveAction');
  });
  
  test('should generate invariants from contract', () => {
    const module = backend.compile(meetingRoomIntent);
    
    expect(module.invariants.length).toBeGreaterThan(0);
  });
  
  test('should generate spec formula', () => {
    const module = backend.compile(meetingRoomIntent);
    
    expect(module.spec).toContain('Init');
    expect(module.spec).toContain('WF_vars');
  });
  
  test('should serialize to TLA+ text', () => {
    const module = backend.compile(meetingRoomIntent);
    const text = backend.serializeModule(module);
    
    expect(text).toContain('---- MODULE');
    expect(text).toContain('EXTENDS');
    expect(text).toContain('VARIABLES');
    expect(text).toContain('Init ==');
    expect(text).toContain('====');
  });
});

describe('Alloy Backend', () => {
  let backend: AlloyBackend;
  
  beforeEach(() => {
    backend = new AlloyBackend();
  });
  
  test('should compile to Alloy model', () => {
    const model = backend.compile(meetingRoomIntent);
    
    expect(model.name).toBeTruthy();
    expect(model.signatures.length).toBeGreaterThan(0);
    expect(model.predicates.length).toBeGreaterThan(0);
  });
  
  test('should generate signatures', () => {
    const model = backend.compile(meetingRoomIntent);
    
    // Should have State, Step, StepState signatures
    const sigNames = model.signatures.map(s => s.name);
    expect(sigNames).toContain('State');
    expect(sigNames).toContain('Step');
  });
  
  test('should generate facts from contract', () => {
    const model = backend.compile(meetingRoomIntent);
    
    expect(model.facts.length).toBeGreaterThan(0);
    expect(model.facts.some(f => f.name === 'Contract')).toBe(true);
  });
  
  test('should generate predicates from plan', () => {
    const model = backend.compile(meetingRoomIntent);
    
    expect(model.predicates.length).toBeGreaterThan(0);
    expect(model.predicates.some(p => p.name === 'ExecutePlan')).toBe(true);
  });
  
  test('should generate assertions', () => {
    const model = backend.compile(meetingRoomIntent);
    
    expect(model.assertions.length).toBeGreaterThan(0);
  });
  
  test('should serialize to Alloy text', () => {
    const model = backend.compile(meetingRoomIntent);
    const text = backend.serializeModel(model);
    
    expect(text).toContain('sig State');
    expect(text).toContain('fact Contract');
    expect(text).toContain('pred ExecutePlan');
  });
});

describe('OPA Backend', () => {
  let backend: OPABackend;
  
  beforeEach(() => {
    backend = new OPABackend();
  });
  
  test('should compile to OPA policy', () => {
    const policy = backend.compile(meetingRoomIntent);
    
    expect(policy.package).toBeTruthy();
    expect(policy.rules.length).toBeGreaterThan(0);
  });
  
  test('should generate allow rules', () => {
    const policy = backend.compile(meetingRoomIntent);
    
    const allowRules = policy.rules.filter(r => r.path[0] === 'allow');
    expect(allowRules.length).toBeGreaterThan(0);
  });
  
  test('should generate step-specific rules', () => {
    const policy = backend.compile(meetingRoomIntent);
    
    const stepRules = policy.rules.filter(r => r.path.includes('step'));
    expect(stepRules.length).toBe(2); // check and reserve
  });
  
  test('should generate helper functions', () => {
    const policy = backend.compile(meetingRoomIntent);
    
    expect(policy.helpers.length).toBeGreaterThan(0);
  });
  
  test('should serialize to Rego', () => {
    const policy = backend.compile(meetingRoomIntent);
    const text = backend.serializePolicy(policy);
    
    expect(text).toContain('package plix');
    expect(text).toContain('import');
    expect(text).toContain('default allow = false');
    expect(text).toContain('allow.execute');
  });
  
  test('should handle effect row in policy generation', () => {
    const effectRow = { io: true, net: true, db: false };
    const policy = backend.compile(meetingRoomIntent, effectRow);
    
    expect(policy.rules.some(r => r.path.includes('capabilities'))).toBe(true);
  });
});

describe('IRPlan Backend', () => {
  let backend: IRPlanBackend;
  
  beforeEach(() => {
    backend = new IRPlanBackend();
  });
  
  test('should compile to IRPlan', () => {
    const plan = backend.compile(meetingRoomIntent);
    
    expect(plan.metadata.name).toBeTruthy();
    expect(plan.steps.length).toBe(2);
    expect(plan.dependencies.size).toBeGreaterThan(0);
  });
  
  test('should generate state definition', () => {
    const plan = backend.compile(meetingRoomIntent);
    
    expect(plan.state.variables.length).toBeGreaterThan(0);
  });
  
  test('should generate steps with effects', () => {
    const plan = backend.compile(meetingRoomIntent);
    
    for (const step of plan.steps) {
      expect(step.effects).toBeDefined();
      expect(step.confidence).toBeGreaterThan(0);
    }
  });
  
  test('should generate dependencies map', () => {
    const plan = backend.compile(meetingRoomIntent);
    
    expect(plan.dependencies.has('reserve')).toBe(true);
    expect(plan.dependencies.get('reserve')).toContain('check');
  });
  
  test('should generate compensations', () => {
    const plan = backend.compile(meetingRoomIntent);
    
    expect(plan.compensations.has('reserve')).toBe(true);
  });
  
  test('should generate contract', () => {
    const plan = backend.compile(meetingRoomIntent);
    
    expect(plan.contract.preconditions.length).toBeGreaterThan(0);
    expect(plan.contract.postconditions.length).toBeGreaterThan(0);
  });
  
  test('should serialize to JSON', () => {
    const plan = backend.compile(meetingRoomIntent);
    const json = backend.serializePlan(plan);
    
    expect(json).toBeTruthy();
    expect(() => JSON.parse(json)).not.toThrow();
  });
  
  test('should validate plan structure', () => {
    const plan = backend.compile(meetingRoomIntent);
    const validation = backend.validate(plan);
    
    expect(validation.valid).toBe(true);
    expect(validation.errors).toHaveLength(0);
  });
  
  test('should detect circular dependencies', () => {
    const invalidIntent: any = {
      ...meetingRoomIntent,
      plan: {
        ...meetingRoomIntent.plan,
        steps: [
          { ...meetingRoomIntent.plan.steps[0], depends_on: ['reserve'] },
          { ...meetingRoomIntent.plan.steps[1], depends_on: ['check'] }
        ]
      }
    };
    
    const plan = backend.compile(invalidIntent);
    const validation = backend.validate(plan);
    
    expect(validation.valid).toBe(false);
    expect(validation.errors.some(e => e.includes('Circular'))).toBe(true);
  });
});

describe('Cross-Backend Integration', () => {
  test('should compile same intent to all 4 backends', async () => {
    const tlaBackend = new TLAPlusBackend();
    const alloyBackend = new AlloyBackend();
    const opaBackend = new OPABackend();
    const irplanBackend = new IRPlanBackend();
    
    const tlaModule = tlaBackend.compile(meetingRoomIntent);
    const alloyModel = alloyBackend.compile(meetingRoomIntent);
    const opaPolicy = opaBackend.compile(meetingRoomIntent);
    const irplan = irplanBackend.compile(meetingRoomIntent);
    
    // All should succeed
    expect(tlaModule).toBeDefined();
    expect(alloyModel).toBeDefined();
    expect(opaPolicy).toBeDefined();
    expect(irplan).toBeDefined();
    
    // All should be serializable
    expect(tlaBackend.serializeModule(tlaModule)).toBeTruthy();
    expect(alloyBackend.serializeModel(alloyModel)).toBeTruthy();
    expect(opaBackend.serializePolicy(opaPolicy)).toBeTruthy();
    expect(irplanBackend.serializePlan(irplan)).toBeTruthy();
  });
  
  test('should preserve semantics across backends', () => {
    const tlaBackend = new TLAPlusBackend();
    const alloyBackend = new AlloyBackend();
    const opaBackend = new OPABackend();
    const irplanBackend = new IRPlanBackend();
    
    const tlaModule = tlaBackend.compile(meetingRoomIntent);
    const alloyModel = alloyBackend.compile(meetingRoomIntent);
    const opaPolicy = opaBackend.compile(meetingRoomIntent);
    const irplan = irplanBackend.compile(meetingRoomIntent);
    
    // All should have 2 steps
    expect(tlaModule.actions.length).toBe(2);
    expect(alloyModel.predicates.filter(p => p.name.startsWith('Execute_')).length).toBe(2);
    expect(opaPolicy.rules.filter(r => r.path.includes('step')).length).toBe(2);
    expect(irplan.steps.length).toBe(2);
    
    // All should preserve dependencies
    expect(tlaModule.actions[1].definition.some(d => d.includes('check'))).toBe(true);
    expect(alloyModel.facts.some(f => f.name === 'Dependencies')).toBe(true);
    expect(irplan.dependencies.has('reserve')).toBe(true);
  });
});

