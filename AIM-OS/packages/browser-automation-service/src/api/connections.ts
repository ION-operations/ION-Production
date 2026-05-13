/**
 * Connection Management API Endpoints
 * 
 * REST API endpoints for account and session management
 * Based on: BROWSER_AUTOMATION_PANEL_SPECIFICATION_T3.md
 */

import { Router, Request, Response } from 'express';
import { ConnectionManager } from '../services/connectionManager';
import { BrowserService } from '../services/browserService';
import {
  CredentialVaultService,
  VaultCredentialNotFoundError,
  VaultUsageLimitExceededError
} from '../services/credentialVaultService';
import {
  SaveAccountRequest,
  SaveAccountResponse,
  ListAccountsResponse,
  GetAccountResponse,
  LoadSessionRequest,
  LoadSessionResponse,
  SaveSessionRequest,
  SaveSessionResponse,
  VerifySessionRequest,
  VerifySessionResponse,
  UpdateCookiesRequest,
  UpdateCookiesResponse,
  SaveVaultCredentialRequest,
  SaveVaultCredentialResponse,
  UpdateVaultCredentialRequest,
  UpdateVaultCredentialResponse,
  ListVaultCredentialsResponse,
  GetVaultCredentialResponse,
  LinkVaultCredentialRequest,
  LinkVaultCredentialResponse,
  CheckVaultUsageRequest,
  CheckVaultUsageResponse,
  RecordVaultUsageRequest,
  RecordVaultUsageResponse
} from '../types/api';

export function createConnectionsRouter(
  connectionManager: ConnectionManager,
  browserService: BrowserService,
  credentialVaultService: CredentialVaultService
): Router {
  const router = Router();

  const handleVaultError = (error: unknown, res: Response): boolean => {
    if (error instanceof VaultCredentialNotFoundError) {
      res.status(404).json({
        success: false,
        error: error.message
      });
      return true;
    }

    if (error instanceof VaultUsageLimitExceededError) {
      res.status(429).json({
        success: false,
        error: error.message
      });
      return true;
    }

    return false;
  };

  /**
   * POST /api/connections/save
   * Save an account
   */
  router.post('/save', async (req: Request<{}, SaveAccountResponse, SaveAccountRequest>, res: Response<SaveAccountResponse>) => {
    try {
      const { provider, email, displayName, credentials, vaultCredentialId } = req.body;

      if (!provider) {
        return res.status(400).json({
          success: false,
          error: 'provider is required'
        });
      }

      const accountId = `account-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

      await connectionManager.saveAccount({
        id: accountId,
        provider,
        email,
        displayName,
        credentials,
        vaultCredentialId,
        createdAt: new Date()
      });

      res.json({
        success: true,
        accountId
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * GET /api/connections/list
   * List all accounts
   */
  router.get('/list', async (req: Request, res: Response<ListAccountsResponse>) => {
    try {
      const { provider } = req.query;

      const accounts = await connectionManager.listAccounts();

      // Filter by provider if specified
      const filteredAccounts = provider
        ? accounts.filter(acc => acc.provider === provider)
        : accounts;

      res.json({
        success: true,
        accounts: filteredAccounts.map(acc => ({
          id: acc.id,
          provider: acc.provider,
            email: acc.email,
            displayName: acc.displayName,
            vaultCredentialId: acc.vaultCredentialId,
            lastUsed: acc.lastUsed?.toISOString()
        }))
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * POST /api/connections/vault/save
   * Save encrypted vault credential (server-side)
   */
  router.post('/vault/save', async (req: Request<{}, SaveVaultCredentialResponse, SaveVaultCredentialRequest>, res: Response<SaveVaultCredentialResponse>) => {
    try {
      const { provider, label, secret, metadata } = req.body;

      if (!provider || !label || !secret || typeof secret !== 'object') {
        return res.status(400).json({
          success: false,
          error: 'provider, label, and secret are required'
        });
      }

      const vaultCredentialId = await credentialVaultService.createCredential({
        provider,
        label,
        secret,
        metadata
      });

      res.json({
        success: true,
        vaultCredentialId
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * GET /api/connections/vault/list
   * List vault credential summaries (no secret values)
   */
  router.get('/vault/list', async (req: Request, res: Response<ListVaultCredentialsResponse>) => {
    try {
      const { provider } = req.query;
      const credentials = await credentialVaultService.listCredentials(
        typeof provider === 'string' ? provider as any : undefined
      );

      res.json({
        success: true,
        credentials: credentials.map(item => ({
          id: item.id,
          provider: item.provider,
          label: item.label,
          usernameHint: item.usernameHint,
          createdAt: item.createdAt.toISOString(),
          updatedAt: item.updatedAt.toISOString(),
          metadata: item.metadata
        }))
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * GET /api/connections/vault/:id
   * Get vault credential summary (no secret value)
   */
  router.get('/vault/:id', async (req: Request<{ id: string }>, res: Response<GetVaultCredentialResponse>) => {
    try {
      const { id } = req.params;
      const credential = await credentialVaultService.getCredential(id);
      if (!credential) {
        return res.status(404).json({
          success: false,
          error: 'Vault credential not found'
        });
      }

      res.json({
        success: true,
        credential: {
          id: credential.id,
          provider: credential.provider,
          label: credential.label,
          usernameHint: credential.usernameHint,
          createdAt: credential.createdAt.toISOString(),
          updatedAt: credential.updatedAt.toISOString(),
          metadata: credential.metadata
        }
      });
    } catch (error) {
      if (handleVaultError(error, res)) {
        return;
      }
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * GET /api/connections/vault/:id/usage
   * Read current vault usage/limits state without consuming quota
   */
  router.get('/vault/:id/usage', async (req: Request<{ id: string }>, res: Response<CheckVaultUsageResponse>) => {
    try {
      const { id } = req.params;
      const usage = await credentialVaultService.getUsageState(id);
      return res.json({
        success: true,
        usage
      });
    } catch (error) {
      if (handleVaultError(error, res)) {
        return;
      }
      return res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * POST /api/connections/vault/:id/check-limit
   * Check projected usage impact without consuming quota
   */
  router.post('/vault/:id/check-limit', async (req: Request<{ id: string }, CheckVaultUsageResponse, CheckVaultUsageRequest>, res: Response<CheckVaultUsageResponse>) => {
    try {
      const { id } = req.params;
      const { estimatedCost = 0, callIncrement = 1 } = req.body || {};
      const usage = await credentialVaultService.checkUsageLimit(id, estimatedCost, callIncrement);
      return res.json({
        success: true,
        usage
      });
    } catch (error) {
      if (handleVaultError(error, res)) {
        return;
      }
      return res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * POST /api/connections/vault/:id/record-usage
   * Consume quota after a successful operation
   */
  router.post('/vault/:id/record-usage', async (req: Request<{ id: string }, RecordVaultUsageResponse, RecordVaultUsageRequest>, res: Response<RecordVaultUsageResponse>) => {
    try {
      const { id } = req.params;
      const { actualCost = 0, callIncrement = 1 } = req.body || {};
      const stats = await credentialVaultService.recordUsage(id, actualCost, callIncrement);
      return res.json({
        success: true,
        stats
      });
    } catch (error) {
      if (handleVaultError(error, res)) {
        return;
      }
      return res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * PUT /api/connections/vault/:id
   * Update vault credential label/secret/metadata
   */
  router.put('/vault/:id', async (req: Request<{ id: string }, UpdateVaultCredentialResponse, UpdateVaultCredentialRequest>, res: Response<UpdateVaultCredentialResponse>) => {
    try {
      const { id } = req.params;
      const { label, secret, metadata } = req.body;

      if (label === undefined && secret === undefined && metadata === undefined) {
        return res.status(400).json({
          success: false,
          error: 'At least one of label, secret, or metadata must be provided'
        });
      }

      await credentialVaultService.updateCredential(id, { label, secret, metadata });

      res.json({
        success: true,
        vaultCredentialId: id
      });
    } catch (error) {
      if (handleVaultError(error, res)) {
        return;
      }
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * DELETE /api/connections/vault/:id
   * Delete vault credential entry
   */
  router.delete('/vault/:id', async (req: Request<{ id: string }>, res: Response) => {
    try {
      const { id } = req.params;
      await credentialVaultService.deleteCredential(id);
      res.json({ success: true });
    } catch (error) {
      if (handleVaultError(error, res)) {
        return;
      }
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * GET /api/connections/:id
   * Get a specific account
   */
  router.get('/:id', async (req: Request<{ id: string }>, res: Response<GetAccountResponse>) => {
    try {
      const { id } = req.params;

      const account = await connectionManager.getAccount(id);

      if (!account) {
        return res.status(404).json({
          success: false,
          error: 'Account not found'
        });
      }

      res.json({
        success: true,
        account
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * POST /api/connections/:id/load-session
   * Load session into browser
   */
  router.post('/:id/load-session', async (req: Request<{ id: string }, LoadSessionResponse, LoadSessionRequest>, res: Response<LoadSessionResponse>) => {
    try {
      const { id } = req.params;
      const { browserId } = req.body;

      if (!browserId) {
        return res.status(400).json({
          success: false,
          error: 'browserId is required'
        });
      }

      await connectionManager.loadSession(id, browserId, browserService);

      res.json({
        success: true
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * POST /api/connections/:id/save-session
   * Save session cookies from active browser into account
   */
  router.post('/:id/save-session', async (req: Request<{ id: string }, SaveSessionResponse, SaveSessionRequest>, res: Response<SaveSessionResponse>) => {
    try {
      const { id } = req.params;
      const { browserId } = req.body;

      if (!browserId) {
        return res.status(400).json({
          success: false,
          error: 'browserId is required'
        });
      }

      await connectionManager.saveSession(id, browserId, browserService);

      res.json({
        success: true
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * POST /api/connections/:id/verify-session
   * Verify whether account appears logged in on current page context
   */
  router.post('/:id/verify-session', async (req: Request<{ id: string }, VerifySessionResponse, VerifySessionRequest>, res: Response<VerifySessionResponse>) => {
    try {
      const { id } = req.params;
      const { browserId } = req.body;

      if (!browserId) {
        return res.status(400).json({
          success: false,
          error: 'browserId is required'
        });
      }

      const sessionValid = await connectionManager.verifySession(id, browserId, browserService);

      res.json({
        success: true,
        sessionValid
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * POST /api/connections/:id/link-vault
   * Link account to server-side vault credential reference
   */
  router.post('/:id/link-vault', async (req: Request<{ id: string }, LinkVaultCredentialResponse, LinkVaultCredentialRequest>, res: Response<LinkVaultCredentialResponse>) => {
    try {
      const { id } = req.params;
      const { vaultCredentialId, clearInlineCredentials = true } = req.body;

      if (!vaultCredentialId) {
        return res.status(400).json({
          success: false,
          error: 'vaultCredentialId is required'
        });
      }

      const exists = await credentialVaultService.exists(vaultCredentialId);
      if (!exists) {
        return res.status(404).json({
          success: false,
          error: 'Vault credential not found'
        });
      }

      await connectionManager.linkVaultCredential(id, vaultCredentialId, clearInlineCredentials);
      return res.json({
        success: true,
        accountId: id,
        vaultCredentialId
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * POST /api/connections/:id/update-cookies
   * Update session cookies
   */
  router.post('/:id/update-cookies', async (req: Request<{ id: string }, UpdateCookiesResponse, UpdateCookiesRequest>, res: Response<UpdateCookiesResponse>) => {
    try {
      const { id } = req.params;
      const { cookies } = req.body;

      if (!cookies || !Array.isArray(cookies)) {
        return res.status(400).json({
          success: false,
          error: 'cookies array is required'
        });
      }

      await connectionManager.updateSessionCookies(id, cookies);

      res.json({
        success: true
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * DELETE /api/connections/:id
   * Delete an account
   */
  router.delete('/:id', async (req: Request<{ id: string }>, res: Response) => {
    try {
      const { id } = req.params;

      await connectionManager.deleteAccount(id);

      res.json({
        success: true
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  return router;
}

