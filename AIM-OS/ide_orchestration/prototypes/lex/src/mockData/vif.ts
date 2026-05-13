// Mock Data - VIF
import { VIFWitness, VIFConfidence } from '@/types'

export const mockVIFWitnesses: VIFWitness[] = [
  {
    id: 'witness_789',
    task: 'File IDELayout.tsx implementation',
    confidence: 0.85,
    evidence: ['atom_123', 'atom_456'],
    timestamp: '2025-11-07T10:05:00Z',
  },
  {
    id: 'witness_012',
    task: 'Context Web visualization',
    confidence: 0.90,
    evidence: ['atom_789', 'atom_321'],
    timestamp: '2025-11-07T10:15:00Z',
  },
  {
    id: 'witness_345',
    task: 'SEG contradiction detection',
    confidence: 0.88,
    evidence: ['atom_654'],
    timestamp: '2025-11-07T10:25:00Z',
  },
]

export const mockVIFConfidences: VIFConfidence[] = [
  {
    task: 'IDE Layout Prototype Design',
    confidence: 0.90,
    evidence: ['atom_123', 'atom_456', 'atom_789'],
    reasoning: 'Strong evidence from past implementations and AIM-OS integration patterns',
  },
  {
    task: 'Context Web Implementation',
    confidence: 0.85,
    evidence: ['atom_789', 'atom_321'],
    reasoning: 'Good evidence from CMC and HHNI integration patterns',
  },
  {
    task: 'VIF Confidence Indicators',
    confidence: 0.92,
    evidence: ['atom_321', 'atom_654'],
    reasoning: 'Very strong evidence from VIF system integration',
  },
]

