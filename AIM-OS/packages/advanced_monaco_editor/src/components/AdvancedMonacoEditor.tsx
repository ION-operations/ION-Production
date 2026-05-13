/**
 * Advanced Monaco Editor - Main Component
 * 
 * This is the main React component that provides advanced Monaco Editor functionality
 * with AI-driven intelligence, natural language descriptions, and AIM-OS integration.
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as monaco from 'monaco-editor';
import { Editor } from '@monaco-editor/react';
import { SymbolDetectionService } from '../services/SymbolDetectionService';
import { CodeAnalysisService } from '../services/CodeAnalysisService';
import { AIMOSIntegrationService } from '../services/AIMOSIntegrationService';
import { ThemeManager } from '../themes/ThemeManager';
import { ThemeService } from '../services/ThemeService';
import { ThemeSelector } from './ThemeSelector';
import { PerformanceService } from '../services/PerformanceService';
import { LazyLoadingService } from '../services/LazyLoadingService';
import { ResourceOptimizationService } from '../services/ResourceOptimizationService';
import { SecurityService } from '../services/SecurityService';
import { ValidationService } from '../services/ValidationService';
import { 
  AdvancedMonacoConfiguration, 
  SymbolInfo, 
  CodeAnalysis, 
  DropdownInfo, 
  ContextMenuInfo, 
  TooltipInfo,
  Position,
  Range
} from '../types/MonacoTypes';
import { AIMOSConfiguration } from '../types/IntegrationTypes';
import './AdvancedMonacoEditor.css';

/**
 * Props for the Advanced Monaco Editor component
 */
export interface AdvancedMonacoEditorProps {
  code: string;
  language?: string;
  configuration?: AdvancedMonacoConfiguration;
  onCodeChange?: (code: string) => void;
  onSymbolDetected?: (symbol: SymbolInfo) => void;
  onAnalysisComplete?: (analysis: CodeAnalysis) => void;
  onError?: (error: Error) => void;
  onThemeChange?: (themeId: string) => void;
  showThemeSelector?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

/**
 * Advanced Monaco Editor component
 */
export const AdvancedMonacoEditor: React.FC<AdvancedMonacoEditorProps> = ({
  code,
  language = 'typescript',
  configuration,
  onCodeChange,
  onSymbolDetected,
  onAnalysisComplete,
  onError,
  onThemeChange,
  showThemeSelector = true,
  className,
  style
}) => {
  // State
  const [editor, setEditor] = useState<monaco.editor.IStandaloneCodeEditor | null>(null);
  const [symbols, setSymbols] = useState<SymbolInfo[]>([]);
  const [analysis, setAnalysis] = useState<CodeAnalysis | null>(null);
  const [dropdown, setDropdown] = useState<DropdownInfo | null>(null);
  const [contextMenu, setContextMenu] = useState<ContextMenuInfo | null>(null);
  const [tooltip, setTooltip] = useState<TooltipInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [currentTheme, setCurrentTheme] = useState<string>('default-dark');

  // Refs
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const symbolDetectionServiceRef = useRef<SymbolDetectionService | null>(null);
  const codeAnalysisServiceRef = useRef<CodeAnalysisService | null>(null);
  const aimosIntegrationServiceRef = useRef<AIMOSIntegrationService | null>(null);
  const themeManagerRef = useRef<ThemeManager | null>(null);
  const themeServiceRef = useRef<ThemeService | null>(null);
  const performanceServiceRef = useRef<PerformanceService | null>(null);
  const lazyLoadingServiceRef = useRef<LazyLoadingService | null>(null);
  const resourceOptimizationServiceRef = useRef<ResourceOptimizationService | null>(null);
  const securityServiceRef = useRef<SecurityService | null>(null);
  const validationServiceRef = useRef<ValidationService | null>(null);
  const dropdownRef = useRef<HTMLDivElement | null>(null);
  const contextMenuRef = useRef<HTMLDivElement | null>(null);
  const tooltipRef = useRef<HTMLDivElement | null>(null);

  // Default configuration
  const defaultConfig: AdvancedMonacoConfiguration = {
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
      analysisDepth: 'medium',
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
      maxAnalysisTime: 5000,
      maxMemoryUsage: 100 * 1024 * 1024, // 100MB
      enableProfiling: false,
      enableMetrics: true,
      enableOptimizations: true,
      enableLazyLoading: true,
      enableProgressiveLoading: true,
      workerThreads: 2,
      batchSize: 10
    },
    security: {
      enableSandboxing: true,
      maxCodeSize: 1024 * 1024, // 1MB
      enableValidation: true,
      enableEncryption: false,
      enableAccessControl: true,
      allowedDomains: ['localhost'],
      blockedDomains: [],
      enableDataProtection: true,
      enableAuditLogging: false,
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

  // Merge configuration
  const finalConfig = { ...defaultConfig, ...configuration };

  /**
   * Initialize services
   */
  const initializeServices = useCallback(async () => {
    if (!editor) return;

    try {
      setLoading(true);

      // Initialize theme manager and service
      themeManagerRef.current = new ThemeManager({
        defaultTheme: 'default-dark',
        autoDetect: true,
        persistTheme: true,
        accessibility: {
          highContrast: false,
          reducedMotion: false,
          fontSize: 'medium'
        }
      });

      themeServiceRef.current = new ThemeService(themeManagerRef.current, {
        storageKey: 'advanced-monaco-editor-themes',
        autoSave: true,
        autoLoad: true,
        validateThemes: true,
        migrateThemes: true,
        syncThemes: false
      });

      // Set up theme change handler
      themeManagerRef.current.on('themeChanged', ({ current }) => {
        setCurrentTheme(current);
        onThemeChange?.(current);
      });

      // Set Monaco editor theme
      themeManagerRef.current.setMonacoEditor(editor);

      // Initialize performance services
      performanceServiceRef.current = new PerformanceService({
        enableMonitoring: finalConfig.performance?.enableMetrics || true,
        enableProfiling: finalConfig.performance?.enableProfiling || false,
        enableMemoryTracking: true,
        enableCpuTracking: true,
        enableRenderTracking: true,
        enableAnalysisTracking: true,
        enableCacheTracking: true,
        enableLazyLoading: finalConfig.performance?.enableLazyLoading || true,
        maxMemoryUsage: finalConfig.performance?.maxMemoryUsage || 100 * 1024 * 1024,
        maxCpuUsage: 80,
        maxRenderTime: finalConfig.performance?.maxAnalysisTime || 16,
        maxAnalysisTime: finalConfig.performance?.maxAnalysisTime || 100,
        minCacheHitRate: 70,
        monitoringInterval: 1000,
        profilingInterval: 5000,
        maxMetricsHistory: 1000,
        enableAlerts: true,
        alertThresholds: {
          memory: 80,
          cpu: 70,
          render: 20,
          analysis: 200,
          cache: 50
        }
      });

      lazyLoadingServiceRef.current = new LazyLoadingService({
        enabled: finalConfig.performance?.enableLazyLoading || true,
        preloadThreshold: 100,
        loadTimeout: 5000,
        maxConcurrentLoads: finalConfig.performance?.workerThreads || 3,
        retryAttempts: 3,
        retryDelay: 1000,
        cacheEnabled: finalConfig.intelligence?.cacheEnabled || true,
        cacheSize: finalConfig.intelligence?.cacheSize || 50,
        cacheTimeout: finalConfig.intelligence?.cacheTimeout || 300000,
        enablePreloading: true,
        enableIntersectionObserver: true,
        enableResourceHints: true,
        enableServiceWorker: false
      });

      resourceOptimizationServiceRef.current = new ResourceOptimizationService({
        enableImageOptimization: true,
        enableFontOptimization: true,
        enableCssOptimization: true,
        enableJsOptimization: true,
        enableBundleOptimization: true,
        enableNetworkOptimization: true,
        enableMemoryOptimization: true,
        imageQuality: 80,
        imageFormat: 'auto',
        fontDisplay: 'swap',
        cssMinification: true,
        jsMinification: true,
        bundleSplitting: true,
        treeShaking: true,
        compressionLevel: 6,
        cacheStrategy: 'moderate',
        preloadCriticalResources: true,
        lazyLoadNonCriticalResources: true,
        enableServiceWorker: false,
        enableCDN: false
      });

      // Start performance monitoring
      performanceServiceRef.current.startMonitoring();

      // Set up performance event handlers
      performanceServiceRef.current.on('alert', (alert) => {
        console.warn('Performance alert:', alert);
      });

      performanceServiceRef.current.on('metricsCollected', (metrics) => {
        // Log performance metrics if needed
        if (finalConfig.performance?.enableMetrics) {
          console.log('Performance metrics:', metrics);
        }
      });

      // Initialize security service
      securityServiceRef.current = new SecurityService({
        enableInputValidation: finalConfig.security?.enableValidation || true,
        enableXSSProtection: true,
        enableCSRFProtection: true,
        enableCSP: true,
        enableAccessControl: finalConfig.security?.enableAccessControl || true,
        enableAuditLogging: finalConfig.security?.enableAuditLogging || false,
        enableThreatDetection: true,
        enableDataEncryption: finalConfig.security?.enableEncryption || false,
        enableSandboxing: finalConfig.security?.enableSandboxing || true,
        maxCodeSize: finalConfig.security?.maxCodeSize || 1024 * 1024,
        allowedDomains: finalConfig.security?.allowedDomains || ['localhost'],
        blockedDomains: finalConfig.security?.blockedDomains || [],
        allowedFileTypes: ['.js', '.ts', '.jsx', '.tsx', '.json', '.md'],
        blockedFileTypes: ['.exe', '.bat', '.cmd', '.scr', '.pif'],
        maxFileSize: 10 * 1024 * 1024,
        enableRateLimiting: true,
        rateLimitWindow: 60000,
        rateLimitMaxRequests: 100,
        enableContentFiltering: true,
        blockedPatterns: [
          /<script[^>]*>.*?<\/script>/gi,
          /javascript:/gi,
          /on\w+\s*=/gi,
          /eval\s*\(/gi,
          /expression\s*\(/gi
        ],
        enableDataProtection: finalConfig.security?.enableDataProtection || true,
        enablePrivacyMode: finalConfig.security?.enablePrivacyMode || false,
        enableSecureStorage: false,
        auditLogLevel: 'medium'
      });

      // Set up security event handlers
      securityServiceRef.current.on('securityEvent', (event) => {
        console.warn('Security event:', event);
      });

      // Initialize validation service
      validationServiceRef.current = new ValidationService({
        enableRealTimeValidation: true,
        enableBatchValidation: true,
        enableAsyncValidation: true,
        enableCaching: finalConfig.intelligence?.cacheEnabled || true,
        cacheSize: finalConfig.intelligence?.cacheSize || 1000,
        cacheTimeout: finalConfig.intelligence?.cacheTimeout || 300000,
        maxValidationTime: finalConfig.performance?.maxAnalysisTime || 5000,
        enableParallelValidation: true,
        maxParallelValidations: finalConfig.performance?.workerThreads || 5,
        enableValidationProfiling: false,
        enableValidationMetrics: true,
        validationTimeout: 10000,
        retryAttempts: 3,
        retryDelay: 1000
      });

      // Set up validation event handlers
      validationServiceRef.current.on('ruleAdded', (rule) => {
        console.log('Validation rule added:', rule.name);
      });

      validationServiceRef.current.on('ruleRemoved', (ruleId) => {
        console.log('Validation rule removed:', ruleId);
      });

      // Initialize symbol detection service
      symbolDetectionServiceRef.current = new SymbolDetectionService(editor, {
        language,
        enableRealTimeDetection: finalConfig.intelligence?.realTimeAnalysis || false,
        enableBackgroundDetection: finalConfig.intelligence?.backgroundAnalysis || false,
        cacheEnabled: finalConfig.intelligence?.cacheEnabled || false,
        cacheSize: finalConfig.intelligence?.cacheSize || 100,
        cacheTimeout: finalConfig.intelligence?.cacheTimeout || 300000
      });

      symbolDetectionServiceRef.current.on('symbols-detected', (detectedSymbols: SymbolInfo[]) => {
        setSymbols(detectedSymbols);
        detectedSymbols.forEach(symbol => {
          onSymbolDetected?.(symbol);
        });
      });

      symbolDetectionServiceRef.current.on('error', (error: any) => {
        console.error('Symbol Detection Error:', error);
        onError?.(error);
      });

      // Initialize code analysis service
      codeAnalysisServiceRef.current = new CodeAnalysisService({
        enableRealTimeAnalysis: finalConfig.intelligence?.realTimeAnalysis || false,
        enableBackgroundAnalysis: finalConfig.intelligence?.backgroundAnalysis || false,
        analysisDepth: finalConfig.intelligence?.analysisDepth || 'medium',
        cacheEnabled: finalConfig.intelligence?.cacheEnabled || false,
        cacheSize: finalConfig.intelligence?.cacheSize || 100,
        cacheTimeout: finalConfig.intelligence?.cacheTimeout || 300000,
        maxAnalysisTime: finalConfig.performance?.maxAnalysisTime || 5000,
        maxMemoryUsage: finalConfig.performance?.maxMemoryUsage || 100 * 1024 * 1024,
        enableProfiling: finalConfig.performance?.enableProfiling || false,
        enableMetrics: finalConfig.performance?.enableMetrics || true,
        enableOptimizations: finalConfig.performance?.enableOptimizations || true,
        enableLazyLoading: finalConfig.performance?.enableLazyLoading || true,
        enableProgressiveLoading: finalConfig.performance?.enableProgressiveLoading || true,
        workerThreads: finalConfig.performance?.workerThreads || 2,
        batchSize: finalConfig.performance?.batchSize || 10
      });

      codeAnalysisServiceRef.current.on('analysis-completed', (analysis: CodeAnalysis) => {
        setAnalysis(analysis);
        onAnalysisComplete?.(analysis);
      });

      codeAnalysisServiceRef.current.on('error', (error: any) => {
        console.error('Code Analysis Error:', error);
        onError?.(error);
      });

      // Initialize AIM-OS integration service
      aimosIntegrationServiceRef.current = new AIMOSIntegrationService(finalConfig.aimos!);
      aimosIntegrationServiceRef.current.on('error', (error: any) => {
        console.error('AIM-OS Integration Error:', error);
        onError?.(error);
      });

      aimosIntegrationServiceRef.current.on('connected', () => {
        console.log('AIM-OS Integration connected');
      });

      aimosIntegrationServiceRef.current.on('disconnected', () => {
        console.log('AIM-OS Integration disconnected');
      });

      // Store symbols in AIM-OS
      if (finalConfig.intelligence?.aimosIntegration) {
        const detectedSymbols = await symbolDetectionServiceRef.current.detectSymbols();
        for (const symbol of detectedSymbols) {
          await aimosIntegrationServiceRef.current.storeSymbol(symbol);
        }
      }

      // Perform initial analysis
      if (finalConfig.intelligence?.realTimeAnalysis) {
        const initialAnalysis = await codeAnalysisServiceRef.current.analyzeCode(code, language);
        setAnalysis(initialAnalysis);
        onAnalysisComplete?.(initialAnalysis);
      }

    } catch (error) {
      console.error('Failed to initialize services:', error);
      setError(error as Error);
      onError?.(error as Error);
    } finally {
      setLoading(false);
    }
  }, [editor, language, code, finalConfig, onSymbolDetected, onAnalysisComplete, onError]);

  /**
   * Handle editor mount
   */
  const handleEditorDidMount = useCallback((editor: monaco.editor.IStandaloneCodeEditor) => {
    setEditor(editor);
    editorRef.current = editor;
    initializeServices();
  }, [initializeServices]);

  /**
   * Handle code change
   */
  const handleCodeChange = useCallback((value: string | undefined) => {
    if (value !== undefined) {
      onCodeChange?.(value);
      
      // Trigger symbol detection
      if (symbolDetectionServiceRef.current) {
        symbolDetectionServiceRef.current.detectSymbols();
      }

      // Trigger code analysis if enabled
      if (finalConfig.intelligence?.realTimeAnalysis && codeAnalysisServiceRef.current) {
        setLoading(true);
        codeAnalysisServiceRef.current.analyzeCode(value, language)
          .then(analysis => {
            setAnalysis(analysis);
            onAnalysisComplete?.(analysis);
          })
          .catch(error => {
            console.error('Code analysis failed:', error);
            setError(error);
            onError?.(error);
          })
          .finally(() => {
            setLoading(false);
          });
      }
    }
  }, [onCodeChange, language, finalConfig, onAnalysisComplete, onError]);

  /**
   * Handle symbol click
   */
  const handleSymbolClick = useCallback(async (symbol: SymbolInfo) => {
    if (!finalConfig.dropdowns?.enabled) return;

    try {
      setLoading(true);

      // Get enhanced symbol information from AIM-OS if available
      let enhancedSymbol = symbol;
      if (finalConfig.intelligence?.aimosIntegration && aimosIntegrationServiceRef.current) {
        try {
          const retrievedSymbol = await aimosIntegrationServiceRef.current.retrieveSymbol(symbol.id);
          if (retrievedSymbol) {
            enhancedSymbol = { ...symbol, ...retrievedSymbol };
          }
        } catch (error) {
          console.warn('Failed to retrieve enhanced symbol from AIM-OS:', error);
        }
      }

      // Get related symbols
      let relatedSymbols: SymbolInfo[] = [];
      if (finalConfig.intelligence?.aimosIntegration && aimosIntegrationServiceRef.current) {
        try {
          relatedSymbols = await aimosIntegrationServiceRef.current.searchSymbols(symbol.name, {
            limit: 5,
            includeRelated: true,
            includeDependencies: true
          });
        } catch (error) {
          console.warn('Failed to retrieve related symbols from AIM-OS:', error);
        }
      }

      // Get code examples
      let examples: string[] = [];
      if (finalConfig.intelligence?.aimosIntegration && aimosIntegrationServiceRef.current) {
        try {
          const knowledge = await aimosIntegrationServiceRef.current.synthesizeKnowledge({
            topics: [symbol.name, symbol.type, symbol.kind],
            depth: 'medium',
            format: 'structured'
          });
          if (knowledge.examples) {
            examples = knowledge.examples;
          }
        } catch (error) {
          console.warn('Failed to retrieve examples from AIM-OS:', error);
        }
      }

      // Build comprehensive details
      const details = [
        `Type: ${enhancedSymbol.type}`,
        `Kind: ${enhancedSymbol.kind}`,
        `Language: ${enhancedSymbol.language}`,
        `Position: Line ${enhancedSymbol.position.line}, Column ${enhancedSymbol.position.column}`,
        `Complexity: ${enhancedSymbol.metadata.complexity || 'Unknown'}`,
        `Dependencies: ${enhancedSymbol.metadata.dependencies?.length || 0}`,
        `Modifiers: ${enhancedSymbol.metadata.modifiers?.join(', ') || 'None'}`,
        `Return Type: ${enhancedSymbol.metadata.returnType || 'Unknown'}`,
        `Parameters: ${enhancedSymbol.metadata.parameters?.length || 0}`
      ];

      // Build actions
      const actions = [
        {
          id: 'analyze',
          label: 'Deep Analysis',
          icon: '🔍',
          handler: async () => {
            if (codeAnalysisServiceRef.current) {
              const analysis = await codeAnalysisServiceRef.current.analyzeCode(code, language);
              console.log('Deep analysis completed:', analysis);
            }
          },
          enabled: true,
          category: 'analysis'
        },
        {
          id: 'refactor',
          label: 'Refactor',
          icon: '🔧',
          handler: () => {
            console.log('Refactoring symbol:', symbol.name);
          },
          enabled: true,
          category: 'refactor'
        },
        {
          id: 'document',
          label: 'Add Documentation',
          icon: '📝',
          handler: () => {
            console.log('Adding documentation for:', symbol.name);
          },
          enabled: true,
          category: 'documentation'
        },
        {
          id: 'find-usages',
          label: 'Find Usages',
          icon: '🔍',
          handler: () => {
            console.log('Finding usages of:', symbol.name);
          },
          enabled: true,
          category: 'navigation'
        },
        {
          id: 'go-to-definition',
          label: 'Go to Definition',
          icon: '↗️',
          handler: () => {
            console.log('Going to definition of:', symbol.name);
          },
          enabled: true,
          category: 'navigation'
        }
      ];

      // Show dropdown with enhanced symbol information
      const dropdownInfo: DropdownInfo = {
        id: `dropdown_${symbol.id}`,
        symbol: enhancedSymbol,
        position: symbol.position,
        content: {
          title: enhancedSymbol.name,
          description: enhancedSymbol.metadata.description || `A ${enhancedSymbol.type} symbol`,
          details,
          examples,
          related: relatedSymbols.map(s => ({
            id: s.id,
            name: s.name,
            type: s.type,
            kind: s.kind,
            position: s.position
          })),
          metadata: enhancedSymbol.metadata
        },
        actions,
        visible: true,
        timestamp: Date.now()
      };

      setDropdown(dropdownInfo);

      // Auto-hide after timeout
      if (finalConfig.dropdowns?.timeout) {
        setTimeout(() => {
          setDropdown(null);
        }, finalConfig.dropdowns.timeout);
      }

    } catch (error) {
      console.error('Failed to show dropdown:', error);
      onError?.(error as Error);
    } finally {
      setLoading(false);
    }
  }, [finalConfig, code, language, onError]);

  /**
   * Handle context menu
   */
  const handleContextMenu = useCallback((event: React.MouseEvent, position: Position, symbol?: SymbolInfo) => {
    if (!finalConfig.contextMenus?.enabled) return;

    event.preventDefault();

    // Build context menu actions based on symbol type and available services
    const actions = [
      {
        id: 'analyze',
        label: 'Analyze Code',
        icon: '🔍',
        shortcut: 'Ctrl+Shift+A',
        handler: () => {
          if (codeAnalysisServiceRef.current) {
            codeAnalysisServiceRef.current.analyzeCode(code, language);
          }
        },
        enabled: true,
        category: 'analysis'
      },
      {
        id: 'refactor',
        label: 'Refactor',
        icon: '🔧',
        shortcut: 'Ctrl+Shift+R',
        handler: () => {
          console.log('Refactoring...');
        },
        enabled: true,
        category: 'refactor'
      },
      {
        id: 'document',
        label: 'Add Documentation',
        icon: '📝',
        shortcut: 'Ctrl+Shift+D',
        handler: () => {
          console.log('Adding documentation...');
        },
        enabled: true,
        category: 'documentation'
      },
      {
        id: 'format',
        label: 'Format Code',
        icon: '✨',
        shortcut: 'Shift+Alt+F',
        handler: () => {
          if (editor) {
            editor.getAction('editor.action.formatDocument')?.run();
          }
        },
        enabled: true,
        category: 'formatting'
      },
      {
        id: 'find-usages',
        label: 'Find Usages',
        icon: '🔍',
        shortcut: 'Shift+F12',
        handler: () => {
          console.log('Finding usages...');
        },
        enabled: !!symbol,
        category: 'navigation'
      },
      {
        id: 'go-to-definition',
        label: 'Go to Definition',
        icon: '↗️',
        shortcut: 'F12',
        handler: () => {
          console.log('Going to definition...');
        },
        enabled: !!symbol,
        category: 'navigation'
      },
      {
        id: 'rename',
        label: 'Rename Symbol',
        icon: '✏️',
        shortcut: 'F2',
        handler: () => {
          if (editor && symbol) {
            editor.getAction('editor.action.rename')?.run();
          }
        },
        enabled: !!symbol,
        category: 'refactor'
      },
      {
        id: 'extract-method',
        label: 'Extract Method',
        icon: '🔧',
        shortcut: 'Ctrl+Shift+M',
        handler: () => {
          console.log('Extracting method...');
        },
        enabled: !!symbol && symbol.type === 'function',
        category: 'refactor'
      },
      {
        id: 'extract-variable',
        label: 'Extract Variable',
        icon: '🔧',
        shortcut: 'Ctrl+Shift+V',
        handler: () => {
          console.log('Extracting variable...');
        },
        enabled: !!symbol && symbol.type === 'variable',
        category: 'refactor'
      },
      {
        id: 'generate-tests',
        label: 'Generate Tests',
        icon: '🧪',
        shortcut: 'Ctrl+Shift+T',
        handler: () => {
          console.log('Generating tests...');
        },
        enabled: !!symbol && symbol.type === 'function',
        category: 'testing'
      },
      {
        id: 'generate-docs',
        label: 'Generate Documentation',
        icon: '📚',
        shortcut: 'Ctrl+Shift+J',
        handler: () => {
          console.log('Generating documentation...');
        },
        enabled: !!symbol,
        category: 'documentation'
      },
      {
        id: 'optimize',
        label: 'Optimize Code',
        icon: '⚡',
        shortcut: 'Ctrl+Shift+O',
        handler: () => {
          console.log('Optimizing code...');
        },
        enabled: true,
        category: 'optimization'
      },
      {
        id: 'security-scan',
        label: 'Security Scan',
        icon: '🔒',
        shortcut: 'Ctrl+Shift+S',
        handler: () => {
          console.log('Running security scan...');
        },
        enabled: true,
        category: 'security'
      },
      {
        id: 'performance-analysis',
        label: 'Performance Analysis',
        icon: '📊',
        shortcut: 'Ctrl+Shift+P',
        handler: () => {
          console.log('Running performance analysis...');
        },
        enabled: true,
        category: 'performance'
      }
    ];

    // Filter actions based on configuration
    const filteredActions = actions.filter(action => {
      if (finalConfig.contextMenus?.maxItems && actions.indexOf(action) >= finalConfig.contextMenus.maxItems) {
        return false;
      }
      return action.enabled;
    });

    // Group actions if enabled
    const groupedActions = finalConfig.contextMenus?.grouping ? 
      filteredActions.reduce((groups, action) => {
        if (!groups[action.category]) {
          groups[action.category] = [];
        }
        groups[action.category].push(action);
        return groups;
      }, {} as Record<string, typeof filteredActions>) : 
      { 'all': filteredActions };

    const contextMenuInfo: ContextMenuInfo = {
      id: `context_${Date.now()}`,
      position,
      symbol,
      actions: filteredActions,
      groupedActions,
      visible: true,
      timestamp: Date.now()
    };

    setContextMenu(contextMenuInfo);
  }, [finalConfig, code, language, editor]);

  /**
   * Handle tooltip
   */
  const handleTooltip = useCallback(async (position: Position, symbol?: SymbolInfo) => {
    if (!finalConfig.tooltips?.enabled) return;

    try {
      // Get enhanced symbol information from AIM-OS if available
      let enhancedSymbol = symbol;
      if (finalConfig.intelligence?.aimosIntegration && aimosIntegrationServiceRef.current && symbol) {
        try {
          const retrievedSymbol = await aimosIntegrationServiceRef.current.retrieveSymbol(symbol.id);
          if (retrievedSymbol) {
            enhancedSymbol = { ...symbol, ...retrievedSymbol };
          }
        } catch (error) {
          console.warn('Failed to retrieve enhanced symbol from AIM-OS:', error);
        }
      }

      // Get natural language description
      let naturalLanguageDescription = enhancedSymbol?.metadata.description || 'Hover for more information';
      if (finalConfig.intelligence?.naturalLanguage && aimosIntegrationServiceRef.current && enhancedSymbol) {
        try {
          const description = await aimosIntegrationServiceRef.current.getNaturalLanguageDescription(enhancedSymbol.id);
          if (description) {
            naturalLanguageDescription = description;
          }
        } catch (error) {
          console.warn('Failed to retrieve natural language description from AIM-OS:', error);
        }
      }

      // Get additional metadata
      const additionalMetadata = {
        complexity: enhancedSymbol?.metadata.complexity || 'Unknown',
        dependencies: enhancedSymbol?.metadata.dependencies?.length || 0,
        modifiers: enhancedSymbol?.metadata.modifiers?.join(', ') || 'None',
        returnType: enhancedSymbol?.metadata.returnType || 'Unknown',
        parameters: enhancedSymbol?.metadata.parameters?.length || 0,
        securityLevel: enhancedSymbol?.metadata.securityLevel || 'Unknown',
        performance: enhancedSymbol?.metadata.performance || 'Unknown',
        quality: enhancedSymbol?.metadata.quality || 'Unknown'
      };

      const tooltipInfo: TooltipInfo = {
        id: `tooltip_${Date.now()}`,
        position,
        symbol: enhancedSymbol,
        content: {
          title: enhancedSymbol?.name || 'Code Information',
          description: naturalLanguageDescription,
          type: enhancedSymbol?.type || 'unknown',
          value: enhancedSymbol?.name,
          documentation: enhancedSymbol?.metadata.documentation,
          metadata: {
            ...enhancedSymbol?.metadata || {},
            ...additionalMetadata
          }
        },
        visible: true,
        timestamp: Date.now()
      };

      setTooltip(tooltipInfo);

      // Auto-hide after timeout
      if (finalConfig.tooltips?.timeout) {
        setTimeout(() => {
          setTooltip(null);
        }, finalConfig.tooltips.timeout);
      }

    } catch (error) {
      console.error('Failed to show tooltip:', error);
      onError?.(error as Error);
    }
  }, [finalConfig, onError]);

  /**
   * Hide dropdown
   */
  const hideDropdown = useCallback(() => {
    setDropdown(null);
  }, []);

  /**
   * Hide context menu
   */
  const hideContextMenu = useCallback(() => {
    setContextMenu(null);
  }, []);

  /**
   * Hide tooltip
   */
  const hideTooltip = useCallback(() => {
    setTooltip(null);
  }, []);

  /**
   * Handle click outside
   */
  const handleClickOutside = useCallback((event: MouseEvent) => {
    if (finalConfig.dropdowns?.closeOnClickOutside && dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
      hideDropdown();
    }
    if (finalConfig.contextMenus?.closeOnClickOutside && contextMenuRef.current && !contextMenuRef.current.contains(event.target as Node)) {
      hideContextMenu();
    }
    if (finalConfig.tooltips?.closeOnClickOutside && tooltipRef.current && !tooltipRef.current.contains(event.target as Node)) {
      hideTooltip();
    }
  }, [finalConfig, hideDropdown, hideContextMenu, hideTooltip]);

  /**
   * Handle escape key
   */
  const handleEscape = useCallback((event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      if (finalConfig.dropdowns?.closeOnEscape) hideDropdown();
      if (finalConfig.contextMenus?.closeOnEscape) hideContextMenu();
      if (finalConfig.tooltips?.closeOnEscape) hideTooltip();
    }
  }, [finalConfig, hideDropdown, hideContextMenu, hideTooltip]);

  // Effects
  useEffect(() => {
    document.addEventListener('click', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('click', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [handleClickOutside, handleEscape]);

  useEffect(() => {
    return () => {
      // Cleanup services
      symbolDetectionServiceRef.current?.destroy();
      codeAnalysisServiceRef.current?.destroy();
      aimosIntegrationServiceRef.current?.destroy();
      themeManagerRef.current?.destroy();
      themeServiceRef.current?.destroy();
      performanceServiceRef.current?.destroy();
      lazyLoadingServiceRef.current?.destroy();
      resourceOptimizationServiceRef.current?.destroy();
      securityServiceRef.current?.destroy();
      validationServiceRef.current?.destroy();
    };
  }, []);

  return (
    <div className={`advanced-monaco-editor ${className || ''}`} style={style}>
      {/* Theme Selector */}
      {showThemeSelector && themeManagerRef.current && (
        <div className="theme-selector-container">
          <ThemeSelector
            themeManager={themeManagerRef.current}
            onThemeChange={(theme) => {
              setCurrentTheme(theme.id);
              onThemeChange?.(theme.id);
            }}
            onConfigChange={(config) => {
              console.log('Theme config changed:', config);
            }}
            showAccessibility={true}
            showCustomThemes={true}
            showPreview={true}
          />
        </div>
      )}

      {/* Monaco Editor */}
      <Editor
        height="100%"
        language={language}
        value={code}
        onChange={handleCodeChange}
        onMount={handleEditorDidMount}
        options={finalConfig.editor}
        theme={currentTheme}
      />

      {/* Loading indicator */}
      {loading && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <span>Analyzing code...</span>
        </div>
      )}

      {/* Error indicator */}
      {error && (
        <div className="error-indicator">
          <span>Error: {error.message}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* Dropdown */}
      {dropdown && (
        <div
          ref={dropdownRef}
          className="symbol-dropdown"
          style={{
            position: 'absolute',
            top: `${dropdown.position.line * 20 + 20}px`,
            left: `${dropdown.position.column * 8 + 20}px`,
            maxWidth: finalConfig.dropdowns?.maxWidth || 400,
            maxHeight: finalConfig.dropdowns?.maxHeight || 300
          }}
        >
          <div className="dropdown-header">
            <h3>{dropdown.content.title}</h3>
            <button onClick={hideDropdown}>×</button>
          </div>
          <div className="dropdown-content">
            <p>{dropdown.content.description}</p>
            <ul>
              {dropdown.content.details.map((detail, index) => (
                <li key={index}>{detail}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Context Menu */}
      {contextMenu && (
        <div
          ref={contextMenuRef}
          className="context-menu"
          style={{
            position: 'absolute',
            top: `${contextMenu.position.line * 20 + 20}px`,
            left: `${contextMenu.position.column * 8 + 20}px`
          }}
        >
          {finalConfig.contextMenus?.grouping && contextMenu.groupedActions ? (
            Object.entries(contextMenu.groupedActions).map(([category, actions]) => (
              <div key={category} className="context-menu-group">
                <div className="context-menu-group-header">
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </div>
                {actions.map(action => (
                  <button
                    key={action.id}
                    className="context-menu-item"
                    onClick={action.handler}
                    disabled={!action.enabled}
                  >
                    {finalConfig.contextMenus?.icons && action.icon && (
                      <span className="icon">{action.icon}</span>
                    )}
                    <span className="label">{action.label}</span>
                    {finalConfig.contextMenus?.shortcuts && action.shortcut && (
                      <span className="shortcut">{action.shortcut}</span>
                    )}
                  </button>
                ))}
              </div>
            ))
          ) : (
            contextMenu.actions.map(action => (
              <button
                key={action.id}
                className="context-menu-item"
                onClick={action.handler}
                disabled={!action.enabled}
              >
                {finalConfig.contextMenus?.icons && action.icon && (
                  <span className="icon">{action.icon}</span>
                )}
                <span className="label">{action.label}</span>
                {finalConfig.contextMenus?.shortcuts && action.shortcut && (
                  <span className="shortcut">{action.shortcut}</span>
                )}
              </button>
            ))
          )}
        </div>
      )}

      {/* Tooltip */}
      {tooltip && (
        <div
          ref={tooltipRef}
          className="tooltip"
          style={{
            position: 'absolute',
            top: `${tooltip.position.line * 20 + 20}px`,
            left: `${tooltip.position.column * 8 + 20}px`,
            maxWidth: finalConfig.tooltips?.maxWidth || 300
          }}
        >
          <div className="tooltip-header">
            <h4>{tooltip.content.title}</h4>
          </div>
          <div className="tooltip-content">
            <p>{tooltip.content.description}</p>
            {tooltip.content.documentation && (
              <p className="documentation">{tooltip.content.documentation}</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvancedMonacoEditor;
