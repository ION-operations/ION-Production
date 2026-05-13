/**
 * Integration Bridge Tests
 * 
 * End-to-end tests for parser → compiler → interpreter → verifier pipeline
 */

import { PLIxIntegrationBridge, Pipeline, type PipelineResult } from '../integration-bridge';

describe('Integration Bridge', () => {
  test('should execute parse stage', async () => {
    const bridge = new PLIxIntegrationBridge();
    
    const plixText = `
ensure ent:plix://test/example
  act:test
  requires
    con:x == 1
  ensures
    con:y == 2
    `;
    
    const result = await bridge.execute(plixText);
    
    expect(result.metadata.stages).toContain('parse');
    expect(result.parse).toBeDefined();
    expect(result.parse?.intent).not.toBeNull();
  });
  
  test('should execute compile stage', async () => {
    const bridge = new PLIxIntegrationBridge();
    
    const plixText = `
ensure ent:plix://room/reservation
  act:reserve
  requires
    con:room_available == true
  ensures
    con:room_reserved == true
  plan [
    task check := api.check_room()
    task reserve := api.reserve_room(room_id: check.ref:room_id)
  ]
    `;
    
    const result = await bridge.execute(plixText);
    
    expect(result.metadata.stages).toContain('compile');
    expect(result.compile).toBeDefined();
    expect(result.compile?.aipGraph).toBeDefined();
    expect(result.compile?.apoeP).toBeDefined();
  });
  
  test('should report parse errors', async () => {
    const bridge = new PLIxIntegrationBridge();
    
    const plixText = `invalid syntax here`;
    
    const result = await bridge.execute(plixText);
    
    expect(result.success).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });
  
  test('should execute type checking when enabled', async () => {
    const bridge = new PLIxIntegrationBridge({
      validation: {
        enableTypeChecking: true
      }
    });
    
    const plixText = `
ensure ent:plix://test/example
  act:test
  requires
    con:x == 1
    `;
    
    const result = await bridge.execute(plixText);
    
    expect(result.metadata.stages).toContain('typeCheck');
    expect(result.typeCheck).toBeDefined();
  });
  
  test('should execute effect checking when enabled', async () => {
    const bridge = new PLIxIntegrationBridge({
      validation: {
        enableEffectChecking: true,
        contextId: 'test_ctx',
        policyId: 'test_policy'
      }
    });
    
    // Register context and policy
    bridge['effectValidator'].getEffectChecker().registerContext('test_ctx', { io: true });
    bridge['effectValidator'].getPolicyEngine().registerPolicy('test_policy', {
      allowed: ['io'],
      prohibited: ['net', 'db'],
      requiresApproval: []
    });
    
    const plixText = `
ensure ent:plix://test/example
  act:test
  plan [
    step step1
  ]
    `;
    
    const result = await bridge.execute(plixText);
    
    expect(result.metadata.stages).toContain('effectCheck');
    expect(result.effectCheck).toBeDefined();
  });
  
  test('should measure pipeline duration', async () => {
    const bridge = new PLIxIntegrationBridge();
    
    const plixText = `
ensure ent:plix://test/example
  act:test
    `;
    
    const result = await bridge.execute(plixText);
    
    expect(result.metadata.durationMs).toBeGreaterThan(0);
    expect(result.metadata.startTime).toBeLessThan(result.metadata.endTime);
  });
});

describe('Pipeline Convenience Functions', () => {
  test('parseAndCompile should return AIP graph', async () => {
    const plixText = `
ensure ent:plix://test/example
  act:test
  plan [
    task step1 := api.action()
  ]
    `;
    
    const result = await Pipeline.parseAndCompile(plixText);
    
    expect(result.aipGraph).not.toBeNull();
    expect(result.errors).toHaveLength(0);
  });
  
  test('validate should check types and effects', async () => {
    const plixText = `
ensure ent:plix://test/example
  act:test
  requires
    con:x == 1
    `;
    
    const result = await Pipeline.validate(plixText);
    
    expect(result.valid).toBe(true);
  });
  
  test('executeFullPipeline should run all stages', async () => {
    const plixText = `
ensure ent:plix://test/example
  act:test
    `;
    
    const result = await Pipeline.executeFullPipeline(plixText);
    
    expect(result.metadata.stages.length).toBeGreaterThan(2);
  });
});

describe('Golden Example: Meeting Room', () => {
  test('should execute full pipeline for meeting room example', async () => {
    const bridge = new PLIxIntegrationBridge({
      validation: {
        enableTypeChecking: true,
        enableEffectChecking: true,
        contextId: 'app_ctx',
        policyId: 'app_policy'
      }
    });
    
    // Register context and policy
    bridge['effectValidator'].getEffectChecker().registerContext('app_ctx', {
      io: true,
      net: true,
      db: true,
      compensable: true
    });
    
    bridge['effectValidator'].getPolicyEngine().registerPolicy('app_policy', {
      allowed: ['io', 'net', 'db', 'compensable'],
      prohibited: [],
      requiresApproval: []
    });
    
    const plixText = `
ensure ent:plix://room/reservation
  act:reserve
  requires
    con:room_available(date, duration) == true
  ensures
    con:room_reserved == true
  plan [
    task check := api.check_room_availability(date: date, duration: duration)
    task reserve := api.reserve_room(room_id: check.ref:room_id, duration: duration)
    task invite := api.create_calendar_event(room_id: reserve.ref:room_id)
    compensate reserve -> api.cancel_reservation(reservation_id: reserve.ref:id)
  ]
    `;
    
    const result = await bridge.execute(plixText);
    
    // Validation
    expect(result.parse?.intent).not.toBeNull();
    expect(result.compile?.aipGraph).toBeDefined();
    expect(result.metadata.stages).toContain('parse');
    expect(result.metadata.stages).toContain('compile');
    
    // Should succeed (assuming no network/runtime errors)
    expect(result.parse?.errors).toHaveLength(0);
  });
});

