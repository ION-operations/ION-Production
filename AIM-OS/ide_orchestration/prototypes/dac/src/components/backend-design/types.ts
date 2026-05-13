// Backend Design System - Type Definitions
// Comprehensive types for the visual backend builder

import { Node, Edge } from 'reactflow'

// Template Categories
export type TemplateCategory = 
  | 'architecture' 
  | 'auth' 
  | 'database' 
  | 'api' 
  | 'realtime' 
  | 'jobs' 
  | 'storage' 
  | 'deploy' 
  | 'monitor'
  | 'security'
  | 'testing'
  | 'integration'

export type TemplateStatus = 'configured' | 'incomplete' | 'error' | 'running' | 'success'

// Template Node Data
export interface TemplateNodeData {
  id: string
  type: TemplateCategory
  name: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  status: TemplateStatus
  config: Record<string, any>
  inputs: PortDefinition[]
  outputs: PortDefinition[]
  executionTime?: number
  lastRun?: Date
  version: string
  author: string
  tags: string[]
}

// Port Definition for node connections
export interface PortDefinition {
  id: string
  name: string
  type: 'data' | 'trigger' | 'config' | 'error'
  dataType?: string // e.g., 'User', 'string', 'number', 'any'
  required?: boolean
  description?: string
}

// Template Definition
export interface Template {
  id: string
  type: TemplateCategory
  name: string
  description: string
  longDescription?: string
  icon: React.ComponentType<{ className?: string }>
  defaultConfig: Record<string, ConfigField>
  configSchema: ConfigSchema
  inputs: PortDefinition[]
  outputs: PortDefinition[]
  lines: number
  coverage: number
  dependencies: string[]
  version: string
  author: string
  tags: string[]
  preview?: string // Code preview snippet
  documentation?: string
  examples?: TemplateExample[]
}

// Config Field Definition
export interface ConfigField {
  value: any
  type: 'string' | 'number' | 'boolean' | 'select' | 'multiselect' | 'code' | 'json' | 'password' | 'url' | 'email'
  label: string
  description?: string
  placeholder?: string
  required?: boolean
  validation?: string // Regex pattern
  options?: { value: string; label: string }[] // For select/multiselect
  min?: number
  max?: number
  default?: any
  group?: string // For grouping in UI
  advanced?: boolean // Show in advanced section
  dependsOn?: { field: string; value: any } // Conditional visibility
}

export interface ConfigSchema {
  groups: ConfigGroup[]
}

export interface ConfigGroup {
  id: string
  name: string
  description?: string
  collapsed?: boolean
  fields: string[]
}

// Template Example
export interface TemplateExample {
  title: string
  description: string
  config: Record<string, any>
  code?: string
}

// Category Configuration
export interface CategoryConfig {
  id: TemplateCategory
  name: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  color: string
  bgColor: string
  borderColor: string
  accentColor: string
  count?: number
}

// Workflow Definition (for save/load)
export interface Workflow {
  id: string
  name: string
  description?: string
  nodes: Node<TemplateNodeData>[]
  edges: Edge[]
  settings: WorkflowSettings
  metadata: WorkflowMetadata
  createdAt: Date
  updatedAt: Date
  version: number
}

export interface WorkflowSettings {
  autoLayout: boolean
  snapToGrid: boolean
  gridSize: number
  showMinimap: boolean
  showControls: boolean
  theme: 'dark' | 'light'
  language: 'typescript' | 'python' | 'go' | 'rust' | 'java'
  framework: 'express' | 'fastify' | 'nestjs' | 'django' | 'fastapi' | 'gin' | 'actix' | 'spring'
}

export interface WorkflowMetadata {
  author: string
  tags: string[]
  estimatedLines: number
  estimatedFiles: number
  testCoverage: number
  complexity: 'low' | 'medium' | 'high'
}

// Generated Code Output
export interface GeneratedCode {
  files: GeneratedFile[]
  structure: FileTreeNode[]
  stats: GenerationStats
  warnings: string[]
  errors: string[]
}

export interface GeneratedFile {
  path: string
  content: string
  language: string
  template: string
  description?: string
}

export interface FileTreeNode {
  name: string
  type: 'file' | 'directory'
  path: string
  children?: FileTreeNode[]
  language?: string
  lines?: number
}

export interface GenerationStats {
  totalFiles: number
  totalLines: number
  languages: { [key: string]: number }
  templates: string[]
  duration: number
  testFiles: number
  testCoverage: number
}

// Deployment Configuration
export interface DeploymentConfig {
  target: 'docker' | 'kubernetes' | 'vercel' | 'railway' | 'fly' | 'aws' | 'gcp' | 'azure'
  environment: 'development' | 'staging' | 'production'
  settings: Record<string, any>
}

// Execution State (for workflow testing)
export interface ExecutionState {
  status: 'idle' | 'running' | 'paused' | 'completed' | 'failed'
  currentNodeId?: string
  executedNodes: string[]
  failedNodes: string[]
  logs: ExecutionLog[]
  startTime?: Date
  endTime?: Date
  duration?: number
}

export interface ExecutionLog {
  timestamp: Date
  nodeId: string
  nodeName: string
  level: 'info' | 'warn' | 'error' | 'debug'
  message: string
  data?: any
}

// Collaboration (for real-time features)
export interface Collaborator {
  id: string
  name: string
  avatar?: string
  color: string
  cursor?: { x: number; y: number }
  selectedNodes: string[]
}

// Undo/Redo History
export interface HistoryState {
  past: WorkflowSnapshot[]
  present: WorkflowSnapshot
  future: WorkflowSnapshot[]
}

export interface WorkflowSnapshot {
  nodes: Node<TemplateNodeData>[]
  edges: Edge[]
  timestamp: Date
  action: string
}

