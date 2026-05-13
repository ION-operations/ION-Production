/**
 * Code Pane Data Service
 * 
 * Handles file system operations, dependency analysis, and code metrics
 * for the Code Pane of the Lucid Orchestrator.
 */

import { 
  CodePaneData, 
  SystemInfo, 
  FileCollection, 
  FileInfo, 
  CodeMetrics, 
  DependencyGraph,
  FileMetadata,
  FunctionInfo,
  ClassInfo,
  InterfaceInfo,
  PropertyInfo
} from '../data_models/core_interfaces';
import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';

export class CodePaneService {
  private systemRoot: string = '';
  private fileWatchers: Map<string, fs.FSWatcher> = new Map();
  private changeCallbacks: Set<(data: CodePaneData) => void> = new Set();

  constructor(systemRoot: string) {
    this.systemRoot = systemRoot;
  }

  /**
   * Load all files for a system
   */
  async loadSystemFiles(systemId: string): Promise<FileCollection> {
    const systemPath = path.join(this.systemRoot, systemId);
    
    if (!fs.existsSync(systemPath)) {
      throw new Error(`System path not found: ${systemPath}`);
    }

    const files: FileCollection = {
      documentation: [],
      source: [],
      tests: [],
      config: [],
      other: []
    };

    await this.scanDirectory(systemPath, files, systemId);
    return files;
  }

  /**
   * Scan directory recursively for files
   */
  private async scanDirectory(
    dirPath: string, 
    files: FileCollection, 
    systemId: string,
    relativePath: string = ''
  ): Promise<void> {
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dirPath, entry.name);
      const relPath = path.join(relativePath, entry.name);

      if (entry.isDirectory()) {
        // Skip certain directories
        if (this.shouldSkipDirectory(entry.name)) {
          continue;
        }
        await this.scanDirectory(fullPath, files, systemId, relPath);
      } else if (entry.isFile()) {
        const fileInfo = await this.analyzeFile(fullPath, relPath, systemId);
        this.categorizeFile(fileInfo, files);
      }
    }
  }

  /**
   * Determine if directory should be skipped
   */
  private shouldSkipDirectory(dirName: string): boolean {
    const skipDirs = [
      'node_modules',
      '.git',
      '.vscode',
      '.idea',
      'dist',
      'build',
      'coverage',
      '.nyc_output',
      'temp',
      'tmp'
    ];
    return skipDirs.includes(dirName);
  }

  /**
   * Analyze a single file
   */
  private async analyzeFile(
    fullPath: string, 
    relativePath: string, 
    systemId: string
  ): Promise<FileInfo> {
    const stats = fs.statSync(fullPath);
    const content = fs.readFileSync(fullPath, 'utf-8');
    const contentHash = crypto.createHash('md5').update(content).digest('hex');
    
    const fileInfo: FileInfo = {
      id: `${systemId}:${relativePath}`,
      path: relativePath,
      name: path.basename(relativePath),
      type: this.getFileType(relativePath),
      size: stats.size,
      lines: content.split('\n').length,
      lastModified: stats.mtime.toISOString(),
      contentHash,
      metadata: await this.extractMetadata(fullPath, content, relativePath)
    };

    return fileInfo;
  }

  /**
   * Determine file type from extension
   */
  private getFileType(filePath: string): FileInfo['type'] {
    const ext = path.extname(filePath).toLowerCase();
    
    const typeMap: Record<string, FileInfo['type']> = {
      '.md': 'markdown',
      '.py': 'python',
      '.ts': 'typescript',
      '.tsx': 'typescript',
      '.js': 'javascript',
      '.jsx': 'javascript',
      '.json': 'json',
      '.yaml': 'yaml',
      '.yml': 'yaml'
    };

    return typeMap[ext] || 'other';
  }

  /**
   * Extract metadata from file content
   */
  private async extractMetadata(
    filePath: string, 
    content: string, 
    relativePath: string
  ): Promise<FileMetadata> {
    const metadata: FileMetadata = {};

    // Check if it's a documentation file
    if (relativePath.includes('knowledge_architecture') && filePath.endsWith('.md')) {
      metadata.level = this.extractDocumentationLevel(relativePath);
      metadata.wordCount = this.countWords(content);
    }

    // Extract code-specific metadata
    if (this.isCodeFile(filePath)) {
      metadata.complexity = this.calculateComplexity(content);
      metadata.functions = this.extractFunctions(content, filePath);
      metadata.classes = this.extractClasses(content, filePath);
      metadata.interfaces = this.extractInterfaces(content, filePath);
      metadata.imports = this.extractImports(content);
      metadata.exports = this.extractExports(content);
    }

    // Extract test coverage if it's a test file
    if (this.isTestFile(filePath)) {
      metadata.testCoverage = await this.calculateTestCoverage(filePath);
    }

    return metadata;
  }

  /**
   * Extract documentation level from file path
   */
  private extractDocumentationLevel(filePath: string): 'L0' | 'L1' | 'L2' | 'L3' | 'L4' | undefined {
    const levelMatch = filePath.match(/L(\d)_/);
    if (levelMatch) {
      const level = parseInt(levelMatch[1]);
      return `L${level}` as 'L0' | 'L1' | 'L2' | 'L3' | 'L4';
    }
    return undefined;
  }

  /**
   * Count words in content
   */
  private countWords(content: string): number {
    return content.split(/\s+/).filter(word => word.length > 0).length;
  }

  /**
   * Check if file is a code file
   */
  private isCodeFile(filePath: string): boolean {
    const codeExtensions = ['.py', '.ts', '.tsx', '.js', '.jsx'];
    return codeExtensions.some(ext => filePath.endsWith(ext));
  }

  /**
   * Check if file is a test file
   */
  private isTestFile(filePath: string): boolean {
    return filePath.includes('test') || filePath.includes('spec') || filePath.includes('__tests__');
  }

  /**
   * Calculate code complexity (simplified)
   */
  private calculateComplexity(content: string): number {
    // Simple complexity calculation based on control structures
    const complexityKeywords = ['if', 'else', 'elif', 'for', 'while', 'try', 'except', 'catch', 'switch', 'case'];
    let complexity = 1; // Base complexity

    for (const keyword of complexityKeywords) {
      const regex = new RegExp(`\\b${keyword}\\b`, 'g');
      const matches = content.match(regex);
      if (matches) {
        complexity += matches.length;
      }
    }

    return Math.min(complexity, 10); // Cap at 10
  }

  /**
   * Extract functions from code
   */
  private extractFunctions(content: string, filePath: string): FunctionInfo[] {
    const functions: FunctionInfo[] = [];
    
    if (filePath.endsWith('.py')) {
      const functionRegex = /def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*(\w+))?/g;
      let match;
      let lineNumber = 1;
      
      for (const line of content.split('\n')) {
        if ((match = functionRegex.exec(line)) !== null) {
          functions.push({
            name: match[1],
            line: lineNumber,
            parameters: match[2] ? match[2].split(',').map(p => p.trim()) : [],
            returnType: match[3],
            complexity: this.calculateComplexity(line),
            documentation: this.extractFunctionDoc(content, lineNumber)
          });
        }
        lineNumber++;
      }
    } else if (filePath.endsWith('.ts') || filePath.endsWith('.tsx')) {
      const functionRegex = /(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*(\w+))?/g;
      let match;
      let lineNumber = 1;
      
      for (const line of content.split('\n')) {
        if ((match = functionRegex.exec(line)) !== null) {
          functions.push({
            name: match[1],
            line: lineNumber,
            parameters: match[2] ? match[2].split(',').map(p => p.trim()) : [],
            returnType: match[3],
            complexity: this.calculateComplexity(line),
            documentation: this.extractFunctionDoc(content, lineNumber)
          });
        }
        lineNumber++;
      }
    }

    return functions;
  }

  /**
   * Extract classes from code
   */
  private extractClasses(content: string, filePath: string): ClassInfo[] {
    const classes: ClassInfo[] = [];
    
    if (filePath.endsWith('.py')) {
      const classRegex = /class\s+(\w+)(?:\(([^)]*)\))?:/g;
      let match;
      let lineNumber = 1;
      
      for (const line of content.split('\n')) {
        if ((match = classRegex.exec(line)) !== null) {
          classes.push({
            name: match[1],
            line: lineNumber,
            methods: [], // Would need more complex parsing
            properties: [],
            inheritance: match[2] ? [match[2]] : [],
            complexity: this.calculateComplexity(line),
            documentation: this.extractFunctionDoc(content, lineNumber)
          });
        }
        lineNumber++;
      }
    }

    return classes;
  }

  /**
   * Extract interfaces from TypeScript code
   */
  private extractInterfaces(content: string, filePath: string): InterfaceInfo[] {
    const interfaces: InterfaceInfo[] = [];
    
    if (filePath.endsWith('.ts') || filePath.endsWith('.tsx')) {
      const interfaceRegex = /interface\s+(\w+)(?:\s+extends\s+([^{]+))?\s*{/g;
      let match;
      let lineNumber = 1;
      
      for (const line of content.split('\n')) {
        if ((match = interfaceRegex.exec(line)) !== null) {
          interfaces.push({
            name: match[1],
            line: lineNumber,
            properties: [],
            methods: [],
            inheritance: match[2] ? match[2].split(',').map(i => i.trim()) : [],
            documentation: this.extractFunctionDoc(content, lineNumber)
          });
        }
        lineNumber++;
      }
    }

    return interfaces;
  }

  /**
   * Extract imports from code
   */
  private extractImports(content: string): string[] {
    const imports: string[] = [];
    const importRegex = /(?:import|from)\s+['"]([^'"]+)['"]/g;
    let match;
    
    while ((match = importRegex.exec(content)) !== null) {
      imports.push(match[1]);
    }
    
    return imports;
  }

  /**
   * Extract exports from code
   */
  private extractExports(content: string): string[] {
    const exports: string[] = [];
    const exportRegex = /export\s+(?:const|let|var|function|class|interface|type)\s+(\w+)/g;
    let match;
    
    while ((match = exportRegex.exec(content)) !== null) {
      exports.push(match[1]);
    }
    
    return exports;
  }

  /**
   * Extract function documentation
   */
  private extractFunctionDoc(content: string, lineNumber: number): string | undefined {
    const lines = content.split('\n');
    const docLines: string[] = [];
    
    // Look for docstring above the function
    for (let i = lineNumber - 2; i >= 0; i--) {
      const line = lines[i].trim();
      if (line.startsWith('"""') || line.startsWith("'''")) {
        docLines.unshift(line);
        break;
      } else if (line.startsWith('#')) {
        docLines.unshift(line.substring(1).trim());
      } else if (line.length > 0) {
        break;
      }
    }
    
    return docLines.length > 0 ? docLines.join(' ') : undefined;
  }

  /**
   * Calculate test coverage (simplified)
   */
  private async calculateTestCoverage(filePath: string): Promise<number> {
    // This would integrate with actual test coverage tools
    // For now, return a mock value
    return Math.random() * 0.5 + 0.5; // 50-100% coverage
  }

  /**
   * Categorize file into appropriate collection
   */
  private categorizeFile(fileInfo: FileInfo, files: FileCollection): void {
    const { path: filePath, type } = fileInfo;
    
    if (filePath.includes('knowledge_architecture') && type === 'markdown') {
      files.documentation.push(fileInfo);
    } else if (filePath.includes('test') || filePath.includes('spec')) {
      files.tests.push(fileInfo);
    } else if (['json', 'yaml'].includes(type) || filePath.includes('config')) {
      files.config.push(fileInfo);
    } else if (['python', 'typescript', 'javascript'].includes(type)) {
      files.source.push(fileInfo);
    } else {
      files.other.push(fileInfo);
    }
  }

  /**
   * Analyze dependencies between files
   */
  async analyzeDependencies(files: FileInfo[]): Promise<DependencyGraph> {
    const dependencies: DependencyGraph = {
      internal: [],
      external: [],
      documentation: []
    };

    for (const file of files) {
      if (file.metadata.imports) {
        for (const importPath of file.metadata.imports) {
          const targetFile = this.findFileByImport(importPath, files);
          
          if (targetFile) {
            dependencies.internal.push({
              from: file.id,
              to: targetFile.id,
              type: 'import',
              weight: 1.0,
              metadata: { importPath }
            });
          } else {
            dependencies.external.push({
              from: file.id,
              to: importPath,
              type: 'import',
              weight: 0.5,
              metadata: { importPath }
            });
          }
        }
      }

      // Add documentation references
      if (file.metadata.level) {
        dependencies.documentation.push({
          from: file.id,
          to: `doc:${file.metadata.level}`,
          type: 'reference',
          weight: 0.8,
          metadata: { level: file.metadata.level }
        });
      }
    }

    return dependencies;
  }

  /**
   * Find file by import path
   */
  private findFileByImport(importPath: string, files: FileInfo[]): FileInfo | null {
    // Simplified file resolution
    for (const file of files) {
      if (file.path.includes(importPath) || file.name === importPath) {
        return file;
      }
    }
    return null;
  }

  /**
   * Calculate code metrics
   */
  async calculateMetrics(files: FileCollection): Promise<CodeMetrics> {
    const allFiles = [
      ...files.documentation,
      ...files.source,
      ...files.tests,
      ...files.config,
      ...files.other
    ];

    const totalLines = allFiles.reduce((sum, file) => sum + file.lines, 0);
    const totalFiles = allFiles.length;
    
    const testFiles = files.tests.length;
    const sourceFiles = files.source.length;
    const testCoverage = testFiles > 0 ? testFiles / sourceFiles : 0;
    
    const docFiles = files.documentation.length;
    const docCoverage = docFiles > 0 ? docFiles / sourceFiles : 0;
    
    const avgComplexity = files.source.reduce((sum, file) => 
      sum + (file.metadata.complexity || 0), 0) / sourceFiles;
    
    const maintainability = Math.max(0, 10 - avgComplexity);
    const technicalDebt = Math.max(0, avgComplexity - 5);
    const codeQuality = (testCoverage + docCoverage + (maintainability / 10)) / 3;

    return {
      totalLines,
      totalFiles,
      testCoverage,
      documentationCoverage: docCoverage,
      complexity: avgComplexity,
      maintainability,
      technicalDebt,
      codeQuality
    };
  }

  /**
   * Watch for file changes
   */
  async watchFileChanges(systemId: string, callback: (data: CodePaneData) => void): Promise<void> {
    this.changeCallbacks.add(callback);
    
    const systemPath = path.join(this.systemRoot, systemId);
    if (fs.existsSync(systemPath)) {
      const watcher = fs.watch(systemPath, { recursive: true }, async () => {
        const data = await this.loadSystemData(systemId);
        this.changeCallbacks.forEach(cb => cb(data));
      });
      
      this.fileWatchers.set(systemId, watcher);
    }
  }

  /**
   * Load complete system data
   */
  async loadSystemData(systemId: string): Promise<CodePaneData> {
    const files = await this.loadSystemFiles(systemId);
    const dependencies = await this.analyzeDependencies([
      ...files.documentation,
      ...files.source,
      ...files.tests,
      ...files.config,
      ...files.other
    ]);
    const metrics = await this.calculateMetrics(files);

    return {
      system: {
        id: systemId,
        name: systemId,
        description: `System ${systemId}`,
        status: 'active',
        rootPath: path.join(this.systemRoot, systemId),
        language: 'typescript'
      },
      files,
      metrics,
      dependencies
    };
  }

  /**
   * Stop watching file changes
   */
  stopWatching(systemId: string): void {
    const watcher = this.fileWatchers.get(systemId);
    if (watcher) {
      watcher.close();
      this.fileWatchers.delete(systemId);
    }
  }

  /**
   * Cleanup all watchers
   */
  cleanup(): void {
    this.fileWatchers.forEach(watcher => watcher.close());
    this.fileWatchers.clear();
    this.changeCallbacks.clear();
  }
}
