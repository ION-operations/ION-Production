// Mock Data - Timeline (TCS)
import { TimelineEntry } from '@/types'

export const mockTimelineEntries: TimelineEntry[] = [
  {
    id: 'entry_001',
    prompt_id: 'prompt_123',
    user_input: 'Create IDE layout prototype',
    context_state: {
      task: 'IDE Layout Prototype Design',
      status: 'in_progress',
    },
    timestamp: '2025-11-07T10:00:00Z',
  },
  {
    id: 'entry_002',
    prompt_id: 'prompt_124',
    user_input: 'Design Context Web visualization',
    context_state: {
      task: 'Context Web Design',
      status: 'completed',
    },
    timestamp: '2025-11-07T10:15:00Z',
  },
  {
    id: 'entry_003',
    prompt_id: 'prompt_125',
    user_input: 'Implement VIF confidence indicators',
    context_state: {
      task: 'VIF Integration',
      status: 'in_progress',
    },
    timestamp: '2025-11-07T10:30:00Z',
  },
  {
    id: 'entry_004',
    prompt_id: 'prompt_126',
    user_input: 'Add SEG contradiction detection',
    context_state: {
      task: 'SEG Integration',
      status: 'planned',
    },
    timestamp: '2025-11-07T10:45:00Z',
  },
  {
    id: 'entry_005',
    prompt_id: 'prompt_127',
    user_input: 'Build Evolution Explorer',
    context_state: {
      task: 'Evolution Explorer',
      status: 'in_progress',
    },
    timestamp: '2025-11-07T11:00:00Z',
  },
]

