/**
 * Advanced Monaco Editor - Code Utilities
 * 
 * This file contains utility functions for code analysis and manipulation.
 */

import { SymbolInfo, SymbolType, SymbolKind, Position, Range } from '../types/MonacoTypes';

/**
 * Utility functions for code analysis and manipulation
 */
export class CodeUtils {
  /**
   * Extract symbols from code using regex patterns
   */
  static extractSymbols(code: string, language: string): SymbolInfo[] {
    const symbols: SymbolInfo[] = [];
    const lines = code.split('\n');

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const lineNumber = i + 1;

      // Extract different types of symbols based on language
      const lineSymbols = this.extractLineSymbols(line, lineNumber, language);
      symbols.push(...lineSymbols);
    }

    return symbols;
  }

  /**
   * Extract symbols from a single line
   */
  private static extractLineSymbols(line: string, lineNumber: number, language: string): SymbolInfo[] {
    const symbols: SymbolInfo[] = [];
    const trimmedLine = line.trim();

    // Skip empty lines and comments
    if (!trimmedLine || trimmedLine.startsWith('//') || trimmedLine.startsWith('/*')) {
      return symbols;
    }

    // Extract functions
    const functionSymbols = this.extractFunctions(line, lineNumber, language);
    symbols.push(...functionSymbols);

    // Extract classes
    const classSymbols = this.extractClasses(line, lineNumber, language);
    symbols.push(...classSymbols);

    // Extract interfaces
    const interfaceSymbols = this.extractInterfaces(line, lineNumber, language);
    symbols.push(...interfaceSymbols);

    // Extract variables
    const variableSymbols = this.extractVariables(line, lineNumber, language);
    symbols.push(...variableSymbols);

    // Extract constants
    const constantSymbols = this.extractConstants(line, lineNumber, language);
    symbols.push(...constantSymbols);

    // Extract enums
    const enumSymbols = this.extractEnums(line, lineNumber, language);
    symbols.push(...enumSymbols);

    // Extract modules
    const moduleSymbols = this.extractModules(line, lineNumber, language);
    symbols.push(...moduleSymbols);

    // Extract namespaces
    const namespaceSymbols = this.extractNamespaces(line, lineNumber, language);
    symbols.push(...namespaceSymbols);

    // Extract types
    const typeSymbols = this.extractTypes(line, lineNumber, language);
    symbols.push(...typeSymbols);

    return symbols;
  }

  /**
   * Extract function symbols
   */
  private static extractFunctions(line: string, lineNumber: number, language: string): SymbolInfo[] {
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
   * Extract class symbols
   */
  private static extractClasses(line: string, lineNumber: number, language: string): SymbolInfo[] {
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
   * Extract interface symbols
   */
  private static extractInterfaces(line: string, lineNumber: number, language: string): SymbolInfo[] {
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
   * Extract variable symbols
   */
  private static extractVariables(line: string, lineNumber: number, language: string): SymbolInfo[] {
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
   * Extract constant symbols
   */
  private static extractConstants(line: string, lineNumber: number, language: string): SymbolInfo[] {
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
   * Extract enum symbols
   */
  private static extractEnums(line: string, lineNumber: number, language: string): SymbolInfo[] {
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
   * Extract module symbols
   */
  private static extractModules(line: string, lineNumber: number, language: string): SymbolInfo[] {
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
   * Extract namespace symbols
   */
  private static extractNamespaces(line: string, lineNumber: number, language: string): SymbolInfo[] {
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
   * Extract type symbols
   */
  private static extractTypes(line: string, lineNumber: number, language: string): SymbolInfo[] {
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
  private static extractFunctionMetadata(line: string, name: string): any {
    return {
      parameters: this.extractParameters(line),
      returnType: this.extractReturnType(line),
      modifiers: this.extractModifiers(line),
      annotations: this.extractAnnotations(line),
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract class metadata
   */
  private static extractClassMetadata(line: string, name: string): any {
    return {
      modifiers: this.extractModifiers(line),
      annotations: this.extractAnnotations(line),
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract interface metadata
   */
  private static extractInterfaceMetadata(line: string, name: string): any {
    return {
      modifiers: this.extractModifiers(line),
      annotations: this.extractAnnotations(line),
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract variable metadata
   */
  private static extractVariableMetadata(line: string, name: string): any {
    return {
      type: this.extractVariableType(line),
      modifiers: this.extractModifiers(line),
      annotations: this.extractAnnotations(line),
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract constant metadata
   */
  private static extractConstantMetadata(line: string, name: string): any {
    return {
      type: this.extractVariableType(line),
      modifiers: this.extractModifiers(line),
      annotations: this.extractAnnotations(line),
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract enum metadata
   */
  private static extractEnumMetadata(line: string, name: string): any {
    return {
      modifiers: this.extractModifiers(line),
      annotations: this.extractAnnotations(line),
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract module metadata
   */
  private static extractModuleMetadata(line: string, name: string): any {
    return {
      modifiers: this.extractModifiers(line),
      annotations: this.extractAnnotations(line),
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract namespace metadata
   */
  private static extractNamespaceMetadata(line: string, name: string): any {
    return {
      modifiers: this.extractModifiers(line),
      annotations: this.extractAnnotations(line),
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract type metadata
   */
  private static extractTypeMetadata(line: string, name: string): any {
    return {
      modifiers: this.extractModifiers(line),
      annotations: this.extractAnnotations(line),
      complexity: this.calculateComplexity(line),
      dependencies: this.extractDependencies(line)
    };
  }

  /**
   * Extract parameters from function line
   */
  private static extractParameters(line: string): any[] {
    const parameters: any[] = [];
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
  private static extractReturnType(line: string): string | undefined {
    const returnTypeRegex = /\)\s*:\s*([^{=>]+)/;
    const match = line.match(returnTypeRegex);
    return match ? match[1].trim() : undefined;
  }

  /**
   * Extract variable type from variable line
   */
  private static extractVariableType(line: string): string | undefined {
    const typeRegex = /:\s*([^=;]+)/;
    const match = line.match(typeRegex);
    return match ? match[1].trim() : undefined;
  }

  /**
   * Extract modifiers from line
   */
  private static extractModifiers(line: string): string[] {
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
  private static extractAnnotations(line: string): any[] {
    const annotations: any[] = [];
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
  private static calculateComplexity(line: string): number {
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
  private static extractDependencies(line: string): string[] {
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
  private static isReservedWord(word: string): boolean {
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
  private static generateSymbolId(name: string, lineNumber: number): string {
    return `${name}_${lineNumber}_${Date.now()}`;
  }

  /**
   * Format code with proper indentation
   */
  static formatCode(code: string, language: string): string {
    // This would integrate with a proper code formatter
    // For now, return the code as-is
    return code;
  }

  /**
   * Validate code syntax
   */
  static validateCode(code: string, language: string): { valid: boolean; errors: string[] } {
    // This would integrate with a proper syntax validator
    // For now, return mock validation
    return {
      valid: true,
      errors: []
    };
  }

  /**
   * Get language-specific configuration
   */
  static getLanguageConfig(language: string): any {
    const configs: Record<string, any> = {
      typescript: {
        tabSize: 2,
        insertSpaces: true,
        detectIndentation: true
      },
      javascript: {
        tabSize: 2,
        insertSpaces: true,
        detectIndentation: true
      },
      python: {
        tabSize: 4,
        insertSpaces: true,
        detectIndentation: true
      },
      java: {
        tabSize: 4,
        insertSpaces: true,
        detectIndentation: true
      },
      csharp: {
        tabSize: 4,
        insertSpaces: true,
        detectIndentation: true
      }
    };

    return configs[language] || configs.typescript;
  }
}
