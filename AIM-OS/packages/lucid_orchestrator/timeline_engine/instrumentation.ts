/**
 * Lucid Orchestrator - Timeline Instrumentation
 * 
 * This module provides instrumentation for capturing runtime events
 * and building the timeline of system behavior.
 */

import { TimelineEvent, TimelineSpan, TimelineSession, TimelineUtils, TimelineEventType, ThreadType } from './timeline_model';
import { now as highResNow } from '../utils/time';

export interface InstrumentationConfig {
  /** Enable function boundary instrumentation */
  enableFunctionInstrumentation: boolean;
  
  /** Enable async boundary instrumentation */
  enableAsyncInstrumentation: boolean;
  
  /** Enable I/O instrumentation */
  enableIOInstrumentation: boolean;
  
  /** Enable UI instrumentation */
  enableUIInstrumentation: boolean;
  
  /** Enable performance instrumentation */
  enablePerformanceInstrumentation: boolean;
  
  /** Enable security instrumentation */
  enableSecurityInstrumentation: boolean;
  
  /** Sample rate for performance events (0-1) */
  performanceSampleRate: number;
  
  /** Maximum events per session */
  maxEventsPerSession: number;
  
  /** Maximum session duration in milliseconds */
  maxSessionDuration: number;
}

export interface InstrumentationContext {
  /** Current session */
  session: TimelineSession;
  
  /** Active spans */
  activeSpans: Map<string, TimelineSpan>;
  
  /** Event counter */
  eventCounter: number;
  
  /** Last cleanup time */
  lastCleanup: number;
}

export class TimelineInstrumentation {
  private config: InstrumentationConfig;
  private context: InstrumentationContext;
  private originalMethods: Map<string, any> = new Map();
  
  constructor(config: Partial<InstrumentationConfig> = {}) {
    this.config = {
      enableFunctionInstrumentation: true,
      enableAsyncInstrumentation: true,
      enableIOInstrumentation: true,
      enableUIInstrumentation: true,
      enablePerformanceInstrumentation: true,
      enableSecurityInstrumentation: true,
      performanceSampleRate: 1.0,
      maxEventsPerSession: 10000,
      maxSessionDuration: 300000, // 5 minutes
      ...config
    };
    
    this.context = {
      session: TimelineUtils.createSession('default', 'custom'),
      activeSpans: new Map(),
      eventCounter: 0,
      lastCleanup: Date.now()
    };
  }
  
  /**
   * Start a new session
   */
  startSession(name: string, sessionType: TimelineSession['metadata']['sessionType'] = 'custom'): void {
    this.context.session = TimelineUtils.createSession(name, sessionType);
    this.context.activeSpans.clear();
    this.context.eventCounter = 0;
  }
  
  /**
   * End the current session
   */
  endSession(): TimelineSession {
    const session = this.context.session;
    session.endTime = highResNow();
    
    // Complete all active spans
    for (const span of this.context.activeSpans.values()) {
      if (span.status === 'running') {
        span.status = 'cancelled';
      }
    }
    
    return session;
  }
  
  /**
   * Instrument a function
   */
  instrumentFunction<T extends (...args: any[]) => any>(
    nodeId: string,
    symbol: string,
    fn: T,
    options: {
      thread?: ThreadType;
      captureArgs?: boolean;
      captureReturn?: boolean;
      captureErrors?: boolean;
    } = {}
  ): T {
    const {
      thread = 'main',
      captureArgs = false,
      captureReturn = false,
      captureErrors = true
    } = options;
    
    if (!this.config.enableFunctionInstrumentation) {
      return fn;
    }
    
    const instrumented = async (...args: any[]) => {
      const startEvent = TimelineUtils.createEvent(
        nodeId,
        symbol,
        'function_start',
        'start',
        thread,
        {
          functionName: symbol,
          customData: captureArgs ? { args } : {}
        }
      );
      
      const span = TimelineUtils.createSpan(startEvent, nodeId, symbol, thread);
      this.context.activeSpans.set(span.id, span);
      TimelineUtils.addEventToSession(this.context.session, startEvent);
      TimelineUtils.addSpanToSession(this.context.session, span);
      
      try {
        const result = await fn(...args);
        
        const endEvent = TimelineUtils.createEvent(
          nodeId,
          symbol,
          'function_end',
          'end',
          thread,
          {
            functionName: symbol,
            customData: captureReturn ? { result } : {}
          }
        );
        
        const completedSpan = TimelineUtils.completeSpan(span, endEvent);
        this.context.activeSpans.set(span.id, completedSpan);
        TimelineUtils.addEventToSession(this.context.session, endEvent);
        
        return result;
      } catch (error) {
        const errorEvent = TimelineUtils.createEvent(
          nodeId,
          symbol,
          'error_event',
          'throw',
          thread,
          {
            functionName: symbol,
            errorMessage: error instanceof Error ? error.message : String(error),
            errorStack: error instanceof Error ? error.stack : undefined
          }
        );
        
        span.status = 'failed';
        span.metadata.errorCount++;
        this.context.activeSpans.set(span.id, span);
        TimelineUtils.addEventToSession(this.context.session, errorEvent);
        
        if (captureErrors) {
          throw error;
        }
      }
    };
    
    return instrumented as T;
  }
  
  /**
   * Instrument an async operation
   */
  instrumentAsync<T>(
    nodeId: string,
    symbol: string,
    asyncOp: () => Promise<T>,
    options: {
      thread?: ThreadType;
      captureResult?: boolean;
    } = {}
  ): Promise<T> {
    const { thread = 'main', captureResult = false } = options;
    
    if (!this.config.enableAsyncInstrumentation) {
      return asyncOp();
    }
    
    const awaitEvent = TimelineUtils.createEvent(
      nodeId,
      symbol,
      'function_await',
      'await',
      thread,
      { functionName: symbol }
    );
    
    TimelineUtils.addEventToSession(this.context.session, awaitEvent);
    
    return asyncOp().then(
      (result) => {
        const endEvent = TimelineUtils.createEvent(
          nodeId,
          symbol,
          'function_end',
          'end',
          thread,
          {
            functionName: symbol,
            customData: captureResult ? { result } : {}
          }
        );
        
        TimelineUtils.addEventToSession(this.context.session, endEvent);
        return result;
      },
      (error) => {
        const errorEvent = TimelineUtils.createEvent(
          nodeId,
          symbol,
          'error_event',
          'throw',
          thread,
          {
            functionName: symbol,
            errorMessage: error instanceof Error ? error.message : String(error),
            errorStack: error instanceof Error ? error.stack : undefined
          }
        );
        
        TimelineUtils.addEventToSession(this.context.session, errorEvent);
        throw error;
      }
    );
  }
  
  /**
   * Instrument I/O operations
   */
  instrumentIO<T>(
    nodeId: string,
    symbol: string,
    ioOp: () => Promise<T>,
    options: {
      ioType: 'network' | 'database' | 'file' | 'cache';
      thread?: ThreadType;
    } = { ioType: 'network', thread: 'main' }
  ): Promise<T> {
    const { ioType, thread = 'main' } = options;
    
    if (!this.config.enableIOInstrumentation) {
      return ioOp();
    }
    
    const startEvent = TimelineUtils.createEvent(
      nodeId,
      symbol,
      'io_start',
      'io',
      thread,
      {
        functionName: symbol,
        customData: { ioType }
      }
    );
    
    TimelineUtils.addEventToSession(this.context.session, startEvent);
    
    const startTime = highResNow();
    
    return ioOp().then(
      (result) => {
        const endEvent = TimelineUtils.createEvent(
          nodeId,
          symbol,
          'io_end',
          'io',
          thread,
          {
            functionName: symbol,
            performanceData: {
              executionTime: highResNow() - startTime
            },
            customData: { ioType }
          }
        );
        
        TimelineUtils.addEventToSession(this.context.session, endEvent);
        return result;
      },
      (error) => {
        const errorEvent = TimelineUtils.createEvent(
          nodeId,
          symbol,
          'error_event',
          'throw',
          thread,
          {
            functionName: symbol,
            errorMessage: error instanceof Error ? error.message : String(error),
            customData: { ioType }
          }
        );
        
        TimelineUtils.addEventToSession(this.context.session, errorEvent);
        throw error;
      }
    );
  }
  
  /**
   * Instrument UI operations
   */
  instrumentUI(
    nodeId: string,
    symbol: string,
    uiOp: () => void,
    options: {
      uiType: 'render' | 'commit' | 'interaction';
      thread?: ThreadType;
    } = { uiType: 'render', thread: 'main' }
  ): void {
    const { uiType, thread = 'main' } = options;
    
    if (!this.config.enableUIInstrumentation) {
      uiOp();
      return;
    }
    
    const eventType = uiType === 'render' ? 'ui_render' : 'ui_commit';
    
    const event = TimelineUtils.createEvent(
      nodeId,
      symbol,
      eventType,
      'commit',
      thread,
      {
        functionName: symbol,
        customData: { uiType }
      }
    );
    
    TimelineUtils.addEventToSession(this.context.session, event);
    
    try {
      uiOp();
    } catch (error) {
      const errorEvent = TimelineUtils.createEvent(
        nodeId,
        symbol,
        'error_event',
        'throw',
        thread,
        {
          functionName: symbol,
          errorMessage: error instanceof Error ? error.message : String(error),
          customData: { uiType }
        }
      );
      
      TimelineUtils.addEventToSession(this.context.session, errorEvent);
      throw error;
    }
  }
  
  /**
   * Record a performance event
   */
  recordPerformance(
    nodeId: string,
    symbol: string,
    performanceData: {
      executionTime: number;
      memoryUsage?: number;
      cpuUsage?: number;
      networkRequests?: number;
      databaseQueries?: number;
      cacheHits?: number;
      cacheMisses?: number;
    },
    thread: ThreadType = 'main'
  ): void {
    if (!this.config.enablePerformanceInstrumentation) return;
    
    // Apply sampling
    if (Math.random() > this.config.performanceSampleRate) return;
    
    const event = TimelineUtils.createEvent(
      nodeId,
      symbol,
      'performance_event',
      'start',
      thread,
      {
        functionName: symbol,
        performanceData
      }
    );
    
    TimelineUtils.addEventToSession(this.context.session, event);
  }
  
  /**
   * Record a security event
   */
  recordSecurity(
    nodeId: string,
    symbol: string,
    securityFlags: string[],
    details?: Record<string, any>,
    thread: ThreadType = 'main'
  ): void {
    if (!this.config.enableSecurityInstrumentation) return;
    
    const event = TimelineUtils.createEvent(
      nodeId,
      symbol,
      'security_event',
      'start',
      thread,
      {
        functionName: symbol,
        securityFlags,
        customData: details
      }
    );
    
    TimelineUtils.addEventToSession(this.context.session, event);
  }
  
  /**
   * Record a custom event
   */
  recordCustom(
    nodeId: string,
    symbol: string,
    eventType: string,
    data: Record<string, any>,
    thread: ThreadType = 'main'
  ): void {
    const event = TimelineUtils.createEvent(
      nodeId,
      symbol,
      'custom',
      'start',
      thread,
      {
        functionName: symbol,
        customData: { eventType, ...data }
      }
    );
    
    TimelineUtils.addEventToSession(this.context.session, event);
  }
  
  /**
   * Get current session
   */
  getCurrentSession(): TimelineSession {
    return this.context.session;
  }
  
  /**
   * Get events for a node
   */
  getEventsForNode(nodeId: string): TimelineEvent[] {
    return TimelineUtils.getEventsForNode(this.context.session, nodeId);
  }
  
  /**
   * Get performance data for a node
   */
  getPerformanceData(nodeId: string) {
    return TimelineUtils.getPerformanceData(this.context.session, nodeId);
  }
  
  /**
   * Clean up old events to prevent memory bloat
   */
  private cleanup(): void {
    const now = Date.now();
    
    // Only cleanup every 30 seconds
    if (now - this.context.lastCleanup < 30000) return;
    
    this.context.lastCleanup = now;
    
    // Check session duration
    if (now - this.context.session.startTime > this.config.maxSessionDuration) {
      this.endSession();
      this.startSession('auto_restart', 'custom');
      return;
    }
    
    // Check event count
    if (this.context.session.stats.totalEvents > this.config.maxEventsPerSession) {
      // Remove oldest events (simple FIFO for now)
      const events = Array.from(this.context.session.events.values())
        .sort((a, b) => a.timestamp - b.timestamp);
      
      const eventsToRemove = events.slice(0, Math.floor(this.config.maxEventsPerSession * 0.1));
      
      for (const event of eventsToRemove) {
        this.context.session.events.delete(event.id);
      }
      
      this.context.session.stats.totalEvents = this.context.session.events.size;
    }
  }
  
  /**
   * Auto-cleanup on interval
   */
  startAutoCleanup(intervalMs: number = 30000): void {
    setInterval(() => this.cleanup(), intervalMs);
  }
}

/**
 * Global instrumentation instance
 */
let globalInstrumentation: TimelineInstrumentation | null = null;

/**
 * Get or create global instrumentation instance
 */
export function getGlobalInstrumentation(): TimelineInstrumentation {
  if (!globalInstrumentation) {
    globalInstrumentation = new TimelineInstrumentation();
    globalInstrumentation.startAutoCleanup();
  }
  return globalInstrumentation;
}

/**
 * Set global instrumentation instance
 */
export function setGlobalInstrumentation(instrumentation: TimelineInstrumentation): void {
  globalInstrumentation = instrumentation;
}
