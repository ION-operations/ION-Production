// Mock Data - CMC
import { CMCAtom, CMCStats } from '@/types'

export const mockCMCStats: CMCStats = {
  totalAtoms: 165,
  activeSessions: 1,
  storage: 'SQLite',
}

export const mockCMCAtoms: CMCAtom[] = [
  {
    id: 'atom_123',
    content: 'File IDELayout.tsx uses react-resizable-panels for multi-panel layout',
    timestamp: '2025-11-07T10:00:00Z',
    tags: ['ide', 'layout', 'react'],
    confidence: 0.95,
  },
  {
    id: 'atom_456',
    content: 'Monaco Editor integrated with AIM-OS systems for code completion',
    timestamp: '2025-11-07T10:05:00Z',
    tags: ['ide', 'editor', 'monaco'],
    confidence: 0.90,
  },
  {
    id: 'atom_789',
    content: 'Context Web visualization shows CMC atoms and HHNI retrieval paths',
    timestamp: '2025-11-07T10:10:00Z',
    tags: ['ide', 'visualization', 'cmc', 'hhni'],
    confidence: 0.85,
  },
  {
    id: 'atom_321',
    content: 'VIF confidence indicators displayed on all AI interactions',
    timestamp: '2025-11-07T10:15:00Z',
    tags: ['ide', 'vif', 'confidence'],
    confidence: 0.88,
  },
  {
    id: 'atom_654',
    content: 'SEG contradiction detection alerts shown inline in code editor',
    timestamp: '2025-11-07T10:20:00Z',
    tags: ['ide', 'seg', 'contradiction'],
    confidence: 0.92,
  },
  {
    id: 'atom_987',
    content: 'Evolution Explorer provides bidirectional Timeline ↔ Chain visualization',
    timestamp: '2025-11-07T10:25:00Z',
    tags: ['ide', 'visualization', 'timeline', 'chain'],
    confidence: 0.87,
  },
  {
    id: 'atom_111',
    content: 'File Explorer displays CMC atom metadata and VIF witnesses',
    timestamp: '2025-11-07T10:30:00Z',
    tags: ['ide', 'file-explorer', 'cmc', 'vif'],
    confidence: 0.91,
  },
  {
    id: 'atom_222',
    content: 'Memory Browser integrates CMC and HHNI for semantic search',
    timestamp: '2025-11-07T10:35:00Z',
    tags: ['ide', 'memory', 'cmc', 'hhni'],
    confidence: 0.89,
  },
  {
    id: 'atom_333',
    content: 'System Monitor shows VIF confidence metrics and SCOR system health',
    timestamp: '2025-11-07T10:40:00Z',
    tags: ['ide', 'monitor', 'vif', 'scor'],
    confidence: 0.93,
  },
  {
    id: 'atom_444',
    content: 'Agent Management panel displays APOE plans and agent coordination',
    timestamp: '2025-11-07T10:45:00Z',
    tags: ['ide', 'agents', 'apoe'],
    confidence: 0.86,
  },
]

