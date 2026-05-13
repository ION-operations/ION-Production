/**
 * PLIX Phase 3 Registry Tests
 * 
 * Tests for tag registry, rename governance, and authority tier tracking
 */

import { describe, it, expect } from 'vitest';
import { PLIXTagRegistry } from '../registry/tag-registry';
import type { AuthorityTier } from '../registry/tag-registry';

describe('PLIX Phase 3 Registry Tests', () => {
  
  describe('Tag Registration', () => {
    it('should register a new tag', async () => {
      const registry = new PLIXTagRegistry();
      
      const tagDef = await registry.registerTag(
        'plix://db/table/users#rev@h_98fa',
        { type: 'table', name: 'users' },
        'A',
        'system'
      );
      
      expect(tagDef.tag).toBe('plix://db/table/users#rev@h_98fa');
      expect(tagDef.namespace).toBe('db');
      expect(tagDef.path).toBe('table/users');
      expect(tagDef.authorityTier).toBe('A');
    });
    
    it('should throw error when registering duplicate tag', async () => {
      const registry = new PLIXTagRegistry();
      
      await registry.registerTag(
        'plix://db/table/users#rev@h_98fa',
        { type: 'table', name: 'users' },
        'A',
        'system'
      );
      
      await expect(
        registry.registerTag(
          'plix://db/table/users#rev@h_98fa',
          { type: 'table', name: 'users' },
          'A',
          'system'
        )
      ).rejects.toThrow('Tag already registered');
    });
    
    it('should parse tag components correctly', async () => {
      const registry = new PLIXTagRegistry();
      
      const tagDef = await registry.registerTag(
        'plix://db/table/users#rev@h_98fa',
        { type: 'table' },
        'A',
        'system'
      );
      
      expect(tagDef.namespace).toBe('db');
      expect(tagDef.path).toBe('table/users');
      expect(tagDef.revision).toBe('rev');
      expect(tagDef.hash).toBe('h_98fa');
    });
  });
  
  describe('Tag Resolution', () => {
    it('should resolve registered tag', async () => {
      const registry = new PLIXTagRegistry();
      
      await registry.registerTag(
        'plix://db/table/users#rev@h_98fa',
        { type: 'table', name: 'users' },
        'A',
        'system'
      );
      
      const resolved = await registry.resolveTag('plix://db/table/users#rev@h_98fa');
      
      expect(resolved).not.toBeNull();
      expect(resolved?.tag).toBe('plix://db/table/users#rev@h_98fa');
      expect(resolved?.resolved.name).toBe('users');
    });
    
    it('should return null for non-existent tag', async () => {
      const registry = new PLIXTagRegistry();
      
      const resolved = await registry.resolveTag('plix://nonexistent/tag');
      
      expect(resolved).toBeNull();
    });
    
    it('should cache resolved tags', async () => {
      const registry = new PLIXTagRegistry();
      
      await registry.registerTag(
        'plix://db/table/users#rev@h_98fa',
        { type: 'table' },
        'A',
        'system'
      );
      
      // First resolve (cache miss)
      const resolved1 = await registry.resolveTag('plix://db/table/users#rev@h_98fa');
      
      // Second resolve (cache hit)
      const resolved2 = await registry.resolveTag('plix://db/table/users#rev@h_98fa');
      
      expect(resolved1).not.toBeNull();
      expect(resolved2).not.toBeNull();
      expect(resolved1).toBe(resolved2); // Same object reference
    });
  });
  
  describe('Tag Querying', () => {
    it('should query tags by namespace', async () => {
      const registry = new PLIXTagRegistry();
      
      await registry.registerTag('plix://db/table/users', { type: 'table' }, 'A', 'system');
      await registry.registerTag('plix://db/table/posts', { type: 'table' }, 'A', 'system');
      await registry.registerTag('plix://tool/mcp/migrate', { type: 'tool' }, 'B', 'system');
      
      const dbTags = await registry.queryTags({ namespace: 'db' });
      
      expect(dbTags.length).toBe(2);
      expect(dbTags.every(t => t.namespace === 'db')).toBe(true);
    });
    
    it('should query tags by authority tier', async () => {
      const registry = new PLIXTagRegistry();
      
      await registry.registerTag('plix://db/table/users', { type: 'table' }, 'A', 'system');
      await registry.registerTag('plix://tool/mcp/migrate', { type: 'tool' }, 'B', 'system');
      await registry.registerTag('plix://witness/schema', { type: 'witness' }, 'C', 'system');
      
      const tierATags = await registry.queryTags({ authorityTier: 'A' });
      
      expect(tierATags.length).toBe(1);
      expect(tierATags[0].authorityTier).toBe('A');
    });
    
    it('should query tags by path pattern', async () => {
      const registry = new PLIXTagRegistry();
      
      await registry.registerTag('plix://db/table/users', { type: 'table' }, 'A', 'system');
      await registry.registerTag('plix://db/table/posts', { type: 'table' }, 'A', 'system');
      await registry.registerTag('plix://db/view/user_summary', { type: 'view' }, 'A', 'system');
      
      const tableTags = await registry.queryTags({ pathPattern: 'table/.*' });
      
      expect(tableTags.length).toBe(2);
      expect(tableTags.every(t => t.path.startsWith('table/'))).toBe(true);
    });
    
    it('should paginate query results', async () => {
      const registry = new PLIXTagRegistry();
      
      // Register 5 tags
      for (let i = 0; i < 5; i++) {
        await registry.registerTag(
          `plix://db/table/table${i}`,
          { type: 'table' },
          'A',
          'system'
        );
      }
      
      const page1 = await registry.queryTags({ namespace: 'db', limit: 2, offset: 0 });
      const page2 = await registry.queryTags({ namespace: 'db', limit: 2, offset: 2 });
      
      expect(page1.length).toBe(2);
      expect(page2.length).toBe(2);
      expect(page1[0].tag).not.toBe(page2[0].tag);
    });
  });
  
  describe('Rename Governance', () => {
    it('should create rename record', async () => {
      const registry = new PLIXTagRegistry();
      
      await registry.registerTag('plix://db/table/users_old', { type: 'table' }, 'A', 'system');
      
      const rename = await registry.renameTag(
        'plix://db/table/users_old',
        'plix://db/table/users',
        'A',
        'admin',
        'Standardizing name'
      );
      
      expect(rename.fromTag).toBe('plix://db/table/users_old');
      expect(rename.toTag).toBe('plix://db/table/users');
      expect(rename.status).toBe('pending');
    });
    
    it('should throw error when renaming non-existent tag', async () => {
      const registry = new PLIXTagRegistry();
      
      await expect(
        registry.renameTag(
          'plix://nonexistent/tag',
          'plix://new/tag',
          'A',
          'admin'
        )
      ).rejects.toThrow('Tag not found');
    });
    
    it('should throw error when target tag already exists', async () => {
      const registry = new PLIXTagRegistry();
      
      await registry.registerTag('plix://db/table/users_old', { type: 'table' }, 'A', 'system');
      await registry.registerTag('plix://db/table/users', { type: 'table' }, 'A', 'system');
      
      await expect(
        registry.renameTag(
          'plix://db/table/users_old',
          'plix://db/table/users',
          'A',
          'admin'
        )
      ).rejects.toThrow('Target tag already exists');
    });
    
    it('should throw error when authority tier is insufficient', async () => {
      const registry = new PLIXTagRegistry();
      
      await registry.registerTag('plix://db/table/users', { type: 'table' }, 'A', 'system');
      
      await expect(
        registry.renameTag(
          'plix://db/table/users',
          'plix://db/table/users_new',
          'B', // Lower tier than required 'A'
          'user'
        )
      ).rejects.toThrow('Insufficient authority tier');
    });
    
    it('should find dependents when renaming', async () => {
      const registry = new PLIXTagRegistry();
      
      await registry.registerTag(
        'plix://db/table/users_old',
        { type: 'table', name: 'users_old' },
        'A',
        'system'
      );
      
      await registry.registerTag(
        'plix://tool/mcp/migrate',
        {
          type: 'tool',
          references: ['plix://db/table/users_old']
        },
        'B',
        'system'
      );
      
      const rename = await registry.renameTag(
        'plix://db/table/users_old',
        'plix://db/table/users',
        'A',
        'admin'
      );
      
      expect(rename.dependents.length).toBeGreaterThan(0);
      expect(rename.dependents).toContain('plix://tool/mcp/migrate');
    });
    
    it('should acknowledge rename and complete when all dependents acknowledge', async () => {
      const registry = new PLIXTagRegistry();
      
      await registry.registerTag(
        'plix://db/table/users_old',
        { type: 'table' },
        'A',
        'system'
      );
      
      await registry.registerTag(
        'plix://tool/mcp/migrate',
        { references: ['plix://db/table/users_old'] },
        'B',
        'system'
      );
      
      const rename = await registry.renameTag(
        'plix://db/table/users_old',
        'plix://db/table/users',
        'A',
        'admin'
      );
      
      // Acknowledge rename
      await registry.acknowledgeRename(
        'plix://db/table/users_old',
        'plix://tool/mcp/migrate',
        'system'
      );
      
      // Check that rename is completed
      const resolved = await registry.resolveTag('plix://db/table/users');
      expect(resolved).not.toBeNull();
      expect(resolved?.tag).toBe('plix://db/table/users');
    });
  });
  
  describe('Statistics and Cache', () => {
    it('should provide registry statistics', async () => {
      const registry = new PLIXTagRegistry();
      
      await registry.registerTag('plix://db/table/users', { type: 'table' }, 'A', 'system');
      await registry.registerTag('plix://db/table/posts', { type: 'table' }, 'A', 'system');
      await registry.registerTag('plix://tool/mcp/migrate', { type: 'tool' }, 'B', 'system');
      
      const stats = registry.getStats();
      
      expect(stats.totalTags).toBe(3);
      expect(stats.tagsByNamespace['db']).toBe(2);
      expect(stats.tagsByNamespace['tool']).toBe(1);
      expect(stats.tagsByAuthorityTier['A']).toBe(2);
      expect(stats.tagsByAuthorityTier['B']).toBe(1);
    });
    
    it('should track cache hit rate', async () => {
      const registry = new PLIXTagRegistry();
      
      await registry.registerTag('plix://db/table/users', { type: 'table' }, 'A', 'system');
      
      // First resolve (cache miss)
      await registry.resolveTag('plix://db/table/users');
      
      // Second resolve (cache hit)
      await registry.resolveTag('plix://db/table/users');
      
      const stats = registry.getStats();
      
      expect(stats.cacheHitRate).toBeGreaterThan(0);
      expect(stats.cacheHitRate).toBeLessThanOrEqual(1);
    });
    
    it('should clear cache', async () => {
      const registry = new PLIXTagRegistry();
      
      await registry.registerTag('plix://db/table/users', { type: 'table' }, 'A', 'system');
      
      await registry.resolveTag('plix://db/table/users');
      
      registry.clearCache();
      
      const stats = registry.getStats();
      expect(stats.cacheHitRate).toBe(0);
    });
  });
  
  describe('Rename History', () => {
    it('should track rename history', async () => {
      const registry = new PLIXTagRegistry();
      
      await registry.registerTag('plix://db/table/users_old', { type: 'table' }, 'A', 'system');
      
      const rename = await registry.renameTag(
        'plix://db/table/users_old',
        'plix://db/table/users',
        'A',
        'admin'
      );
      
      const history = registry.getRenameHistory('plix://db/table/users');
      
      expect(history.length).toBeGreaterThan(0);
      expect(history.some(r => r.fromTag === 'plix://db/table/users_old')).toBe(true);
    });
  });
});

