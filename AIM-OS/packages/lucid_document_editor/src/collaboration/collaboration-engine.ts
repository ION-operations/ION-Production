/**
 * LUCID Document Editor - Collaboration Engine
 * 
 * Yjs CRDT integration for real-time collaboration
 */

import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';
import { DocumentModel, DocumentSection } from '../models';

export interface CollaborationConfig {
  documentId: string;
  userId: string;
  userName: string;
  websocketUrl: string;
  room?: string;
}

export interface UserPresence {
  userId: string;
  userName: string;
  cursor?: { sectionId: string; offset: number };
  selection?: { sectionId: string; start: number; end: number };
  color: string;
  avatar?: string;
}

export interface Comment {
  id: string;
  sectionId: string;
  position: { offset: number };
  content: string;
  author: string;
  authorName: string;
  createdAt: string;
  resolved: boolean;
  resolvedBy?: string;
  resolvedAt?: string;
  replies?: Comment[];
}

export interface Conflict {
  id: string;
  sectionId: string;
  type: 'content' | 'structure' | 'metadata';
  local: any;
  remote: any;
  timestamp: string;
}

export class CollaborationEngine {
  private ydoc: Y.Doc;
  private provider: WebsocketProvider | null = null;
  private awareness: any;
  private config: CollaborationConfig;
  private listeners: Map<string, Set<Function>> = new Map();
  private comments: Y.Array<any>;
  private sections: Y.Map<any>;
  private users: Map<string, UserPresence> = new Map();

  constructor(config: CollaborationConfig) {
    this.config = config;
    this.ydoc = new Y.Doc();
    
    // Initialize Yjs data structures
    this.sections = this.ydoc.getMap('sections');
    this.comments = this.ydoc.getArray('comments');
    
    // Initialize awareness (presence)
    this.awareness = this.ydoc.getMap('awareness');
  }

  /**
   * Connect to collaboration server
   */
  async connect(): Promise<void> {
    const room = this.config.room || `doc-${this.config.documentId}`;
    
    this.provider = new WebsocketProvider(
      this.config.websocketUrl,
      room,
      this.ydoc
    );

    // Set up awareness (presence)
    this.provider.awareness.setLocalStateField('user', {
      id: this.config.userId,
      name: this.config.userName,
      color: this.generateUserColor(this.config.userId),
    });

    // Listen for awareness changes (user presence)
    this.provider.awareness.on('change', () => {
      this.updateUserPresence();
      this.emit('presence', Array.from(this.users.values()));
    });

    // Listen for document changes
    this.ydoc.on('update', () => {
      this.emit('change', this.getDocument());
    });

    // Listen for comments
    this.comments.observe(() => {
      this.emit('comments', this.getComments());
    });

    return new Promise((resolve) => {
      this.provider!.on('status', (event: any) => {
        if (event.status === 'connected') {
          resolve();
        }
      });
    });
  }

  /**
   * Disconnect from collaboration server
   */
  disconnect(): void {
    if (this.provider) {
      this.provider.destroy();
      this.provider = null;
    }
  }

  /**
   * Update section content
   */
  updateSection(sectionId: string, content: string): void {
    const sectionMap = this.sections.get(sectionId);
    if (sectionMap) {
      sectionMap.set('content', content);
      sectionMap.set('updatedAt', new Date().toISOString());
    } else {
      const newSection = new Y.Map();
      newSection.set('id', sectionId);
      newSection.set('content', content);
      newSection.set('updatedAt', new Date().toISOString());
      this.sections.set(sectionId, newSection);
    }
  }

  /**
   * Add comment
   */
  addComment(comment: Omit<Comment, 'id' | 'createdAt'>): Comment {
    const newComment: Comment = {
      ...comment,
      id: `comment-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      createdAt: new Date().toISOString(),
      resolved: false,
      replies: [],
    };

    this.comments.push([newComment]);
    return newComment;
  }

  /**
   * Get all comments
   */
  getComments(sectionId?: string): Comment[] {
    const allComments = this.comments.toArray() as Comment[];
    return sectionId
      ? allComments.filter(c => c.sectionId === sectionId)
      : allComments;
  }

  /**
   * Resolve comment
   */
  resolveComment(commentId: string, resolvedBy: string): void {
    const comments = this.comments.toArray() as Comment[];
    const index = comments.findIndex(c => c.id === commentId);
    if (index !== -1) {
      const comment = comments[index];
      comment.resolved = true;
      comment.resolvedBy = resolvedBy;
      comment.resolvedAt = new Date().toISOString();
      this.comments.delete(index);
      this.comments.insert(index, [comment]);
    }
  }

  /**
   * Get active users
   */
  getActiveUsers(): UserPresence[] {
    return Array.from(this.users.values());
  }

  /**
   * Update user cursor position
   */
  updateCursor(sectionId: string, offset: number): void {
    this.provider?.awareness.setLocalStateField('cursor', {
      sectionId,
      offset,
    });
  }

  /**
   * Update user selection
   */
  updateSelection(sectionId: string, start: number, end: number): void {
    this.provider?.awareness.setLocalStateField('selection', {
      sectionId,
      start,
      end,
    });
  }

  /**
   * Get document from Yjs
   */
  getDocument(): DocumentModel {
    const sections: DocumentSection[] = [];
    this.sections.forEach((sectionMap, sectionId) => {
      sections.push({
        id: sectionId,
        title: sectionMap.get('title') || 'Untitled Section',
        content: sectionMap.get('content') || '',
        type: sectionMap.get('type') || 'text',
        tags: sectionMap.get('tags') || [],
        metadata: sectionMap.get('metadata') || {},
        version: sectionMap.get('version') || 1,
        locked: sectionMap.get('locked') || false,
        lockedBy: sectionMap.get('lockedBy'),
        createdAt: sectionMap.get('createdAt') || new Date().toISOString(),
        updatedAt: sectionMap.get('updatedAt') || new Date().toISOString(),
      });
    });

    return {
      id: this.config.documentId,
      title: this.ydoc.getMap('document').get('title') || 'Untitled Document',
      description: this.ydoc.getMap('document').get('description'),
      sections,
      tags: this.ydoc.getMap('document').get('tags') || [],
      metadata: this.ydoc.getMap('document').get('metadata') || {
        totalWords: 0,
        totalSections: sections.length,
        totalMathBlocks: 0,
        totalCodeBlocks: 0,
        estimatedReadingTime: 0,
        language: 'en',
        aiManaged: false,
      },
      version: this.ydoc.getMap('document').get('version') || 1,
      createdAt: this.ydoc.getMap('document').get('createdAt') || new Date().toISOString(),
      updatedAt: this.ydoc.getMap('document').get('updatedAt') || new Date().toISOString(),
      createdBy: this.ydoc.getMap('document').get('createdBy') || 'user',
      collaborators: Array.from(this.users.keys()),
    };
  }

  /**
   * Sync document to Yjs
   */
  syncDocument(document: DocumentModel): void {
    const docMap = this.ydoc.getMap('document');
    docMap.set('title', document.title);
    docMap.set('description', document.description);
    docMap.set('tags', document.tags);
    docMap.set('metadata', document.metadata);
    docMap.set('version', document.version);
    docMap.set('updatedAt', document.updatedAt);

    // Sync sections
    document.sections.forEach(section => {
      const sectionMap = this.sections.get(section.id) || new Y.Map();
      sectionMap.set('id', section.id);
      sectionMap.set('title', section.title);
      sectionMap.set('content', section.content);
      sectionMap.set('type', section.type);
      sectionMap.set('tags', section.tags);
      sectionMap.set('metadata', section.metadata);
      sectionMap.set('version', section.version);
      sectionMap.set('locked', section.locked);
      sectionMap.set('lockedBy', section.lockedBy);
      sectionMap.set('createdAt', section.createdAt);
      sectionMap.set('updatedAt', section.updatedAt);
      this.sections.set(section.id, sectionMap);
    });
  }

  /**
   * Event listeners
   */
  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
  }

  off(event: string, callback: Function): void {
    this.listeners.get(event)?.delete(callback);
  }

  private emit(event: string, data: any): void {
    this.listeners.get(event)?.forEach(callback => callback(data));
  }

  private updateUserPresence(): void {
    this.users.clear();
    const states = this.provider?.awareness.getStates();
    if (states) {
      states.forEach((state: any, clientId: number) => {
        if (state.user) {
          this.users.set(state.user.id, {
            userId: state.user.id,
            userName: state.user.name,
            cursor: state.cursor,
            selection: state.selection,
            color: state.user.color || this.generateUserColor(state.user.id),
          });
        }
      });
    }
  }

  private generateUserColor(userId: string): string {
    const colors = [
      '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
      '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52BE80',
    ];
    const hash = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[hash % colors.length];
  }
}

