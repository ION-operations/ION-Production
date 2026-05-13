// Mock Data - SEG
import { SEGContradiction } from '@/types'

export const mockSEGContradictions: SEGContradiction[] = [
  {
    id: 'contradiction_001',
    type: 'conflict',
    source: 'IDELayout.tsx line 45',
    target: 'IDELayout.tsx line 120',
    severity: 'medium',
    message: 'Panel configuration conflicts with layout state',
  },
  {
    id: 'contradiction_002',
    type: 'inconsistency',
    source: 'MonacoEditor.tsx',
    target: 'CodeEditor.tsx',
    severity: 'low',
    message: 'Editor options differ between components',
  },
  {
    id: 'contradiction_003',
    type: 'error',
    source: 'FileExplorer.tsx',
    target: 'FileTree.tsx',
    severity: 'high',
    message: 'File tree structure mismatch detected',
  },
]

