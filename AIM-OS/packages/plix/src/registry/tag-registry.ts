/**
 * PLIX Tag Registry
 * 
 * Phase 3: Queryable tag storage with resolution caching, rename governance,
 * and authority tier tracking
 */

import type { PLIxIntent } from '../models/schema';

export type AuthorityTier = 'S' | 'A' | 'B' | 'C';

export interface TagDefinition {
  /** Full tag (plix://namespace/path#rev@hash) */
  tag: string;
  
  /** Namespace (e.g., 'db', 'tool', 'witness') */
  namespace: string;
  
  /** Path within namespace (e.g., 'table/users') */
  path: string;
  
  /** Revision identifier (optional) */
  revision?: string;
  
  /** Content hash (optional) */
  hash?: string;
  
  /** Resolved entity/action/capability data */
  resolved: any;
  
  /** Authority tier required for operations */
  authorityTier: AuthorityTier;
  
  /** Created timestamp */
  createdAt: string;
  
  /** Last updated timestamp */
  updatedAt: string;
  
  /** Created by (agent/user ID) */
  createdBy: string;
  
  /** Metadata */
  metadata?: Record<string, any>;
}

export interface TagRename {
  /** Original tag */
  fromTag: string;
  
  /** New tag */
  toTag: string;
  
  /** Authority tier that authorized rename */
  authorityTier: AuthorityTier;
  
  /** Renamed by (agent/user ID) */
  renamedBy: string;
  
  /** Timestamp */
  timestamp: string;
  
  /** Reason for rename */
  reason?: string;
  
  /** Dependents that must acknowledge */
  dependents: string[];
  
  /** Acknowledged by */
  acknowledgedBy: Map<string, string>; // dependent -> timestamp
  
  /** Status */
  status: 'pending' | 'acknowledged' | 'completed' | 'rejected';
}

export interface TagQuery {
  /** Query by namespace */
  namespace?: string;
  
  /** Query by path pattern */
  pathPattern?: string;
  
  /** Query by revision */
  revision?: string;
  
  /** Query by authority tier */
  authorityTier?: AuthorityTier;
  
  /** Query by created/updated date range */
  dateRange?: {
    from: string;
    to: string;
  };
  
  /** Limit results */
  limit?: number;
  
  /** Offset for pagination */
  offset?: number;
}

export interface TagRegistryStats {
  totalTags: number;
  tagsByNamespace: Record<string, number>;
  tagsByAuthorityTier: Record<AuthorityTier, number>;
  pendingRenames: number;
  cacheHitRate: number;
}

/**
 * PLIX Tag Registry
 * 
 * Provides queryable storage for PLIX tags with:
 * - Tag resolution and caching
 * - Rename governance with dependent tracking
 * - Authority tier tracking
 * - Integration with CMC for persistence
 */
export class PLIXTagRegistry {
  private tags: Map<string, TagDefinition>;
  private renames: Map<string, TagRename>; // fromTag -> TagRename
  private cache: Map<string, TagDefinition>;
  private cmcClient: any; // CMC client (to be injected)
  private stats: {
    cacheHits: number;
    cacheMisses: number;
  };
  
  constructor(options?: {
    cmcClient?: any;
  }) {
    this.tags = new Map();
    this.renames = new Map();
    this.cache = new Map();
    this.cmcClient = options?.cmcClient;
    this.stats = {
      cacheHits: 0,
      cacheMisses: 0
    };
  }
  
  /**
   * Register a new tag
   */
  async registerTag(
    tag: string,
    resolved: any,
    authorityTier: AuthorityTier,
    createdBy: string,
    metadata?: Record<string, any>
  ): Promise<TagDefinition> {
    // Parse tag
    const parsed = this.parseTag(tag);
    
    // Check if tag already exists
    if (this.tags.has(tag)) {
      throw new Error(`Tag already registered: ${tag}`);
    }
    
    // Create tag definition
    const definition: TagDefinition = {
      tag,
      namespace: parsed.namespace,
      path: parsed.path,
      revision: parsed.revision,
      hash: parsed.hash,
      resolved,
      authorityTier,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      createdBy,
      metadata
    };
    
    // Store in memory
    this.tags.set(tag, definition);
    this.cache.set(tag, definition);
    
    // Persist to CMC if available
    if (this.cmcClient) {
      await this.persistToCMC(definition);
    }
    
    return definition;
  }
  
  /**
   * Resolve a tag (with caching and rename handling)
   */
  async resolveTag(tag: string): Promise<TagDefinition | null> {
    // Check cache first
    if (this.cache.has(tag)) {
      this.stats.cacheHits++;
      return this.cache.get(tag)!;
    }
    
    this.stats.cacheMisses++;
    
    // Check for rename
    const rename = this.renames.get(tag);
    if (rename && rename.status === 'completed') {
      // Resolve renamed tag
      return this.resolveTag(rename.toTag);
    }
    
    // Check memory store
    if (this.tags.has(tag)) {
      const definition = this.tags.get(tag)!;
      this.cache.set(tag, definition);
      return definition;
    }
    
    // Try CMC if available
    if (this.cmcClient) {
      const cmcResult = await this.queryCMC(tag);
      if (cmcResult) {
        this.tags.set(tag, cmcResult);
        this.cache.set(tag, cmcResult);
        return cmcResult;
      }
    }
    
    return null;
  }
  
  /**
   * Query tags by criteria
   */
  async queryTags(query: TagQuery): Promise<TagDefinition[]> {
    let results: TagDefinition[] = Array.from(this.tags.values());
    
    // Filter by namespace
    if (query.namespace) {
      results = results.filter(t => t.namespace === query.namespace);
    }
    
    // Filter by path pattern
    if (query.pathPattern) {
      const pattern = new RegExp(query.pathPattern);
      results = results.filter(t => pattern.test(t.path));
    }
    
    // Filter by revision
    if (query.revision) {
      results = results.filter(t => t.revision === query.revision);
    }
    
    // Filter by authority tier
    if (query.authorityTier) {
      results = results.filter(t => t.authorityTier === query.authorityTier);
    }
    
    // Filter by date range
    if (query.dateRange) {
      results = results.filter(t => {
        const createdAt = new Date(t.createdAt);
        const from = new Date(query.dateRange!.from);
        const to = new Date(query.dateRange!.to);
        return createdAt >= from && createdAt <= to;
      });
    }
    
    // Apply pagination
    const offset = query.offset || 0;
    const limit = query.limit || 100;
    results = results.slice(offset, offset + limit);
    
    return results;
  }
  
  /**
   * Rename a tag (with governance)
   */
  async renameTag(
    fromTag: string,
    toTag: string,
    authorityTier: AuthorityTier,
    renamedBy: string,
    reason?: string
  ): Promise<TagRename> {
    // Verify tag exists
    const existingTag = await this.resolveTag(fromTag);
    if (!existingTag) {
      throw new Error(`Tag not found: ${fromTag}`);
    }
    
    // Verify authority tier is sufficient
    if (!this.hasAuthority(authorityTier, existingTag.authorityTier)) {
      throw new Error(`Insufficient authority tier: ${authorityTier} < ${existingTag.authorityTier}`);
    }
    
    // Check if toTag already exists
    if (this.tags.has(toTag)) {
      throw new Error(`Target tag already exists: ${toTag}`);
    }
    
    // Find dependents (tags that reference this tag)
    const dependents = await this.findDependents(fromTag);
    
    // Create rename record
    const rename: TagRename = {
      fromTag,
      toTag,
      authorityTier,
      renamedBy,
      timestamp: new Date().toISOString(),
      reason,
      dependents,
      acknowledgedBy: new Map(),
      status: 'pending'
    };
    
    // Store rename
    this.renames.set(fromTag, rename);
    
    // Persist to CMC if available
    if (this.cmcClient) {
      await this.persistRenameToCMC(rename);
    }
    
    return rename;
  }
  
  /**
   * Acknowledge a rename (by dependent)
   */
  async acknowledgeRename(
    fromTag: string,
    dependentTag: string,
    acknowledgedBy: string
  ): Promise<void> {
    const rename = this.renames.get(fromTag);
    if (!rename) {
      throw new Error(`Rename not found: ${fromTag}`);
    }
    
    if (!rename.dependents.includes(dependentTag)) {
      throw new Error(`Tag ${dependentTag} is not a dependent of ${fromTag}`);
    }
    
    // Mark as acknowledged
    rename.acknowledgedBy.set(dependentTag, new Date().toISOString());
    
    // Check if all dependents have acknowledged
    if (rename.acknowledgedBy.size === rename.dependents.length) {
      rename.status = 'acknowledged';
      
      // Complete the rename
      await this.completeRename(fromTag);
    }
    
    // Persist to CMC if available
    if (this.cmcClient) {
      await this.persistRenameToCMC(rename);
    }
  }
  
  /**
   * Complete a rename (after all dependents acknowledge)
   */
  private async completeRename(fromTag: string): Promise<void> {
    const rename = this.renames.get(fromTag);
    if (!rename) {
      return;
    }
    
    // Get original tag definition
    const originalTag = this.tags.get(fromTag);
    if (!originalTag) {
      return;
    }
    
    // Create new tag definition
    const newTag: TagDefinition = {
      ...originalTag,
      tag: rename.toTag,
      updatedAt: new Date().toISOString(),
      metadata: {
        ...originalTag.metadata,
        renamedFrom: fromTag,
        renamedAt: rename.timestamp
      }
    };
    
    // Register new tag
    this.tags.set(rename.toTag, newTag);
    this.cache.set(rename.toTag, newTag);
    
    // Remove old tag
    this.tags.delete(fromTag);
    this.cache.delete(fromTag);
    
    // Mark rename as completed
    rename.status = 'completed';
    
    // Persist to CMC if available
    if (this.cmcClient) {
      await this.persistToCMC(newTag);
      await this.persistRenameToCMC(rename);
    }
  }
  
  /**
   * Find tags that depend on a given tag
   */
  private async findDependents(tag: string): Promise<string[]> {
    const dependents: string[] = [];
    
    // Search through all tags for references
    for (const [tagKey, definition] of this.tags.entries()) {
      // Check if tag is referenced in resolved data
      const resolvedStr = JSON.stringify(definition.resolved);
      if (resolvedStr.includes(tag)) {
        dependents.push(tagKey);
      }
      
      // Check metadata
      if (definition.metadata) {
        const metadataStr = JSON.stringify(definition.metadata);
        if (metadataStr.includes(tag)) {
          dependents.push(tagKey);
        }
      }
    }
    
    return dependents;
  }
  
  /**
   * Parse tag into components
   */
  private parseTag(tag: string): {
    namespace: string;
    path: string;
    revision?: string;
    hash?: string;
  } {
    const match = tag.match(/^plix:\/\/([^#]+)(?:#rev@(.+))?$/);
    if (!match) {
      throw new Error(`Invalid tag format: ${tag}`);
    }
    
    const [, pathPart, hashPart] = match;
    const [namespace, ...pathParts] = pathPart.split('/');
    const path = pathParts.join('/');
    
    // Extract revision and hash from hashPart if present
    let revision: string | undefined;
    let hash: string | undefined;
    
    if (hashPart) {
      const hashMatch = hashPart.match(/^(.+?)@(.+)$/);
      if (hashMatch) {
        revision = hashMatch[1];
        hash = hashMatch[2];
      } else {
        hash = hashPart;
      }
    }
    
    return {
      namespace,
      path,
      revision,
      hash
    };
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
   * Persist tag definition to CMC
   */
  private async persistToCMC(definition: TagDefinition): Promise<void> {
    if (!this.cmcClient || typeof this.cmcClient.store_memory !== 'function') {
      return;
    }
    
    try {
      await this.cmcClient.store_memory({
        content: JSON.stringify(definition),
        tags: {
          type: 'plix_tag',
          tag: definition.tag,
          namespace: definition.namespace,
          path: definition.path,
          authority_tier: definition.authorityTier
        }
      });
    } catch (error) {
      console.error('Failed to persist tag to CMC:', error);
    }
  }
  
  /**
   * Query CMC for tag definition
   */
  private async queryCMC(tag: string): Promise<TagDefinition | null> {
    if (!this.cmcClient || typeof this.cmcClient.retrieve_memory !== 'function') {
      return null;
    }
    
    try {
      const result = await this.cmcClient.retrieve_memory({
        query: tag,
        tags: {
          type: 'plix_tag',
          tag: tag
        },
        limit: 1
      });
      
      if (result && result.results && result.results.length > 0) {
        const content = result.results[0].content;
        return JSON.parse(content) as TagDefinition;
      }
    } catch (error) {
      console.error('Failed to query CMC for tag:', error);
    }
    
    return null;
  }
  
  /**
   * Persist rename to CMC
   */
  private async persistRenameToCMC(rename: TagRename): Promise<void> {
    if (!this.cmcClient || typeof this.cmcClient.store_memory !== 'function') {
      return;
    }
    
    try {
      await this.cmcClient.store_memory({
        content: JSON.stringify(rename),
        tags: {
          type: 'plix_rename',
          from_tag: rename.fromTag,
          to_tag: rename.toTag,
          status: rename.status
        }
      });
    } catch (error) {
      console.error('Failed to persist rename to CMC:', error);
    }
  }
  
  /**
   * Get registry statistics
   */
  getStats(): TagRegistryStats {
    const tagsByNamespace: Record<string, number> = {};
    const tagsByAuthorityTier: Record<AuthorityTier, number> = {
      'S': 0,
      'A': 0,
      'B': 0,
      'C': 0
    };
    
    for (const tag of this.tags.values()) {
      tagsByNamespace[tag.namespace] = (tagsByNamespace[tag.namespace] || 0) + 1;
      tagsByAuthorityTier[tag.authorityTier]++;
    }
    
    const totalRequests = this.stats.cacheHits + this.stats.cacheMisses;
    const cacheHitRate = totalRequests > 0 
      ? this.stats.cacheHits / totalRequests 
      : 0;
    
    return {
      totalTags: this.tags.size,
      tagsByNamespace,
      tagsByAuthorityTier,
      pendingRenames: Array.from(this.renames.values()).filter(r => r.status === 'pending').length,
      cacheHitRate
    };
  }
  
  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
    this.stats.cacheHits = 0;
    this.stats.cacheMisses = 0;
  }
  
  /**
   * Get pending renames
   */
  getPendingRenames(): TagRename[] {
    return Array.from(this.renames.values()).filter(r => r.status === 'pending');
  }
  
  /**
   * Get rename history for a tag
   */
  getRenameHistory(tag: string): TagRename[] {
    const history: TagRename[] = [];
    
    // Check if tag was renamed from something
    for (const rename of this.renames.values()) {
      if (rename.toTag === tag && rename.status === 'completed') {
        history.push(rename);
      }
    }
    
    // Check if tag was renamed to something
    const rename = this.renames.get(tag);
    if (rename) {
      history.push(rename);
    }
    
    return history.sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
  }
}

