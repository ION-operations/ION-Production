/**
 * Analytics Service
 * 
 * Provides advanced analytics and insights for the Lucid Orchestrator system.
 */

import { EventEmitter } from 'events';
import { LucidOrchestratorData, Event, CodeMetrics, QualityMetrics } from '../../../lucid_orchestrator/data_models/core_interfaces';

export interface AnalyticsInsight {
  id: string;
  type: 'performance' | 'quality' | 'trend' | 'anomaly' | 'recommendation';
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  data: any;
  timestamp: Date;
  actionable: boolean;
  action?: {
    type: string;
    description: string;
    url?: string;
  };
}

export interface TrendAnalysis {
  metric: string;
  direction: 'up' | 'down' | 'stable';
  change: number;
  significance: 'low' | 'medium' | 'high';
  period: string;
  data: Array<{ date: string; value: number }>;
}

export interface PerformanceAnalysis {
  overallScore: number;
  bottlenecks: Array<{
    component: string;
    impact: number;
    description: string;
  }>;
  recommendations: Array<{
    priority: 'low' | 'medium' | 'high';
    effort: 'low' | 'medium' | 'high';
    description: string;
    impact: number;
  }>;
}

export interface QualityAnalysis {
  overallQuality: number;
  qualityTrends: TrendAnalysis[];
  qualityGaps: Array<{
    area: string;
    currentScore: number;
    targetScore: number;
    gap: number;
  }>;
  improvementSuggestions: Array<{
    area: string;
    suggestion: string;
    impact: number;
    effort: 'low' | 'medium' | 'high';
  }>;
}

export class AnalyticsService extends EventEmitter {
  private insights: Map<string, AnalyticsInsight> = new Map();
  private historicalData: Map<string, any[]> = new Map();
  private analysisCache: Map<string, any> = new Map();
  private updateInterval: NodeJS.Timeout | null = null;

  constructor() {
    super();
    this.startAnalysisLoop();
  }

  /**
   * Analyze system data and generate insights
   */
  async analyzeSystem(data: LucidOrchestratorData): Promise<AnalyticsInsight[]> {
    const insights: AnalyticsInsight[] = [];

    // Analyze code metrics
    const codeInsights = await this.analyzeCodeMetrics(data.code);
    insights.push(...codeInsights);

    // Analyze blueprint architecture
    const blueprintInsights = await this.analyzeBlueprint(data.blueprint);
    insights.push(...blueprintInsights);

    // Analyze specifications
    const specInsights = await this.analyzeSpecifications(data.spec);
    insights.push(...specInsights);

    // Analyze timeline events
    const timelineInsights = await this.analyzeTimeline(data.timeline);
    insights.push(...timelineInsights);

    // Analyze cross-pane relationships
    const crossPaneInsights = await this.analyzeCrossPaneRelationships(data);
    insights.push(...crossPaneInsights);

    // Store insights
    insights.forEach(insight => {
      this.insights.set(insight.id, insight);
    });

    // Emit insights
    this.emit('insights_updated', insights);

    return insights;
  }

  /**
   * Analyze code metrics
   */
  private async analyzeCodeMetrics(codeData: any): Promise<AnalyticsInsight[]> {
    const insights: AnalyticsInsight[] = [];
    const metrics = codeData.metrics;

    // Check test coverage
    if (metrics.testCoverage < 0.8) {
      insights.push({
        id: `test_coverage_${Date.now()}`,
        type: 'quality',
        title: 'Low Test Coverage',
        description: `Test coverage is ${(metrics.testCoverage * 100).toFixed(1)}%, below the recommended 80%`,
        severity: metrics.testCoverage < 0.5 ? 'high' : 'medium',
        confidence: 0.9,
        data: { coverage: metrics.testCoverage, threshold: 0.8 },
        timestamp: new Date(),
        actionable: true,
        action: {
          type: 'improve_test_coverage',
          description: 'Add more unit tests to improve coverage',
          url: '/code/tests'
        }
      });
    }

    // Check code complexity
    if (metrics.complexity > 5) {
      insights.push({
        id: `complexity_${Date.now()}`,
        type: 'performance',
        title: 'High Code Complexity',
        description: `Average complexity is ${metrics.complexity.toFixed(2)}, which may impact maintainability`,
        severity: metrics.complexity > 8 ? 'high' : 'medium',
        confidence: 0.8,
        data: { complexity: metrics.complexity, threshold: 5 },
        timestamp: new Date(),
        actionable: true,
        action: {
          type: 'refactor_complex_code',
          description: 'Refactor complex functions to improve maintainability',
          url: '/code/refactor'
        }
      });
    }

    // Check documentation coverage
    if (metrics.documentationCoverage < 0.6) {
      insights.push({
        id: `doc_coverage_${Date.now()}`,
        type: 'quality',
        title: 'Low Documentation Coverage',
        description: `Documentation coverage is ${(metrics.documentationCoverage * 100).toFixed(1)}%, below the recommended 60%`,
        severity: 'medium',
        confidence: 0.9,
        data: { coverage: metrics.documentationCoverage, threshold: 0.6 },
        timestamp: new Date(),
        actionable: true,
        action: {
          type: 'improve_documentation',
          description: 'Add more documentation to improve coverage',
          url: '/docs'
        }
      });
    }

    return insights;
  }

  /**
   * Analyze blueprint architecture
   */
  private async analyzeBlueprint(blueprintData: any): Promise<AnalyticsInsight[]> {
    const insights: AnalyticsInsight[] = [];
    const { architecture } = blueprintData;

    // Check for isolated nodes
    const isolatedNodes = architecture.nodes.filter((node: any) => {
      const hasIncoming = architecture.edges.some((edge: any) => edge.to === node.id);
      const hasOutgoing = architecture.edges.some((edge: any) => edge.from === node.id);
      return !hasIncoming && !hasOutgoing;
    });

    if (isolatedNodes.length > 0) {
      insights.push({
        id: `isolated_nodes_${Date.now()}`,
        type: 'anomaly',
        title: 'Isolated Architecture Nodes',
        description: `${isolatedNodes.length} nodes are not connected to the rest of the architecture`,
        severity: 'medium',
        confidence: 0.9,
        data: { isolatedNodes: isolatedNodes.length, nodes: isolatedNodes },
        timestamp: new Date(),
        actionable: true,
        action: {
          type: 'connect_isolated_nodes',
          description: 'Review and connect isolated nodes to the architecture',
          url: '/blueprint/architecture'
        }
      });
    }

    // Check for high coupling
    const nodeConnections = new Map();
    architecture.edges.forEach((edge: any) => {
      nodeConnections.set(edge.from, (nodeConnections.get(edge.from) || 0) + 1);
      nodeConnections.set(edge.to, (nodeConnections.get(edge.to) || 0) + 1);
    });

    const highCouplingNodes = Array.from(nodeConnections.entries())
      .filter(([_, count]) => count > 10)
      .map(([nodeId, count]) => ({ nodeId, count }));

    if (highCouplingNodes.length > 0) {
      insights.push({
        id: `high_coupling_${Date.now()}`,
        type: 'performance',
        title: 'High Coupling Detected',
        description: `${highCouplingNodes.length} nodes have high coupling (>10 connections)`,
        severity: 'medium',
        confidence: 0.8,
        data: { highCouplingNodes },
        timestamp: new Date(),
        actionable: true,
        action: {
          type: 'reduce_coupling',
          description: 'Consider breaking down highly coupled components',
          url: '/blueprint/refactor'
        }
      });
    }

    return insights;
  }

  /**
   * Analyze specifications
   */
  private async analyzeSpecifications(specData: any): Promise<AnalyticsInsight[]> {
    const insights: AnalyticsInsight[] = [];
    const { compliance, quality } = specData;

    // Check compliance score
    if (compliance.overallScore < 0.8) {
      insights.push({
        id: `low_compliance_${Date.now()}`,
        type: 'quality',
        title: 'Low Compliance Score',
        description: `Compliance score is ${(compliance.overallScore * 100).toFixed(1)}%, below the recommended 80%`,
        severity: compliance.overallScore < 0.6 ? 'high' : 'medium',
        confidence: 0.9,
        data: { score: compliance.overallScore, threshold: 0.8 },
        timestamp: new Date(),
        actionable: true,
        action: {
          type: 'improve_compliance',
          description: 'Address violations and warnings to improve compliance',
          url: '/spec/compliance'
        }
      });
    }

    // Check for critical violations
    const criticalViolations = compliance.violations.filter((v: any) => v.severity === 'error');
    if (criticalViolations.length > 0) {
      insights.push({
        id: `critical_violations_${Date.now()}`,
        type: 'quality',
        title: 'Critical Violations Found',
        description: `${criticalViolations.length} critical violations need immediate attention`,
        severity: 'critical',
        confidence: 1.0,
        data: { violations: criticalViolations },
        timestamp: new Date(),
        actionable: true,
        action: {
          type: 'fix_violations',
          description: 'Fix critical violations immediately',
          url: '/spec/violations'
        }
      });
    }

    return insights;
  }

  /**
   * Analyze timeline events
   */
  private async analyzeTimeline(timelineData: any): Promise<AnalyticsInsight[]> {
    const insights: AnalyticsInsight[] = [];
    const { events, analytics } = timelineData;

    // Check for activity trends
    const recentActivity = analytics.activity.slice(-7);
    const avgActivity = recentActivity.reduce((sum: number, day: any) => sum + day.totalActivity, 0) / recentActivity.length;
    const currentActivity = recentActivity[recentActivity.length - 1]?.totalActivity || 0;

    if (currentActivity < avgActivity * 0.5) {
      insights.push({
        id: `low_activity_${Date.now()}`,
        type: 'trend',
        title: 'Low Recent Activity',
        description: `Recent activity is ${((currentActivity / avgActivity) * 100).toFixed(1)}% of the average`,
        severity: 'low',
        confidence: 0.7,
        data: { current: currentActivity, average: avgActivity },
        timestamp: new Date(),
        actionable: false
      });
    }

    // Check for quality trends
    const recentQuality = analytics.quality.slice(-7);
    const qualityTrend = this.calculateTrend(recentQuality.map((q: any) => q.overallQuality));

    if (qualityTrend.direction === 'down' && qualityTrend.significance === 'high') {
      insights.push({
        id: `quality_decline_${Date.now()}`,
        type: 'trend',
        title: 'Quality Declining',
        description: `Quality has been declining significantly over the past week`,
        severity: 'medium',
        confidence: 0.8,
        data: { trend: qualityTrend },
        timestamp: new Date(),
        actionable: true,
        action: {
          type: 'investigate_quality',
          description: 'Investigate causes of quality decline',
          url: '/timeline/quality'
        }
      });
    }

    return insights;
  }

  /**
   * Analyze cross-pane relationships
   */
  private async analyzeCrossPaneRelationships(data: LucidOrchestratorData): Promise<AnalyticsInsight[]> {
    const insights: AnalyticsInsight[] = [];

    // Check for documentation-code alignment
    const docFiles = data.code.files.documentation.length;
    const sourceFiles = data.code.files.source.length;
    const docRatio = docFiles / sourceFiles;

    if (docRatio < 0.5) {
      insights.push({
        id: `doc_code_alignment_${Date.now()}`,
        type: 'quality',
        title: 'Documentation-Code Alignment Issue',
        description: `Documentation ratio is ${(docRatio * 100).toFixed(1)}%, below the recommended 50%`,
        severity: 'medium',
        confidence: 0.8,
        data: { docFiles, sourceFiles, ratio: docRatio },
        timestamp: new Date(),
        actionable: true,
        action: {
          type: 'improve_doc_alignment',
          description: 'Add more documentation to match code complexity',
          url: '/docs/alignment'
        }
      });
    }

    // Check for spec-code alignment
    const specCount = data.spec.specs.requirements.length + data.spec.specs.constraints.length;
    const specRatio = specCount / sourceFiles;

    if (specRatio < 0.3) {
      insights.push({
        id: `spec_code_alignment_${Date.now()}`,
        type: 'quality',
        title: 'Specification-Code Alignment Issue',
        description: `Specification ratio is ${(specRatio * 100).toFixed(1)}%, below the recommended 30%`,
        severity: 'medium',
        confidence: 0.8,
        data: { specCount, sourceFiles, ratio: specRatio },
        timestamp: new Date(),
        actionable: true,
        action: {
          type: 'improve_spec_alignment',
          description: 'Add more specifications to match code complexity',
          url: '/spec/alignment'
        }
      });
    }

    return insights;
  }

  /**
   * Calculate trend from data points
   */
  private calculateTrend(data: number[]): TrendAnalysis {
    if (data.length < 2) {
      return {
        metric: 'unknown',
        direction: 'stable',
        change: 0,
        significance: 'low',
        period: 'unknown',
        data: []
      };
    }

    const first = data[0];
    const last = data[data.length - 1];
    const change = last - first;
    const changePercent = (change / first) * 100;

    let direction: 'up' | 'down' | 'stable' = 'stable';
    let significance: 'low' | 'medium' | 'high' = 'low';

    if (Math.abs(changePercent) > 20) {
      direction = change > 0 ? 'up' : 'down';
      significance = 'high';
    } else if (Math.abs(changePercent) > 10) {
      direction = change > 0 ? 'up' : 'down';
      significance = 'medium';
    }

    return {
      metric: 'quality',
      direction,
      change: changePercent,
      significance,
      period: `${data.length} days`,
      data: data.map((value, index) => ({
        date: new Date(Date.now() - (data.length - index - 1) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        value
      }))
    };
  }

  /**
   * Get all insights
   */
  getInsights(): AnalyticsInsight[] {
    return Array.from(this.insights.values());
  }

  /**
   * Get insights by type
   */
  getInsightsByType(type: AnalyticsInsight['type']): AnalyticsInsight[] {
    return this.getInsights().filter(insight => insight.type === type);
  }

  /**
   * Get insights by severity
   */
  getInsightsBySeverity(severity: AnalyticsInsight['severity']): AnalyticsInsight[] {
    return this.getInsights().filter(insight => insight.severity === severity);
  }

  /**
   * Get actionable insights
   */
  getActionableInsights(): AnalyticsInsight[] {
    return this.getInsights().filter(insight => insight.actionable);
  }

  /**
   * Start analysis loop
   */
  private startAnalysisLoop(): void {
    this.updateInterval = setInterval(() => {
      this.emit('analysis_required');
    }, 30000); // Run analysis every 30 seconds
  }

  /**
   * Stop analysis loop
   */
  private stopAnalysisLoop(): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
  }

  /**
   * Cleanup resources
   */
  cleanup(): void {
    this.stopAnalysisLoop();
    this.removeAllListeners();
    this.insights.clear();
    this.historicalData.clear();
    this.analysisCache.clear();
  }
}
