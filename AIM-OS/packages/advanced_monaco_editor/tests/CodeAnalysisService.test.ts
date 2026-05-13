/**
 * Advanced Monaco Editor - Code Analysis Service Tests
 * 
 * This file contains tests for the CodeAnalysisService.
 */

import { CodeAnalysisService } from '../src/services/CodeAnalysisService';

describe('CodeAnalysisService', () => {
  let service: CodeAnalysisService;

  beforeEach(() => {
    service = new CodeAnalysisService();
  });

  afterEach(() => {
    service.destroy();
  });

  describe('analyzeCode', () => {
    it('should analyze TypeScript code', async () => {
      const code = 'function hello() { return "world"; }';
      const language = 'typescript';

      const analysis = await service.analyzeCode(code, language);

      expect(analysis).toBeDefined();
      expect(analysis.id).toBeDefined();
      expect(analysis.code).toBe(code);
      expect(analysis.language).toBe(language);
      expect(analysis.symbols).toBeDefined();
      expect(analysis.dependencies).toBeDefined();
      expect(analysis.complexity).toBeDefined();
      expect(analysis.performance).toBeDefined();
      expect(analysis.security).toBeDefined();
      expect(analysis.quality).toBeDefined();
      expect(analysis.timestamp).toBeDefined();
      expect(analysis.confidence).toBeDefined();
      expect(analysis.analysisTime).toBeDefined();
    });

    it('should analyze JavaScript code', async () => {
      const code = 'const hello = () => "world";';
      const language = 'javascript';

      const analysis = await service.analyzeCode(code, language);

      expect(analysis).toBeDefined();
      expect(analysis.language).toBe(language);
    });

    it('should analyze Python code', async () => {
      const code = 'def hello():\n    return "world"';
      const language = 'python';

      const analysis = await service.analyzeCode(code, language);

      expect(analysis).toBeDefined();
      expect(analysis.language).toBe(language);
    });

    it('should handle empty code', async () => {
      const code = '';
      const language = 'typescript';

      const analysis = await service.analyzeCode(code, language);

      expect(analysis).toBeDefined();
      expect(analysis.code).toBe('');
    });

    it('should handle code with comments', async () => {
      const code = '// This is a comment\nfunction hello() { return "world"; }';
      const language = 'typescript';

      const analysis = await service.analyzeCode(code, language);

      expect(analysis).toBeDefined();
      expect(analysis.complexity.lines).toBe(2);
    });

    it('should handle code with multiple functions', async () => {
      const code = `
        function hello() { return "world"; }
        function goodbye() { return "bye"; }
        function greet(name) { return \`Hello \${name}\`; }
      `;
      const language = 'typescript';

      const analysis = await service.analyzeCode(code, language);

      expect(analysis).toBeDefined();
      expect(analysis.complexity.functions).toBe(3);
    });

    it('should handle code with classes', async () => {
      const code = `
        class User {
          constructor(name) {
            this.name = name;
          }
          getName() {
            return this.name;
          }
        }
      `;
      const language = 'typescript';

      const analysis = await service.analyzeCode(code, language);

      expect(analysis).toBeDefined();
      expect(analysis.complexity.classes).toBe(1);
    });

    it('should handle code with interfaces', async () => {
      const code = `
        interface User {
          name: string;
          email: string;
        }
      `;
      const language = 'typescript';

      const analysis = await service.analyzeCode(code, language);

      expect(analysis).toBeDefined();
    });

    it('should handle code with imports', async () => {
      const code = `
        import { Component } from 'react';
        import * as utils from './utils';
        const data = require('./data.json');
      `;
      const language = 'typescript';

      const analysis = await service.analyzeCode(code, language);

      expect(analysis).toBeDefined();
      expect(analysis.dependencies.length).toBe(3);
    });

    it('should handle code with security vulnerabilities', async () => {
      const code = `
        function queryUser(id) {
          const query = "SELECT * FROM users WHERE id = " + id;
          return database.query(query);
        }
      `;
      const language = 'typescript';

      const analysis = await service.analyzeCode(code, language);

      expect(analysis).toBeDefined();
      expect(analysis.security.vulnerabilities.length).toBeGreaterThan(0);
      expect(analysis.security.vulnerabilities[0].type).toBe('sql-injection');
    });

    it('should handle code with XSS vulnerabilities', async () => {
      const code = `
        function displayMessage(message) {
          document.getElementById('output').innerHTML = message;
        }
      `;
      const language = 'typescript';

      const analysis = await service.analyzeCode(code, language);

      expect(analysis).toBeDefined();
      expect(analysis.security.vulnerabilities.length).toBeGreaterThan(0);
      expect(analysis.security.vulnerabilities[0].type).toBe('xss');
    });

    it('should handle code with hardcoded secrets', async () => {
      const code = `
        const apiKey = "sk-1234567890abcdef";
        const password = "admin123";
      `;
      const language = 'typescript';

      const analysis = await service.analyzeCode(code, language);

      expect(analysis).toBeDefined();
      expect(analysis.security.vulnerabilities.length).toBeGreaterThan(0);
      expect(analysis.security.vulnerabilities[0].type).toBe('hardcoded-secret');
    });

    it('should handle code with eval usage', async () => {
      const code = `
        function executeCode(code) {
          return eval(code);
        }
      `;
      const language = 'typescript';

      const analysis = await service.analyzeCode(code, language);

      expect(analysis).toBeDefined();
      expect(analysis.security.vulnerabilities.length).toBeGreaterThan(0);
      expect(analysis.security.vulnerabilities[0].type).toBe('code-injection');
    });

    it('should calculate complexity metrics correctly', async () => {
      const code = `
        function complexFunction(x, y) {
          if (x > 0) {
            if (y > 0) {
              return x + y;
            } else {
              return x - y;
            }
          } else {
            if (y > 0) {
              return y - x;
            } else {
              return -(x + y);
            }
          }
        }
      `;
      const language = 'typescript';

      const analysis = await service.analyzeCode(code, language);

      expect(analysis).toBeDefined();
      expect(analysis.complexity.cyclomatic).toBeGreaterThan(1);
      expect(analysis.complexity.cognitive).toBeGreaterThan(1);
      expect(analysis.complexity.nesting).toBeGreaterThan(0);
    });

    it('should handle errors gracefully', async () => {
      const code = 'function hello() { return "world"; }';
      const language = 'invalid-language';

      await expect(service.analyzeCode(code, language)).resolves.toBeDefined();
    });
  });

  describe('generateSuggestions', () => {
    it('should generate suggestions for high complexity code', async () => {
      const analysis = {
        id: 'test',
        code: 'function complex() { if (true) { if (true) { if (true) { return "complex"; } } } }',
        language: 'typescript',
        symbols: [],
        dependencies: [],
        complexity: { cyclomatic: 15, cognitive: 10, maintainability: 30, nesting: 3, lines: 1, statements: 1, functions: 1, classes: 0 },
        performance: { executionTime: 0, memoryUsage: 0, cpuUsage: 0, networkRequests: 0, databaseQueries: 0, cacheHits: 0, cacheMisses: 0 },
        security: { vulnerabilities: [], securityScore: 100, riskLevel: 'low', recommendations: [] },
        quality: { testCoverage: 0, codeDuplication: 0, technicalDebt: 0, maintainabilityIndex: 30, reliability: 100, efficiency: 100, usability: 100 },
        timestamp: Date.now(),
        confidence: 0.8,
        analysisTime: 100
      };

      const suggestions = await service.generateSuggestions(analysis);

      expect(suggestions).toBeDefined();
      expect(suggestions.length).toBeGreaterThan(0);
      expect(suggestions[0].type).toBe('refactor');
      expect(suggestions[0].title).toContain('complexity');
    });

    it('should generate suggestions for performance issues', async () => {
      const analysis = {
        id: 'test',
        code: 'function slow() { return "slow"; }',
        language: 'typescript',
        symbols: [],
        dependencies: [],
        complexity: { cyclomatic: 1, cognitive: 1, maintainability: 100, nesting: 0, lines: 1, statements: 1, functions: 1, classes: 0 },
        performance: { executionTime: 2000, memoryUsage: 0, cpuUsage: 0, networkRequests: 0, databaseQueries: 0, cacheHits: 0, cacheMisses: 0 },
        security: { vulnerabilities: [], securityScore: 100, riskLevel: 'low', recommendations: [] },
        quality: { testCoverage: 0, codeDuplication: 0, technicalDebt: 0, maintainabilityIndex: 100, reliability: 100, efficiency: 100, usability: 100 },
        timestamp: Date.now(),
        confidence: 0.8,
        analysisTime: 100
      };

      const suggestions = await service.generateSuggestions(analysis);

      expect(suggestions).toBeDefined();
      expect(suggestions.length).toBeGreaterThan(0);
      expect(suggestions[0].type).toBe('optimize');
      expect(suggestions[0].title).toContain('performance');
    });

    it('should generate suggestions for security issues', async () => {
      const analysis = {
        id: 'test',
        code: 'function insecure() { return eval("malicious code"); }',
        language: 'typescript',
        symbols: [],
        dependencies: [],
        complexity: { cyclomatic: 1, cognitive: 1, maintainability: 100, nesting: 0, lines: 1, statements: 1, functions: 1, classes: 0 },
        performance: { executionTime: 0, memoryUsage: 0, cpuUsage: 0, networkRequests: 0, databaseQueries: 0, cacheHits: 0, cacheMisses: 0 },
        security: { 
          vulnerabilities: [{ type: 'code-injection', severity: 'critical', description: 'Use of eval()', location: { line: 1, column: 0 } }], 
          securityScore: 50, 
          riskLevel: 'high', 
          recommendations: [] 
        },
        quality: { testCoverage: 0, codeDuplication: 0, technicalDebt: 0, maintainabilityIndex: 100, reliability: 100, efficiency: 100, usability: 100 },
        timestamp: Date.now(),
        confidence: 0.8,
        analysisTime: 100
      };

      const suggestions = await service.generateSuggestions(analysis);

      expect(suggestions).toBeDefined();
      expect(suggestions.length).toBeGreaterThan(0);
      expect(suggestions[0].type).toBe('fix');
      expect(suggestions[0].title).toContain('security');
    });

    it('should generate suggestions for documentation', async () => {
      const analysis = {
        id: 'test',
        code: 'function undocumented() { return "no docs"; }',
        language: 'typescript',
        symbols: [],
        dependencies: [],
        complexity: { cyclomatic: 1, cognitive: 1, maintainability: 100, nesting: 0, lines: 1, statements: 1, functions: 1, classes: 0 },
        performance: { executionTime: 0, memoryUsage: 0, cpuUsage: 0, networkRequests: 0, databaseQueries: 0, cacheHits: 0, cacheMisses: 0 },
        security: { vulnerabilities: [], securityScore: 100, riskLevel: 'low', recommendations: [] },
        quality: { testCoverage: 0, codeDuplication: 0, technicalDebt: 0, maintainabilityIndex: 30, reliability: 100, efficiency: 100, usability: 100 },
        timestamp: Date.now(),
        confidence: 0.8,
        analysisTime: 100
      };

      const suggestions = await service.generateSuggestions(analysis);

      expect(suggestions).toBeDefined();
      expect(suggestions.length).toBeGreaterThan(0);
      expect(suggestions[0].type).toBe('document');
      expect(suggestions[0].title).toContain('documentation');
    });
  });

  describe('generateActions', () => {
    it('should generate actions for any analysis', async () => {
      const analysis = {
        id: 'test',
        code: 'function test() { return "test"; }',
        language: 'typescript',
        symbols: [],
        dependencies: [],
        complexity: { cyclomatic: 1, cognitive: 1, maintainability: 100, nesting: 0, lines: 1, statements: 1, functions: 1, classes: 0 },
        performance: { executionTime: 0, memoryUsage: 0, cpuUsage: 0, networkRequests: 0, databaseQueries: 0, cacheHits: 0, cacheMisses: 0 },
        security: { vulnerabilities: [], securityScore: 100, riskLevel: 'low', recommendations: [] },
        quality: { testCoverage: 0, codeDuplication: 0, technicalDebt: 0, maintainabilityIndex: 100, reliability: 100, efficiency: 100, usability: 100 },
        timestamp: Date.now(),
        confidence: 0.8,
        analysisTime: 100
      };

      const actions = await service.generateActions(analysis);

      expect(actions).toBeDefined();
      expect(actions.length).toBeGreaterThan(0);
      expect(actions[0].type).toBe('refactor');
      expect(actions[0].handler).toBeDefined();
      expect(actions[0].enabled).toBe(true);
    });
  });

  describe('caching', () => {
    it('should cache analysis results', async () => {
      const code = 'function hello() { return "world"; }';
      const language = 'typescript';

      const analysis1 = await service.analyzeCode(code, language);
      const analysis2 = await service.analyzeCode(code, language);

      expect(analysis1.id).toBe(analysis2.id);
    });

    it('should clear cache', () => {
      service.clearCache();
      expect(service.getCacheSize()).toBe(0);
    });

    it('should return cache size', () => {
      const size = service.getCacheSize();
      expect(typeof size).toBe('number');
      expect(size).toBeGreaterThanOrEqual(0);
    });
  });

  describe('event handling', () => {
    it('should emit analysis-started event', (done) => {
      service.on('analysis-started', (data) => {
        expect(data.code).toBe('function test() { return "test"; }');
        expect(data.language).toBe('typescript');
        done();
      });

      service.analyzeCode('function test() { return "test"; }', 'typescript');
    });

    it('should emit analysis-completed event', (done) => {
      service.on('analysis-completed', (analysis) => {
        expect(analysis).toBeDefined();
        expect(analysis.code).toBe('function test() { return "test"; }');
        done();
      });

      service.analyzeCode('function test() { return "test"; }', 'typescript');
    });

    it('should emit analysis-failed event on error', (done) => {
      service.on('analysis-failed', (data) => {
        expect(data.error).toBeDefined();
        expect(data.code).toBe('function test() { return "test"; }');
        done();
      });

      // Mock an error by using an invalid language
      service.analyzeCode('function test() { return "test"; }', 'invalid-language');
    });

    it('should remove event listeners', () => {
      const listener = jest.fn();
      service.on('analysis-completed', listener);
      service.off('analysis-completed', listener);

      service.analyzeCode('function test() { return "test"; }', 'typescript');

      // Wait a bit to ensure the event would have been emitted
      setTimeout(() => {
        expect(listener).not.toHaveBeenCalled();
      }, 100);
    });
  });

  describe('cleanup', () => {
    it('should destroy service and clean up resources', () => {
      service.destroy();
      // Service should be destroyed without errors
    });
  });
});
