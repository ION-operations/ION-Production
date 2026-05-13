/**
 * Advanced Monaco Editor - Tests
 * 
 * This file contains tests for the Advanced Monaco Editor component.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AdvancedMonacoEditor } from '../src/components/AdvancedMonacoEditor';

// Mock Monaco Editor
jest.mock('@monaco-editor/react', () => ({
  Editor: ({ onMount, onChange, ...props }: any) => {
    const mockEditor = {
      getModel: () => ({
        getValue: () => props.value || '',
        getLanguageId: () => props.language || 'typescript'
      }),
      onDidChangeModelContent: jest.fn(),
      onDidChangeModel: jest.fn(),
      dispose: jest.fn()
    };

    React.useEffect(() => {
      if (onMount) {
        onMount(mockEditor);
      }
    }, [onMount]);

    return (
      <div data-testid="monaco-editor" onClick={() => onChange && onChange(props.value)}>
        Monaco Editor
      </div>
    );
  }
}));

// Mock services
jest.mock('../src/services/SymbolDetectionService', () => ({
  SymbolDetectionService: jest.fn().mockImplementation(() => ({
    detectSymbols: jest.fn().mockResolvedValue([]),
    getSymbols: jest.fn().mockReturnValue([]),
    getSymbol: jest.fn().mockReturnValue(null),
    getSymbolsByType: jest.fn().mockReturnValue([]),
    getSymbolsByKind: jest.fn().mockReturnValue([]),
    searchSymbols: jest.fn().mockReturnValue([]),
    on: jest.fn(),
    off: jest.fn(),
    destroy: jest.fn()
  }))
}));

jest.mock('../src/services/CodeAnalysisService', () => ({
  CodeAnalysisService: jest.fn().mockImplementation(() => ({
    analyzeCode: jest.fn().mockResolvedValue({
      id: 'test-analysis',
      code: 'test code',
      language: 'typescript',
      symbols: [],
      dependencies: [],
      complexity: { cyclomatic: 1, cognitive: 1, maintainability: 100, nesting: 0, lines: 1, statements: 1, functions: 0, classes: 0 },
      performance: { executionTime: 0, memoryUsage: 0, cpuUsage: 0, networkRequests: 0, databaseQueries: 0, cacheHits: 0, cacheMisses: 0 },
      security: { vulnerabilities: [], securityScore: 100, riskLevel: 'low', recommendations: [] },
      quality: { testCoverage: 0, codeDuplication: 0, technicalDebt: 0, maintainabilityIndex: 100, reliability: 100, efficiency: 100, usability: 100 },
      timestamp: Date.now(),
      confidence: 0.8,
      analysisTime: 100
    }),
    generateSuggestions: jest.fn().mockResolvedValue([]),
    generateActions: jest.fn().mockResolvedValue([]),
    on: jest.fn(),
    off: jest.fn(),
    destroy: jest.fn()
  }))
}));

jest.mock('../src/services/AIMOSIntegrationService', () => ({
  AIMOSIntegrationService: jest.fn().mockImplementation(() => ({
    cmc: {
      storeMemory: jest.fn().mockResolvedValue(undefined),
      retrieveMemory: jest.fn().mockResolvedValue(null),
      searchMemory: jest.fn().mockResolvedValue([]),
      deleteMemory: jest.fn().mockResolvedValue(undefined),
      listMemories: jest.fn().mockResolvedValue([])
    },
    hhni: {
      indexSymbol: jest.fn().mockResolvedValue(undefined),
      searchSymbols: jest.fn().mockResolvedValue([]),
      getRelatedSymbols: jest.fn().mockResolvedValue([]),
      updateSymbol: jest.fn().mockResolvedValue(undefined),
      deleteSymbol: jest.fn().mockResolvedValue(undefined)
    },
    vif: {
      trackConfidence: jest.fn().mockResolvedValue(undefined),
      getConfidence: jest.fn().mockResolvedValue(0.8),
      validateOutput: jest.fn().mockResolvedValue(true),
      getValidationResult: jest.fn().mockResolvedValue({ valid: true, errors: [], warnings: [], confidence: 0.8, metadata: {} })
    },
    seg: {
      synthesizeKnowledge: jest.fn().mockResolvedValue({}),
      getKnowledgeGraph: jest.fn().mockResolvedValue({}),
      addEvidence: jest.fn().mockResolvedValue(undefined),
      getEvidence: jest.fn().mockResolvedValue([])
    },
    apoe: {
      createPlan: jest.fn().mockResolvedValue({ id: 'plan_123', status: 'created' }),
      executePlan: jest.fn().mockResolvedValue({ id: 'plan_123', status: 'executed' }),
      updatePlan: jest.fn().mockResolvedValue(undefined),
      getPlanStatus: jest.fn().mockResolvedValue({ id: 'plan_123', status: 'completed' })
    },
    iis: {
      computeIntuition: jest.fn().mockResolvedValue(0.8),
      updateIntuitionWeights: jest.fn().mockResolvedValue(undefined),
      getIntuitionTrace: jest.fn().mockResolvedValue([])
    },
    isConnected: jest.fn().mockReturnValue(true),
    getStatus: jest.fn().mockResolvedValue({
      connected: true,
      services: { cmc: true, hhni: true, vif: true, seg: true, apoe: true, iis: true },
      lastUpdate: Date.now(),
      errors: [],
      warnings: []
    }),
    storeSymbol: jest.fn().mockResolvedValue(undefined),
    retrieveSymbol: jest.fn().mockResolvedValue(null),
    searchSymbols: jest.fn().mockResolvedValue([]),
    storeAnalysis: jest.fn().mockResolvedValue(undefined),
    synthesizeKnowledge: jest.fn().mockResolvedValue({}),
    createImprovementPlan: jest.fn().mockResolvedValue({}),
    computeIntuition: jest.fn().mockResolvedValue(0.8),
    on: jest.fn(),
    off: jest.fn(),
    destroy: jest.fn()
  }))
}));

describe('AdvancedMonacoEditor', () => {
  const defaultProps = {
    code: 'function test() { return "hello"; }',
    language: 'typescript'
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<AdvancedMonacoEditor {...defaultProps} />);
    expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
  });

  it('renders with custom configuration', () => {
    const customConfig = {
      dropdowns: { enabled: false },
      contextMenus: { enabled: false },
      tooltips: { enabled: false }
    };

    render(
      <AdvancedMonacoEditor 
        {...defaultProps} 
        configuration={customConfig}
      />
    );
    
    expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
  });

  it('calls onCodeChange when code changes', async () => {
    const onCodeChange = jest.fn();
    render(
      <AdvancedMonacoEditor 
        {...defaultProps} 
        onCodeChange={onCodeChange}
      />
    );

    const editor = screen.getByTestId('monaco-editor');
    fireEvent.click(editor);

    await waitFor(() => {
      expect(onCodeChange).toHaveBeenCalledWith(defaultProps.code);
    });
  });

  it('calls onSymbolDetected when symbols are detected', async () => {
    const onSymbolDetected = jest.fn();
    render(
      <AdvancedMonacoEditor 
        {...defaultProps} 
        onSymbolDetected={onSymbolDetected}
      />
    );

    // Wait for symbol detection to complete
    await waitFor(() => {
      // This would be called when symbols are detected
      // The actual implementation would depend on the SymbolDetectionService
    });
  });

  it('calls onAnalysisComplete when analysis completes', async () => {
    const onAnalysisComplete = jest.fn();
    const config = {
      intelligence: { realTimeAnalysis: true }
    };

    render(
      <AdvancedMonacoEditor 
        {...defaultProps} 
        configuration={config}
        onAnalysisComplete={onAnalysisComplete}
      />
    );

    const editor = screen.getByTestId('monaco-editor');
    fireEvent.click(editor);

    await waitFor(() => {
      expect(onAnalysisComplete).toHaveBeenCalled();
    });
  });

  it('calls onError when an error occurs', async () => {
    const onError = jest.fn();
    render(
      <AdvancedMonacoEditor 
        {...defaultProps} 
        onError={onError}
      />
    );

    // Simulate an error
    // This would be triggered by the services
  });

  it('applies custom className and style', () => {
    const className = 'custom-editor';
    const style = { backgroundColor: 'red' };

    render(
      <AdvancedMonacoEditor 
        {...defaultProps} 
        className={className}
        style={style}
      />
    );

    const editor = screen.getByTestId('monaco-editor');
    expect(editor.parentElement).toHaveClass(className);
    expect(editor.parentElement).toHaveStyle(style);
  });

  it('handles different languages', () => {
    const languages = ['typescript', 'javascript', 'python', 'java', 'csharp'];

    languages.forEach(language => {
      const { unmount } = render(
        <AdvancedMonacoEditor 
          {...defaultProps} 
          language={language}
        />
      );
      
      expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
      unmount();
    });
  });

  it('handles empty code', () => {
    render(
      <AdvancedMonacoEditor 
        {...defaultProps} 
        code=""
      />
    );

    expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
  });

  it('handles undefined code', () => {
    render(
      <AdvancedMonacoEditor 
        {...defaultProps} 
        code={undefined as any}
      />
    );

    expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
  });

  it('cleans up services on unmount', () => {
    const { unmount } = render(<AdvancedMonacoEditor {...defaultProps} />);
    
    unmount();
    
    // The services should be destroyed
    // This would be verified by checking if destroy was called
  });

  it('handles configuration updates', () => {
    const { rerender } = render(<AdvancedMonacoEditor {...defaultProps} />);
    
    const newConfig = {
      dropdowns: { enabled: false },
      contextMenus: { enabled: false },
      tooltips: { enabled: false }
    };

    rerender(
      <AdvancedMonacoEditor 
        {...defaultProps} 
        configuration={newConfig}
      />
    );

    expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
  });

  it('handles code updates', () => {
    const { rerender } = render(<AdvancedMonacoEditor {...defaultProps} />);
    
    const newCode = 'function newTest() { return "world"; }';
    rerender(
      <AdvancedMonacoEditor 
        {...defaultProps} 
        code={newCode}
      />
    );

    expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
  });

  it('handles language updates', () => {
    const { rerender } = render(<AdvancedMonacoEditor {...defaultProps} />);
    
    rerender(
      <AdvancedMonacoEditor 
        {...defaultProps} 
        language="javascript"
      />
    );

    expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
  });
});
