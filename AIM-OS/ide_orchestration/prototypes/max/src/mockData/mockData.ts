// File Tree Mock Data
export interface FileNode {
  name: string;
  type: 'file' | 'directory';
  path: string;
  size?: number;
  modified?: string;
  gitStatus?: 'M' | 'A' | 'D' | 'U' | '?' | null;
  children?: Record<string, FileNode>;
}

export const mockFileTree: Record<string, FileNode> = {
  'src/': {
    name: 'src',
    type: 'directory',
    path: 'src/',
    children: {
      'components/': {
        name: 'components',
        type: 'directory',
        path: 'src/components/',
        children: {
          'Button.tsx': {
            name: 'Button.tsx',
            type: 'file',
            path: 'src/components/Button.tsx',
            size: 1234,
            modified: '2025-11-07T10:00:00Z',
            gitStatus: 'M',
          },
          'Input.tsx': {
            name: 'Input.tsx',
            type: 'file',
            path: 'src/components/Input.tsx',
            size: 2345,
            modified: '2025-11-07T09:30:00Z',
            gitStatus: 'A',
          },
          'Card.tsx': {
            name: 'Card.tsx',
            type: 'file',
            path: 'src/components/Card.tsx',
            size: 3456,
            modified: '2025-11-06T15:20:00Z',
            gitStatus: null,
          },
        },
      },
      'utils/': {
        name: 'utils',
        type: 'directory',
        path: 'src/utils/',
        children: {
          'helpers.ts': {
            name: 'helpers.ts',
            type: 'file',
            path: 'src/utils/helpers.ts',
            size: 5678,
            modified: '2025-11-05T14:10:00Z',
            gitStatus: null,
          },
        },
      },
    },
  },
  'package.json': {
    name: 'package.json',
    type: 'file',
    path: 'package.json',
    size: 1234,
    modified: '2025-11-07T08:00:00Z',
    gitStatus: 'M',
  },
};

// Terminal Mock Data
export interface Terminal {
  id: string;
  name: string;
  output: string[];
  cwd: string;
  commandHistory: string[];
}

export const mockTerminals: Terminal[] = [
  {
    id: '1',
    name: 'Terminal 1',
    output: [
      '$ npm install',
      'Installing packages...',
      'added 1234 packages in 45s',
      '',
      '$ npm run dev',
      'VITE v5.0.8  ready in 234 ms',
      '',
      '➜  Local:   http://localhost:3002/',
    ],
    cwd: '/project',
    commandHistory: ['npm install', 'npm run dev', 'git status'],
  },
  {
    id: '2',
    name: 'Terminal 2',
    output: [
      '$ git status',
      'On branch main',
      'Changes not staged for commit:',
      '  modified:   src/components/Button.tsx',
    ],
    cwd: '/project',
    commandHistory: ['git status'],
  },
];

// Problems Mock Data
export interface Problem {
  id: string;
  file: string;
  line: number;
  column: number;
  severity: 'error' | 'warning' | 'info';
  message: string;
  code?: string;
}

export const mockProblems: Problem[] = [
  {
    id: '1',
    file: 'src/components/Button.tsx',
    line: 12,
    column: 15,
    severity: 'error',
    message: "Type error: 'variant' is possibly 'undefined'",
    code: "className={`btn btn-${variant}`}",
  },
  {
    id: '2',
    file: 'src/components/Button.tsx',
    line: 8,
    column: 10,
    severity: 'warning',
    message: "Unused variable 'disabled'",
    code: 'disabled = false,',
  },
];

// Chat Mock Data
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  codeBlocks?: string[];
}

export const mockChatMessages: ChatMessage[] = [
  {
    id: '1',
    role: 'user',
    content: 'How do I create a button component in React?',
    timestamp: '2025-11-07T10:00:00Z',
  },
  {
    id: '2',
    role: 'assistant',
    content: 'Here\'s how to create a button component:\n\n```typescript\nexport const Button = ({ label, onClick }) => {\n  return <button onClick={onClick}>{label}</button>;\n};\n```',
    timestamp: '2025-11-07T10:00:05Z',
    codeBlocks: [
      "export const Button = ({ label, onClick }) => {\n  return <button onClick={onClick}>{label}</button>;\n};",
    ],
  },
];

// Debug Console Mock Data
export interface DebugLogEntry {
  id: string;
  level: 'log' | 'info' | 'warn' | 'error' | 'debug';
  source: string;
  message: string;
  timestamp: string;
  confidence: number;
  evidence: string[];
  context?: Record<string, any>;
  bitemporal?: {
    valid_from: string;
    valid_to: string | null;
  };
}

export const mockDebugLogs: DebugLogEntry[] = [
  {
    id: 'debug_1',
    level: 'log',
    source: 'IDELayout',
    message: 'Component mounted successfully',
    timestamp: new Date().toISOString(),
    confidence: 0.95,
    evidence: ['atom_123'],
    context: { component: 'Layout', props: {} },
    bitemporal: { valid_from: new Date().toISOString(), valid_to: null },
  },
  {
    id: 'debug_2',
    level: 'info',
    source: 'CMC',
    message: 'Atom created: file_operation',
    timestamp: new Date(Date.now() - 5000).toISOString(),
    confidence: 0.98,
    evidence: ['atom_124'],
    context: { atom_id: 'atom_124', operation: 'file_read', file: 'Layout.tsx' },
    bitemporal: { valid_from: new Date(Date.now() - 5000).toISOString(), valid_to: null },
  },
  {
    id: 'debug_3',
    level: 'warn',
    source: 'VIF',
    message: 'Confidence below threshold: 0.65',
    timestamp: new Date(Date.now() - 10000).toISOString(),
    confidence: 0.65,
    evidence: ['atom_125'],
    context: { threshold: 0.70, system: 'HHNI', operation: 'semantic_search' },
    bitemporal: { valid_from: new Date(Date.now() - 10000).toISOString(), valid_to: null },
  },
  {
    id: 'debug_4',
    level: 'error',
    source: 'APOE',
    message: 'Task dependency resolution failed',
    timestamp: new Date(Date.now() - 15000).toISOString(),
    confidence: 0.88,
    evidence: ['atom_126'],
    context: { task_id: 'task_42', dependency: 'task_41', reason: 'circular_dependency' },
    bitemporal: { valid_from: new Date(Date.now() - 15000).toISOString(), valid_to: null },
  },
  {
    id: 'debug_5',
    level: 'info',
    source: 'HHNI',
    message: 'Semantic search executed',
    timestamp: new Date(Date.now() - 20000).toISOString(),
    confidence: 0.92,
    evidence: ['atom_127'],
    context: { query: 'debug console', results: 5 },
    bitemporal: { valid_from: new Date(Date.now() - 20000).toISOString(), valid_to: null },
  },
  {
    id: 'debug_6',
    level: 'log',
    source: 'SEG',
    message: 'Evidence node created',
    timestamp: new Date(Date.now() - 25000).toISOString(),
    confidence: 0.93,
    evidence: ['atom_128'],
    context: { entity_id: 'entity_1', relation_type: 'SUPPORTS' },
    bitemporal: { valid_from: new Date(Date.now() - 25000).toISOString(), valid_to: null },
  },
];

