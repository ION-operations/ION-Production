// AI Chat & Management Panel - Discord-style Channel System
// Organized by channels (tasks/goals/sections) and sub-channels (researching/documenting/building/debugging)

import React, { useState, useEffect, useRef, useMemo } from 'react'
import { 
  MessageSquare, Send, Bot, User, Settings, 
  Plus, MoreVertical, CheckCircle, Clock, AlertCircle,
  Hash, Lock, ChevronDown, ChevronRight, File, GitBranch,
  Target, Database, Shield, ExternalLink, Code, TrendingUp,
  Zap, Link2, X, ChevronRight as ChevronRightIcon, ChevronUp, ChevronDown as ChevronDownIcon
} from 'lucide-react'
import { useSummaryAtomsWithRAG } from '../hooks/useSummaryAtomsWithRAG'
import { MessageContextBadge } from '../components/MessageContextBadge'
import { assemble, updateContextInfo, type Need } from '../utils/assemble'
import { hybridRetrieve, HybridRetrievalResult } from '../utils/hybridRetrieval'
import { AIChatContextProvider } from '../contexts/AIChatContext'
import { ChatMessage, WorkReference, ToolCall, PingContext, EvidenceTrail, GoalAlignment } from '../types/chatTypes'

interface Channel {
  id: string
  name: string
  type: 'channel' | 'section'
  parentId?: string
  description?: string
  unreadCount?: number
  isLocked?: boolean
}

interface Agent {
  id: string
  name: string
  status: 'active' | 'idle' | 'busy'
  currentTask?: string
  confidence?: number
  currentChannel?: string
  capabilities?: string[]
  strengths?: string[]
  performance?: {
    tasks_completed: number
    success_rate: number
    average_confidence: number
  }
  recent_files?: string[]
  recent_goals?: string[]
}

const CHANNELS: Channel[] = [
  // Main Channels
  { id: 'ui', name: 'UI', type: 'channel', description: 'User interface development' },
  { id: 'backend', name: 'Backend', type: 'channel', description: 'Backend API and services' },
  { id: 'frontend', name: 'Frontend', type: 'channel', description: 'Frontend components and views' },
  { id: 'infrastructure', name: 'Infrastructure', type: 'channel', description: 'DevOps and infrastructure' },
  
  // UI Sections
  { id: 'ui-research', name: 'researching', type: 'section', parentId: 'ui' },
  { id: 'ui-documenting', name: 'documenting', type: 'section', parentId: 'ui' },
  { id: 'ui-building', name: 'building', type: 'section', parentId: 'ui' },
  { id: 'ui-debugging', name: 'debugging', type: 'section', parentId: 'ui' },
  
  // Backend Sections
  { id: 'backend-research', name: 'researching', type: 'section', parentId: 'backend' },
  { id: 'backend-documenting', name: 'documenting', type: 'section', parentId: 'backend' },
  { id: 'backend-building', name: 'building', type: 'section', parentId: 'backend' },
  { id: 'backend-debugging', name: 'debugging', type: 'section', parentId: 'backend' },
]

export const AIChatManagement: React.FC = () => {
  const [messages, setMessages] = useState<Record<string, ChatMessage[]>>({})
  const [input, setInput] = useState('')
  const [selectedChannel, setSelectedChannel] = useState<string>('ui-building')
  const [expandedChannels, setExpandedChannels] = useState<Set<string>>(new Set(['ui', 'backend']))
  const [connectedChannels, setConnectedChannels] = useState<Set<string>>(new Set())  // Channels connected to current channel
  const [showPingMenu, setShowPingMenu] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [expandedMessages, setExpandedMessages] = useState<Set<string>>(new Set())  // Message IDs that are expanded
  const [selectedChannels, setSelectedChannels] = useState<Set<string>>(new Set(['ui-building']))  // Multi-select channels (shift-click)
  const [agents, setAgents] = useState<Agent[]>([
    { 
      id: 'aether', 
      name: 'Aether', 
      status: 'active', 
      currentTask: 'Building IDE prototype', 
      confidence: 0.92, 
      currentChannel: 'ui-building',
      capabilities: ['coding', 'planning', 'execution', 'architecture'],
      strengths: ['System design', 'Problem solving', 'Quality assurance'],
      performance: {
        tasks_completed: 247,
        success_rate: 0.94,
        average_confidence: 0.91
      },
      recent_files: [
        'ide_orchestration/prototypes/dac/src/components/IDELayout.tsx',
        'ide_orchestration/prototypes/dac/src/panels/AIChatManagement.tsx'
      ],
      recent_goals: ['OBJ-07', 'OBJ-08']
    },
    { 
      id: 'dac', 
      name: 'Dac', 
      status: 'active', 
      currentTask: 'Enhancing panels', 
      confidence: 0.88, 
      currentChannel: 'ui-building',
      capabilities: ['UI development', 'React', 'TypeScript', 'Panel systems'],
      strengths: ['Component design', 'User experience', 'Responsive layouts'],
      performance: {
        tasks_completed: 189,
        success_rate: 0.91,
        average_confidence: 0.87
      },
      recent_files: [
        'ide_orchestration/prototypes/dac/src/panels/DebugConsolePanel.tsx',
        'ide_orchestration/prototypes/dac/src/panels/FileTree.tsx'
      ],
      recent_goals: ['OBJ-07']
    },
    { 
      id: 'codex', 
      name: 'Codex', 
      status: 'idle', 
      confidence: 0.85,
      capabilities: ['Research', 'Documentation', 'Analysis'],
      strengths: ['Technical research', 'Best practices', 'Library evaluation'],
      performance: {
        tasks_completed: 156,
        success_rate: 0.89,
        average_confidence: 0.85
      }
    },
  ])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  // Initialize summary atoms and significance scoring with RAG support
  const [ragEnabled, setRagEnabled] = useState(false)
  const {
    summaryAtoms,
    contextInfo,
    overrides,
    ragIndexed: isRagIndexed,
    getSummaryAtom,
    getContextInfo,
    getOverride,
    togglePin,
    setPriority,
    setForcedLevel,
    handleMessageView
  } = useSummaryAtomsWithRAG(messages, { ragEnabled, autoIndex: true })
  
  // Get messages including connected channels and multi-selected channels (memoized)
  const displayMessages = useMemo(() => {
    // Get all channels to include (selected + connected + multi-selected)
    const channelsToInclude = new Set<string>([selectedChannel])
    
    // Add connected channels
    connectedChannels.forEach(ch => channelsToInclude.add(ch))
    
    // Add multi-selected channels (shift-click)
    selectedChannels.forEach(ch => channelsToInclude.add(ch))
    
    // Collect messages from all channels
    const allMessages: ChatMessage[] = []
    
    channelsToInclude.forEach(channelId => {
      const channelMessages = messages[channelId] || []
      const isMainChannel = channelId === selectedChannel
      const isMultiSelected = selectedChannels.has(channelId) && channelId !== selectedChannel
      
      channelMessages.forEach(msg => {
        allMessages.push({
          ...msg,
          connected_channel: isMainChannel ? undefined : (msg.connected_channel || channelId),
          multi_selected_channel: isMultiSelected ? channelId : undefined
        })
      })
    })

    // Sort by timestamp
    return allMessages.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
  }, [messages, selectedChannel, connectedChannels, selectedChannels])
  
  // Perform retrieval for current channel (optional - can be toggled)
  const [useRetrieval, setUseRetrieval] = useState(false)
  const [retrievalBudget] = useState(12000) // 12k token budget
  const [hybridResult, setHybridResult] = useState<HybridRetrievalResult | null>(null)
  
  // Assemble context when retrieval is enabled (with RAG support)
  useEffect(() => {
    if (!useRetrieval || !summaryAtoms[selectedChannel]) {
      setHybridResult(null)
      return
    }
    
    const needs: Need[] = [
      { kind: 'decision', objects: [] },
      { kind: 'fact', objects: [] },
      { kind: 'task', objects: [] }
    ]
    
    const query = displayMessages.slice(-10).map(m => m.content).join(' ') // Last 10 messages for context
    
    // Use hybrid retrieval if RAG is enabled, otherwise use atom-only
    if (ragEnabled && isRagIndexed) {
      hybridRetrieve(
        query,
        messages,
        summaryAtoms,
        overrides,
        needs,
        retrievalBudget,
        {
          ragEnabled: true,
          ragWeight: 0.6,
          atomWeight: 0.4,
          crossChannel: selectedChannels.size > 1,
          channelIds: Array.from(selectedChannels),
          limit: 30
        }
      ).then(result => {
        setHybridResult(result)
      }).catch(err => {
        console.error('Hybrid retrieval failed:', err)
        // Fallback to atom-only
        const availableAtoms = summaryAtoms[selectedChannel] || []
        const atomResult = assemble(query, needs, retrievalBudget, availableAtoms, overrides, 'default')
        setHybridResult({
          ragResults: [],
          atomResults: atomResult,
          combined: atomResult.atoms.map(atom => ({
            atom,
            score: atom.sig.score,
            source: 'atom' as const,
            reasons: atomResult.reasons[atom.id] || ['significance']
          })),
          totalTokens: atomResult.totalTokens,
          ragTokens: 0,
          atomTokens: atomResult.totalTokens
        })
      })
    } else {
      // Atom-only retrieval (existing behavior)
      const availableAtoms = summaryAtoms[selectedChannel] || []
      const atomResult = assemble(query, needs, retrievalBudget, availableAtoms, overrides, 'default')
      setHybridResult({
        ragResults: [],
        atomResults: atomResult,
        combined: atomResult.atoms.map(atom => ({
          atom,
          score: atom.sig.score,
          source: 'atom' as const,
          reasons: atomResult.reasons[atom.id] || ['significance']
        })),
        totalTokens: atomResult.totalTokens,
        ragTokens: 0,
        atomTokens: atomResult.totalTokens
      })
    }
  }, [useRetrieval, ragEnabled, isRagIndexed, selectedChannel, summaryAtoms, displayMessages, retrievalBudget, overrides, messages, selectedChannels])
  
  // Convert hybrid result to assembled context format for compatibility
  const assembledContext = useMemo(() => {
    if (!hybridResult) return null
    
    return {
      atoms: hybridResult.combined
        .filter(r => r.atom)
        .map(r => r.atom!)
        .slice(0, 50), // Limit to top 50
      totalTokens: hybridResult.totalTokens,
      usedByAgent: { default: hybridResult.totalTokens },
      reasons: Object.fromEntries(
        hybridResult.combined.map(r => [
          r.message?.id || r.atom?.id || '',
          r.reasons
        ]).filter(([id]) => id)
      )
    }
  }, [hybridResult])
  
  // Calculate pack total for badges
  const packTotal = assembledContext?.totalTokens ?? 0
  
  // Track message views when displayed
  useEffect(() => {
    displayMessages.forEach(msg => {
      handleMessageView(msg.id)
    })
  }, [displayMessages, handleMessageView])
  
  // Initialize messages with realistic mock data
  useEffect(() => {
    const now = Date.now()
    const mockMessages: Record<string, ChatMessage[]> = {
      'ui-building': [
        {
          id: 'msg_1',
          timestamp: new Date(now - 3600000),
          role: 'assistant',
          content: 'Starting implementation of the drag-and-drop toolbar system. Using react-dnd for cross-zone dragging.',
          agent: 'aether',
          agent_id: 'aether_001',
          confidence: 0.91,
          tool_calls: [
            {
              id: 'tool_1',
              tool_name: 'mcp_lucid-mcp_store_memory',
              arguments: {
                content: 'Starting drag-and-drop toolbar implementation',
                tags: { type: 'task_start', system: 'ide', component: 'toolbar' }
              },
              result: { memory_id: 'mem_001', atom_id: 'atom_drag_drop_001' },
              status: 'success',
              duration_ms: 45,
              timestamp: new Date(now - 3600000)
            },
            {
              id: 'tool_2',
              tool_name: 'mcp_lucid-mcp_track_confidence',
              arguments: {
                task: 'Drag-and-drop toolbar implementation',
                confidence: 0.91
              },
              result: { tracked: true },
              status: 'success',
              duration_ms: 12,
              timestamp: new Date(now - 3600000)
            }
          ],
          work_references: {
            files: [{
              path: 'ide_orchestration/prototypes/dac/src/components/IDELayout.tsx',
              operation: 'modified',
              lines: [120, 145]
            }],
            goals: ['OBJ-07'],
            cmc_atoms: ['atom_drag_drop_001']
          },
          evidence_trail: {
            cmc_atom_id: 'atom_drag_drop_001',
            vif_witness_id: 'witness_001'
          },
          goal_alignment: {
            objective: 'OBJ-07',
            key_result: 'KR-07-01',
            progress: 0.45
          }
        },
        {
          id: 'msg_2',
          timestamp: new Date(now - 3300000),
          role: 'assistant',
          content: 'I can help with the panel responsiveness. The DebugConsolePanel needs flex-1 min-w-0 for proper sizing in different zones.',
          agent: 'dac',
          agent_id: 'dac_001',
          confidence: 0.87,
          work_references: {
            files: [{
              path: 'ide_orchestration/prototypes/dac/src/panels/DebugConsolePanel.tsx',
              operation: 'modified',
              lines: [45, 67]
            }]
          }
        },
        {
          id: 'msg_3',
          timestamp: new Date(now - 3000000),
          role: 'user',
          content: 'Can we make the toolbar buttons thinner? They should match the top/bottom bar thickness.'
        },
        {
          id: 'msg_4',
          timestamp: new Date(now - 2700000),
          role: 'assistant',
          content: 'Changing toolbar width from w-12 to w-8 and button sizes from w-10 h-10 to w-8 h-8. Icon sizes reduced to w-3 h-3.',
          agent: 'aether',
          agent_id: 'aether_001',
          confidence: 0.93,
          work_references: {
            files: [{
              path: 'ide_orchestration/prototypes/dac/src/components/IDELayout.tsx',
              operation: 'modified',
              lines: [89, 112],
              commit_hash: 'abc123def'
            }]
          }
        },
        {
          id: 'msg_5',
          timestamp: new Date(now - 2400000),
          role: 'assistant',
          content: 'Applied changes. All toolbars now have consistent thickness. Testing drag-and-drop functionality...',
          agent: 'dac',
          agent_id: 'dac_001',
          confidence: 0.89
        },
        {
          id: 'msg_6',
          timestamp: new Date(now - 2100000),
          role: 'assistant',
          content: '✅ Drag-and-drop working perfectly across all zones. Cross-toolbar dragging implemented successfully.',
          agent: 'aether',
          agent_id: 'aether_001',
          confidence: 0.95,
          work_references: {
            files: [{
              path: 'ide_orchestration/prototypes/dac/src/components/IDELayout.tsx',
              operation: 'modified',
              lines: [200, 250]
            }],
            cmc_atoms: ['atom_drag_drop_002'],
            vif_witnesses: ['witness_002']
          },
          evidence_trail: {
            cmc_atom_id: 'atom_drag_drop_002',
            vif_witness_id: 'witness_002'
          }
        },
        {
          id: 'msg_7',
          timestamp: new Date(now - 1800000),
          role: 'user',
          content: 'The AI chat panel isn\'t working. Getting a lazy loading error.'
        },
        {
          id: 'msg_8',
          timestamp: new Date(now - 1500000),
          role: 'assistant',
          content: 'Investigating lazy loading issue. Checking export pattern in AIChatManagement.tsx...',
          agent: 'dac',
          agent_id: 'dac_001',
          confidence: 0.86,
          work_references: {
            files: [{
              path: 'ide_orchestration/prototypes/dac/src/panels/AIChatManagement.tsx',
              operation: 'modified',
              lines: [1, 50]
            }]
          }
        },
        {
          id: 'msg_9',
          timestamp: new Date(now - 1200000),
          role: 'assistant',
          content: 'Found the issue - missing default export. Adding default export and updating lazy loader to handle both named and default exports.',
          agent: 'aether',
          agent_id: 'aether_001',
          confidence: 0.92,
          work_references: {
            files: [
              {
                path: 'ide_orchestration/prototypes/dac/src/panels/AIChatManagement.tsx',
                operation: 'modified',
                lines: [355, 356]
              },
              {
                path: 'ide_orchestration/prototypes/dac/src/utils/performance.tsx',
                operation: 'modified',
                lines: [45, 47]
              }
            ],
            cmc_atoms: ['atom_chat_fix_001']
          },
          evidence_trail: {
            cmc_atom_id: 'atom_chat_fix_001',
            supporting_files: [{
              path: 'ide_orchestration/prototypes/dac/src/panels/AIChatManagement.tsx',
              lines: [1, 100],
              relevance: 0.95
            }]
          }
        },
        {
          id: 'msg_10',
          timestamp: new Date(now - 900000),
          role: 'assistant',
          content: 'Also found Hashtag icon import error. Replacing with Hash icon from lucide-react.',
          agent: 'dac',
          agent_id: 'dac_001',
          confidence: 0.88,
          work_references: {
            files: [{
              path: 'ide_orchestration/prototypes/dac/src/panels/AIChatManagement.tsx',
              operation: 'modified',
              lines: [8, 8]
            }]
          }
        },
        {
          id: 'msg_11',
          timestamp: new Date(now - 600000),
          role: 'assistant',
          content: '✅ AI chat panel fixed and loading correctly. Debug console also works in left/right panels now.',
          agent: 'aether',
          agent_id: 'aether_001',
          confidence: 0.94,
          work_references: {
            files: [
              {
                path: 'ide_orchestration/prototypes/dac/src/panels/AIChatManagement.tsx',
                operation: 'modified',
                lines: [1, 100]
              },
              {
                path: 'ide_orchestration/prototypes/dac/src/components/IDELayout.tsx',
                operation: 'modified',
                lines: [450, 500]
              }
            ],
            goals: ['OBJ-07'],
            cmc_atoms: ['atom_chat_fix_002'],
            vif_witnesses: ['witness_003']
          },
          evidence_trail: {
            cmc_atom_id: 'atom_chat_fix_002',
            vif_witness_id: 'witness_003'
          },
          goal_alignment: {
            objective: 'OBJ-07',
            key_result: 'KR-07-01',
            progress: 0.65
          }
        }
      ],
      'ui-research': [
        {
          id: 'msg_r1',
          timestamp: new Date(now - 7200000),
          role: 'assistant',
          content: 'Researching best practices for panel layout systems. Looking at VSCode, JetBrains IDEs, and modern web IDEs.',
          agent: 'codex',
          agent_id: 'codex_001',
          confidence: 0.85,
          work_references: {
            files: [{
              path: 'knowledge_architecture/systems/lucid-ide/backend-api-system/L3_detailed.md',
              operation: 'modified',
              lines: [120, 150]
            }],
            cmc_atoms: ['atom_research_panel_layout_001']
          },
          evidence_trail: {
            cmc_atom_id: 'atom_research_panel_layout_001',
            supporting_files: [{
              path: 'knowledge_architecture/systems/lucid-ide/backend-api-system/L3_detailed.md',
              lines: [120, 150],
              relevance: 0.85
            }]
          },
          goal_alignment: {
            objective: 'OBJ-07',
            key_result: 'KR-07-02',
            progress: 0.30
          }
        },
        {
          id: 'msg_r2',
          timestamp: new Date(now - 6900000),
          role: 'assistant',
          content: 'Found react-resizable-panels library - perfect for our use case. Supports nested panels and drag handles.',
          agent: 'aether',
          agent_id: 'aether_001',
          confidence: 0.90,
          work_references: {
            files: [{
              path: 'ide_orchestration/prototypes/dac/package.json',
              operation: 'modified',
              lines: [25, 30]
            }],
            cmc_atoms: ['atom_library_research_001'],
            vif_witnesses: ['witness_research_001']
          },
          evidence_trail: {
            cmc_atom_id: 'atom_library_research_001',
            vif_witness_id: 'witness_research_001'
          },
          goal_alignment: {
            objective: 'OBJ-07',
            key_result: 'KR-07-02',
            progress: 0.50
          }
        },
        {
          id: 'msg_r3',
          timestamp: new Date(now - 6600000),
          role: 'user',
          content: 'What about performance with many panels?'
        },
        {
          id: 'msg_r4',
          timestamp: new Date(now - 6300000),
          role: 'assistant',
          content: 'React-resizable-panels uses CSS transforms, so it\'s performant. We should lazy load panel components to avoid initial bundle bloat.',
          agent: 'codex',
          agent_id: 'codex_001',
          confidence: 0.87,
          work_references: {
            files: [{
              path: 'ide_orchestration/prototypes/dac/src/utils/performance.tsx',
              operation: 'modified',
              lines: [1, 50]
            }],
            cmc_atoms: ['atom_performance_research_001']
          },
          evidence_trail: {
            cmc_atom_id: 'atom_performance_research_001',
            supporting_files: [{
              path: 'ide_orchestration/prototypes/dac/src/utils/performance.tsx',
              lines: [1, 50],
              relevance: 0.90
            }]
          },
          goal_alignment: {
            objective: 'OBJ-07',
            key_result: 'KR-07-02',
            progress: 0.70
          }
        }
      ],
      'ui-documenting': [
        {
          id: 'msg_d1',
          timestamp: new Date(now - 5400000),
          role: 'assistant',
          content: 'Documenting the 5-zone layout system: left, right, top, bottom, and main content areas.',
          agent: 'dac',
          agent_id: 'dac_001',
          confidence: 0.89,
          work_references: {
            files: [{
              path: 'ide_orchestration/prototypes/dac/README.md',
              operation: 'modified',
              lines: [45, 80]
            }],
            goals: ['OBJ-06'],
            cmc_atoms: ['atom_doc_layout_001']
          },
          evidence_trail: {
            cmc_atom_id: 'atom_doc_layout_001',
            supporting_files: [{
              path: 'ide_orchestration/prototypes/dac/README.md',
              lines: [45, 80],
              relevance: 0.75
            }]
          },
          goal_alignment: {
            objective: 'OBJ-06',
            key_result: 'KR-06-01',
            progress: 0.60
          }
        },
        {
          id: 'msg_d2',
          timestamp: new Date(now - 5100000),
          role: 'assistant',
          content: 'Each zone supports split panels (top/bottom for left/right, left/right for bottom). Toolbars are always visible.',
          agent: 'aether',
          agent_id: 'aether_001',
          confidence: 0.91,
          work_references: {
            files: [{
              path: 'ide_orchestration/prototypes/dac/README.md',
              operation: 'modified',
              lines: [80, 120]
            }],
            cmc_atoms: ['atom_doc_panels_001'],
            vif_witnesses: ['witness_doc_001']
          },
          evidence_trail: {
            cmc_atom_id: 'atom_doc_panels_001',
            vif_witness_id: 'witness_doc_001'
          },
          goal_alignment: {
            objective: 'OBJ-06',
            key_result: 'KR-06-01',
            progress: 0.75
          }
        }
      ],
      'ui-debugging': [
        {
          id: 'msg_db1',
          timestamp: new Date(now - 1800000),
          role: 'assistant',
          content: 'Debugging panel auto-close logic. Panels should close when no panel is selected in that zone.',
          agent: 'dac',
          agent_id: 'dac_001',
          confidence: 0.88,
          work_references: {
            files: [{
              path: 'ide_orchestration/prototypes/dac/src/components/IDELayout.tsx',
              operation: 'modified',
              lines: [280, 320]
            }],
            cmc_atoms: ['atom_debug_autoclose_001']
          },
          evidence_trail: {
            cmc_atom_id: 'atom_debug_autoclose_001',
            supporting_files: [{
              path: 'ide_orchestration/prototypes/dac/src/components/IDELayout.tsx',
              lines: [280, 320],
              relevance: 0.88
            }]
          },
          goal_alignment: {
            objective: 'OBJ-07',
            key_result: 'KR-07-01',
            progress: 0.55
          }
        },
        {
          id: 'msg_db2',
          timestamp: new Date(now - 1500000),
          role: 'assistant',
          content: 'Added useEffect hooks to monitor panel state. Auto-closing works correctly now.',
          agent: 'aether',
          agent_id: 'aether_001',
          confidence: 0.92,
          work_references: {
            files: [{
              path: 'ide_orchestration/prototypes/dac/src/components/IDELayout.tsx',
              operation: 'modified',
              lines: [320, 360],
              commit_hash: 'def456ghi'
            }],
            cmc_atoms: ['atom_debug_autoclose_002'],
            vif_witnesses: ['witness_debug_001']
          },
          evidence_trail: {
            cmc_atom_id: 'atom_debug_autoclose_002',
            vif_witness_id: 'witness_debug_001'
          },
          goal_alignment: {
            objective: 'OBJ-07',
            key_result: 'KR-07-01',
            progress: 0.70
          }
        }
      ],
      'backend-building': [
        {
          id: 'msg_b1',
          timestamp: new Date(now - 10800000),
          role: 'assistant',
          content: 'Implementing MCP server integration. Setting up tool routing and RAG filtering.',
          agent: 'codex',
          agent_id: 'codex_001',
          confidence: 0.86,
          work_references: {
            files: [
              {
                path: 'packages/mcp_rag_proxy/mcp_rag_middleware.py',
                operation: 'modified',
                lines: [50, 100]
              },
              {
                path: 'lucid_mcp_server.py',
                operation: 'modified',
                lines: [200, 250]
              }
            ],
            goals: ['OBJ-08'],
            cmc_atoms: ['atom_mcp_integration_001']
          },
          evidence_trail: {
            cmc_atom_id: 'atom_mcp_integration_001',
            supporting_files: [
              {
                path: 'packages/mcp_rag_proxy/mcp_rag_middleware.py',
                lines: [1, 100],
                relevance: 0.92
              },
              {
                path: 'lucid_mcp_server.py',
                lines: [1, 50],
                relevance: 0.88
              }
            ]
          },
          goal_alignment: {
            objective: 'OBJ-08',
            key_result: 'KR-08-01',
            progress: 0.40
          }
        },
        {
          id: 'msg_b2',
          timestamp: new Date(now - 10500000),
          role: 'assistant',
          content: 'CMC integration complete. All tool executions are being stored as atoms with VIF witnesses.',
          agent: 'aether',
          agent_id: 'aether_001',
          confidence: 0.93,
          tool_calls: [
            {
              id: 'tool_b2_1',
              tool_name: 'mcp_lucid-mcp_store_memory',
              arguments: {
                content: 'CMC integration complete for MCP server',
                tags: { type: 'integration', system: 'mcp', component: 'cmc' }
              },
              result: { memory_id: 'mem_cmc_001', atom_id: 'atom_cmc_integration_001' },
              status: 'success',
              duration_ms: 78,
              timestamp: new Date(now - 10500000)
            },
            {
              id: 'tool_b2_2',
              tool_name: 'mcp_lucid-mcp_track_confidence',
              arguments: {
                task: 'CMC integration',
                confidence: 0.93,
                evidence: ['atom_cmc_integration_001']
              },
              result: { tracked: true, witness_id: 'witness_cmc_001' },
              status: 'success',
              duration_ms: 23,
              timestamp: new Date(now - 10500000)
            },
            {
              id: 'tool_b2_3',
              tool_name: 'mcp_lucid-mcp_update_goal_progress',
              arguments: {
                goal_id: 'OBJ-08',
                progress: 0.65,
                milestone: 'CMC integration complete'
              },
              result: { updated: true },
              status: 'success',
              duration_ms: 15,
              timestamp: new Date(now - 10500000)
            }
          ],
          work_references: {
            files: [
              {
                path: 'packages/lucid_mcp_server/tools/cmc_tools.py',
                operation: 'modified',
                lines: [1, 50]
              },
              {
                path: 'packages/lucid_mcp_server/tools/vif_tools.py',
                operation: 'modified',
                lines: [1, 50]
              }
            ],
            goals: ['OBJ-01', 'OBJ-08'],
            cmc_atoms: ['atom_cmc_integration_001'],
            vif_witnesses: ['witness_cmc_001']
          },
          evidence_trail: {
            cmc_atom_id: 'atom_cmc_integration_001',
            vif_witness_id: 'witness_cmc_001'
          },
          goal_alignment: {
            objective: 'OBJ-08',
            key_result: 'KR-08-01',
            progress: 0.65
          }
        },
        {
          id: 'msg_b3',
          timestamp: new Date(now - 10200000),
          role: 'user',
          content: 'How are we handling the 80-tool limit in Cursor?'
        },
        {
          id: 'msg_b4',
          timestamp: new Date(now - 9900000),
          role: 'assistant',
          content: 'Using RAG middleware to intelligently filter tools based on context. Only relevant tools are exposed to Cursor.',
          agent: 'codex',
          agent_id: 'codex_001',
          confidence: 0.88,
          work_references: {
            files: [{
              path: 'packages/mcp_rag_proxy/mcp_rag_middleware.py',
              operation: 'modified',
              lines: [100, 150]
            }],
            cmc_atoms: ['atom_rag_filtering_001'],
            vif_witnesses: ['witness_rag_001']
          },
          evidence_trail: {
            cmc_atom_id: 'atom_rag_filtering_001',
            vif_witness_id: 'witness_rag_001'
          },
          goal_alignment: {
            objective: 'OBJ-08',
            key_result: 'KR-08-01',
            progress: 0.80
          }
        }
      ],
      'backend-research': [
        {
          id: 'msg_br1',
          timestamp: new Date(now - 14400000),
          role: 'assistant',
          content: 'Researching MCP protocol specifications. Need to understand tool registration and execution flow.',
          agent: 'codex',
          agent_id: 'codex_001',
          confidence: 0.84,
          work_references: {
            files: [{
              path: 'knowledge_architecture/AETHER_MEMORY/investigations/MCP_TOOLS_DEEP_INVESTIGATION.md',
              operation: 'modified',
              lines: [1, 50]
            }],
            cmc_atoms: ['atom_mcp_research_001']
          },
          evidence_trail: {
            cmc_atom_id: 'atom_mcp_research_001',
            supporting_files: [{
              path: 'knowledge_architecture/AETHER_MEMORY/investigations/MCP_TOOLS_DEEP_INVESTIGATION.md',
              lines: [1, 50],
              relevance: 0.80
            }]
          },
          goal_alignment: {
            objective: 'OBJ-08',
            key_result: 'KR-08-02',
            progress: 0.25
          }
        },
        {
          id: 'msg_br2',
          timestamp: new Date(now - 14100000),
          role: 'assistant',
          content: 'MCP uses JSON-RPC 2.0. Tools are registered via tools/list, executed via tools/call. We need to handle async operations.',
          agent: 'aether',
          agent_id: 'aether_001',
          confidence: 0.90,
          work_references: {
            files: [
              {
                path: 'knowledge_architecture/AETHER_MEMORY/investigations/MCP_TOOLS_DEEP_INVESTIGATION.md',
                operation: 'modified',
                lines: [50, 100]
              },
              {
                path: 'lucid_mcp_server.py',
                operation: 'modified',
                lines: [1, 50]
              }
            ],
            cmc_atoms: ['atom_mcp_research_002'],
            vif_witnesses: ['witness_mcp_research_001']
          },
          evidence_trail: {
            cmc_atom_id: 'atom_mcp_research_002',
            vif_witness_id: 'witness_mcp_research_001'
          },
          goal_alignment: {
            objective: 'OBJ-08',
            key_result: 'KR-08-02',
            progress: 0.50
          }
        }
      ]
    }
    
    setMessages(mockMessages)
  }, [])
  
  // Initialize messages for selected channel if empty
  useEffect(() => {
    if (!messages[selectedChannel]) {
      setMessages(prev => ({
        ...prev,
        [selectedChannel]: []
      }))
    }
  }, [selectedChannel, messages])
  
  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [displayMessages, connectedChannels])
  
  // Close ping menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showPingMenu && !(event.target as Element).closest('.ping-menu-container')) {
        setShowPingMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [showPingMenu])
  
  // Handle channel selection with shift-click support
  const handleChannelSelect = (channelId: string, event?: React.MouseEvent) => {
    const isShiftClick = event?.shiftKey || false
    const channel = CHANNELS.find(c => c.id === channelId)
    const sections = CHANNELS.filter(c => c.parentId === channelId)
    
    // If clicking main channel with sections, select all sub-channels
    if (sections.length > 0 && !isShiftClick) {
      const allSectionIds = sections.map(s => s.id)
      setSelectedChannel(channelId) // Set main as primary
      setSelectedChannels(new Set([channelId, ...allSectionIds]))
      return
    }
    
    // Shift-click: multi-select
    if (isShiftClick) {
      setSelectedChannels(prev => {
        const next = new Set(prev)
        if (next.has(channelId)) {
          next.delete(channelId)
          // If removing primary, set first remaining as primary
          if (channelId === selectedChannel && next.size > 0) {
            setSelectedChannel(Array.from(next)[0])
          }
        } else {
          next.add(channelId)
        }
        return next
      })
    } else {
      // Normal click: single select
      setSelectedChannel(channelId)
      setSelectedChannels(new Set([channelId]))
    }
  }
  
  // Toggle channel expansion
  const toggleChannel = (channelId: string) => {
    setExpandedChannels(prev => {
      const next = new Set(prev)
      if (next.has(channelId)) {
        next.delete(channelId)
      } else {
        next.add(channelId)
      }
      return next
    })
  }
  
  const handleSend = () => {
    if (!input.trim()) return
    
    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      timestamp: new Date(),
      role: 'user',
      content: input,
      agent: 'user',
      context_summary: `Sent to ${selectedChannels.size} channel(s): ${Array.from(selectedChannels).map(id => CHANNELS.find(c => c.id === id)?.name || id).join(', ')}`
    }
    
    // Send message to all selected channels
    setMessages(prev => {
      const next = { ...prev }
      selectedChannels.forEach(channelId => {
        if (!next[channelId]) next[channelId] = []
        next[channelId] = [...next[channelId], userMessage]
      })
      return next
    })
    setInput('')
    
    // Simulate AI response from agents in selected channels
    setTimeout(() => {
      selectedChannels.forEach(channelId => {
        const activeAgents = agents.filter(a => a.currentChannel === channelId && a.status === 'active')
        const agent = activeAgents[0] || agents[0]
        const aiMessage: ChatMessage = {
          id: `ai_${Date.now()}_${channelId}`,
          timestamp: new Date(),
          role: 'assistant',
          content: `Response from ${agent.name} in #${CHANNELS.find(c => c.id === channelId)?.name || channelId}: I understand your request. Processing...`,
          agent: agent.id,
          confidence: agent.confidence,
          context_summary: `Context from #${CHANNELS.find(c => c.id === channelId)?.name || channelId}: ${selectedChannels.size > 1 ? `Also visible in ${selectedChannels.size - 1} other channel(s)` : 'Single channel view'}`
        }
        setMessages(prev => ({
          ...prev,
          [channelId]: [...(prev[channelId] || []), aiMessage]
        }))
      })
    }, 1000)
  }
  
  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'active': return 'text-green-400'
      case 'busy': return 'text-yellow-400'
      case 'idle': return 'text-gray-400'
    }
  }

  // Helper component for work references - Enhanced with full file details
  const WorkReferences: React.FC<{ references: WorkReference }> = ({ references }) => {
    if (!references || (!references.files?.length && !references.goals?.length && !references.cmc_atoms?.length && !references.vif_witnesses?.length)) {
      return null
    }

    return (
      <div className="mt-2 pt-2 border-t border-gray-700 space-y-2">
        <div className="text-[10px] text-gray-400 font-semibold">Work References</div>
        
        {/* Files - Show full paths and line numbers */}
        {references.files && references.files.length > 0 && (
          <div className="space-y-1">
            <div className="text-[10px] text-gray-500 mb-1">Files ({references.files.length}):</div>
            {references.files.map((file, idx) => (
              <div key={idx} className="px-2 py-1 rounded bg-gray-700/50 text-[10px] text-gray-300 font-mono">
                <div className="text-gray-400">{file.path}</div>
                {file.lines && file.lines.length > 0 && (
                  <div className="text-gray-500 mt-0.5">
                    Lines {file.lines[0]}{file.lines.length > 1 ? `-${file.lines[file.lines.length - 1]}` : ''}
                    {file.operation && (
                      <span className="ml-2 text-gray-600">({file.operation})</span>
                    )}
                    {file.commit_hash && (
                      <span className="ml-2 text-gray-600 font-mono">commit: {file.commit_hash.slice(0, 7)}</span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
        
        {/* Goals */}
        {references.goals && references.goals.length > 0 && (
          <div className="space-y-1">
            <div className="text-[10px] text-gray-500 mb-1">Goals ({references.goals.length}):</div>
            <div className="flex flex-wrap gap-1">
              {references.goals.map((goal, idx) => (
                <div key={idx} className="px-2 py-0.5 rounded bg-blue-600/20 text-[10px] text-blue-300">
                  {goal}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* CMC Atoms */}
        {references.cmc_atoms && references.cmc_atoms.length > 0 && (
          <div className="space-y-1">
            <div className="text-[10px] text-gray-500 mb-1">CMC Atoms ({references.cmc_atoms.length}):</div>
            <div className="flex flex-wrap gap-1">
              {references.cmc_atoms.map((atom, idx) => (
                <div key={idx} className="px-2 py-0.5 rounded bg-purple-600/20 text-[10px] text-purple-300 font-mono">
                  {atom}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* VIF Witnesses */}
        {references.vif_witnesses && references.vif_witnesses.length > 0 && (
          <div className="space-y-1">
            <div className="text-[10px] text-gray-500 mb-1">VIF Witnesses ({references.vif_witnesses.length}):</div>
            <div className="flex flex-wrap gap-1">
              {references.vif_witnesses.map((witness, idx) => (
                <div key={idx} className="px-2 py-0.5 rounded bg-green-600/20 text-[10px] text-green-300 font-mono">
                  {witness}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  // Helper component for evidence trail - Enhanced with full file details
  const EvidenceTrail: React.FC<{ trail: ChatMessage['evidence_trail'] }> = ({ trail }) => {
    if (!trail || (!trail.cmc_atom_id && !trail.vif_witness_id && !trail.supporting_files?.length)) {
      return null
    }

    return (
      <div className="mt-2 pt-2 border-t border-gray-700">
        <div className="text-[10px] text-gray-400 mb-2 font-semibold">Evidence Trail</div>
        <div className="space-y-2">
          {trail.cmc_atom_id && (
            <div className="px-2 py-1 rounded bg-purple-600/20 text-[10px] text-purple-300">
              <span className="font-mono">CMC: {trail.cmc_atom_id}</span>
            </div>
          )}
          {trail.vif_witness_id && (
            <div className="px-2 py-1 rounded bg-green-600/20 text-[10px] text-green-300">
              <span className="font-mono">VIF: {trail.vif_witness_id}</span>
            </div>
          )}
          {trail.supporting_files && trail.supporting_files.length > 0 && (
            <div className="space-y-1">
              <div className="text-[10px] text-gray-500 mb-1">Files Referenced ({trail.supporting_files.length}):</div>
              {trail.supporting_files.map((file, idx) => (
                <div key={idx} className="px-2 py-1 rounded bg-gray-700/50 text-[10px] text-gray-300 font-mono">
                  <div className="text-gray-400">{file.path}</div>
                  {file.lines && file.lines.length > 0 && (
                    <div className="text-gray-500 mt-0.5">
                      Lines: {file.lines.join(', ')}
                      {file.relevance && (
                        <span className="ml-2 text-gray-600">({(file.relevance * 100).toFixed(0)}% relevant)</span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    )
  }

  // Helper component for goal alignment - No icons
  const GoalAlignmentDisplay: React.FC<{ alignment?: GoalAlignment }> = ({ alignment }) => {
    if (!alignment || !alignment.objective) return null

    return (
      <div className="mt-2 pt-2 border-t border-gray-700">
        <div className="flex items-center gap-2 text-[10px] text-gray-400">
          <span>Goal Alignment:</span>
          <span className="text-blue-300">{alignment.objective}</span>
          {alignment.key_result && (
            <>
              <span className="text-gray-500">→</span>
              <span className="text-blue-200">{alignment.key_result}</span>
            </>
          )}
          {alignment.progress !== undefined && (
            <div className="ml-auto flex items-center gap-1">
              <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-blue-500 transition-all"
                  style={{ width: `${alignment.progress * 100}%` }}
                />
              </div>
              <span className="text-gray-400">{(alignment.progress * 100).toFixed(0)}%</span>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Helper component for tool calls - No icons
  const ToolCalls: React.FC<{ toolCalls: ToolCall[] }> = ({ toolCalls }) => {
    if (!toolCalls || toolCalls.length === 0) return null

    return (
      <div className="mt-2 pt-2 border-t border-gray-700 space-y-1.5">
        <div className="text-[10px] text-gray-400 mb-1 font-semibold">Tool Calls ({toolCalls.length})</div>
        {toolCalls.map((toolCall, idx) => {
          const toolName = toolCall.tool_name.replace('mcp_lucid-mcp_', '')
          const displayName = toolName.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
          
          return (
            <div
              key={toolCall.id || idx}
              className={`px-2 py-1.5 rounded text-xs border ${
                toolCall.status === 'success'
                  ? 'bg-green-600/10 border-green-600/30 text-green-300'
                  : toolCall.status === 'error'
                  ? 'bg-red-600/10 border-red-600/30 text-red-300'
                  : 'bg-yellow-600/10 border-yellow-600/30 text-yellow-300'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono font-semibold">{displayName}</span>
                <span className={`text-[10px] px-1 py-0.5 rounded ${
                  toolCall.status === 'success' ? 'bg-green-600/20' :
                  toolCall.status === 'error' ? 'bg-red-600/20' :
                  'bg-yellow-600/20'
                }`}>
                  {toolCall.status}
                </span>
                {toolCall.duration_ms && (
                  <span className="text-[10px] text-gray-500 ml-auto">
                    {toolCall.duration_ms}ms
                  </span>
                )}
              </div>
              {Object.keys(toolCall.arguments || {}).length > 0 && (
                <div className="mt-1 text-[10px] text-gray-400 font-mono">
                  <div className="opacity-70">Args: {JSON.stringify(toolCall.arguments, null, 2).slice(0, 100)}...</div>
                </div>
              )}
              {toolCall.result && toolCall.status === 'success' && (
                <div className="mt-1 text-[10px] text-gray-300">
                  <div className="opacity-70">Result: {typeof toolCall.result === 'string' ? toolCall.result.slice(0, 80) : JSON.stringify(toolCall.result).slice(0, 80)}...</div>
                </div>
              )}
              {toolCall.status === 'error' && toolCall.result && (
                <div className="mt-1 text-[10px] text-red-300">
                  Error: {typeof toolCall.result === 'string' ? toolCall.result : JSON.stringify(toolCall.result)}
                </div>
              )}
            </div>
          )
        })}
      </div>
    )
  }

  // Helper component for context summary display
  const ContextSummary: React.FC<{ summary?: string }> = ({ summary }) => {
    if (!summary) return null
    
    return (
      <div className="mt-2 pt-2 border-t border-gray-700">
        <div className="text-[10px] text-gray-400 mb-1 font-semibold">Context Summary</div>
        <div className="px-2 py-1 rounded bg-gray-700/30 text-[10px] text-gray-300">
          {summary}
        </div>
      </div>
    )
  }
  
  // Helper component for connected channel badge
  const ConnectedChannelBadge: React.FC<{ channelId: string }> = ({ channelId }) => {
    const channel = CHANNELS.find(c => c.id === channelId)
    return (
      <div className="flex items-center gap-1 px-2 py-0.5 rounded bg-blue-600/20 text-[10px] text-blue-300 border border-blue-600/30">
        <Link2 className="w-2.5 h-2.5" />
        <span>#{channel?.name || channelId}</span>
      </div>
    )
  }

  // Helper component for compact tool display
  const CompactToolDisplay: React.FC<{ toolCalls: ToolCall[] }> = ({ toolCalls }) => {
    if (!toolCalls || toolCalls.length === 0) return null

    const [showTooltip, setShowTooltip] = useState(false)

    // Extract tool names (remove mcp_lucid-mcp_ prefix for display)
    const toolNames = toolCalls.map(tc => {
      const name = tc.tool_name.replace('mcp_lucid-mcp_', '')
      return name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
    })

    // If only one tool, show it directly
    if (toolCalls.length === 1) {
      return (
        <div className="flex items-center gap-1 text-[10px] text-gray-400">
          <span className="truncate max-w-[120px]">{toolNames[0]}</span>
        </div>
      )
    }

    // Multiple tools - show first one + count
    return (
      <div className="relative">
        <div
          className="flex items-center gap-1 text-[10px] text-gray-400 cursor-help"
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
        >
          <span className="truncate max-w-[100px]">{toolNames[0]}</span>
          <span className="text-blue-400 font-semibold">+{toolCalls.length - 1}</span>
        </div>
        
        {/* Tooltip with all tools */}
        {showTooltip && (
          <div
            className="absolute bottom-full left-0 mb-2 w-64 bg-gray-900 border border-gray-700 rounded shadow-lg z-50 p-2"
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
          >
            <div className="text-[10px] font-semibold text-gray-300 mb-1.5">Tools Used ({toolCalls.length})</div>
            <div className="space-y-1">
              {toolCalls.map((tc, idx) => {
                const name = tc.tool_name.replace('mcp_lucid-mcp_', '')
                const displayName = name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
                return (
                  <div
                    key={tc.id || idx}
                    className="flex items-center gap-2 text-[10px] text-gray-400"
                  >
                    <Code className={`w-2.5 h-2.5 flex-shrink-0 ${
                      tc.status === 'success' ? 'text-green-400' :
                      tc.status === 'error' ? 'text-red-400' :
                      'text-yellow-400'
                    }`} />
                    <span className="flex-1">{displayName}</span>
                    {tc.duration_ms && (
                      <span className="text-gray-500">{tc.duration_ms}ms</span>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>
    )
  }

  // Function to ping/connect channels
  const handlePingChannel = (targetChannelId: string, reason: string) => {
    const pingMessage: ChatMessage = {
      id: `ping_${Date.now()}`,
      timestamp: new Date(),
      role: 'system',
      content: `🔔 Pinged #${CHANNELS.find(c => c.id === targetChannelId)?.name || targetChannelId}: ${reason}`,
      ping_context: {
        from_channel: selectedChannel,
        reason,
        connected_at: new Date()
      }
    }

    // Add ping message to current channel
    setMessages(prev => ({
      ...prev,
      [selectedChannel]: [...(prev[selectedChannel] || []), pingMessage]
    }))

    // Connect channels
    setConnectedChannels(prev => new Set([...prev, targetChannelId]))

    // Add connection message to target channel (simulated)
    const connectionMessage: ChatMessage = {
      id: `connect_${Date.now()}`,
      timestamp: new Date(),
      role: 'system',
      content: `🔗 Connected to #${CHANNELS.find(c => c.id === selectedChannel)?.name || selectedChannel}. Reason: ${reason}`,
      ping_context: {
        from_channel: selectedChannel,
        reason,
        connected_at: new Date()
      }
    }

    setMessages(prev => ({
      ...prev,
      [targetChannelId]: [...(prev[targetChannelId] || []), connectionMessage]
    }))
  }

  // Function to disconnect channels
  const handleDisconnectChannel = (channelId: string) => {
    setConnectedChannels(prev => {
      const next = new Set(prev)
      next.delete(channelId)
      return next
    })

    // Add disconnect message
    const disconnectMessage: ChatMessage = {
      id: `disconnect_${Date.now()}`,
      timestamp: new Date(),
      role: 'system',
      content: `🔌 Disconnected from #${CHANNELS.find(c => c.id === channelId)?.name || channelId}`
    }

    setMessages(prev => ({
      ...prev,
      [selectedChannel]: [...(prev[selectedChannel] || []), disconnectMessage]
    }))
  }

  const mainChannels = CHANNELS.filter(c => c.type === 'channel')
  const selectedChannelData = CHANNELS.find(c => c.id === selectedChannel)
  const availableChannels = CHANNELS.filter(c => c.id !== selectedChannel && !connectedChannels.has(c.id))
  
  const toggleMessageExpansion = (messageId: string) => {
    setExpandedMessages(prev => {
      const next = new Set(prev)
      if (next.has(messageId)) {
        next.delete(messageId)
      } else {
        next.add(messageId)
      }
      return next
    })
  }

  return (
    <AIChatContextProvider
      messages={messages}
      contextInfo={contextInfo}
      assembledContext={assembledContext}
      selectedChannel={selectedChannel}
      budget={retrievalBudget}
      useRetrieval={useRetrieval}
      setUseRetrieval={setUseRetrieval}
    >
      <div className="h-full flex bg-gray-950">
      {/* Channel Sidebar */}
      <div className={`${sidebarCollapsed ? 'w-12' : 'w-48'} bg-gray-900 border-r border-gray-800 flex flex-col transition-all duration-200`}>
        {/* Header */}
        <div className="p-3 border-b border-gray-800">
          <div className="flex items-center justify-between mb-2">
            {!sidebarCollapsed && (
              <h3 className="text-xs font-semibold text-gray-400 uppercase">Channels</h3>
            )}
            <div className="flex items-center gap-1">
              {!sidebarCollapsed && (
                <button className="p-1 rounded hover:bg-gray-800 text-gray-400 hover:text-gray-300">
                  <Plus className="w-3 h-3" />
                </button>
              )}
              <button
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                className="p-1 rounded hover:bg-gray-800 text-gray-400 hover:text-gray-300"
                title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
              >
                {sidebarCollapsed ? (
                  <ChevronRight className="w-3 h-3" />
                ) : (
                  <ChevronRight className="w-3 h-3 rotate-180" />
                )}
              </button>
            </div>
          </div>
        </div>
        
        {/* Channel List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {mainChannels.map(channel => {
            const isExpanded = expandedChannels.has(channel.id)
            const sections = CHANNELS.filter(c => c.parentId === channel.id)
            const isSelected = selectedChannel === channel.id || sections.some(s => s.id === selectedChannel)
            
            return (
              <div key={channel.id}>
                {/* Main Channel */}
                <button
                  onClick={(e) => {
                    if (sections.length > 0) {
                      if (e.shiftKey) {
                        // Shift-click: multi-select all sections
                        const allSectionIds = sections.map(s => s.id)
                        setSelectedChannels(prev => {
                          const next = new Set(prev)
                          allSectionIds.forEach(id => next.add(id))
                          return next
                        })
                      } else {
                        // Normal click: select all sub-channels
                        handleChannelSelect(channel.id, e)
                      }
                    } else {
                      handleChannelSelect(channel.id, e)
                    }
                  }}
                  className={`w-full text-left ${sidebarCollapsed ? 'px-1.5 py-1.5 justify-center' : 'px-2 py-1.5'} rounded text-xs transition-colors flex items-center gap-1 ${
                    isSelected && sections.length === 0
                      ? 'bg-gray-800 text-gray-100'
                      : selectedChannels.has(channel.id)
                      ? 'bg-blue-600/20 text-blue-300 border border-blue-600/30'
                      : 'text-gray-400 hover:bg-gray-800 hover:text-gray-300'
                  }`}
                  title={sidebarCollapsed ? channel.name : undefined}
                >
                  {sections.length > 0 ? (
                    isExpanded ? (
                      <ChevronDown className="w-3 h-3 flex-shrink-0" />
                    ) : (
                      <ChevronRight className="w-3 h-3 flex-shrink-0" />
                    )
                  ) : (
                    <Hash className="w-3 h-3 flex-shrink-0" />
                  )}
                  {!sidebarCollapsed && (
                    <span className="truncate flex-1">{channel.name}</span>
                  )}
                </button>
                
                {/* Sections */}
                {!sidebarCollapsed && isExpanded && sections.length > 0 && (
                  <div className="ml-4 mt-1 space-y-0.5">
                    {sections.map(section => {
                      const isSectionSelected = selectedChannel === section.id
                      const isMultiSelected = selectedChannels.has(section.id) && !isSectionSelected
                      
                      return (
                        <button
                          key={section.id}
                          onClick={(e) => handleChannelSelect(section.id, e)}
                          className={`w-full text-left px-2 py-1 rounded text-xs transition-colors flex items-center gap-1 ${
                            isSectionSelected
                              ? 'bg-blue-600 text-white'
                              : isMultiSelected
                              ? 'bg-blue-600/20 text-blue-300 border border-blue-600/30'
                              : 'text-gray-500 hover:bg-gray-800 hover:text-gray-300'
                          }`}
                        >
                          <Hash className="w-3 h-3 flex-shrink-0" />
                          <span className="truncate flex-1">{section.name}</span>
                        </button>
                      )
                    })}
                  </div>
                )}
              </div>
            )
          })}
        </div>
        
        {/* Active Agents */}
        {!sidebarCollapsed && (
          <div className="border-t border-gray-800 p-2 bg-gray-900/50">
            <div className="text-xs font-semibold text-gray-400 mb-2">Active Agents</div>
            <div className="space-y-1">
              {agents.map(agent => (
                <div
                  key={agent.id}
                  className="flex items-center gap-2 px-2 py-1 rounded text-xs"
                >
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(agent.status)}`} />
                  <span className="text-gray-400 truncate flex-1">{agent.name}</span>
                  {agent.confidence && (
                    <span className="text-[10px] text-gray-500">
                      {(agent.confidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      
      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Channel Header */}
        <div className="h-12 border-b border-gray-800 px-4 flex items-center gap-2 bg-gray-900/50">
          <Hash className="w-4 h-4 text-gray-400" />
          <span className="text-sm font-semibold text-gray-200">
            {selectedChannels.size > 1 
              ? `${selectedChannelData?.name || 'Channel'} (+${selectedChannels.size - 1} more)`
              : selectedChannelData?.name || 'Channel'
            }
          </span>
          {selectedChannelData?.description && (
            <span className="text-xs text-gray-500">• {selectedChannelData.description}</span>
          )}
          
          {/* Multi-selected channels indicator */}
          {selectedChannels.size > 1 && (
            <div className="flex items-center gap-1 ml-2">
              {Array.from(selectedChannels).filter(id => id !== selectedChannel).slice(0, 3).map(channelId => {
                const channel = CHANNELS.find(c => c.id === channelId)
                return (
                  <div key={channelId} className="px-1.5 py-0.5 rounded bg-blue-600/20 text-[10px] text-blue-300 border border-blue-600/30">
                    #{channel?.name || channelId}
                  </div>
                )
              })}
              {selectedChannels.size > 4 && (
                <span className="text-[10px] text-gray-500">+{selectedChannels.size - 4}</span>
              )}
            </div>
          )}
          
          {/* Connected Channels */}
          {connectedChannels.size > 0 && (
            <div className="flex items-center gap-1 ml-2">
              {Array.from(connectedChannels).map(channelId => (
                <div key={channelId} className="flex items-center gap-1 px-2 py-0.5 rounded bg-blue-600/20 text-[10px] text-blue-300 border border-blue-600/30">
                  <Link2 className="w-2.5 h-2.5" />
                  <span>#{CHANNELS.find(c => c.id === channelId)?.name || channelId}</span>
                  <button
                    onClick={() => handleDisconnectChannel(channelId)}
                    className="ml-1 hover:bg-blue-600/30 rounded p-0.5"
                    title="Disconnect"
                  >
                    <X className="w-2.5 h-2.5" />
                  </button>
                </div>
              ))}
            </div>
          )}
          
          <div className="flex-1" />
          
          {/* Retrieval Toggle */}
          <div className="flex items-center gap-2 mr-2">
            {/* RAG Toggle */}
            <button
              onClick={() => setRagEnabled(!ragEnabled)}
              className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                ragEnabled ? 'bg-purple-600' : 'bg-gray-700'
              }`}
              title={ragEnabled ? 'Disable RAG retrieval' : 'Enable RAG retrieval'}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  ragEnabled ? 'translate-x-5' : 'translate-x-1'
                }`}
              />
            </button>
            <span className="text-xs text-gray-400">RAG</span>
            
            {/* Context Retrieval Toggle */}
            <span className="text-xs text-gray-400">Retrieval</span>
            <button
              onClick={() => setUseRetrieval(!useRetrieval)}
              className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                useRetrieval ? 'bg-blue-600' : 'bg-gray-700'
              }`}
              title={useRetrieval ? 'Disable context retrieval' : 'Enable context retrieval'}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  useRetrieval ? 'translate-x-5' : 'translate-x-1'
                }`}
              />
            </button>
            {useRetrieval && hybridResult && (
              <span className="text-xs text-gray-400">
                {hybridResult.totalTokens.toLocaleString()}/{retrievalBudget.toLocaleString()}
                {ragEnabled && (
                  <span className="ml-1 text-purple-400">
                    ({hybridResult.ragTokens.toLocaleString()} RAG, {hybridResult.atomTokens.toLocaleString()} atoms)
                  </span>
                )}
              </span>
            )}
          </div>
          
          {/* Ping/Connect Button */}
          <div className="relative ping-menu-container">
            <button
              onClick={() => setShowPingMenu(!showPingMenu)}
              className="p-1.5 rounded hover:bg-gray-800 text-gray-400 hover:text-gray-300 transition-colors"
              title="Ping/Connect Channel"
            >
              <Zap className="w-4 h-4" />
            </button>
            
            {/* Ping Menu */}
            {showPingMenu && (
              <div className="absolute right-0 top-full mt-1 w-64 bg-gray-900 border border-gray-700 rounded shadow-lg z-50">
                <div className="p-2 border-b border-gray-800">
                  <div className="text-xs font-semibold text-gray-300 mb-1">Connect to Channel</div>
                  <div className="text-[10px] text-gray-500">Select a channel to collaborate with</div>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  {availableChannels.length === 0 ? (
                    <div className="p-3 text-xs text-gray-500 text-center">
                      No available channels
                    </div>
                  ) : (
                    availableChannels.map(channel => (
                      <button
                        key={channel.id}
                        onClick={() => {
                          const reason = prompt(`Reason for connecting to #${channel.name}:`)
                          if (reason) {
                            handlePingChannel(channel.id, reason)
                            setShowPingMenu(false)
                          }
                        }}
                        className="w-full text-left px-3 py-2 hover:bg-gray-800 text-xs text-gray-300 flex items-center gap-2"
                      >
                        <Hash className="w-3 h-3" />
                        <span className="flex-1">{channel.name}</span>
                        <ChevronRightIcon className="w-3 h-3 text-gray-500" />
                      </button>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
        
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {displayMessages.length === 0 ? (
            <div className="text-center text-gray-500 py-8 text-xs">
              <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No messages in this channel yet</p>
              <p className="text-[10px] text-gray-600 mt-1">
                Start a conversation
              </p>
            </div>
          ) : (
            displayMessages.map(msg => (
              <div
                key={msg.id}
                className={`flex gap-3 ${
                  msg.role === 'user' ? 'justify-end' : 'justify-start'
                } ${msg.connected_channel ? 'opacity-90' : ''}`}
              >
                <div className={`max-w-[85%] ${msg.role === 'user' ? 'flex flex-col items-end' : ''}`}>
                  {/* Compact Header */}
                  <div className="flex items-center gap-2 mb-1">
                    {msg.multi_selected_channel && (
                      <div className="px-2 py-0.5 rounded bg-blue-600/20 text-[10px] text-blue-300 border border-blue-600/30">
                        <span>#{CHANNELS.find(c => c.id === msg.multi_selected_channel)?.name || msg.multi_selected_channel}</span>
                      </div>
                    )}
                    {msg.connected_channel && (
                      <ConnectedChannelBadge channelId={msg.connected_channel} />
                    )}
                    {msg.role !== 'user' && msg.agent && (
                      <>
                        <span className="text-xs font-semibold text-gray-300">
                          {agents.find(a => a.id === msg.agent)?.name || msg.agent}
                        </span>
                        <span className="text-[10px] text-gray-500">
                          {msg.timestamp.toLocaleTimeString()}
                        </span>
                      </>
                    )}
                    {msg.role === 'user' && (
                      <>
                        <span className="text-xs font-semibold text-gray-300">You</span>
                        <span className="text-[10px] text-gray-500">
                          {msg.timestamp.toLocaleTimeString()}
                        </span>
                      </>
                    )}
                    {/* Compact indicators */}
                    <div className="flex items-center gap-1 ml-auto">
                      {msg.tool_calls && msg.tool_calls.length > 0 && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-600/20 text-blue-300 border border-blue-600/30">
                          {msg.tool_calls.length} tool{msg.tool_calls.length > 1 ? 's' : ''}
                        </span>
                      )}
                      {msg.work_references && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-700/50 text-gray-400 border border-gray-600/30">
                          {[
                            msg.work_references.files?.length || 0,
                            msg.work_references.goals?.length || 0,
                            msg.work_references.cmc_atoms?.length || 0
                          ].filter(n => n > 0).length} ref{[
                            msg.work_references.files?.length || 0,
                            msg.work_references.goals?.length || 0,
                            msg.work_references.cmc_atoms?.length || 0
                          ].filter(n => n > 0).length > 1 ? 's' : ''}
                        </span>
                      )}
                      {(msg.tool_calls || msg.work_references || msg.evidence_trail || msg.goal_alignment) && (
                        <button
                          onClick={() => toggleMessageExpansion(msg.id)}
                          className="p-0.5 rounded hover:bg-gray-700 text-gray-500 hover:text-gray-300 transition-colors"
                          title={expandedMessages.has(msg.id) ? "Collapse details" : "Expand details"}
                        >
                          {expandedMessages.has(msg.id) ? (
                            <ChevronUp className="w-3 h-3" />
                          ) : (
                            <ChevronDownIcon className="w-3 h-3" />
                          )}
                        </button>
                      )}
                    </div>
                  </div>
                  
                  {/* Message Content */}
                  <div
                    className={`rounded-lg p-3 text-sm ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : msg.role === 'system'
                        ? 'bg-gray-800 text-gray-400 border border-gray-700'
                        : msg.connected_channel
                        ? 'bg-gray-800 text-gray-200 border-l-2 border-purple-500'
                        : 'bg-gray-800 text-gray-200'
                    }`}
                  >
                    <div className="mb-2">{msg.content}</div>
                    
                    {/* Compact inline indicators - Always show if there's any metadata */}
                    {!expandedMessages.has(msg.id) && (msg.tool_calls && msg.tool_calls.length > 0 || msg.confidence || msg.goal_alignment || msg.work_references) && (
                      <div className="flex items-center gap-2 flex-wrap mt-2 pt-2 border-t border-gray-700/50">
                        {/* MCP Tools - Compact Display */}
                        {msg.tool_calls && msg.tool_calls.length > 0 && (
                          <CompactToolDisplay toolCalls={msg.tool_calls} />
                        )}
                        {msg.confidence && (
                          <div className="flex items-center gap-1 text-[10px]">
                            <span className="text-gray-400">{(msg.confidence * 100).toFixed(0)}%</span>
                          </div>
                        )}
                        {msg.goal_alignment && (
                          <div className="flex items-center gap-1 text-[10px] text-gray-400">
                            <span>{msg.goal_alignment.objective}</span>
                            {msg.goal_alignment.progress !== undefined && (
                              <span className="text-gray-500">
                                {(msg.goal_alignment.progress * 100).toFixed(0)}%
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                    
                    {/* Expanded Details */}
                    {expandedMessages.has(msg.id) && (
                      <div className="mt-3 pt-3 border-t border-gray-700 space-y-2">
                        {/* Tool Calls */}
                        {msg.tool_calls && <ToolCalls toolCalls={msg.tool_calls} />}
                        
                        {/* Work References */}
                        {msg.work_references && <WorkReferences references={msg.work_references} />}
                        
                        {/* Evidence Trail */}
                        {msg.evidence_trail && <EvidenceTrail trail={msg.evidence_trail} />}
                        
                        {/* Goal Alignment */}
                        {msg.goal_alignment && <GoalAlignmentDisplay alignment={msg.goal_alignment} />}
                        
                        {/* Context Summary */}
                        {msg.context_summary && <ContextSummary summary={msg.context_summary} />}
                        
                        {/* Confidence Score */}
                        {msg.confidence && (
                          <div className="text-[10px] opacity-70">
                            <span>Confidence: {(msg.confidence * 100).toFixed(0)}%</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {/* Message Context Badge */}
                  {msg.role !== 'user' && (
                    <div className="mt-2">
                      <MessageContextBadge
                        messageId={msg.id}
                        atom={getSummaryAtom(selectedChannel, msg.id)}
                        contextInfo={getContextInfo(selectedChannel, msg.id)}
                        override={getOverride(msg.id)}
                        packTotal={packTotal}
                        onPromote={(id) => {
                          // Promote: increase half-life (future enhancement)
                          console.log('Promote message:', id)
                        }}
                        onPin={togglePin}
                        onForce={setForcedLevel}
                        onPriority={setPriority}
                      />
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input Area */}
        <div className="border-t border-gray-800 p-3 bg-gray-900/50">
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder={`Message #${selectedChannelData?.name || 'channel'}...`}
              className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-300 outline-none focus:border-blue-500"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className="p-2 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          </div>
        </div>
      </div>
    </AIChatContextProvider>
  )
}

// Default export for lazy loading compatibility
export default AIChatManagement
