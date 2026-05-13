/**
 * Browser Automation Service - Main Entry Point
 * 
 * Exports all public APIs and services
 */

export * from './types/automation';
export * from './types/api';

// Services
export { BrowserService } from './services/browserService';
export { ScriptEngine } from './services/scriptEngine';
export { ConnectionManager } from './services/connectionManager';
export { CredentialVaultService } from './services/credentialVaultService';

// Server
export { BrowserAutomationServer } from './server';
export type { ServerOptions } from './server';

