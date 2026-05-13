/**
 * Lucid Orchestrator Main Service
 * 
 * Coordinates all four panes and provides unified data management
 * for the Lucid Orchestrator system.
 */

import {
  LucidOrchestratorData,
  SystemMetadata,
  CodePaneData,
  BlueprintPaneData,
  SpecPaneData,
  TimelinePaneData
} from '../data_models/core_interfaces';
import { CodePaneService } from './code_pane_service';
import { BlueprintPaneService } from './blueprint_pane_service';
import { SpecPaneService } from './spec_pane_service';
import { TimelinePaneService } from './timeline_pane_service';
import { Event } from '../data_models/core_interfaces';

export class LucidOrchestratorService {
  private codeService: CodePaneService;
  private blueprintService: BlueprintPaneService;
  private specService: SpecPaneService;
  private timelineService: TimelinePaneService;
  private currentSystemId: string | null = null;
  private dataCache: Map<string, LucidOrchestratorData> = new Map();
  private changeCallbacks: Set<(data: LucidOrchestratorData) => void> = new Set();

  constructor(systemRoot: string = 'knowledge_architecture/systems') {
    this.codeService = new CodePaneService(systemRoot);
    this.blueprintService = new BlueprintPaneService();
    this.specService = new SpecPaneService();
    this.timelineService = new TimelinePaneService();
    
    this.setupEventHandlers();
  }

  /**
   * Load complete system data
   */
  async loadSystem(systemId: string): Promise<LucidOrchestratorData> {
    this.currentSystemId = systemId;

    // Check cache first
    if (this.dataCache.has(systemId)) {
      return this.dataCache.get(systemId)!;
    }

    try {
      // Load data from all services
      const [codeData, specData, timelineData] = await Promise.all([
        this.codeService.loadSystemData(systemId),
        this.specService.loadSpecifications(systemId),
        this.timelineService.loadEvents(systemId)
      ]);

      // Build blueprint from code data
      const blueprintData = await this.buildBlueprintData(codeData);

      // Build spec pane data
      const specPaneData = await this.buildSpecPaneData(specData, codeData);

      // Build timeline pane data
      const timelinePaneData = await this.buildTimelinePaneData(timelineData, systemId);

      // Create unified data structure
      const orchestratorData: LucidOrchestratorData = {
        code: codeData,
        blueprint: blueprintData,
        spec: specPaneData,
        timeline: timelinePaneData,
        metadata: {
          id: systemId,
          name: codeData.system.name,
          description: codeData.system.description,
          version: '1.0.0',
          status: 'active',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          lastSyncAt: new Date().toISOString()
        }
      };

      // Cache the data
      this.dataCache.set(systemId, orchestratorData);

      // Notify callbacks
      this.changeCallbacks.forEach(callback => callback(orchestratorData));

      return orchestratorData;
    } catch (error) {
      console.error(`Error loading system ${systemId}:`, error);
      throw error;
    }
  }

  /**
   * Build blueprint data from code data
   */
  private async buildBlueprintData(codeData: CodePaneData): Promise<BlueprintPaneData> {
    const architecture = await this.blueprintService.buildArchitectureGraph(codeData);
    const documentation = await this.blueprintService.buildDocumentationGraph(codeData);

    return {
      architecture,
      documentation,
      layout: this.blueprintService.getLayoutConfiguration(),
      filters: this.blueprintService.getFilterConfiguration()
    };
  }

  /**
   * Build spec pane data
   */
  private async buildSpecPaneData(specs: any, codeData: CodePaneData): Promise<SpecPaneData> {
    const documentation = await this.specService.buildDocumentationMapping(codeData);
    const compliance = await this.calculateOverallCompliance(specs, codeData);
    const quality = await this.specService.calculateQualityMetrics(specs);

    return {
      specs,
      documentation,
      compliance,
      quality
    };
  }

  /**
   * Build timeline pane data
   */
  private async buildTimelinePaneData(events: any, systemId: string): Promise<TimelinePaneData> {
    const documentation = await this.timelineService.buildDocumentationTimeline(systemId);
    const evolution = await this.timelineService.buildEvolutionData(systemId);
    const analytics = await this.timelineService.getAnalytics(systemId);

    return {
      events,
      documentation,
      evolution,
      analytics
    };
  }

  /**
   * Calculate overall compliance
   */
  private async calculateOverallCompliance(specs: any, codeData: CodePaneData): Promise<any> {
    const allViolations: any[] = [];
    const allWarnings: any[] = [];
    const allRecommendations: any[] = [];

    // Check compliance for each specification
    for (const req of specs.requirements) {
      try {
        const compliance = await this.specService.checkCompliance(req.id, codeData);
        allViolations.push(...compliance.violations);
        allWarnings.push(...compliance.warnings);
        allRecommendations.push(...compliance.recommendations);
      } catch (error) {
        console.error(`Error checking compliance for ${req.id}:`, error);
      }
    }

    // Calculate overall score
    const totalIssues = allViolations.length + allWarnings.length;
    const overallScore = totalIssues === 0 ? 1.0 : Math.max(0, 1.0 - totalIssues / 10);

    return {
      violations: allViolations,
      warnings: allWarnings,
      recommendations: allRecommendations,
      overallScore
    };
  }

  /**
   * Update system data
   */
  async updateSystem(systemId: string, updates: Partial<LucidOrchestratorData>): Promise<void> {
    const currentData = this.dataCache.get(systemId);
    if (!currentData) {
      throw new Error(`System ${systemId} not loaded`);
    }

    // Update the data
    const updatedData = {
      ...currentData,
      ...updates,
      metadata: {
        ...currentData.metadata,
        ...updates.metadata,
        updatedAt: new Date().toISOString(),
        lastSyncAt: new Date().toISOString()
      }
    };

    // Update cache
    this.dataCache.set(systemId, updatedData);

    // Notify callbacks
    this.changeCallbacks.forEach(callback => callback(updatedData));
  }

  /**
   * Refresh system data
   */
  async refreshSystem(systemId: string): Promise<LucidOrchestratorData> {
    // Clear cache
    this.dataCache.delete(systemId);
    
    // Reload system
    return await this.loadSystem(systemId);
  }

  /**
   * Get current system data
   */
  getCurrentSystemData(): LucidOrchestratorData | null {
    if (!this.currentSystemId) {
      return null;
    }
    return this.dataCache.get(this.currentSystemId) || null;
  }

  /**
   * Get system data by ID
   */
  getSystemData(systemId: string): LucidOrchestratorData | null {
    return this.dataCache.get(systemId) || null;
  }

  /**
   * Subscribe to data changes
   */
  subscribeToChanges(callback: (data: LucidOrchestratorData) => void): () => void {
    this.changeCallbacks.add(callback);
    
    // Return unsubscribe function
    return () => {
      this.changeCallbacks.delete(callback);
    };
  }

  /**
   * Setup event handlers for cross-pane synchronization
   */
  private setupEventHandlers(): void {
    // Subscribe to timeline events
    this.timelineService.subscribeToEvents((event: Event) => {
      this.handleTimelineEvent(event);
    });

    // Subscribe to code changes
    this.codeService.watchFileChanges('current', (codeData: CodePaneData) => {
      this.handleCodeChange(codeData);
    });
  }

  /**
   * Handle timeline event
   */
  private handleTimelineEvent(event: Event): void {
    if (!this.currentSystemId) return;

    // Update relevant panes based on event type
    switch (event.type) {
      case 'documentation_created':
      case 'documentation_updated':
      case 'documentation_deleted':
        this.handleDocumentationChange(event);
        break;
      case 'code_implemented':
      case 'code_modified':
      case 'code_deleted':
        this.handleCodeChangeFromEvent(event);
        break;
      case 'spec_created':
      case 'spec_updated':
      case 'spec_deleted':
        this.handleSpecChange(event);
        break;
    }
  }

  /**
   * Handle documentation change
   */
  private async handleDocumentationChange(event: Event): Promise<void> {
    if (!this.currentSystemId) return;

    // Refresh blueprint pane to reflect documentation changes
    const currentData = this.dataCache.get(this.currentSystemId);
    if (currentData) {
      const updatedBlueprint = await this.buildBlueprintData(currentData.code);
      await this.updateSystem(this.currentSystemId, {
        blueprint: updatedBlueprint
      });
    }
  }

  /**
   * Handle code change
   */
  private async handleCodeChange(codeData: CodePaneData): Promise<void> {
    if (!this.currentSystemId) return;

    // Update code pane data
    await this.updateSystem(this.currentSystemId, {
      code: codeData
    });

    // Update blueprint pane
    const updatedBlueprint = await this.buildBlueprintData(codeData);
    await this.updateSystem(this.currentSystemId, {
      blueprint: updatedBlueprint
    });

    // Update spec pane compliance
    const currentData = this.dataCache.get(this.currentSystemId);
    if (currentData) {
      const updatedSpec = await this.buildSpecPaneData(currentData.spec.specs, codeData);
      await this.updateSystem(this.currentSystemId, {
        spec: updatedSpec
      });
    }
  }

  /**
   * Handle code change from event
   */
  private async handleCodeChangeFromEvent(event: Event): Promise<void> {
    if (!this.currentSystemId) return;

    // Refresh code data
    const codeData = await this.codeService.loadSystemData(this.currentSystemId);
    await this.handleCodeChange(codeData);
  }

  /**
   * Handle spec change
   */
  private async handleSpecChange(event: Event): Promise<void> {
    if (!this.currentSystemId) return;

    // Refresh spec data
    const specData = await this.specService.loadSpecifications(this.currentSystemId);
    const currentData = this.dataCache.get(this.currentSystemId);
    
    if (currentData) {
      const updatedSpec = await this.buildSpecPaneData(specData, currentData.code);
      await this.updateSystem(this.currentSystemId, {
        spec: updatedSpec
      });
    }
  }

  /**
   * Export system data
   */
  async exportSystem(systemId: string, format: 'json' | 'graphml' | 'dot' = 'json'): Promise<string> {
    const systemData = this.dataCache.get(systemId);
    if (!systemData) {
      throw new Error(`System ${systemId} not found`);
    }

    switch (format) {
      case 'json':
        return JSON.stringify(systemData, null, 2);
      case 'graphml':
        return await this.blueprintService.exportGraph('graphml');
      case 'dot':
        return await this.blueprintService.exportGraph('dot');
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }
  }

  /**
   * Get system metadata
   */
  getSystemMetadata(systemId: string): SystemMetadata | null {
    const systemData = this.dataCache.get(systemId);
    return systemData?.metadata || null;
  }

  /**
   * List all loaded systems
   */
  listLoadedSystems(): string[] {
    return Array.from(this.dataCache.keys());
  }

  /**
   * Clear system cache
   */
  clearSystemCache(systemId?: string): void {
    if (systemId) {
      this.dataCache.delete(systemId);
    } else {
      this.dataCache.clear();
    }
  }

  /**
   * Get service instances for direct access
   */
  getServices() {
    return {
      code: this.codeService,
      blueprint: this.blueprintService,
      spec: this.specService,
      timeline: this.timelineService
    };
  }

  /**
   * Cleanup resources
   */
  cleanup(): void {
    this.codeService.cleanup();
    this.timelineService.clearAnalyticsCache();
    this.specService.clearCaches();
    this.changeCallbacks.clear();
    this.dataCache.clear();
  }
}
