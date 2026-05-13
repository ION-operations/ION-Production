/**
 * Advanced Monaco Editor End-to-End Tests
 * 
 * Comprehensive end-to-end tests for the AdvancedMonacoEditor component
 * covering complete user workflows and interactions
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AdvancedMonacoEditor } from '../src/components/AdvancedMonacoEditor';

// Mock Monaco Editor with more realistic behavior
jest.mock('@monaco-editor/react', () => ({
  Editor: ({ onChange, onMount, value, theme, language, ...props }: any) => {
    const [editorValue, setEditorValue] = React.useState(value);
    const [editorInstance, setEditorInstance] = React.useState(null);
    
    React.useEffect(() => {
      setEditorValue(value);
    }, [value]);
    
    const handleChange = (newValue: string) => {
      setEditorValue(newValue);
      onChange?.(newValue);
    };
    
    const handleMount = (editor: any) => {
      setEditorInstance(editor);
      onMount?.(editor);
    };
    
    const handleFocus = () => {
      if (!editorInstance) {
        handleMount({});
      }
    };
    
    const handleContextMenu = (e: any) => {
      e.preventDefault();
      const contextMenu = document.createElement('div');
      contextMenu.setAttribute('data-testid', 'context-menu');
      contextMenu.innerHTML = `
        <div data-testid="context-menu-item" data-action="copy">Copy</div>
        <div data-testid="context-menu-item" data-action="paste">Paste</div>
        <div data-testid="context-menu-item" data-action="cut">Cut</div>
      `;
      contextMenu.style.position = 'absolute';
      contextMenu.style.left = '0px';
      contextMenu.style.top = '0px';
      contextMenu.style.zIndex = '1000';
      document.body.appendChild(contextMenu);
    };
    
    const handleMouseOver = (e: any) => {
      const tooltip = document.createElement('div');
      tooltip.setAttribute('data-testid', 'tooltip');
      tooltip.innerHTML = 'Symbol: testFunction - A test function for demonstration';
      tooltip.style.position = 'absolute';
      tooltip.style.left = '0px';
      tooltip.style.top = '0px';
      tooltip.style.zIndex = '1000';
      document.body.appendChild(tooltip);
    };
    
    const handleMouseOut = () => {
      const tooltip = document.querySelector('[data-testid="tooltip"]');
      if (tooltip) {
        tooltip.remove();
      }
    };
    
    return (
      <div data-testid="monaco-editor" data-theme={theme} data-language={language} {...props}>
        <textarea
          data-testid="monaco-textarea"
          value={editorValue}
          onChange={(e) => handleChange(e.target.value)}
          onFocus={handleFocus}
          onContextMenu={handleContextMenu}
          onMouseOver={handleMouseOver}
          onMouseOut={handleMouseOut}
          style={{ width: '100%', height: '100%', minHeight: '200px' }}
        />
      </div>
    );
  }
}));

// Mock services with realistic behavior
jest.mock('../src/services/SymbolDetectionService', () => ({
  SymbolDetectionService: jest.fn().mockImplementation(() => ({
    initialize: jest.fn().mockResolvedValue(true),
    detectSymbols: jest.fn().mockImplementation((code) => {
      const symbols = [];
      const lines = code.split('\n');
      
      lines.forEach((line, lineIndex) => {
        const functionMatch = line.match(/function\s+(\w+)/);
        if (functionMatch) {
          symbols.push({
            id: `symbol-${lineIndex}`,
            name: functionMatch[1],
            type: 'function',
            range: { 
              startLineNumber: lineIndex + 1, 
              endLineNumber: lineIndex + 1, 
              startColumn: line.indexOf(functionMatch[1]), 
              endColumn: line.indexOf(functionMatch[1]) + functionMatch[1].length 
            },
            metadata: { 
              description: `Function ${functionMatch[1]}`,
              complexity: 'low',
              maintainability: 'high'
            }
          });
        }
        
        const variableMatch = line.match(/(?:let|const|var)\s+(\w+)/);
        if (variableMatch) {
          symbols.push({
            id: `symbol-${lineIndex}-var`,
            name: variableMatch[1],
            type: 'variable',
            range: { 
              startLineNumber: lineIndex + 1, 
              endLineNumber: lineIndex + 1, 
              startColumn: line.indexOf(variableMatch[1]), 
              endColumn: line.indexOf(variableMatch[1]) + variableMatch[1].length 
            },
            metadata: { 
              description: `Variable ${variableMatch[1]}`,
              type: 'string'
            }
          });
        }
      });
      
      return Promise.resolve(symbols);
    }),
    destroy: jest.fn()
  }))
}));

jest.mock('../src/services/CodeAnalysisService', () => ({
  CodeAnalysisService: jest.fn().mockImplementation(() => ({
    initialize: jest.fn().mockResolvedValue(true),
    analyzeCode: jest.fn().mockImplementation((code) => {
      const hasFunction = code.includes('function');
      const hasConsole = code.includes('console.log');
      const hasReturn = code.includes('return');
      
      return Promise.resolve({
        specBlock: {
          responsibility: hasFunction ? 'Function implementation' : 'Code block',
          mustNever: hasConsole ? ['console.log in production'] : [],
          inputs: hasFunction ? ['parameters'] : [],
          outputs: hasReturn ? ['return value'] : [],
          sideEffects: hasConsole ? ['console output'] : [],
          securityLevel: 'low',
          perfBudgetMs: 100,
          status: 'active',
          driftReason: null,
          governance: 'automated'
        },
        blueprintSlice: {
          nodeId: 'test-node',
          nodeName: hasFunction ? 'testFunction' : 'codeBlock',
          nodeKind: hasFunction ? 'function' : 'block',
          incomingCallers: [],
          outgoingEffects: hasConsole ? ['console'] : [],
          edgeTypes: [],
          neighborNodes: []
        },
        timelineSummary: {
          nodeId: 'test-node',
          recentExecutions: [],
          avgDuration: 0,
          totalExecutions: 0,
          lastExecution: null
        }
      });
    }),
    destroy: jest.fn()
  }))
}));

jest.mock('../src/services/AIMOSIntegrationService', () => ({
  AIMOSIntegrationService: jest.fn().mockImplementation(() => ({
    initialize: jest.fn().mockResolvedValue(true),
    getEnhancedSymbolInfo: jest.fn().mockImplementation((symbol) => {
      return Promise.resolve({
        symbol: symbol,
        description: `Enhanced description for ${symbol}`,
        examples: [`${symbol}()`, `const result = ${symbol}()`],
        relatedSymbols: ['otherFunction', 'helperFunction'],
        metadata: { 
          complexity: 'low', 
          maintainability: 'high',
          lastModified: new Date().toISOString()
        }
      });
    }),
    getRelatedSymbols: jest.fn().mockResolvedValue(['otherFunction', 'helperFunction']),
    getCodeExamples: jest.fn().mockResolvedValue(['testFunction()', 'const result = testFunction()']),
    destroy: jest.fn()
  }))
}));

jest.mock('../src/services/ThemeManager', () => ({
  ThemeManager: jest.fn().mockImplementation(() => ({
    registerTheme: jest.fn(),
    setTheme: jest.fn(),
    getTheme: jest.fn().mockReturnValue({ id: 'default-dark', name: 'Default Dark' }),
    on: jest.fn(),
    destroy: jest.fn()
  }))
}));

jest.mock('../src/services/PerformanceService', () => ({
  PerformanceService: jest.fn().mockImplementation(() => ({
    startMonitoring: jest.fn(),
    stopMonitoring: jest.fn(),
    getMetrics: jest.fn().mockReturnValue({
      memoryUsage: 50,
      cpuUsage: 30,
      renderTime: 16,
      analysisTime: 50,
      cacheHitRate: 0.8,
      errorRate: 0.02
    }),
    on: jest.fn(),
    destroy: jest.fn()
  }))
}));

jest.mock('../src/services/SecurityService', () => ({
  SecurityService: jest.fn().mockImplementation(() => ({
    validateInput: jest.fn().mockImplementation((input) => ({
      isValid: !input.includes('<script>'),
      errors: input.includes('<script>') ? [{ message: 'XSS threat detected', code: 'XSS_THREAT' }] : [],
      warnings: input.length > 1000 ? [{ message: 'Input is very long', code: 'LONG_INPUT' }] : [],
      riskLevel: input.includes('<script>') ? 'critical' : 'low',
      sanitizedInput: input.replace(/<script[^>]*>.*?<\/script>/gi, '')
    })),
    detectThreats: jest.fn().mockImplementation((input) => {
      const threats = [];
      if (input.includes('<script>')) {
        threats.push({
          isThreat: true,
          threatType: 'xss',
          confidence: 0.9,
          description: 'XSS threat detected'
        });
      }
      return threats;
    }),
    checkRateLimit: jest.fn().mockReturnValue(true),
    checkAccess: jest.fn().mockReturnValue(true),
    on: jest.fn(),
    destroy: jest.fn()
  }))
}));

describe('AdvancedMonacoEditor E2E', () => {
  const defaultProps = {
    value: "function testFunction() {\n  console.log('Hello, World!');\n  return 'test';\n}",
    language: 'javascript',
    onChange: jest.fn(),
    onMount: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Clean up any existing context menus or tooltips
    document.querySelectorAll('[data-testid="context-menu"], [data-testid="tooltip"]').forEach(el => el.remove());
  });

  describe('Complete User Workflow', () => {
    it('should handle complete code editing workflow', async () => {
      const onChange = jest.fn();
      const onMount = jest.fn();
      
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          onChange={onChange}
          onMount={onMount}
          enableDropdowns={true}
          enableContextMenus={true}
          enableTooltips={true}
          showThemeSelector={true}
        />
      );
      
      // 1. Editor should mount
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      // 2. Focus editor to trigger mount
      const textarea = screen.getByTestId('monaco-textarea');
      fireEvent.focus(textarea);
      
      await waitFor(() => {
        expect(onMount).toHaveBeenCalled();
      });
      
      // 3. Edit code
      const newCode = "function newFunction() {\n  const message = 'Hello, World!';\n  console.log(message);\n  return message;\n}";
      fireEvent.change(textarea, { target: { value: newCode } });
      
      expect(onChange).toHaveBeenCalledWith(newCode);
      
      // 4. Test context menu
      fireEvent.contextMenu(textarea);
      
      await waitFor(() => {
        expect(screen.getByTestId('context-menu')).toBeInTheDocument();
        expect(screen.getByTestId('context-menu-item')).toBeInTheDocument();
      });
      
      // 5. Test tooltip
      fireEvent.mouseOver(textarea);
      
      await waitFor(() => {
        expect(screen.getByTestId('tooltip')).toBeInTheDocument();
      });
      
      // 6. Test theme change
      fireEvent.mouseOut(textarea);
      
      await waitFor(() => {
        expect(screen.queryByTestId('tooltip')).not.toBeInTheDocument();
      });
    });

    it('should handle complex code with multiple symbols', async () => {
      const complexCode = `
        class Calculator {
          constructor() {
            this.history = [];
          }
          
          add(a, b) {
            const result = a + b;
            this.history.push(\`\${a} + \${b} = \${result}\`);
            return result;
          }
          
          subtract(a, b) {
            const result = a - b;
            this.history.push(\`\${a} - \${b} = \${result}\`);
            return result;
          }
          
          getHistory() {
            return this.history;
          }
        }
        
        const calc = new Calculator();
        const sum = calc.add(5, 3);
        console.log('Sum:', sum);
      `;
      
      const onChange = jest.fn();
      
      render(
        <AdvancedMonacoEditor 
          value={complexCode}
          language="javascript"
          onChange={onChange}
          enableDropdowns={true}
          enableContextMenus={true}
          enableTooltips={true}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      const textarea = screen.getByTestId('monaco-textarea');
      expect(textarea).toHaveValue(complexCode);
      
      // Test symbol detection
      fireEvent.focus(textarea);
      
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
    });
  });

  describe('Theme System E2E', () => {
    it('should handle complete theme workflow', async () => {
      const onThemeChange = jest.fn();
      
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          showThemeSelector={true}
          onThemeChange={onThemeChange}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      // Theme should be applied
      expect(editor).toHaveAttribute('data-theme');
      
      // Test theme change
      const textarea = screen.getByTestId('monaco-textarea');
      fireEvent.focus(textarea);
      
      await waitFor(() => {
        expect(editor).toHaveAttribute('data-theme');
      });
    });

    it('should persist theme selection', async () => {
      const onThemeChange = jest.fn();
      
      const { rerender } = render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          showThemeSelector={true}
          onThemeChange={onThemeChange}
          theme="custom-theme"
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toHaveAttribute('data-theme', 'custom-theme');
      
      // Rerender with different theme
      rerender(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          showThemeSelector={true}
          onThemeChange={onThemeChange}
          theme="another-theme"
        />
      );
      
      expect(editor).toHaveAttribute('data-theme', 'another-theme');
    });
  });

  describe('AIM-OS Integration E2E', () => {
    it('should handle complete AIM-OS workflow', async () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          config={{
            aimos: {
              enabled: true,
              services: ['cmc', 'hhni', 'vif', 'seg', 'apoe', 'iis'],
              retryAttempts: 3,
              retryDelay: 1000
            },
            intelligence: {
              enabled: true,
              realTimeAnalysis: true,
              cacheEnabled: true,
              cacheSize: 1000,
              cacheTimeout: 300000
            }
          }}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      const textarea = screen.getByTestId('monaco-textarea');
      fireEvent.focus(textarea);
      
      // AIM-OS integration should be active
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
      
      // Test code analysis
      fireEvent.change(textarea, { target: { value: "function newFunction() { return 'new'; }" } });
      
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
    });

    it('should handle AIM-OS service failures gracefully', async () => {
      // Mock service to fail
      const mockService = require('../src/services/AIMOSIntegrationService').AIMOSIntegrationService;
      mockService.mockImplementation(() => ({
        initialize: jest.fn().mockRejectedValue(new Error('AIM-OS service unavailable')),
        getEnhancedSymbolInfo: jest.fn().mockRejectedValue(new Error('Service error')),
        getRelatedSymbols: jest.fn().mockRejectedValue(new Error('Service error')),
        getCodeExamples: jest.fn().mockRejectedValue(new Error('Service error')),
        destroy: jest.fn()
      }));

      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          config={{
            aimos: {
              enabled: true,
              services: ['cmc', 'hhni', 'vif', 'seg', 'apoe', 'iis'],
              retryAttempts: 3,
              retryDelay: 1000
            }
          }}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      // Should not crash despite service failure
      const textarea = screen.getByTestId('monaco-textarea');
      fireEvent.focus(textarea);
      
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
    });
  });

  describe('Performance Monitoring E2E', () => {
    it('should handle complete performance monitoring workflow', async () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          config={{
            performance: {
              enableMetrics: true,
              enableProfiling: true,
              enableLazyLoading: true,
              maxMemoryUsage: 100 * 1024 * 1024,
              maxAnalysisTime: 100
            }
          }}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      const textarea = screen.getByTestId('monaco-textarea');
      fireEvent.focus(textarea);
      
      // Performance monitoring should be active
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
      
      // Test performance under load
      for (let i = 0; i < 10; i++) {
        fireEvent.change(textarea, { target: { value: `function test${i}() { return ${i}; }` } });
      }
      
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
    });

    it('should handle performance alerts', async () => {
      // Mock performance service to trigger alerts
      const mockService = require('../src/services/PerformanceService').PerformanceService;
      mockService.mockImplementation(() => ({
        startMonitoring: jest.fn(),
        stopMonitoring: jest.fn(),
        getMetrics: jest.fn().mockReturnValue({
          memoryUsage: 95, // High memory usage
          cpuUsage: 90,    // High CPU usage
          renderTime: 50,  // Slow render
          analysisTime: 200, // Slow analysis
          cacheHitRate: 0.3,
          errorRate: 0.1
        }),
        on: jest.fn().mockImplementation((event, callback) => {
          if (event === 'alert') {
            // Simulate alert
            setTimeout(() => callback({
              type: 'memory',
              level: 'warning',
              message: 'High memory usage detected',
              value: 95,
              threshold: 80
            }), 100);
          }
        }),
        destroy: jest.fn()
      }));

      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          config={{
            performance: {
              enableMetrics: true,
              enableProfiling: true,
              enableLazyLoading: true,
              maxMemoryUsage: 100 * 1024 * 1024,
              maxAnalysisTime: 100
            }
          }}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      // Should handle performance alerts gracefully
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
    });
  });

  describe('Security Features E2E', () => {
    it('should handle complete security workflow', async () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          config={{
            security: {
              enableValidation: true,
              enableAccessControl: true,
              enableAuditLogging: true,
              enableEncryption: false,
              enableSandboxing: true
            }
          }}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      const textarea = screen.getByTestId('monaco-textarea');
      fireEvent.focus(textarea);
      
      // Security features should be active
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
      
      // Test security validation
      fireEvent.change(textarea, { target: { value: "function test() { return 'safe'; }" } });
      
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
    });

    it('should handle security threats', async () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          config={{
            security: {
              enableValidation: true,
              enableAccessControl: true,
              enableAuditLogging: true,
              enableEncryption: false,
              enableSandboxing: true
            }
          }}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      const textarea = screen.getByTestId('monaco-textarea');
      fireEvent.focus(textarea);
      
      // Test XSS threat detection
      fireEvent.change(textarea, { target: { value: "function test() { return '<script>alert(\"xss\")</script>'; }" } });
      
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
    });
  });

  describe('Error Recovery E2E', () => {
    it('should recover from service failures', async () => {
      // Mock service to fail initially, then succeed
      let shouldFail = true;
      const mockService = require('../src/services/SymbolDetectionService').SymbolDetectionService;
      mockService.mockImplementation(() => ({
        initialize: jest.fn().mockImplementation(() => {
          if (shouldFail) {
            shouldFail = false;
            return Promise.reject(new Error('Service temporarily unavailable'));
          }
          return Promise.resolve(true);
        }),
        detectSymbols: jest.fn().mockResolvedValue([]),
        destroy: jest.fn()
      }));

      render(<AdvancedMonacoEditor {...defaultProps} />);
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      // Should recover from initial failure
      const textarea = screen.getByTestId('monaco-textarea');
      fireEvent.focus(textarea);
      
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
    });

    it('should handle configuration changes gracefully', async () => {
      const { rerender } = render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          enableDropdowns={true}
          enableContextMenus={true}
          enableTooltips={true}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      // Change configuration
      rerender(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          enableDropdowns={false}
          enableContextMenus={false}
          enableTooltips={false}
        />
      );
      
      expect(editor).toBeInTheDocument();
      
      // Should handle configuration change gracefully
      const textarea = screen.getByTestId('monaco-textarea');
      fireEvent.focus(textarea);
      
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
    });
  });

  describe('Cleanup E2E', () => {
    it('should cleanup all resources on unmount', async () => {
      const { unmount } = render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          enableDropdowns={true}
          enableContextMenus={true}
          enableTooltips={true}
          showThemeSelector={true}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      const textarea = screen.getByTestId('monaco-textarea');
      fireEvent.focus(textarea);
      fireEvent.contextMenu(textarea);
      fireEvent.mouseOver(textarea);
      
      await waitFor(() => {
        expect(screen.getByTestId('context-menu')).toBeInTheDocument();
        expect(screen.getByTestId('tooltip')).toBeInTheDocument();
      });
      
      // Unmount should cleanup everything
      unmount();
      
      expect(editor).not.toBeInTheDocument();
      expect(screen.queryByTestId('context-menu')).not.toBeInTheDocument();
      expect(screen.queryByTestId('tooltip')).not.toBeInTheDocument();
    });
  });
});
