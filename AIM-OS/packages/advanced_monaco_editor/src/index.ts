/**
 * Advanced Monaco Editor - Main Export
 * 
 * This file exports all the main components, services, and types
 * for the Advanced Monaco Editor package.
 */

// Main component
export { AdvancedMonacoEditor, type AdvancedMonacoEditorProps } from './components/AdvancedMonacoEditor';

// Services
export { SymbolDetectionService } from './services/SymbolDetectionService';
export { CodeAnalysisService } from './services/CodeAnalysisService';
export { AIMOSIntegrationService } from './services/AIMOSIntegrationService';

// Types
export * from './types/MonacoTypes';
export * from './types/CodeAnalysisTypes';
export * from './types/IntegrationTypes';

// Re-export Monaco Editor types for convenience
export type { IStandaloneCodeEditor, IStandaloneEditorConstructionOptions } from 'monaco-editor';
