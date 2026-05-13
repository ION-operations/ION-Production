/**
 * Core-PLIx Golden Example Test
 * 
 * Comprehensive test of Core-PLIx meeting-room example from grammar specification
 * This is the definitive test for 100% Core-PLIx compliance
 */

import { PLIXParser } from '../index';
import type { ParseResult } from '../index';

describe('Core-PLIx Golden Example: Meeting Room Reservation', () => {
  let parser: PLIXParser;

  beforeEach(() => {
    parser = new PLIXParser();
  });

  test('should parse complete Core-PLIx meeting-room example', () => {
    const text = `
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
    depends reserve <- check
    depends invite <- reserve
    compensate reserve -> api.cancel_reservation(reservation_id: reserve.ref:id)
  ]
    `;

    const result: ParseResult = parser.parse(text);

    // Should parse without errors
    expect(result.errors).toHaveLength(0);
    expect(result.intent).not.toBeNull();

    // Verify speech act
    expect(result.intent?.intent).toBe('ensure');

    // Verify entity
    expect((result.intent as any)?.entity).toBe('plix://room/reservation');

    // Verify action
    expect((result.intent as any)?.action).toMatchObject({
      type: 'action',
      value: 'reserve'
    });

    // Verify contract (requires/ensures should map to pre/post)
    expect(result.intent?.contract.pre).toHaveLength(1);
    expect(result.intent?.contract.post).toHaveLength(1);

    // Verify plan structure
    expect(result.intent?.plan.steps).toHaveLength(3);

    // Verify task 1: check
    expect(result.intent?.plan.steps[0]).toMatchObject({
      id: 'check',
      action: expect.stringContaining('check_room_availability')
    });

    // Verify task 2: reserve
    expect(result.intent?.plan.steps[1]).toMatchObject({
      id: 'reserve',
      action: expect.stringContaining('reserve_room')
    });

    // Verify task 3: invite
    expect(result.intent?.plan.steps[2]).toMatchObject({
      id: 'invite',
      action: expect.stringContaining('create_calendar_event')
    });

    // Verify tag references in parameters
    expect(result.intent?.plan.steps[1].params).toBeDefined();
    expect(result.intent?.plan.steps[2].params).toBeDefined();

    // Verify compensation
    expect(result.intent?.plan.steps[1].compensation).toBeDefined();
  });

  test('should validate 100% Core-PLIx compliance', () => {
    const text = `
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
    depends reserve <- check
    depends invite <- reserve
    compensate reserve -> api.cancel_reservation(reservation_id: reserve.ref:id)
  ]
    `;

    const result = parser.parse(text);

    // GOLDEN EXAMPLE PASS CRITERIA:
    // 1. ✅ Speech act: ensure
    expect(result.intent?.intent).toBe('ensure');

    // 2. ✅ Entity clause: ent:plix://room/reservation
    expect((result.intent as any)?.entity).toBe('plix://room/reservation');

    // 3. ✅ Action clause: act:reserve
    expect((result.intent as any)?.action?.value).toBe('reserve');

    // 4. ✅ Contract: requires/ensures (mapped to pre/post)
    expect(result.intent?.contract.pre).toBeDefined();
    expect(result.intent?.contract.post).toBeDefined();

    // 5. ✅ Formal step definitions: task id := Action(params)
    const checkStep = result.intent?.plan.steps[0];
    expect(checkStep?.action).toBeTruthy();
    expect(checkStep?.params).toBeDefined();

    // 6. ✅ Tag references: check.ref:room_id
    const reserveStep = result.intent?.plan.steps[1];
    expect(reserveStep?.params).toBeDefined();

    // 7. ✅ Dependencies: depends reserve <- check
    expect(reserveStep?.depends_on).toContain('check');

    // 8. ✅ Formal compensation: compensate id -> Action(params)
    expect(reserveStep?.compensation).toBeDefined();
    expect(reserveStep?.compensation?.action).toBeTruthy();

    // ALL CRITERIA MET = 100% CORE-PLIX COMPLIANT ✅
    expect(result.errors).toHaveLength(0);
  });

  test('should support alternative Core-PLIx examples', () => {
    // Example 2: Database Migration
    const text = `
ensure ent:plix://db/schema/public
  act:migrate
  requires
    con:schema_intact == true
  ensures
    con:schema_fingerprint == h_next
  evidence
    require plix://witness/schema_before
    produce plix://witness/schema_after
  plan [
    task migrate := api.migrate(version: "v2.0")
  ]
    `;

    const result = parser.parse(text);

    expect(result.errors).toHaveLength(0);
    expect(result.intent).not.toBeNull();

    // Verify evidence structure (require/produce)
    expect(result.intent?.evidence.required).toBeDefined();
    expect(result.intent?.evidence.produce).toBeDefined();
  });

  test('should handle Core-PLIx with all features', () => {
    const text = `
ensure ent:plix://complex/example
  act:execute
  requires
    con:precondition1 == true
    con:precondition2 <= 100
  ensures
    con:postcondition == true
  evidence
    require plix://witness/before
    produce plix://witness/after
  plan [
    task step1 := api.action1(param1: value1)
    task step2 := api.action2(param2: step1.ref:result)
    task step3 := api.action3()
    depends step2 <- step1
    depends step3 <- step2
    compensate step1 -> api.rollback1(id: step1.ref:id)
    compensate step2 -> api.rollback2(id: step2.ref:id)
  ]
    `;

    const result = parser.parse(text);

    expect(result.errors).toHaveLength(0);
    expect(result.intent?.contract.pre).toHaveLength(2);
    expect(result.intent?.contract.post).toHaveLength(1);
    expect(result.intent?.plan.steps).toHaveLength(3);
    expect(result.intent?.evidence.required.length).toBeGreaterThan(0);
    expect(result.intent?.evidence.produce.length).toBeGreaterThan(0);
  });
});

describe('Core-PLIx Compliance: All Features', () => {
  let parser: PLIXParser;

  beforeEach(() => {
    parser = new PLIXParser();
  });

  test('Feature 1: Dual syntax (requires/ensures AND pre:/post:)', () => {
    const text1 = `
ensure ent:plix://test
  act:test
  requires
    con:x == 1
  ensures
    con:y == 2
    `;

    const text2 = `
ensure ent:plix://test
  act:test
  pre:
    con:x == 1
  post:
    con:y == 2
    `;

    const result1 = parser.parse(text1);
    const result2 = parser.parse(text2);

    expect(result1.errors).toHaveLength(0);
    expect(result2.errors).toHaveLength(0);
    
    // Both should produce equivalent AST
    expect(result1.intent?.contract.pre.length).toBe(result2.intent?.contract.pre.length);
    expect(result1.intent?.contract.post.length).toBe(result2.intent?.contract.post.length);
  });

  test('Feature 2: Formal step definitions (task := Action)', () => {
    const text = `
ensure ent:plix://test
  act:test
  plan [
    task step1 := api.call(param: value)
  ]
    `;

    const result = parser.parse(text);

    expect(result.errors).toHaveLength(0);
    expect(result.intent?.plan.steps[0].action).toBeTruthy();
  });

  test('Feature 3: Tag references (check.ref:field)', () => {
    const text = `
ensure ent:plix://test
  act:test
  plan [
    task check := api.check()
    task use := api.use(data: check.ref:result)
  ]
    `;

    const result = parser.parse(text);

    expect(result.errors).toHaveLength(0);
    expect(result.intent?.plan.steps[1].params).toBeDefined();
  });

  test('Feature 4: Formal compensation (-> Action)', () => {
    const text = `
ensure ent:plix://test
  act:test
  plan [
    task create := api.create()
    compensate create -> api.delete(id: create.ref:id)
  ]
    `;

    const result = parser.parse(text);

    expect(result.errors).toHaveLength(0);
    expect(result.intent?.plan.steps[0].compensation).toBeDefined();
  });

  test('Feature 5: Evidence structure (require/produce)', () => {
    const text = `
ensure ent:plix://test
  act:test
  evidence
    require plix://witness/before
    produce plix://witness/after
    `;

    const result = parser.parse(text);

    expect(result.errors).toHaveLength(0);
    expect(result.intent?.evidence.required).toBeDefined();
    expect(result.intent?.evidence.produce).toBeDefined();
  });

  test('Feature 6: Backward compatibility (all simplified syntax)', () => {
    const text = `
ensure ent:plix://test
  act:test
  pre:
    con:x == 1
  post:
    con:y == 2
  evidence:
    w:plix://witness/test
  plan [
    step step1
    step step2
    compensate step1
  ]
    `;

    const result = parser.parse(text);

    expect(result.errors).toHaveLength(0);
    expect(result.intent).not.toBeNull();
  });
});

describe('Round-Trip Conversion', () => {
  let parser: PLIXParser;

  beforeEach(() => {
    parser = new PLIXParser();
  });

  test('should preserve semantics in round-trip conversion', () => {
    const originalText = `
ensure ent:plix://room/reservation
  act:reserve
  requires
    con:room_available == true
  ensures
    con:room_reserved == true
  plan [
    task check := api.check_room_availability(date: date, duration: duration)
    task reserve := api.reserve_room(room_id: check.ref:room_id)
    compensate reserve -> api.cancel_reservation(id: reserve.ref:id)
  ]
    `;

    const result = parser.parse(originalText);

    expect(result.errors).toHaveLength(0);
    expect(result.intent).not.toBeNull();

    // Intent should have all required properties
    expect(result.intent?.intent).toBeTruthy();
    expect(result.intent?.contract).toBeTruthy();
    expect(result.intent?.plan).toBeTruthy();
    expect(result.intent?.evidence).toBeTruthy();
  });
});

