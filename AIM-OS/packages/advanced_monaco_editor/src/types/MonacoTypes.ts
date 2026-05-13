/**
 * Advanced Monaco Editor - Core Type Definitions
 * 
 * This file contains all the core type definitions for the Advanced Monaco Editor system.
 * These types define the interfaces for components, services, and data structures.
 */

import * as monaco from 'monaco-editor';

// ============================================================================
// CORE MONACO EDITOR TYPES
// ============================================================================

/**
 * Position in the Monaco editor
 */
export interface Position {
  line: number;
  column: number;
}

/**
 * Range in the Monaco editor
 */
export interface Range {
  start: Position;
  end: Position;
}

/**
 * Symbol types that can be detected in code
 */
export enum SymbolType {
  FUNCTION = 'function',
  CLASS = 'class',
  INTERFACE = 'interface',
  VARIABLE = 'variable',
  CONSTANT = 'constant',
  ENUM = 'enum',
  MODULE = 'module',
  NAMESPACE = 'namespace',
  TYPE = 'type',
  METHOD = 'method',
  PROPERTY = 'property',
  PARAMETER = 'parameter'
}

/**
 * Symbol kinds for classification
 */
export enum SymbolKind {
  DECLARATION = 'declaration',
  DEFINITION = 'definition',
  REFERENCE = 'reference',
  IMPORT = 'import',
  EXPORT = 'export',
  CALL = 'call',
  ASSIGNMENT = 'assignment',
  ACCESS = 'access'
}

/**
 * Symbol information extracted from code
 */
export interface SymbolInfo {
  id: string;
  name: string;
  type: SymbolType;
  kind: SymbolKind;
  position: Position;
  range: Range;
  language: string;
  metadata: SymbolMetadata;
  parent?: string;
  children?: string[];
}

/**
 * Symbol metadata containing additional information
 */
export interface SymbolMetadata {
  description?: string;
  parameters?: ParameterInfo[];
  returnType?: string;
  modifiers?: string[];
  annotations?: Annotation[];
  documentation?: string;
  complexity?: number;
  dependencies?: string[];
  usages?: UsageInfo[];
}

/**
 * Parameter information for functions and methods
 */
export interface ParameterInfo {
  name: string;
  type: string;
  optional: boolean;
  defaultValue?: string;
  description?: string;
}

/**
 * Annotation information
 */
export interface Annotation {
  type: string;
  value: string;
  position: Position;
}

/**
 * Usage information for symbols
 */
export interface UsageInfo {
  file: string;
  position: Position;
  context: string;
  type: SymbolKind;
}

// ============================================================================
// ANALYSIS TYPES
// ============================================================================

/**
 * Code analysis result
 */
export interface CodeAnalysis {
  id: string;
  code: string;
  language: string;
  symbols: SymbolInfo[];
  dependencies: DependencyInfo[];
  complexity: ComplexityMetrics;
  performance: PerformanceMetrics;
  security: SecurityMetrics;
  quality: QualityMetrics;
  timestamp: number;
  confidence: number;
  analysisTime: number;
}

/**
 * Symbol analysis result
 */
export interface SymbolAnalysis {
  symbol: SymbolInfo;
  analysis: CodeAnalysis;
  naturalLanguage: string;
  suggestions: CodeSuggestion[];
  actions: CodeAction[];
  relatedSymbols: SymbolInfo[];
  confidence: number;
  analysisTime: number;
}

/**
 * Dependency information
 */
export interface DependencyInfo {
  name: string;
  type: 'import' | 'export' | 'dependency' | 'devDependency';
  version?: string;
  path: string;
  used: boolean;
  usages: UsageInfo[];
}

/**
 * Complexity metrics
 */
export interface ComplexityMetrics {
  cyclomatic: number;
  cognitive: number;
  maintainability: number;
  nesting: number;
  lines: number;
  statements: number;
  functions: number;
  classes: number;
}

/**
 * Performance metrics
 */
export interface PerformanceMetrics {
  executionTime: number;
  memoryUsage: number;
  cpuUsage: number;
  networkRequests: number;
  databaseQueries: number;
  cacheHits: number;
  cacheMisses: number;
}

/**
 * Security metrics
 */
export interface SecurityMetrics {
  vulnerabilities: Vulnerability[];
  securityScore: number;
  riskLevel: RiskLevel;
  recommendations: SecurityRecommendation[];
}

/**
 * Quality metrics
 */
export interface QualityMetrics {
  testCoverage: number;
  codeDuplication: number;
  technicalDebt: number;
  maintainabilityIndex: number;
  reliability: number;
  efficiency: number;
  usability: number;
}

/**
 * Vulnerability information
 */
export interface Vulnerability {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  location: Position;
  fix?: string;
  references?: string[];
}

/**
 * Risk levels
 */
export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

/**
 * Security recommendation
 */
export interface SecurityRecommendation {
  type: string;
  priority: number;
  description: string;
  implementation: string;
  references?: string[];
}

// ============================================================================
// UI TYPES
// ============================================================================

/**
 * Dropdown information
 */
export interface DropdownInfo {
  id: string;
  symbol: SymbolInfo;
  position: Position;
  content: DropdownContent;
  actions: DropdownAction[];
  visible: boolean;
  timestamp: number;
}

/**
 * Dropdown content
 */
export interface DropdownContent {
  title: string;
  description: string;
  details: string[];
  examples: string[];
  related: RelatedInfo[];
  metadata: Record<string, any>;
}

/**
 * Dropdown action
 */
export interface DropdownAction {
  id: string;
  label: string;
  icon?: string;
  shortcut?: string;
  handler: () => void;
  enabled: boolean;
  category?: string;
}

/**
 * Context menu information
 */
export interface ContextMenuInfo {
  id: string;
  position: Position;
  symbol?: SymbolInfo;
  actions: ContextMenuAction[];
  groupedActions?: Record<string, ContextMenuAction[]>;
  visible: boolean;
  timestamp: number;
}

/**
 * Context menu action
 */
export interface ContextMenuAction {
  id: string;
  label: string;
  icon?: string;
  shortcut?: string;
  handler: () => void;
  enabled: boolean;
  category?: string;
  submenu?: ContextMenuAction[];
}

/**
 * Tooltip information
 */
export interface TooltipInfo {
  id: string;
  position: Position;
  symbol?: SymbolInfo;
  content: TooltipContent;
  visible: boolean;
  timestamp: number;
}

/**
 * Tooltip content
 */
export interface TooltipContent {
  title: string;
  description: string;
  type: string;
  value?: string;
  documentation?: string;
  metadata: Record<string, any>;
}

/**
 * Related information
 */
export interface RelatedInfo {
  type: 'symbol' | 'file' | 'documentation' | 'example';
  name: string;
  description: string;
  url?: string;
  position?: Position;
  metadata?: Record<string, any>;
}

// ============================================================================
// CONFIGURATION TYPES
// ============================================================================

/**
 * Main configuration interface
 */
export interface AdvancedMonacoConfiguration {
  dropdowns?: DropdownConfiguration;
  contextMenus?: ContextMenuConfiguration;
  tooltips?: TooltipConfiguration;
  intelligence?: IntelligenceConfiguration;
  aimos?: AIMOSConfiguration;
  performance?: PerformanceConfiguration;
  security?: SecurityConfiguration;
  theme?: ThemeConfiguration;
  editor?: monaco.editor.IStandaloneEditorConstructionOptions;
}

/**
 * Dropdown configuration
 */
export interface DropdownConfiguration {
  enabled: boolean;
  position: 'below' | 'above' | 'auto';
  maxWidth: number;
  maxHeight: number;
  animation: boolean;
  delay: number;
  timeout: number;
  autoHide: boolean;
  closeOnClickOutside: boolean;
  closeOnEscape: boolean;
}

/**
 * Context menu configuration
 */
export interface ContextMenuConfiguration {
  enabled: boolean;
  position: 'mouse' | 'symbol' | 'auto';
  maxItems: number;
  grouping: boolean;
  icons: boolean;
  shortcuts: boolean;
  autoHide: boolean;
  closeOnClickOutside: boolean;
  closeOnEscape: boolean;
}

/**
 * Tooltip configuration
 */
export interface TooltipConfiguration {
  enabled: boolean;
  position: 'mouse' | 'symbol' | 'auto';
  delay: number;
  timeout: number;
  maxWidth: number;
  animation: boolean;
  autoHide: boolean;
  closeOnClickOutside: boolean;
  closeOnEscape: boolean;
}

/**
 * Intelligence configuration
 */
export interface IntelligenceConfiguration {
  enabled: boolean;
  analysisDepth: 'shallow' | 'medium' | 'deep';
  cacheEnabled: boolean;
  cacheSize: number;
  cacheTimeout: number;
  aimosIntegration: boolean;
  naturalLanguage: boolean;
  suggestions: boolean;
  actions: boolean;
  realTimeAnalysis: boolean;
  backgroundAnalysis: boolean;
}

/**
 * AIM-OS integration configuration
 */
export interface AIMOSConfiguration {
  enabled: boolean;
  endpoints: {
    cmc?: string;
    hhni?: string;
    vif?: string;
    seg?: string;
    apoe?: string;
    iis?: string;
  };
  timeout: number;
  retries: number;
  cache: boolean;
  authentication?: {
    type: 'none' | 'api-key' | 'oauth' | 'jwt';
    credentials: Record<string, any>;
  };
}

/**
 * Performance configuration
 */
export interface PerformanceConfiguration {
  maxAnalysisTime: number;
  maxMemoryUsage: number;
  enableProfiling: boolean;
  enableMetrics: boolean;
  enableOptimizations: boolean;
  enableLazyLoading: boolean;
  enableProgressiveLoading: boolean;
  workerThreads: number;
  batchSize: number;
}

/**
 * Security configuration
 */
export interface SecurityConfiguration {
  enableSandboxing: boolean;
  maxCodeSize: number;
  enableValidation: boolean;
  enableEncryption: boolean;
  enableAccessControl: boolean;
  allowedDomains: string[];
  blockedDomains: string[];
  enableDataProtection: boolean;
  enableAuditLogging: boolean;
  enablePrivacyMode: boolean;
}

/**
 * Theme configuration
 */
export interface ThemeConfiguration {
  name: string;
  base: 'vs-dark' | 'vs-light' | 'hc-black' | 'hc-light';
  colors: Record<string, string>;
  tokenColors: monaco.editor.ITokenThemeRule[];
  customCSS?: string;
}

// ============================================================================
// EVENT TYPES
// ============================================================================

/**
 * Event listener type
 */
export type EventListener<T> = (event: T) => void;

/**
 * Event emitter interface
 */
export interface EventEmitter {
  on<T>(eventType: string, listener: EventListener<T>): void;
  off<T>(eventType: string, listener: EventListener<T>): void;
  emit<T>(eventType: string, event: T): void;
  once<T>(eventType: string, listener: EventListener<T>): void;
}

/**
 * Symbol events
 */
export interface SymbolDetectedEvent {
  type: 'symbol-detected';
  symbol: SymbolInfo;
  timestamp: number;
}

export interface SymbolUpdatedEvent {
  type: 'symbol-updated';
  symbol: SymbolInfo;
  timestamp: number;
}

/**
 * Dropdown events
 */
export interface DropdownOpenedEvent {
  type: 'dropdown-opened';
  dropdown: DropdownInfo;
  timestamp: number;
}

export interface DropdownClosedEvent {
  type: 'dropdown-closed';
  dropdown: DropdownInfo;
  timestamp: number;
}

/**
 * Context menu events
 */
export interface ContextMenuOpenedEvent {
  type: 'context-menu-opened';
  menu: ContextMenuInfo;
  timestamp: number;
}

export interface ContextMenuClosedEvent {
  type: 'context-menu-closed';
  menu: ContextMenuInfo;
  timestamp: number;
}

/**
 * Tooltip events
 */
export interface TooltipShownEvent {
  type: 'tooltip-shown';
  tooltip: TooltipInfo;
  timestamp: number;
}

export interface TooltipHiddenEvent {
  type: 'tooltip-hidden';
  tooltip: TooltipInfo;
  timestamp: number;
}

/**
 * Analysis events
 */
export interface AnalysisStartedEvent {
  type: 'analysis-started';
  symbol: SymbolInfo;
  timestamp: number;
}

export interface AnalysisCompletedEvent {
  type: 'analysis-completed';
  analysis: CodeAnalysis;
  timestamp: number;
}

export interface AnalysisFailedEvent {
  type: 'analysis-failed';
  error: Error;
  symbol: SymbolInfo;
  timestamp: number;
}

/**
 * Error events
 */
export interface ErrorEvent {
  type: 'error';
  error: Error;
  context: string;
  timestamp: number;
}

// ============================================================================
// SUGGESTION AND ACTION TYPES
// ============================================================================

/**
 * Code suggestion
 */
export interface CodeSuggestion {
  id: string;
  type: 'refactor' | 'optimize' | 'fix' | 'enhance' | 'document';
  title: string;
  description: string;
  implementation: string;
  confidence: number;
  priority: number;
  category: string;
  tags: string[];
}

/**
 * Code action
 */
export interface CodeAction {
  id: string;
  type: 'refactor' | 'optimize' | 'fix' | 'enhance' | 'document' | 'generate' | 'test';
  title: string;
  description: string;
  handler: () => void;
  enabled: boolean;
  confidence: number;
  priority: number;
  category: string;
  tags: string[];
}

// ============================================================================
// HOOK TYPES
// ============================================================================

/**
 * Advanced Monaco Editor hook options
 */
export interface UseAdvancedMonacoEditorOptions {
  configuration?: AdvancedMonacoConfiguration;
  onSymbolDetected?: (symbol: SymbolInfo) => void;
  onAnalysisComplete?: (analysis: CodeAnalysis) => void;
  onError?: (error: Error) => void;
  onDropdownOpened?: (dropdown: DropdownInfo) => void;
  onContextMenuOpened?: (menu: ContextMenuInfo) => void;
  onTooltipShown?: (tooltip: TooltipInfo) => void;
}

/**
 * Advanced Monaco Editor hook return type
 */
export interface UseAdvancedMonacoEditorReturn {
  editor: monaco.editor.IStandaloneCodeEditor | null;
  configuration: AdvancedMonacoConfiguration;
  setConfiguration: (config: AdvancedMonacoConfiguration) => void;
  analyzeCode: (code: string, language: string) => Promise<CodeAnalysis>;
  getSymbols: () => Promise<SymbolInfo[]>;
  showDropdown: (symbol: SymbolInfo) => Promise<void>;
  hideDropdown: () => void;
  showContextMenu: (position: Position, symbol?: SymbolInfo) => Promise<void>;
  hideContextMenu: () => void;
  showTooltip: (position: Position, symbol?: SymbolInfo) => Promise<void>;
  hideTooltip: () => void;
  destroy: () => void;
}

/**
 * Code analysis hook options
 */
export interface UseCodeAnalysisOptions {
  code: string;
  language: string;
  enabled?: boolean;
  onAnalysisComplete?: (analysis: CodeAnalysis) => void;
  onError?: (error: Error) => void;
}

/**
 * Code analysis hook return type
 */
export interface UseCodeAnalysisReturn {
  analysis: CodeAnalysis | null;
  loading: boolean;
  error: Error | null;
  analyze: () => Promise<void>;
  clearAnalysis: () => void;
}

/**
 * Symbol detection hook options
 */
export interface UseSymbolDetectionOptions {
  code: string;
  language: string;
  enabled?: boolean;
  onSymbolDetected?: (symbol: SymbolInfo) => void;
  onSymbolsUpdated?: (symbols: SymbolInfo[]) => void;
}

/**
 * Symbol detection hook return type
 */
export interface UseSymbolDetectionReturn {
  symbols: SymbolInfo[];
  loading: boolean;
  error: Error | null;
  detectSymbols: () => Promise<void>;
  clearSymbols: () => void;
}

// ============================================================================
// EXPORT ALL TYPES
// ============================================================================

export * from './CodeAnalysisTypes';
export * from './IntegrationTypes';
