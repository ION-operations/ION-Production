/**
 * Connection Manager
 * Manages connection to Extension Command Server
 */

import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface ConnectionConfig {
  commandServerUrl: string;
  daemonUrl: string;
  timeout: number;
}

const DEFAULT_CONFIG: ConnectionConfig = {
  commandServerUrl: 'http://localhost:5001', // Development - needs configurable
  daemonUrl: 'http://localhost:5000',
  timeout: 10000
};

class ConnectionManager {
  private config: ConnectionConfig;
  private isConnected: boolean = false;
  private lastCheck: Date | null = null;

  constructor() {
    this.config = DEFAULT_CONFIG;
    this.loadConfig();
  }

  async loadConfig(): Promise<void> {
    try {
      const saved = await AsyncStorage.getItem('connection_config');
      if (saved) {
        this.config = JSON.parse(saved);
      }
    } catch (error) {
      console.error('Failed to load connection config:', error);
    }
  }

  async saveConfig(config: Partial<ConnectionConfig>): Promise<void> {
    this.config = { ...this.config, ...config };
    try {
      await AsyncStorage.setItem('connection_config', JSON.stringify(this.config));
    } catch (error) {
      console.error('Failed to save connection config:', error);
    }
  }

  async checkConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.config.commandServerUrl}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(this.config.timeout)
      });
      
      this.isConnected = response.ok;
      this.lastCheck = new Date();
      return this.isConnected;
    } catch (error) {
      this.isConnected = false;
      return false;
    }
  }

  getCommandServerUrl(): string {
    return this.config.commandServerUrl;
  }

  getDaemonUrl(): string {
    return this.config.daemonUrl;
  }

  getConnectionStatus(): { connected: boolean; lastCheck: Date | null } {
    return {
      connected: this.isConnected,
      lastCheck: this.lastCheck
    };
  }

  // For mobile, we need to detect if we're on same network
  // This is a placeholder - production would use proper network detection
  async detectServerUrl(): Promise<string | null> {
    // Try localhost first (development)
    if (await this.checkConnection()) {
      return this.config.commandServerUrl;
    }
    
    // Future: Try network IP addresses
    // Future: Try discovered servers
    // Future: Try configured URLs
    
    return null;
  }
}

export const connectionManager = new ConnectionManager();

