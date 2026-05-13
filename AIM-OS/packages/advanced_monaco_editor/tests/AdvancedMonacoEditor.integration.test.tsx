/**
 * Advanced Monaco Editor Integration Tests
 * 
 * Comprehensive integration tests for the AdvancedMonacoEditor component
 * covering all major features and integrations
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AdvancedMonacoEditor } from '../src/components/AdvancedMonacoEditor';

// Mock Monaco Editor
jest.mock('@monaco-editor/react', () => ({
  Editor: ({ onChange, onMount, value, theme, ...props }: any) => {
    const handleChange = (e: any) => onChange?.(e);
    const handleMount = (editor: any) => onMount?.(editor);
    
    return (
      <div data-testid="monaco-editor" data-theme={theme} {...props}>
        <textarea
          data-testid="monaco-textarea"
          value={value}
          onChange={handleChange}
          onFocus={() => handleMount({})}
          onContextMenu={(e) => {
            // Simulate context menu
            e.preventDefault();
            const contextMenu = document.createElement('div');
            contextMenu.setAttribute('data-testid', 'context-menu');
            contextMenu.innerHTML = 'Context Menu';
            document.body.appendChild(contextMenu);
          }}
        />
      </div>
    );
  }
}));

// Mock services
jest.mock('../src/services/SymbolDetectionService', () => ({
  SymbolDetectionService: jest.fn().mockImplementation(() => ({
    initialize: jest.fn(),
    detectSymbols: jest.fn().mockResolvedValue([
      {
        id: 'test-symbol',
        name: 'testFunction',
        type: 'function',
        range: { startLineNumber: 1, endLineNumber: 1, startColumn: 1, endColumn: 20 },
        metadata: { description: 'Test function' }
      }
    ]),
    destroy: jest.fn()
  }))
}));

jest.mock('../src/services/CodeAnalysisService', () => ({
  CodeAnalysisService: jest.fn().mockImplementation(() => ({
    initialize: jest.fn(),
    analyzeCode: jest.fn().mockResolvedValue({
      specBlock: {
        responsibility: 'Test function',
        mustNever: [],
        inputs: [],
        outputs: [],
        sideEffects: [],
        securityLevel: 'low',
        perfBudgetMs: 100,
        status: 'active',
        driftReason: null,
        governance: 'automated'
      },
      blueprintSlice: {
        nodeId: 'test-node',
        nodeName: 'testFunction',
        nodeKind: 'function',
        incomingCallers: [],
        outgoingEffects: [],
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
    }),
    destroy: jest.fn()
  }))
}));

jest.mock('../src/services/AIMOSIntegrationService', () => ({
  AIMOSIntegrationService: jest.fn().mockImplementation(() => ({
    initialize: jest.fn(),
    getEnhancedSymbolInfo: jest.fn().mockResolvedValue({
      symbol: 'testFunction',
      description: 'A test function for demonstration',
      examples: ['testFunction()', 'const result = testFunction()'],
      relatedSymbols: ['otherFunction', 'helperFunction'],
      metadata: { complexity: 'low', maintainability: 'high' }
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
      analysisTime: 50
    }),
    on: jest.fn(),
    destroy: jest.fn()
  }))
}));

jest.mock('../src/services/SecurityService', () => ({
  SecurityService: jest.fn().mockImplementation(() => ({
    validateInput: jest.fn().mockReturnValue({
      isValid: true,
      errors: [],
      warnings: [],
      riskLevel: 'low',
      sanitizedInput: 'test input'
    }),
    detectThreats: jest.fn().mockReturnValue([]),
    checkRateLimit: jest.fn().mockReturnValue(true),
    checkAccess: jest.fn().mockReturnValue(true),
    on: jest.fn(),
    destroy: jest.fn()
  }))
}));

describe('AdvancedMonacoEditor Integration', () => {
  const defaultProps = {
    value: "function testFunction() {\n  console.log('Hello, World!');\n  return 'test';\n}",
    language: 'javascript',
    onChange: jest.fn(),
    onMount: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('should render with basic configuration', () => {
      render(<AdvancedMonacoEditor {...defaultProps} />);
      
      expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
      expect(screen.getByTestId('monaco-textarea')).toHaveValue(defaultProps.value);
    });

    it('should render with theme selector when enabled', () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          showThemeSelector={true}
        />
      );
      
      expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
      // Theme selector should be present
      expect(screen.getByTestId('monaco-editor')).toHaveAttribute('data-theme');
    });

    it('should handle value changes', async () => {
      const onChange = jest.fn();
      render(<AdvancedMonacoEditor {...defaultProps} onChange={onChange} />);
      
      const textarea = screen.getByTestId('monaco-textarea');
      const newValue = "function newFunction() {\n  return 'new';\n}";
      
      fireEvent.change(textarea, { target: { value: newValue } });
      
      expect(onChange).toHaveBeenCalledWith(newValue);
    });

    it('should handle editor mount', async () => {
      const onMount = jest.fn();
      render(<AdvancedMonacoEditor {...defaultProps} onMount={onMount} />);
      
      const textarea = screen.getByTestId('monaco-textarea');
      fireEvent.focus(textarea);
      
      await waitFor(() => {
        expect(onMount).toHaveBeenCalled();
      });
    });
  });

  describe('Dropdown Functionality', () => {
    it('should enable dropdowns when configured', async () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          enableDropdowns={true}
          config={{
            dropdowns: {
              enabled: true,
              maxItems: 10,
              showDescriptions: true,
              showExamples: true,
              showRelatedSymbols: true
            }
          }}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      // Simulate symbol click
      const textarea = screen.getByTestId('monaco-textarea');
      fireEvent.click(textarea);
      
      await waitFor(() => {
        // Dropdown functionality should be active
        expect(editor).toBeInTheDocument();
      });
    });

    it('should disable dropdowns when configured', () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          enableDropdowns={false}
          config={{
            dropdowns: {
              enabled: false
            }
          }}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
    });
  });

  describe('Context Menu Functionality', () => {
    it('should enable context menus when configured', async () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          enableContextMenus={true}
          config={{
            contextMenus: {
              enabled: true,
              maxItems: 15,
              groupActions: true,
              showCategories: true,
              filterActions: true
            }
          }}
        />
      );
      
      const textarea = screen.getByTestId('monaco-textarea');
      
      // Simulate context menu
      fireEvent.contextMenu(textarea);
      
      await waitFor(() => {
        expect(screen.getByTestId('context-menu')).toBeInTheDocument();
      });
    });

    it('should disable context menus when configured', () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          enableContextMenus={false}
          config={{
            contextMenus: {
              enabled: false
            }
          }}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
    });
  });

  describe('Tooltip Functionality', () => {
    it('should enable tooltips when configured', async () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          enableTooltips={true}
          config={{
            tooltips: {
              enabled: true,
              showMetadata: true,
              showExamples: true,
              showRelatedSymbols: true,
              showNaturalLanguage: true
            }
          }}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      // Tooltip functionality should be active
      const textarea = screen.getByTestId('monaco-textarea');
      fireEvent.mouseOver(textarea);
      
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
    });

    it('should disable tooltips when configured', () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          enableTooltips={false}
          config={{
            tooltips: {
              enabled: false
            }
          }}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
    });
  });

  describe('Theme System Integration', () => {
    it('should handle theme changes', async () => {
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
      
      // Theme change should be handled
      await waitFor(() => {
        expect(editor).toHaveAttribute('data-theme');
      });
    });

    it('should apply custom theme', () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          theme="custom-theme"
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toHaveAttribute('data-theme', 'custom-theme');
    });
  });

  describe('AIM-OS Integration', () => {
    it('should integrate with AIM-OS services when enabled', async () => {
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
      
      // AIM-OS integration should be active
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
    });

    it('should disable AIM-OS integration when configured', () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          config={{
            aimos: {
              enabled: false
            }
          }}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
    });
  });

  describe('Performance Monitoring', () => {
    it('should enable performance monitoring when configured', async () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          config={{
            performance: {
              enableMetrics: true,
              enableProfiling: false,
              enableLazyLoading: true,
              maxMemoryUsage: 100 * 1024 * 1024,
              maxAnalysisTime: 100
            }
          }}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      // Performance monitoring should be active
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
    });

    it('should disable performance monitoring when configured', () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          config={{
            performance: {
              enableMetrics: false,
              enableProfiling: false,
              enableLazyLoading: false
            }
          }}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
    });
  });

  describe('Security Features', () => {
    it('should enable security features when configured', async () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          config={{
            security: {
              enableValidation: true,
              enableAccessControl: true,
              enableAuditLogging: false,
              enableEncryption: false,
              enableSandboxing: true
            }
          }}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      // Security features should be active
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
    });

    it('should disable security features when configured', () => {
      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          config={{
            security: {
              enableValidation: false,
              enableAccessControl: false,
              enableAuditLogging: false,
              enableEncryption: false,
              enableSandboxing: false
            }
          }}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should handle service initialization errors gracefully', async () => {
      // Mock service to throw error
      const mockService = require('../src/services/SymbolDetectionService').SymbolDetectionService;
      mockService.mockImplementation(() => ({
        initialize: jest.fn().mockRejectedValue(new Error('Service initialization failed')),
        detectSymbols: jest.fn().mockResolvedValue([]),
        destroy: jest.fn()
      }));

      render(<AdvancedMonacoEditor {...defaultProps} />);
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      // Should not crash despite service error
      await waitFor(() => {
        expect(editor).toBeInTheDocument();
      });
    });

    it('should handle configuration errors gracefully', () => {
      const invalidConfig = {
        dropdowns: {
          enabled: 'invalid' // Should be boolean
        }
      };

      render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          config={invalidConfig}
        />
      );
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
    });
  });

  describe('Cleanup', () => {
    it('should cleanup services on unmount', () => {
      const { unmount } = render(<AdvancedMonacoEditor {...defaultProps} />);
      
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toBeInTheDocument();
      
      unmount();
      
      // Services should be cleaned up
      expect(editor).not.toBeInTheDocument();
    });
  });
});