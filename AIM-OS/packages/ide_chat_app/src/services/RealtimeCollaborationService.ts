/**
 * Real-time Collaboration Service
 * 
 * Handles real-time synchronization and collaboration features
 * for the Lucid Orchestrator system.
 */

import { EventEmitter } from 'events';
import { LucidOrchestratorData, Event } from '../../../lucid_orchestrator/data_models/core_interfaces';

export interface CollaborationUser {
  id: string;
  name: string;
  color: string;
  cursor?: {
    x: number;
    y: number;
    pane: string;
  };
  selection?: {
    nodeId?: string;
    fileId?: string;
    specId?: string;
    eventId?: string;
  };
  lastSeen: Date;
}

export interface CollaborationEvent {
  type: 'cursor_move' | 'selection_change' | 'data_update' | 'user_join' | 'user_leave';
  userId: string;
  timestamp: Date;
  data: any;
}

export class RealtimeCollaborationService extends EventEmitter {
  private users: Map<string, CollaborationUser> = new Map();
  private currentUser: CollaborationUser | null = null;
  private isConnected = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private syncInterval: NodeJS.Timeout | null = null;

  constructor() {
    super();
    this.setupEventHandlers();
  }

  /**
   * Initialize collaboration service
   */
  async initialize(userId: string, userName: string): Promise<void> {
    this.currentUser = {
      id: userId,
      name: userName,
      color: this.generateUserColor(),
      lastSeen: new Date()
    };

    this.users.set(userId, this.currentUser);
    this.emit('user_joined', this.currentUser);
    
    // Start heartbeat
    this.startHeartbeat();
    
    // Start sync interval
    this.startSyncInterval();
    
    this.isConnected = true;
    this.emit('connected');
  }

  /**
   * Disconnect from collaboration
   */
  async disconnect(): Promise<void> {
    if (this.currentUser) {
      this.emit('user_left', this.currentUser);
      this.users.delete(this.currentUser.id);
    }

    this.stopHeartbeat();
    this.stopSyncInterval();
    this.isConnected = false;
    this.emit('disconnected');
  }

  /**
   * Update user cursor position
   */
  updateCursor(x: number, y: number, pane: string): void {
    if (!this.currentUser) return;

    this.currentUser.cursor = { x, y, pane };
    this.currentUser.lastSeen = new Date();

    this.broadcastEvent({
      type: 'cursor_move',
      userId: this.currentUser.id,
      timestamp: new Date(),
      data: { x, y, pane }
    });
  }

  /**
   * Update user selection
   */
  updateSelection(selection: CollaborationUser['selection']): void {
    if (!this.currentUser) return;

    this.currentUser.selection = selection;
    this.currentUser.lastSeen = new Date();

    this.broadcastEvent({
      type: 'selection_change',
      userId: this.currentUser.id,
      timestamp: new Date(),
      data: selection
    });
  }

  /**
   * Broadcast data update
   */
  broadcastDataUpdate(data: Partial<LucidOrchestratorData>): void {
    if (!this.currentUser) return;

    this.broadcastEvent({
      type: 'data_update',
      userId: this.currentUser.id,
      timestamp: new Date(),
      data
    });
  }

  /**
   * Get all connected users
   */
  getUsers(): CollaborationUser[] {
    return Array.from(this.users.values());
  }

  /**
   * Get current user
   */
  getCurrentUser(): CollaborationUser | null {
    return this.currentUser;
  }

  /**
   * Check if connected
   */
  isServiceConnected(): boolean {
    return this.isConnected;
  }

  /**
   * Setup event handlers
   */
  private setupEventHandlers(): void {
    this.on('user_joined', (user: CollaborationUser) => {
      console.log(`User joined: ${user.name}`);
    });

    this.on('user_left', (user: CollaborationUser) => {
      console.log(`User left: ${user.name}`);
    });

    this.on('cursor_move', (event: CollaborationEvent) => {
      const user = this.users.get(event.userId);
      if (user && user.id !== this.currentUser?.id) {
        user.cursor = event.data;
        this.emit('user_cursor_updated', user);
      }
    });

    this.on('selection_change', (event: CollaborationEvent) => {
      const user = this.users.get(event.userId);
      if (user && user.id !== this.currentUser?.id) {
        user.selection = event.data;
        this.emit('user_selection_updated', user);
      }
    });

    this.on('data_update', (event: CollaborationEvent) => {
      if (event.userId !== this.currentUser?.id) {
        this.emit('remote_data_update', event.data);
      }
    });
  }

  /**
   * Broadcast event to all users
   */
  private broadcastEvent(event: CollaborationEvent): void {
    // In a real implementation, this would send to a WebSocket server
    // For now, we'll just emit locally
    this.emit(event.type, event);
  }

  /**
   * Generate a unique color for a user
   */
  private generateUserColor(): string {
    const colors = [
      '#3B82F6', // Blue
      '#10B981', // Green
      '#F59E0B', // Yellow
      '#EF4444', // Red
      '#8B5CF6', // Purple
      '#06B6D4', // Cyan
      '#F97316', // Orange
      '#84CC16', // Lime
      '#EC4899', // Pink
      '#6B7280'  // Gray
    ];

    const usedColors = Array.from(this.users.values()).map(u => u.color);
    const availableColors = colors.filter(c => !usedColors.includes(c));
    
    return availableColors.length > 0 
      ? availableColors[0] 
      : colors[Math.floor(Math.random() * colors.length)];
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.currentUser) {
        this.currentUser.lastSeen = new Date();
        this.broadcastEvent({
          type: 'cursor_move',
          userId: this.currentUser.id,
          timestamp: new Date(),
          data: this.currentUser.cursor || { x: 0, y: 0, pane: 'code' }
        });
      }
    }, 5000); // Heartbeat every 5 seconds
  }

  /**
   * Stop heartbeat
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * Start sync interval for data synchronization
   */
  private startSyncInterval(): void {
    this.syncInterval = setInterval(() => {
      // In a real implementation, this would sync with the server
      // For now, we'll just emit a sync event
      this.emit('sync_required');
    }, 10000); // Sync every 10 seconds
  }

  /**
   * Stop sync interval
   */
  private stopSyncInterval(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  /**
   * Simulate user joining (for demo purposes)
   */
  simulateUserJoin(userId: string, userName: string): void {
    const user: CollaborationUser = {
      id: userId,
      name: userName,
      color: this.generateUserColor(),
      lastSeen: new Date()
    };

    this.users.set(userId, user);
    this.emit('user_joined', user);
  }

  /**
   * Simulate user leaving (for demo purposes)
   */
  simulateUserLeave(userId: string): void {
    const user = this.users.get(userId);
    if (user) {
      this.users.delete(userId);
      this.emit('user_left', user);
    }
  }

  /**
   * Simulate cursor movement (for demo purposes)
   */
  simulateCursorMove(userId: string, x: number, y: number, pane: string): void {
    const user = this.users.get(userId);
    if (user) {
      user.cursor = { x, y, pane };
      user.lastSeen = new Date();
      this.emit('user_cursor_updated', user);
    }
  }

  /**
   * Simulate selection change (for demo purposes)
   */
  simulateSelectionChange(userId: string, selection: CollaborationUser['selection']): void {
    const user = this.users.get(userId);
    if (user) {
      user.selection = selection;
      user.lastSeen = new Date();
      this.emit('user_selection_updated', user);
    }
  }

  /**
   * Cleanup resources
   */
  cleanup(): void {
    this.stopHeartbeat();
    this.stopSyncInterval();
    this.removeAllListeners();
    this.users.clear();
    this.currentUser = null;
    this.isConnected = false;
  }
}
