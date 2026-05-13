/**
 * Validation Service
 * 
 * Provides comprehensive validation functionality for the Advanced Monaco Editor
 * including:
 * - Code validation
 * - Schema validation
 * - Input validation
 * - Output validation
 * - Data validation
 * - Format validation
 * - Business rule validation
 */

import { EventEmitter } from 'events';

export interface ValidationRule {
  id: string;
  name: string;
  description: string;
  type: 'required' | 'format' | 'length' | 'range' | 'pattern' | 'custom' | 'business';
  severity: 'error' | 'warning' | 'info';
  enabled: boolean;
  validator: (value: any, context?: any) => ValidationResult;
  dependencies?: string[];
  metadata?: Record<string, any>;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  suggestions: ValidationSuggestion[];
  metadata?: Record<string, any>;
}

export interface ValidationError {
  id: string;
  ruleId: string;
  message: string;
  field?: string;
  value?: any;
  expected?: any;
  actual?: any;
  severity: 'error' | 'warning' | 'info';
  line?: number;
  column?: number;
  context?: Record<string, any>;
}

export interface ValidationWarning {
  id: string;
  ruleId: string;
  message: string;
  field?: string;
  value?: any;
  suggestion?: string;
  line?: number;
  column?: number;
  context?: Record<string, any>;
}

export interface ValidationSuggestion {
  id: string;
  ruleId: string;
  message: string;
  field?: string;
  value?: any;
  suggestion?: string;
  line?: number;
  column?: number;
  context?: Record<string, any>;
}

export interface ValidationConfig {
  enableRealTimeValidation: boolean;
  enableBatchValidation: boolean;
  enableAsyncValidation: boolean;
  enableCaching: boolean;
  cacheSize: number;
  cacheTimeout: number;
  maxValidationTime: number;
  enableParallelValidation: boolean;
  maxParallelValidations: number;
  enableValidationProfiling: boolean;
  enableValidationMetrics: boolean;
  validationTimeout: number;
  retryAttempts: number;
  retryDelay: number;
}

export class ValidationService extends EventEmitter {
  private config: ValidationConfig;
  private rules: Map<string, ValidationRule> = new Map();
  private validationCache: Map<string, ValidationResult> = new Map();
  private validationMetrics: Map<string, number> = new Map();
  private validationQueue: Array<{ id: string; data: any; context?: any; resolve: Function; reject: Function }> = [];
  private isProcessing: boolean = false;

  constructor(config: Partial<ValidationConfig> = {}) {
    super();
    
    this.config = {
      enableRealTimeValidation: true,
      enableBatchValidation: true,
      enableAsyncValidation: true,
      enableCaching: true,
      cacheSize: 1000,
      cacheTimeout: 300000, // 5 minutes
      maxValidationTime: 5000, // 5 seconds
      enableParallelValidation: true,
      maxParallelValidations: 5,
      enableValidationProfiling: false,
      enableValidationMetrics: true,
      validationTimeout: 10000, // 10 seconds
      retryAttempts: 3,
      retryDelay: 1000,
      ...config
    };

    this.initializeDefaultRules();
  }

  private initializeDefaultRules(): void {
    // Required field validation
    this.addRule({
      id: 'required',
      name: 'Required Field',
      description: 'Validates that a field is not empty',
      type: 'required',
      severity: 'error',
      enabled: true,
      validator: (value: any) => {
        const isValid = value !== null && value !== undefined && value !== '';
        return {
          isValid,
          errors: isValid ? [] : [{
            id: 'required-error',
            ruleId: 'required',
            message: 'This field is required',
            severity: 'error'
          }],
          warnings: [],
          suggestions: []
        };
      }
    });

    // Email validation
    this.addRule({
      id: 'email',
      name: 'Email Format',
      description: 'Validates email format',
      type: 'format',
      severity: 'error',
      enabled: true,
      validator: (value: string) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const isValid = emailRegex.test(value);
        return {
          isValid,
          errors: isValid ? [] : [{
            id: 'email-error',
            ruleId: 'email',
            message: 'Invalid email format',
            severity: 'error'
          }],
          warnings: [],
          suggestions: isValid ? [] : [{
            id: 'email-suggestion',
            ruleId: 'email',
            message: 'Please enter a valid email address',
            suggestion: 'example@domain.com'
          }]
        };
      }
    });

    // URL validation
    this.addRule({
      id: 'url',
      name: 'URL Format',
      description: 'Validates URL format',
      type: 'format',
      severity: 'error',
      enabled: true,
      validator: (value: string) => {
        try {
          new URL(value);
          return {
            isValid: true,
            errors: [],
            warnings: [],
            suggestions: []
          };
        } catch {
          return {
            isValid: false,
            errors: [{
              id: 'url-error',
              ruleId: 'url',
              message: 'Invalid URL format',
              severity: 'error'
            }],
            warnings: [],
            suggestions: [{
              id: 'url-suggestion',
              ruleId: 'url',
              message: 'Please enter a valid URL',
              suggestion: 'https://example.com'
            }]
          };
        }
      }
    });

    // Length validation
    this.addRule({
      id: 'length',
      name: 'Length Validation',
      description: 'Validates string length',
      type: 'length',
      severity: 'error',
      enabled: true,
      validator: (value: string, context: { min?: number; max?: number }) => {
        const length = value.length;
        const min = context?.min || 0;
        const max = context?.max || Infinity;
        const isValid = length >= min && length <= max;
        
        const errors: ValidationError[] = [];
        if (length < min) {
          errors.push({
            id: 'length-min-error',
            ruleId: 'length',
            message: `Minimum length is ${min} characters`,
            severity: 'error'
          });
        }
        if (length > max) {
          errors.push({
            id: 'length-max-error',
            ruleId: 'length',
            message: `Maximum length is ${max} characters`,
            severity: 'error'
          });
        }

        return {
          isValid,
          errors,
          warnings: [],
          suggestions: []
        };
      }
    });

    // Range validation
    this.addRule({
      id: 'range',
      name: 'Range Validation',
      description: 'Validates numeric range',
      type: 'range',
      severity: 'error',
      enabled: true,
      validator: (value: number, context: { min?: number; max?: number }) => {
        const min = context?.min || -Infinity;
        const max = context?.max || Infinity;
        const isValid = value >= min && value <= max;
        
        const errors: ValidationError[] = [];
        if (value < min) {
          errors.push({
            id: 'range-min-error',
            ruleId: 'range',
            message: `Minimum value is ${min}`,
            severity: 'error'
          });
        }
        if (value > max) {
          errors.push({
            id: 'range-max-error',
            ruleId: 'range',
            message: `Maximum value is ${max}`,
            severity: 'error'
          });
        }

        return {
          isValid,
          errors,
          warnings: [],
          suggestions: []
        };
      }
    });

    // Pattern validation
    this.addRule({
      id: 'pattern',
      name: 'Pattern Validation',
      description: 'Validates against regex pattern',
      type: 'pattern',
      severity: 'error',
      enabled: true,
      validator: (value: string, context: { pattern: RegExp; message?: string }) => {
        const pattern = context?.pattern;
        const message = context?.message || 'Value does not match required pattern';
        const isValid = pattern.test(value);
        
        return {
          isValid,
          errors: isValid ? [] : [{
            id: 'pattern-error',
            ruleId: 'pattern',
            message,
            severity: 'error'
          }],
          warnings: [],
          suggestions: []
        };
      }
    });

    // Code validation
    this.addRule({
      id: 'code-syntax',
      name: 'Code Syntax',
      description: 'Validates code syntax',
      type: 'custom',
      severity: 'error',
      enabled: true,
      validator: (value: string, context: { language?: string }) => {
        // Simplified code validation
        const language = context?.language || 'javascript';
        const errors: ValidationError[] = [];
        const warnings: ValidationWarning[] = [];
        const suggestions: ValidationSuggestion[] = [];

        // Check for basic syntax issues
        if (language === 'javascript' || language === 'typescript') {
          // Check for unclosed brackets
          const openBrackets = (value.match(/\{/g) || []).length;
          const closeBrackets = (value.match(/\}/g) || []).length;
          if (openBrackets !== closeBrackets) {
            errors.push({
              id: 'bracket-mismatch',
              ruleId: 'code-syntax',
              message: 'Unclosed brackets detected',
              severity: 'error'
            });
          }

          // Check for unclosed parentheses
          const openParens = (value.match(/\(/g) || []).length;
          const closeParens = (value.match(/\)/g) || []).length;
          if (openParens !== closeParens) {
            errors.push({
              id: 'paren-mismatch',
              ruleId: 'code-syntax',
              message: 'Unclosed parentheses detected',
              severity: 'error'
            });
          }

          // Check for semicolons (warning)
          const lines = value.split('\n');
          for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            if (line && !line.endsWith(';') && !line.endsWith('{') && !line.endsWith('}') && !line.startsWith('//')) {
              warnings.push({
                id: 'missing-semicolon',
                ruleId: 'code-syntax',
                message: 'Consider adding semicolon',
                line: i + 1,
                suggestion: 'Add semicolon at end of line'
              });
            }
          }
        }

        return {
          isValid: errors.length === 0,
          errors,
          warnings,
          suggestions
        };
      }
    });
  }

  public addRule(rule: ValidationRule): void {
    this.rules.set(rule.id, rule);
    this.emit('ruleAdded', rule);
  }

  public removeRule(ruleId: string): boolean {
    const removed = this.rules.delete(ruleId);
    if (removed) {
      this.emit('ruleRemoved', ruleId);
    }
    return removed;
  }

  public getRule(ruleId: string): ValidationRule | undefined {
    return this.rules.get(ruleId);
  }

  public getAllRules(): ValidationRule[] {
    return Array.from(this.rules.values());
  }

  public validate(data: any, rules: string[] = [], context?: any): Promise<ValidationResult> {
    return new Promise((resolve, reject) => {
      const validationId = this.generateValidationId();
      
      // Check cache first
      if (this.config.enableCaching) {
        const cacheKey = this.generateCacheKey(data, rules, context);
        const cached = this.validationCache.get(cacheKey);
        if (cached) {
          resolve(cached);
          return;
        }
      }

      // Add to validation queue
      this.validationQueue.push({
        id: validationId,
        data,
        context,
        resolve,
        reject
      });

      // Process queue if not already processing
      if (!this.isProcessing) {
        this.processValidationQueue();
      }
    });
  }

  public validateSync(data: any, rules: string[] = [], context?: any): ValidationResult {
    const enabledRules = rules.length > 0 
      ? rules.map(id => this.rules.get(id)).filter(Boolean) as ValidationRule[]
      : Array.from(this.rules.values()).filter(rule => rule.enabled);

    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];
    const suggestions: ValidationSuggestion[] = [];

    for (const rule of enabledRules) {
      try {
        const result = rule.validator(data, context);
        errors.push(...result.errors);
        warnings.push(...result.warnings);
        suggestions.push(...result.suggestions);
      } catch (error) {
        errors.push({
          id: `rule-error-${rule.id}`,
          ruleId: rule.id,
          message: `Validation rule error: ${error}`,
          severity: 'error'
        });
      }
    }

    const validationResult: ValidationResult = {
      isValid: errors.length === 0,
      errors,
      warnings,
      suggestions
    };

    // Cache result
    if (this.config.enableCaching) {
      const cacheKey = this.generateCacheKey(data, rules, context);
      this.validationCache.set(cacheKey, validationResult);
    }

    return validationResult;
  }

  public validateBatch(dataArray: any[], rules: string[] = [], context?: any): Promise<ValidationResult[]> {
    if (!this.config.enableBatchValidation) {
      return Promise.all(dataArray.map(data => this.validate(data, rules, context)));
    }

    return new Promise((resolve, reject) => {
      const validationId = this.generateValidationId();
      
      // Process in parallel if enabled
      if (this.config.enableParallelValidation) {
        const promises = dataArray.map(data => this.validate(data, rules, context));
        Promise.all(promises)
          .then(resolve)
          .catch(reject);
      } else {
        // Process sequentially
        const results: ValidationResult[] = [];
        let index = 0;

        const processNext = () => {
          if (index >= dataArray.length) {
            resolve(results);
            return;
          }

          this.validate(dataArray[index], rules, context)
            .then(result => {
              results.push(result);
              index++;
              processNext();
            })
            .catch(reject);
        };

        processNext();
      }
    });
  }

  private async processValidationQueue(): Promise<void> {
    if (this.isProcessing || this.validationQueue.length === 0) {
      return;
    }

    this.isProcessing = true;

    while (this.validationQueue.length > 0) {
      const { id, data, context, resolve, reject } = this.validationQueue.shift()!;

      try {
        const result = await this.performValidation(data, context);
        resolve(result);
      } catch (error) {
        reject(error);
      }
    }

    this.isProcessing = false;
  }

  private async performValidation(data: any, context?: any): Promise<ValidationResult> {
    const startTime = Date.now();
    
    try {
      const result = this.validateSync(data, [], context);
      
      // Record metrics
      if (this.config.enableValidationMetrics) {
        const duration = Date.now() - startTime;
        this.validationMetrics.set('totalValidations', (this.validationMetrics.get('totalValidations') || 0) + 1);
        this.validationMetrics.set('totalValidationTime', (this.validationMetrics.get('totalValidationTime') || 0) + duration);
        this.validationMetrics.set('averageValidationTime', 
          (this.validationMetrics.get('totalValidationTime') || 0) / (this.validationMetrics.get('totalValidations') || 1)
        );
      }

      return result;
    } catch (error) {
      throw new Error(`Validation failed: ${error}`);
    }
  }

  private generateValidationId(): string {
    return `validation_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateCacheKey(data: any, rules: string[], context?: any): string {
    return JSON.stringify({ data, rules, context });
  }

  public clearCache(): void {
    this.validationCache.clear();
    this.emit('cacheCleared');
  }

  public getValidationMetrics(): Record<string, number> {
    return Object.fromEntries(this.validationMetrics);
  }

  public getValidationReport(): {
    totalValidations: number;
    averageValidationTime: number;
    cacheHitRate: number;
    errorRate: number;
    warningRate: number;
    mostCommonErrors: string[];
    mostCommonWarnings: string[];
  } {
    const totalValidations = this.validationMetrics.get('totalValidations') || 0;
    const averageValidationTime = this.validationMetrics.get('averageValidationTime') || 0;
    const cacheHits = this.validationMetrics.get('cacheHits') || 0;
    const cacheMisses = this.validationMetrics.get('cacheMisses') || 0;
    const totalCacheRequests = cacheHits + cacheMisses;
    const cacheHitRate = totalCacheRequests > 0 ? (cacheHits / totalCacheRequests) * 100 : 0;

    // This would be calculated from actual validation results
    const errorRate = 0;
    const warningRate = 0;
    const mostCommonErrors: string[] = [];
    const mostCommonWarnings: string[] = [];

    return {
      totalValidations,
      averageValidationTime,
      cacheHitRate,
      errorRate,
      warningRate,
      mostCommonErrors,
      mostCommonWarnings
    };
  }

  public destroy(): void {
    this.rules.clear();
    this.validationCache.clear();
    this.validationMetrics.clear();
    this.validationQueue = [];
    this.isProcessing = false;
    this.removeAllListeners();
  }
}
