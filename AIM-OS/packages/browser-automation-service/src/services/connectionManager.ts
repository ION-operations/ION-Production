/**
 * Connection Manager - Account & Session Management
 * 
 * Manages accounts, sessions, and credentials with secure encryption
 * Based on: BROWSER_AUTOMATION_PANEL_SPECIFICATION_T3.md
 */

import { promises as fs } from 'fs';
import { join } from 'path';
import * as crypto from 'crypto';
import { BrowserService } from './browserService';
import { ChatAccount, Cookie, EncryptedCredentials } from '../types/automation';

export class ConnectionManager {
  private accounts: Map<string, ChatAccount> = new Map();
  private storagePath: string;
  private encryptionKey: Buffer;

  constructor(storagePath?: string, encryptionKey?: string) {
    // Default storage path
    this.storagePath = storagePath || join(process.cwd(), 'browser-automation-accounts.json');

    // Encryption key (should be from environment variable in production)
    const keyString = encryptionKey || process.env.BROWSER_AUTOMATION_ENCRYPTION_KEY || 'default-key-change-in-production-32-chars!!';
    this.encryptionKey = crypto.scryptSync(keyString, 'salt', 32);

    // Load accounts on initialization
    this.loadAccounts().catch(error => {
      console.error('Failed to load accounts:', error);
    });
  }

  /**
   * Save an account
   */
  async saveAccount(account: ChatAccount): Promise<void> {
    try {
      // Encrypt credentials if provided
      let encryptedCredentials: EncryptedCredentials | undefined;
      if (account.credentials) {
        encryptedCredentials = await this.encryptCredentials(account.credentials as any);
      }

      // Create account with encrypted credentials
      const accountToSave: ChatAccount = {
        ...account,
        credentials: encryptedCredentials,
        createdAt: account.createdAt || new Date(),
        lastUsed: account.lastUsed || new Date()
      };

      this.accounts.set(account.id, accountToSave);
      await this.persistAccounts();

      this.log('SUCCESS', `Account saved: ${account.id}`, { accountId: account.id, provider: account.provider });
    } catch (error) {
      this.log('ERROR', `Failed to save account: ${error}`, { accountId: account.id, error });
      throw new Error(`Failed to save account: ${error}`);
    }
  }

  /**
   * Get an account
   */
  async getAccount(accountId: string): Promise<ChatAccount | null> {
    const account = this.accounts.get(accountId);
    if (!account) {
      return null;
    }

    // Decrypt credentials if present
    if (account.credentials) {
      try {
        const decrypted = await this.decryptCredentials(account.credentials);
        return {
          ...account,
          credentials: decrypted as any
        };
      } catch (error) {
        this.log('WARN', `Failed to decrypt credentials for account: ${accountId}`, { accountId, error });
        return account; // Return account without decrypted credentials
      }
    }

    return account;
  }

  /**
   * List all accounts
   */
  async listAccounts(): Promise<ChatAccount[]> {
    return Array.from(this.accounts.values()).map(account => ({
      ...account,
      // Don't expose encrypted credentials in list
      credentials: undefined
    }));
  }

  /**
   * Delete an account
   */
  async deleteAccount(accountId: string): Promise<void> {
    if (!this.accounts.has(accountId)) {
      throw new Error(`Account not found: ${accountId}`);
    }

    this.accounts.delete(accountId);
    await this.persistAccounts();

    this.log('SUCCESS', `Account deleted: ${accountId}`, { accountId });
  }

  /**
   * Update an account
   */
  async updateAccount(accountId: string, updates: Partial<ChatAccount>): Promise<void> {
    const account = this.accounts.get(accountId);
    if (!account) {
      throw new Error(`Account not found: ${accountId}`);
    }

    // Encrypt credentials if provided
    let encryptedCredentials: EncryptedCredentials | undefined;
    if (updates.credentials) {
      encryptedCredentials = await this.encryptCredentials(updates.credentials as any);
    }

    const updatedAccount: ChatAccount = {
      ...account,
      ...updates,
      credentials: encryptedCredentials || account.credentials,
      id: accountId // Ensure ID doesn't change
    };

    this.accounts.set(accountId, updatedAccount);
    await this.persistAccounts();

    this.log('SUCCESS', `Account updated: ${accountId}`, { accountId });
  }

  /**
   * Link an account to a vault credential reference.
   * Optionally clears inline account credentials after linking.
   */
  async linkVaultCredential(accountId: string, vaultCredentialId: string, clearInlineCredentials: boolean = true): Promise<void> {
    const account = this.accounts.get(accountId);
    if (!account) {
      throw new Error(`Account not found: ${accountId}`);
    }

    const updated: ChatAccount = {
      ...account,
      vaultCredentialId,
      credentials: clearInlineCredentials ? undefined : account.credentials,
    };

    this.accounts.set(accountId, updated);
    await this.persistAccounts();

    this.log('SUCCESS', `Linked vault credential to account`, {
      accountId,
      vaultCredentialId,
      clearInlineCredentials
    });
  }

  /**
   * Remove vault credential link from an account.
   */
  async unlinkVaultCredential(accountId: string): Promise<void> {
    const account = this.accounts.get(accountId);
    if (!account) {
      throw new Error(`Account not found: ${accountId}`);
    }

    const updated: ChatAccount = {
      ...account,
      vaultCredentialId: undefined,
    };

    this.accounts.set(accountId, updated);
    await this.persistAccounts();

    this.log('SUCCESS', `Unlinked vault credential from account`, { accountId });
  }

  /**
   * Load session into browser
   */
  async loadSession(accountId: string, browserId: string, browserService: BrowserService): Promise<void> {
    const account = await this.getAccount(accountId);
    if (!account) {
      throw new Error(`Account not found: ${accountId}`);
    }

    try {
      const instance = browserService.getInstance(browserId);

      // Set cookies if available
      if (account.sessionCookies && account.sessionCookies.length > 0) {
        await instance.page.setCookie(...account.sessionCookies);
        this.log('SUCCESS', `Session cookies loaded for account: ${accountId}`, {
          accountId,
          browserId,
          cookieCount: account.sessionCookies.length
        });
      }

      // Update last used
      account.lastUsed = new Date();
      await this.updateAccount(accountId, { lastUsed: account.lastUsed });

    } catch (error) {
      this.log('ERROR', `Failed to load session: ${error}`, { accountId, browserId, error });
      throw new Error(`Failed to load session: ${error}`);
    }
  }

  /**
   * Save session from browser
   */
  async saveSession(accountId: string, browserId: string, browserService: BrowserService): Promise<void> {
    const account = await this.getAccount(accountId);
    if (!account) {
      throw new Error(`Account not found: ${accountId}`);
    }

    try {
      const instance = browserService.getInstance(browserId);

      // Get cookies from browser
      const cookies = await instance.page.cookies();

      // Update account with cookies
      await this.updateAccount(accountId, {
        sessionCookies: cookies,
        lastUsed: new Date()
      });

      this.log('SUCCESS', `Session saved for account: ${accountId}`, {
        accountId,
        browserId,
        cookieCount: cookies.length
      });
    } catch (error) {
      this.log('ERROR', `Failed to save session: ${error}`, { accountId, browserId, error });
      throw new Error(`Failed to save session: ${error}`);
    }
  }

  /**
   * Update session cookies
   */
  async updateSessionCookies(accountId: string, cookies: Cookie[]): Promise<void> {
    const account = this.accounts.get(accountId);
    if (!account) {
      throw new Error(`Account not found: ${accountId}`);
    }

    await this.updateAccount(accountId, {
      sessionCookies: cookies,
      lastUsed: new Date()
    });

    this.log('SUCCESS', `Session cookies updated for account: ${accountId}`, {
      accountId,
      cookieCount: cookies.length
    });
  }

  /**
   * Clear session
   */
  async clearSession(accountId: string): Promise<void> {
    await this.updateAccount(accountId, {
      sessionCookies: [],
      lastUsed: new Date()
    });

    this.log('SUCCESS', `Session cleared for account: ${accountId}`, { accountId });
  }

  /**
   * Encrypt credentials
   */
  private async encryptCredentials(credentials: any): Promise<EncryptedCredentials> {
    const algorithm = 'aes-256-gcm';
    const iv = crypto.randomBytes(16);
    const authTagLength = 16;

    const cipher = crypto.createCipheriv(algorithm, this.encryptionKey, iv) as crypto.CipherGCM;

    const encrypted = Buffer.concat([
      cipher.update(JSON.stringify(credentials), 'utf8'),
      cipher.final()
    ]);

    const authTag = cipher.getAuthTag();

    return {
      encrypted: encrypted.toString('base64'),
      algorithm,
      iv: iv.toString('base64'),
      authTag: authTag.toString('base64')
    };
  }

  /**
   * Decrypt credentials
   */
  private async decryptCredentials(encrypted: EncryptedCredentials): Promise<any> {
    try {
      const iv = Buffer.from(encrypted.iv, 'base64');
      const authTag = Buffer.from(encrypted.authTag || '', 'base64');
      const encryptedData = Buffer.from(encrypted.encrypted, 'base64');

      const decipher = crypto.createDecipheriv(encrypted.algorithm, this.encryptionKey, iv) as crypto.DecipherGCM;
      decipher.setAuthTag(authTag);

      const decrypted = Buffer.concat([
        decipher.update(encryptedData),
        decipher.final()
      ]);

      return JSON.parse(decrypted.toString('utf8'));
    } catch (error) {
      this.log('ERROR', `Failed to decrypt credentials: ${error}`, { error });
      throw new Error(`Failed to decrypt credentials: ${error}`);
    }
  }

  /**
   * Persist accounts to disk
   */
  private async persistAccounts(): Promise<void> {
    try {
      const accountsArray = Array.from(this.accounts.values());
      await fs.writeFile(this.storagePath, JSON.stringify(accountsArray, null, 2), 'utf8');
    } catch (error) {
      this.log('ERROR', `Failed to persist accounts: ${error}`, { error });
      throw new Error(`Failed to persist accounts: ${error}`);
    }
  }

  /**
   * Load accounts from disk
   */
  private async loadAccounts(): Promise<void> {
    try {
      const data = await fs.readFile(this.storagePath, 'utf8');
      const accountsArray = JSON.parse(data) as ChatAccount[];

      accountsArray.forEach(account => {
        // Convert date strings back to Date objects
        account.createdAt = new Date(account.createdAt as any);
        if (account.lastUsed) {
          account.lastUsed = new Date(account.lastUsed as any);
        }
        this.accounts.set(account.id, account);
      });

      this.log('SUCCESS', `Loaded ${accountsArray.length} accounts`, {
        accountCount: accountsArray.length
      });
    } catch (error: any) {
      if (error.code === 'ENOENT') {
        // File doesn't exist yet, start with empty map
        this.accounts = new Map();
        this.log('LOG', 'No accounts file found, starting with empty accounts', {});
      } else {
        this.log('ERROR', `Failed to load accounts: ${error}`, { error });
        throw error;
      }
    }
  }

  /**
   * Verify session is valid (check if logged in)
   * Supports: chatgpt, gemini, claude
   */
  async verifySession(accountId: string, browserId: string, browserService: BrowserService): Promise<boolean> {
    try {
      const instance = browserService.getInstance(browserId);

      const url = instance.page.url();
      const title = await instance.page.title();

      const account = await this.getAccount(accountId);
      if (!account) {
        return false;
      }

      this.log('LOG', `Verifying session for ${account.provider}`, { url, title });

        switch (account.provider) {
        case 'chatgpt': {
          // ChatGPT uses chatgpt.com domain (2024+)
          // Logged in: URL is chatgpt.com/*, not auth0 or login pages
          const isOnChatPage = (url.includes('chatgpt.com') || url.includes('chat.openai.com'))
            && !url.includes('auth') && !url.includes('login');
          if (isOnChatPage) {
            // Double-check with auth-aware DOM signals.
            try {
              const state = await instance.page.evaluate(() => {
                const pageText = (document.body?.innerText || '').toLowerCase();
                const actionTexts = Array.from(document.querySelectorAll('button, a'))
                  .map(el => (el.textContent || '').trim().toLowerCase())
                  .filter(Boolean);

                const hasInput = !!document.querySelector('textarea, [contenteditable="true"], #prompt-textarea');
                const hasProfileIndicator =
                  !!document.querySelector('[data-testid="profile-button"]') ||
                  !!document.querySelector('button[aria-label*="profile" i]') ||
                  !!document.querySelector('img[alt*="user" i]');
                const hasLoginCta = actionTexts.some(t =>
                  t === 'log in' || t === 'login' || t.startsWith('log in') || t.includes('sign up')
                );
                const hasLoggedOutHint = pageText.includes('get responses tailored to you');
                const hasHumanCheck =
                  pageText.includes('verify you are human') ||
                  pageText.includes('are you human') ||
                  pageText.includes('captcha') ||
                  pageText.includes('cf-turnstile') ||
                  pageText.includes('cloudflare');

                return {
                  hasInput,
                  hasProfileIndicator,
                  hasLoginCta,
                  hasLoggedOutHint,
                  hasHumanCheck,
                };
              });

              if (state.hasHumanCheck) return false;
              if (state.hasLoginCta || state.hasLoggedOutHint) return false;
              if (state.hasProfileIndicator) return true;
              return state.hasInput;
            } catch {
              return isOnChatPage;
            }
          }
          return false;
        }

        case 'gemini': {
          // Gemini: gemini.google.com — logged in when not on accounts.google.com
          const isOnGemini = url.includes('gemini.google.com');
          const isOnGoogleLogin = url.includes('accounts.google.com');
          if (isOnGemini && !isOnGoogleLogin) {
            // Double-check: look for chat input
            try {
              const hasInput = await instance.page.evaluate(() => {
                return !!document.querySelector('rich-textarea, .ql-editor, textarea, [contenteditable="true"]');
              });
              return hasInput;
            } catch {
              return isOnGemini;
            }
          }
          return false;
        }

        case 'claude': {
          // Claude: claude.ai — logged in when not redirected to login
          const isOnClaude = url.includes('claude.ai') && !url.includes('login');
          return isOnClaude && title.toLowerCase().includes('claude');
        }

        default:
          // Generic check
          return !url.includes('login') && !url.includes('auth') && !url.includes('signin');
      }
    } catch (error) {
      this.log('ERROR', `Failed to verify session: ${error}`, { accountId, browserId, error });
      return false;
    }
  }

  /**
   * Logging utility
   */
  private log(level: 'LOG' | 'SUCCESS' | 'WARN' | 'ERROR' | 'DEBUG', message: string, data?: any): void {
    const timestamp = Date.now();
    const logEntry = {
      timestamp,
      level,
      category: 'BROWSER_AUTOMATION' as const,
      message,
      data
    };

    // Console logging (can be replaced with proper logging service)
    const logMethod = level === 'ERROR' ? console.error :
      level === 'WARN' ? console.warn :
        level === 'DEBUG' ? console.debug :
          console.log;

    logMethod(`[${level}] ${message}`, data || '');

    // TODO: Integrate with AIM-OS logging system
    // AIMOSLogger.log('BROWSER_AUTOMATION', message, data);
  }
}

