/**
 * Browser Automation Service - Express Server
 * 
 * Main server file that sets up Express and all API routes
 */

import express, { Express } from 'express';
import cors from 'cors';
import type { Server as HttpServer } from 'http';
import { BrowserService } from './services/browserService';
import { ScriptEngine } from './services/scriptEngine';
import { ConnectionManager } from './services/connectionManager';
import { CredentialVaultService } from './services/credentialVaultService';
import { createBrowserRouter } from './api/browser';
import { createAutomationRouter } from './api/automation';
import { createScriptsRouter } from './api/scripts';
import { createConnectionsRouter } from './api/connections';
import { createMcpBridgeRouter } from './api/mcpBridge';

export interface ServerOptions {
  port?: number;
  accountsPath?: string;
  vaultPath?: string;
  scriptsPath?: string;
  encryptionKey?: string;
}

export class BrowserAutomationServer {
  private app: Express;
  private browserService: BrowserService;
  private scriptEngine: ScriptEngine;
  private connectionManager: ConnectionManager;
  private credentialVaultService: CredentialVaultService;
  private port: number;
  private httpServer: HttpServer | null = null;

  constructor(options: ServerOptions = {}) {
    this.port = options.port || 5002;
    this.app = express();

    // Initialize services
    this.browserService = new BrowserService();
    this.connectionManager = new ConnectionManager(options.accountsPath, options.encryptionKey);
    this.credentialVaultService = new CredentialVaultService(options.vaultPath, options.encryptionKey);
    this.scriptEngine = new ScriptEngine(this.browserService, this.connectionManager);

    // Middleware
    this.app.use(cors());
    this.app.use(express.json());
    this.app.use(express.urlencoded({ extended: true }));

    // Health check endpoint
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        services: {
          browser: 'running',
          scriptEngine: 'running',
          connectionManager: 'running'
        }
      });
    });

    // API routes
    this.app.use('/api/browser', createBrowserRouter(this.browserService));
    this.app.use('/api/automation', createAutomationRouter(this.scriptEngine, options.scriptsPath));
    this.app.use('/api/scripts', createScriptsRouter(options.scriptsPath));
    this.app.use('/api/connections', createConnectionsRouter(this.connectionManager, this.browserService, this.credentialVaultService));
    this.app.use('/api/bridge', createMcpBridgeRouter(this.browserService, this.connectionManager, this.credentialVaultService));

    // Error handling middleware
    this.app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
      console.error('Server error:', err);
      res.status(500).json({
        success: false,
        error: err.message || 'Internal server error'
      });
    });
  }

  /**
   * Start the server
   */
  async start(): Promise<void> {
    if (this.httpServer) {
      return;
    }

    return new Promise((resolve, reject) => {
      try {
        this.httpServer = this.app.listen(this.port, () => {
          console.log(`Browser Automation Service running on port ${this.port}`);
          console.log(`Health check: http://localhost:${this.port}/health`);
          console.log(`API base: http://localhost:${this.port}/api`);

          // Start browser instance cleanup interval (every 5 min, 30 min timeout)
          this.browserService.startCleanupInterval();

          resolve();
        });
        this.httpServer.on('error', reject);
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Stop the server and cleanup
   */
  async stop(): Promise<void> {
    // Stop cleanup interval
    this.browserService.stopCleanupInterval();
    // Close all browser instances
    await this.browserService.closeAllBrowsers();
    // Close HTTP listener so process can exit cleanly.
    if (this.httpServer) {
      await new Promise<void>((resolve, reject) => {
        this.httpServer?.close((error?: Error) => {
          if (error) {
            reject(error);
            return;
          }
          resolve();
        });
      });
      this.httpServer = null;
    }
    console.log('Browser Automation Service stopped');
  }

  /**
   * Get Express app (for testing)
   */
  getApp(): Express {
    return this.app;
  }
}

// Start server if run directly
if (require.main === module) {
  const server = new BrowserAutomationServer({
    port: parseInt(process.env.PORT || '5002'),
    encryptionKey: process.env.BROWSER_AUTOMATION_ENCRYPTION_KEY
  });

  server.start().catch(error => {
    console.error('Failed to start server:', error);
    process.exit(1);
  });

  // Graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\nShutting down...');
    await server.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('\nShutting down...');
    await server.stop();
    process.exit(0);
  });
}

