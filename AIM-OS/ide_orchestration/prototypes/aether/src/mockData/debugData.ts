// Debug Infrastructure Mock Data - AIM-OS Native Debugging
// Debugging infrastructure built in tandem with application

// Debug Console Mock Data (CMC-backed logs)
export const mockDebugConsole = [
  {
    id: 'debug_1',
    level: 'log',
    source: 'IDELayout',
    message: 'Component mounted successfully',
    timestamp: '2025-11-07T15:30:00Z',
    confidence: 0.95,
    evidence: ['atom_123'],
    context: { component: 'AetherIDELayout', props: {} },
    bitemporal: { valid_from: '2025-11-07T15:30:00Z', valid_to: null }
  },
  {
    id: 'debug_2',
    level: 'info',
    source: 'CMC',
    message: 'Atom created: file_operation',
    timestamp: '2025-11-07T15:30:05Z',
    confidence: 0.98,
    evidence: ['atom_124'],
    context: { atom_id: 'atom_124', operation: 'file_read', file: 'IDELayout.tsx' },
    bitemporal: { valid_from: '2025-11-07T15:30:05Z', valid_to: null }
  },
  {
    id: 'debug_3',
    level: 'warn',
    source: 'VIF',
    message: 'Confidence below threshold: 0.65',
    timestamp: '2025-11-07T15:30:10Z',
    confidence: 0.65,
    evidence: ['atom_125'],
    context: { threshold: 0.70, system: 'HHNI', operation: 'semantic_search' },
    bitemporal: { valid_from: '2025-11-07T15:30:10Z', valid_to: null }
  },
  {
    id: 'debug_4',
    level: 'error',
    source: 'APOE',
    message: 'Task dependency resolution failed',
    timestamp: '2025-11-07T15:30:15Z',
    confidence: 0.88,
    evidence: ['atom_126'],
    context: { task_id: 'task_42', dependency: 'task_41', reason: 'circular_dependency' },
    bitemporal: { valid_from: '2025-11-07T15:30:15Z', valid_to: null }
  }
]

// Debug Logs by System (CMC-backed)
export const mockDebugLogsBySystem = {
  CMC: [
    { level: 'log', message: 'Atom stored: file_operation', count: 142, confidence: 0.95 },
    { level: 'info', message: 'Bitemporal tag applied', count: 89, confidence: 0.98 },
    { level: 'warn', message: 'Evidence link missing', count: 3, confidence: 0.75 }
  ],
  HHNI: [
    { level: 'log', message: 'Semantic search executed', count: 234, confidence: 0.92 },
    { level: 'info', message: 'Index updated', count: 56, confidence: 0.95 },
    { level: 'warn', message: 'Low confidence result', count: 12, confidence: 0.68 }
  ],
  VIF: [
    { level: 'log', message: 'Confidence calculated', count: 456, confidence: 0.94 },
    { level: 'info', message: 'Quality gate passed', count: 389, confidence: 0.97 },
    { level: 'warn', message: 'Confidence below threshold', count: 23, confidence: 0.65 }
  ],
  SEG: [
    { level: 'log', message: 'Evidence node created', count: 178, confidence: 0.93 },
    { level: 'info', message: 'Contradiction detected', count: 5, confidence: 0.88 },
    { level: 'warn', message: 'Evidence link broken', count: 2, confidence: 0.70 }
  ],
  APOE: [
    { level: 'log', message: 'Task scheduled', count: 234, confidence: 0.91 },
    { level: 'info', message: 'Agent assigned', count: 189, confidence: 0.94 },
    { level: 'error', message: 'Dependency resolution failed', count: 1, confidence: 0.88 }
  ],
  SDF_CVF: [
    { level: 'log', message: 'Quality metric recorded', count: 312, confidence: 0.92 },
    { level: 'info', message: 'Improvement suggestion generated', count: 45, confidence: 0.89 },
    { level: 'warn', message: 'Validation loop timeout', count: 3, confidence: 0.75 }
  ],
  CAS: [
    { level: 'log', message: 'Consciousness metric updated', count: 567, confidence: 0.95 },
    { level: 'info', message: 'Attention focus changed', count: 234, confidence: 0.93 },
    { level: 'warn', message: 'Cognitive drift detected', count: 2, confidence: 0.82 }
  ],
  TCS: [
    { level: 'log', message: 'Timeline event recorded', count: 1234, confidence: 0.96 },
    { level: 'info', message: 'Context restored', count: 89, confidence: 0.94 },
    { level: 'warn', message: 'Sequence gap detected', count: 1, confidence: 0.78 }
  ]
}

// Debug Analysis (HHNI-powered)
export const mockDebugAnalysis = {
  patterns: [
    {
      pattern: 'High confidence operations',
      count: 2345,
      systems: ['CMC', 'TCS', 'CAS'],
      confidence: 0.94,
      evidence: ['atom_200', 'atom_201']
    },
    {
      pattern: 'Low confidence warnings',
      count: 45,
      systems: ['VIF', 'HHNI'],
      confidence: 0.68,
      evidence: ['atom_202', 'atom_203']
    },
    {
      pattern: 'Error patterns',
      count: 3,
      systems: ['APOE'],
      confidence: 0.88,
      evidence: ['atom_204']
    }
  ],
  insights: [
    {
      insight: 'CMC operations have highest confidence',
      confidence: 0.95,
      evidence: ['atom_205'],
      recommendation: 'Continue CMC-first approach'
    },
    {
      insight: 'VIF warnings correlate with HHNI low confidence',
      confidence: 0.87,
      evidence: ['atom_206'],
      recommendation: 'Investigate HHNI confidence calibration'
    }
  ]
}

// Debug Infrastructure Status (Built-in)
export const mockDebugInfrastructure = {
  logging: {
    enabled: true,
    level: 'debug',
    destinations: ['CMC', 'Console', 'File'],
    rotation: 'daily',
    retention: '30 days',
    confidence: 0.98
  },
  analysis: {
    enabled: true,
    real_time: true,
    pattern_detection: true,
    insight_generation: true,
    confidence: 0.92
  },
  integration: {
    cmc: { enabled: true, all_logs_stored: true, bitemporal: true },
    hhni: { enabled: true, semantic_analysis: true, pattern_detection: true },
    vif: { enabled: true, confidence_tracking: true, validation: true },
    seg: { enabled: true, evidence_trails: true, contradiction_detection: true },
    apoe: { enabled: true, task_debugging: true, orchestration_logs: true },
    sdf_cvf: { enabled: true, quality_tracking: true, improvement_logs: true },
    cas: { enabled: true, consciousness_debugging: true, drift_logs: true },
    tcs: { enabled: true, timeline_debugging: true, context_logs: true }
  }
}

// Debug Console Filters
export const mockDebugFilters = {
  levels: ['log', 'info', 'warn', 'error', 'debug'],
  sources: ['CMC', 'HHNI', 'VIF', 'SEG', 'APOE', 'SDF-CVF', 'CAS', 'TCS', 'IDELayout', 'CodeEditor'],
  timeRange: { start: '2025-11-07T00:00:00Z', end: '2025-11-07T23:59:59Z' },
  confidenceRange: { min: 0.0, max: 1.0 }
}

