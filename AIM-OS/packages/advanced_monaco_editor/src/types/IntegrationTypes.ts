/**
 * Advanced Monaco Editor - Integration Types
 * 
 * This file contains type definitions for AIM-OS integration.
 */

import { SymbolInfo, CodeAnalysis } from './MonacoTypes';

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
 * CMC (Context Memory Core) integration
 */
export interface CMCIntegration {
  storeMemory: (key: string, value: any, metadata?: any) => Promise<void>;
  retrieveMemory: (key: string) => Promise<any>;
  searchMemory: (query: string, limit?: number) => Promise<any[]>;
  deleteMemory: (key: string) => Promise<void>;
  listMemories: () => Promise<string[]>;
}

/**
 * HHNI (Hierarchical Hypergraph Neural Index) integration
 */
export interface HHNIIntegration {
  indexSymbol: (symbol: SymbolInfo) => Promise<void>;
  searchSymbols: (query: string, limit?: number) => Promise<SymbolInfo[]>;
  getRelatedSymbols: (symbolId: string, limit?: number) => Promise<SymbolInfo[]>;
  updateSymbol: (symbol: SymbolInfo) => Promise<void>;
  deleteSymbol: (symbolId: string) => Promise<void>;
}

/**
 * VIF (Verifiable Intelligence Framework) integration
 */
export interface VIFIntegration {
  trackConfidence: (task: string, confidence: number, reasoning: string) => Promise<void>;
  getConfidence: (task: string) => Promise<number>;
  validateOutput: (output: any, schema: any) => Promise<boolean>;
  getValidationResult: (output: any, schema: any) => Promise<ValidationResult>;
}

/**
 * SEG (Shared Evidence Graph) integration
 */
export interface SEGIntegration {
  synthesizeKnowledge: (topics: string[], depth?: string) => Promise<any>;
  getKnowledgeGraph: (topics: string[]) => Promise<any>;
  addEvidence: (evidence: any) => Promise<void>;
  getEvidence: (topic: string) => Promise<any[]>;
}

/**
 * APOE (AI-Powered Orchestration Engine) integration
 */
export interface APOEIntegration {
  createPlan: (goal: string, context: string) => Promise<any>;
  executePlan: (planId: string) => Promise<any>;
  updatePlan: (planId: string, updates: any) => Promise<void>;
  getPlanStatus: (planId: string) => Promise<any>;
}

/**
 * IIS (Intuitive Intelligence System) integration
 */
export interface IISIntegration {
  computeIntuition: (confidence: number, context: string) => Promise<number>;
  updateIntuitionWeights: (decisionId: string, label: number) => Promise<void>;
  getIntuitionTrace: (decisionId: string) => Promise<any[]>;
}

/**
 * Validation result
 */
export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  confidence: number;
  metadata: Record<string, any>;
}

/**
 * Integration service interface
 */
export interface IntegrationService {
  cmc: CMCIntegration;
  hhni: HHNIIntegration;
  vif: VIFIntegration;
  seg: SEGIntegration;
  apoe: APOEIntegration;
  iis: IISIntegration;
  configuration: AIMOSConfiguration;
  initialize: () => Promise<void>;
  destroy: () => Promise<void>;
  isConnected: () => boolean;
  getStatus: () => Promise<IntegrationStatus>;
}

/**
 * Integration status
 */
export interface IntegrationStatus {
  connected: boolean;
  services: {
    cmc: boolean;
    hhni: boolean;
    vif: boolean;
    seg: boolean;
    apoe: boolean;
    iis: boolean;
  };
  lastUpdate: number;
  errors: string[];
  warnings: string[];
}

/**
 * Integration event
 */
export interface IntegrationEvent {
  type: 'connected' | 'disconnected' | 'error' | 'warning' | 'status-update';
  service: string;
  message: string;
  timestamp: number;
  data?: any;
}

/**
 * Integration error
 */
export interface IntegrationError extends Error {
  service: string;
  code: string;
  details?: any;
  timestamp: number;
}

/**
 * Integration configuration update
 */
export interface IntegrationConfigurationUpdate {
  service: string;
  configuration: Partial<AIMOSConfiguration>;
  timestamp: number;
}
