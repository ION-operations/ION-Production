/**
 * Browser Service - Puppeteer/Playwright Integration
 * 
 * Manages browser instances and provides automation capabilities
 * Based on: BROWSER_AUTOMATION_PANEL_SPECIFICATION_T3.md
 */

import puppeteer, { Browser, Page, ScreenshotOptions } from 'puppeteer';
import { BrowserOptions, BrowserInstance, BrowserStatus, ScreenshotOptions as CustomScreenshotOptions } from '../types/automation';

interface ConsoleEvent {
  timestamp: string;
  type: string;
  text: string;
  location?: {
    url?: string;
    lineNumber?: number;
    columnNumber?: number;
  };
}

interface PageErrorEvent {
  timestamp: string;
  message: string;
  stack?: string;
}

interface RequestFailureEvent {
  timestamp: string;
  url: string;
  method: string;
  resourceType: string;
  errorText?: string;
}

interface HttpErrorEvent {
  timestamp: string;
  url: string;
  status: number;
  statusText: string;
  resourceType: string;
}

interface RuntimeDiagnosticsStore {
  totalResponses: number;
  lastUpdated: string;
  consoleEvents: ConsoleEvent[];
  pageErrors: PageErrorEvent[];
  requestFailures: RequestFailureEvent[];
  httpErrors: HttpErrorEvent[];
}

export class BrowserService {
  private instances: Map<string, BrowserInstance> = new Map();
  private runtimeDiagnostics: Map<string, RuntimeDiagnosticsStore> = new Map();

  /**
   * Launch a new browser instance
   */
  async launchBrowser(options: BrowserOptions): Promise<string> {
    const browserId = `browser-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

    try {
      const browser = await puppeteer.launch({
        headless: options.headless,
        defaultViewport: options.viewport,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-blink-features=AutomationControlled',
          '--disable-dev-shm-usage',
          ...(options.args || [])
        ]
      });

      const page = await browser.newPage();

      // Set user agent
      if (options.userAgent) {
        await page.setUserAgent(options.userAgent);
      } else {
        // Default user agent to avoid detection
        await page.setUserAgent(
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        );
      }

      // Anti-detection measures
      await page.evaluateOnNewDocument(() => {
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        });

        // Fake plugins
        Object.defineProperty(navigator, 'plugins', {
          get: () => [1, 2, 3, 4, 5]
        });

        // Fake languages
        Object.defineProperty(navigator, 'languages', {
          get: () => ['en-US', 'en']
        });

        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters: any) => (
          parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission } as PermissionStatus) :
            originalQuery(parameters)
        );
      });

      const instance: BrowserInstance = {
        browserId,
        browser: browser as any,
        page: page as any,
        status: 'idle',
        createdAt: new Date(),
        lastActivity: new Date()
      };

      this.instances.set(browserId, instance);
      this.initializeRuntimeDiagnostics(browserId);
      this.attachDiagnosticsListeners(browserId, page as any);

      // Log browser launch
      this.log('SUCCESS', `Browser launched: ${browserId}`, { browserId });

      return browserId;
    } catch (error) {
      this.log('ERROR', `Failed to launch browser: ${error}`, { error });
      throw new Error(`Failed to launch browser: ${error}`);
    }
  }

  /**
   * Navigate to a URL
   */
  async navigateTo(browserId: string, url: string): Promise<void> {
    const instance = this.getInstance(browserId);

    try {
      instance.status = 'navigating';
      instance.lastActivity = new Date();

      await instance.page.goto(url, {
        waitUntil: 'networkidle2',
        timeout: 30000
      });

      instance.status = 'idle';
      instance.lastActivity = new Date();

      this.log('SUCCESS', `Navigated to: ${url}`, { browserId, url });
    } catch (error) {
      instance.status = 'error';
      this.log('ERROR', `Navigation failed: ${error}`, { browserId, url, error });
      throw new Error(`Navigation failed: ${error}`);
    }
  }

  /**
   * Click an element
   */
  async click(browserId: string, selector: string): Promise<void> {
    const instance = this.getInstance(browserId);

    try {
      await instance.page.waitForSelector(selector, { timeout: 10000 });
      await instance.page.click(selector);
      instance.lastActivity = new Date();

      this.log('SUCCESS', `Clicked element: ${selector}`, { browserId, selector });
    } catch (error) {
      this.log('ERROR', `Click failed: ${error}`, { browserId, selector, error });
      throw new Error(`Click failed: ${error}`);
    }
  }

  /**
   * Type text into an element (with human-like delays)
   */
  async type(browserId: string, selector: string, text: string, humanLike: boolean = true): Promise<void> {
    const instance = this.getInstance(browserId);

    try {
      await instance.page.waitForSelector(selector, { timeout: 10000 });

      if (humanLike) {
        // Human-like typing with random delays
        await instance.page.type(selector, text, { delay: 50 + Math.random() * 50 });
      } else {
        await instance.page.type(selector, text);
      }

      instance.lastActivity = new Date();

      this.log('SUCCESS', `Typed text into: ${selector}`, { browserId, selector });
    } catch (error) {
      this.log('ERROR', `Type failed: ${error}`, { browserId, selector, error });
      throw new Error(`Type failed: ${error}`);
    }
  }

  /**
   * Wait for an element to appear
   */
  async waitForElement(browserId: string, selector: string, timeout?: number): Promise<void> {
    const instance = this.getInstance(browserId);

    try {
      await instance.page.waitForSelector(selector, { timeout: timeout || 10000 });
      instance.lastActivity = new Date();

      this.log('SUCCESS', `Element appeared: ${selector}`, { browserId, selector });
    } catch (error) {
      this.log('ERROR', `Wait for element failed: ${error}`, { browserId, selector, error });
      throw new Error(`Wait for element failed: ${error}`);
    }
  }

  /**
   * Capture screenshot
   */
  async screenshot(browserId: string, options?: CustomScreenshotOptions): Promise<Buffer> {
    const instance = this.getInstance(browserId);

    try {
      const screenshotOptions: ScreenshotOptions = {
        type: options?.type || 'png',
        fullPage: options?.fullPage || false
      };

      if (options?.quality && screenshotOptions.type === 'jpeg') {
        screenshotOptions.quality = options.quality;
      }

      if (options?.clip) {
        screenshotOptions.clip = options.clip;
      }

      const screenshot = await instance.page.screenshot(screenshotOptions) as Buffer;
      instance.lastActivity = new Date();

      this.log('SUCCESS', `Screenshot captured`, { browserId });
      return screenshot;
    } catch (error) {
      this.log('ERROR', `Screenshot failed: ${error}`, { browserId, error });
      throw new Error(`Screenshot failed: ${error}`);
    }
  }

  /**
   * Extract data from an element
   */
  async extractData(browserId: string, selector: string): Promise<any> {
    const instance = this.getInstance(browserId);

    try {
      const data = await instance.page.evaluate((sel: string) => {
        const element = document.querySelector(sel);
        if (!element) return null;

        return {
          text: element.textContent?.trim(),
          html: element.innerHTML,
          attributes: Array.from(element.attributes).reduce((acc, attr) => {
            acc[attr.name] = attr.value;
            return acc;
          }, {} as Record<string, string>),
          value: (element as HTMLInputElement).value
        };
      }, selector);

      instance.lastActivity = new Date();

      this.log('SUCCESS', `Data extracted from: ${selector}`, { browserId, selector });
      return data;
    } catch (error) {
      this.log('ERROR', `Extract data failed: ${error}`, { browserId, selector, error });
      throw new Error(`Extract data failed: ${error}`);
    }
  }

  /**
   * Scroll the page
   */
  async scroll(browserId: string, amount: number): Promise<void> {
    const instance = this.getInstance(browserId);

    try {
      await instance.page.evaluate((amt: number) => {
        window.scrollBy(0, amt);
      }, amount);

      instance.lastActivity = new Date();

      this.log('SUCCESS', `Scrolled: ${amount}px`, { browserId, amount });
    } catch (error) {
      this.log('ERROR', `Scroll failed: ${error}`, { browserId, error });
      throw new Error(`Scroll failed: ${error}`);
    }
  }

  /**
   * Hover over an element
   */
  async hover(browserId: string, selector: string): Promise<void> {
    const instance = this.getInstance(browserId);

    try {
      await instance.page.waitForSelector(selector, { timeout: 10000 });
      await instance.page.hover(selector);
      instance.lastActivity = new Date();

      this.log('SUCCESS', `Hovered over: ${selector}`, { browserId, selector });
    } catch (error) {
      this.log('ERROR', `Hover failed: ${error}`, { browserId, selector, error });
      throw new Error(`Hover failed: ${error}`);
    }
  }

  /**
   * Upload a file
   */
  async uploadFile(browserId: string, selector: string, filePath: string): Promise<void> {
    const instance = this.getInstance(browserId);

    try {
      const input = await instance.page.$(selector);
      if (!input) {
        throw new Error(`File input not found: ${selector}`);
      }

      await input.uploadFile(filePath);
      instance.lastActivity = new Date();

      this.log('SUCCESS', `File uploaded: ${filePath}`, { browserId, selector, filePath });
    } catch (error) {
      this.log('ERROR', `File upload failed: ${error}`, { browserId, selector, filePath, error });
      throw new Error(`File upload failed: ${error}`);
    }
  }

  /**
   * Get browser status
   */
  async getBrowserStatus(browserId: string): Promise<BrowserStatus> {
    const instance = this.getInstance(browserId);

    try {
      const url = instance.page.url();
      const title = await instance.page.title();

      return {
        browserId,
        status: instance.status,
        url,
        title,
        createdAt: instance.createdAt,
        lastActivity: instance.lastActivity
      };
    } catch (error) {
      this.log('ERROR', `Get status failed: ${error}`, { browserId, error });
      throw new Error(`Get status failed: ${error}`);
    }
  }

  /**
   * Get viewport URL (CDP devtools frontend or WebSocket endpoint)
   */
  async getViewportUrl(browserId: string): Promise<string | null> {
    const instance = this.getInstance(browserId);

    try {
      const wsEndpoint = instance.browser.wsEndpoint();
      // Optional template for teams that deploy an HTTP viewport proxy.
      // Example:
      //   BROWSER_AUTOMATION_VIEWPORT_HTTP_TEMPLATE=http://localhost:9223/view?ws={wsEndpoint}&id={browserId}
      const template = process.env.BROWSER_AUTOMATION_VIEWPORT_HTTP_TEMPLATE;
      if (template && /^https?:\/\//i.test(template)) {
        const viewportUrl = template
          .replace('{wsEndpoint}', encodeURIComponent(wsEndpoint))
          .replace('{browserId}', encodeURIComponent(browserId));

        this.log('SUCCESS', `Viewport URL resolved via template for: ${browserId}`, {
          browserId,
          viewportUrl
        });
        return viewportUrl;
      }

      // Default posture: no embeddable live viewport URL available.
      // Consumers should fall back to screenshot mode.
      this.log('LOG', `No embeddable viewport URL configured; use screenshot fallback`, {
        browserId
      });
      return null;
    } catch (error) {
      this.log('WARN', `Failed to get viewport URL: ${error}`, { browserId, error });
      return null;
    }
  }

  /**
   * Detect interactive elements on the current page
   */
  async detectElements(browserId: string, selector?: string): Promise<Array<{
    selector: string;
    xpath: string;
    text?: string;
    tag: string;
    attributes: Record<string, string>;
    bounds: { x: number; y: number; width: number; height: number };
    confidence: number;
  }>> {
    const instance = this.getInstance(browserId);

    try {
      const elements = await instance.page.evaluate((filterSelector?: string) => {
        // Target interactive elements
        const interactiveSelectors = filterSelector
          ? filterSelector
          : 'a, button, input, textarea, select, [role="button"], [role="link"], [role="textbox"], [contenteditable="true"], [tabindex]';

        const els = document.querySelectorAll(interactiveSelectors);
        const results: Array<{
          selector: string;
          xpath: string;
          text?: string;
          tag: string;
          attributes: Record<string, string>;
          bounds: { x: number; y: number; width: number; height: number };
          confidence: number;
        }> = [];

        els.forEach((el: Element) => {
          const rect = el.getBoundingClientRect();
          // Skip invisible elements
          if (rect.width === 0 || rect.height === 0) return;

          // Build a CSS selector
          let cssSelector = el.tagName.toLowerCase();
          if (el.id) {
            cssSelector = `#${el.id}`;
          } else if (el.className && typeof el.className === 'string') {
            const classes = el.className.trim().split(/\s+/).slice(0, 2).join('.');
            if (classes) cssSelector += `.${classes}`;
          }

          // Build XPath
          const getXPath = (element: Element): string => {
            if (element.id) return `//*[@id="${element.id}"]`;
            const parts: string[] = [];
            let current: Element | null = element;
            while (current && current.nodeType === Node.ELEMENT_NODE) {
              let count = 0;
              let sibling: Element | null = current.previousElementSibling;
              while (sibling) {
                if (sibling.tagName === current.tagName) count++;
                sibling = sibling.previousElementSibling;
              }
              parts.unshift(`${current.tagName.toLowerCase()}[${count + 1}]`);
              current = current.parentElement;
            }
            return '/' + parts.join('/');
          };

          // Gather attributes
          const attrs: Record<string, string> = {};
          for (const attr of Array.from(el.attributes)) {
            attrs[attr.name] = attr.value;
          }

          // Compute confidence based on specificity of selector
          let confidence = 0.5;
          if (el.id) confidence = 0.95;
          else if (el.getAttribute('data-testid')) confidence = 0.9;
          else if (el.getAttribute('name')) confidence = 0.85;
          else if (el.getAttribute('aria-label')) confidence = 0.8;
          else if (el.className) confidence = 0.7;

          results.push({
            selector: cssSelector,
            xpath: getXPath(el),
            text: el.textContent?.trim()?.substring(0, 100) || undefined,
            tag: el.tagName.toLowerCase(),
            attributes: attrs,
            bounds: {
              x: Math.round(rect.x),
              y: Math.round(rect.y),
              width: Math.round(rect.width),
              height: Math.round(rect.height)
            },
            confidence
          });
        });

        return results.slice(0, 100); // Cap at 100 elements
      }, selector);

      instance.lastActivity = new Date();
      this.log('SUCCESS', `Detected ${elements.length} elements`, { browserId });
      return elements;
    } catch (error) {
      this.log('ERROR', `Element detection failed: ${error}`, { browserId, error });
      throw new Error(`Element detection failed: ${error}`);
    }
  }

  /**
   * Close a browser instance
   */
  async closeBrowser(browserId: string): Promise<void> {
    const instance = this.getInstance(browserId);

    try {
      await instance.browser.close();
      this.instances.delete(browserId);
      this.runtimeDiagnostics.delete(browserId);

      this.log('SUCCESS', `Browser closed: ${browserId}`, { browserId });
    } catch (error) {
      this.log('ERROR', `Close browser failed: ${error}`, { browserId, error });
      throw new Error(`Close browser failed: ${error}`);
    }
  }

  /**
   * Get browser instance (internal)
   */
  getInstance(browserId: string): BrowserInstance {
    const instance = this.instances.get(browserId);
    if (!instance) {
      throw new Error(`Browser instance not found: ${browserId}`);
    }
    return instance;
  }

  /**
   * Get all browser instances
   */
  getAllInstances(): BrowserInstance[] {
    return Array.from(this.instances.values());
  }

  /**
   * Get runtime diagnostics captured from browser events.
   */
  getRuntimeDiagnostics(browserId: string): {
    totalResponses: number;
    lastUpdated: string;
    consoleEvents: ConsoleEvent[];
    pageErrors: PageErrorEvent[];
    requestFailures: RequestFailureEvent[];
    httpErrors: HttpErrorEvent[];
  } {
    const diagnostics = this.runtimeDiagnostics.get(browserId);
    if (!diagnostics) {
      throw new Error(`Runtime diagnostics not found: ${browserId}`);
    }

    return {
      totalResponses: diagnostics.totalResponses,
      lastUpdated: diagnostics.lastUpdated,
      consoleEvents: [...diagnostics.consoleEvents],
      pageErrors: [...diagnostics.pageErrors],
      requestFailures: [...diagnostics.requestFailures],
      httpErrors: [...diagnostics.httpErrors],
    };
  }

  /**
   * Close all browser instances
   */
  async closeAllBrowsers(): Promise<void> {
    const browserIds = Array.from(this.instances.keys());
    for (const browserId of browserIds) {
      try {
        await this.closeBrowser(browserId);
      } catch (error) {
        this.log('WARN', `Failed to close browser: ${browserId}`, { browserId, error });
      }
    }
  }

  /**
   * Cleanup stale browser instances (inactive for more than the timeout)
   * @param timeoutMs - Inactivity timeout in milliseconds (default: 30 minutes)
   */
  async cleanupStaleInstances(timeoutMs: number = 30 * 60 * 1000): Promise<string[]> {
    const now = Date.now();
    const staleIds: string[] = [];

    for (const [browserId, instance] of this.instances.entries()) {
      const inactiveMs = now - instance.lastActivity.getTime();
      if (inactiveMs > timeoutMs) {
        staleIds.push(browserId);
      }
    }

    for (const browserId of staleIds) {
      try {
        await this.closeBrowser(browserId);
        this.log('WARN', `Cleaned up stale browser instance: ${browserId}`, { browserId, reason: 'inactivity' });
      } catch (error) {
        // Force remove from map even if close fails
        this.instances.delete(browserId);
        this.runtimeDiagnostics.delete(browserId);
        this.log('ERROR', `Force-removed stale browser: ${browserId}`, { browserId, error });
      }
    }

    if (staleIds.length > 0) {
      this.log('LOG', `Stale instance cleanup: removed ${staleIds.length} instances`, { removed: staleIds });
    }

    return staleIds;
  }

  /**
   * Check if a browser instance is still alive (process connected)
   */
  async isInstanceAlive(browserId: string): Promise<boolean> {
    try {
      const instance = this.instances.get(browserId);
      if (!instance) return false;
      // Attempt to access browser — throws if disconnected
      const connected = instance.browser.isConnected();
      return connected;
    } catch {
      return false;
    }
  }

  /**
   * Start periodic cleanup of stale/dead instances
   */
  private cleanupIntervalId: NodeJS.Timeout | null = null;

  startCleanupInterval(intervalMs: number = 5 * 60 * 1000, timeoutMs: number = 30 * 60 * 1000): void {
    this.stopCleanupInterval();
    this.cleanupIntervalId = setInterval(async () => {
      // First remove dead instances
      for (const [browserId] of this.instances.entries()) {
        const alive = await this.isInstanceAlive(browserId);
        if (!alive) {
          this.instances.delete(browserId);
          this.runtimeDiagnostics.delete(browserId);
          this.log('WARN', `Removed dead browser instance: ${browserId}`, { browserId, reason: 'disconnected' });
        }
      }
      // Then clean up stale ones
      await this.cleanupStaleInstances(timeoutMs);
    }, intervalMs);
    this.log('LOG', `Browser cleanup interval started (every ${intervalMs / 1000}s, timeout ${timeoutMs / 1000}s)`, {});
  }

  stopCleanupInterval(): void {
    if (this.cleanupIntervalId) {
      clearInterval(this.cleanupIntervalId);
      this.cleanupIntervalId = null;
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

  private initializeRuntimeDiagnostics(browserId: string): void {
    this.runtimeDiagnostics.set(browserId, {
      totalResponses: 0,
      lastUpdated: new Date().toISOString(),
      consoleEvents: [],
      pageErrors: [],
      requestFailures: [],
      httpErrors: [],
    });
  }

  private updateDiagnosticsTimestamp(browserId: string): void {
    const diag = this.runtimeDiagnostics.get(browserId);
    if (diag) {
      diag.lastUpdated = new Date().toISOString();
    }
  }

  private pushLimited<T>(target: T[], item: T, maxSize: number): void {
    target.push(item);
    if (target.length > maxSize) {
      target.splice(0, target.length - maxSize);
    }
  }

  private attachDiagnosticsListeners(browserId: string, page: any): void {
    const getStore = (): RuntimeDiagnosticsStore | null => this.runtimeDiagnostics.get(browserId) || null;
    const trimText = (value: string, maxLen: number = 600): string => {
      if (!value) return value;
      return value.length > maxLen ? `${value.substring(0, maxLen)}...[truncated]` : value;
    };

    page.on('console', (msg: any) => {
      const store = getStore();
      if (!store) return;

      const location = typeof msg.location === 'function' ? msg.location() : undefined;
      this.pushLimited(store.consoleEvents, {
        timestamp: new Date().toISOString(),
        type: typeof msg.type === 'function' ? msg.type() : 'log',
        text: trimText(typeof msg.text === 'function' ? msg.text() : String(msg)),
        location: location && (location.url || location.lineNumber || location.columnNumber) ? {
          url: location.url,
          lineNumber: location.lineNumber,
          columnNumber: location.columnNumber,
        } : undefined,
      }, 250);
      this.updateDiagnosticsTimestamp(browserId);
    });

    page.on('pageerror', (err: any) => {
      const store = getStore();
      if (!store) return;

      this.pushLimited(store.pageErrors, {
        timestamp: new Date().toISOString(),
        message: trimText(err?.message || String(err)),
        stack: trimText(err?.stack || ''),
      }, 100);
      this.updateDiagnosticsTimestamp(browserId);
    });

    page.on('requestfailed', (request: any) => {
      const store = getStore();
      if (!store) return;

      this.pushLimited(store.requestFailures, {
        timestamp: new Date().toISOString(),
        url: request.url(),
        method: request.method(),
        resourceType: request.resourceType(),
        errorText: request.failure()?.errorText,
      }, 250);
      this.updateDiagnosticsTimestamp(browserId);
    });

    page.on('response', (response: any) => {
      const store = getStore();
      if (!store) return;

      store.totalResponses += 1;
      const status = response.status();
      if (status >= 400) {
        const request = response.request();
        this.pushLimited(store.httpErrors, {
          timestamp: new Date().toISOString(),
          url: response.url(),
          status,
          statusText: response.statusText(),
          resourceType: request?.resourceType?.() || 'unknown',
        }, 250);
      }
      this.updateDiagnosticsTimestamp(browserId);
    });
  }
}

