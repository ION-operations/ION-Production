/**
 * Lucid Orchestrator - Main Service
 * 
 * This module orchestrates all four engines (Graph, Spec, Timeline, Event Bus)
 * to provide the complete four-pane consciousness interface.
 */

import { IRGraph, IRGraphBuilder, IRNode, NodeStatus } from './graph_engine/ir_model';
import { TypeScriptExtractor } from './graph_engine/typescript_extractor';
import { SpecEngineService, SpecEngineConfig } from './spec_engine/spec_engine';
import { SpecBlock, SpecStatus } from './spec_engine/spec_model';
import { TimelineInstrumentation, InstrumentationConfig } from './timeline_engine/instrumentation';
import { TimelineEvent, TimelineEventType, TimelineSession, ThreadType, TimelineUtils } from './timeline_engine/timeline_model';
import { EventBus, EventBusConfig, FocusEvent, UpdateEvent, getGlobalEventBus } from './event_bus/event_bus';
import { now as highResNow } from './utils/time';

export interface LucidOrchestratorConfig {
  /** Graph engine configuration */
  graph: {
    enableAutoExtraction: boolean;
    extractionInterval: number;
    includeTests: boolean;
    includeDependencies: boolean;
  };
  
  /** Spec engine configuration */
  spec: SpecEngineConfig;
  
  /** Timeline engine configuration */
  timeline: InstrumentationConfig;
  
  /** Event bus configuration */
  eventBus: EventBusConfig;
  
  /** General configuration */
  general: {
    enableLogging: boolean;
    enableMetrics: boolean;
    enableHealthMonitoring: boolean;
  };
}

export interface LucidOrchestratorStatus {
  /** Overall status */
  status: 'initializing' | 'running' | 'stopped' | 'error';
  
  /** Individual engine statuses */
  engines: {
    graph: 'running' | 'stopped' | 'error';
    spec: 'running' | 'stopped' | 'error';
    timeline: 'running' | 'stopped' | 'error';
    eventBus: 'running' | 'stopped' | 'error';
  };
  
  /** Health metrics */
  health: {
    overall: number;
    graph: number;
    spec: number;
    timeline: number;
    eventBus: number;
  };
  
  /** Statistics */
  stats: {
    totalNodes: number;
    totalSpecs: number;
    totalEvents: number;
    totalSessions: number;
    uptime: number;
  };
  
  /** Last activity */
  lastActivity: string;
  
  /** Error message if status is error */
  error?: string;
}

export interface BlueprintNodeSummary {
  id: string;
  name: string;
  kind: IRNode['kind'];
  status: NodeStatus;
  filePath: string;
  range: IRNode['range'];
  tags: string[];
  inputs: number;
  outputs: number;
  sideEffects: string[];
  metrics: {
    complexity: number;
    estimatedComplexity: number;
    hasSideEffects: boolean;
    isAsync: boolean;
  };
  security?: IRNode['security'];
  linkedSpecIds: string[];
}

export interface SpecSummary {
  id: string;
  symbol: string;
  status: SpecStatus;
  responsibility: string;
  mustNever: string[];
  securityLevel: SpecBlock['security_level'];
  perfBudgetMs?: number;
  riskLevel: SpecBlock['risk_level'];
  driftReason?: string;
  linkedNodeIds: string[];
  metadata: SpecBlock['metadata'];
}

export type TimelineEventSeverity = 'info' | 'warning' | 'error';

export interface TimelineEventSummary {
  id: string;
  nodeId: string;
  symbol: string;
  type: TimelineEventType;
  phase: TimelineEvent['phase'];
  thread: ThreadType;
  timestamp: string;
  durationMs?: number;
  severity: TimelineEventSeverity;
  metadata: TimelineEvent['metadata'];
}

export interface TimelineSnapshot {
  sessionId: string;
  sessionType: TimelineSession['metadata']['sessionType'];
  health: number;
  stats: TimelineSession['stats'];
  recentEvents: TimelineEventSummary[];
}

export interface ConsciousnessSnapshot {
  status: LucidOrchestratorStatus['status'];
  health: LucidOrchestratorStatus['health'];
  stats: LucidOrchestratorStatus['stats'];
  nodes: BlueprintNodeSummary[];
  specs: SpecSummary[];
  timeline: TimelineSnapshot;
  focusHistory: FocusEvent[];
  updateHistory: UpdateEvent[];
  lastActivity: string;
}

export class LucidOrchestrator {
  private config: LucidOrchestratorConfig;
  private status: LucidOrchestratorStatus;
  private startTime: number;
  private projectRoot: string = '.';
  
  // Engines
  private graphBuilder: IRGraphBuilder;
  private extractor: TypeScriptExtractor;
  private specEngine: SpecEngineService;
  private timelineInstrumentation: TimelineInstrumentation;
  private eventBus: EventBus;
  
  // State
  private currentIRGraph: IRGraph | null = null;
  private isInitialized = false;
  private focusHistory: FocusEvent[] = [];
  private updateHistory: UpdateEvent[] = [];
  
  constructor(config: Partial<LucidOrchestratorConfig> = {}) {
    this.config = {
      graph: {
        enableAutoExtraction: true,
        extractionInterval: 30000, // 30 seconds
        includeTests: false,
        includeDependencies: false
      },
      spec: {
        enableDriftDetection: true,
        driftDetectionInterval: 30000,
        enableAutoGeneration: true,
        securityThreshold: 'medium'
      },
      timeline: {
        enableFunctionInstrumentation: true,
        enableAsyncInstrumentation: true,
        enableIOInstrumentation: true,
        enableUIInstrumentation: true,
        enablePerformanceInstrumentation: true,
        enableSecurityInstrumentation: true,
        performanceSampleRate: 1.0,
        maxEventsPerSession: 10000,
        maxSessionDuration: 300000
      },
      eventBus: {
        enableFocusSync: true,
        enableUpdateBroadcasting: true,
        enableEventLogging: true,
        maxEventHistory: 1000,
        deduplicationWindow: 100
      },
      general: {
        enableLogging: true,
        enableMetrics: true,
        enableHealthMonitoring: true
      },
      ...config
    };
    
    this.startTime = Date.now();
    this.status = {
      status: 'initializing',
      engines: {
        graph: 'stopped',
        spec: 'stopped',
        timeline: 'stopped',
        eventBus: 'stopped'
      },
      health: {
        overall: 0,
        graph: 0,
        spec: 0,
        timeline: 0,
        eventBus: 0
      },
      stats: {
        totalNodes: 0,
        totalSpecs: 0,
        totalEvents: 0,
        totalSessions: 0,
        uptime: 0
      },
      lastActivity: new Date().toISOString()
    };
    
    // Initialize engines
    this.graphBuilder = new IRGraphBuilder();
    this.extractor = new TypeScriptExtractor({
      includeTests: this.config.graph.includeTests,
      includeNodeModules: this.config.graph.includeDependencies
    });
    this.specEngine = new SpecEngineService(this.config.spec);
    this.timelineInstrumentation = new TimelineInstrumentation(this.config.timeline);
    this.eventBus = getGlobalEventBus();
    
    this.setupEventHandlers();
  }
  
  /**
   * Initialize the Lucid Orchestrator
   */
  async initialize(projectPath: string = '.'): Promise<void> {
    try {
      this.status.status = 'initializing';
      this.projectRoot = projectPath;
      
      // Initialize extractor with project path
      this.extractor = new TypeScriptExtractor({
        includeTests: this.config.graph.includeTests,
        includeNodeModules: this.config.graph.includeDependencies
      });
      
      // Start engines
      await this.startEngines();
      
      // Perform initial extraction
      if (this.config.graph.enableAutoExtraction) {
        await this.extractIRGraph();
      }
      
      this.isInitialized = true;
      this.status.status = 'running';
      this.status.lastActivity = new Date().toISOString();
      
      if (this.config.general.enableLogging) {
        console.log('Lucid Orchestrator initialized successfully');
      }
      
    } catch (error) {
      this.status.status = 'error';
      this.status.error = error instanceof Error ? error.message : 'Unknown error';
      throw error;
    }
  }
  
  /**
   * Start all engines
   */
  private async startEngines(): Promise<void> {
    try {
      // Start spec engine
      await this.specEngine.start();
      this.status.engines.spec = 'running';
      
      // Start timeline instrumentation
      this.timelineInstrumentation.startSession('lucid_orchestrator', 'custom');
      this.status.engines.timeline = 'running';
      
      // Start event bus
      this.eventBus.start();
      this.status.engines.eventBus = 'running';
      
      // Graph engine is started when extraction runs
      this.status.engines.graph = 'running';
      
    } catch (error) {
      this.status.status = 'error';
      this.status.error = error instanceof Error ? error.message : 'Unknown error';
      throw error;
    }
  }
  
  /**
   * Extract IR graph from codebase
   */
  async extractIRGraph(): Promise<IRGraph> {
    try {
      const result = await this.extractor.extractIRGraphFromProject(this.projectRoot);
      this.graphBuilder = result;
      
      // Return the built graph
      const graph = result.getGraph();
      this.currentIRGraph = graph;
      
      // Generate specs from IR nodes
      if (this.config.spec.enableAutoGeneration) {
        const generatedSpecs = this.specEngine.generateSpecsFromIR(graph);
        if (this.config.general.enableLogging) {
          console.log(`Generated ${generatedSpecs.length} spec blocks from IR nodes`);
        }
      }
      
      // Update status
      this.status.stats.totalNodes = graph.nodes.size;
      this.status.lastActivity = new Date().toISOString();
      
      // Emit update event
      this.eventBus.emitUpdateEvent({
        type: 'NODE_ADDED',
        source: 'graph_engine',
        data: { nodeCount: this.currentIRGraph?.nodes.size || 0 }
      });
      
      return graph;
      
    } catch (error) {
      this.status.engines.graph = 'error';
      throw error;
    }
  }
  
  /**
   * Run drift detection
   */
  async runDriftDetection(): Promise<void> {
    if (!this.currentIRGraph) {
      throw new Error('No IR graph available for drift detection');
    }
    
    try {
      const result = await this.specEngine.runDriftDetection(this.currentIRGraph);
      
      // Update status
      this.status.stats.totalSpecs = result.summary.totalSpecs;
      this.status.lastActivity = new Date().toISOString();
      
      // Emit update events for drifted/violated specs
      for (const spec of result.driftedSpecs) {
        this.eventBus.emitUpdateEvent({
          type: 'DRIFT_DETECTED',
          nodeId: spec.linked_nodes[0],
          source: 'spec_engine',
          data: { specId: spec.id, reason: spec.drift_reason }
        });
      }
      
      for (const spec of result.violatedSpecs) {
        this.eventBus.emitUpdateEvent({
          type: 'VIOLATION_DETECTED',
          nodeId: spec.linked_nodes[0],
          source: 'spec_engine',
          data: { specId: spec.id, reason: spec.drift_reason }
        });
      }
      
    } catch (error) {
      this.status.engines.spec = 'error';
      throw error;
    }
  }
  
  /**
   * Focus on a node across all panes
   */
  focusNode(nodeId: string, sourcePane: 'code' | 'blueprint' | 'spec' | 'timeline' = 'code'): void {
    this.eventBus.emitFocusEvent({
      type: 'FOCUS_NODE',
      nodeId,
      sourcePane
    });
  }
  
  /**
   * Focus on a spec across all panes
   */
  focusSpec(specId: string, sourcePane: 'code' | 'blueprint' | 'spec' | 'timeline' = 'spec'): void {
    this.eventBus.emitFocusEvent({
      type: 'FOCUS_SPEC',
      specId,
      sourcePane
    });
  }
  
  /**
   * Focus on a timeline event across all panes
   */
  focusTimeline(eventId: string, sourcePane: 'code' | 'blueprint' | 'spec' | 'timeline' = 'timeline'): void {
    this.eventBus.emitFocusEvent({
      type: 'FOCUS_TIMELINE',
      eventId,
      sourcePane
    });
  }
  
  /**
   * Get current status
   */
  getStatus(): LucidOrchestratorStatus {
    // Update uptime
    this.status.stats.uptime = Date.now() - this.startTime;
    
    // Update health scores
    this.updateHealthScores();
    
    return { ...this.status };
  }
  
  /**
   * Get IR graph
   */
  getIRGraph(): IRGraph | null {
    return this.currentIRGraph;
  }
  
  /**
   * Get spec engine
   */
  getSpecEngine(): SpecEngineService {
    return this.specEngine;
  }
  
  /**
   * Get timeline instrumentation
   */
  getTimelineInstrumentation(): TimelineInstrumentation {
    return this.timelineInstrumentation;
  }
  
  /**
   * Get event bus
   */
  getEventBus(): EventBus {
    return this.eventBus;
  }

  getConsciousnessSnapshot(limit: number = 50): ConsciousnessSnapshot {
    const status = this.getStatus();

    const specs = this.specEngine.getAllSpecBlocks();
    const specByNode = new Map<string, SpecBlock[]>();
    for (const spec of specs) {
      for (const nodeId of spec.linked_nodes) {
        if (!specByNode.has(nodeId)) {
          specByNode.set(nodeId, []);
        }
        specByNode.get(nodeId)!.push(spec);
      }
    }

    const nodeSummaries: BlueprintNodeSummary[] = [];
    if (this.currentIRGraph) {
      const nodes = Array.from(this.currentIRGraph.nodes.values());
      const nodePriority = (nodeStatus: NodeStatus) => {
        switch (nodeStatus) {
          case 'violation':
            return 0;
          case 'drift':
            return 1;
          case 'proposed':
            return 2;
          case 'orphan':
            return 3;
          default:
            return 4;
        }
      };

      nodes
        .sort((a, b) => nodePriority(a.status) - nodePriority(b.status))
        .slice(0, limit)
        .forEach((node) => {
          const linkedSpecIds = (specByNode.get(node.id) ?? []).map((spec) => spec.id);
          nodeSummaries.push({
            id: node.id,
            name: node.name,
            kind: node.kind,
            status: node.status,
            filePath: node.filePath,
            range: node.range,
            tags: node.tags,
            inputs: node.inputs.length,
            outputs: node.outputs.length,
            sideEffects: node.sideEffects,
            metrics: {
              complexity: node.metadata?.complexity ?? 0,
              estimatedComplexity: node.performance?.estimatedComplexity ?? 0,
              hasSideEffects: node.performance?.hasSideEffects ?? node.sideEffects.length > 0,
              isAsync: node.performance?.isAsync ?? false,
            },
            security: node.security,
            linkedSpecIds,
          });
        });
    }

    const specPriority = (status: SpecStatus) => {
      switch (status) {
        case 'violation':
          return 0;
        case 'drift':
          return 1;
        case 'proposed':
          return 2;
        case 'orphan':
          return 3;
        default:
          return 4;
      }
    };

    const specSummaries: SpecSummary[] = specs
      .slice()
      .sort((a, b) => specPriority(a.status) - specPriority(b.status))
      .slice(0, limit)
      .map((spec) => ({
        id: spec.id,
        symbol: spec.symbol,
        status: spec.status,
        responsibility: spec.responsibility,
        mustNever: spec.must_never,
        securityLevel: spec.security_level,
        perfBudgetMs: spec.perf_budget_ms,
        riskLevel: spec.risk_level,
        driftReason: spec.drift_reason,
        linkedNodeIds: spec.linked_nodes.slice(),
        metadata: spec.metadata,
      }));

    const session = this.timelineInstrumentation.getCurrentSession();
    const sessionHealth = TimelineUtils.calculateSessionHealth(session);
    const nowPerformance = highResNow();
    const nowEpoch = Date.now();
    const timelineEvents = Array.from(session.events.values())
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, limit)
      .map<TimelineEventSummary>((event) => {
        const delta = nowPerformance - event.timestamp;
        const occurredAt = new Date(nowEpoch - delta).toISOString();
        const severity: TimelineEventSeverity = event.type === 'error_event'
          ? 'error'
          : event.type === 'security_event' || (event.metadata?.securityFlags?.length ?? 0) > 0
            ? 'warning'
            : 'info';
        return {
          id: event.id,
          nodeId: event.nodeId,
          symbol: event.symbol,
          type: event.type,
          phase: event.phase,
          thread: event.thread,
          timestamp: occurredAt,
          durationMs: event.durationMs,
          severity,
          metadata: event.metadata,
        };
      });

    const timelineSnapshot: TimelineSnapshot = {
      sessionId: session.id,
      sessionType: session.metadata.sessionType,
      health: sessionHealth,
      stats: session.stats,
      recentEvents: timelineEvents,
    };

    return {
      status: status.status,
      health: status.health,
      stats: status.stats,
      nodes: nodeSummaries,
      specs: specSummaries,
      timeline: timelineSnapshot,
      focusHistory: this.focusHistory.slice(0, 25),
      updateHistory: this.updateHistory.slice(0, 50),
      lastActivity: status.lastActivity,
    };
  }
  
  /**
   * Stop the orchestrator
   */
  async stop(): Promise<void> {
    try {
      // Stop engines
      await this.specEngine.stop();
      this.timelineInstrumentation.endSession();
      this.eventBus.stop();
      
      this.status.status = 'stopped';
      this.status.engines = {
        graph: 'stopped',
        spec: 'stopped',
        timeline: 'stopped',
        eventBus: 'stopped'
      };
      
      if (this.config.general.enableLogging) {
        console.log('Lucid Orchestrator stopped');
      }
      
    } catch (error) {
      this.status.status = 'error';
      this.status.error = error instanceof Error ? error.message : 'Unknown error';
      throw error;
    }
  }
  
  /**
   * Setup event handlers
   */
  private setupEventHandlers(): void {
    // Handle focus events
    this.eventBus.onFocus((event) => {
      if (this.config.general.enableLogging) {
        console.log('Focus event:', event);
      }
      this.focusHistory.unshift(event);
      if (this.focusHistory.length > 50) {
        this.focusHistory.pop();
      }
    });
    
    // Handle update events
    this.eventBus.onUpdate((event) => {
      if (this.config.general.enableLogging) {
        console.log('Update event:', event);
      }
      this.updateHistory.unshift(event);
      if (this.updateHistory.length > 100) {
        this.updateHistory.pop();
      }
    });
  }
  
  /**
   * Update health scores
   */
  private updateHealthScores(): void {
    // Graph health (based on node count and extraction success)
    this.status.health.graph = this.currentIRGraph ? 100 : 0;
    
    // Spec health (from spec engine)
    const specHealth = this.specEngine.getHealthMetrics();
    this.status.health.spec = specHealth.specEngine.healthScore;
    
    // Timeline health (based on session health)
    const timelineHealth = this.timelineInstrumentation.getCurrentSession();
    this.status.health.timeline = 100; // Placeholder - would calculate from session health
    
    // Event bus health (based on status)
    this.status.health.eventBus = this.eventBus.getStatus().status === 'running' ? 100 : 0;
    
    // Overall health (average of all engines)
    const engineHealths = [
      this.status.health.graph,
      this.status.health.spec,
      this.status.health.timeline,
      this.status.health.eventBus
    ];
    this.status.health.overall = engineHealths.reduce((sum, health) => sum + health, 0) / engineHealths.length;
  }
}

/**
 * Factory function to create a Lucid Orchestrator instance
 */
export function createLucidOrchestrator(config?: Partial<LucidOrchestratorConfig>): LucidOrchestrator {
  return new LucidOrchestrator(config);
}

/**
 * Global Lucid Orchestrator instance
 */
let globalOrchestrator: LucidOrchestrator | null = null;

/**
 * Get or create global Lucid Orchestrator instance
 */
export function getGlobalOrchestrator(): LucidOrchestrator {
  if (!globalOrchestrator) {
    globalOrchestrator = createLucidOrchestrator();
  }
  return globalOrchestrator;
}

/**
 * Set global Lucid Orchestrator instance
 */
export function setGlobalOrchestrator(orchestrator: LucidOrchestrator): void {
  globalOrchestrator = orchestrator;
}
