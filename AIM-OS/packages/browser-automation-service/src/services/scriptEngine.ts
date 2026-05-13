/**
 * Script Engine - Automation Script Execution
 * 
 * Executes JSON-based automation scripts with error recovery and progress tracking
 * Based on: BROWSER_AUTOMATION_PANEL_SPECIFICATION_T3.md
 */

import { BrowserService } from './browserService';
import { ConnectionManager } from './connectionManager';
import {
  AutomationScript,
  AutomationAction,
  ScriptResult,
  ActionResult,
  AutomationErrorCategory,
  RetryStrategy
} from '../types/automation';

export class ScriptEngine {
  private executions: Map<string, {
    browserId: string;
    script: AutomationScript;
    startTime: number;
    currentStep: number;
    totalSteps: number;
    status: 'running' | 'paused' | 'completed' | 'error';
    results: ActionResult[];
  }> = new Map();

  private readonly DEFAULT_RETRY_STRATEGY: RetryStrategy = {
    maxRetries: 3,
    initialDelay: 1000,      // 1 second
    maxDelay: 10000,         // 10 seconds
    backoffMultiplier: 2,    // Double each retry
    retryableErrors: [
      AutomationErrorCategory.TIMEOUT,
      AutomationErrorCategory.NETWORK,
      AutomationErrorCategory.ELEMENT_NOT_FOUND
    ]
  };

  constructor(
    private browserService: BrowserService,
    private connectionManager?: ConnectionManager // Optional - will be used when provided
  ) { }

  /**
   * Start script execution in background and return execution ID immediately.
   */
  startExecution(
    browserId: string,
    script: AutomationScript,
    variables?: Record<string, string>
  ): string {
    const executionId = this.createExecutionId();
    // Fire-and-forget execution so API can return early for polling.
    void this.executeScript(browserId, script, variables, executionId);
    return executionId;
  }

  private createExecutionId(): string {
    return `exec-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
  }

  /**
   * Execute an automation script
   */
  async executeScript(
    browserId: string,
    script: AutomationScript,
    variables?: Record<string, string>,
    providedExecutionId?: string
  ): Promise<ScriptResult> {
    const executionId = providedExecutionId || this.createExecutionId();
    const startTime = Date.now();
    const results: ActionResult[] = [];

    try {
      // Replace variables in script
      const processedScript = this.processVariables(script, variables || {});

      // Initialize execution tracking
      this.executions.set(executionId, {
        browserId,
        script: processedScript,
        startTime,
        currentStep: 0,
        totalSteps: processedScript.actions.length,
        status: 'running',
        results: []
      });

      // Load session if account specified
      if (this.connectionManager && script.provider && processedScript.variables?.accountId) {
        await this.connectionManager.loadSession(
          processedScript.variables.accountId,
          browserId,
          this.browserService
        );
      }

      // Execute each action
      for (let i = 0; i < processedScript.actions.length; i++) {
        const action = processedScript.actions[i];

        // Honor pause/stop requests before every action boundary.
        const runState = await this.waitForRunnableState(executionId);
        if (runState === 'stopped') {
          const stopError = new Error('Execution stopped by operator');
          const stopResult: ActionResult = {
            action,
            success: false,
            duration: 0,
            error: stopError
          };
          results.push(stopResult);
          const stoppedExecution = this.executions.get(executionId);
          if (stoppedExecution) {
            stoppedExecution.results.push(stopResult);
            stoppedExecution.status = 'error';
          }
          break;
        }

        const execution = this.executions.get(executionId);
        if (!execution) break;

        // Update execution status
        execution.currentStep = i + 1;
        execution.status = 'running';

        try {
          // Check condition if specified
          if (action.condition) {
            const conditionMet = await this.evaluateCondition(browserId, action.condition);
            if (!conditionMet) {
              const result: ActionResult = {
                action,
                success: false,
                duration: 0,
                error: new Error(`Condition not met: ${action.condition}`)
              };
              results.push(result);
              execution.results.push(result);
              continue;
            }
          }

          // Before delay
          if (action.beforeDelay) {
            await this.sleep(action.beforeDelay);
          }

          // Execute action with retry
          const actionStartTime = Date.now();
          const result = await this.executeActionWithRetry(browserId, action, executionId);
          const actionDuration = Date.now() - actionStartTime;

          const actionResult: ActionResult = {
            action,
            success: result.success,
            duration: actionDuration,
            error: result.error,
            screenshot: result.screenshot,
            extractedData: result.extractedData
          };

          results.push(actionResult);
          execution.results.push(actionResult);

          // After delay
          if (action.afterDelay) {
            await this.sleep(action.afterDelay);
          }

          // If action failed and no retry, stop execution
          if (!result.success && !action.retry) {
            execution.status = 'error';
            break;
          }

        } catch (error) {
          const actionResult: ActionResult = {
            action,
            success: false,
            duration: 0,
            error: error instanceof Error ? error : new Error(String(error))
          };

          results.push(actionResult);
          execution.results.push(actionResult);

          // Stop on error unless retry specified
          if (!action.retry) {
            execution.status = 'error';
            break;
          }
        }
      }

      // Extract output if specified
      const output: Record<string, any> = {};
      if (processedScript.output) {
        for (const [key, selector] of Object.entries(processedScript.output)) {
          try {
            output[key] = await this.browserService.extractData(browserId, selector);
          } catch (error) {
            this.log('WARN', `Failed to extract output for ${key}: ${error}`, { executionId, key, selector, error });
          }
        }
      }

      const duration = Date.now() - startTime;
      const success = results.every(r => r.success);

      const execution = this.executions.get(executionId);
      if (execution) {
        execution.status = success ? 'completed' : 'error';
      }

      this.log('SUCCESS', `Script execution ${success ? 'completed' : 'failed'}: ${script.name}`, {
        executionId,
        script: script.name,
        success,
        duration,
        totalActions: results.length
      });

      return {
        success,
        results,
        output,
        duration
      };

    } catch (error) {
      const execution = this.executions.get(executionId);
      if (execution) {
        execution.status = 'error';
      }

      this.log('ERROR', `Script execution error: ${error}`, {
        executionId,
        script: script.name,
        error
      });

      return {
        success: false,
        results,
        error: error instanceof Error ? error : new Error(String(error)),
        duration: Date.now() - startTime
      };
    }
  }

  private async waitForRunnableState(executionId: string): Promise<'running' | 'stopped'> {
    while (true) {
      const execution = this.executions.get(executionId);
      if (!execution) return 'stopped';
      if (execution.status === 'paused') {
        await this.sleep(150);
        continue;
      }
      if (execution.status === 'error') {
        return 'stopped';
      }
      return 'running';
    }
  }

  /**
   * Execute action with retry logic
   */
  private async executeActionWithRetry(
    browserId: string,
    action: AutomationAction,
    executionId: string,
    strategy: RetryStrategy = this.DEFAULT_RETRY_STRATEGY
  ): Promise<{ success: boolean; error?: Error; screenshot?: Buffer; extractedData?: any }> {
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= strategy.maxRetries; attempt++) {
      const runState = await this.waitForRunnableState(executionId);
      if (runState === 'stopped') {
        return {
          success: false,
          error: new Error('Execution stopped by operator')
        };
      }

      try {
        const result = await this.executeAction(browserId, action);

        if (result.success) {
          return result;
        }

        // Classify error
        const errorCategory = this.classifyError(result.error!);

        // Check if error is retryable
        if (!strategy.retryableErrors.includes(errorCategory)) {
          return result; // Don't retry non-retryable errors
        }

        // Retry if attempts remaining
        if (attempt < strategy.maxRetries) {
          const delay = Math.min(
            strategy.initialDelay * Math.pow(strategy.backoffMultiplier, attempt - 1),
            strategy.maxDelay
          );
          this.log('LOG', `Retrying action (attempt ${attempt + 1}/${strategy.maxRetries}) after ${delay}ms`, {
            executionId,
            action: action.type,
            attempt,
            delay
          });
          await this.sleep(delay);
          continue;
        }

        lastError = result.error!;
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));

        const errorCategory = this.classifyError(lastError);

        // Don't retry non-retryable errors
        if (!strategy.retryableErrors.includes(errorCategory)) {
          throw lastError;
        }

        // Retry if attempts remaining
        if (attempt < strategy.maxRetries) {
          const delay = Math.min(
            strategy.initialDelay * Math.pow(strategy.backoffMultiplier, attempt - 1),
            strategy.maxDelay
          );
          this.log('LOG', `Retrying action (attempt ${attempt + 1}/${strategy.maxRetries}) after ${delay}ms`, {
            executionId,
            action: action.type,
            attempt,
            delay
          });
          await this.sleep(delay);
          continue;
        }
      }
    }

    // All retries failed
    throw lastError || new Error('All retry attempts failed');
  }

  /**
   * Execute a single action
   */
  private async executeAction(
    browserId: string,
    action: AutomationAction
  ): Promise<{ success: boolean; error?: Error; screenshot?: Buffer; extractedData?: any }> {
    try {
      switch (action.type) {
        case 'navigate':
          if (!action.url) {
            throw new Error('Navigate action requires URL');
          }
          await this.browserService.navigateTo(browserId, action.url);
          return { success: true };

        case 'click':
          if (!action.selector) {
            throw new Error('Click action requires selector');
          }
          await this.browserService.click(browserId, action.selector);
          return { success: true };

        case 'type':
          if (!action.selector || !action.value) {
            throw new Error('Type action requires selector and value');
          }
          await this.browserService.type(
            browserId,
            action.selector,
            action.value,
            action.humanLike !== false
          );
          return { success: true };

        case 'wait':
          if (!action.selector) {
            throw new Error('Wait action requires selector');
          }
          await this.browserService.waitForElement(browserId, action.selector, action.timeout);
          return { success: true };

        case 'screenshot':
          const screenshot = await this.browserService.screenshot(browserId, {
            type: 'png',
            fullPage: false
          });
          return { success: true, screenshot };

        case 'extract':
          if (!action.selector) {
            throw new Error('Extract action requires selector');
          }
          const extractedData = await this.browserService.extractData(browserId, action.selector);
          return { success: true, extractedData };

        case 'scroll':
          await this.browserService.scroll(browserId, action.scrollAmount || 500);
          return { success: true };

        case 'hover':
          if (!action.selector) {
            throw new Error('Hover action requires selector');
          }
          await this.browserService.hover(browserId, action.selector);
          return { success: true };

        case 'upload':
          if (!action.selector || !action.filePath) {
            throw new Error('Upload action requires selector and filePath');
          }
          await this.browserService.uploadFile(browserId, action.selector, action.filePath);
          return { success: true };

        default:
          throw new Error(`Unknown action type: ${action.type}`);
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error : new Error(String(error))
      };
    }
  }

  /**
   * Process variables in script
   */
  private processVariables(
    script: AutomationScript,
    variables: Record<string, string>
  ): AutomationScript {
    const processed = JSON.parse(JSON.stringify(script)) as AutomationScript;

    // Replace variables in actions
    processed.actions = processed.actions.map((action: AutomationAction) => {
      if (action.value) {
        action.value = this.replaceVariables(action.value, variables);
      }
      if (action.url) {
        action.url = this.replaceVariables(action.url, variables);
      }
      if (action.filePath) {
        action.filePath = this.replaceVariables(action.filePath, variables);
      }
      return action;
    });

    // Merge variables
    processed.variables = { ...processed.variables, ...variables };

    return processed;
  }

  /**
   * Replace variables in text
   */
  private replaceVariables(text: string, variables: Record<string, string>): string {
    return text.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      return variables[key] || match;
    });
  }

  /**
   * Evaluate JavaScript condition
   */
  private async evaluateCondition(browserId: string, condition: string): Promise<boolean> {
    try {
      const instance = this.browserService.getInstance(browserId);
      return await instance.page.evaluate((cond: string) => {
        try {
          return eval(cond);
        } catch {
          return false;
        }
      }, condition);
    } catch (error) {
      this.log('WARN', `Condition evaluation failed: ${error}`, { browserId, condition, error });
      return false;
    }
  }

  /**
   * Classify error for retry strategy
   */
  private classifyError(error: Error): AutomationErrorCategory {
    const message = error.message.toLowerCase();

    if (message.includes('browser instance not found') || message.includes('browser not found')) {
      return AutomationErrorCategory.UNKNOWN;
    }

    if (message.includes('timeout') || message.includes('timed out')) {
      return AutomationErrorCategory.TIMEOUT;
    }

    if (message.includes('navigation') || message.includes('failed to navigate')) {
      return AutomationErrorCategory.NAVIGATION;
    }

    if (message.includes('element') || message.includes('selector') || message.includes('not found')) {
      return AutomationErrorCategory.ELEMENT_NOT_FOUND;
    }

    if (message.includes('network') || message.includes('connection')) {
      return AutomationErrorCategory.NETWORK;
    }

    if (message.includes('auth') || message.includes('login') || message.includes('session')) {
      return AutomationErrorCategory.AUTHENTICATION;
    }

    return AutomationErrorCategory.UNKNOWN;
  }

  /**
   * Get execution status
   */
  getExecutionStatus(executionId: string): {
    status: 'running' | 'paused' | 'completed' | 'error';
    currentStep: number;
    totalSteps: number;
    stepName?: string;
    progress: number;
    results?: Array<{
      action: AutomationAction;
      success: boolean;
      duration: number;
      error?: {
        message: string;
        category: AutomationErrorCategory;
      };
      hasScreenshot?: boolean;
      hasExtractedData?: boolean;
    }>;
  } | null {
    const execution = this.executions.get(executionId);
    if (!execution) {
      return null;
    }

    const currentAction = execution.script.actions[execution.currentStep - 1];
    const stepName = currentAction ? `${currentAction.type}${currentAction.selector ? `: ${currentAction.selector}` : ''}` : undefined;

    return {
      status: execution.status,
      currentStep: execution.currentStep,
      totalSteps: execution.totalSteps,
      stepName,
      progress: execution.totalSteps > 0 ? execution.currentStep / execution.totalSteps : 0,
      results: this.serializeActionResults(execution.results)
    };
  }

  private serializeActionResults(results: ActionResult[]): Array<{
    action: AutomationAction;
    success: boolean;
    duration: number;
    error?: {
      message: string;
      category: AutomationErrorCategory;
    };
    hasScreenshot?: boolean;
    hasExtractedData?: boolean;
  }> {
    return results.map((result) => ({
      action: result.action,
      success: result.success,
      duration: result.duration,
      error: result.error
        ? {
          message: result.error.message,
          category: this.classifyError(result.error)
        }
        : undefined,
      hasScreenshot: !!result.screenshot,
      hasExtractedData: result.extractedData !== undefined
    }));
  }

  /**
   * Pause execution
   */
  pauseExecution(executionId: string): void {
    const execution = this.executions.get(executionId);
    if (execution && execution.status === 'running') {
      execution.status = 'paused';
      this.log('LOG', `Execution paused: ${executionId}`, { executionId });
    }
  }

  /**
   * Resume execution
   */
  resumeExecution(executionId: string): void {
    const execution = this.executions.get(executionId);
    if (execution && execution.status === 'paused') {
      execution.status = 'running';
      this.log('LOG', `Execution resumed: ${executionId}`, { executionId });
    }
  }

  /**
   * Stop execution
   */
  stopExecution(executionId: string): void {
    const execution = this.executions.get(executionId);
    if (execution) {
      execution.status = 'error';
      this.log('LOG', `Execution stopped: ${executionId}`, { executionId });
    }
  }

  /**
   * Get aggregated execution metrics
   */
  getMetrics(): {
    totalExecutions: number;
    successRate: number;
    averageDuration: number;
    lastExecution?: string;
    errorCount: number;
  } {
    const executions = Array.from(this.executions.values());
    const completed = executions.filter(e => e.status === 'completed' || e.status === 'error');
    const totalExecutions = completed.length;
    const errorCount = completed.filter(e => e.status === 'error').length;
    const successCount = totalExecutions - errorCount;
    const successRate = totalExecutions > 0 ? successCount / totalExecutions : 0;

    // Calculate average duration from completed executions
    let totalDuration = 0;
    let lastExecution: string | undefined;
    for (const exec of completed) {
      const lastResult = exec.results[exec.results.length - 1];
      if (lastResult) {
        totalDuration += exec.results.reduce((sum, r) => sum + r.duration, 0);
      }
    }
    const averageDuration = totalExecutions > 0 ? totalDuration / totalExecutions / 1000 : 0; // in seconds

    // Find most recent execution
    if (completed.length > 0) {
      const sorted = completed.sort((a, b) => b.startTime - a.startTime);
      lastExecution = new Date(sorted[0].startTime).toISOString();
    }

    return {
      totalExecutions,
      successRate: Math.round(successRate * 100) / 100,
      averageDuration: Math.round(averageDuration * 100) / 100,
      lastExecution,
      errorCount
    };
  }

  /**
   * Sleep utility
   */
  private async sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
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

