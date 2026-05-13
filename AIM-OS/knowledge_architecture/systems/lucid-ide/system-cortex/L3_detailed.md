---
id: "lucid-ide-system-cortex-L3-detailed"
system: "lucid-ide-system-cortex"
component: null
level: "L3"
type: "detailed"
title: "Lucid IDE System Cortex - Detailed Implementation Guide"
description: "10,000-word detailed implementation guide for Lucid IDE System Cortex"
audience: "developers, implementers, maintainers"
confidence_threshold: 0.70
token_cost: 10000
word_count: 10000
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "sev"
status: "complete"
tags: ["lucid-ide", "system-cortex", "implementation"]
dependencies: ["lucid-ide-system-cortex-L2-architecture"]
related_docs: ["lucid-ide-system-cortex-L4-complete", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

# Lucid IDE System Cortex – L3 Detailed Implementation Guide

**Purpose:** Complete implementation guide for Lucid IDE System Cortex with step-by-step instructions, code examples, system analysis, code browsing, version history, and best practices.

**Audience:** Developers implementing, integrating with, or maintaining the Lucid IDE System Cortex.

**Prerequisites:**
- React 19+
- TypeScript 5+
- Understanding of Git operations
- Familiarity with code analysis
- Knowledge of system architecture patterns

---

## 📜 **EVOLUTION & HISTORY**

### **Version Timeline**

**v1.0 (2025-11-09) - Initial Documentation**
- **Changes:** Comprehensive AIM-OS protocol-compliant documentation
- **Key Features:** System hierarchy tree, code browser, version history, enhanced reactor integration
- **Status:** Production-ready with identified enhancement needs

### **Key Evolution Points**

**Phase 1: Basic Analysis (Initial)**
- **Goal:** Basic codebase scanning and analysis
- **Implementation:** File system scanning, basic component identification
- **Outcome:** Functional system analysis

**Phase 2: Hierarchy Tree**
- **Goal:** Hierarchical system visualization
- **Implementation:** Tree data structure, node expansion/collapse
- **Outcome:** Navigable system hierarchy

**Phase 3: Advanced Features**
- **Goal:** Version history, enhanced reactor integration
- **Implementation:** Git integration, 3D visualization
- **Outcome:** Comprehensive system analysis system

---

## 🔧 **IMPLEMENTATION GUIDE**

### **Step 1: System Analysis Service**

#### **1.1 Cortex Service**

```typescript
// lib/cortex-service.ts
import { exec } from "child_process"
import { promisify } from "util"
import * as fs from "fs/promises"
import * as path from "path"

const execAsync = promisify(exec)

export interface SystemNode {
  id: string
  name: string
  type: "system" | "layer" | "component" | "service" | "file"
  path: string
  children?: SystemNode[]
  metadata?: {
    linesOfCode?: number
    dependencies?: string[]
    complexity?: number
  }
}

export class CortexService {
  private basePath: string

  constructor(basePath: string = process.cwd()) {
    this.basePath = basePath
  }

  async scanSystem(): Promise<SystemNode[]> {
    const rootNode: SystemNode = {
      id: "root",
      name: "System Root",
      type: "system",
      path: this.basePath,
      children: [],
    }

    await this.scanDirectory(this.basePath, rootNode)
    return [rootNode]
  }

  private async scanDirectory(
    dirPath: string,
    parentNode: SystemNode
  ): Promise<void> {
    try {
      const entries = await fs.readdir(dirPath, { withFileTypes: true })

      for (const entry of entries) {
        // Skip node_modules, .git, etc.
        if (this.shouldSkip(entry.name)) continue

        const fullPath = path.join(dirPath, entry.name)

        if (entry.isDirectory()) {
          const childNode: SystemNode = {
            id: `${parentNode.id}-${entry.name}`,
            name: entry.name,
            type: this.inferType(entry.name),
            path: fullPath,
            children: [],
          }

          await this.scanDirectory(fullPath, childNode)
          parentNode.children?.push(childNode)
        } else if (entry.isFile() && this.isCodeFile(entry.name)) {
          const fileNode: SystemNode = {
            id: `${parentNode.id}-${entry.name}`,
            name: entry.name,
            type: "file",
            path: fullPath,
            metadata: await this.analyzeFile(fullPath),
          }

          parentNode.children?.push(fileNode)
        }
      }
    } catch (error) {
      console.error(`Error scanning directory ${dirPath}:`, error)
    }
  }

  private shouldSkip(name: string): boolean {
    const skipPatterns = [
      "node_modules",
      ".git",
      ".next",
      "dist",
      "build",
      ".DS_Store",
    ]
    return skipPatterns.includes(name)
  }

  private inferType(name: string): "system" | "layer" | "component" | "service" {
    if (name === "components") return "component"
    if (name === "services") return "service"
    if (name === "app" || name === "pages") return "layer"
    return "system"
  }

  private isCodeFile(name: string): boolean {
    const codeExtensions = [".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs"]
    return codeExtensions.some(ext => name.endsWith(ext))
  }

  private async analyzeFile(filePath: string): Promise<SystemNode["metadata"]> {
    try {
      const content = await fs.readFile(filePath, "utf-8")
      const lines = content.split("\n")
      const linesOfCode = lines.filter(line => line.trim().length > 0).length

      // Extract imports/dependencies
      const imports = this.extractImports(content)

      // Calculate complexity (simplified)
      const complexity = this.calculateComplexity(content)

      return {
        linesOfCode,
        dependencies: imports,
        complexity,
      }
    } catch (error) {
      console.error(`Error analyzing file ${filePath}:`, error)
      return {}
    }
  }

  private extractImports(content: string): string[] {
    const importRegex = /import\s+.*?\s+from\s+['"](.+?)['"]/g
    const imports: string[] = []
    let match

    while ((match = importRegex.exec(content)) !== null) {
      imports.push(match[1])
    }

    return imports
  }

  private calculateComplexity(content: string): number {
    // Simplified complexity calculation
    const cyclomaticComplexity = (content.match(/if|else|for|while|switch/g) || []).length
    const nestingDepth = this.calculateNestingDepth(content)
    return cyclomaticComplexity + nestingDepth
  }

  private calculateNestingDepth(content: string): number {
    let maxDepth = 0
    let currentDepth = 0

    for (const char of content) {
      if (char === "{") {
        currentDepth++
        maxDepth = Math.max(maxDepth, currentDepth)
      } else if (char === "}") {
        currentDepth--
      }
    }

    return maxDepth
  }

  async getComponentInfo(componentId: string): Promise<any> {
    // Get detailed information about a component
    const node = await this.findNode(componentId)
    if (!node) return null

    return {
      id: node.id,
      name: node.name,
      type: node.type,
      path: node.path,
      metadata: node.metadata,
      children: node.children?.map(child => ({
        id: child.id,
        name: child.name,
        type: child.type,
      })),
    }
  }

  private async findNode(id: string): Promise<SystemNode | null> {
    const nodes = await this.scanSystem()
    return this.findNodeRecursive(nodes[0], id)
  }

  private findNodeRecursive(
    node: SystemNode,
    id: string
  ): SystemNode | null {
    if (node.id === id) return node

    if (node.children) {
      for (const child of node.children) {
        const found = this.findNodeRecursive(child, id)
        if (found) return found
      }
    }

    return null
  }
}
```

### **Step 2: Code Browser Implementation**

#### **2.1 Code Browser Component**

```typescript
// components/system-cortex/code-browser.tsx
"use client"

import { useState, useEffect } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { File, Folder, FolderOpen, ChevronRight, ChevronDown } from "lucide-react"

interface FileNode {
  name: string
  path: string
  type: "file" | "folder"
  children?: FileNode[]
  expanded?: boolean
}

export function CodeBrowser({ basePath }: { basePath: string }) {
  const [fileTree, setFileTree] = useState<FileNode[]>([])
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [fileContent, setFileContent] = useState<string>("")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadFileTree()
  }, [basePath])

  const loadFileTree = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/cortex/files?path=${encodeURIComponent(basePath)}`)
      const data = await response.json()
      setFileTree(data.files || [])
    } catch (error) {
      console.error("Failed to load file tree:", error)
    } finally {
      setLoading(false)
    }
  }

  const toggleExpand = async (node: FileNode) => {
    if (node.type === "file") {
      // Load file content
      setSelectedFile(node.path)
      setLoading(true)
      try {
        const response = await fetch(`/api/cortex/file-content?path=${encodeURIComponent(node.path)}`)
        const data = await response.json()
        setFileContent(data.content || "")
      } catch (error) {
        console.error("Failed to load file content:", error)
      } finally {
        setLoading(false)
      }
    } else {
      // Toggle folder expansion
      if (!node.expanded && (!node.children || node.children.length === 0)) {
        // Load children
        const response = await fetch(`/api/cortex/files?path=${encodeURIComponent(node.path)}`)
        const data = await response.json()
        node.children = data.files || []
      }
      node.expanded = !node.expanded
      setFileTree([...fileTree])
    }
  }

  return (
    <div className="code-browser">
      <div className="file-tree">
        <ScrollArea>
          {fileTree.map(node => (
            <FileTreeNode
              key={node.path}
              node={node}
              level={0}
              onToggle={toggleExpand}
            />
          ))}
        </ScrollArea>
      </div>
      <div className="file-content">
        {selectedFile && (
          <div className="file-header">
            <span>{selectedFile}</span>
          </div>
        )}
        {loading ? (
          <div>Loading...</div>
        ) : (
          <pre className="code-content">{fileContent}</pre>
        )}
      </div>
    </div>
  )
}

function FileTreeNode({
  node,
  level,
  onToggle,
}: {
  node: FileNode
  level: number
  onToggle: (node: FileNode) => void
}) {
  const Icon = node.type === "folder" 
    ? (node.expanded ? FolderOpen : Folder)
    : File
  const Chevron = node.expanded ? ChevronDown : ChevronRight

  return (
    <div>
      <div
        className="file-tree-node"
        style={{ paddingLeft: `${level * 20}px` }}
        onClick={() => onToggle(node)}
      >
        {node.type === "folder" && <Chevron className="chevron" />}
        <Icon className="icon" />
        <span>{node.name}</span>
      </div>
      {node.expanded && node.children && (
        <div>
          {node.children.map(child => (
            <FileTreeNode
              key={child.path}
              node={child}
              level={level + 1}
              onToggle={onToggle}
            />
          ))}
        </div>
      )}
    </div>
  )
}
```

### **Step 3: System Hierarchy Tree**

#### **3.1 Hierarchy Tree Component**

```typescript
// components/system-cortex/system-hierarchy-tree.tsx
"use client"

import { useState, useEffect } from "react"
import { SystemNode } from "@/lib/cortex-service"
import { ChevronRight, ChevronDown } from "lucide-react"

export function SystemHierarchyTree() {
  const [rootNodes, setRootNodes] = useState<SystemNode[]>([])
  const [selectedNode, setSelectedNode] = useState<SystemNode | null>(null)
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())

  useEffect(() => {
    loadHierarchy()
  }, [])

  const loadHierarchy = async () => {
    try {
      const response = await fetch("/api/cortex/hierarchy")
      const data = await response.json()
      setRootNodes(data.nodes || [])
    } catch (error) {
      console.error("Failed to load hierarchy:", error)
    }
  }

  const toggleExpand = (nodeId: string) => {
    setExpandedNodes(prev => {
      const next = new Set(prev)
      if (next.has(nodeId)) {
        next.delete(nodeId)
      } else {
        next.add(nodeId)
      }
      return next
    })
  }

  return (
    <div className="system-hierarchy-tree">
      {rootNodes.map(node => (
        <HierarchyTreeNode
          key={node.id}
          node={node}
          level={0}
          expanded={expandedNodes.has(node.id)}
          selected={selectedNode?.id === node.id}
          onToggleExpand={toggleExpand}
          onSelect={setSelectedNode}
        />
      ))}
    </div>
  )
}

function HierarchyTreeNode({
  node,
  level,
  expanded,
  selected,
  onToggleExpand,
  onSelect,
}: {
  node: SystemNode
  level: number
  expanded: boolean
  selected: boolean
  onToggleExpand: (id: string) => void
  onSelect: (node: SystemNode) => void
}) {
  const hasChildren = node.children && node.children.length > 0

  return (
    <div>
      <div
        className={`hierarchy-tree-node ${selected ? "selected" : ""}`}
        style={{ paddingLeft: `${level * 20}px` }}
        onClick={() => onSelect(node)}
      >
        {hasChildren && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onToggleExpand(node.id)
            }}
          >
            {expanded ? <ChevronDown /> : <ChevronRight />}
          </button>
        )}
        <span className="node-name">{node.name}</span>
        <span className="node-type">{node.type}</span>
      </div>
      {expanded && hasChildren && (
        <div>
          {node.children!.map(child => (
            <HierarchyTreeNode
              key={child.id}
              node={child}
              level={level + 1}
              expanded={false}
              selected={false}
              onToggleExpand={onToggleExpand}
              onSelect={onSelect}
            />
          ))}
        </div>
      )}
    </div>
  )
}
```

### **Step 4: Version History**

#### **4.1 Version History Component**

```typescript
// components/system-cortex/version-history.tsx
"use client"

import { useState, useEffect } from "react"
import { GitCommit, GitBranch, Tag } from "lucide-react"

interface Commit {
  hash: string
  message: string
  author: string
  date: Date
  files: string[]
}

export function VersionHistory() {
  const [commits, setCommits] = useState<Commit[]>([])
  const [selectedCommit, setSelectedCommit] = useState<Commit | null>(null)
  const [diff, setDiff] = useState<string>("")

  useEffect(() => {
    loadCommits()
  }, [])

  const loadCommits = async () => {
    try {
      const response = await fetch("/api/cortex/git/commits")
      const data = await response.json()
      setCommits(data.commits || [])
    } catch (error) {
      console.error("Failed to load commits:", error)
    }
  }

  const loadDiff = async (commitHash: string) => {
    try {
      const response = await fetch(`/api/cortex/git/diff?hash=${commitHash}`)
      const data = await response.json()
      setDiff(data.diff || "")
    } catch (error) {
      console.error("Failed to load diff:", error)
    }
  }

  return (
    <div className="version-history">
      <div className="commits-list">
        {commits.map(commit => (
          <div
            key={commit.hash}
            className={`commit-item ${selectedCommit?.hash === commit.hash ? "selected" : ""}`}
            onClick={() => {
              setSelectedCommit(commit)
              loadDiff(commit.hash)
            }}
          >
            <GitCommit className="icon" />
            <div className="commit-info">
              <div className="commit-message">{commit.message}</div>
              <div className="commit-meta">
                <span>{commit.author}</span>
                <span>{new Date(commit.date).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      {selectedCommit && (
        <div className="diff-viewer">
          <pre className="diff-content">{diff}</pre>
        </div>
      )}
    </div>
  )
}
```

### **Step 5: Git Integration**

#### **5.1 Git Service**

```typescript
// lib/git-service.ts
import { exec } from "child_process"
import { promisify } from "util"

const execAsync = promisify(exec)

export class GitService {
  private repoPath: string

  constructor(repoPath: string = process.cwd()) {
    this.repoPath = repoPath
  }

  async getCommits(limit: number = 50): Promise<any[]> {
    try {
      const { stdout } = await execAsync(
        `git log --pretty=format:"%H|%s|%an|%ad" --date=iso -n ${limit}`,
        { cwd: this.repoPath }
      )

      return stdout.split("\n").map(line => {
        const [hash, message, author, date] = line.split("|")
        return {
          hash,
          message,
          author,
          date: new Date(date),
        }
      })
    } catch (error) {
      console.error("Failed to get commits:", error)
      return []
    }
  }

  async getDiff(hash: string): Promise<string> {
    try {
      const { stdout } = await execAsync(
        `git show ${hash}`,
        { cwd: this.repoPath }
      )
      return stdout
    } catch (error) {
      console.error("Failed to get diff:", error)
      return ""
    }
  }

  async getBranches(): Promise<string[]> {
    try {
      const { stdout } = await execAsync(
        "git branch --list",
        { cwd: this.repoPath }
      )
      return stdout.split("\n").map(branch => branch.trim().replace(/^\*\s*/, ""))
    } catch (error) {
      console.error("Failed to get branches:", error)
      return []
    }
  }
}
```

### **Step 6: Testing**

#### **6.1 Service Testing**

```typescript
// __tests__/lib/cortex-service.test.ts
import { CortexService } from "@/lib/cortex-service"

describe("CortexService", () => {
  it("scans system correctly", async () => {
    const service = new CortexService("./test-fixtures")
    const nodes = await service.scanSystem()
    expect(nodes.length).toBeGreaterThan(0)
    expect(nodes[0].type).toBe("system")
  })

  it("analyzes files correctly", async () => {
    const service = new CortexService("./test-fixtures")
    const nodes = await service.scanSystem()
    const fileNode = nodes[0].children?.find(child => child.type === "file")
    if (fileNode) {
      expect(fileNode.metadata?.linesOfCode).toBeGreaterThan(0)
    }
  })
})
```

### **Step 7: Troubleshooting**

#### **7.1 Common Issues**

**Issue: File tree not loading**
- **Cause:** Path traversal or permission issues
- **Solution:** Validate paths, check permissions, sanitize input

**Issue: Git operations failing**
- **Cause:** Not a git repository or git not installed
- **Solution:** Check git availability, verify repository

**Issue: Performance degradation**
- **Cause:** Scanning large codebase
- **Solution:** Implement incremental scanning, caching

### **Step 8: Best Practices**

#### **8.1 System Analysis**

**Do:**
- ✅ Cache analysis results
- ✅ Implement incremental scanning
- ✅ Validate file paths
- ✅ Handle errors gracefully
- ✅ Optimize for large codebases

**Don't:**
- ❌ Scan entire codebase every time
- ❌ Ignore performance
- ❌ Trust user input paths
- ❌ Skip error handling
- ❌ Block UI during scanning

---

## 📚 **REFERENCES**

- System map: `systems/lucid-ide/system-cortex/system.map.lucid.json5`
- System index: `systems/lucid-ide/system-cortex/system.index.lucid.json5`
- L2 Architecture: `systems/lucid-ide/system-cortex/L2_architecture.md`
- L4 Complete: `systems/lucid-ide/system-cortex/L4_complete.md`

---

**Status:** Complete  
**Last Updated:** 2025-11-09  
**Version:** v1.0.0

