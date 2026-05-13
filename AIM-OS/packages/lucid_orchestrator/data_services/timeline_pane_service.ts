/**
 * Timeline Pane Data Service
 * 
 * Handles event tracking, timeline visualization,
 * and analytics for the Timeline Pane of the Lucid Orchestrator.
 */

import {
  TimelinePaneData,
  EventCollection,
  Event,
  EventType,
  EventData,
  EventContext,
  DocumentationTimeline,
  LevelTimeline,
  TimelineEvent,
  LevelTrends,
  EvolutionData,
  VersionInfo,
  Milestone,
  AnalyticsData,
  ActivityData,
  QualityData,
  PerformanceData,
  EventFilters,
  TimeRange
} from '../data_models/core_interfaces';
import { CodePaneData } from '../data_models/core_interfaces';
import * as fs from 'fs';
import * as path from 'path';

export class TimelinePaneService {
  private events: Map<string, Event> = new Map();
  private analyticsCache: Map<string, AnalyticsData> = new Map();
  private eventCallbacks: Set<(event: Event) => void> = new Set();

  constructor() {
    this.loadHistoricalEvents();
  }

  /**
   * Load events for a system
   */
  async loadEvents(systemId: string, filters?: EventFilters): Promise<EventCollection> {
    const allEvents = Array.from(this.events.values())
      .filter(event => event.context.system === systemId);

    let filteredEvents = allEvents;

    // Apply filters
    if (filters) {
      if (filters.types && filters.types.length > 0) {
        filteredEvents = filteredEvents.filter(event => 
          filters.types!.includes(event.type)
        );
      }

      if (filters.nodeIds && filters.nodeIds.length > 0) {
        filteredEvents = filteredEvents.filter(event => 
          event.nodeId && filters.nodeIds!.includes(event.nodeId)
        );
      }

      if (filters.timeRange) {
        const start = new Date(filters.timeRange.start);
        const end = new Date(filters.timeRange.end);
        filteredEvents = filteredEvents.filter(event => {
          const eventTime = new Date(event.timestamp);
          return eventTime >= start && eventTime <= end;
        });
      }

      if (filters.users && filters.users.length > 0) {
        filteredEvents = filteredEvents.filter(event => 
          filters.users!.includes(event.context.user)
        );
      }
    }

    // Categorize events
    const events: EventCollection = {
      documentation: [],
      code: [],
      spec: [],
      system: []
    };

    filteredEvents.forEach(event => {
      switch (event.type) {
        case 'documentation_created':
        case 'documentation_updated':
        case 'documentation_deleted':
          events.documentation.push(event);
          break;
        case 'code_implemented':
        case 'code_modified':
        case 'code_deleted':
        case 'test_added':
        case 'test_updated':
          events.code.push(event);
          break;
        case 'spec_created':
        case 'spec_updated':
        case 'spec_deleted':
        case 'violation_detected':
        case 'violation_resolved':
          events.spec.push(event);
          break;
        case 'system_created':
        case 'system_updated':
        case 'system_deleted':
        case 'deployment':
        case 'rollback':
          events.system.push(event);
          break;
      }
    });

    return events;
  }

  /**
   * Add a new event
   */
  async addEvent(event: Event): Promise<void> {
    // Validate event
    this.validateEvent(event);

    // Store event
    this.events.set(event.id, event);

    // Notify callbacks
    this.eventCallbacks.forEach(callback => callback(event));

    // Persist event
    await this.persistEvent(event);
  }

  /**
   * Validate event data
   */
  private validateEvent(event: Event): void {
    if (!event.id || !event.timestamp || !event.type || !event.sessionId) {
      throw new Error('Invalid event: missing required fields');
    }

    if (!event.data || !event.context) {
      throw new Error('Invalid event: missing data or context');
    }

    if (!event.context.user || !event.context.system) {
      throw new Error('Invalid event: missing user or system in context');
    }
  }

  /**
   * Persist event to storage
   */
  private async persistEvent(event: Event): Promise<void> {
    const eventsDir = path.join('data', 'timeline', 'events');
    if (!fs.existsSync(eventsDir)) {
      fs.mkdirSync(eventsDir, { recursive: true });
    }

    const eventFile = path.join(eventsDir, `${event.id}.json`);
    fs.writeFileSync(eventFile, JSON.stringify(event, null, 2));
  }

  /**
   * Load historical events from storage
   */
  private loadHistoricalEvents(): void {
    const eventsDir = path.join('data', 'timeline', 'events');
    if (!fs.existsSync(eventsDir)) {
      return;
    }

    const files = fs.readdirSync(eventsDir);
    for (const file of files) {
      if (file.endsWith('.json')) {
        try {
          const eventData = fs.readFileSync(path.join(eventsDir, file), 'utf-8');
          const event = JSON.parse(eventData) as Event;
          this.events.set(event.id, event);
        } catch (error) {
          console.error(`Error loading event file ${file}:`, error);
        }
      }
    }
  }

  /**
   * Build documentation timeline
   */
  async buildDocumentationTimeline(systemId: string): Promise<DocumentationTimeline> {
    const events = await this.loadEvents(systemId, {
      types: ['documentation_created', 'documentation_updated', 'documentation_deleted']
    });

    const timeline: DocumentationTimeline = {
      L0: this.buildLevelTimeline(events.documentation, 'L0'),
      L1: this.buildLevelTimeline(events.documentation, 'L1'),
      L2: this.buildLevelTimeline(events.documentation, 'L2'),
      L3: this.buildLevelTimeline(events.documentation, 'L3'),
      L4: this.buildLevelTimeline(events.documentation, 'L4')
    };

    return timeline;
  }

  /**
   * Build timeline for a specific documentation level
   */
  private buildLevelTimeline(events: Event[], level: 'L0' | 'L1' | 'L2' | 'L3' | 'L4'): LevelTimeline {
    const levelEvents = events.filter(event => 
      event.data.details?.level === level
    );

    const timelineEvents: TimelineEvent[] = levelEvents.map(event => ({
      id: event.id,
      timestamp: event.timestamp,
      action: event.data.action,
      quality: this.calculateEventQuality(event)
    }));

    const trends: LevelTrends = this.calculateLevelTrends(timelineEvents);

    return {
      level,
      events: timelineEvents,
      trends
    };
  }

  /**
   * Calculate quality score for an event
   */
  private calculateEventQuality(event: Event): number {
    let quality = 0.5; // Base quality

    // Adjust based on event type
    switch (event.type) {
      case 'documentation_created':
        quality += 0.2;
        break;
      case 'documentation_updated':
        quality += 0.1;
        break;
      case 'documentation_deleted':
        quality -= 0.1;
        break;
    }

    // Adjust based on data quality
    if (event.data.details?.wordCount && event.data.details.wordCount > 100) {
      quality += 0.1;
    }

    if (event.data.details?.changes && Array.isArray(event.data.details.changes) && event.data.details.changes.length > 0) {
      quality += 0.1;
    }

    return Math.max(0, Math.min(1, quality));
  }

  /**
   * Calculate trends for a documentation level
   */
  private calculateLevelTrends(events: TimelineEvent[]): LevelTrends {
    if (events.length === 0) {
      return {
        qualityImprovement: 0,
        updateFrequency: 'monthly',
        stability: 'low'
      };
    }

    // Calculate quality improvement
    const firstQuality = events[0]?.quality || 0.5;
    const lastQuality = events[events.length - 1]?.quality || 0.5;
    const qualityImprovement = lastQuality - firstQuality;

    // Calculate update frequency
    const timeSpan = this.calculateTimeSpan(events);
    let updateFrequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' = 'monthly';
    
    if (timeSpan.days <= 7) {
      updateFrequency = 'daily';
    } else if (timeSpan.days <= 30) {
      updateFrequency = 'weekly';
    } else if (timeSpan.days <= 90) {
      updateFrequency = 'monthly';
    } else {
      updateFrequency = 'quarterly';
    }

    // Calculate stability
    const qualityVariance = this.calculateQualityVariance(events);
    let stability: 'high' | 'medium' | 'low' = 'low';
    
    if (qualityVariance < 0.1) {
      stability = 'high';
    } else if (qualityVariance < 0.3) {
      stability = 'medium';
    }

    return {
      qualityImprovement,
      updateFrequency,
      stability
    };
  }

  /**
   * Calculate time span of events
   */
  private calculateTimeSpan(events: TimelineEvent[]): { days: number } {
    if (events.length < 2) {
      return { days: 0 };
    }

    const firstTime = new Date(events[0].timestamp);
    const lastTime = new Date(events[events.length - 1].timestamp);
    const diffMs = lastTime.getTime() - firstTime.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    return { days: diffDays };
  }

  /**
   * Calculate quality variance
   */
  private calculateQualityVariance(events: TimelineEvent[]): number {
    if (events.length < 2) {
      return 0;
    }

    const qualities = events.map(e => e.quality);
    const mean = qualities.reduce((sum, q) => sum + q, 0) / qualities.length;
    const variance = qualities.reduce((sum, q) => sum + Math.pow(q - mean, 2), 0) / qualities.length;
    
    return Math.sqrt(variance);
  }

  /**
   * Build evolution data
   */
  async buildEvolutionData(systemId: string): Promise<EvolutionData> {
    const versions = await this.buildVersionHistory(systemId);
    const milestones = await this.buildMilestones(systemId);

    return {
      versions,
      milestones
    };
  }

  /**
   * Build version history
   */
  private async buildVersionHistory(systemId: string): Promise<VersionInfo[]> {
    const events = await this.loadEvents(systemId, {
      types: ['system_created', 'system_updated', 'deployment']
    });

    const versions: VersionInfo[] = [];
    let versionNumber = 1;

    const eventsArray = Array.isArray(events) ? events : [
      ...(events.documentation || []),
      ...(events.code || []),
      ...(events.spec || []),
      ...(events.system || [])
    ];
    for (const event of eventsArray) {
      if (event.type === 'deployment' || event.type === 'system_created') {
        versions.push({
          version: `v${versionNumber}.0.0`,
          timestamp: event.timestamp,
          changes: (Array.isArray(event.data.details?.changes) ? event.data.details.changes : ['Initial version']) as string[],
          quality: this.calculateEventQuality(event)
        });
        versionNumber++;
      }
    }

    return versions;
  }

  /**
   * Build milestones
   */
  private async buildMilestones(systemId: string): Promise<Milestone[]> {
    const events = await this.loadEvents(systemId, {
      types: ['system_created', 'deployment', 'violation_resolved']
    });

    const milestones: Milestone[] = [];

    const eventsArray = Array.isArray(events) ? events : [
      ...(events.documentation || []),
      ...(events.code || []),
      ...(events.spec || []),
      ...(events.system || [])
    ];
    for (const event of eventsArray) {
      if (event.type === 'system_created') {
        milestones.push({
          id: `milestone_${event.id}`,
          name: 'System Created',
          timestamp: event.timestamp,
          description: 'Initial system creation',
          status: 'completed'
        });
      } else if (event.type === 'deployment') {
        milestones.push({
          id: `milestone_${event.id}`,
          name: 'System Deployed',
          timestamp: event.timestamp,
          description: 'System deployed to production',
          status: 'completed'
        });
      } else if (event.type === 'violation_resolved') {
        milestones.push({
          id: `milestone_${event.id}`,
          name: 'Violation Resolved',
          timestamp: event.timestamp,
          description: 'Critical violation resolved',
          status: 'completed'
        });
      }
    }

    return milestones;
  }

  /**
   * Get analytics data
   */
  async getAnalytics(systemId: string, timeRange?: TimeRange): Promise<AnalyticsData> {
    const cacheKey = `${systemId}_${timeRange ? JSON.stringify(timeRange) : 'all'}`;
    
    if (this.analyticsCache.has(cacheKey)) {
      return this.analyticsCache.get(cacheKey)!;
    }

    const events = await this.loadEvents(systemId, { timeRange });
    const analytics = this.calculateAnalytics(events);

    this.analyticsCache.set(cacheKey, analytics);
    return analytics;
  }

  /**
   * Calculate analytics from events
   */
  private calculateAnalytics(events: EventCollection): AnalyticsData {
    const activity = this.calculateActivityData(events);
    const quality = this.calculateQualityData(events);
    const performance = this.calculatePerformanceData(events);

    return {
      activity,
      quality,
      performance
    };
  }

  /**
   * Calculate activity data
   */
  private calculateActivityData(events: EventCollection): ActivityData[] {
    const activityMap = new Map<string, ActivityData>();

    // Process all events
    const allEvents = [
      ...events.documentation,
      ...events.code,
      ...events.spec,
      ...events.system
    ];

    for (const event of allEvents) {
      const date = new Date(event.timestamp).toISOString().split('T')[0];
      
      if (!activityMap.has(date)) {
        activityMap.set(date, {
          date,
          documentationUpdates: 0,
          codeChanges: 0,
          specUpdates: 0,
          totalActivity: 0
        });
      }

      const activity = activityMap.get(date)!;
      
      switch (event.type) {
        case 'documentation_created':
        case 'documentation_updated':
        case 'documentation_deleted':
          activity.documentationUpdates++;
          break;
        case 'code_implemented':
        case 'code_modified':
        case 'code_deleted':
        case 'test_added':
        case 'test_updated':
          activity.codeChanges++;
          break;
        case 'spec_created':
        case 'spec_updated':
        case 'spec_deleted':
        case 'violation_detected':
        case 'violation_resolved':
          activity.specUpdates++;
          break;
      }
      
      activity.totalActivity++;
    }

    return Array.from(activityMap.values()).sort((a, b) => 
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
  }

  /**
   * Calculate quality data
   */
  private calculateQualityData(events: EventCollection): QualityData[] {
    const qualityMap = new Map<string, QualityData>();

    const allEvents = [
      ...events.documentation,
      ...events.code,
      ...events.spec,
      ...events.system
    ];

    for (const event of allEvents) {
      const date = new Date(event.timestamp).toISOString().split('T')[0];
      
      if (!qualityMap.has(date)) {
        qualityMap.set(date, {
          date,
          overallQuality: 0,
          documentationQuality: 0,
          codeQuality: 0,
          specQuality: 0
        });
      }

      const quality = qualityMap.get(date)!;
      const eventQuality = this.calculateEventQuality(event);
      
      // Update quality scores based on event type
      if (event.type.startsWith('documentation_')) {
        quality.documentationQuality = Math.max(quality.documentationQuality, eventQuality);
      } else if (event.type.startsWith('code_') || event.type.startsWith('test_')) {
        quality.codeQuality = Math.max(quality.codeQuality, eventQuality);
      } else if (event.type.startsWith('spec_') || event.type.startsWith('violation_')) {
        quality.specQuality = Math.max(quality.specQuality, eventQuality);
      }
      
      quality.overallQuality = (quality.documentationQuality + quality.codeQuality + quality.specQuality) / 3;
    }

    return Array.from(qualityMap.values()).sort((a, b) => 
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
  }

  /**
   * Calculate performance data
   */
  private calculatePerformanceData(events: EventCollection): PerformanceData[] {
    const performanceMap = new Map<string, PerformanceData>();

    const allEvents = [
      ...events.documentation,
      ...events.code,
      ...events.spec,
      ...events.system
    ];

    for (const event of allEvents) {
      const date = new Date(event.timestamp).toISOString().split('T')[0];
      
      if (!performanceMap.has(date)) {
        performanceMap.set(date, {
          date,
          memoryUsage: 0.5, // Mock data
          responseTime: 100, // Mock data
          throughput: 1000, // Mock data
          errorRate: 0.01 // Mock data
        });
      }

      const performance = performanceMap.get(date)!;
      
      // Update performance metrics based on event type
      if (event.type === 'code_implemented') {
        performance.memoryUsage += 0.1;
        performance.throughput += 100;
      } else if (event.type === 'violation_detected') {
        performance.errorRate += 0.01;
      } else if (event.type === 'violation_resolved') {
        performance.errorRate -= 0.01;
        performance.responseTime -= 10;
      }
      
      // Ensure values stay within reasonable bounds
      performance.memoryUsage = Math.max(0, Math.min(1, performance.memoryUsage));
      performance.errorRate = Math.max(0, Math.min(1, performance.errorRate));
      performance.responseTime = Math.max(10, performance.responseTime);
      performance.throughput = Math.max(100, performance.throughput);
    }

    return Array.from(performanceMap.values()).sort((a, b) => 
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
  }

  /**
   * Subscribe to event notifications
   */
  subscribeToEvents(callback: (event: Event) => void): () => void {
    this.eventCallbacks.add(callback);
    
    // Return unsubscribe function
    return () => {
      this.eventCallbacks.delete(callback);
    };
  }

  /**
   * Create a new event
   */
  createEvent(
    type: EventType,
    nodeId: string | undefined,
    sessionId: string,
    data: EventData,
    context: EventContext
  ): Event {
    return {
      id: `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      type,
      nodeId,
      sessionId,
      data,
      context
    };
  }

  /**
   * Clear analytics cache
   */
  clearAnalyticsCache(): void {
    this.analyticsCache.clear();
  }

  /**
   * Get event by ID
   */
  getEvent(eventId: string): Event | null {
    return this.events.get(eventId) || null;
  }

  /**
   * Get all events for a system
   */
  getSystemEvents(systemId: string): Event[] {
    return Array.from(this.events.values())
      .filter(event => event.context.system === systemId);
  }
}
