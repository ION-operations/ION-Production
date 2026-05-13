// Mock Data - Agents
import { Agent } from '@/types'

export const mockAgents: Agent[] = [
  {
    id: 'agent_lex',
    name: 'Lex',
    status: 'active',
    currentTask: 'IDE Layout Prototype Implementation',
    capabilities: ['research', 'analysis', 'documentation', 'implementation'],
    confidence: 0.90,
  },
  {
    id: 'agent_aether',
    name: 'Aether',
    status: 'active',
    currentTask: 'System Architecture Review',
    capabilities: ['architecture', 'strategy', 'integration'],
    confidence: 0.95,
  },
  {
    id: 'agent_rev',
    name: 'Rev',
    status: 'active',
    currentTask: 'Research Coordination',
    capabilities: ['coordination', 'research', 'synthesis'],
    confidence: 0.88,
  },
  {
    id: 'agent_sam',
    name: 'Sam',
    status: 'idle',
    currentTask: 'UI Patterns Research',
    capabilities: ['ui', 'design', 'patterns'],
    confidence: 0.85,
  },
  {
    id: 'agent_max',
    name: 'Max',
    status: 'idle',
    currentTask: 'Panel Functionality Design',
    capabilities: ['ui', 'functionality', 'interaction'],
    confidence: 0.87,
  },
]

