/**
 * PLIx Deep Research Protocol - Data Extraction Form Schema
 * 
 * SEG-ready JSON schema for storing research findings in CMC
 */

export interface PLIxResearchSource {
  /** Unique identifier (auto-generated) */
  id: string;
  
  /** Source title */
  title: string;
  
  /** Publication year */
  year: number;
  
  /** Family classification */
  family: 'planning' | 'workflow' | 'policy' | 'formal' | 'provenance' | 'agent' | 'dev-semantics';
  
  /** Artifact type */
  artifact: 'spec' | 'paper' | 'lib' | 'post' | 'doc';
  
  /** Source URL */
  url: string;
  
  /** Key claims made by the source */
  claims: string[];
  
  /** Model descriptions */
  model: {
    intent: string;
    plan: string;
    policy: string;
    provenance: string;
    confidence: string;
  };
  
  /** Semantic capabilities */
  semantics: {
    types: boolean;
    pre: boolean;
    post: boolean;
    retry: boolean;
    compensate: boolean;
    determinism: 'low' | 'med' | 'high';
  };
  
  /** Interoperability targets */
  interop: string[];
  
  /** Evidence handling style */
  evidence_style: 'none' | 'logs' | 'lineage' | 'first-class';
  
  /** Maturity level */
  maturity: 'research' | 'alpha' | 'prod';
  
  /** Strengths */
  strengths: string[];
  
  /** Limitations */
  limitations: string[];
  
  /** Notable quotes (≤25 words each) */
  notable_quotes: string[];
  
  /** Fit assessment for PLIx */
  fit_for_PLix: 'low' | 'med' | 'high';
  
  /** Concepts to borrow/reuse */
  reuse_targets: string[];
  
  /** Open questions */
  open_questions: string[];
  
  /** Normalized scores (0-5) */
  score: {
    intent: number;      // 0-5: How well does it express typed intents?
    plans: number;        // 0-5: How well does it handle recoverable plans?
    evidence: number;     // 0-5: How well does it model evidence/provenance?
    confidence: number;   // 0-5: How well does it handle confidence gates?
    interop: number;      // 0-5: How interoperable is it?
    ide_fit: number;      // 0-5: How well does it fit IDE context?
  };
  
  /** Metadata */
  metadata: {
    extracted_at: string;
    extracted_by: string;
    tags: string[];
    related_sources: string[]; // IDs of related sources
  };
}

/**
 * Comparison Matrix Entry
 */
export interface PLIxComparisonEntry {
  system: string;
  family: PLIxResearchSource['family'];
  intent_contracts: number;        // 0-5
  recoverable_conditions: number; // 0-5
  evidence_provenance: number;    // 0-5
  policy_gates: number;           // 0-5
  interop_targets: string[];
  ide_fit: number;                // 0-5
  license: string;
  maturity: PLIxResearchSource['maturity'];
  
  /** Additional notes */
  notes?: string;
}

/**
 * Evidence Edge (SEG format)
 */
export interface PLIxEvidenceEdge {
  claim: string;
  evidence: Array<{
    type: 'code' | 'doc' | 'decision' | 'test' | 'diff' | 'lineage';
    path?: string;
    url?: string;
    id?: string;
    content?: string;
  }>;
  confidence: number; // 0-1
  source_id: string;  // Reference to PLIxResearchSource
}

/**
 * Benchmark Run Log (TCS format)
 */
export interface PLIxBenchmarkRun {
  task: string;           // Task ID (e.g., "T1-remember-me")
  run: number;           // Run number
  seed: number;          // Random seed
  planId: string;        // PLIx plan ID
  result: 'success' | 'failure' | 'partial';
  violations: number;   // Number of constraint violations
  latency_ms: number;    // Total execution time
  rework_count: number;  // Number of edits/rollbacks
  evidence_completeness: number; // 0-1: fraction of required evidence captured
  operator_load: number; // Number of human interventions
  auditability_score: number; // 0-1: explainability rubric score
}

