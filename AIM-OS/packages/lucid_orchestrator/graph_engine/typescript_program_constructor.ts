/**
 * TypeScript Program Constructor for Lucid Orchestrator
 * 
 * This module provides real TypeScript program construction using the TypeScript compiler API
 * to build accurate IR graphs from actual codebases.
 */

import * as ts from 'typescript';
import * as path from 'path';
import * as fs from 'fs';
import { IRNode, IREdge, NodeKind, EdgeType, IRGraphBuilder } from './ir_model';

export interface TypeScriptProgramOptions {
  /** Path to tsconfig.json */
  tsConfigPath?: string;
  /** Root directory of the project */
  projectRoot: string;
  /** File patterns to include */
  includePatterns: string[];
  /** File patterns to exclude */
  excludePatterns: string[];
  /** Whether to include declaration files */
  includeDeclarations: boolean;
  /** Whether to include test files */
  includeTests: boolean;
}

export const DEFAULT_TYPESCRIPT_OPTIONS: TypeScriptProgramOptions = {
  projectRoot: process.cwd(),
  includePatterns: ['**/*.ts', '**/*.tsx', '**/*.js', '**/*.jsx'],
  excludePatterns: ['**/node_modules/**', '**/dist/**', '**/build/**'],
  includeDeclarations: false,
  includeTests: true
};

export class TypeScriptProgramConstructor {
  private options: TypeScriptProgramOptions;
  private program: ts.Program | null = null;
  private checker: ts.TypeChecker | null = null;

  constructor(options: Partial<TypeScriptProgramOptions> = {}) {
    this.options = { ...DEFAULT_TYPESCRIPT_OPTIONS, ...options };
  }

  /**
   * Initialize TypeScript program from tsconfig.json or project root
   */
  async initializeProgram(): Promise<void> {
    try {
      // Try to load tsconfig.json
      const tsConfigPath = this.options.tsConfigPath || 
        path.join(this.options.projectRoot, 'tsconfig.json');
      
      let config: ts.ParsedCommandLine;
      
      if (fs.existsSync(tsConfigPath)) {
        const configFile = ts.readConfigFile(tsConfigPath, ts.sys.readFile);
        const parsedConfig = ts.parseJsonConfigFileContent(
          configFile.config,
          ts.sys,
          path.dirname(tsConfigPath)
        );
        config = parsedConfig;
      } else {
        // Create default config
        config = {
          options: {
            target: ts.ScriptTarget.ES2020,
            module: ts.ModuleKind.ESNext,
            moduleResolution: ts.ModuleResolutionKind.NodeJs,
            allowJs: true,
            checkJs: false,
            jsx: ts.JsxEmit.React,
            declaration: false,
            outDir: undefined,
            rootDir: this.options.projectRoot,
            strict: false,
            noImplicitAny: false,
            skipLibCheck: true
          },
          fileNames: [],
          errors: []
        };
      }

      // Add files based on patterns
      const files = this.collectFiles();
      config.fileNames = files;

      // Create program
      this.program = ts.createProgram(config.fileNames, config.options);
      this.checker = this.program.getTypeChecker();

      console.log(`TypeScript program initialized with ${files.length} files`);
    } catch (error) {
      console.error('Failed to initialize TypeScript program:', error);
      throw error;
    }
  }

  /**
   * Collect files based on include/exclude patterns
   */
  private collectFiles(): string[] {
    const files: string[] = [];
    const rootDir = this.options.projectRoot;

    const collectFilesRecursive = (dir: string) => {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        const relativePath = path.relative(rootDir, fullPath);

        if (entry.isDirectory()) {
          // Check if directory should be excluded
          const shouldExclude = this.options.excludePatterns.some(pattern => 
            this.matchesPattern(relativePath, pattern)
          );
          
          if (!shouldExclude) {
            collectFilesRecursive(fullPath);
          }
        } else if (entry.isFile()) {
          // Check if file should be included
          const shouldInclude = this.options.includePatterns.some(pattern => 
            this.matchesPattern(relativePath, pattern)
          );
          
          const shouldExclude = this.options.excludePatterns.some(pattern => 
            this.matchesPattern(relativePath, pattern)
          );

          if (shouldInclude && !shouldExclude) {
            // Additional filters
            if (!this.options.includeTests && this.isTestFile(relativePath)) {
              return;
            }
            if (!this.options.includeDeclarations && relativePath.endsWith('.d.ts')) {
              return;
            }
            
            files.push(fullPath);
          }
        }
      }
    };

    collectFilesRecursive(rootDir);
    return files;
  }

  /**
   * Check if a path matches a glob pattern
   */
  private matchesPattern(filePath: string, pattern: string): boolean {
    // Simple glob pattern matching
    const regex = new RegExp(
      pattern
        .replace(/\*\*/g, '.*')
        .replace(/\*/g, '[^/]*')
        .replace(/\?/g, '.')
    );
    return regex.test(filePath);
  }

  /**
   * Check if a file is a test file
   */
  private isTestFile(filePath: string): boolean {
    return /\.(test|spec)\.(ts|tsx|js|jsx)$/.test(filePath) ||
           /\/__tests__\//.test(filePath) ||
           /\/tests?\//.test(filePath);
  }

  /**
   * Build IR graph from TypeScript program
   */
  async buildIRGraph(): Promise<IRGraphBuilder> {
    if (!this.program || !this.checker) {
      throw new Error('TypeScript program not initialized. Call initializeProgram() first.');
    }

    const builder = new IRGraphBuilder();
    const sourceFiles = this.program.getSourceFiles();

    for (const sourceFile of sourceFiles) {
      // Skip declaration files and node_modules
      if (sourceFile.isDeclarationFile || 
          sourceFile.fileName.includes('node_modules')) {
        continue;
      }

      await this.processSourceFile(sourceFile, builder);
    }

    return builder;
  }

  /**
   * Process a single source file and extract IR nodes
   */
  private async processSourceFile(sourceFile: ts.SourceFile, builder: IRGraphBuilder): Promise<void> {
    const visit = (node: ts.Node) => {
      // Extract different types of nodes
      if (ts.isFunctionDeclaration(node) || ts.isMethodDeclaration(node)) {
        this.extractFunctionNode(node, sourceFile, builder);
      } else if (ts.isClassDeclaration(node)) {
        this.extractClassNode(node, sourceFile, builder);
      } else if (ts.isInterfaceDeclaration(node)) {
        this.extractInterfaceNode(node, sourceFile, builder);
      } else if (ts.isTypeAliasDeclaration(node)) {
        this.extractTypeNode(node, sourceFile, builder);
      } else if (ts.isEnumDeclaration(node)) {
        this.extractEnumNode(node, sourceFile, builder);
      } else if (ts.isVariableStatement(node)) {
        this.extractVariableNodes(node, sourceFile, builder);
      } else if (ts.isImportDeclaration(node)) {
        this.extractImportEdges(node, sourceFile, builder);
      }

      // Visit children
      ts.forEachChild(node, visit);
    };

    visit(sourceFile);
  }

  /**
   * Extract function/method nodes
   */
  private extractFunctionNode(node: ts.FunctionLikeDeclaration, sourceFile: ts.SourceFile, builder: IRGraphBuilder): void {
    if (!node.name) return;

    const nodeId = this.generateNodeId(node.name.text, sourceFile.fileName);
    const range = this.getNodeRange(node, sourceFile);
    
    const irNode: IRNode = {
      id: nodeId,
      name: node.name.text,
      kind: this.determineNodeKind(node),
      filePath: sourceFile.fileName,
      range,
      metadata: {
        isExported: this.isExported(node),
        isAsync: node.modifiers?.some(m => m.kind === ts.SyntaxKind.AsyncKeyword) || false,
        parameters: this.extractParameters(node),
        returnType: this.extractReturnType(node),
        complexity: this.calculateComplexity(node)
      },
      status: 'clean'
    };

    builder.addNode(irNode);
  }

  /**
   * Extract class nodes
   */
  private extractClassNode(node: ts.ClassDeclaration, sourceFile: ts.SourceFile, builder: IRGraphBuilder): void {
    if (!node.name) return;

    const nodeId = this.generateNodeId(node.name.text, sourceFile.fileName);
    const range = this.getNodeRange(node, sourceFile);
    
    const irNode: IRNode = {
      id: nodeId,
      name: node.name.text,
      kind: 'component',
      filePath: sourceFile.fileName,
      range,
      metadata: {
        isExported: this.isExported(node),
        isAbstract: node.modifiers?.some(m => m.kind === ts.SyntaxKind.AbstractKeyword) || false,
        methods: this.extractClassMethods(node),
        properties: this.extractClassProperties(node),
        extends: this.extractExtends(node),
        implements: this.extractImplements(node)
      },
      status: 'clean'
    };

    builder.addNode(irNode);
  }

  /**
   * Extract interface nodes
   */
  private extractInterfaceNode(node: ts.InterfaceDeclaration, sourceFile: ts.SourceFile, builder: IRGraphBuilder): void {
    const nodeId = this.generateNodeId(node.name.text, sourceFile.fileName);
    const range = this.getNodeRange(node, sourceFile);
    
    const irNode: IRNode = {
      id: nodeId,
      name: node.name.text,
      kind: 'interface',
      filePath: sourceFile.fileName,
      range,
      metadata: {
        isExported: this.isExported(node),
        properties: this.extractInterfaceProperties(node),
        extends: this.extractExtends(node),
        methods: this.extractInterfaceMethods(node)
      },
      status: 'clean'
    };

    builder.addNode(irNode);
  }

  /**
   * Extract type alias nodes
   */
  private extractTypeNode(node: ts.TypeAliasDeclaration, sourceFile: ts.SourceFile, builder: IRGraphBuilder): void {
    const nodeId = this.generateNodeId(node.name.text, sourceFile.fileName);
    const range = this.getNodeRange(node, sourceFile);
    
    const irNode: IRNode = {
      id: nodeId,
      name: node.name.text,
      kind: 'type',
      filePath: sourceFile.fileName,
      range,
      metadata: {
        isExported: this.isExported(node),
        typeDefinition: node.type.getText(sourceFile)
      },
      status: 'clean'
    };

    builder.addNode(irNode);
  }

  /**
   * Extract enum nodes
   */
  private extractEnumNode(node: ts.EnumDeclaration, sourceFile: ts.SourceFile, builder: IRGraphBuilder): void {
    const nodeId = this.generateNodeId(node.name.text, sourceFile.fileName);
    const range = this.getNodeRange(node, sourceFile);
    
    const irNode: IRNode = {
      id: nodeId,
      name: node.name.text,
      kind: 'enum',
      filePath: sourceFile.fileName,
      range,
      metadata: {
        isExported: this.isExported(node),
        members: this.extractEnumMembers(node)
      },
      status: 'clean'
    };

    builder.addNode(irNode);
  }

  /**
   * Extract variable nodes
   */
  private extractVariableNodes(node: ts.VariableStatement, sourceFile: ts.SourceFile, builder: IRGraphBuilder): void {
    for (const declaration of node.declarationList.declarations) {
      if (!ts.isIdentifier(declaration.name)) continue;

      const nodeId = this.generateNodeId(declaration.name.text, sourceFile.fileName);
      const range = this.getNodeRange(declaration, sourceFile);
      
      const irNode: IRNode = {
        id: nodeId,
        name: declaration.name.text,
        kind: this.isConstant(declaration) ? 'constant' : 'variable',
        filePath: sourceFile.fileName,
        range,
        metadata: {
          isExported: this.isExported(node),
          isConst: this.isConstant(declaration),
          type: declaration.type ? declaration.type.getText(sourceFile) : undefined
        },
        status: 'clean'
      };

      builder.addNode(irNode);
    }
  }

  /**
   * Extract import edges
   */
  private extractImportEdges(node: ts.ImportDeclaration, sourceFile: ts.SourceFile, builder: IRGraphBuilder): void {
    if (!node.moduleSpecifier || !ts.isStringLiteral(node.moduleSpecifier)) return;

    const modulePath = node.moduleSpecifier.text;
    const isRelative = modulePath.startsWith('./') || modulePath.startsWith('../');

    if (node.importClause?.namedBindings && ts.isNamedImports(node.importClause.namedBindings)) {
      for (const importSpecifier of node.importClause.namedBindings.elements) {
        const edge: IREdge = {
          id: `${sourceFile.fileName}:${importSpecifier.name.text}:imports:${modulePath}`,
          from: sourceFile.fileName,
          to: modulePath,
          type: 'imports',
          metadata: {
            importedName: importSpecifier.name.text,
            alias: importSpecifier.propertyName?.text,
            isRelative,
            isTypeOnly: importSpecifier.isTypeOnly
          }
        };

        builder.addEdge(edge);
      }
    }
  }

  /**
   * Generate unique node ID
   */
  private generateNodeId(name: string, filePath: string): string {
    const relativePath = path.relative(this.options.projectRoot, filePath);
    return `${relativePath}:${name}`;
  }

  /**
   * Get node range in source file
   */
  private getNodeRange(node: ts.Node, sourceFile: ts.SourceFile): { startLine: number; endLine: number } {
    const start = sourceFile.getLineAndCharacterOfPosition(node.getStart());
    const end = sourceFile.getLineAndCharacterOfPosition(node.getEnd());
    
    return {
      startLine: start.line + 1, // Convert to 1-based
      endLine: end.line + 1
    };
  }

  /**
   * Determine node kind based on context
   */
  private determineNodeKind(node: ts.FunctionLikeDeclaration): NodeKind {
    // Check if it's a React component
    if (this.isReactComponent(node)) {
      return 'reactComponent';
    }
    
    // Check if it's a hook
    if (this.isReactHook(node)) {
      return 'hook';
    }
    
    // Check if it's a test
    if (this.isTestFunction(node)) {
      return 'test';
    }
    
    return 'function';
  }

  /**
   * Check if function is a React component
   */
  private isReactComponent(node: ts.FunctionLikeDeclaration): boolean {
    const name = node.name?.text || '';
    return /^[A-Z]/.test(name) && 
           (name.endsWith('Component') || 
            name.endsWith('Page') || 
            name.endsWith('View') ||
            name.endsWith('Panel'));
  }

  /**
   * Check if function is a React hook
   */
  private isReactHook(node: ts.FunctionLikeDeclaration): boolean {
    const name = node.name?.text || '';
    return name.startsWith('use') && /^[A-Z]/.test(name.slice(2));
  }

  /**
   * Check if function is a test
   */
  private isTestFunction(node: ts.FunctionLikeDeclaration): boolean {
    const name = node.name?.text || '';
    return name.startsWith('test') || 
           name.startsWith('it') || 
           name.startsWith('describe') ||
           name.startsWith('expect');
  }

  /**
   * Check if node is exported
   */
  private isExported(node: ts.Node): boolean {
    return node.modifiers?.some(m => m.kind === ts.SyntaxKind.ExportKeyword) || false;
  }

  /**
   * Check if variable is constant
   */
  private isConstant(declaration: ts.VariableDeclaration): boolean {
    return declaration.parent.parent.modifiers?.some(m => m.kind === ts.SyntaxKind.ConstKeyword) || false;
  }

  /**
   * Extract function parameters
   */
  private extractParameters(node: ts.FunctionLikeDeclaration): string[] {
    return node.parameters.map(param => param.name.getText());
  }

  /**
   * Extract return type
   */
  private extractReturnType(node: ts.FunctionLikeDeclaration): string | undefined {
    return node.type ? node.type.getText() : undefined;
  }

  /**
   * Calculate function complexity
   */
  private calculateComplexity(node: ts.FunctionLikeDeclaration): number {
    // Simple complexity calculation based on nesting depth
    let complexity = 1;
    const visit = (n: ts.Node) => {
      if (ts.isIfStatement(n) || ts.isForStatement(n) || ts.isWhileStatement(n) || ts.isSwitchStatement(n)) {
        complexity++;
      }
      ts.forEachChild(n, visit);
    };
    visit(node);
    return complexity;
  }

  /**
   * Extract class methods
   */
  private extractClassMethods(node: ts.ClassDeclaration): string[] {
    return node.members
      .filter(member => ts.isMethodDeclaration(member))
      .map(member => member.name?.getText() || '')
      .filter(name => name);
  }

  /**
   * Extract class properties
   */
  private extractClassProperties(node: ts.ClassDeclaration): string[] {
    return node.members
      .filter(member => ts.isPropertyDeclaration(member))
      .map(member => member.name?.getText() || '')
      .filter(name => name);
  }

  /**
   * Extract extends clause
   */
  private extractExtends(node: ts.ClassDeclaration | ts.InterfaceDeclaration): string[] {
    return node.heritageClauses
      ?.filter(clause => clause.token === ts.SyntaxKind.ExtendsKeyword)
      .flatMap(clause => clause.types.map(type => type.expression.getText())) || [];
  }

  /**
   * Extract implements clause
   */
  private extractImplements(node: ts.ClassDeclaration): string[] {
    return node.heritageClauses
      ?.filter(clause => clause.token === ts.SyntaxKind.ImplementsKeyword)
      .flatMap(clause => clause.types.map(type => type.expression.getText())) || [];
  }

  /**
   * Extract interface properties
   */
  private extractInterfaceProperties(node: ts.InterfaceDeclaration): string[] {
    return node.members
      .filter(member => ts.isPropertySignature(member))
      .map(member => member.name?.getText() || '')
      .filter(name => name);
  }

  /**
   * Extract interface methods
   */
  private extractInterfaceMethods(node: ts.InterfaceDeclaration): string[] {
    return node.members
      .filter(member => ts.isMethodSignature(member))
      .map(member => member.name?.getText() || '')
      .filter(name => name);
  }

  /**
   * Extract enum members
   */
  private extractEnumMembers(node: ts.EnumDeclaration): string[] {
    return node.members.map(member => member.name.getText());
  }

  /**
   * Get TypeScript program instance
   */
  getProgram(): ts.Program | null {
    return this.program;
  }

  /**
   * Get TypeScript type checker
   */
  getChecker(): ts.TypeChecker | null {
    return this.checker;
  }
}
