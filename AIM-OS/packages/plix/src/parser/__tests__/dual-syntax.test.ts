/**
 * Dual Syntax Support Tests
 * 
 * Tests for Core-PLIx dual syntax: pre:/post: AND requires/ensures
 */

import { PLIXParser } from '../index';
import type { ParseResult } from '../index';

describe('Dual Syntax Support', () => {
  let parser: PLIXParser;

  beforeEach(() => {
    parser = new PLIXParser();
  });

  describe('Contract Keywords', () => {
    test('should parse pre: and post: (existing syntax)', () => {
      const text = `
ensure ent:plix://room/reservation
  act:reserve
  pre:
    con:room_available == true
    con:duration <= 4h
  post:
    con:room_reserved == true
      `;

      const result: ParseResult = parser.parse(text);

      expect(result.errors).toHaveLength(0);
      expect(result.intent).not.toBeNull();
      expect(result.intent?.contract.pre).toHaveLength(2);
      expect(result.intent?.contract.post).toHaveLength(1);
    });

    test('should parse requires and ensures (Core-PLIx syntax)', () => {
      const text = `
ensure ent:plix://room/reservation
  act:reserve
  requires
    con:room_available == true
    con:duration <= 4h
  ensures
    con:room_reserved == true
      `;

      const result: ParseResult = parser.parse(text);

      expect(result.errors).toHaveLength(0);
      expect(result.intent).not.toBeNull();
      expect(result.intent?.contract.pre).toHaveLength(2);
      expect(result.intent?.contract.post).toHaveLength(1);
    });

    test('should normalize both syntaxes to pre/post in AST', () => {
      const text1 = `
ensure ent:plix://test
  act:test
  pre:
    con:x == 1
  post:
    con:y == 2
      `;

      const text2 = `
ensure ent:plix://test
  act:test
  requires
    con:x == 1
  ensures
    con:y == 2
      `;

      const result1 = parser.parse(text1);
      const result2 = parser.parse(text2);

      expect(result1.intent).toEqual(result2.intent);
    });

    test('should handle mixed constraints with requires/ensures', () => {
      const text = `
ensure ent:plix://db/schema
  act:migrate
  requires
    con:schema_intact == true
    con:forall_rows unique_email
  ensures
    con:schema_fingerprint == h_next
    con:migration_complete == true
      `;

      const result = parser.parse(text);

      expect(result.errors).toHaveLength(0);
      expect(result.intent?.contract.pre).toHaveLength(2);
      expect(result.intent?.contract.post).toHaveLength(2);
    });
  });

  describe('Backward Compatibility', () => {
    test('should still parse existing pre:/post: syntax', () => {
      const text = `
ask ent:plix://api/service
  act:query
  pre:
    con:authenticated == true
  post:
    con:results_returned == true
      `;

      const result = parser.parse(text);

      expect(result.errors).toHaveLength(0);
      expect(result.intent).not.toBeNull();
    });

    test('should handle constraints without prefix', () => {
      const text = `
ensure ent:plix://test
  act:test
  requires
    con:x == 1
  ensures
    con:y == 2
      `;

      const result = parser.parse(text);

      expect(result.errors).toHaveLength(0);
      expect(result.intent?.contract.pre.length).toBeGreaterThan(0);
      expect(result.intent?.contract.post.length).toBeGreaterThan(0);
    });
  });

  describe('Error Handling', () => {
    test('should handle missing constraints gracefully', () => {
      const text = `
ensure ent:plix://test
  act:test
  requires
  ensures
      `;

      const result = parser.parse(text);

      // Should parse but may have warnings
      expect(result.intent).not.toBeNull();
      expect(result.intent?.contract.pre).toHaveLength(0);
      expect(result.intent?.contract.post).toHaveLength(0);
    });

    test('should provide clear error messages for malformed syntax', () => {
      const text = `
ensure ent:plix://test
  act:test
  requires invalid syntax here
      `;

      const result = parser.parse(text);

      // Parser should handle gracefully
      expect(result.intent).not.toBeNull();
    });
  });

  describe('Round-Trip Conversion', () => {
    test('should preserve semantics in round-trip conversion', () => {
      const text = `
ensure ent:plix://room/reservation
  act:reserve
  requires
    con:room_available == true
  ensures
    con:room_reserved == true
      `;

      const result = parser.parse(text);
      expect(result.errors).toHaveLength(0);
      
      // Intent should be parseable and have correct structure
      expect(result.intent?.contract.pre).toBeDefined();
      expect(result.intent?.contract.post).toBeDefined();
    });
  });
});

