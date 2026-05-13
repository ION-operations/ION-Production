/**
 * Core Data Interfaces for Lucid Orchestrator
 * 
 * This file defines the fundamental data structures for the 4-pane system:
 * - Code Pane: File system, dependencies, metrics
 * - Blueprint Pane: Architecture visualization, documentation mapping
 * - Spec Pane: Specifications, compliance, quality
 * - Timeline Pane: Events, evolution, analytics
 */

export interface LucidOrchestratorData {
  code: CodePaneData;
  blueprint: BlueprintPaneData;
  spec: SpecPaneData;
  timeline: TimelinePaneData;
  metadata: SystemMetadata;
}

export interface SystemMetadata {
  id: string;
  name: string;
  description: string;
  version: string;
  status: 'active' | 'inactive' | 'archived';
  createdAt: string;
  updatedAt: string;
  lastSyncAt: string;
}

// ============================================================================
// CODE PANE DATA STRUCTURES
// ============================================================================

export interface CodePaneData {
  system: SystemInfo;
  files: FileCollection;
  metrics: CodeMetrics;
  dependencies: DependencyGraph;
}

export interface SystemInfo {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive' | 'archived';
  rootPath: string;
  language: string;
  framework?: string;
}

export interface FileCollection {
  documentation: FileInfo[];
  source: FileInfo[];
  tests: FileInfo[];
  config: FileInfo[];
  other: FileInfo[];
}

export interface FileInfo {
  id: string;
  path: string;
  name: string;
  type: 'markdown' | 'python' | 'typescript' | 'javascript' | 'json' | 'yaml' | 'other';
  size: number;
  lines: number;
  lastModified: string;
  contentHash: string;
  metadata: FileMetadata;
}

export interface FileMetadata {
  level?: 'L0' | 'L1' | 'L2' | 'L3' | 'L4';
  wordCount?: number;
  complexity?: number;
  testCoverage?: number;
  dependencies?: string[];
  imports?: string[];
  exports?: string[];
  functions?: FunctionInfo[];
  classes?: ClassInfo[];
  interfaces?: InterfaceInfo[];
}

export interface FunctionInfo {
  name: string;
  line: number;
  parameters: string[];
  returnType?: string;
  complexity: number;
  documentation?: string;
}

export interface ClassInfo {
  name: string;
  line: number;
  methods: FunctionInfo[];
  properties: PropertyInfo[];
  inheritance?: string[];
  complexity: number;
  documentation?: string;
}

export interface InterfaceInfo {
  name: string;
  line: number;
  properties: PropertyInfo[];
  methods: FunctionInfo[];
  inheritance?: string[];
  documentation?: string;
}

export interface PropertyInfo {
  name: string;
  type: string;
  line: number;
  optional: boolean;
  documentation?: string;
}

export interface CodeMetrics {
  totalLines: number;
  totalFiles: number;
  testCoverage: number;
  documentationCoverage: number;
  complexity: number;
  maintainability: number;
  technicalDebt: number;
  codeQuality: number;
}

export interface DependencyGraph {
  internal: DependencyEdge[];
  external: DependencyEdge[];
  documentation: DependencyEdge[];
}

export interface DependencyEdge {
  from: string;
  to: string;
  type: 'import' | 'reference' | 'inheritance' | 'composition' | 'aggregation';
  weight: number;
  metadata?: Record<string, any>;
}

// ============================================================================
// BLUEPRINT PANE DATA STRUCTURES
// ============================================================================

export interface BlueprintPaneData {
  architecture: ArchitectureGraph;
  documentation: DocumentationGraph;
  layout: LayoutConfiguration;
  filters: FilterConfiguration;
}

export interface ArchitectureGraph {
  nodes: ArchitectureNode[];
  edges: ArchitectureEdge[];
  metadata: GraphMetadata;
}

export interface ArchitectureNode {
  id: string;
  name: string;
  type: 'system' | 'component' | 'module' | 'class' | 'function' | 'interface';
  position: Position;
  size: Size;
  style: NodeStyle;
  data: NodeData;
}

export interface Position {
  x: number;
  y: number;
}

export interface Size {
  width: number;
  height: number;
}

export interface NodeStyle {
  color: string;
  shape: 'rectangle' | 'circle' | 'diamond' | 'hexagon';
  border: BorderStyle;
  fill: FillStyle;
  text: TextStyle;
}

export interface BorderStyle {
  width: number;
  style: 'solid' | 'dashed' | 'dotted';
  color: string;
}

export interface FillStyle {
  color: string;
  opacity: number;
}

export interface TextStyle {
  color: string;
  fontSize: number;
  fontWeight: 'normal' | 'bold';
  fontFamily: string;
}

export interface NodeData {
  system?: string;
  component?: string;
  file?: string;
  line?: number;
  complexity?: number;
  status?: 'active' | 'inactive' | 'deprecated';
  quality?: number;
  [key: string]: any;
}

export interface ArchitectureEdge {
  id: string;
  from: string;
  to: string;
  type: 'composition' | 'aggregation' | 'inheritance' | 'dependency' | 'association';
  weight: number;
  style: EdgeStyle;
  label?: string;
  data?: Record<string, any>;
}

export interface EdgeStyle {
  color: string;
  width: number;
  style: 'solid' | 'dashed' | 'dotted';
  arrow?: 'none' | 'forward' | 'backward' | 'both';
}

export interface DocumentationGraph {
  L0: DocumentationNode[];
  L1: DocumentationNode[];
  L2: DocumentationNode[];
  L3: DocumentationNode[];
  L4: DocumentationNode[];
}

export interface DocumentationNode {
  id: string;
  title: string;
  position: Position;
  size: Size;
  style: NodeStyle;
  data: DocumentationNodeData;
}

export interface DocumentationNodeData {
  file: string;
  level: 'L0' | 'L1' | 'L2' | 'L3' | 'L4';
  wordCount: number;
  quality: number;
  lastModified: string;
  [key: string]: any;
}

export interface GraphMetadata {
  totalNodes: number;
  totalEdges: number;
  lastUpdated: string;
  version: string;
  exportedAt?: string;
}

export interface LayoutConfiguration {
  algorithm: 'force-directed' | 'hierarchical' | 'circular' | 'grid';
  settings: Record<string, any>;
  autoLayout: boolean;
  spacing: number;
}

export interface FilterConfiguration {
  nodeTypes: string[];
  edgeTypes: string[];
  qualityThreshold: number;
  complexityThreshold: number;
  statusFilter: string[];
}

// ============================================================================
// SPEC PANE DATA STRUCTURES
// ============================================================================

export interface SpecPaneData {
  specs: SpecificationCollection;
  documentation: DocumentationMapping;
  compliance: ComplianceStatus;
  quality: QualityMetrics;
}

export interface SpecificationCollection {
  requirements: Specification[];
  constraints: Specification[];
  standards: Specification[];
  guidelines: Specification[];
}

export interface Specification {
  id: string;
  nodeId?: string;
  title: string;
  description: string;
  type: 'requirement' | 'constraint' | 'standard' | 'guideline';
  priority: 'critical' | 'high' | 'medium' | 'low';
  content: SpecificationContent;
  status: 'active' | 'inactive' | 'deprecated' | 'draft';
  violations: Violation[];
  created: string;
  updated: string;
  author: string;
  version: string;
}

export interface SpecificationContent {
  must: string[];
  mustNot: string[];
  should: string[];
  could: string[];
  examples?: string[];
  references?: string[];
}

export interface Violation {
  id: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
  line?: number;
  file?: string;
  suggestion?: string;
  created: string;
  resolved?: string;
}

export interface DocumentationMapping {
  L0: MappingEntry[];
  L1: MappingEntry[];
  L2: MappingEntry[];
  L3: MappingEntry[];
  L4: MappingEntry[];
}

export interface MappingEntry {
  specId: string;
  docId: string;
  mapping: string;
  alignment: number;
}

export interface ComplianceStatus {
  violations: Violation[];
  warnings: Warning[];
  recommendations: Recommendation[];
  overallScore: number;
}

export interface Warning {
  id: string;
  specId: string;
  message: string;
  severity: 'high' | 'medium' | 'low';
  recommendation: string;
}

export interface Recommendation {
  id: string;
  specId: string;
  message: string;
  priority: 'high' | 'medium' | 'low';
  effort: 'low' | 'medium' | 'high';
}

export interface QualityMetrics {
  specCompleteness: number;
  docAlignment: number;
  complianceRate: number;
  overallHealth: number;
  lastChecked: string;
}

// ============================================================================
// TIMELINE PANE DATA STRUCTURES
// ============================================================================

export interface TimelinePaneData {
  events: EventCollection;
  documentation: DocumentationTimeline;
  evolution: EvolutionData;
  analytics: AnalyticsData;
}

export interface EventCollection {
  documentation: Event[];
  code: Event[];
  spec: Event[];
  system: Event[];
}

export interface Event {
  id: string;
  timestamp: string;
  type: EventType;
  nodeId?: string;
  sessionId: string;
  data: EventData;
  context: EventContext;
}

export type EventType = 
  | 'documentation_created' | 'documentation_updated' | 'documentation_deleted'
  | 'code_implemented' | 'code_modified' | 'code_deleted' | 'test_added' | 'test_updated'
  | 'spec_created' | 'spec_updated' | 'spec_deleted' | 'violation_detected' | 'violation_resolved'
  | 'system_created' | 'system_updated' | 'system_deleted' | 'deployment' | 'rollback';

export interface EventData {
  action: string;
  details: Record<string, any>;
  result: 'success' | 'failure' | 'partial';
}

export interface EventContext {
  user: string;
  system: string;
  environment: 'development' | 'staging' | 'production';
  version: string;
}

export interface DocumentationTimeline {
  L0: LevelTimeline;
  L1: LevelTimeline;
  L2: LevelTimeline;
  L3: LevelTimeline;
  L4: LevelTimeline;
}

export interface LevelTimeline {
  level: 'L0' | 'L1' | 'L2' | 'L3' | 'L4';
  events: TimelineEvent[];
  trends: LevelTrends;
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  action: string;
  quality: number;
}

export interface LevelTrends {
  qualityImprovement: number;
  updateFrequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
  stability: 'high' | 'medium' | 'low';
}

export interface EvolutionData {
  versions: VersionInfo[];
  milestones: Milestone[];
}

export interface VersionInfo {
  version: string;
  timestamp: string;
  changes: string[];
  quality: number;
}

export interface Milestone {
  id: string;
  name: string;
  timestamp: string;
  description: string;
  status: 'completed' | 'in_progress' | 'planned' | 'cancelled';
}

export interface AnalyticsData {
  activity: ActivityData[];
  quality: QualityData[];
  performance: PerformanceData[];
}

export interface ActivityData {
  date: string;
  documentationUpdates: number;
  codeChanges: number;
  specUpdates: number;
  totalActivity: number;
}

export interface QualityData {
  date: string;
  overallQuality: number;
  documentationQuality: number;
  codeQuality: number;
  specQuality: number;
}

export interface PerformanceData {
  date: string;
  memoryUsage: number;
  responseTime: number;
  throughput: number;
  errorRate: number;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export interface TimeRange {
  start: string;
  end: string;
}

export interface EventFilters {
  types?: EventType[];
  nodeIds?: string[];
  timeRange?: TimeRange;
  users?: string[];
  systems?: string[];
}

export interface ChangeSet {
  added: string[];
  modified: string[];
  deleted: string[];
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

export interface ReferenceMap {
  [key: string]: string[];
}

// ============================================================================
// EXPORT ALL INTERFACES
// ============================================================================

export * from './core_interfaces';
