/**
 * React Component Detector for Lucid Orchestrator
 * 
 * This module provides advanced React component detection using AST analysis
 * to identify React components, hooks, and their relationships.
 */

import * as ts from 'typescript';
import * as path from 'path';
import { IRNode, IREdge, NodeKind, IRGraphBuilder } from './ir_model';

export interface ReactComponentInfo {
  /** Component name */
  name: string;
  /** Component type (functional, class, hook, etc.) */
  type: 'functional' | 'class' | 'hook' | 'context' | 'provider' | 'consumer';
  /** Props interface name if available */
  propsInterface?: string;
  /** State interface name if available */
  stateInterface?: string;
  /** Hooks used in the component */
  hooks: string[];
  /** Child components used */
  childComponents: string[];
  /** Event handlers */
  eventHandlers: string[];
  /** Lifecycle methods (for class components) */
  lifecycleMethods: string[];
  /** Whether component is exported */
  isExported: boolean;
  /** Whether component is default export */
  isDefaultExport: boolean;
  /** JSX elements used */
  jsxElements: string[];
  /** Styling approach (css, styled-components, etc.) */
  stylingApproach?: string;
  /** Whether component uses TypeScript */
  usesTypeScript: boolean;
}

export interface ReactHookInfo {
  /** Hook name */
  name: string;
  /** Hook type */
  type: 'state' | 'effect' | 'context' | 'ref' | 'memo' | 'callback' | 'custom';
  /** Dependencies */
  dependencies: string[];
  /** Whether hook is custom */
  isCustom: boolean;
  /** Return type */
  returnType?: string;
}

export class ReactComponentDetector {
  private checker: ts.TypeChecker;
  private sourceFile: ts.SourceFile;

  constructor(checker: ts.TypeChecker, sourceFile: ts.SourceFile) {
    this.checker = checker;
    this.sourceFile = sourceFile;
  }

  /**
   * Detect all React components in a source file
   */
  detectComponents(): ReactComponentInfo[] {
    const components: ReactComponentInfo[] = [];
    
    const visit = (node: ts.Node) => {
      // Detect functional components
      if (this.isFunctionalComponent(node)) {
        const component = this.extractFunctionalComponent(node);
        if (component) components.push(component);
      }
      
      // Detect class components
      if (this.isClassComponent(node)) {
        const component = this.extractClassComponent(node);
        if (component) components.push(component);
      }
      
      // Detect custom hooks
      if (this.isCustomHook(node)) {
        const hook = this.extractCustomHook(node);
        if (hook) {
          components.push({
            name: hook.name,
            type: 'hook',
            hooks: [],
            childComponents: [],
            eventHandlers: [],
            lifecycleMethods: [],
            isExported: this.isExported(node),
            isDefaultExport: this.isDefaultExport(node),
            jsxElements: [],
            usesTypeScript: true
          });
        }
      }
      
      // Detect context providers/consumers
      if (this.isContextProvider(node) || this.isContextConsumer(node)) {
        const context = this.extractContext(node);
        if (context) components.push(context);
      }
      
      ts.forEachChild(node, visit);
    };
    
    visit(this.sourceFile);
    return components;
  }

  /**
   * Check if node is a functional component
   */
  private isFunctionalComponent(node: ts.Node): boolean {
    if (!ts.isFunctionDeclaration(node) && !ts.isVariableDeclaration(node)) {
      return false;
    }
    
    const name = this.getNodeName(node);
    if (!name) return false;
    
    // Check if it's a React component (starts with uppercase)
    if (!/^[A-Z]/.test(name)) return false;
    
    // Check if it returns JSX
    return this.returnsJSX(node);
  }

  /**
   * Check if node is a class component
   */
  private isClassComponent(node: ts.Node): boolean {
    if (!ts.isClassDeclaration(node)) return false;
    
    const name = node.name?.text;
    if (!name) return false;
    
    // Check if it's a React component (starts with uppercase)
    if (!/^[A-Z]/.test(name)) return false;
    
    // Check if it extends React.Component or has render method
    return this.extendsReactComponent(node) || this.hasRenderMethod(node);
  }

  /**
   * Check if node is a custom hook
   */
  private isCustomHook(node: ts.Node): boolean {
    if (!ts.isFunctionDeclaration(node) && !ts.isVariableDeclaration(node)) {
      return false;
    }
    
    const name = this.getNodeName(node);
    if (!name) return false;
    
    // Check if it starts with 'use'
    return name.startsWith('use') && /^[A-Z]/.test(name.slice(2));
  }

  /**
   * Check if node is a context provider
   */
  private isContextProvider(node: ts.Node): boolean {
    const name = this.getNodeName(node);
    return name ? name.endsWith('Provider') : false;
  }

  /**
   * Check if node is a context consumer
   */
  private isContextConsumer(node: ts.Node): boolean {
    const name = this.getNodeName(node);
    return name ? name.endsWith('Consumer') : false;
  }

  /**
   * Extract functional component information
   */
  private extractFunctionalComponent(node: ts.Node): ReactComponentInfo | null {
    const name = this.getNodeName(node);
    if (!name) return null;

    const hooks = this.extractHooks(node);
    const childComponents = this.extractChildComponents(node);
    const eventHandlers = this.extractEventHandlers(node);
    const jsxElements = this.extractJSXElements(node);
    const propsInterface = this.extractPropsInterface(node);

    return {
      name,
      type: 'functional',
      propsInterface,
      hooks: hooks.map(h => h.name),
      childComponents,
      eventHandlers,
      lifecycleMethods: [],
      isExported: this.isExported(node),
      isDefaultExport: this.isDefaultExport(node),
      jsxElements,
      stylingApproach: this.detectStylingApproach(node),
      usesTypeScript: true
    };
  }

  /**
   * Extract class component information
   */
  private extractClassComponent(node: ts.Node): ReactComponentInfo | null {
    if (!ts.isClassDeclaration(node)) return null;
    
    const name = node.name?.text;
    if (!name) return null;

    const hooks: ReactHookInfo[] = []; // Class components don't use hooks
    const childComponents = this.extractChildComponents(node);
    const eventHandlers = this.extractEventHandlers(node);
    const lifecycleMethods = this.extractLifecycleMethods(node);
    const jsxElements = this.extractJSXElements(node);
    const propsInterface = this.extractPropsInterface(node);
    const stateInterface = this.extractStateInterface(node);

    return {
      name,
      type: 'class',
      propsInterface,
      stateInterface,
      hooks: hooks.map(h => h.name),
      childComponents,
      eventHandlers,
      lifecycleMethods,
      isExported: this.isExported(node),
      isDefaultExport: this.isDefaultExport(node),
      jsxElements,
      stylingApproach: this.detectStylingApproach(node),
      usesTypeScript: true
    };
  }

  /**
   * Extract custom hook information
   */
  private extractCustomHook(node: ts.Node): ReactHookInfo | null {
    const name = this.getNodeName(node);
    if (!name) return null;

    const dependencies = this.extractHookDependencies(node);
    const returnType = this.extractReturnType(node);

    return {
      name,
      type: 'custom',
      dependencies,
      isCustom: true,
      returnType
    };
  }

  /**
   * Extract context information
   */
  private extractContext(node: ts.Node): ReactComponentInfo | null {
    const name = this.getNodeName(node);
    if (!name) return null;

    const isProvider = name.endsWith('Provider');
    const isConsumer = name.endsWith('Consumer');

    return {
      name,
      type: isProvider ? 'provider' : isConsumer ? 'consumer' : 'context',
      hooks: [],
      childComponents: [],
      eventHandlers: [],
      lifecycleMethods: [],
      isExported: this.isExported(node),
      isDefaultExport: this.isDefaultExport(node),
      jsxElements: [],
      usesTypeScript: true
    };
  }

  /**
   * Extract hooks used in a component
   */
  private extractHooks(node: ts.Node): ReactHookInfo[] {
    const hooks: ReactHookInfo[] = [];
    
    const visit = (n: ts.Node) => {
      if (ts.isCallExpression(n)) {
        const hookName = this.getCallExpressionName(n);
        if (hookName && hookName.startsWith('use')) {
          hooks.push({
            name: hookName,
            type: this.getHookType(hookName),
            dependencies: this.extractHookDependencies(n),
            isCustom: !this.isBuiltInHook(hookName),
            returnType: this.extractHookReturnType(n)
          });
        }
      }
      ts.forEachChild(n, visit);
    };
    
    visit(node);
    return hooks;
  }

  /**
   * Extract child components used in JSX
   */
  private extractChildComponents(node: ts.Node): string[] {
    const components: string[] = [];
    
    const visit = (n: ts.Node) => {
      if (ts.isJsxElement(n) || ts.isJsxSelfClosingElement(n)) {
        const tagName = this.getJSXTagName(n);
        if (tagName && /^[A-Z]/.test(tagName)) {
          components.push(tagName);
        }
      }
      ts.forEachChild(n, visit);
    };
    
    visit(node);
    return [...new Set(components)]; // Remove duplicates
  }

  /**
   * Extract event handlers
   */
  private extractEventHandlers(node: ts.Node): string[] {
    const handlers: string[] = [];
    
    const visit = (n: ts.Node) => {
      if (ts.isJsxAttribute(n) && ts.isIdentifier(n.name)) {
        const attrName = n.name.text;
        if (attrName.startsWith('on') && attrName.length > 2) {
          handlers.push(attrName);
        }
      }
      ts.forEachChild(n, visit);
    };
    
    visit(node);
    return [...new Set(handlers)];
  }

  /**
   * Extract lifecycle methods for class components
   */
  private extractLifecycleMethods(node: ts.Node): string[] {
    if (!ts.isClassDeclaration(node)) return [];
    
    const lifecycleMethods = [
      'componentDidMount',
      'componentDidUpdate',
      'componentWillUnmount',
      'componentWillMount',
      'componentWillReceiveProps',
      'componentWillUpdate',
      'shouldComponentUpdate',
      'getSnapshotBeforeUpdate',
      'getDerivedStateFromProps',
      'getDerivedStateFromError',
      'componentDidCatch'
    ];
    
    return node.members
      .filter(member => ts.isMethodDeclaration(member))
      .map(member => member.name?.getText() || '')
      .filter(name => lifecycleMethods.includes(name));
  }

  /**
   * Extract JSX elements used
   */
  private extractJSXElements(node: ts.Node): string[] {
    const elements: string[] = [];
    
    const visit = (n: ts.Node) => {
      if (ts.isJsxElement(n) || ts.isJsxSelfClosingElement(n)) {
        const tagName = this.getJSXTagName(n);
        if (tagName) {
          elements.push(tagName);
        }
      }
      ts.forEachChild(n, visit);
    };
    
    visit(node);
    return [...new Set(elements)];
  }

  /**
   * Extract props interface name
   */
  private extractPropsInterface(node: ts.Node): string | undefined {
    if (ts.isFunctionDeclaration(node) || ts.isVariableDeclaration(node)) {
      const parameters = this.getFunctionParameters(node);
      if (parameters.length > 0) {
        const firstParam = parameters[0];
        if (ts.isParameter(firstParam) && firstParam.type) {
          return this.getTypeName(firstParam.type);
        }
      }
    }
    return undefined;
  }

  /**
   * Extract state interface name
   */
  private extractStateInterface(node: ts.Node): string | undefined {
    if (ts.isClassDeclaration(node)) {
      const stateProperty = node.members.find(member => 
        ts.isPropertyDeclaration(member) && 
        member.name?.getText() === 'state'
      );
      
      if (stateProperty && ts.isPropertyDeclaration(stateProperty) && stateProperty.type) {
        return this.getTypeName(stateProperty.type);
      }
    }
    return undefined;
  }

  /**
   * Detect styling approach
   */
  private detectStylingApproach(node: ts.Node): string | undefined {
    const imports = this.extractImports(node);
    
    if (imports.some(imp => imp.includes('styled-components'))) {
      return 'styled-components';
    }
    if (imports.some(imp => imp.includes('emotion'))) {
      return 'emotion';
    }
    if (imports.some(imp => imp.includes('css-modules'))) {
      return 'css-modules';
    }
    if (imports.some(imp => imp.includes('tailwind'))) {
      return 'tailwind';
    }
    
    return undefined;
  }

  /**
   * Helper methods
   */
  private getNodeName(node: ts.Node): string | null {
    if (ts.isFunctionDeclaration(node)) {
      return node.name?.text || null;
    }
    if (ts.isVariableDeclaration(node)) {
      return ts.isIdentifier(node.name) ? node.name.text : null;
    }
    if (ts.isClassDeclaration(node)) {
      return node.name?.text || null;
    }
    return null;
  }

  private returnsJSX(node: ts.Node): boolean {
    let hasJSX = false;
    
    const visit = (n: ts.Node) => {
      if (ts.isJsxElement(n) || ts.isJsxSelfClosingElement(n) || ts.isJsxFragment(n)) {
        hasJSX = true;
        return;
      }
      ts.forEachChild(n, visit);
    };
    
    visit(node);
    return hasJSX;
  }

  private extendsReactComponent(node: ts.ClassDeclaration): boolean {
    return node.heritageClauses?.some(clause => 
      clause.token === ts.SyntaxKind.ExtendsKeyword &&
      clause.types.some(type => 
        type.expression.getText().includes('Component')
      )
    ) || false;
  }

  private hasRenderMethod(node: ts.ClassDeclaration): boolean {
    return node.members.some(member => 
      ts.isMethodDeclaration(member) && 
      member.name?.getText() === 'render'
    );
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

  private getHookType(hookName: string): ReactHookInfo['type'] {
    const hookTypes: Record<string, ReactHookInfo['type']> = {
      'useState': 'state',
      'useEffect': 'effect',
      'useContext': 'context',
      'useRef': 'ref',
      'useMemo': 'memo',
      'useCallback': 'callback'
    };
    
    return hookTypes[hookName] || 'custom';
  }

  private isBuiltInHook(hookName: string): boolean {
    const builtInHooks = [
      'useState', 'useEffect', 'useContext', 'useRef', 
      'useMemo', 'useCallback', 'useReducer', 'useImperativeHandle',
      'useLayoutEffect', 'useDebugValue'
    ];
    
    return builtInHooks.includes(hookName);
  }

  private extractHookDependencies(node: ts.Node): string[] {
    if (ts.isCallExpression(node) && node.arguments.length > 1) {
      const depsArg = node.arguments[1];
      if (ts.isArrayLiteralExpression(depsArg)) {
        return depsArg.elements
          .filter(ts.isIdentifier)
          .map(id => id.text);
      }
    }
    return [];
  }

  private extractHookReturnType(node: ts.Node): string | undefined {
    // This would require more complex type analysis
    return undefined;
  }

  private getJSXTagName(node: ts.JsxElement | ts.JsxSelfClosingElement): string | null {
    const tagName = node.tagName;
    if (ts.isIdentifier(tagName)) {
      return tagName.text;
    }
    if (ts.isQualifiedName(tagName)) {
      return tagName.right.text;
    }
    return null;
  }

  private getFunctionParameters(node: ts.Node): ts.Node[] {
    if (ts.isFunctionDeclaration(node)) {
      return node.parameters;
    }
    if (ts.isVariableDeclaration(node) && ts.isArrowFunction(node.initializer)) {
      return node.initializer.parameters;
    }
    return [];
  }

  private getTypeName(type: ts.TypeNode): string | undefined {
    if (ts.isTypeReferenceNode(type)) {
      return type.typeName.getText();
    }
    return undefined;
  }

  private extractImports(node: ts.Node): string[] {
    const imports: string[] = [];
    
    const visit = (n: ts.Node) => {
      if (ts.isImportDeclaration(n) && ts.isStringLiteral(n.moduleSpecifier)) {
        imports.push(n.moduleSpecifier.text);
      }
      ts.forEachChild(n, visit);
    };
    
    visit(node);
    return imports;
  }

  private isExported(node: ts.Node): boolean {
    return node.modifiers?.some(m => m.kind === ts.SyntaxKind.ExportKeyword) || false;
  }

  private isDefaultExport(node: ts.Node): boolean {
    return node.modifiers?.some(m => m.kind === ts.SyntaxKind.DefaultKeyword) || false;
  }

  private extractReturnType(node: ts.Node): string | undefined {
    if (ts.isFunctionDeclaration(node) && node.type) {
      return node.type.getText();
    }
    return undefined;
  }
}
