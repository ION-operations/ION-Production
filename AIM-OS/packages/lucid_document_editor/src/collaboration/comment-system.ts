/**
 * LUCID Document Editor - Comment System
 * 
 * Comment management for collaborative editing
 */

import { Comment } from './collaboration-engine';

export interface CommentThread {
  id: string;
  sectionId: string;
  position: { offset: number };
  comments: Comment[];
  resolved: boolean;
  createdAt: string;
  updatedAt: string;
}

export class CommentManager {
  private threads: Map<string, CommentThread> = new Map();

  /**
   * Create a new comment thread
   */
  createThread(
    sectionId: string,
    position: { offset: number },
    content: string,
    author: string,
    authorName: string
  ): CommentThread {
    const comment: Comment = {
      id: `comment-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      sectionId,
      position,
      content,
      author,
      authorName,
      createdAt: new Date().toISOString(),
      resolved: false,
    };

    const thread: CommentThread = {
      id: `thread-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      sectionId,
      position,
      comments: [comment],
      resolved: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    this.threads.set(thread.id, thread);
    return thread;
  }

  /**
   * Add reply to thread
   */
  addReply(
    threadId: string,
    content: string,
    author: string,
    authorName: string
  ): Comment | null {
    const thread = this.threads.get(threadId);
    if (!thread) return null;

    const reply: Comment = {
      id: `comment-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      sectionId: thread.sectionId,
      position: thread.position,
      content,
      author,
      authorName,
      createdAt: new Date().toISOString(),
      resolved: false,
    };

    thread.comments.push(reply);
    thread.updatedAt = new Date().toISOString();
    this.threads.set(threadId, thread);

    return reply;
  }

  /**
   * Resolve thread
   */
  resolveThread(threadId: string, resolvedBy: string): boolean {
    const thread = this.threads.get(threadId);
    if (!thread) return false;

    thread.resolved = true;
    thread.updatedAt = new Date().toISOString();
    thread.comments.forEach(comment => {
      comment.resolved = true;
      comment.resolvedBy = resolvedBy;
      comment.resolvedAt = new Date().toISOString();
    });

    this.threads.set(threadId, thread);
    return true;
  }

  /**
   * Get threads for section
   */
  getThreadsForSection(sectionId: string, includeResolved: boolean = false): CommentThread[] {
    const threads = Array.from(this.threads.values())
      .filter(t => t.sectionId === sectionId);
    
    return includeResolved
      ? threads
      : threads.filter(t => !t.resolved);
  }

  /**
   * Get all threads
   */
  getAllThreads(includeResolved: boolean = false): CommentThread[] {
    const threads = Array.from(this.threads.values());
    return includeResolved ? threads : threads.filter(t => !t.resolved);
  }

  /**
   * Get thread by ID
   */
  getThread(threadId: string): CommentThread | undefined {
    return this.threads.get(threadId);
  }

  /**
   * Delete thread
   */
  deleteThread(threadId: string): boolean {
    return this.threads.delete(threadId);
  }
}

