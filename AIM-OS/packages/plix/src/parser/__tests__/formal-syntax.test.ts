/**
 * Formal Syntax Support Tests
 * 
 * Tests for Core-PLIx formal syntax: task id := Action(params)
 */

import { PLIXParser } from '../index';
import type { ParseResult } from '../index';

describe('Formal Step Definition', () => {
  let parser: PLIXParser;

  beforeEach(() => {
    parser = new PLIXParser();
  });

  describe('Task Keyword', () => {
    test('should parse task keyword (Core-PLIx syntax)', () => {
      const text = `
ensure ent:plix://room/reservation
  act:reserve
  requires
    con:room_available == true
  ensures
    con:room_reserved == true
  plan [
    task check
    task reserve
    task invite
  ]
      `;

      const result: ParseResult = parser.parse(text);

      expect(result.errors).toHaveLength(0);
      expect(result.intent).not.toBeNull();
      expect(result.intent?.plan.steps).toHaveLength(3);
    });

    test('should parse step keyword (existing syntax)', () => {
      const text = `
ensure ent:plix://room/reservation
  act:reserve
  plan [
    step check
    step reserve
    step invite
  ]
      `;

      const result = parser.parse(text);

      expect(result.errors).toHaveLength(0);
      expect(result.intent?.plan.steps).toHaveLength(3);
    });
  });

  describe('Action Definition', () => {
    test('should parse task with := action definition', () => {
      const text = `
ensure ent:plix://test
  act:test
  plan [
    task check := api.check_auth()
  ]
      `;

      const result = parser.parse(text);

      expect(result.errors).toHaveLength(0);
      expect(result.intent?.plan.steps[0]).toMatchObject({
        id: 'check',
        action: 'api.check_auth'
      });
    });

    test('should parse task with parameters', () => {
      const text = `
ensure ent:plix://test
  act:test
  plan [
    task query := api.query_users(filter: "active == true")
  ]
      `;

      const result = parser.parse(text);

      expect(result.errors).toHaveLength(0);
      expect(result.intent?.plan.steps[0]).toHaveProperty('action');
      expect(result.intent?.plan.steps[0]).toHaveProperty('params');
    });

    test('should parse task with tag references', () => {
      const text = `
ensure ent:plix://test
  act:test
  plan [
    task check := api.check_room()
    task reserve := api.reserve_room(room_id: check.ref:room_id)
  ]
      `;

      const result = parser.parse(text);

      expect(result.errors).toHaveLength(0);
      expect(result.intent?.plan.steps).toHaveLength(2);
      // Tag reference should be parsed
      expect(result.intent?.plan.steps[1].params).toBeDefined();
    });
  });

  describe('Backward Compatibility', () => {
    test('should still parse simplified syntax', () => {
      const text = `
ensure ent:plix://test
  act:test
  plan [
    step check
    step reserve
  ]
      `;

      const result = parser.parse(text);

      expect(result.errors).toHaveLength(0);
      expect(result.intent?.plan.steps).toHaveLength(2);
    });

    test('should handle mixed syntax (step and task)', () => {
      const text = `
ensure ent:plix://test
  act:test
  plan [
    step check
    task reserve := api.reserve()
  ]
      `;

      const result = parser.parse(text);

      expect(result.errors).toHaveLength(0);
      expect(result.intent?.plan.steps).toHaveLength(2);
    });
  });

  describe('Complex Examples', () => {
    test('should parse full meeting-room example', () => {
      const text = `
ensure ent:plix://room/reservation
  act:reserve
  requires
    con:room_available == true
  ensures
    con:room_reserved == true
  plan [
    task check := api.check_room_availability(date: date, duration: duration)
    task reserve := api.reserve_room(room_id: check.ref:room_id, duration: duration)
    task invite := api.create_calendar_event(room_id: reserve.ref:room_id)
  ]
      `;

      const result = parser.parse(text);

      expect(result.errors).toHaveLength(0);
      expect(result.intent?.plan.steps).toHaveLength(3);
      expect(result.intent?.plan.steps[0].action).toContain('check_room_availability');
      expect(result.intent?.plan.steps[1].action).toContain('reserve_room');
      expect(result.intent?.plan.steps[2].action).toContain('create_calendar_event');
    });
  });
});

describe('Formal Compensation', () => {
  let parser: PLIXParser;

  beforeEach(() => {
    parser = new PLIXParser();
  });

  test('should parse compensation with -> action syntax', () => {
    const text = `
ensure ent:plix://test
  act:test
  plan [
    task create := api.create_user(data: user_data)
    compensate create -> api.delete_user(id: create.ref:id)
  ]
    `;

    const result = parser.parse(text);

    expect(result.errors).toHaveLength(0);
    // Compensation should be parsed (implementation may vary)
  });

  test('should parse simplified compensation syntax', () => {
    const text = `
ensure ent:plix://test
  act:test
  plan [
    step create
    compensate create
  ]
    `;

    const result = parser.parse(text);

    expect(result.errors).toHaveLength(0);
  });
});

describe('Evidence Structure', () => {
  let parser: PLIXParser;

  beforeEach(() => {
    parser = new PLIXParser();
  });

  test('should parse require/produce evidence keywords', () => {
    const text = `
ensure ent:plix://db/schema
  act:migrate
  evidence
    require plix://witness/schema_before
    produce plix://witness/schema_after
    `;

    const result = parser.parse(text);

    expect(result.errors).toHaveLength(0);
    // Evidence should be parsed
  });

  test('should parse simplified witness syntax', () => {
    const text = `
ensure ent:plix://db/schema
  act:migrate
  evidence:
    w:plix://witness/schema_before
    w:plix://witness/schema_after
    `;

    const result = parser.parse(text);

    expect(result.errors).toHaveLength(0);
  });
});

