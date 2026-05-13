/**
 * Advanced Monaco Editor - AIM-OS Integration Service Tests
 * 
 * This file contains tests for the AIMOSIntegrationService.
 */

import { AIMOSIntegrationService } from '../src/services/AIMOSIntegrationService';
import { AIMOSConfiguration } from '../src/types/IntegrationTypes';
import { SymbolInfo, CodeAnalysis } from '../src/types/MonacoTypes';

describe('AIMOSIntegrationService', () => {
  let service: AIMOSIntegrationService;
  let configuration: AIMOSConfiguration;

  beforeEach(() => {
    configuration = {
      enabled: true,
      endpoints: {
        cmc: 'http://localhost:8000/cmc',
        hhni: 'http://localhost:8000/hhni',
        vif: 'http://localhost:8000/vif',
        seg: 'http://localhost:8000/seg',
        apoe: 'http://localhost:8000/apoe',
        iis: 'http://localhost:8000/iis'
      },
      timeout: 5000,
      retries: 3,
      cache: true
    };

    service = new AIMOSIntegrationService(configuration);
  });

  afterEach(() => {
    service.destroy();
  });

  describe('initialization', () => {
    it('should initialize with configuration', () => {
      expect(service).toBeDefined();
      expect(service.configuration).toBe(configuration);
    });

    it('should initialize with disabled configuration', () => {
      const disabledConfig = { ...configuration, enabled: false };
      const disabledService = new AIMOSIntegrationService(disabledConfig);
      
      expect(disabledService).toBeDefined();
      expect(disabledService.configuration.enabled).toBe(false);
      
      disabledService.destroy();
    });

    it('should initialize with missing endpoints', () => {
      const minimalConfig = { ...configuration, endpoints: {} };
      const minimalService = new AIMOSIntegrationService(minimalConfig);
      
      expect(minimalService).toBeDefined();
      expect(minimalService.configuration.endpoints).toEqual({});
      
      minimalService.destroy();
    });
  });

  describe('connection status', () => {
    it('should return connection status', () => {
      const isConnected = service.isConnected();
      expect(typeof isConnected).toBe('boolean');
    });

    it('should return integration status', async () => {
      const status = await service.getStatus();
      
      expect(status).toBeDefined();
      expect(status.connected).toBeDefined();
      expect(typeof status.connected).toBe('boolean');
      expect(status.services).toBeDefined();
      expect(status.services.cmc).toBeDefined();
      expect(status.services.hhni).toBeDefined();
      expect(status.services.vif).toBeDefined();
      expect(status.services.seg).toBeDefined();
      expect(status.services.apoe).toBeDefined();
      expect(status.services.iis).toBeDefined();
      expect(status.lastUpdate).toBeDefined();
      expect(status.errors).toBeDefined();
      expect(status.warnings).toBeDefined();
    });
  });

  describe('symbol operations', () => {
    const mockSymbol: SymbolInfo = {
      id: 'test-symbol-1',
      name: 'testFunction',
      type: 'function' as any,
      kind: 'definition' as any,
      position: { line: 1, column: 0 },
      range: {
        start: { line: 1, column: 0 },
        end: { line: 1, column: 20 }
      },
      language: 'typescript',
      metadata: {
        description: 'A test function',
        parameters: [],
        returnType: 'string',
        modifiers: ['export'],
        annotations: [],
        complexity: 1,
        dependencies: []
      }
    };

    it('should store symbol', async () => {
      await expect(service.storeSymbol(mockSymbol)).resolves.not.toThrow();
    });

    it('should retrieve symbol', async () => {
      const symbol = await service.retrieveSymbol('test-symbol-1');
      expect(symbol).toBeDefined();
    });

    it('should search symbols', async () => {
      const results = await service.searchSymbols('test', 10);
      expect(results).toBeDefined();
      expect(Array.isArray(results)).toBe(true);
    });

    it('should handle symbol storage errors', async () => {
      // Test with invalid symbol
      const invalidSymbol = { ...mockSymbol, id: '' };
      await expect(service.storeSymbol(invalidSymbol)).resolves.not.toThrow();
    });
  });

  describe('analysis operations', () => {
    const mockAnalysis: CodeAnalysis = {
      id: 'test-analysis-1',
      code: 'function test() { return "hello"; }',
      language: 'typescript',
      symbols: [],
      dependencies: [],
      complexity: {
        cyclomatic: 1,
        cognitive: 1,
        maintainability: 100,
        nesting: 0,
        lines: 1,
        statements: 1,
        functions: 1,
        classes: 0
      },
      performance: {
        executionTime: 0,
        memoryUsage: 0,
        cpuUsage: 0,
        networkRequests: 0,
        databaseQueries: 0,
        cacheHits: 0,
        cacheMisses: 0
      },
      security: {
        vulnerabilities: [],
        securityScore: 100,
        riskLevel: 'low' as any,
        recommendations: []
      },
      quality: {
        testCoverage: 0,
        codeDuplication: 0,
        technicalDebt: 0,
        maintainabilityIndex: 100,
        reliability: 100,
        efficiency: 100,
        usability: 100
      },
      timestamp: Date.now(),
      confidence: 0.8,
      analysisTime: 100
    };

    it('should store analysis', async () => {
      await expect(service.storeAnalysis(mockAnalysis)).resolves.not.toThrow();
    });

    it('should handle analysis storage errors', async () => {
      // Test with invalid analysis
      const invalidAnalysis = { ...mockAnalysis, id: '' };
      await expect(service.storeAnalysis(invalidAnalysis)).resolves.not.toThrow();
    });
  });

  describe('knowledge synthesis', () => {
    const mockSymbols: SymbolInfo[] = [
      {
        id: 'symbol-1',
        name: 'function1',
        type: 'function' as any,
        kind: 'definition' as any,
        position: { line: 1, column: 0 },
        range: {
          start: { line: 1, column: 0 },
          end: { line: 1, column: 20 }
        },
        language: 'typescript',
        metadata: {
          description: 'First function',
          parameters: [],
          returnType: 'string',
          modifiers: [],
          annotations: [],
          complexity: 1,
          dependencies: []
        }
      },
      {
        id: 'symbol-2',
        name: 'function2',
        type: 'function' as any,
        kind: 'definition' as any,
        position: { line: 2, column: 0 },
        range: {
          start: { line: 2, column: 0 },
          end: { line: 2, column: 20 }
        },
        language: 'typescript',
        metadata: {
          description: 'Second function',
          parameters: [],
          returnType: 'number',
          modifiers: [],
          annotations: [],
          complexity: 1,
          dependencies: []
        }
      }
    ];

    it('should synthesize knowledge', async () => {
      const knowledge = await service.synthesizeKnowledge(mockSymbols);
      expect(knowledge).toBeDefined();
    });

    it('should handle empty symbols array', async () => {
      const knowledge = await service.synthesizeKnowledge([]);
      expect(knowledge).toBeDefined();
    });
  });

  describe('improvement planning', () => {
    const mockAnalysis: CodeAnalysis = {
      id: 'test-analysis-1',
      code: 'function test() { return "hello"; }',
      language: 'typescript',
      symbols: [],
      dependencies: [],
      complexity: {
        cyclomatic: 1,
        cognitive: 1,
        maintainability: 100,
        nesting: 0,
        lines: 1,
        statements: 1,
        functions: 1,
        classes: 0
      },
      performance: {
        executionTime: 0,
        memoryUsage: 0,
        cpuUsage: 0,
        networkRequests: 0,
        databaseQueries: 0,
        cacheHits: 0,
        cacheMisses: 0
      },
      security: {
        vulnerabilities: [],
        securityScore: 100,
        riskLevel: 'low' as any,
        recommendations: []
      },
      quality: {
        testCoverage: 0,
        codeDuplication: 0,
        technicalDebt: 0,
        maintainabilityIndex: 100,
        reliability: 100,
        efficiency: 100,
        usability: 100
      },
      timestamp: Date.now(),
      confidence: 0.8,
      analysisTime: 100
    };

    it('should create improvement plan', async () => {
      const plan = await service.createImprovementPlan(mockAnalysis);
      expect(plan).toBeDefined();
    });

    it('should handle invalid analysis', async () => {
      const invalidAnalysis = { ...mockAnalysis, id: '' };
      const plan = await service.createImprovementPlan(invalidAnalysis);
      expect(plan).toBeDefined();
    });
  });

  describe('intuition computation', () => {
    it('should compute intuition', async () => {
      const intuition = await service.computeIntuition(0.8, 'test context');
      expect(intuition).toBeDefined();
      expect(typeof intuition).toBe('number');
      expect(intuition).toBeGreaterThanOrEqual(0);
      expect(intuition).toBeLessThanOrEqual(1);
    });

    it('should handle low confidence', async () => {
      const intuition = await service.computeIntuition(0.2, 'test context');
      expect(intuition).toBeDefined();
      expect(typeof intuition).toBe('number');
    });

    it('should handle high confidence', async () => {
      const intuition = await service.computeIntuition(0.9, 'test context');
      expect(intuition).toBeDefined();
      expect(typeof intuition).toBe('number');
    });

    it('should handle empty context', async () => {
      const intuition = await service.computeIntuition(0.8, '');
      expect(intuition).toBeDefined();
      expect(typeof intuition).toBe('number');
    });
  });

  describe('event handling', () => {
    it('should add event listener', () => {
      const listener = jest.fn();
      service.on('connected', listener);
      
      // The listener should be added without error
      expect(() => service.on('connected', listener)).not.toThrow();
    });

    it('should remove event listener', () => {
      const listener = jest.fn();
      service.on('connected', listener);
      service.off('connected', listener);
      
      // The listener should be removed without error
      expect(() => service.off('connected', listener)).not.toThrow();
    });

    it('should emit connected event', (done) => {
      service.on('connected', (data) => {
        expect(data).toBeDefined();
        expect(data.service).toBe('all');
        expect(data.message).toBeDefined();
        done();
      });

      // The service should emit connected event during initialization
      // This is handled in the constructor
    });

    it('should emit error event', (done) => {
      service.on('error', (data) => {
        expect(data).toBeDefined();
        expect(data.service).toBeDefined();
        expect(data.message).toBeDefined();
        done();
      });

      // Simulate an error by calling a method that might fail
      service.storeSymbol({
        id: '',
        name: '',
        type: 'function' as any,
        kind: 'definition' as any,
        position: { line: 0, column: 0 },
        range: {
          start: { line: 0, column: 0 },
          end: { line: 0, column: 0 }
        },
        language: 'typescript',
        metadata: {
          description: '',
          parameters: [],
          returnType: '',
          modifiers: [],
          annotations: [],
          complexity: 0,
          dependencies: []
        }
      });
    });
  });

  describe('service methods', () => {
    it('should have CMC service', () => {
      expect(service.cmc).toBeDefined();
      expect(service.cmc.storeMemory).toBeDefined();
      expect(service.cmc.retrieveMemory).toBeDefined();
      expect(service.cmc.searchMemory).toBeDefined();
      expect(service.cmc.deleteMemory).toBeDefined();
      expect(service.cmc.listMemories).toBeDefined();
    });

    it('should have HHNI service', () => {
      expect(service.hhni).toBeDefined();
      expect(service.hhni.indexSymbol).toBeDefined();
      expect(service.hhni.searchSymbols).toBeDefined();
      expect(service.hhni.getRelatedSymbols).toBeDefined();
      expect(service.hhni.updateSymbol).toBeDefined();
      expect(service.hhni.deleteSymbol).toBeDefined();
    });

    it('should have VIF service', () => {
      expect(service.vif).toBeDefined();
      expect(service.vif.trackConfidence).toBeDefined();
      expect(service.vif.getConfidence).toBeDefined();
      expect(service.vif.validateOutput).toBeDefined();
      expect(service.vif.getValidationResult).toBeDefined();
    });

    it('should have SEG service', () => {
      expect(service.seg).toBeDefined();
      expect(service.seg.synthesizeKnowledge).toBeDefined();
      expect(service.seg.getKnowledgeGraph).toBeDefined();
      expect(service.seg.addEvidence).toBeDefined();
      expect(service.seg.getEvidence).toBeDefined();
    });

    it('should have APOE service', () => {
      expect(service.apoe).toBeDefined();
      expect(service.apoe.createPlan).toBeDefined();
      expect(service.apoe.executePlan).toBeDefined();
      expect(service.apoe.updatePlan).toBeDefined();
      expect(service.apoe.getPlanStatus).toBeDefined();
    });

    it('should have IIS service', () => {
      expect(service.iis).toBeDefined();
      expect(service.iis.computeIntuition).toBeDefined();
      expect(service.iis.updateIntuitionWeights).toBeDefined();
      expect(service.iis.getIntuitionTrace).toBeDefined();
    });
  });

  describe('cleanup', () => {
    it('should destroy service and clean up resources', async () => {
      await service.destroy();
      // Service should be destroyed without errors
    });
  });

  describe('error handling', () => {
    it('should handle service initialization errors', () => {
      const invalidConfig = {
        ...configuration,
        endpoints: {
          cmc: 'invalid-url',
          hhni: 'invalid-url',
          vif: 'invalid-url',
          seg: 'invalid-url',
          apoe: 'invalid-url',
          iis: 'invalid-url'
        }
      };

      expect(() => new AIMOSIntegrationService(invalidConfig)).not.toThrow();
    });

    it('should handle network errors gracefully', async () => {
      const offlineConfig = {
        ...configuration,
        endpoints: {
          cmc: 'http://offline-server/cmc',
          hhni: 'http://offline-server/hhni',
          vif: 'http://offline-server/vif',
          seg: 'http://offline-server/seg',
          apoe: 'http://offline-server/apoe',
          iis: 'http://offline-server/iis'
        }
      };

      const offlineService = new AIMOSIntegrationService(offlineConfig);
      
      // Should not throw errors even when offline
      await expect(offlineService.storeSymbol({
        id: 'test',
        name: 'test',
        type: 'function' as any,
        kind: 'definition' as any,
        position: { line: 1, column: 0 },
        range: {
          start: { line: 1, column: 0 },
          end: { line: 1, column: 10 }
        },
        language: 'typescript',
        metadata: {
          description: 'test',
          parameters: [],
          returnType: 'string',
          modifiers: [],
          annotations: [],
          complexity: 1,
          dependencies: []
        }
      })).resolves.not.toThrow();

      await offlineService.destroy();
    });
  });
});
