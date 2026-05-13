/**
 * LUCID Document Editor - Section Locking
 * 
 * Lock management for document sections
 */

import { DocumentSection } from '../models';

export interface SectionLock {
  sectionId: string;
  lockedBy: string;
  lockedAt: string;
  expiresAt?: string;
  reason?: string;
}

export class SectionLockManager {
  private locks: Map<string, SectionLock> = new Map();
  private defaultTimeout = 30 * 60 * 1000; // 30 minutes

  /**
   * Lock a section
   */
  lockSection(
    sectionId: string,
    userId: string,
    timeout?: number,
    reason?: string
  ): SectionLock {
    const now = new Date();
    const expiresAt = timeout
      ? new Date(now.getTime() + timeout)
      : new Date(now.getTime() + this.defaultTimeout);

    const lock: SectionLock = {
      sectionId,
      lockedBy: userId,
      lockedAt: now.toISOString(),
      expiresAt: expiresAt.toISOString(),
      reason,
    };

    this.locks.set(sectionId, lock);
    return lock;
  }

  /**
   * Unlock a section
   */
  unlockSection(sectionId: string, userId: string): boolean {
    const lock = this.locks.get(sectionId);
    if (!lock) return false;

    // Only the user who locked it can unlock it (or admin)
    if (lock.lockedBy !== userId) {
      return false;
    }

    this.locks.delete(sectionId);
    return true;
  }

  /**
   * Check if a section is locked
   */
  isLocked(sectionId: string): boolean {
    const lock = this.locks.get(sectionId);
    if (!lock) return false;

    // Check if lock expired
    if (lock.expiresAt) {
      const expiresAt = new Date(lock.expiresAt);
      if (expiresAt < new Date()) {
        this.locks.delete(sectionId);
        return false;
      }
    }

    return true;
  }

  /**
   * Get lock information
   */
  getLock(sectionId: string): SectionLock | undefined {
    const lock = this.locks.get(sectionId);
    if (!lock) return undefined;

    // Check if expired
    if (lock.expiresAt) {
      const expiresAt = new Date(lock.expiresAt);
      if (expiresAt < new Date()) {
        this.locks.delete(sectionId);
        return undefined;
      }
    }

    return lock;
  }

  /**
   * Check if user can edit section
   */
  canEdit(sectionId: string, userId: string): boolean {
    const lock = this.locks.get(sectionId);
    if (!lock) return true;

    // Check if expired
    if (lock.expiresAt) {
      const expiresAt = new Date(lock.expiresAt);
      if (expiresAt < new Date()) {
        this.locks.delete(sectionId);
        return true;
      }
    }

    // Only the user who locked it can edit
    return lock.lockedBy === userId;
  }

  /**
   * Extend lock timeout
   */
  extendLock(sectionId: string, userId: string, additionalTime: number): boolean {
    const lock = this.locks.get(sectionId);
    if (!lock || lock.lockedBy !== userId) return false;

    if (lock.expiresAt) {
      const expiresAt = new Date(lock.expiresAt);
      lock.expiresAt = new Date(expiresAt.getTime() + additionalTime).toISOString();
    } else {
      lock.expiresAt = new Date(Date.now() + additionalTime).toISOString();
    }

    this.locks.set(sectionId, lock);
    return true;
  }

  /**
   * Clear all expired locks
   */
  clearExpiredLocks(): void {
    const now = new Date();
    for (const [sectionId, lock] of this.locks.entries()) {
      if (lock.expiresAt) {
        const expiresAt = new Date(lock.expiresAt);
        if (expiresAt < now) {
          this.locks.delete(sectionId);
        }
      }
    }
  }
}

