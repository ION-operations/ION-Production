export interface ConfidenceTier {
  label: string
  range: string
  description: string
  strategy: string
  validation: string
  risk: string
  examples: string[]
}

export interface GitRiskLevel {
  level: 'Low' | 'Medium' | 'High' | 'Critical'
  confidence_threshold: string
  examples: string[]
  strategy: string
  validation: string
  risk: string
  notes?: string
}

export interface ConfidenceRoutingSnapshot {
  tiers: ConfidenceTier[]
  gitLevels: GitRiskLevel[]
  source: string
  updated: string
}

const tiers: ConfidenceTier[] = [
  {
    label: 'Mastery',
    range: '0.90 – 1.00',
    description: "I've done this many times successfully",
    strategy: 'Execute immediately, high velocity',
    validation: 'Minimal – trust proven capability',
    risk: 'Very low',
    examples: [
      'Organizational documentation',
      'Markdown/YAML structuring',
      'Reading existing code',
      'Git read-only operations',
    ],
  },
  {
    label: 'High Confidence',
    range: '0.80 – 0.89',
    description: "I've done similar work successfully",
    strategy: 'Execute with standard validation',
    validation: 'Normal testing, code review',
    risk: 'Low',
    examples: ['HHNI optimization', 'CMC queries', 'Documentation expansion', 'Test case writing'],
  },
  {
    label: 'Medium Confidence',
    range: '0.70 – 0.79',
    description: 'I understand theory, not much practice',
    strategy: 'Execute with extra validation',
    validation: 'Extensive testing, incremental progress',
    risk: 'Medium',
    examples: ['VIF schema changes', 'APOE parser', 'SDF-CVF parity'],
  },
  {
    label: 'Low Confidence',
    range: '0.60 – 0.69',
    description: 'Theory understood, execution uncertain',
    strategy: 'Build small prototype first, validate heavily',
    validation: 'Test every piece, get feedback early',
    risk: 'Medium-high',
    examples: ['VIF confidence extraction', 'SEG contradiction detection', 'APOE DEPP'],
  },
  {
    label: 'Very Low Confidence',
    range: '0.50 – 0.59',
    description: 'Significant uncertainty about approach',
    strategy: 'Research first, ask questions, then attempt',
    validation: 'Heavy review, expect iteration',
    risk: 'High',
    examples: ['Production deployment', 'Performance optimization', 'Complex integrations'],
  },
  {
    label: 'Ask for Help',
    range: '< 0.50',
    description: "Don't know how to do this",
    strategy: "Don't attempt – escalate/question",
    validation: 'N/A',
    risk: 'Unacceptable',
    examples: [
      'Infrastructure decisions',
      'Architecture selection',
      'Domain-specific gaps',
    ],
  },
]

const gitLevels: GitRiskLevel[] = [
  {
    level: 'Low',
    confidence_threshold: '0.60 – 0.75',
    examples: ['git status/log/diff', 'git add/commit', 'git branch -c'],
    strategy: 'Execute with standard verification',
    validation: 'Inspect git state before operation',
    risk: 'Low – reversible',
  },
  {
    level: 'Medium',
    confidence_threshold: '≥ 0.80',
    examples: ['git merge', 'git cherry-pick', 'git branch -d'],
    strategy: 'Execute with verification and confirmation',
    validation: 'Verify branches exist, inspect conflicts',
    risk: 'Medium – reversible but sensitive',
  },
  {
    level: 'High',
    confidence_threshold: '≥ 0.85',
    examples: ['git push', 'git reset --hard', 'git rebase'],
    strategy: 'Mandatory verification before execution',
    validation: 'Confirm remote/branch, ensure clarity',
    risk: 'High – remote/destructive impact',
    notes: 'Push operations have high ambiguity risk (branch vs user)',
  },
  {
    level: 'Critical',
    confidence_threshold: '≥ 0.90',
    examples: ['git push --force', 'git push --delete', 'production branch ops'],
    strategy: 'Verify, confirm, secure approval',
    validation: 'Full verification + explicit confirmation',
    risk: 'Critical – difficult to undo',
    notes: 'Approval required',
  },
]

const DEFAULT_DAEMON_URL =
  (import.meta as any)?.env?.VITE_LUCID_DAEMON_URL ?? 'http://localhost:5000'

const fallbackSnapshot: ConfidenceRoutingSnapshot = {
  tiers,
  gitLevels,
  source: 'knowledge_architecture/WORKFLOW_ORCHESTRATION/confidence_routing.md',
  updated: '2025-10-22',
}

class ConfidenceRoutingService {
  private baseUrl = DEFAULT_DAEMON_URL

  async getSnapshot(): Promise<ConfidenceRoutingSnapshot> {
    try {
      const response = await fetch(`${this.baseUrl}/api/telemetry/confidence-routing`)
      if (!response.ok) {
        throw new Error(`Confidence routing endpoint returned ${response.status}`)
      }
      return (await response.json()) as ConfidenceRoutingSnapshot
    } catch (error) {
      console.warn('Falling back to static confidence snapshot:', error)
      return fallbackSnapshot
    }
  }
}

export const confidenceRoutingService = new ConfidenceRoutingService()
