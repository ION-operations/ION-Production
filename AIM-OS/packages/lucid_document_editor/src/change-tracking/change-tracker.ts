/**
 * LUCID Document Editor - Change Tracker
 * 
 * Track and manage document changes
 */

import { DocumentChange, DocumentSection } from '../models';

export class ChangeTracker {
  private changes: DocumentChange[] = [];
  private maxHistorySize = 1000;

  /**
   * Track a change
   */
  trackChange(
    sectionId: string,
    type: DocumentChange['type'],
    before: string | undefined,
    after: string | undefined,
    author: string,
    metadata?: Record<string, unknown>
  ): DocumentChange {
    const change: DocumentChange = {
      id: `change-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      sectionId,
      type,
      before,
      after,
      timestamp: new Date().toISOString(),
      author,
      metadata,
    };

    this.changes.push(change);

    // Limit history size
    if (this.changes.length > this.maxHistorySize) {
      this.changes = this.changes.slice(-this.maxHistorySize);
    }

    return change;
  }

  /**
   * Get changes for a section
   */
  getChangesForSection(sectionId: string, limit?: number): DocumentChange[] {
    const sectionChanges = this.changes
      .filter(c => c.sectionId === sectionId)
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

    return limit ? sectionChanges.slice(0, limit) : sectionChanges;
  }

  /**
   * Get all changes
   */
  getAllChanges(limit?: number): DocumentChange[] {
    const sorted = [...this.changes].sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
    return limit ? sorted.slice(0, limit) : sorted;
  }

  /**
   * Get changes by author
   */
  getChangesByAuthor(author: string, limit?: number): DocumentChange[] {
    const authorChanges = this.changes
      .filter(c => c.author === author)
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

    return limit ? authorChanges.slice(0, limit) : authorChanges;
  }

  /**
   * Get changes in time range
   */
  getChangesInRange(startTime: string, endTime: string): DocumentChange[] {
    const start = new Date(startTime).getTime();
    const end = new Date(endTime).getTime();

    return this.changes.filter(c => {
      const time = new Date(c.timestamp).getTime();
      return time >= start && time <= end;
    });
  }

  /**
   * Clear changes
   */
  clearChanges(sectionId?: string): void {
    if (sectionId) {
      this.changes = this.changes.filter(c => c.sectionId !== sectionId);
    } else {
      this.changes = [];
    }
  }

  /**
   * Get change statistics
   */
  getStatistics(): {
    totalChanges: number;
    changesByType: Record<string, number>;
    changesByAuthor: Record<string, number>;
    changesBySection: Record<string, number>;
  } {
    const byType: Record<string, number> = {};
    const byAuthor: Record<string, number> = {};
    const bySection: Record<string, number> = {};

    this.changes.forEach(change => {
      byType[change.type] = (byType[change.type] || 0) + 1;
      byAuthor[change.author] = (byAuthor[change.author] || 0) + 1;
      bySection[change.sectionId] = (bySection[change.sectionId] || 0) + 1;
    });

    return {
      totalChanges: this.changes.length,
      changesByType: byType,
      changesByAuthor: byAuthor,
      changesBySection: bySection,
    };
  }
}

