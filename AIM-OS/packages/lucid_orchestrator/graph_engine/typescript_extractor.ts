/**
 * TypeScript Extractor for Lucid Orchestrator
 *
 * Builds an IR graph by analysing real TypeScript/JavaScript projects.
 * The extractor loads the TypeScript compiler lazily so the IDE bundle
 * stays browser-friendly while server-side execution uses full AST data.
 */

import { IRNode, IREdge, NodeKind, IRGraphBuilder } from './ir_model'

type TypeScriptModule = any
type TSNode = any
type SourceFile = any
type TypeChecker = any
type SyntaxKind = number

interface ImportSpecifierInfo {
  local: string
  imported: string
}

interface ImportRecord {
  moduleSpecifier: string
  specifiers: ImportSpecifierInfo[]
  resolvedFileName?: string | null
}

interface FileSummary {
  filePath: string
  nodes: IRNode[]
  exports: Map<string, string>
  imports: ImportRecord[]
  localSymbolToNode: Map<string, string>
}

export interface ExtractionOptions {
  includeTests: boolean
  includeNodeModules: boolean
  extensions: string[]
  maxFileSize: number
}

export const DEFAULT_EXTRACTION_OPTIONS: ExtractionOptions = {
  includeTests: false,
  includeNodeModules: false,
  extensions: ['.ts', '.tsx', '.js', '.jsx'],
  maxFileSize: 1024 * 1024, // 1 MB
}

const DEFAULT_COMPILER_OPTIONS = {
  target: 99, // ScriptTarget.Latest
  module: 1, // ModuleKind.CommonJS
  jsx: 2, // JsxEmit.React
  allowJs: true,
  skipLibCheck: true,
  esModuleInterop: true,
}

const normalizePath = (filePath: string): string =>
  filePath.replace(/\\/g, '/')

const isTestFile = (filePath: string): boolean =>
  /(\.|\/)(test|spec)\.[tj]sx?$/.test(filePath) ||
  filePath.includes('__tests__') ||
  filePath.includes('__mocks__')

const nowISO = () => new Date().toISOString()

export class TypeScriptExtractor {
  private options: ExtractionOptions
  private tsModule: TypeScriptModule | null = null

  constructor(options: Partial<ExtractionOptions> = {}) {
    this.options = { ...DEFAULT_EXTRACTION_OPTIONS, ...options }
  }

  async extractIRGraphFromProject(projectPath: string): Promise<IRGraphBuilder> {
    const ts = await this.loadTypeScript()
    if (!ts) {
      return new IRGraphBuilder()
    }

    const files = this.collectProjectFiles(ts, projectPath)
    return this.buildGraph(ts, files)
  }

  async extractIRGraphFromFiles(filePaths: string[]): Promise<IRGraphBuilder> {
    const ts = await this.loadTypeScript()
    if (!ts) {
      return new IRGraphBuilder()
    }

    const normalized = Array.from(
      new Set(filePaths.map((file) => normalizePath(file)))
    )
    return this.buildGraph(ts, normalized)
  }

  private async loadTypeScript(): Promise<TypeScriptModule | null> {
    if (this.tsModule) {
      return this.tsModule
    }

    if (typeof globalThis === 'undefined') return null
    if (typeof (globalThis as any).process === 'undefined') return null

    try {
      const imported = await import(
        /* @vite-ignore */ 'typescript'
      )
      const ts = (imported as any).default ?? imported
      this.tsModule = ts as TypeScriptModule
      return this.tsModule
    } catch (error) {
      console.warn(
        '[TypeScriptExtractor] Failed to load TypeScript compiler API',
        error
      )
      return null
    }
  }

  private collectProjectFiles(ts: TypeScriptModule, projectPath: string): string[] {
    const excludes: string[] = []
    if (!this.options.includeNodeModules) {
      excludes.push('node_modules')
    }

    const files = ts.sys.readDirectory(
      projectPath,
      this.options.extensions,
      excludes
    )

    const filtered = files.filter((filePath: string) => {
      if (!this.options.includeTests && isTestFile(filePath)) return false
      const size = ts.sys.getFileSize?.(filePath)
      if (typeof size === 'number' && size > this.options.maxFileSize) return false
      return true
    })

    return filtered.map(normalizePath)
  }

  private async buildGraph(
    ts: TypeScriptModule,
    filePaths: string[]
  ): Promise<IRGraphBuilder> {
    const builder = new IRGraphBuilder()
    if (filePaths.length === 0) return builder

    const program = ts.createProgram(filePaths, DEFAULT_COMPILER_OPTIONS)
    const checker = program.getTypeChecker()

    const summaries: FileSummary[] = []

    for (const filePath of filePaths) {
      const sourceFile = program.getSourceFile(filePath)
      if (!sourceFile || sourceFile.isDeclarationFile) continue
      const summary = this.analyzeSourceFile(ts, sourceFile, checker)
      summary.nodes.forEach((node) => builder.addNode(node))
      summaries.push(summary)
    }

    this.createImportEdges(ts, program, builder, summaries)

    return builder
  }

  private analyzeSourceFile(
    ts: TypeScriptModule,
    sourceFile: SourceFile,
    checker: TypeChecker
  ): FileSummary {
    const filePath = normalizePath(sourceFile.fileName)

    const summary: FileSummary = {
      filePath,
      nodes: [],
      exports: new Map(),
      imports: [],
      localSymbolToNode: new Map(),
    }

    for (const statement of sourceFile.statements) {
      if (ts.isImportDeclaration(statement)) {
        summary.imports.push(this.describeImport(ts, statement))
        continue
      }

      if (ts.isFunctionDeclaration(statement) && statement.name) {
        const node = this.createFunctionNode(ts, checker, sourceFile, statement, filePath)
        summary.nodes.push(node)
        summary.localSymbolToNode.set(node.name, node.id)
        if (this.hasModifier(ts, statement, ts.SyntaxKind.ExportKeyword)) {
          summary.exports.set(node.name, node.id)
          if (this.hasModifier(ts, statement, ts.SyntaxKind.DefaultKeyword)) {
            summary.exports.set('default', node.id)
          }
        }
        continue
      }

      if (ts.isClassDeclaration(statement) && statement.name) {
        const node = this.createClassNode(ts, checker, sourceFile, statement, filePath)
        summary.nodes.push(node)
        summary.localSymbolToNode.set(node.name, node.id)
        if (this.hasModifier(ts, statement, ts.SyntaxKind.ExportKeyword)) {
          summary.exports.set(node.name, node.id)
          if (this.hasModifier(ts, statement, ts.SyntaxKind.DefaultKeyword)) {
            summary.exports.set('default', node.id)
          }
        }
        continue
      }

      if (ts.isVariableStatement(statement)) {
        const isExported = this.hasModifier(ts, statement, ts.SyntaxKind.ExportKeyword)
        for (const declaration of statement.declarationList.declarations) {
          if (
            ts.isIdentifier(declaration.name) &&
            declaration.initializer &&
            (ts.isArrowFunction(declaration.initializer) ||
              ts.isFunctionExpression(declaration.initializer))
          ) {
            const node = this.createVariableFunctionNode(
              ts,
              checker,
              sourceFile,
              declaration,
              filePath
            )
            summary.nodes.push(node)
            summary.localSymbolToNode.set(node.name, node.id)
            if (isExported) {
              summary.exports.set(node.name, node.id)
            }
          }
        }
        continue
      }

      if (ts.isExportAssignment(statement)) {
        const expr = statement.expression
        if (ts.isIdentifier(expr)) {
          const targetId = summary.localSymbolToNode.get(expr.text)
          if (targetId) {
            summary.exports.set('default', targetId)
          }
        }
      }
    }

    return summary
  }

  private createFunctionNode(
    ts: TypeScriptModule,
    checker: TypeChecker,
    sourceFile: SourceFile,
    node: any,
    filePath: string
  ): IRNode {
    const name = node.name!.text
    const kind = this.determineFunctionKind(ts, node, sourceFile)

    return this.buildNode(ts, checker, sourceFile, node, {
      name,
      kind,
      filePath,
      isAsync: this.hasModifier(ts, node, ts.SyntaxKind.AsyncKeyword),
    })
  }

  private createClassNode(
    ts: TypeScriptModule,
    checker: TypeChecker,
    sourceFile: SourceFile,
    node: any,
    filePath: string
  ): IRNode {
    const name = node.name!.text
    const isReactComponent = this.extendsReactComponent(ts, node)
    const kind: NodeKind = isReactComponent ? 'reactComponent' : 'component'

    return this.buildNode(ts, checker, sourceFile, node, {
      name,
      kind,
      filePath,
      isAsync: false,
    })
  }

  private createVariableFunctionNode(
    ts: TypeScriptModule,
    checker: TypeChecker,
    sourceFile: SourceFile,
    node: any,
    filePath: string
  ): IRNode {
    const name = (node.name as any).text
    const initializer = node.initializer as TSNode
    const kind = this.determineVariableFunctionKind(ts, initializer, sourceFile, name)
    const isAsync =
      this.hasModifier(ts, node.parent.parent, ts.SyntaxKind.AsyncKeyword) ||
      ('modifiers' in initializer &&
        this.hasModifier(ts, initializer as any, ts.SyntaxKind.AsyncKeyword))

    return this.buildNode(ts, checker, sourceFile, initializer, {
      name,
      kind,
      filePath,
      isAsync,
    })
  }

  private buildNode(
    ts: TypeScriptModule,
    checker: TypeChecker,
    sourceFile: SourceFile,
    node: TSNode,
    options: { name: string; kind: NodeKind; filePath: string; isAsync: boolean }
  ): IRNode {
    const { name, kind, filePath, isAsync } = options
    const range = this.getRange(ts, sourceFile, node)
    const metadataTime = nowISO()

    const performance = this.estimatePerformance(ts, node, isAsync)
    const security = this.estimateSecurity(filePath)
    const tags = this.deriveTags(kind, filePath)
    const inputs = this.extractInputs(ts, checker, node)

    const irNode: IRNode = {
      id: `${filePath}#${name}`,
      name,
      kind,
      filePath,
      range,
      inputs,
      outputs: [],
      sideEffects: this.detectSideEffects(ts, node),
      tags,
      status: 'clean',
      performance,
      security,
      metadata: {
        createdAt: metadataTime,
        lastModified: metadataTime,
        complexity: performance.estimatedComplexity,
        dependencies: [],
        dependents: [],
      },
    }

    return irNode
  }

  private describeImport(
    ts: TypeScriptModule,
    node: any
  ): ImportRecord {
    const moduleSpecifier = (node.moduleSpecifier as any).text
    const specifiers: ImportSpecifierInfo[] = []

    const clause = node.importClause
    if (!clause) {
      specifiers.push({ local: '*', imported: '*' })
    } else {
      if (clause.name) {
        specifiers.push({ local: clause.name.text, imported: 'default' })
      }
      if (clause.namedBindings) {
        if (ts.isNamespaceImport(clause.namedBindings)) {
          specifiers.push({
            local: clause.namedBindings.name.text,
            imported: '*',
          })
        } else if (ts.isNamedImports(clause.namedBindings)) {
          for (const element of clause.namedBindings.elements) {
            const imported = element.propertyName?.text ?? element.name.text
            specifiers.push({
              local: element.name.text,
              imported,
            })
          }
        }
      }
    }

    return { moduleSpecifier, specifiers }
  }

  private createImportEdges(
    ts: TypeScriptModule,
    program: any,
    builder: IRGraphBuilder,
    summaries: FileSummary[]
  ) {
    const compilerOptions = program.getCompilerOptions()
    const exportIndex = new Map<string, Map<string, string>>()

    for (const summary of summaries) {
      exportIndex.set(summary.filePath, summary.exports)
    }

    const graph = builder.getGraph()

    for (const summary of summaries) {
      for (const importRecord of summary.imports) {
        const resolvedFile =
          importRecord.resolvedFileName ??
          ts.resolveModuleName(
            importRecord.moduleSpecifier,
            summary.filePath,
            compilerOptions,
            ts.sys
          ).resolvedModule?.resolvedFileName

        if (!resolvedFile) continue
        const normalizedTarget = normalizePath(resolvedFile)
        const targetExports = exportIndex.get(normalizedTarget)
        if (!targetExports || targetExports.size === 0) continue

        for (const specifier of importRecord.specifiers) {
          const targetId =
            targetExports.get(specifier.imported) ??
            targetExports.get('default') ??
            Array.from(targetExports.values())[0]

          if (!targetId) continue

          for (const node of summary.nodes) {
            const timestamp = nowISO()
            const edge: IREdge = {
              from: node.id,
              to: targetId,
              type: 'imports',
              metadata: {
                createdAt: timestamp,
                lastSeen: timestamp,
                frequency: 1,
                isDirect: true,
                isAsync: false,
              },
            }

            builder.addEdge(edge)
            const fromNode = graph.nodes.get(node.id)
            const toNode = graph.nodes.get(targetId)
            if (fromNode) {
              if (!fromNode.metadata.dependencies.includes(targetId)) {
                fromNode.metadata.dependencies.push(targetId)
              }
            }
            if (toNode) {
              if (!toNode.metadata.dependents.includes(node.id)) {
                toNode.metadata.dependents.push(node.id)
              }
            }
          }
        }
      }
    }
  }

  private hasModifier(
    ts: TypeScriptModule,
    node: { modifiers?: any },
    kind: SyntaxKind
  ): boolean {
    return Boolean(node.modifiers?.some((modifier: any) => modifier.kind === kind))
  }

  private getRange(
    ts: TypeScriptModule,
    sourceFile: SourceFile,
    node: TSNode
  ): IRNode['range'] {
    const start = sourceFile.getLineAndCharacterOfPosition(node.getStart(sourceFile, false))
    const end = sourceFile.getLineAndCharacterOfPosition(node.getEnd())

    return {
      startLine: start.line + 1,
      endLine: end.line + 1,
      startColumn: start.character + 1,
      endColumn: end.character + 1,
    }
  }

  private determineFunctionKind(
    ts: TypeScriptModule,
    node: any,
    sourceFile: SourceFile
  ): NodeKind {
    if (!node.name) return 'function'
    const containsJsx = this.containsJsx(ts, node)
    const name = node.name.text
    if (containsJsx || (this.isPascalCase(name) && sourceFile.fileName.endsWith('.tsx'))) {
      return 'reactComponent'
    }
    return 'function'
  }

  private determineVariableFunctionKind(
    ts: TypeScriptModule,
    initializer: TSNode,
    sourceFile: SourceFile,
    name: string
  ): NodeKind {
    if (this.containsJsx(ts, initializer) || (this.isPascalCase(name) && sourceFile.fileName.endsWith('.tsx'))) {
      return 'reactComponent'
    }
    return 'function'
  }

  private extendsReactComponent(
    ts: TypeScriptModule,
    node: any
  ): boolean {
    if (!node.heritageClauses) return false
    for (const clause of node.heritageClauses) {
      if (clause.token !== ts.SyntaxKind.ExtendsKeyword) continue
      for (const type of clause.types) {
        const text = type.expression.getText()
        if (text === 'Component' || text === 'React.Component') {
          return true
        }
      }
    }
    return false
  }

  private containsJsx(ts: TypeScriptModule, node: TSNode): boolean {
    let found = false
    const visit = (child: TSNode) => {
      if (
        child.kind === ts.SyntaxKind.JsxElement ||
        child.kind === ts.SyntaxKind.JsxSelfClosingElement ||
        child.kind === ts.SyntaxKind.JsxFragment
      ) {
        found = true
        return
      }
      child.forEachChild(visit)
    }
    node.forEachChild(visit)
    return found
  }

  private isPascalCase(value: string): boolean {
    return /^[A-Z][A-Za-z0-9]*$/.test(value)
  }

  private estimatePerformance(
    ts: TypeScriptModule,
    node: TSNode,
    isAsync: boolean
  ): NonNullable<IRNode['performance']> {
    const complexity = this.estimateComplexity(ts, node)
    return {
      estimatedComplexity: complexity,
      estimatedExecutionTime: Math.min(1000, complexity * 50),
      memoryUsage: 1024 * Math.max(1, complexity),
      cpuUsage: Math.min(1, complexity / 20),
      isAsync,
      hasSideEffects: this.detectSideEffects(ts, node).length > 0,
      isPure: false,
    }
  }

  private estimateComplexity(ts: TypeScriptModule, node: TSNode): number {
    let branches = 0
    const visit = (child: TSNode) => {
      switch (child.kind) {
        case ts.SyntaxKind.IfStatement:
        case ts.SyntaxKind.ForStatement:
        case ts.SyntaxKind.ForOfStatement:
        case ts.SyntaxKind.ForInStatement:
        case ts.SyntaxKind.WhileStatement:
        case ts.SyntaxKind.DoStatement:
        case ts.SyntaxKind.SwitchStatement:
        case ts.SyntaxKind.ConditionalExpression:
          branches += 1
          break
        default:
          break
      }
      child.forEachChild(visit)
    }
    node.forEachChild(visit)
    return Math.max(1, branches + 1)
  }

  private extractInputs(
    ts: TypeScriptModule,
    checker: TypeChecker,
    node: TSNode
  ): string[] {
    const inputs: string[] = []

    const addParameter = (parameter: any) => {
      const name = parameter.name.getText()
      const type = parameter.type
        ? parameter.type.getText()
        : checker.typeToString(checker.getTypeAtLocation(parameter))
      inputs.push(`${name}: ${type}`)
    }

    if (this.isFunctionLike(ts, node) && node.parameters) {
      node.parameters.forEach(addParameter)
    } else if (ts.isVariableDeclaration(node) && node.initializer && this.isFunctionLike(ts, node.initializer)) {
      node.initializer.parameters.forEach(addParameter)
    }

    return inputs
  }

  private detectSideEffects(ts: TypeScriptModule, node: TSNode): string[] {
    const effects = new Set<string>()

    const visit = (child: TSNode) => {
      if (ts.isCallExpression(child)) {
        const expressionText = child.expression.getText()
        if (expressionText.startsWith('console.')) {
          effects.add('console')
        }
        if (expressionText.startsWith('fetch') || expressionText.startsWith('axios')) {
          effects.add('network')
        }
      }
      child.forEachChild(visit)
    }

    node.forEachChild(visit)

    return Array.from(effects)
  }

  private estimateSecurity(filePath: string): NonNullable<IRNode['security']> {
    const lower = filePath.toLowerCase()
    let level: 'low' | 'medium' | 'high' | 'critical' = 'low'

    if (lower.includes('auth') || lower.includes('payment')) {
      level = 'high'
    } else if (lower.includes('api') || lower.includes('server')) {
      level = 'medium'
    }

    return {
      level,
      isPublic: !lower.includes('internal'),
      handlesSensitiveData: level !== 'low',
      requiresAuth: level !== 'low',
    }
  }

  private deriveTags(kind: NodeKind, filePath: string): string[] {
    const tags = new Set<string>()
    tags.add(kind)
    if (filePath.includes('hooks')) tags.add('hook')
    if (filePath.includes('context')) tags.add('context')
    if (filePath.includes('service')) tags.add('service')
    if (filePath.includes('component')) tags.add('component')
    return Array.from(tags)
  }

  private isFunctionLike(
    ts: TypeScriptModule,
    node: TSNode
  ): node is any {
    return (
      ts.isFunctionDeclaration(node) ||
      ts.isMethodDeclaration(node) ||
      ts.isFunctionExpression(node) ||
      ts.isArrowFunction(node)
    )
  }
}

export async function extractIRGraphFromProject(
  projectPath: string,
  options?: Partial<ExtractionOptions>
): Promise<IRGraphBuilder> {
  const extractor = new TypeScriptExtractor(options)
  return extractor.extractIRGraphFromProject(projectPath)
}

export async function extractIRGraphFromFiles(
  filePaths: string[],
  options?: Partial<ExtractionOptions>
): Promise<IRGraphBuilder> {
  const extractor = new TypeScriptExtractor(options)
  return extractor.extractIRGraphFromFiles(filePaths)
}
