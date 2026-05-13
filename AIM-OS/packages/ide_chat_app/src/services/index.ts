/**
 * Services Index
 * 
 * Exports all services for the Lucid Orchestrator system.
 */

export { RealtimeCollaborationService } from './RealtimeCollaborationService';
export { AnalyticsService } from './AnalyticsService';
export { PerformanceService } from './PerformanceService';
export { TestingService } from './TestingService';

// Re-export types
export type { 
  CollaborationEvent, 
  CollaborationState, 
  User, 
  CollaborationMessage 
} from './RealtimeCollaborationService';

export type { 
  AnalyticsInsight, 
  TrendAnalysis, 
  PerformanceAnalysis, 
  QualityAnalysis 
} from './AnalyticsService';

export type { 
  PerformanceMetrics, 
  OptimizationStrategy, 
  CacheConfig, 
  VirtualizationConfig 
} from './PerformanceService';

export type { 
  TestCase, 
  TestSuite, 
  TestResult, 
  ValidationRule, 
  ValidationResult 
} from './TestingService';
