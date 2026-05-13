/**
 * Lucid Orchestrator - Timeline Engine Model
 * 
 * This module defines the data structures for the Timeline Engine that
 * captures runtime truth and provides the memory/conscience of the system.
 */

import { now as highResNow } from '../utils/time';

export type TimelineEventType = 
  | 'function_start'
  | 'function_end'
  | 'function_await'
  | 'function_throw'
  | 'io_start'
  | 'io_end'
  | 'ui_commit'
  | 'ui_render'
  | 'security_event'
  | 'performance_event'
  | 'error_event'
  | 'custom';

export type ThreadType = 'main' | 'worker' | 'server' | 'background';

export interface TimelineEvent {
  /** Unique event identifier */
  id: string;
  
  /** Node ID this event relates to */
  nodeId: string;
  
  /** Symbol name (function, component, etc.) */
  symbol: string;
  
  /** Event type */
  type: TimelineEventType;
  
  /** Event phase */
  phase: 'start' | 'end' | 'await' | 'io' | 'commit' | 'throw';
  
  /** High-resolution timestamp */
  timestamp: number;
  
  /** Event duration in milliseconds (for completed events) */
  durationMs?: number;
  
  /** Thread where event occurred */
  thread: ThreadType;
  
  /** Event metadata */
  metadata: {
    functionName?: string;
    errorMessage?: string;
    errorStack?: string;
    performanceData?: PerformanceData;
    sideEffects?: string[];
    securityFlags?: string[];
    customData?: Record<string, any>;
  };
  
  /** Parent event ID (for nested events) */
  parentEventId?: string;
  
  /** Child event IDs */
  childEventIds: string[];
}

export interface PerformanceData {
  /** Execution time in milliseconds */
  executionTime: number;
  
  /** Memory usage in bytes */
  memoryUsage?: number;
  
  /** CPU usage percentage */
  cpuUsage?: number;
  
  /** Network requests made */
  networkRequests?: number;
  
  /** Database queries made */
  databaseQueries?: number;
  
  /** Cache hits/misses */
  cacheHits?: number;
  cacheMisses?: number;
}

export interface TimelineSpan {
  /** Span identifier */
  id: string;
  
  /** Start event */
  startEvent: TimelineEvent;
  
  /** End event (if completed) */
  endEvent?: TimelineEvent;
  
  /** Child spans */
  childSpans: TimelineSpan[];
  
  /** Parent span */
  parentSpanId?: string;
  
  /** Span duration in milliseconds */
  durationMs: number;
  
  /** Span status */
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  
  /** Span metadata */
  metadata: {
    nodeId: string;
    symbol: string;
    thread: ThreadType;
    startTime: number;
    endTime?: number;
    errorCount: number;
    warningCount: number;
  };
}

export interface TimelineSession {
  /** Session identifier */
  id: string;
  
  /** Session name/description */
  name: string;
  
  /** Session start time */
  startTime: number;
  
  /** Session end time */
  endTime?: number;
  
  /** All events in this session */
  events: Map<string, TimelineEvent>;
  
  /** All spans in this session */
  spans: Map<string, TimelineSpan>;
  
  /** Session metadata */
  metadata: {
    sessionType: 'app_boot' | 'user_action' | 'background_job' | 'test_run' | 'custom';
    environment: string;
    version: string;
    userId?: string;
    sessionId?: string;
  };
  
  /** Session statistics */
  stats: {
    totalEvents: number;
    totalSpans: number;
    totalDuration: number;
    errorCount: number;
    warningCount: number;
    performanceIssues: number;
  };
}

export interface TimelineEngine {
  /** All sessions */
  sessions: Map<string, TimelineSession>;
  
  /** Current active session */
  currentSession?: TimelineSession;
  
  /** Engine metadata */
  metadata: {
    totalSessions: number;
    totalEvents: number;
    totalSpans: number;
    lastActivity: string;
    version: string;
  };
}

/**
 * Utility functions for working with timeline data
 */
export class TimelineUtils {
  /**
   * Create a new timeline event
   */
  static createEvent(
    nodeId: string,
    symbol: string,
    type: TimelineEventType,
    phase: TimelineEvent['phase'],
    thread: ThreadType = 'main',
    metadata: TimelineEvent['metadata'] = {}
  ): TimelineEvent {
    return {
      id: `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      nodeId,
      symbol,
      type,
      phase,
    timestamp: highResNow(),
      thread,
      metadata,
      childEventIds: []
    };
  }
  
  /**
   * Create a new timeline span
   */
  static createSpan(
    startEvent: TimelineEvent,
    nodeId: string,
    symbol: string,
    thread: ThreadType = 'main'
  ): TimelineSpan {
    return {
      id: `span_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      startEvent,
      durationMs: 0,
      status: 'running',
      childSpans: [],
      metadata: {
        nodeId,
        symbol,
        thread,
        startTime: startEvent.timestamp,
        errorCount: 0,
        warningCount: 0
      }
    };
  }
  
  /**
   * Complete a timeline span
   */
  static completeSpan(span: TimelineSpan, endEvent: TimelineEvent): TimelineSpan {
    const completed = { ...span };
    completed.endEvent = endEvent;
    completed.durationMs = endEvent.timestamp - span.startEvent.timestamp;
    completed.status = 'completed';
    completed.metadata.endTime = endEvent.timestamp;
    
    return completed;
  }
  
  /**
   * Create a new timeline session
   */
  static createSession(
    name: string,
    sessionType: TimelineSession['metadata']['sessionType'],
    environment: string = 'development'
  ): TimelineSession {
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    return {
      id: sessionId,
      name,
    startTime: highResNow(),
      events: new Map(),
      spans: new Map(),
      metadata: {
        sessionType,
        environment,
        version: '1.0.0'
      },
      stats: {
        totalEvents: 0,
        totalSpans: 0,
        totalDuration: 0,
        errorCount: 0,
        warningCount: 0,
        performanceIssues: 0
      }
    };
  }
  
  /**
   * Add an event to a session
   */
  static addEventToSession(session: TimelineSession, event: TimelineEvent): void {
    session.events.set(event.id, event);
    session.stats.totalEvents++;
    
    // Update error/warning counts
    if (event.type === 'error_event') {
      session.stats.errorCount++;
    } else if (event.metadata.securityFlags?.includes('warning')) {
      session.stats.warningCount++;
    }
  }
  
  /**
   * Add a span to a session
   */
  static addSpanToSession(session: TimelineSession, span: TimelineSpan): void {
    session.spans.set(span.id, span);
    session.stats.totalSpans++;
    
    // Update duration
    if (span.status === 'completed') {
      session.stats.totalDuration += span.durationMs;
    }
  }
  
  /**
   * Get events for a specific node
   */
  static getEventsForNode(session: TimelineSession, nodeId: string): TimelineEvent[] {
    return Array.from(session.events.values())
      .filter(event => event.nodeId === nodeId);
  }
  
  /**
   * Get spans for a specific node
   */
  static getSpansForNode(session: TimelineSession, nodeId: string): TimelineSpan[] {
    return Array.from(session.spans.values())
      .filter(span => span.metadata.nodeId === nodeId);
  }
  
  /**
   * Get performance data for a node
   */
  static getPerformanceData(session: TimelineSession, nodeId: string): PerformanceData | null {
    const events = this.getEventsForNode(session, nodeId);
    const performanceEvents = events.filter(e => e.type === 'performance_event' && e.metadata.performanceData);
    
    if (performanceEvents.length === 0) return null;
    
    const performanceData = performanceEvents.map(e => e.metadata.performanceData!);
    
    return {
      executionTime: performanceData.reduce((sum, p) => sum + p.executionTime, 0) / performanceData.length,
      memoryUsage: performanceData.reduce((sum, p) => sum + (p.memoryUsage || 0), 0) / performanceData.length,
      cpuUsage: performanceData.reduce((sum, p) => sum + (p.cpuUsage || 0), 0) / performanceData.length,
      networkRequests: performanceData.reduce((sum, p) => sum + (p.networkRequests || 0), 0),
      databaseQueries: performanceData.reduce((sum, p) => sum + (p.databaseQueries || 0), 0),
      cacheHits: performanceData.reduce((sum, p) => sum + (p.cacheHits || 0), 0),
      cacheMisses: performanceData.reduce((sum, p) => sum + (p.cacheMisses || 0), 0)
    };
  }
  
  /**
   * Get error events for a node
   */
  static getErrorEvents(session: TimelineSession, nodeId: string): TimelineEvent[] {
    return this.getEventsForNode(session, nodeId)
      .filter(event => event.type === 'error_event');
  }
  
  /**
   * Get security events for a node
   */
  static getSecurityEvents(session: TimelineSession, nodeId: string): TimelineEvent[] {
    return this.getEventsForNode(session, nodeId)
      .filter(event => event.type === 'security_event');
  }
  
  /**
   * Calculate session health score
   */
  static calculateSessionHealth(session: TimelineSession): number {
    const { stats } = session;
    
    if (stats.totalEvents === 0) return 100;
    
    let healthScore = 100;
    
    // Deduct for errors
    healthScore -= (stats.errorCount / stats.totalEvents) * 50;
    
    // Deduct for warnings
    healthScore -= (stats.warningCount / stats.totalEvents) * 25;
    
    // Deduct for performance issues
    healthScore -= (stats.performanceIssues / stats.totalEvents) * 25;
    
    return Math.max(0, Math.round(healthScore));
  }
  
  /**
   * Export session to JSON
   */
  static exportSession(session: TimelineSession): string {
    return JSON.stringify({
      id: session.id,
      name: session.name,
      startTime: session.startTime,
      endTime: session.endTime,
      events: Array.from(session.events.entries()),
      spans: Array.from(session.spans.entries()),
      metadata: session.metadata,
      stats: session.stats
    }, null, 2);
  }
  
  /**
   * Import session from JSON
   */
  static importSession(json: string): TimelineSession {
    const data = JSON.parse(json);
    
    return {
      id: data.id,
      name: data.name,
      startTime: data.startTime,
      endTime: data.endTime,
      events: new Map(data.events),
      spans: new Map(data.spans),
      metadata: data.metadata,
      stats: data.stats
    };
  }
}
