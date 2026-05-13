/**
 * Validation Service Tests
 * 
 * Comprehensive unit tests for the ValidationService class
 */

import { ValidationService, ValidationConfig, ValidationRule, ValidationResult, ValidationMetrics } from '../src/services/ValidationService';

describe('ValidationService', () => {
  let validationService: ValidationService;

  beforeEach(() => {
    validationService = new ValidationService({
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
      retryDelay: 1000
    });
  });

  afterEach(() => {
    validationService.destroy();
  });

  describe('Initialization', () => {
    it('should initialize with default configuration', () => {
      const defaultService = new ValidationService();
      expect(defaultService).toBeDefined();
      expect(defaultService.getConfig().enableRealTimeValidation).toBe(true);
      expect(defaultService.getConfig().enableBatchValidation).toBe(true);
      expect(defaultService.getConfig().enableAsyncValidation).toBe(true);
      expect(defaultService.getConfig().enableCaching).toBe(true);
      expect(defaultService.getConfig().enableParallelValidation).toBe(true);
      expect(defaultService.getConfig().enableValidationProfiling).toBe(false);
      expect(defaultService.getConfig().enableValidationMetrics).toBe(true);
      defaultService.destroy();
    });

    it('should initialize with custom configuration', () => {
      const customConfig: Partial<ValidationConfig> = {
        enableRealTimeValidation: false,
        enableBatchValidation: false,
        enableAsyncValidation: false,
        enableCaching: false,
        enableParallelValidation: false,
        enableValidationProfiling: true,
        enableValidationMetrics: false,
        cacheSize: 2000,
        cacheTimeout: 600000,
        maxValidationTime: 10000,
        maxParallelValidations: 10,
        validationTimeout: 20000,
        retryAttempts: 5,
        retryDelay: 2000
      };

      const customService = new ValidationService(customConfig);
      expect(customService.getConfig().enableRealTimeValidation).toBe(false);
      expect(customService.getConfig().enableBatchValidation).toBe(false);
      expect(customService.getConfig().enableAsyncValidation).toBe(false);
      expect(customService.getConfig().enableCaching).toBe(false);
      expect(customService.getConfig().enableParallelValidation).toBe(false);
      expect(customService.getConfig().enableValidationProfiling).toBe(true);
      expect(customService.getConfig().enableValidationMetrics).toBe(false);
      expect(customService.getConfig().cacheSize).toBe(2000);
      expect(customService.getConfig().cacheTimeout).toBe(600000);
      expect(customService.getConfig().maxValidationTime).toBe(10000);
      expect(customService.getConfig().maxParallelValidations).toBe(10);
      expect(customService.getConfig().validationTimeout).toBe(20000);
      expect(customService.getConfig().retryAttempts).toBe(5);
      expect(customService.getConfig().retryDelay).toBe(2000);
      customService.destroy();
    });
  });

  describe('Rule Management', () => {
    it('should add validation rule', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);
      const rules = validationService.getRules();
      expect(rules).toHaveLength(1);
      expect(rules[0].id).toBe('test-rule');
      expect(rules[0].name).toBe('Test Rule');
      expect(rules[0].description).toBe('A test validation rule');
      expect(rules[0].type).toBe('custom');
      expect(rules[0].priority).toBe('high');
      expect(rules[0].enabled).toBe(true);
      expect(rules[0].context).toBe('general');
      expect(rules[0].category).toBe('input');
      expect(rules[0].tags).toEqual(['test', 'validation']);
    });

    it('should remove validation rule', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);
      expect(validationService.getRules()).toHaveLength(1);

      validationService.removeRule('test-rule');
      expect(validationService.getRules()).toHaveLength(0);
    });

    it('should update validation rule', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);
      expect(validationService.getRules()).toHaveLength(1);

      const updatedRule = { ...rule, name: 'Updated Test Rule', priority: 'medium' as const };
      validationService.updateRule('test-rule', updatedRule);
      const rules = validationService.getRules();
      expect(rules[0].name).toBe('Updated Test Rule');
      expect(rules[0].priority).toBe('medium');
    });

    it('should get rules by context', () => {
      const rule1: ValidationRule = {
        id: 'test-rule-1',
        name: 'Test Rule 1',
        description: 'A test validation rule for code',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'code',
        category: 'input',
        tags: ['test', 'validation']
      };

      const rule2: ValidationRule = {
        id: 'test-rule-2',
        name: 'Test Rule 2',
        description: 'A test validation rule for general',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule1);
      validationService.addRule(rule2);

      const codeRules = validationService.getRulesByContext('code');
      expect(codeRules).toHaveLength(1);
      expect(codeRules[0].id).toBe('test-rule-1');

      const generalRules = validationService.getRulesByContext('general');
      expect(generalRules).toHaveLength(1);
      expect(generalRules[0].id).toBe('test-rule-2');
    });

    it('should get rules by category', () => {
      const rule1: ValidationRule = {
        id: 'test-rule-1',
        name: 'Test Rule 1',
        description: 'A test validation rule for input',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      const rule2: ValidationRule = {
        id: 'test-rule-2',
        name: 'Test Rule 2',
        description: 'A test validation rule for output',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'output',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule1);
      validationService.addRule(rule2);

      const inputRules = validationService.getRulesByCategory('input');
      expect(inputRules).toHaveLength(1);
      expect(inputRules[0].id).toBe('test-rule-1');

      const outputRules = validationService.getRulesByCategory('output');
      expect(outputRules).toHaveLength(1);
      expect(outputRules[0].id).toBe('test-rule-2');
    });

    it('should get rules by priority', () => {
      const rule1: ValidationRule = {
        id: 'test-rule-1',
        name: 'Test Rule 1',
        description: 'A test validation rule with high priority',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      const rule2: ValidationRule = {
        id: 'test-rule-2',
        name: 'Test Rule 2',
        description: 'A test validation rule with medium priority',
        type: 'custom',
        priority: 'medium',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule1);
      validationService.addRule(rule2);

      const highPriorityRules = validationService.getRulesByPriority('high');
      expect(highPriorityRules).toHaveLength(1);
      expect(highPriorityRules[0].id).toBe('test-rule-1');

      const mediumPriorityRules = validationService.getRulesByPriority('medium');
      expect(mediumPriorityRules).toHaveLength(1);
      expect(mediumPriorityRules[0].id).toBe('test-rule-2');
    });

    it('should get rules by tag', () => {
      const rule1: ValidationRule = {
        id: 'test-rule-1',
        name: 'Test Rule 1',
        description: 'A test validation rule with test tag',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      const rule2: ValidationRule = {
        id: 'test-rule-2',
        name: 'Test Rule 2',
        description: 'A test validation rule with validation tag',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['validation', 'security']
      };

      validationService.addRule(rule1);
      validationService.addRule(rule2);

      const testRules = validationService.getRulesByTag('test');
      expect(testRules).toHaveLength(1);
      expect(testRules[0].id).toBe('test-rule-1');

      const validationRules = validationService.getRulesByTag('validation');
      expect(validationRules).toHaveLength(2);

      const securityRules = validationService.getRulesByTag('security');
      expect(securityRules).toHaveLength(1);
      expect(securityRules[0].id).toBe('test-rule-2');
    });

    it('should enable/disable rule', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);
      expect(validationService.getRules()[0].enabled).toBe(true);

      validationService.disableRule('test-rule');
      expect(validationService.getRules()[0].enabled).toBe(false);

      validationService.enableRule('test-rule');
      expect(validationService.getRules()[0].enabled).toBe(true);
    });
  });

  describe('Validation', () => {
    it('should validate input with single rule', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const result = validationService.validate('test input', 'general');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule');
      expect(result.ruleResults[0].isValid).toBe(true);
      expect(result.ruleResults[0].errors).toHaveLength(0);
      expect(result.ruleResults[0].warnings).toHaveLength(0);
      expect(result.ruleResults[0].riskLevel).toBe('low');
    });

    it('should validate input with multiple rules', () => {
      const rule1: ValidationRule = {
        id: 'test-rule-1',
        name: 'Test Rule 1',
        description: 'A test validation rule for length',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      const rule2: ValidationRule = {
        id: 'test-rule-2',
        name: 'Test Rule 2',
        description: 'A test validation rule for format',
        type: 'custom',
        priority: 'medium',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.includes('test'),
            errors: !input.includes('test') ? [{ message: 'Input must contain "test"', code: 'MISSING_TEST' }] : [],
            warnings: [],
            riskLevel: 'medium'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule1);
      validationService.addRule(rule2);

      const result = validationService.validate('test input', 'general');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('medium');
      expect(result.ruleResults).toHaveLength(2);
      expect(result.ruleResults[0].ruleId).toBe('test-rule-1');
      expect(result.ruleResults[0].isValid).toBe(true);
      expect(result.ruleResults[1].ruleId).toBe('test-rule-2');
      expect(result.ruleResults[1].isValid).toBe(true);
    });

    it('should validate input with errors', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const result = validationService.validate('', 'general');
      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0].message).toBe('Input cannot be empty');
      expect(result.errors[0].code).toBe('EMPTY_INPUT');
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule');
      expect(result.ruleResults[0].isValid).toBe(false);
      expect(result.ruleResults[0].errors).toHaveLength(1);
      expect(result.ruleResults[0].warnings).toHaveLength(0);
      expect(result.ruleResults[0].riskLevel).toBe('low');
    });

    it('should validate input with warnings', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: true,
            errors: [],
            warnings: input.length < 10 ? [{ message: 'Input is too short', code: 'SHORT_INPUT' }] : [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const result = validationService.validate('short', 'general');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(1);
      expect(result.warnings[0].message).toBe('Input is too short');
      expect(result.warnings[0].code).toBe('SHORT_INPUT');
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule');
      expect(result.ruleResults[0].isValid).toBe(true);
      expect(result.ruleResults[0].errors).toHaveLength(0);
      expect(result.ruleResults[0].warnings).toHaveLength(1);
      expect(result.ruleResults[0].riskLevel).toBe('low');
    });

    it('should validate input with high risk level', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'high'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const result = validationService.validate('test input', 'general');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('high');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule');
      expect(result.ruleResults[0].isValid).toBe(true);
      expect(result.ruleResults[0].errors).toHaveLength(0);
      expect(result.ruleResults[0].warnings).toHaveLength(0);
      expect(result.ruleResults[0].riskLevel).toBe('high');
    });

    it('should validate input with critical risk level', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'critical'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const result = validationService.validate('test input', 'general');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('critical');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule');
      expect(result.ruleResults[0].isValid).toBe(true);
      expect(result.ruleResults[0].errors).toHaveLength(0);
      expect(result.ruleResults[0].warnings).toHaveLength(0);
      expect(result.ruleResults[0].riskLevel).toBe('critical');
    });

    it('should validate input with disabled rule', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: false,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const result = validationService.validate('', 'general');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(0);
    });

    it('should validate input with context filtering', () => {
      const rule1: ValidationRule = {
        id: 'test-rule-1',
        name: 'Test Rule 1',
        description: 'A test validation rule for code',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'code',
        category: 'input',
        tags: ['test', 'validation']
      };

      const rule2: ValidationRule = {
        id: 'test-rule-2',
        name: 'Test Rule 2',
        description: 'A test validation rule for general',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule1);
      validationService.addRule(rule2);

      const result = validationService.validate('test input', 'code');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule-1');
    });

    it('should validate input with category filtering', () => {
      const rule1: ValidationRule = {
        id: 'test-rule-1',
        name: 'Test Rule 1',
        description: 'A test validation rule for input',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      const rule2: ValidationRule = {
        id: 'test-rule-2',
        name: 'Test Rule 2',
        description: 'A test validation rule for output',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'output',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule1);
      validationService.addRule(rule2);

      const result = validationService.validate('test input', 'general', 'input');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule-1');
    });

    it('should validate input with priority filtering', () => {
      const rule1: ValidationRule = {
        id: 'test-rule-1',
        name: 'Test Rule 1',
        description: 'A test validation rule with high priority',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      const rule2: ValidationRule = {
        id: 'test-rule-2',
        name: 'Test Rule 2',
        description: 'A test validation rule with medium priority',
        type: 'custom',
        priority: 'medium',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule1);
      validationService.addRule(rule2);

      const result = validationService.validate('test input', 'general', 'input', 'high');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule-1');
    });

    it('should validate input with tag filtering', () => {
      const rule1: ValidationRule = {
        id: 'test-rule-1',
        name: 'Test Rule 1',
        description: 'A test validation rule with test tag',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      const rule2: ValidationRule = {
        id: 'test-rule-2',
        name: 'Test Rule 2',
        description: 'A test validation rule with validation tag',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['validation', 'security']
      };

      validationService.addRule(rule1);
      validationService.addRule(rule2);

      const result = validationService.validate('test input', 'general', 'input', 'high', ['test']);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule-1');
    });

    it('should validate input with custom options', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const result = validationService.validate('test input', 'general', 'input', 'high', ['test'], {
        enableCaching: false,
        enableParallelValidation: false,
        enableValidationProfiling: true,
        enableValidationMetrics: true,
        maxValidationTime: 1000,
        validationTimeout: 5000,
        retryAttempts: 1,
        retryDelay: 500
      });
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule');
    });
  });

  describe('Batch Validation', () => {
    it('should validate multiple inputs', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const inputs = ['test input 1', 'test input 2', 'test input 3'];
      const results = validationService.validateBatch(inputs, 'general');
      expect(results).toHaveLength(3);
      expect(results[0].isValid).toBe(true);
      expect(results[1].isValid).toBe(true);
      expect(results[2].isValid).toBe(true);
    });

    it('should validate multiple inputs with errors', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const inputs = ['test input 1', '', 'test input 3'];
      const results = validationService.validateBatch(inputs, 'general');
      expect(results).toHaveLength(3);
      expect(results[0].isValid).toBe(true);
      expect(results[1].isValid).toBe(false);
      expect(results[2].isValid).toBe(true);
    });

    it('should validate multiple inputs with custom options', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const inputs = ['test input 1', 'test input 2', 'test input 3'];
      const results = validationService.validateBatch(inputs, 'general', 'input', 'high', ['test'], {
        enableCaching: false,
        enableParallelValidation: false,
        enableValidationProfiling: true,
        enableValidationMetrics: true,
        maxValidationTime: 1000,
        validationTimeout: 5000,
        retryAttempts: 1,
        retryDelay: 500
      });
      expect(results).toHaveLength(3);
      expect(results[0].isValid).toBe(true);
      expect(results[1].isValid).toBe(true);
      expect(results[2].isValid).toBe(true);
    });
  });

  describe('Async Validation', () => {
    it('should validate input asynchronously', async () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'low'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const result = await validationService.validateAsync('test input', 'general');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule');
      expect(result.ruleResults[0].isValid).toBe(true);
      expect(result.ruleResults[0].errors).toHaveLength(0);
      expect(result.ruleResults[0].warnings).toHaveLength(0);
      expect(result.ruleResults[0].riskLevel).toBe('low');
    });

    it('should validate input asynchronously with errors', async () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'low'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const result = await validationService.validateAsync('', 'general');
      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0].message).toBe('Input cannot be empty');
      expect(result.errors[0].code).toBe('EMPTY_INPUT');
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule');
      expect(result.ruleResults[0].isValid).toBe(false);
      expect(result.ruleResults[0].errors).toHaveLength(1);
      expect(result.ruleResults[0].warnings).toHaveLength(0);
      expect(result.ruleResults[0].riskLevel).toBe('low');
    });

    it('should validate input asynchronously with warnings', async () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: true,
                errors: [],
                warnings: input.length < 10 ? [{ message: 'Input is too short', code: 'SHORT_INPUT' }] : [],
                riskLevel: 'low'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const result = await validationService.validateAsync('short', 'general');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(1);
      expect(result.warnings[0].message).toBe('Input is too short');
      expect(result.warnings[0].code).toBe('SHORT_INPUT');
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule');
      expect(result.ruleResults[0].isValid).toBe(true);
      expect(result.ruleResults[0].errors).toHaveLength(0);
      expect(result.ruleResults[0].warnings).toHaveLength(1);
      expect(result.ruleResults[0].riskLevel).toBe('low');
    });

    it('should validate input asynchronously with high risk level', async () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'high'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const result = await validationService.validateAsync('test input', 'general');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('high');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule');
      expect(result.ruleResults[0].isValid).toBe(true);
      expect(result.ruleResults[0].errors).toHaveLength(0);
      expect(result.ruleResults[0].warnings).toHaveLength(0);
      expect(result.ruleResults[0].riskLevel).toBe('high');
    });

    it('should validate input asynchronously with critical risk level', async () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'critical'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const result = await validationService.validateAsync('test input', 'general');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('critical');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule');
      expect(result.ruleResults[0].isValid).toBe(true);
      expect(result.ruleResults[0].errors).toHaveLength(0);
      expect(result.ruleResults[0].warnings).toHaveLength(0);
      expect(result.ruleResults[0].riskLevel).toBe('critical');
    });

    it('should validate input asynchronously with disabled rule', async () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: false,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'low'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const result = await validationService.validateAsync('', 'general');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(0);
    });

    it('should validate input asynchronously with context filtering', async () => {
      const rule1: ValidationRule = {
        id: 'test-rule-1',
        name: 'Test Rule 1',
        description: 'A test validation rule for code',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'low'
              });
            }, 100);
          });
        },
        context: 'code',
        category: 'input',
        tags: ['test', 'validation']
      };

      const rule2: ValidationRule = {
        id: 'test-rule-2',
        name: 'Test Rule 2',
        description: 'A test validation rule for general',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'low'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule1);
      validationService.addRule(rule2);

      const result = await validationService.validateAsync('test input', 'code');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule-1');
    });

    it('should validate input asynchronously with category filtering', async () => {
      const rule1: ValidationRule = {
        id: 'test-rule-1',
        name: 'Test Rule 1',
        description: 'A test validation rule for input',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'low'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      const rule2: ValidationRule = {
        id: 'test-rule-2',
        name: 'Test Rule 2',
        description: 'A test validation rule for output',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'low'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'output',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule1);
      validationService.addRule(rule2);

      const result = await validationService.validateAsync('test input', 'general', 'input');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule-1');
    });

    it('should validate input asynchronously with priority filtering', async () => {
      const rule1: ValidationRule = {
        id: 'test-rule-1',
        name: 'Test Rule 1',
        description: 'A test validation rule with high priority',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'low'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      const rule2: ValidationRule = {
        id: 'test-rule-2',
        name: 'Test Rule 2',
        description: 'A test validation rule with medium priority',
        type: 'custom',
        priority: 'medium',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'low'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule1);
      validationService.addRule(rule2);

      const result = await validationService.validateAsync('test input', 'general', 'input', 'high');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule-1');
    });

    it('should validate input asynchronously with tag filtering', async () => {
      const rule1: ValidationRule = {
        id: 'test-rule-1',
        name: 'Test Rule 1',
        description: 'A test validation rule with test tag',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'low'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      const rule2: ValidationRule = {
        id: 'test-rule-2',
        name: 'Test Rule 2',
        description: 'A test validation rule with validation tag',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'low'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'input',
        tags: ['validation', 'security']
      };

      validationService.addRule(rule1);
      validationService.addRule(rule2);

      const result = await validationService.validateAsync('test input', 'general', 'input', 'high', ['test']);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule-1');
    });

    it('should validate input asynchronously with custom options', async () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'low'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const result = await validationService.validateAsync('test input', 'general', 'input', 'high', ['test'], {
        enableCaching: false,
        enableParallelValidation: false,
        enableValidationProfiling: true,
        enableValidationMetrics: true,
        maxValidationTime: 1000,
        validationTimeout: 5000,
        retryAttempts: 1,
        retryDelay: 500
      });
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
      expect(result.ruleResults).toHaveLength(1);
      expect(result.ruleResults[0].ruleId).toBe('test-rule');
    });
  });

  describe('Batch Async Validation', () => {
    it('should validate multiple inputs asynchronously', async () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'low'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const inputs = ['test input 1', 'test input 2', 'test input 3'];
      const results = await validationService.validateBatchAsync(inputs, 'general');
      expect(results).toHaveLength(3);
      expect(results[0].isValid).toBe(true);
      expect(results[1].isValid).toBe(true);
      expect(results[2].isValid).toBe(true);
    });

    it('should validate multiple inputs asynchronously with errors', async () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'low'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const inputs = ['test input 1', '', 'test input 3'];
      const results = await validationService.validateBatchAsync(inputs, 'general');
      expect(results).toHaveLength(3);
      expect(results[0].isValid).toBe(true);
      expect(results[1].isValid).toBe(false);
      expect(results[2].isValid).toBe(true);
    });

    it('should validate multiple inputs asynchronously with custom options', async () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: async (input: string) => {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                isValid: input.length > 0,
                errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
                warnings: [],
                riskLevel: 'low'
              });
            }, 100);
          });
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      const inputs = ['test input 1', 'test input 2', 'test input 3'];
      const results = await validationService.validateBatchAsync(inputs, 'general', 'input', 'high', ['test'], {
        enableCaching: false,
        enableParallelValidation: false,
        enableValidationProfiling: true,
        enableValidationMetrics: true,
        maxValidationTime: 1000,
        validationTimeout: 5000,
        retryAttempts: 1,
        retryDelay: 500
      });
      expect(results).toHaveLength(3);
      expect(results[0].isValid).toBe(true);
      expect(results[1].isValid).toBe(true);
      expect(results[2].isValid).toBe(true);
    });
  });

  describe('Caching', () => {
    it('should cache validation results', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      // First validation
      const result1 = validationService.validate('test input', 'general');
      expect(result1.isValid).toBe(true);
      expect(result1.errors).toHaveLength(0);
      expect(result1.warnings).toHaveLength(0);
      expect(result1.riskLevel).toBe('low');
      expect(result1.ruleResults).toHaveLength(1);
      expect(result1.ruleResults[0].ruleId).toBe('test-rule');
      expect(result1.ruleResults[0].isValid).toBe(true);
      expect(result1.ruleResults[0].errors).toHaveLength(0);
      expect(result1.ruleResults[0].warnings).toHaveLength(0);
      expect(result1.ruleResults[0].riskLevel).toBe('low');

      // Second validation (should use cache)
      const result2 = validationService.validate('test input', 'general');
      expect(result2.isValid).toBe(true);
      expect(result2.errors).toHaveLength(0);
      expect(result2.warnings).toHaveLength(0);
      expect(result2.riskLevel).toBe('low');
      expect(result2.ruleResults).toHaveLength(1);
      expect(result2.ruleResults[0].ruleId).toBe('test-rule');
      expect(result2.ruleResults[0].isValid).toBe(true);
      expect(result2.ruleResults[0].errors).toHaveLength(0);
      expect(result2.ruleResults[0].warnings).toHaveLength(0);
      expect(result2.ruleResults[0].riskLevel).toBe('low');
    });

    it('should not cache validation results when disabled', () => {
      const service = new ValidationService({ enableCaching: false });
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      service.addRule(rule);

      // First validation
      const result1 = service.validate('test input', 'general');
      expect(result1.isValid).toBe(true);
      expect(result1.errors).toHaveLength(0);
      expect(result1.warnings).toHaveLength(0);
      expect(result1.riskLevel).toBe('low');
      expect(result1.ruleResults).toHaveLength(1);
      expect(result1.ruleResults[0].ruleId).toBe('test-rule');
      expect(result1.ruleResults[0].isValid).toBe(true);
      expect(result1.ruleResults[0].errors).toHaveLength(0);
      expect(result1.ruleResults[0].warnings).toHaveLength(0);
      expect(result1.ruleResults[0].riskLevel).toBe('low');

      // Second validation (should not use cache)
      const result2 = service.validate('test input', 'general');
      expect(result2.isValid).toBe(true);
      expect(result2.errors).toHaveLength(0);
      expect(result2.warnings).toHaveLength(0);
      expect(result2.riskLevel).toBe('low');
      expect(result2.ruleResults).toHaveLength(1);
      expect(result2.ruleResults[0].ruleId).toBe('test-rule');
      expect(result2.ruleResults[0].isValid).toBe(true);
      expect(result2.ruleResults[0].errors).toHaveLength(0);
      expect(result2.ruleResults[0].warnings).toHaveLength(0);
      expect(result2.ruleResults[0].riskLevel).toBe('low');

      service.destroy();
    });

    it('should clear cache', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      // First validation
      const result1 = validationService.validate('test input', 'general');
      expect(result1.isValid).toBe(true);
      expect(result1.errors).toHaveLength(0);
      expect(result1.warnings).toHaveLength(0);
      expect(result1.riskLevel).toBe('low');
      expect(result1.ruleResults).toHaveLength(1);
      expect(result1.ruleResults[0].ruleId).toBe('test-rule');
      expect(result1.ruleResults[0].isValid).toBe(true);
      expect(result1.ruleResults[0].errors).toHaveLength(0);
      expect(result1.ruleResults[0].warnings).toHaveLength(0);
      expect(result1.ruleResults[0].riskLevel).toBe('low');

      // Clear cache
      validationService.clearCache();

      // Second validation (should not use cache)
      const result2 = validationService.validate('test input', 'general');
      expect(result2.isValid).toBe(true);
      expect(result2.errors).toHaveLength(0);
      expect(result2.warnings).toHaveLength(0);
      expect(result2.riskLevel).toBe('low');
      expect(result2.ruleResults).toHaveLength(1);
      expect(result2.ruleResults[0].ruleId).toBe('test-rule');
      expect(result2.ruleResults[0].isValid).toBe(true);
      expect(result2.ruleResults[0].errors).toHaveLength(0);
      expect(result2.ruleResults[0].warnings).toHaveLength(0);
      expect(result2.ruleResults[0].riskLevel).toBe('low');
    });
  });

  describe('Metrics', () => {
    it('should collect validation metrics', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      // Perform some validations
      validationService.validate('test input 1', 'general');
      validationService.validate('test input 2', 'general');
      validationService.validate('', 'general');

      const metrics = validationService.getMetrics();
      expect(metrics).toBeDefined();
      expect(metrics.totalValidations).toBe(3);
      expect(metrics.successfulValidations).toBe(2);
      expect(metrics.failedValidations).toBe(1);
      expect(metrics.averageValidationTime).toBeGreaterThan(0);
      expect(metrics.validationTimeByRule).toBeDefined();
      expect(metrics.validationTimeByRule['test-rule']).toBeGreaterThan(0);
      expect(metrics.validationTimeByContext).toBeDefined();
      expect(metrics.validationTimeByContext['general']).toBeGreaterThan(0);
      expect(metrics.validationTimeByCategory).toBeDefined();
      expect(metrics.validationTimeByCategory['input']).toBeGreaterThan(0);
      expect(metrics.validationTimeByPriority).toBeDefined();
      expect(metrics.validationTimeByPriority['high']).toBeGreaterThan(0);
      expect(metrics.validationTimeByTag).toBeDefined();
      expect(metrics.validationTimeByTag['test']).toBeGreaterThan(0);
      expect(metrics.validationTimeByTag['validation']).toBeGreaterThan(0);
      expect(metrics.errorRate).toBeCloseTo(1/3, 2);
      expect(metrics.warningRate).toBe(0);
      expect(metrics.riskLevelDistribution).toBeDefined();
      expect(metrics.riskLevelDistribution['low']).toBe(2);
      expect(metrics.riskLevelDistribution['high']).toBe(0);
      expect(metrics.riskLevelDistribution['critical']).toBe(0);
      expect(metrics.cacheHitRate).toBeGreaterThanOrEqual(0);
      expect(metrics.cacheMissRate).toBeGreaterThanOrEqual(0);
      expect(metrics.parallelValidationRate).toBeGreaterThanOrEqual(0);
      expect(metrics.asyncValidationRate).toBeGreaterThanOrEqual(0);
      expect(metrics.retryRate).toBeGreaterThanOrEqual(0);
      expect(metrics.timeoutRate).toBeGreaterThanOrEqual(0);
      expect(metrics.profilingEnabled).toBe(false);
      expect(metrics.metricsEnabled).toBe(true);
      expect(metrics.lastUpdated).toBeDefined();
    });

    it('should reset metrics', () => {
      const rule: ValidationRule = {
        id: 'test-rule',
        name: 'Test Rule',
        description: 'A test validation rule',
        type: 'custom',
        priority: 'high',
        enabled: true,
        validator: (input: string) => {
          return {
            isValid: input.length > 0,
            errors: input.length === 0 ? [{ message: 'Input cannot be empty', code: 'EMPTY_INPUT' }] : [],
            warnings: [],
            riskLevel: 'low'
          };
        },
        context: 'general',
        category: 'input',
        tags: ['test', 'validation']
      };

      validationService.addRule(rule);

      // Perform some validations
      validationService.validate('test input 1', 'general');
      validationService.validate('test input 2', 'general');
      validationService.validate('', 'general');

      let metrics = validationService.getMetrics();
      expect(metrics.totalValidations).toBe(3);

      // Reset metrics
      validationService.resetMetrics();

      metrics = validationService.getMetrics();
      expect(metrics.totalValidations).toBe(0);
      expect(metrics.successfulValidations).toBe(0);
      expect(metrics.failedValidations).toBe(0);
      expect(metrics.averageValidationTime).toBe(0);
      expect(metrics.validationTimeByRule).toEqual({});
      expect(metrics.validationTimeByContext).toEqual({});
      expect(metrics.validationTimeByCategory).toEqual({});
      expect(metrics.validationTimeByPriority).toEqual({});
      expect(metrics.validationTimeByTag).toEqual({});
      expect(metrics.errorRate).toBe(0);
      expect(metrics.warningRate).toBe(0);
      expect(metrics.riskLevelDistribution).toEqual({});
      expect(metrics.cacheHitRate).toBe(0);
      expect(metrics.cacheMissRate).toBe(0);
      expect(metrics.parallelValidationRate).toBe(0);
      expect(metrics.asyncValidationRate).toBe(0);
      expect(metrics.retryRate).toBe(0);
      expect(metrics.timeoutRate).toBe(0);
      expect(metrics.profilingEnabled).toBe(false);
      expect(metrics.metricsEnabled).toBe(true);
      expect(metrics.lastUpdated).toBeDefined();
    });
  });

  describe('Configuration', () => {
    it('should update configuration', () => {
      const newConfig = {
        enableRealTimeValidation: false,
        enableBatchValidation: false,
        enableAsyncValidation: false,
        enableCaching: false,
        enableParallelValidation: false,
        enableValidationProfiling: true,
        enableValidationMetrics: false,
        cacheSize: 2000,
        cacheTimeout: 600000,
        maxValidationTime: 10000,
        maxParallelValidations: 10,
        validationTimeout: 20000,
        retryAttempts: 5,
        retryDelay: 2000
      };

      validationService.updateConfig(newConfig);
      const config = validationService.getConfig();
      expect(config.enableRealTimeValidation).toBe(false);
      expect(config.enableBatchValidation).toBe(false);
      expect(config.enableAsyncValidation).toBe(false);
      expect(config.enableCaching).toBe(false);
      expect(config.enableParallelValidation).toBe(false);
      expect(config.enableValidationProfiling).toBe(true);
      expect(config.enableValidationMetrics).toBe(false);
      expect(config.cacheSize).toBe(2000);
      expect(config.cacheTimeout).toBe(600000);
      expect(config.maxValidationTime).toBe(10000);
      expect(config.maxParallelValidations).toBe(10);
      expect(config.validationTimeout).toBe(20000);
      expect(config.retryAttempts).toBe(5);
      expect(config.retryDelay).toBe(2000);
    });

    it('should merge configuration properly', () => {
      const newConfig = {
        enableRealTimeValidation: false,
        enableBatchValidation: false,
        enableAsyncValidation: false,
        enableCaching: false,
        enableParallelValidation: false,
        enableValidationProfiling: true,
        enableValidationMetrics: false,
        cacheSize: 2000,
        cacheTimeout: 600000,
        maxValidationTime: 10000,
        maxParallelValidations: 10,
        validationTimeout: 20000,
        retryAttempts: 5,
        retryDelay: 2000
      };

      validationService.updateConfig(newConfig);
      const config = validationService.getConfig();
      expect(config.enableRealTimeValidation).toBe(false);
      expect(config.enableBatchValidation).toBe(false);
      expect(config.enableAsyncValidation).toBe(false);
      expect(config.enableCaching).toBe(false);
      expect(config.enableParallelValidation).toBe(false);
      expect(config.enableValidationProfiling).toBe(true);
      expect(config.enableValidationMetrics).toBe(false);
      expect(config.cacheSize).toBe(2000);
      expect(config.cacheTimeout).toBe(600000);
      expect(config.maxValidationTime).toBe(10000);
      expect(config.maxParallelValidations).toBe(10);
      expect(config.validationTimeout).toBe(20000);
      expect(config.retryAttempts).toBe(5);
      expect(config.retryDelay).toBe(2000);
    });
  });

  describe('Error Handling', () => {
    it('should handle validation errors gracefully', () => {
      // Mock validator to throw error
      const originalValidate = validationService.validate;
      validationService.validate = jest.fn().mockImplementation(() => {
        throw new Error('Validation error');
      });

      // Should not throw error
      expect(() => {
        validationService.validate('test input', 'general');
      }).not.toThrow();

      // Restore original method
      validationService.validate = originalValidate;
    });

    it('should handle async validation errors gracefully', async () => {
      // Mock validator to throw error
      const originalValidateAsync = validationService.validateAsync;
      validationService.validateAsync = jest.fn().mockImplementation(() => {
        throw new Error('Async validation error');
      });

      // Should not throw error
      await expect(validationService.validateAsync('test input', 'general')).rejects.toThrow('Async validation error');

      // Restore original method
      validationService.validateAsync = originalValidateAsync;
    });
  });

  describe('Cleanup', () => {
    it('should destroy service', () => {
      // Trigger some events
      validationService.validate('test input', 'general');
      validationService.clearCache();
      
      const metrics = validationService.getMetrics();
      expect(metrics.totalValidations).toBeGreaterThan(0);
      
      validationService.destroy();
      
      const metricsAfterDestroy = validationService.getMetrics();
      expect(metricsAfterDestroy.totalValidations).toBe(0);
    });
  });
});
