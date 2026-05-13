/**
 * Advanced Monaco Editor - Symbol Detection Service
 * 
 * This service handles the detection and analysis of symbols in code.
 */

import * as monaco from 'monaco-editor';
import { SymbolInfo, SymbolType, SymbolKind, Position, Range, SymbolMetadata, ParameterInfo, Annotation, UsageInfo } from '../types/MonacoTypes';

/**
 * Symbol detection service configuration
 */
export interface SymbolDetectionConfig {
  language?: string;
  enableRealTimeDetection?: boolean;
  enableBackgroundDetection?: boolean;
  cacheEnabled?: boolean;
  cacheSize?: number;
  cacheTimeout?: number;
}

/**
 * Symbol detection service class
 */
export class SymbolDetectionService {
  private editor: monaco.editor.IStandaloneCodeEditor;
  private symbols: Map<string, SymbolInfo> = new Map();
  private listeners: Map<string, Function[]> = new Map();
  private config: SymbolDetectionConfig;
  private cache: Map<string, { symbols: SymbolInfo[], timestamp: number }> = new Map();
  private backgroundWorker?: Worker;
  private debounceTimer?: NodeJS.Timeout;

  constructor(editor: monaco.editor.IStandaloneCodeEditor, config: SymbolDetectionConfig = {}) {
    this.editor = editor;
    this.config = {
      language: 'typescript',
      enableRealTimeDetection: true,
      enableBackgroundDetection: false,
      cacheEnabled: true,
      cacheSize: 100,
      cacheTimeout: 300000,
      ...config
    };
    this.initialize();
  }

  /**
   * Initialize the symbol detection service
   */
  private initialize(): void {
    // Listen for editor changes
    if (this.config.enableRealTimeDetection) {
      this.editor.onDidChangeModelContent(() => {
        this.debouncedDetectSymbols();
      });

      this.editor.onDidChangeModel(() => {
        this.detectSymbols();
      });
    }

    // Initialize background worker if enabled
    if (this.config.enableBackgroundDetection) {
      this.initializeBackgroundWorker();
    }

    // Initial symbol detection
    this.detectSymbols();
  }

  /**
   * Debounced symbol detection
   */
  private debouncedDetectSymbols(): void {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }
    
    this.debounceTimer = setTimeout(() => {
      this.detectSymbols();
    }, 300); // 300ms debounce
  }

  /**
   * Initialize background worker for symbol detection
   */
  private initializeBackgroundWorker(): void {
    // In a real implementation, this would create a Web Worker
    // For now, we'll simulate it with a timeout
    console.log('Background worker initialized for symbol detection');
  }

  /**
   * Detect symbols in the current model
   */
  public async detectSymbols(): Promise<SymbolInfo[]> {
    const model = this.editor.getModel();
    if (!model) {
      return [];
    }

    const code = model.getValue();
    const language = model.getLanguageId();
    
    // Check cache first
    if (this.config.cacheEnabled) {
      const cacheKey = this.generateCacheKey(code, language);
      const cached = this.cache.get(cacheKey);
      
      if (cached && (Date.now() - cached.timestamp) < (this.config.cacheTimeout || 300000)) {
        this.updateSymbols(cached.symbols);
        this.emit('symbols-detected', cached.symbols);
        return cached.symbols;
      }
    }
    
    try {
      const symbols = await this.analyzeCode(code, language);
      
      // Cache the results
      if (this.config.cacheEnabled) {
        const cacheKey = this.generateCacheKey(code, language);
        this.cache.set(cacheKey, {
          symbols,
          timestamp: Date.now()
        });
        
        // Clean up old cache entries
        this.cleanupCache();
      }
      
      this.updateSymbols(symbols);
      this.emit('symbols-detected', symbols);
      return symbols;
    } catch (error) {
      this.emit('error', error);
      return [];
    }
  }

  /**
   * Generate cache key for code and language
   */
  private generateCacheKey(code: string, language: string): string {
    // Simple hash function for cache key
    let hash = 0;
    const str = code + language;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString();
  }

  /**
   * Clean up old cache entries
   */
  private cleanupCache(): void {
    if (this.cache.size > (this.config.cacheSize || 100)) {
      const now = Date.now();
      const timeout = this.config.cacheTimeout || 300000;
      
      for (const [key, value] of this.cache.entries()) {
        if (now - value.timestamp > timeout) {
          this.cache.delete(key);
        }
      }
    }
  }

  /**
   * Analyze code and extract symbols
   */
  private async analyzeCode(code: string, language: string): Promise<SymbolInfo[]> {
    const symbols: SymbolInfo[] = [];
    const lines = code.split('\n');

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const lineNumber = i + 1;

      // Detect different types of symbols based on language
      const lineSymbols = this.detectLineSymbols(line, lineNumber, language);
      symbols.push(...lineSymbols);
    }

    return symbols;
  }

  /**
   * Detect symbols in a single line
   */
  private detectLineSymbols(line: string, lineNumber: number, language: string): SymbolInfo[] {
    const symbols: SymbolInfo[] = [];
    const trimmedLine = line.trim();

    // Skip empty lines and comments
    if (!trimmedLine || trimmedLine.startsWith('//') || trimmedLine.startsWith('/*') || trimmedLine.startsWith('*')) {
      return symbols;
    }

    // Detect functions
    const functionSymbols = this.detectFunctions(line, lineNumber, language);
    symbols.push(...functionSymbols);

    // Detect classes
    const classSymbols = this.detectClasses(line, lineNumber, language);
    symbols.push(...classSymbols);

    // Detect interfaces
    const interfaceSymbols = this.detectInterfaces(line, lineNumber, language);
    symbols.push(...interfaceSymbols);

    // Detect variables
    const variableSymbols = this.detectVariables(line, lineNumber, language);
    symbols.push(...variableSymbols);

    // Detect constants
    const constantSymbols = this.detectConstants(line, lineNumber, language);
    symbols.push(...constantSymbols);

    // Detect enums
    const enumSymbols = this.detectEnums(line, lineNumber, language);
    symbols.push(...enumSymbols);

    // Detect modules
    const moduleSymbols = this.detectModules(line, lineNumber, language);
    symbols.push(...moduleSymbols);

    // Detect namespaces
    const namespaceSymbols = this.detectNamespaces(line, lineNumber, language);
    symbols.push(...namespaceSymbols);

    // Detect types
    const typeSymbols = this.detectTypes(line, lineNumber, language);
    symbols.push(...typeSymbols);

    return symbols;
  }

  /**
   * Detect function symbols
   */
  private detectFunctions(line: string, lineNumber: number, language: string): SymbolInfo[] {
    const symbols: SymbolInfo[] = [];
    const functionRegex = /(?:function\s+(\w+)|(\w+)\s*[:=]\s*(?:function|\([^)]*\)\s*=>|async\s*\([^)]*\)\s*=>)|(\w+)\s*\([^)]*\)\s*{)/g;
    let match;

    while ((match = functionRegex.exec(line)) !== null) {
      const name = match[1] || match[2] || match[3];
      if (name) {
        const symbol: SymbolInfo = {
          id: this.generateSymbolId(name, lineNumber),
          name,
          type: SymbolType.FUNCTION,
          kind: SymbolKind.DEFINITION,
          position: { line: lineNumber, column: match.index },
          range: {
            start: { line: lineNumber, column: match.index },
            end: { line: lineNumber, column: match.index + match[0].length }
          },
          language,
          metadata: this.extractFunctionMetadata(line, name)
        };
        symbols.push(symbol);
      }
    }

    return symbols;
  }

  /**
   * Detect class symbols
   */
  private detectClasses(line: string, lineNumber: number, language: string): SymbolInfo[] {
    const symbols: SymbolInfo[] = [];
    const classRegex = /(?:class\s+(\w+)|export\s+class\s+(\w+)|public\s+class\s+(\w+))/g;
    let match;

    while ((match = classRegex.exec(line)) !== null) {
      const name = match[1] || match[2] || match[3];
      if (name) {
        const symbol: SymbolInfo = {
          id: this.generateSymbolId(name, lineNumber),
          name,
          type: SymbolType.CLASS,
          kind: SymbolKind.DEFINITION,
          position: { line: lineNumber, column: match.index },
          range: {
            start: { line: lineNumber, column: match.index },
            end: { line: lineNumber, column: match.index + match[0].length }
          },
          language,
          metadata: this.extractClassMetadata(line, name)
        };
        symbols.push(symbol);
      }
    }

    return symbols;
  }

  /**
   * Detect interface symbols
   */
  private detectInterfaces(line: string, lineNumber: number, language: string): SymbolInfo[] {
    const symbols: SymbolInfo[] = [];
    const interfaceRegex = /(?:interface\s+(\w+)|export\s+interface\s+(\w+)|public\s+interface\s+(\w+))/g;
    let match;

    while ((match = interfaceRegex.exec(line)) !== null) {
      const name = match[1] || match[2] || match[3];
      if (name) {
        const symbol: SymbolInfo = {
          id: this.generateSymbolId(name, lineNumber),
          name,
          type: SymbolType.INTERFACE,
          kind: SymbolKind.DEFINITION,
          position: { line: lineNumber, column: match.index },
          range: {
            start: { line: lineNumber, column: match.index },
            end: { line: lineNumber, column: match.index + match[0].length }
          },
          language,
          metadata: this.extractInterfaceMetadata(line, name)
        };
        symbols.push(symbol);
      }
    }

    return symbols;
  }

  /**
   * Detect variable symbols
   */
  private detectVariables(line: string, lineNumber: number, language: string): SymbolInfo[] {
    const symbols: SymbolInfo[] = [];
    const variableRegex = /(?:let\s+(\w+)|var\s+(\w+)|const\s+(\w+)|(\w+)\s*[:=])/g;
    let match;

    while ((match = variableRegex.exec(line)) !== null) {
      const name = match[1] || match[2] || match[3] || match[4];
      if (name && !this.isReservedWord(name)) {
        const symbol: SymbolInfo = {
          id: this.generateSymbolId(name, lineNumber),
          name,
          type: SymbolType.VARIABLE,
          kind: SymbolKind.DEFINITION,
          position: { line: lineNumber, column: match.index },
          range: {
            start: { line: lineNumber, column: match.index },
            end: { line: lineNumber, column: match.index + match[0].length }
          },
          language,
          metadata: this.extractVariableMetadata(line, name)
        };
        symbols.push(symbol);
      }
    }

    return symbols;
  }

  /**
   * Detect constant symbols
   */
  private detectConstants(line: string, lineNumber: number, language: string): SymbolInfo[] {
    const symbols: SymbolInfo[] = [];
    const constantRegex = /(?:const\s+(\w+)|final\s+(\w+)|readonly\s+(\w+))/g;
    let match;

    while ((match = constantRegex.exec(line)) !== null) {
      const name = match[1] || match[2] || match[3];
      if (name && !this.isReservedWord(name)) {
        const symbol: SymbolInfo = {
          id: this.generateSymbolId(name, lineNumber),
          name,
          type: SymbolType.CONSTANT,
          kind: SymbolKind.DEFINITION,
          position: { line: lineNumber, column: match.index },
          range: {
            start: { line: lineNumber, column: match.index },
            end: { line: lineNumber, column: match.index + match[0].length }
          },
          language,
          metadata: this.extractConstantMetadata(line, name)
        };
        symbols.push(symbol);
      }
    }

    return symbols;
  }

  /**
   * Detect enum symbols
   */
  private detectEnums(line: string, lineNumber: number, language: string): SymbolInfo[] {
    const symbols: SymbolInfo[] = [];
    const enumRegex = /(?:enum\s+(\w+)|export\s+enum\s+(\w+)|public\s+enum\s+(\w+))/g;
    let match;

    while ((match = enumRegex.exec(line)) !== null) {
      const name = match[1] || match[2] || match[3];
      if (name) {
        const symbol: SymbolInfo = {
          id: this.generateSymbolId(name, lineNumber),
          name,
          type: SymbolType.ENUM,
          kind: SymbolKind.DEFINITION,
          position: { line: lineNumber, column: match.index },
          range: {
            start: { line: lineNumber, column: match.index },
            end: { line: lineNumber, column: match.index + match[0].length }
          },
          language,
          metadata: this.extractEnumMetadata(line, name)
        };
        symbols.push(symbol);
      }
    }

    return symbols;
  }

  /**
   * Detect module symbols
   */
  private detectModules(line: string, lineNumber: number, language: string): SymbolInfo[] {
    const symbols: SymbolInfo[] = [];
    const moduleRegex = /(?:module\s+(\w+)|export\s+module\s+(\w+)|namespace\s+(\w+))/g;
    let match;

    while ((match = moduleRegex.exec(line)) !== null) {
      const name = match[1] || match[2] || match[3];
      if (name) {
        const symbol: SymbolInfo = {
          id: this.generateSymbolId(name, lineNumber),
          name,
          type: SymbolType.MODULE,
          kind: SymbolKind.DEFINITION,
          position: { line: lineNumber, column: match.index },
          range: {
            start: { line: lineNumber, column: match.index },
            end: { line: lineNumber, column: match.index + match[0].length }
          },
          language,
          metadata: this.extractModuleMetadata(line, name)
        };
        symbols.push(symbol);
      }
    }

    return symbols;
  }

  /**
   * Detect namespace symbols
   */
  private detectNamespaces(line: string, lineNumber: number, language: string): SymbolInfo[] {
    const symbols: SymbolInfo[] = [];
    const namespaceRegex = /(?:namespace\s+(\w+)|export\s+namespace\s+(\w+))/g;
    let match;

    while ((match = namespaceRegex.exec(line)) !== null) {
      const name = match[1] || match[2];
      if (name) {
        const symbol: SymbolInfo = {
          id: this.generateSymbolId(name, lineNumber),
          name,
          type: SymbolType.NAMESPACE,
          kind: SymbolKind.DEFINITION,
          position: { line: lineNumber, column: match.index },
          range: {
            start: { line: lineNumber, column: match.index },
            end: { line: lineNumber, column: match.index + match[0].length }
          },
          language,
          metadata: this.extractNamespaceMetadata(line, name)
        };
        symbols.push(symbol);
      }
    }

    return symbols;
  }

  /**
   * Detect type symbols
   */
  private detectTypes(line: string, lineNumber: number, language: string): SymbolInfo[] {
    const symbols: SymbolInfo[] = [];
    const typeRegex = /(?:type\s+(\w+)|export\s+type\s+(\w+)|public\s+type\s+(\w+))/g;
    let match;

    while ((match = typeRegex.exec(line)) !== null) {
      const name = match[1] || match[2] || match[3];
      if (name) {
        const symbol: SymbolInfo = {
          id: this.generateSymbolId(name, lineNumber),
          name,
          type: SymbolType.TYPE,
          kind: SymbolKind.DEFINITION,
          position: { line: lineNumber, column: match.index },
          range: {
            start: { line: lineNumber, column: match.index },
            end: { line: lineNumber, column: match.index + match[0].length }
          },
          language,
          metadata: this.extractTypeMetadata(line, name)
        };
        symbols.push(symbol);
      }
    }

    return symbols;
  }

  /**
   * Extract function metadata
   */
  private extractFunctionMetadata(line: string, name: string): SymbolMetadata {
    const parameters = this.extractParameters(line);
    const returnType = this.extractReturnType(line);
    const modifiers = this.extractModifiers(line);
    const annotations = this.extractAnnotations(line);

    return {
      parameters,
      returnType,
      modifiers,
      annotations,
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract class metadata
   */
  private extractClassMetadata(line: string, name: string): SymbolMetadata {
    const modifiers = this.extractModifiers(line);
    const annotations = this.extractAnnotations(line);

    return {
      modifiers,
      annotations,
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract interface metadata
   */
  private extractInterfaceMetadata(line: string, name: string): SymbolMetadata {
    const modifiers = this.extractModifiers(line);
    const annotations = this.extractAnnotations(line);

    return {
      modifiers,
      annotations,
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract variable metadata
   */
  private extractVariableMetadata(line: string, name: string): SymbolMetadata {
    const type = this.extractVariableType(line);
    const modifiers = this.extractModifiers(line);
    const annotations = this.extractAnnotations(line);

    return {
      type,
      modifiers,
      annotations,
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract constant metadata
   */
  private extractConstantMetadata(line: string, name: string): SymbolMetadata {
    const type = this.extractVariableType(line);
    const modifiers = this.extractModifiers(line);
    const annotations = this.extractAnnotations(line);

    return {
      type,
      modifiers,
      annotations,
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract enum metadata
   */
  private extractEnumMetadata(line: string, name: string): SymbolMetadata {
    const modifiers = this.extractModifiers(line);
    const annotations = this.extractAnnotations(line);

    return {
      modifiers,
      annotations,
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract module metadata
   */
  private extractModuleMetadata(line: string, name: string): SymbolMetadata {
    const modifiers = this.extractModifiers(line);
    const annotations = this.extractAnnotations(line);

    return {
      modifiers,
      annotations,
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract namespace metadata
   */
  private extractNamespaceMetadata(line: string, name: string): SymbolMetadata {
    const modifiers = this.extractModifiers(line);
    const annotations = this.extractAnnotations(line);

    return {
      modifiers,
      annotations,
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract type metadata
   */
  private extractTypeMetadata(line: string, name: string): SymbolMetadata {
    const modifiers = this.extractModifiers(line);
    const annotations = this.extractAnnotations(line);

    return {
      modifiers,
      annotations,
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract parameters from function line
   */
  private extractParameters(line: string): ParameterInfo[] {
    const parameters: ParameterInfo[] = [];
    const paramRegex = /\(([^)]*)\)/;
    const match = line.match(paramRegex);
    
    if (match && match[1]) {
      const paramString = match[1];
      const paramParts = paramString.split(',').map(p => p.trim());
      
      for (const part of paramParts) {
        if (part) {
          const [name, type] = part.split(':').map(p => p.trim());
          const optional = part.includes('?');
          const defaultValue = part.includes('=') ? part.split('=')[1].trim() : undefined;
          
          parameters.push({
            name: name || part,
            type: type || 'any',
            optional,
            defaultValue
          });
        }
      }
    }
    
    return parameters;
  }

  /**
   * Extract return type from function line
   */
  private extractReturnType(line: string): string | undefined {
    const returnTypeRegex = /\)\s*:\s*([^{=>]+)/;
    const match = line.match(returnTypeRegex);
    return match ? match[1].trim() : undefined;
  }

  /**
   * Extract variable type from variable line
   */
  private extractVariableType(line: string): string | undefined {
    const typeRegex = /:\s*([^=;]+)/;
    const match = line.match(typeRegex);
    return match ? match[1].trim() : undefined;
  }

  /**
   * Extract modifiers from line
   */
  private extractModifiers(line: string): string[] {
    const modifiers: string[] = [];
    const modifierRegex = /\b(public|private|protected|static|async|const|let|var|export|import|default|abstract|final|readonly|virtual|override)\b/g;
    let match;
    
    while ((match = modifierRegex.exec(line)) !== null) {
      modifiers.push(match[1]);
    }
    
    return modifiers;
  }

  /**
   * Extract annotations from line
   */
  private extractAnnotations(line: string): Annotation[] {
    const annotations: Annotation[] = [];
    const annotationRegex = /@(\w+)(?:\(([^)]*)\))?/g;
    let match;
    
    while ((match = annotationRegex.exec(line)) !== null) {
      annotations.push({
        type: match[1],
        value: match[2] || '',
        position: { line: 0, column: match.index }
      });
    }
    
    return annotations;
  }

  /**
   * Calculate complexity of a line
   */
  private calculateComplexity(line: string): number {
    let complexity = 1;
    
    // Count control flow statements
    const controlFlowRegex = /\b(if|else|for|while|do|switch|case|catch|try|finally|return|break|continue)\b/g;
    const matches = line.match(controlFlowRegex);
    if (matches) {
      complexity += matches.length;
    }
    
    // Count logical operators
    const logicalRegex = /(&&|\|\||!)/g;
    const logicalMatches = line.match(logicalRegex);
    if (logicalMatches) {
      complexity += logicalMatches.length;
    }
    
    return complexity;
  }

  /**
   * Extract dependencies from line
   */
  private extractDependencies(line: string): string[] {
    const dependencies: string[] = [];
    
    // Extract import statements
    const importRegex = /(?:import\s+.*\s+from\s+['"]([^'"]+)['"]|import\s+['"]([^'"]+)['"]|require\s*\(\s*['"]([^'"]+)['"]\s*\))/g;
    let match;
    
    while ((match = importRegex.exec(line)) !== null) {
      const dep = match[1] || match[2] || match[3];
      if (dep) {
        dependencies.push(dep);
      }
    }
    
    return dependencies;
  }

  /**
   * Check if a word is a reserved word
   */
  private isReservedWord(word: string): boolean {
    const reservedWords = [
      'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default', 'break', 'continue',
      'return', 'function', 'var', 'let', 'const', 'class', 'interface', 'enum', 'type',
      'namespace', 'module', 'import', 'export', 'from', 'as', 'in', 'of', 'typeof', 'instanceof',
      'new', 'this', 'super', 'extends', 'implements', 'public', 'private', 'protected', 'static',
      'abstract', 'final', 'readonly', 'virtual', 'override', 'async', 'await', 'try', 'catch',
      'finally', 'throw', 'debugger', 'with', 'void', 'null', 'undefined', 'true', 'false',
      'NaN', 'Infinity', 'console', 'window', 'document', 'global', 'process', 'require',
      'module', 'exports', 'arguments', 'eval', 'parseInt', 'parseFloat', 'isNaN', 'isFinite',
      'decodeURI', 'decodeURIComponent', 'encodeURI', 'encodeURIComponent', 'escape', 'unescape'
    ];
    
    return reservedWords.includes(word.toLowerCase());
  }

  /**
   * Generate a unique symbol ID
   */
  private generateSymbolId(name: string, lineNumber: number): string {
    return `${name}_${lineNumber}_${Date.now()}`;
  }

  /**
   * Update symbols map
   */
  private updateSymbols(symbols: SymbolInfo[]): void {
    this.symbols.clear();
    symbols.forEach(symbol => {
      this.symbols.set(symbol.id, symbol);
    });
  }

  /**
   * Get all symbols
   */
  public getSymbols(): SymbolInfo[] {
    return Array.from(this.symbols.values());
  }

  /**
   * Get symbol by ID
   */
  public getSymbol(id: string): SymbolInfo | undefined {
    return this.symbols.get(id);
  }

  /**
   * Get symbols by type
   */
  public getSymbolsByType(type: SymbolType): SymbolInfo[] {
    return Array.from(this.symbols.values()).filter(symbol => symbol.type === type);
  }

  /**
   * Get symbols by kind
   */
  public getSymbolsByKind(kind: SymbolKind): SymbolInfo[] {
    return Array.from(this.symbols.values()).filter(symbol => symbol.kind === kind);
  }

  /**
   * Search symbols by name
   */
  public searchSymbols(query: string): SymbolInfo[] {
    const lowercaseQuery = query.toLowerCase();
    return Array.from(this.symbols.values()).filter(symbol => 
      symbol.name.toLowerCase().includes(lowercaseQuery)
    );
  }

  /**
   * Add event listener
   */
  public on(event: string, listener: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(listener);
  }

  /**
   * Remove event listener
   */
  public off(event: string, listener: Function): void {
    const listeners = this.listeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(listener);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  /**
   * Emit event
   */
  private emit(event: string, data?: any): void {
    const listeners = this.listeners.get(event);
    if (listeners) {
      listeners.forEach(listener => listener(data));
    }
  }

  /**
   * Destroy the service
   */
  public destroy(): void {
    this.symbols.clear();
    this.listeners.clear();
    this.cache.clear();
    
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }
    
    if (this.backgroundWorker) {
      this.backgroundWorker.terminate();
    }
  }
}
