/**
 * Edge Extractor for Lucid Orchestrator
 * 
 * This module provides comprehensive edge extraction for IR graphs,
 * including imports, function calls, data flow, and cross-layer connections.
 */

import * as ts from 'typescript';
import * as path from 'path';
import { IREdge, EdgeType, IRNode, IRGraphBuilder } from './ir_model';

export interface EdgeExtractionOptions {
  /** Include import edges */
  includeImports: boolean;
  /** Include function call edges */
  includeCalls: boolean;
  /** Include data flow edges */
  includeDataFlow: boolean;
  /** Include UI update edges */
  includeUIUpdates: boolean;
  /** Include database edges */
  includeDatabase: boolean;
  /** Include event edges */
  includeEvents: boolean;
  /** Include dependency edges */
  includeDependencies: boolean;
  /** Maximum depth for call chain analysis */
  maxCallDepth: number;
}

export const DEFAULT_EDGE_OPTIONS: EdgeExtractionOptions = {
  includeImports: true,
  includeCalls: true,
  includeDataFlow: true,
  includeUIUpdates: true,
  includeDatabase: true,
  includeEvents: true,
  includeDependencies: true,
  maxCallDepth: 3
};

export class EdgeExtractor {
  private options: EdgeExtractionOptions;
  private checker: ts.TypeChecker;
  private sourceFile: ts.SourceFile;
  private projectRoot: string;

  constructor(
    checker: ts.TypeChecker,
    sourceFile: ts.SourceFile,
    projectRoot: string,
    options: Partial<EdgeExtractionOptions> = {}
  ) {
    this.checker = checker;
    this.sourceFile = sourceFile;
    this.projectRoot = projectRoot;
    this.options = { ...DEFAULT_EDGE_OPTIONS, ...options };
  }

  /**
   * Extract all edges from a source file
   */
  extractEdges(): IREdge[] {
    const edges: IREdge[] = [];
    
    const visit = (node: ts.Node) => {
      // Extract different types of edges
      if (this.options.includeImports) {
        edges.push(...this.extractImportEdges(node));
      }
      
      if (this.options.includeCalls) {
        edges.push(...this.extractCallEdges(node));
      }
      
      if (this.options.includeDataFlow) {
        edges.push(...this.extractDataFlowEdges(node));
      }
      
      if (this.options.includeUIUpdates) {
        edges.push(...this.extractUIUpdateEdges(node));
      }
      
      if (this.options.includeDatabase) {
        edges.push(...this.extractDatabaseEdges(node));
      }
      
      if (this.options.includeEvents) {
        edges.push(...this.extractEventEdges(node));
      }
      
      if (this.options.includeDependencies) {
        edges.push(...this.extractDependencyEdges(node));
      }
      
      ts.forEachChild(node, visit);
    };
    
    visit(this.sourceFile);
    return edges;
  }

  /**
   * Extract import edges
   */
  private extractImportEdges(node: ts.Node): IREdge[] {
    const edges: IREdge[] = [];
    
    if (ts.isImportDeclaration(node)) {
      const moduleSpecifier = node.moduleSpecifier;
      if (ts.isStringLiteral(moduleSpecifier)) {
        const modulePath = moduleSpecifier.text;
        const isRelative = modulePath.startsWith('./') || modulePath.startsWith('../');
        
        // Handle named imports
        if (node.importClause?.namedBindings && ts.isNamedImports(node.importClause.namedBindings)) {
          for (const importSpecifier of node.importClause.namedBindings.elements) {
            const edge: IREdge = {
              id: `${this.sourceFile.fileName}:${importSpecifier.name.text}:imports:${modulePath}`,
              from: this.sourceFile.fileName,
              to: this.resolveModulePath(modulePath),
              type: 'imports',
              metadata: {
                importedName: importSpecifier.name.text,
                alias: importSpecifier.propertyName?.text,
                isRelative,
                isTypeOnly: importSpecifier.isTypeOnly,
                isDefault: false
              }
            };
            edges.push(edge);
          }
        }
        
        // Handle default import
        if (node.importClause?.name) {
          const edge: IREdge = {
            id: `${this.sourceFile.fileName}:${node.importClause.name.text}:imports:${modulePath}`,
            from: this.sourceFile.fileName,
            to: this.resolveModulePath(modulePath),
            type: 'imports',
            metadata: {
              importedName: node.importClause.name.text,
              isRelative,
              isTypeOnly: false,
              isDefault: true
            }
          };
          edges.push(edge);
        }
        
        // Handle namespace import
        if (node.importClause?.namedBindings && ts.isNamespaceImport(node.importClause.namedBindings)) {
          const edge: IREdge = {
            id: `${this.sourceFile.fileName}:${node.importClause.namedBindings.name.text}:imports:${modulePath}`,
            from: this.sourceFile.fileName,
            to: this.resolveModulePath(modulePath),
            type: 'imports',
            metadata: {
              importedName: node.importClause.namedBindings.name.text,
              isRelative,
              isTypeOnly: false,
              isDefault: false,
              isNamespace: true
            }
          };
          edges.push(edge);
        }
      }
    }
    
    return edges;
  }

  /**
   * Extract function call edges
   */
  private extractCallEdges(node: ts.Node): IREdge[] {
    const edges: IREdge[] = [];
    
    if (ts.isCallExpression(node)) {
      const callTarget = this.getCallTarget(node);
      if (callTarget) {
        const edge: IREdge = {
          id: `${this.getCurrentFunction()}:${callTarget}:calls:${Date.now()}`,
          from: this.getCurrentFunction() || this.sourceFile.fileName,
          to: callTarget,
          type: 'calls',
          metadata: {
            arguments: this.extractCallArguments(node),
            isAsync: this.isAsyncCall(node),
            returnType: this.getCallReturnType(node),
            isConstructor: ts.isNewExpression(node.parent),
            isMethodCall: ts.isPropertyAccessExpression(node.expression)
          }
        };
        edges.push(edge);
      }
    }
    
    return edges;
  }

  /**
   * Extract data flow edges
   */
  private extractDataFlowEdges(node: ts.Node): IREdge[] {
    const edges: IREdge[] = [];
    
    // Variable assignments
    if (ts.isVariableDeclaration(node)) {
      const variableName = this.getVariableName(node);
      if (variableName) {
        const initializer = node.initializer;
        if (initializer) {
          const dataSource = this.getDataSource(initializer);
          if (dataSource) {
            const edge: IREdge = {
              id: `${this.sourceFile.fileName}:${variableName}:dataflow:${dataSource}`,
              from: dataSource,
              to: variableName,
              type: 'uses',
              metadata: {
                dataType: this.getTypeName(initializer),
                isConstant: node.parent.parent.modifiers?.some(m => m.kind === ts.SyntaxKind.ConstKeyword) || false,
                isReactive: this.isReactiveAssignment(node)
              }
            };
            edges.push(edge);
          }
        }
      }
    }
    
    // Property assignments
    if (ts.isBinaryExpression(node) && node.operatorToken.kind === ts.SyntaxKind.EqualsToken) {
      const left = node.left;
      const right = node.right;
      
      if (ts.isPropertyAccessExpression(left) || ts.isElementAccessExpression(left)) {
        const propertyName = this.getPropertyName(left);
        const dataSource = this.getDataSource(right);
        
        if (propertyName && dataSource) {
          const edge: IREdge = {
            id: `${this.sourceFile.fileName}:${propertyName}:mutates:${dataSource}`,
            from: dataSource,
            to: propertyName,
            type: 'mutates',
            metadata: {
              dataType: this.getTypeName(right),
              isNested: ts.isElementAccessExpression(left),
              isReactive: this.isReactiveAssignment(node)
            }
          };
          edges.push(edge);
        }
      }
    }
    
    return edges;
  }

  /**
   * Extract UI update edges
   */
  private extractUIUpdateEdges(node: ts.Node): IREdge[] {
    const edges: IREdge[] = [];
    
    // React state updates
    if (ts.isCallExpression(node)) {
      const callName = this.getCallExpressionName(node);
      if (callName === 'setState' || callName?.startsWith('set')) {
        const stateVariable = callName.startsWith('set') ? 
          callName.slice(3).toLowerCase() : 'state';
        
        const edge: IREdge = {
          id: `${this.getCurrentFunction()}:${stateVariable}:updatesUI:${Date.now()}`,
          from: this.getCurrentFunction() || this.sourceFile.fileName,
          to: stateVariable,
          type: 'updatesUI',
          metadata: {
            updateType: 'state',
            isAsync: this.isAsyncCall(node),
            isBatch: this.isBatchUpdate(node)
          }
        };
        edges.push(edge);
      }
    }
    
    // DOM manipulations
    if (ts.isCallExpression(node)) {
      const callName = this.getCallExpressionName(node);
      if (callName && this.isDOMMethod(callName)) {
        const edge: IREdge = {
          id: `${this.getCurrentFunction()}:DOM:updatesUI:${Date.now()}`,
          from: this.getCurrentFunction() || this.sourceFile.fileName,
          to: 'DOM',
          type: 'updatesUI',
          metadata: {
            updateType: 'DOM',
            method: callName,
            isAsync: this.isAsyncCall(node)
          }
        };
        edges.push(edge);
      }
    }
    
    return edges;
  }

  /**
   * Extract database edges
   */
  private extractDatabaseEdges(node: ts.Node): IREdge[] {
    const edges: IREdge[] = [];
    
    if (ts.isCallExpression(node)) {
      const callName = this.getCallExpressionName(node);
      if (callName && this.isDatabaseMethod(callName)) {
        const edge: IREdge = {
          id: `${this.getCurrentFunction()}:database:queriesDB:${Date.now()}`,
          from: this.getCurrentFunction() || this.sourceFile.fileName,
          to: 'database',
          type: 'queriesDB',
          metadata: {
            operation: this.getDatabaseOperation(callName),
            isAsync: this.isAsyncCall(node),
            isTransaction: this.isTransaction(node)
          }
        };
        edges.push(edge);
      }
    }
    
    return edges;
  }

  /**
   * Extract event edges
   */
  private extractEventEdges(node: ts.Node): IREdge[] {
    const edges: IREdge[] = [];
    
    // Event listeners
    if (ts.isCallExpression(node)) {
      const callName = this.getCallExpressionName(node);
      if (callName && this.isEventMethod(callName)) {
        const eventType = this.extractEventType(node);
        if (eventType) {
          const edge: IREdge = {
            id: `${this.getCurrentFunction()}:${eventType}:subscribesTo:${Date.now()}`,
            from: this.getCurrentFunction() || this.sourceFile.fileName,
            to: eventType,
            type: 'subscribesTo',
            metadata: {
              eventType,
              isAsync: this.isAsyncCall(node),
              isOnce: callName.includes('once')
            }
          };
          edges.push(edge);
        }
      }
    }
    
    // Event dispatching
    if (ts.isCallExpression(node)) {
      const callName = this.getCallExpressionName(node);
      if (callName && this.isEventDispatchMethod(callName)) {
        const eventType = this.extractEventType(node);
        if (eventType) {
          const edge: IREdge = {
            id: `${this.getCurrentFunction()}:${eventType}:publishesEvent:${Date.now()}`,
            from: this.getCurrentFunction() || this.sourceFile.fileName,
            to: eventType,
            type: 'publishesEvent',
            metadata: {
              eventType,
              isAsync: this.isAsyncCall(node),
              isCustom: this.isCustomEvent(eventType)
            }
          };
          edges.push(edge);
        }
      }
    }
    
    return edges;
  }

  /**
   * Extract dependency edges
   */
  private extractDependencyEdges(node: ts.Node): IREdge[] {
    const edges: IREdge[] = [];
    
    // Function dependencies
    if (ts.isFunctionDeclaration(node) || ts.isMethodDeclaration(node)) {
      const functionName = node.name?.text;
      if (functionName) {
        const dependencies = this.extractFunctionDependencies(node);
        for (const dep of dependencies) {
          const edge: IREdge = {
            id: `${functionName}:${dep}:dependsOn:${Date.now()}`,
            from: functionName,
            to: dep,
            type: 'dependsOn',
            metadata: {
              dependencyType: 'function',
              isRequired: this.isRequiredDependency(node, dep),
              isOptional: this.isOptionalDependency(node, dep)
            }
          };
          edges.push(edge);
        }
      }
    }
    
    return edges;
  }

  /**
   * Helper methods
   */
  private resolveModulePath(modulePath: string): string {
    if (modulePath.startsWith('./') || modulePath.startsWith('../')) {
      return path.resolve(path.dirname(this.sourceFile.fileName), modulePath);
    }
    return modulePath;
  }

  private getCallTarget(node: ts.CallExpression): string | null {
    if (ts.isIdentifier(node.expression)) {
      return node.expression.text;
    }
    if (ts.isPropertyAccessExpression(node.expression)) {
      return `${node.expression.expression.getText()}.${node.expression.name.text}`;
    }
    return null;
  }

  private getCurrentFunction(): string | null {
    // This would need to be tracked during traversal
    // For now, return null
    return null;
  }

  private extractCallArguments(node: ts.CallExpression): string[] {
    return node.arguments
      .filter(arg => ts.isIdentifier(arg))
      .map(arg => (arg as ts.Identifier).text);
  }

  private isAsyncCall(node: ts.CallExpression): boolean {
    return node.expression.getText().includes('await') || 
           this.checker.getTypeAtLocation(node).symbol?.name === 'Promise';
  }

  private getCallReturnType(node: ts.CallExpression): string | undefined {
    const type = this.checker.getTypeAtLocation(node);
    return type.symbol?.name || type.getSymbol()?.name;
  }

  private getCallExpressionName(node: ts.CallExpression): string | null {
    if (ts.isIdentifier(node.expression)) {
      return node.expression.text;
    }
    if (ts.isPropertyAccessExpression(node.expression)) {
      return node.expression.name.text;
    }
    return null;
  }

  private getVariableName(node: ts.VariableDeclaration): string | null {
    if (ts.isIdentifier(node.name)) {
      return node.name.text;
    }
    return null;
  }

  private getDataSource(node: ts.Node): string | null {
    if (ts.isIdentifier(node)) {
      return node.text;
    }
    if (ts.isCallExpression(node)) {
      return this.getCallTarget(node);
    }
    return null;
  }

  private getTypeName(node: ts.Node): string | undefined {
    const type = this.checker.getTypeAtLocation(node);
    return type.symbol?.name || type.getSymbol()?.name;
  }

  private isReactiveAssignment(node: ts.Node): boolean {
    // Check if assignment is reactive (e.g., in React component)
    return node.getText().includes('useState') || 
           node.getText().includes('useEffect');
  }

  private getPropertyName(node: ts.PropertyAccessExpression | ts.ElementAccessExpression): string | null {
    if (ts.isPropertyAccessExpression(node)) {
      return node.name.text;
    }
    if (ts.isElementAccessExpression(node) && ts.isStringLiteral(node.argumentExpression)) {
      return node.argumentExpression.text;
    }
    return null;
  }

  private isDOMMethod(methodName: string): boolean {
    const domMethods = [
      'appendChild', 'removeChild', 'insertBefore', 'replaceChild',
      'setAttribute', 'removeAttribute', 'addEventListener', 'removeEventListener',
      'querySelector', 'querySelectorAll', 'getElementById', 'getElementsByClassName'
    ];
    return domMethods.includes(methodName);
  }

  private isDatabaseMethod(methodName: string): boolean {
    const dbMethods = [
      'find', 'findOne', 'findById', 'create', 'update', 'delete', 'remove',
      'save', 'insert', 'upsert', 'query', 'execute', 'transaction'
    ];
    return dbMethods.includes(methodName) || methodName.includes('db.') || methodName.includes('collection.');
  }

  private getDatabaseOperation(methodName: string): string {
    if (methodName.includes('find')) return 'read';
    if (methodName.includes('create') || methodName.includes('insert')) return 'create';
    if (methodName.includes('update')) return 'update';
    if (methodName.includes('delete') || methodName.includes('remove')) return 'delete';
    return 'unknown';
  }

  private isTransaction(node: ts.CallExpression): boolean {
    return node.expression.getText().includes('transaction') || 
           node.expression.getText().includes('beginTransaction');
  }

  private isEventMethod(methodName: string): boolean {
    return methodName.includes('addEventListener') || 
           methodName.includes('on') ||
           methodName.includes('listen');
  }

  private isEventDispatchMethod(methodName: string): boolean {
    return methodName.includes('dispatch') || 
           methodName.includes('emit') ||
           methodName.includes('trigger');
  }

  private extractEventType(node: ts.CallExpression): string | null {
    if (node.arguments.length > 0 && ts.isStringLiteral(node.arguments[0])) {
      return node.arguments[0].text;
    }
    return null;
  }

  private isCustomEvent(eventType: string): boolean {
    return !['click', 'change', 'submit', 'load', 'unload', 'resize', 'scroll'].includes(eventType);
  }

  private extractFunctionDependencies(node: ts.FunctionDeclaration | ts.MethodDeclaration): string[] {
    const dependencies: string[] = [];
    
    const visit = (n: ts.Node) => {
      if (ts.isIdentifier(n)) {
        const symbol = this.checker.getSymbolAtLocation(n);
        if (symbol && symbol.valueDeclaration) {
          const name = symbol.name;
          if (name !== node.name?.text) {
            dependencies.push(name);
          }
        }
      }
      ts.forEachChild(n, visit);
    };
    
    visit(node);
    return [...new Set(dependencies)];
  }

  private isRequiredDependency(node: ts.Node, dep: string): boolean {
    // Check if dependency is required (not optional)
    return true; // Simplified implementation
  }

  private isOptionalDependency(node: ts.Node, dep: string): boolean {
    // Check if dependency is optional
    return false; // Simplified implementation
  }
}
