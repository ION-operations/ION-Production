/**
 * Advanced Monaco Editor - Code Analysis Types
 * 
 * This file contains type definitions for code analysis functionality.
 */

import { SymbolInfo, Position, Range } from './MonacoTypes';

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
 * Usage information
 */
export interface UsageInfo {
  file: string;
  position: Position;
  context: string;
  type: string;
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
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
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
 * Security recommendation
 */
export interface SecurityRecommendation {
  type: string;
  priority: number;
  description: string;
  implementation: string;
  references?: string[];
}

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
