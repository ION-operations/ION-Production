/**
 * AIM-OS Services Index
 * Central export for all AIM-OS service clients
 */

// Core MCP Service
export { mcpService, MCPService } from './MCPService'
export type { MCPToolRequest, MCPToolResponse, CommandServerHealth } from './MCPService'

// AIM-OS System Services
export { cmcService, CMCService } from './CMCService'
export type { CMCStats, StoreMemoryRequest, RetrieveMemoryRequest } from './CMCService'

export { hhniService, HHNIService } from './HHNIService'

export { vifService, VIFService } from './VIFService'
export type { TrackConfidenceRequest } from './VIFService'

export { tcsService, TCSService } from './TCSService'
export type { AddTimelineEntryRequest } from './TCSService'

export { segService, SEGService } from './SEGService'

export { casService, CASService } from './CASService'

export { apoeService, APOEService } from './APOEService'
export type { ExecutionPlan, PlanExecutionStatus } from './APOEService'

// Organization Services
export { systemIndexService, SystemIndexService } from './SystemIndexService'
export type { SystemIndex } from './SystemIndexService'

export { systemMapService, SystemMapService } from './SystemMapService'
export type { SystemMap } from './SystemMapService'

export { superIndexService, SuperIndexService } from './SuperIndexService'
export type { SuperIndexResponse, SuperIndexFrontmatter } from './SuperIndexService'

export { goalTreeService, GoalTreeService } from './GoalTreeService'
export type { GoalTreeResponse, GoalTreeData, GoalTreeObjective } from './GoalTreeService'

export { hierarchicalNavigationService, HierarchicalNavigationService } from './HierarchicalNavigationService'
export type { HierarchicalNavigationResponse, HierarchicalNavigationFrontmatter } from './HierarchicalNavigationService'

export { consolidationService } from './ConsolidationService'
export type { ConsolidationDocument, SystemMapEntry, IntegrationEntry, PhaseStatus, ConsolidationStats } from './ConsolidationService'

