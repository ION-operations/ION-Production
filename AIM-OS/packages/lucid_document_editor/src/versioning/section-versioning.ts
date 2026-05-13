/**
 * LUCID Document Editor - Section Versioning
 * 
 * Version management for document sections
 */

import { DocumentSection, DocumentChange } from '../models';

export interface SectionVersion {
  id: string;
  sectionId: string;
  version: number;
  content: string;
  timestamp: string;
  author: string;
  reason?: string;
  changeId?: string;
}

export class SectionVersionManager {
  private versions: Map<string, SectionVersion[]> = new Map();

  /**
   * Create a new version of a section
   */
  createVersion(
    section: DocumentSection,
    author: string,
    reason?: string,
    changeId?: string
  ): SectionVersion {
    const version: SectionVersion = {
      id: `version-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      sectionId: section.id,
      version: section.version,
      content: section.content,
      timestamp: new Date().toISOString(),
      author,
      reason,
      changeId,
    };

    const versions = this.versions.get(section.id) || [];
    versions.push(version);
    this.versions.set(section.id, versions);

    return version;
  }

  /**
   * Get all versions for a section
   */
  getVersions(sectionId: string): SectionVersion[] {
    return this.versions.get(sectionId) || [];
  }

  /**
   * Get a specific version
   */
  getVersion(sectionId: string, version: number): SectionVersion | undefined {
    const versions = this.versions.get(sectionId) || [];
    return versions.find(v => v.version === version);
  }

  /**
   * Get the latest version
   */
  getLatestVersion(sectionId: string): SectionVersion | undefined {
    const versions = this.versions.get(sectionId) || [];
    return versions.length > 0 ? versions[versions.length - 1] : undefined;
  }

  /**
   * Compare two versions
   */
  compareVersions(
    sectionId: string,
    version1: number,
    version2: number
  ): { added: string; removed: string; changed: boolean } {
    const v1 = this.getVersion(sectionId, version1);
    const v2 = this.getVersion(sectionId, version2);

    if (!v1 || !v2) {
      return { added: '', removed: '', changed: false };
    }

    return {
      added: this.diffContent(v1.content, v2.content).added,
      removed: this.diffContent(v1.content, v2.content).removed,
      changed: v1.content !== v2.content,
    };
  }

  /**
   * Rollback to a specific version
   */
  rollbackToVersion(
    sectionId: string,
    version: number,
    author: string,
    reason?: string
  ): SectionVersion | undefined {
    const targetVersion = this.getVersion(sectionId, version);
    if (!targetVersion) return undefined;

    // Create new version with old content
    const rollbackVersion: SectionVersion = {
      id: `version-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      sectionId,
      version: targetVersion.version + 1,
      content: targetVersion.content,
      timestamp: new Date().toISOString(),
      author,
      reason: reason || `Rollback to version ${version}`,
    };

    const versions = this.versions.get(sectionId) || [];
    versions.push(rollbackVersion);
    this.versions.set(sectionId, versions);

    return rollbackVersion;
  }

  private diffContent(oldContent: string, newContent: string): { added: string; removed: string } {
    // Simple diff algorithm (can be enhanced with proper diff library)
    const oldLines = oldContent.split('\n');
    const newLines = newContent.split('\n');
    
    const added: string[] = [];
    const removed: string[] = [];

    const maxLen = Math.max(oldLines.length, newLines.length);
    for (let i = 0; i < maxLen; i++) {
      if (i >= oldLines.length) {
        added.push(newLines[i]);
      } else if (i >= newLines.length) {
        removed.push(oldLines[i]);
      } else if (oldLines[i] !== newLines[i]) {
        added.push(newLines[i]);
        removed.push(oldLines[i]);
      }
    }

    return {
      added: added.join('\n'),
      removed: removed.join('\n'),
    };
  }
}

