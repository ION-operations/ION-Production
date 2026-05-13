// Mock Data - File Tree
export interface FileNode {
  name: string
  type: 'file' | 'directory'
  path: string
  size?: number
  modified?: string
  cmcAtoms?: string[]
  witnesses?: string[]
  contradictions?: string[]
  children?: FileNode[]
}

export const mockFileTree: FileNode = {
  name: 'src',
  type: 'directory',
  path: 'src',
  children: [
    {
      name: 'components',
      type: 'directory',
      path: 'src/components',
      children: [
        {
          name: 'IDELayout.tsx',
          type: 'file',
          path: 'src/components/IDELayout.tsx',
          size: 1234,
          modified: '2025-11-07T10:00:00Z',
          cmcAtoms: ['atom_123', 'atom_456'],
          witnesses: ['witness_789'],
          contradictions: [],
        },
        {
          name: 'MonacoEditor.tsx',
          type: 'file',
          path: 'src/components/MonacoEditor.tsx',
          size: 2345,
          modified: '2025-11-07T10:05:00Z',
          cmcAtoms: ['atom_321'],
          witnesses: [],
          contradictions: ['contradiction_002'],
        },
        {
          name: 'FileExplorer.tsx',
          type: 'file',
          path: 'src/components/FileExplorer.tsx',
          size: 3456,
          modified: '2025-11-07T10:10:00Z',
          cmcAtoms: ['atom_111'],
          witnesses: [],
          contradictions: ['contradiction_003'],
        },
      ],
    },
    {
      name: 'hooks',
      type: 'directory',
      path: 'src/hooks',
      children: [
        {
          name: 'useCMC.ts',
          type: 'file',
          path: 'src/hooks/useCMC.ts',
          size: 567,
          modified: '2025-11-07T10:15:00Z',
          cmcAtoms: ['atom_222'],
          witnesses: [],
          contradictions: [],
        },
        {
          name: 'useHHNI.ts',
          type: 'file',
          path: 'src/hooks/useHHNI.ts',
          size: 678,
          modified: '2025-11-07T10:20:00Z',
          cmcAtoms: ['atom_333'],
          witnesses: [],
          contradictions: [],
        },
      ],
    },
    {
      name: 'mockData',
      type: 'directory',
      path: 'src/mockData',
      children: [
        {
          name: 'cmc.ts',
          type: 'file',
          path: 'src/mockData/cmc.ts',
          size: 890,
          modified: '2025-11-07T10:25:00Z',
          cmcAtoms: [],
          witnesses: [],
          contradictions: [],
        },
      ],
    },
  ],
}

