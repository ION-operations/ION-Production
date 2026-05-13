/**
 * Lucid Orchestrator - Event Bus
 * 
 * This module implements the Event Bus that synchronizes all four panes
 * of the Lucid Orchestrator consciousness interface.
 */

import { IRNode, IRGraph } from '../graph_engine/ir_model';
import { SpecBlock } from '../spec_engine/spec_model';
import { TimelineEvent, TimelineSpan } from '../timeline_engine/timeline_model';

type Listener = (...args: any[]) => void;

class SimpleEventEmitter {
  private listeners: Map<string, Set<Listener>> = new Map();

  on(event: string, listener: Listener): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(listener);
  }

  off(event: string, listener: Listener): void {
    this.listeners.get(event)?.delete(listener);
  }

  emit(event: string, ...args: unknown[]): void {
    const listeners = this.listeners.get(event);
    if (!listeners) return;
    for (const listener of Array.from(listeners)) {
      listener(...(args as []));
    }
  }

  listenerCount(event?: string): number {
    if (event) {
      return this.listeners.get(event)?.size ?? 0;
    }
    let count = 0;
    for (const listeners of this.listeners.values()) {
      count += listeners.size;
    }
    return count;
  }

  removeAllListeners(event?: string): void {
    if (event) {
      this.listeners.delete(event);
    } else {
      this.listeners.clear();
    }
  }
}

export type FocusEventType = 
  | 'FOCUS_NODE'
  | 'FOCUS_SPEC'
  | 'FOCUS_TIMELINE'
  | 'FOCUS_CODE'
  | 'UNFOCUS'
  | 'HOVER_NODE'
  | 'HOVER_SPEC'
  | 'HOVER_TIMELINE'
  | 'HOVER_CODE';

export type UpdateEventType =
  | 'NODE_ADDED'
  | 'NODE_UPDATED'
  | 'NODE_REMOVED'
  | 'NODE_STATUS_CHANGED'
  | 'SPEC_ADDED'
  | 'SPEC_UPDATED'
  | 'SPEC_REMOVED'
  | 'SPEC_STATUS_CHANGED'
  | 'TIMELINE_EVENT_ADDED'
  | 'TIMELINE_SPAN_ADDED'
  | 'DRIFT_DETECTED'
  | 'VIOLATION_DETECTED';

export interface FocusEvent {
  /** Event type */
  type: FocusEventType;
  
  /** Event timestamp */
  timestamp: string;
  
  /** Node ID being focused */
  nodeId?: string;
  
  /** Spec ID being focused */
  specId?: string;
  
  /** Timeline event ID being focused */
  eventId?: string;
  
  /** Code location being focused */
  codeLocation?: {
    filePath: string;
    startLine: number;
    endLine: number;
    startColumn?: number;
    endColumn?: number;
  };
  
  /** Source pane that triggered the focus */
  sourcePane: 'code' | 'blueprint' | 'spec' | 'timeline';
  
  /** Event metadata */
  metadata?: Record<string, any>;
}

export interface UpdateEvent {
  /** Event type */
  type: UpdateEventType;
  
  /** Node ID (if applicable) */
  nodeId?: string;
  
  /** Spec ID (if applicable) */
  specId?: string;
  
  /** Timeline event ID (if applicable) */
  eventId?: string;
  
  /** Event data */
  data?: any;
  
  /** Event timestamp */
  timestamp: number;
  
  /** Source of the update */
  source: 'graph_engine' | 'spec_engine' | 'timeline_engine' | 'external';
  
  /** Event metadata */
  metadata?: Record<string, any>;
}

export interface EventBusConfig {
  /** Enable focus synchronization */
  enableFocusSync: boolean;
  
  /** Enable update broadcasting */
  enableUpdateBroadcasting: boolean;
  
  /** Enable event logging */
  enableEventLogging: boolean;
  
  /** Maximum event history */
  maxEventHistory: number;
  
  /** Event deduplication window in milliseconds */
  deduplicationWindow: number;
}

export interface EventBusStatus {
  /** Current status */
  status: 'running' | 'stopped' | 'error';
  
  /** Number of active listeners */
  activeListeners: number;
  
  /** Number of events processed */
  eventsProcessed: number;
  
  /** Last activity timestamp */
  lastActivity: string;
  
  /** Error message if status is error */
  error?: string;
}

export class EventBus extends SimpleEventEmitter {
  private config: EventBusConfig;
  private status: EventBusStatus;
  private eventHistory: (FocusEvent | UpdateEvent)[] = [];
  private deduplicationCache: Map<string, number> = new Map();
  
  constructor(config: Partial<EventBusConfig> = {}) {
    super();
    
    this.config = {
      enableFocusSync: true,
      enableUpdateBroadcasting: true,
      enableEventLogging: true,
      maxEventHistory: 1000,
      deduplicationWindow: 100, // 100ms
      ...config
    };
    
    this.status = {
      status: 'running',
      activeListeners: 0,
      eventsProcessed: 0,
      lastActivity: new Date().toISOString()
    };
    
    this.setupEventHandlers();
  }
  
  /**
   * Emit a focus event
   */
  emitFocusEvent(event: Omit<FocusEvent, 'timestamp'>): void {
    if (!this.config.enableFocusSync) return;
    
    const focusEvent: FocusEvent = {
      ...event,
      timestamp: new Date().toISOString()
    };
    
    // Check for deduplication
    if (this.isDuplicateEvent(focusEvent)) return;
    
    this.processEvent(focusEvent);
    this.emit('focus', focusEvent);
  }
  
  /**
   * Emit an update event
   */
  emitUpdateEvent(event: Omit<UpdateEvent, 'timestamp'>): void {
    if (!this.config.enableUpdateBroadcasting) return;
    
    const updateEvent: UpdateEvent = {
      ...event,
      timestamp: Date.now()
    };
    
    // Check for deduplication
    if (this.isDuplicateEvent(updateEvent)) return;
    
    this.processEvent(updateEvent);
    this.emit('update', updateEvent);
  }
  
  /**
   * Subscribe to focus events
   */
  onFocus(callback: (event: FocusEvent) => void): void {
    this.on('focus', callback);
    this.updateListenerCount();
  }
  
  /**
   * Subscribe to update events
   */
  onUpdate(callback: (event: UpdateEvent) => void): void {
    this.on('update', callback);
    this.updateListenerCount();
  }
  
  /**
   * Subscribe to specific focus event types
   */
  onFocusType(type: FocusEventType, callback: (event: FocusEvent) => void): void {
    this.on('focus', (event: FocusEvent) => {
      if (event.type === type) {
        callback(event);
      }
    });
    this.updateListenerCount();
  }
  
  /**
   * Subscribe to specific update event types
   */
  onUpdateType(type: UpdateEventType, callback: (event: UpdateEvent) => void): void {
    this.on('update', (event: UpdateEvent) => {
      if (event.type === type) {
        callback(event);
      }
    });
    this.updateListenerCount();
  }
  
  /**
   * Unsubscribe from focus events
   */
  offFocus(callback: (event: FocusEvent) => void): void {
    this.off('focus', callback);
    this.updateListenerCount();
  }
  
  /**
   * Unsubscribe from update events
   */
  offUpdate(callback: (event: UpdateEvent) => void): void {
    this.off('update', callback);
    this.updateListenerCount();
  }
  
  /**
   * Get event history
   */
  getEventHistory(): (FocusEvent | UpdateEvent)[] {
    return [...this.eventHistory];
  }
  
  /**
   * Get events for a specific node
   */
  getEventsForNode(nodeId: string): (FocusEvent | UpdateEvent)[] {
    return this.eventHistory.filter(event => 
      event.nodeId === nodeId
    );
  }
  
  /**
   * Get events for a specific spec
   */
  getEventsForSpec(specId: string): (FocusEvent | UpdateEvent)[] {
    return this.eventHistory.filter(event => 
      event.specId === specId
    );
  }
  
  /**
   * Get recent events
   */
  getRecentEvents(count: number = 10): (FocusEvent | UpdateEvent)[] {
    return this.eventHistory.slice(-count);
  }
  
  /**
   * Clear event history
   */
  clearHistory(): void {
    this.eventHistory = [];
    this.deduplicationCache.clear();
  }
  
  /**
   * Get event bus status
   */
  getStatus(): EventBusStatus {
    return { ...this.status };
  }
  
  /**
   * Stop the event bus
   */
  stop(): void {
    this.status.status = 'stopped';
    this.removeAllListeners();
    this.status.activeListeners = 0;
  }
  
  /**
   * Start the event bus
   */
  start(): void {
    this.status.status = 'running';
    this.status.lastActivity = new Date().toISOString();
  }
  
  /**
   * Process an event
   */
  private processEvent(event: FocusEvent | UpdateEvent): void {
    // Add to history
    this.eventHistory.push(event);
    
    // Trim history if too long
    if (this.eventHistory.length > this.config.maxEventHistory) {
      this.eventHistory = this.eventHistory.slice(-this.config.maxEventHistory);
    }
    
    // Update status
    this.status.eventsProcessed++;
    this.status.lastActivity = new Date().toISOString();
    
    // Log event if enabled
    if (this.config.enableEventLogging) {
      console.log(`EventBus: ${event.type}`, event);
    }
  }
  
  /**
   * Check if an event is a duplicate
   */
  private isDuplicateEvent(event: FocusEvent | UpdateEvent): boolean {
    const key = this.generateEventKey(event);
    const now = Date.now();
    const lastSeen = this.deduplicationCache.get(key);
    
    if (lastSeen && (now - lastSeen) < this.config.deduplicationWindow) {
      return true;
    }
    
    this.deduplicationCache.set(key, now);
    return false;
  }
  
  /**
   * Generate a key for event deduplication
   */
  private generateEventKey(event: FocusEvent | UpdateEvent): string {
    if ('type' in event && 'nodeId' in event) {
      return `${event.type}:${event.nodeId}`;
    }
    if ('type' in event && 'specId' in event) {
      return `${event.type}:${event.specId}`;
    }
    return event.type;
  }
  
  /**
   * Update listener count
   */
  private updateListenerCount(): void {
    this.status.activeListeners = this.listenerCount('focus') + this.listenerCount('update');
  }
  
  /**
   * Setup default event handlers
   */
  private setupEventHandlers(): void {
    // Handle focus events
    this.on('focus', (event: FocusEvent) => {
      this.handleFocusEvent(event);
    });
    
    // Handle update events
    this.on('update', (event: UpdateEvent) => {
      this.handleUpdateEvent(event);
    });
    
    // Handle errors
    this.on('error', (error: Error) => {
      this.status.status = 'error';
      this.status.error = error.message;
      console.error('EventBus error:', error);
    });
  }
  
  /**
   * Handle focus events
   */
  private handleFocusEvent(event: FocusEvent): void {
    // Emit specific focus events for different panes
    switch (event.type) {
      case 'FOCUS_NODE':
        this.emit('focus:node', event);
        break;
      case 'FOCUS_SPEC':
        this.emit('focus:spec', event);
        break;
      case 'FOCUS_TIMELINE':
        this.emit('focus:timeline', event);
        break;
      case 'FOCUS_CODE':
        this.emit('focus:code', event);
        break;
      case 'HOVER_NODE':
        this.emit('hover:node', event);
        break;
      case 'HOVER_SPEC':
        this.emit('hover:spec', event);
        break;
      case 'HOVER_TIMELINE':
        this.emit('hover:timeline', event);
        break;
      case 'HOVER_CODE':
        this.emit('hover:code', event);
        break;
    }
  }
  
  /**
   * Handle update events
   */
  private handleUpdateEvent(event: UpdateEvent): void {
    // Emit specific update events for different engines
    switch (event.type) {
      case 'NODE_ADDED':
      case 'NODE_UPDATED':
      case 'NODE_REMOVED':
      case 'NODE_STATUS_CHANGED':
        this.emit('update:graph', event);
        break;
      case 'SPEC_ADDED':
      case 'SPEC_UPDATED':
      case 'SPEC_REMOVED':
      case 'SPEC_STATUS_CHANGED':
        this.emit('update:spec', event);
        break;
      case 'TIMELINE_EVENT_ADDED':
      case 'TIMELINE_SPAN_ADDED':
        this.emit('update:timeline', event);
        break;
      case 'DRIFT_DETECTED':
      case 'VIOLATION_DETECTED':
        this.emit('update:drift', event);
        break;
    }
  }
}

/**
 * Global event bus instance
 */
let globalEventBus: EventBus | null = null;

/**
 * Get or create global event bus instance
 */
export function getGlobalEventBus(): EventBus {
  if (!globalEventBus) {
    globalEventBus = new EventBus();
  }
  return globalEventBus;
}

/**
 * Set global event bus instance
 */
export function setGlobalEventBus(eventBus: EventBus): void {
  globalEventBus = eventBus;
}

/**
 * Utility functions for common event patterns
 */
export class EventBusUtils {
  /**
   * Focus on a node across all panes
   */
  static focusNode(eventBus: EventBus, nodeId: string, sourcePane: FocusEvent['sourcePane'] = 'code'): void {
    eventBus.emitFocusEvent({
      type: 'FOCUS_NODE',
      nodeId,
      sourcePane
    });
  }
  
  /**
   * Focus on a spec across all panes
   */
  static focusSpec(eventBus: EventBus, specId: string, sourcePane: FocusEvent['sourcePane'] = 'spec'): void {
    eventBus.emitFocusEvent({
      type: 'FOCUS_SPEC',
      specId,
      sourcePane
    });
  }
  
  /**
   * Focus on a timeline event across all panes
   */
  static focusTimeline(eventBus: EventBus, eventId: string, sourcePane: FocusEvent['sourcePane'] = 'timeline'): void {
    eventBus.emitFocusEvent({
      type: 'FOCUS_TIMELINE',
      eventId,
      sourcePane
    });
  }
  
  /**
   * Focus on code location across all panes
   */
  static focusCode(
    eventBus: EventBus, 
    filePath: string, 
    startLine: number, 
    endLine: number,
    sourcePane: FocusEvent['sourcePane'] = 'code'
  ): void {
    eventBus.emitFocusEvent({
      type: 'FOCUS_CODE',
      codeLocation: {
        filePath,
        startLine,
        endLine
      },
      sourcePane
    });
  }
  
  /**
   * Notify about node updates
   */
  static notifyNodeUpdate(eventBus: EventBus, nodeId: string, updateType: 'added' | 'updated' | 'removed' | 'status_changed'): void {
    const eventType = `NODE_${updateType.toUpperCase()}` as UpdateEventType;
    eventBus.emitUpdateEvent({
      type: eventType,
      nodeId,
      source: 'graph_engine'
    });
  }
  
  /**
   * Notify about spec updates
   */
  static notifySpecUpdate(eventBus: EventBus, specId: string, updateType: 'added' | 'updated' | 'removed' | 'status_changed'): void {
    const eventType = `SPEC_${updateType.toUpperCase()}` as UpdateEventType;
    eventBus.emitUpdateEvent({
      type: eventType,
      specId,
      source: 'spec_engine'
    });
  }
  
  /**
   * Notify about drift detection
   */
  static notifyDriftDetected(eventBus: EventBus, nodeId: string, driftType: 'drift' | 'violation'): void {
    const eventType = driftType === 'drift' ? 'DRIFT_DETECTED' : 'VIOLATION_DETECTED';
    eventBus.emitUpdateEvent({
      type: eventType,
      nodeId,
      source: 'spec_engine'
    });
  }
}
