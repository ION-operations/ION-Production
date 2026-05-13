/**
 * Advanced Monaco Editor - AIM-OS Integration Example
 * 
 * This example demonstrates the advanced usage of the Advanced Monaco Editor
 * with full AIM-OS integration and intelligent features.
 */

import React, { useState, useEffect, useRef } from 'react';
import { 
  AdvancedMonacoEditor, 
  AdvancedMonacoConfiguration,
  SymbolDetectionService,
  CodeAnalysisService,
  AIMOSIntegrationService,
  SymbolInfo,
  CodeAnalysis
} from '../src';

const AIMOSExample: React.FC = () => {
  const [code, setCode] = useState(`/**
 * AIM-OS Integration Example
 * 
 * This example demonstrates the advanced usage of the Advanced Monaco Editor
 * with full AIM-OS integration and intelligent features.
 */

import { CMCService } from '@aim-os/cmc';
import { HHNIService } from '@aim-os/hhni';
import { VIFService } from '@aim-os/vif';

interface AIMOSConfig {
  cmc: CMCService;
  hhni: HHNIService;
  vif: VIFService;
}

class AIMOSIntegration {
  private config: AIMOSConfig;
  private isConnected: boolean = false;

  constructor(config: AIMOSConfig) {
    this.config = config;
  }

  /**
   * Initialize the AIM-OS integration
   * @returns Promise that resolves when initialization is complete
   */
  async initialize(): Promise<void> {
    try {
      await this.config.cmc.connect();
      await this.config.hhni.connect();
      await this.config.vif.connect();
      
      this.isConnected = true;
      console.log('AIM-OS integration initialized successfully');
    } catch (error) {
      console.error('Failed to initialize AIM-OS integration:', error);
      throw error;
    }
  }

  /**
   * Store a symbol in the AIM-OS system
   * @param symbol - The symbol to store
   * @returns Promise that resolves when storage is complete
   */
  async storeSymbol(symbol: SymbolInfo): Promise<void> {
    if (!this.isConnected) {
      throw new Error('AIM-OS integration not initialized');
    }

    try {
      // Store in CMC
      await this.config.cmc.storeMemory(\`symbol_\${symbol.id}\`, symbol, {
        type: 'symbol',
        language: symbol.language,
        timestamp: Date.now()
      });

      // Index in HHNI
      await this.config.hhni.indexSymbol(symbol);

      console.log('Symbol stored successfully:', symbol.name);
    } catch (error) {
      console.error('Failed to store symbol:', error);
      throw error;
    }
  }

  /**
   * Retrieve a symbol from the AIM-OS system
   * @param symbolId - The ID of the symbol to retrieve
   * @returns Promise that resolves with the symbol or null if not found
   */
  async retrieveSymbol(symbolId: string): Promise<SymbolInfo | null> {
    if (!this.isConnected) {
      throw new Error('AIM-OS integration not initialized');
    }

    try {
      const symbol = await this.config.cmc.retrieveMemory(\`symbol_\${symbolId}\`);
      return symbol;
    } catch (error) {
      console.error('Failed to retrieve symbol:', error);
      return null;
    }
  }

  /**
   * Search for symbols in the AIM-OS system
   * @param query - The search query
   * @param limit - Maximum number of results
   * @returns Promise that resolves with the search results
   */
  async searchSymbols(query: string, limit: number = 10): Promise<SymbolInfo[]> {
    if (!this.isConnected) {
      throw new Error('AIM-OS integration not initialized');
    }

    try {
      const symbols = await this.config.hhni.searchSymbols(query, limit);
      return symbols;
    } catch (error) {
      console.error('Failed to search symbols:', error);
      return [];
    }
  }

  /**
   * Store a code analysis in the AIM-OS system
   * @param analysis - The analysis to store
   * @returns Promise that resolves when storage is complete
   */
  async storeAnalysis(analysis: CodeAnalysis): Promise<void> {
    if (!this.isConnected) {
      throw new Error('AIM-OS integration not initialized');
    }

    try {
      // Store in CMC
      await this.config.cmc.storeMemory(\`analysis_\${analysis.id}\`, analysis, {
        type: 'analysis',
        language: analysis.language,
        timestamp: analysis.timestamp
      });

      // Track confidence in VIF
      await this.config.vif.trackConfidence('code-analysis', analysis.confidence, 'Code analysis completed');

      console.log('Analysis stored successfully:', analysis.id);
    } catch (error) {
      console.error('Failed to store analysis:', error);
      throw error;
    }
  }

  /**
   * Synthesize knowledge for symbols
   * @param symbols - The symbols to synthesize knowledge for
   * @returns Promise that resolves with the synthesized knowledge
   */
  async synthesizeKnowledge(symbols: SymbolInfo[]): Promise<any> {
    if (!this.isConnected) {
      throw new Error('AIM-OS integration not initialized');
    }

    try {
      const topics = symbols.map(s => s.name);
      const knowledge = await this.config.seg.synthesizeKnowledge(topics, 'medium');
      return knowledge;
    } catch (error) {
      console.error('Failed to synthesize knowledge:', error);
      return null;
    }
  }

  /**
   * Create a plan for code improvement
   * @param analysis - The code analysis
   * @returns Promise that resolves with the improvement plan
   */
  async createImprovementPlan(analysis: CodeAnalysis): Promise<any> {
    if (!this.isConnected) {
      throw new Error('AIM-OS integration not initialized');
    }

    try {
      const goal = 'Improve code quality and maintainability';
      const context = \`Code analysis for \${analysis.language} code with \${analysis.symbols.length} symbols\`;
      const plan = await this.config.apoe.createPlan(goal, context);
      return plan;
    } catch (error) {
      console.error('Failed to create improvement plan:', error);
      return null;
    }
  }

  /**
   * Compute intuition for decision making
   * @param confidence - The confidence level
   * @param context - The context for the decision
   * @returns Promise that resolves with the intuition score
   */
  async computeIntuition(confidence: number, context: string): Promise<number> {
    if (!this.isConnected) {
      throw new Error('AIM-OS integration not initialized');
    }

    try {
      const intuition = await this.config.iis.computeIntuition(confidence, context);
      return intuition;
    } catch (error) {
      console.error('Failed to compute intuition:', error);
      return 0.5; // Default intuition
    }
  }

  /**
   * Disconnect from the AIM-OS system
   * @returns Promise that resolves when disconnection is complete
   */
  async disconnect(): Promise<void> {
    try {
      await this.config.cmc.disconnect();
      await this.config.hhni.disconnect();
      await this.config.vif.disconnect();
      
      this.isConnected = false;
      console.log('AIM-OS integration disconnected');
    } catch (error) {
      console.error('Failed to disconnect from AIM-OS:', error);
      throw error;
    }
  }
}

export default AIMOSIntegration;`);

  const [language, setLanguage] = useState('typescript');
  const [symbols, setSymbols] = useState<SymbolInfo[]>([]);
  const [analysis, setAnalysis] = useState<CodeAnalysis | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  const symbolServiceRef = useRef<SymbolDetectionService | null>(null);
  const analysisServiceRef = useRef<CodeAnalysisService | null>(null);
  const aimosServiceRef = useRef<AIMOSIntegrationService | null>(null);

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
  };

  useEffect(() => {
    // Initialize services
    analysisServiceRef.current = new CodeAnalysisService();
    aimosServiceRef.current = new AIMOSIntegrationService({
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
    });

    // Set up event listeners
    analysisServiceRef.current.on('analysis-completed', (analysis: CodeAnalysis) => {
      setAnalysis(analysis);
      addLog(`Analysis completed: ${analysis.symbols.length} symbols detected`);
    });

    aimosServiceRef.current.on('connected', () => {
      setIsConnected(true);
      addLog('AIM-OS integration connected');
    });

    aimosServiceRef.current.on('error', (error: any) => {
      addLog(`AIM-OS error: ${error.message}`);
    });

    // Check connection status
    aimosServiceRef.current.getStatus().then(status => {
      setIsConnected(status.connected);
      addLog(`AIM-OS status: ${status.connected ? 'Connected' : 'Disconnected'}`);
    });

    return () => {
      // Cleanup
      analysisServiceRef.current?.destroy();
      aimosServiceRef.current?.destroy();
    };
  }, []);

  const handleCodeChange = (newCode: string) => {
    setCode(newCode);
    addLog('Code changed');
  };

  const handleSymbolDetected = (symbol: SymbolInfo) => {
    setSymbols(prev => [...prev, symbol]);
    addLog(`Symbol detected: ${symbol.name} (${symbol.type})`);
  };

  const handleAnalysisComplete = (analysis: CodeAnalysis) => {
    setAnalysis(analysis);
    addLog(`Analysis complete: ${analysis.symbols.length} symbols, confidence: ${analysis.confidence}`);
  };

  const handleError = (error: Error) => {
    addLog(`Error: ${error.message}`);
  };

  const handleLanguageChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setLanguage(event.target.value);
    addLog(`Language changed to: ${event.target.value}`);
  };

  const analyzeCode = async () => {
    if (analysisServiceRef.current) {
      try {
        addLog('Starting code analysis...');
        const analysis = await analysisServiceRef.current.analyzeCode(code, language);
        setAnalysis(analysis);
        addLog(`Analysis complete: ${analysis.symbols.length} symbols detected`);
      } catch (error) {
        addLog(`Analysis failed: ${error}`);
      }
    }
  };

  const storeInAIMOS = async () => {
    if (aimosServiceRef.current && analysis) {
      try {
        addLog('Storing analysis in AIM-OS...');
        await aimosServiceRef.current.storeAnalysis(analysis);
        addLog('Analysis stored successfully');
      } catch (error) {
        addLog(`Failed to store analysis: ${error}`);
      }
    }
  };

  const searchSymbols = async () => {
    if (aimosServiceRef.current) {
      try {
        addLog('Searching symbols in AIM-OS...');
        const results = await aimosServiceRef.current.searchSymbols('function', 5);
        addLog(`Found ${results.length} symbols`);
      } catch (error) {
        addLog(`Search failed: ${error}`);
      }
    }
  };

  const configuration: AdvancedMonacoConfiguration = {
    dropdowns: {
      enabled: true,
      position: 'below',
      maxWidth: 400,
      maxHeight: 300,
      animation: true,
      delay: 500,
      timeout: 5000,
      autoHide: true,
      closeOnClickOutside: true,
      closeOnEscape: true
    },
    contextMenus: {
      enabled: true,
      position: 'mouse',
      maxItems: 10,
      grouping: true,
      icons: true,
      shortcuts: true,
      autoHide: true,
      closeOnClickOutside: true,
      closeOnEscape: true
    },
    tooltips: {
      enabled: true,
      position: 'mouse',
      delay: 1000,
      timeout: 3000,
      maxWidth: 300,
      animation: true,
      autoHide: true,
      closeOnClickOutside: true,
      closeOnEscape: true
    },
    intelligence: {
      enabled: true,
      analysisDepth: 'deep',
      cacheEnabled: true,
      cacheSize: 100,
      cacheTimeout: 300000,
      aimosIntegration: true,
      naturalLanguage: true,
      suggestions: true,
      actions: true,
      realTimeAnalysis: true,
      backgroundAnalysis: true
    },
    aimos: {
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
    },
    performance: {
      maxAnalysisTime: 10000,
      maxMemoryUsage: 200 * 1024 * 1024, // 200MB
      enableProfiling: true,
      enableMetrics: true,
      enableOptimizations: true,
      enableLazyLoading: true,
      enableProgressiveLoading: true,
      workerThreads: 4,
      batchSize: 20
    },
    security: {
      enableSandboxing: true,
      maxCodeSize: 2 * 1024 * 1024, // 2MB
      enableValidation: true,
      enableEncryption: false,
      enableAccessControl: true,
      allowedDomains: ['localhost'],
      blockedDomains: [],
      enableDataProtection: true,
      enableAuditLogging: true,
      enablePrivacyMode: false
    },
    theme: {
      name: 'advanced-monaco',
      base: 'vs-dark',
      colors: {},
      tokenColors: []
    },
    editor: {
      theme: 'vs-dark',
      fontSize: 14,
      fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
      lineNumbers: 'on',
      wordWrap: 'on',
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      automaticLayout: true,
      tabSize: 2,
      insertSpaces: true,
      detectIndentation: true,
      renderWhitespace: 'selection',
      renderControlCharacters: false,
      renderIndentGuides: true,
      highlightActiveIndentGuide: true,
      bracketPairColorization: { enabled: true },
      guides: {
        bracketPairs: true,
        indentation: true
      }
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '16px', borderBottom: '1px solid #333', backgroundColor: '#2d2d30' }}>
        <h1 style={{ margin: 0, color: '#fff', fontSize: '24px' }}>
          Advanced Monaco Editor - AIM-OS Integration Example
        </h1>
        <div style={{ marginTop: '8px', display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
          <label style={{ color: '#ccc', fontSize: '14px' }}>
            Language:
            <select
              value={language}
              onChange={handleLanguageChange}
              style={{
                marginLeft: '8px',
                padding: '4px 8px',
                backgroundColor: '#3e3e42',
                color: '#fff',
                border: '1px solid #4e4e52',
                borderRadius: '4px'
              }}
            >
              <option value="typescript">TypeScript</option>
              <option value="javascript">JavaScript</option>
              <option value="python">Python</option>
              <option value="java">Java</option>
              <option value="csharp">C#</option>
            </select>
          </label>
          <div style={{ color: '#888', fontSize: '12px' }}>
            Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'} | 
            Symbols: {symbols.length} | 
            Analysis: {analysis ? '✅ Complete' : '⏳ Pending'}
          </div>
        </div>
        <div style={{ marginTop: '8px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button
            onClick={analyzeCode}
            style={{
              padding: '6px 12px',
              backgroundColor: '#007acc',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            Analyze Code
          </button>
          <button
            onClick={storeInAIMOS}
            disabled={!analysis || !isConnected}
            style={{
              padding: '6px 12px',
              backgroundColor: analysis && isConnected ? '#28a745' : '#666',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              cursor: analysis && isConnected ? 'pointer' : 'not-allowed',
              fontSize: '12px'
            }}
          >
            Store in AIM-OS
          </button>
          <button
            onClick={searchSymbols}
            disabled={!isConnected}
            style={{
              padding: '6px 12px',
              backgroundColor: isConnected ? '#17a2b8' : '#666',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              cursor: isConnected ? 'pointer' : 'not-allowed',
              fontSize: '12px'
            }}
          >
            Search Symbols
          </button>
        </div>
      </div>
      
      <div style={{ flex: 1, display: 'flex' }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <AdvancedMonacoEditor
            code={code}
            language={language}
            configuration={configuration}
            onCodeChange={handleCodeChange}
            onSymbolDetected={handleSymbolDetected}
            onAnalysisComplete={handleAnalysisComplete}
            onError={handleError}
            style={{ height: '100%', width: '100%' }}
          />
        </div>
        
        <div style={{ width: '300px', borderLeft: '1px solid #333', backgroundColor: '#2d2d30', display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '12px', borderBottom: '1px solid #333', backgroundColor: '#3e3e42' }}>
            <h3 style={{ margin: 0, color: '#fff', fontSize: '14px' }}>Activity Log</h3>
          </div>
          <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
            {logs.map((log, index) => (
              <div
                key={index}
                style={{
                  fontSize: '11px',
                  color: '#ccc',
                  marginBottom: '4px',
                  padding: '2px 0',
                  borderBottom: '1px solid #3e3e42'
                }}
              >
                {log}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIMOSExample;
