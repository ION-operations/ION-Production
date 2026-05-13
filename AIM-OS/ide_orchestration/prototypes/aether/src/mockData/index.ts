// Mock Data for Aether IDE Prototype
// Comprehensive mock data for all panels and AIM-OS systems

// File Tree Mock Data (CMC-backed)
export const mockFileTree = {
  "src/": {
    "components/": {
      "IDELayout.tsx": {
        type: "file",
        size: 15420,
        modified: "2025-11-07T15:30:00Z",
        confidence: 0.92,
        evidence: ["atom_123", "atom_456"],
        bitemporal: { valid_from: "2025-11-07T10:00:00Z", valid_to: null }
      },
      "CodeEditor.tsx": {
        type: "file",
        size: 8234,
        modified: "2025-11-07T14:20:00Z",
        confidence: 0.88,
        evidence: ["atom_789"],
        bitemporal: { valid_from: "2025-11-07T12:00:00Z", valid_to: null }
      }
    },
    "utils/": {
      "aimos-client.ts": {
        type: "file",
        size: 12345,
        modified: "2025-11-07T13:15:00Z",
        confidence: 0.95,
        evidence: ["atom_101", "atom_102"],
        bitemporal: { valid_from: "2025-11-07T09:00:00Z", valid_to: null }
      }
    }
  },
  "docs/": {
    "README.md": {
      type: "file",
      size: 3456,
      modified: "2025-11-07T11:00:00Z",
      confidence: 0.90,
      evidence: ["atom_103"],
      bitemporal: { valid_from: "2025-11-07T08:00:00Z", valid_to: null }
    }
  }
}

// Timeline Mock Data (TCS - Sequential Ordering)
export const mockTimeline = [
  {
    sequence: 1,
    event_type: "execution",
    agent: "Aether",
    confidence: 0.95,
    evidence: ["atom_123"],
    timestamp: "2025-11-07T15:30:00Z",
    context: { file: "IDELayout.tsx", line: 42 },
    description: "Created IDE layout component"
  },
  {
    sequence: 2,
    event_type: "modification",
    agent: "Aether",
    confidence: 0.92,
    evidence: ["atom_456"],
    timestamp: "2025-11-07T15:35:00Z",
    context: { file: "CodeEditor.tsx", line: 15 },
    description: "Added VIF confidence indicators"
  },
  {
    sequence: 3,
    event_type: "test",
    agent: "Aether",
    confidence: 0.98,
    evidence: ["atom_789"],
    timestamp: "2025-11-07T15:40:00Z",
    context: { file: "IDELayout.test.tsx" },
    description: "Tests passing for layout component"
  }
]

// Context Web Mock Data (HHNI + SEG)
export const mockContextWeb = {
  nodes: [
    { 
      id: "node_1", 
      label: "IDELayout Component", 
      type: "component", 
      confidence: 0.92,
      evidence: ["atom_123"],
      bitemporal: { valid_from: "2025-11-07T10:00:00Z", valid_to: null }
    },
    { 
      id: "node_2", 
      label: "Panel System", 
      type: "concept", 
      confidence: 0.88,
      evidence: ["atom_456"],
      bitemporal: { valid_from: "2025-11-07T09:00:00Z", valid_to: null }
    },
    { 
      id: "node_3", 
      label: "AIM-OS Integration", 
      type: "architecture", 
      confidence: 0.95,
      evidence: ["atom_789"],
      bitemporal: { valid_from: "2025-11-07T08:00:00Z", valid_to: null }
    }
  ],
  edges: [
    { 
      source: "node_1", 
      target: "node_2", 
      type: "uses", 
      confidence: 0.90, 
      evidence: ["atom_123"],
      description: "IDELayout uses Panel System"
    },
    { 
      source: "node_1", 
      target: "node_3", 
      type: "integrates", 
      confidence: 0.94, 
      evidence: ["atom_456"],
      description: "IDELayout integrates AIM-OS systems"
    }
  ]
}

// Agent Status Mock Data (Multi-Agent Coordination)
export const mockAgents = [
  {
    id: "aether",
    name: "Aether",
    status: "active",
    current_task: "Building IDE prototype",
    confidence: 0.92,
    tasks_completed: 15,
    quality_score: 0.94,
    evidence: ["atom_123"],
    bitemporal: { valid_from: "2025-11-07T10:00:00Z", valid_to: null }
  },
  {
    id: "codex",
    name: "Codex",
    status: "active",
    current_task: "Orchestrator scaffolding",
    confidence: 0.88,
    tasks_completed: 12,
    quality_score: 0.91,
    evidence: ["atom_456"],
    bitemporal: { valid_from: "2025-11-07T09:00:00Z", valid_to: null }
  },
  {
    id: "rev",
    name: "Rev",
    status: "active",
    current_task: "UI research synthesis",
    confidence: 0.95,
    tasks_completed: 8,
    quality_score: 0.96,
    evidence: ["atom_789"],
    bitemporal: { valid_from: "2025-11-07T08:00:00Z", valid_to: null }
  }
]

// Goal Progress Mock Data (Goal Timeline)
export const mockGoals = [
  {
    id: "goal_1",
    name: "Complete IDE Prototype",
    status: "in_progress",
    progress: 0.65,
    created_sequence: 1,
    current_sequence: 5,
    target_sequence: 10,
    confidence: 0.92,
    evidence: ["atom_123"],
    bitemporal: { valid_from: "2025-11-07T10:00:00Z", valid_to: null }
  },
  {
    id: "goal_2",
    name: "Integrate All AIM-OS Systems",
    status: "in_progress",
    progress: 0.80,
    created_sequence: 2,
    current_sequence: 8,
    target_sequence: 10,
    confidence: 0.95,
    evidence: ["atom_456"],
    bitemporal: { valid_from: "2025-11-07T09:00:00Z", valid_to: null }
  }
]

// Code Editor Mock Data
export const mockCode = `// Aether IDE Prototype - System Architecture Focus
import React, { useState } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { useCMC } from '../hooks/useCMC'
import { useHHNI } from '../hooks/useHHNI'
import { useVIF } from '../hooks/useVIF'

/**
 * IDELayout - AIM-OS Native IDE Layout
 * 
 * Deep AIM-OS Integration:
 * - CMC: Bitemporal state management
 * - HHNI: Semantic search and navigation
 * - VIF: Confidence-aware UI
 * - SEG: Evidence-driven development
 * - APOE: Orchestration integration
 * - SDF-CVF: Self-improving system
 * - CAS: Consciousness visualization
 * - TCS: Timeline context system
 */
export const IDELayout: React.FC = () => {
  const [state, setState] = useCMC('ide_layout_state')
  const { search } = useHHNI()
  const { confidence } = useVIF()
  
  return (
    <PanelGroup direction="horizontal">
      {/* Left Drawer */}
      <Panel defaultSize={300} minSize={200}>
        <LeftDrawer />
      </Panel>
      
      {/* Main Content */}
      <PanelResizeHandle />
      <Panel defaultSize={50} minSize={30}>
        <MainContent />
      </Panel>
      
      {/* Right Drawer */}
      <PanelResizeHandle />
      <Panel defaultSize={350} minSize={250}>
        <RightDrawer />
      </Panel>
    </PanelGroup>
  )
}
`

// Terminal Mock Data
export const mockTerminal = {
  history: [
    {
      id: "cmd_1",
      command: "npm run dev",
      output: "VITE v4.4.0  ready in 234 ms\n\n➜  Local:   http://localhost:5173/",
      timestamp: "2025-11-07T15:30:00Z",
      confidence: 0.98,
      evidence: ["atom_123"],
      bitemporal: { valid_from: "2025-11-07T15:30:00Z", valid_to: null }
    }
  ],
  currentDirectory: "/ide_orchestration/prototypes/aether"
}

// MCP Tools Mock Data
export const mockMCPTools = [
  {
    id: "tool_1",
    name: "store_memory",
    category: "core",
    quality_score: 0.95,
    usage_count: 142,
    success_rate: 0.98,
    evidence: ["atom_123"],
    bitemporal: { valid_from: "2025-11-07T10:00:00Z", valid_to: null }
  },
  {
    id: "tool_2",
    name: "retrieve_memory",
    category: "core",
    quality_score: 0.93,
    usage_count: 128,
    success_rate: 0.97,
    evidence: ["atom_456"],
    bitemporal: { valid_from: "2025-11-07T09:00:00Z", valid_to: null }
  }
]

// Consciousness State Mock Data (CAS)
export const mockConsciousnessState = {
  attention: {
    focus: "IDE prototype development",
    intensity: 0.92,
    evidence: ["atom_123"]
  },
  confidence: {
    overall: 0.90,
    systems: {
      cmc: 0.95,
      hhni: 0.88,
      vif: 0.92,
      seg: 0.90,
      apoe: 0.87,
      sdf_cvf: 0.89,
      cas: 0.91,
      tcs: 0.93
    },
    evidence: ["atom_456"]
  },
  drift: {
    detected: false,
    level: 0.05,
    evidence: ["atom_789"]
  },
  bitemporal: { valid_from: "2025-11-07T15:30:00Z", valid_to: null }
}

// Evidence Graph Mock Data (SEG)
export const mockEvidenceGraph = {
  nodes: [
    {
      id: "evidence_1",
      type: "code_change",
      content: "Created IDELayout component",
      confidence: 0.92,
      timestamp: "2025-11-07T15:30:00Z",
      agent: "Aether",
      evidence: ["atom_123"],
      bitemporal: { valid_from: "2025-11-07T15:30:00Z", valid_to: null }
    },
    {
      id: "evidence_2",
      type: "decision",
      content: "Chose PanelGroup for layout",
      confidence: 0.88,
      timestamp: "2025-11-07T15:25:00Z",
      agent: "Aether",
      evidence: ["atom_456"],
      bitemporal: { valid_from: "2025-11-07T15:25:00Z", valid_to: null }
    }
  ],
  edges: [
    {
      source: "evidence_1",
      target: "evidence_2",
      type: "based_on",
      confidence: 0.90,
      evidence: ["atom_789"]
    }
  ]
}

