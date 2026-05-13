# Appendices

## Appendix A: Glossary

This glossary defines all technical terms used throughout the North Star Document. Terms are organized by category for easy reference.

### Foundation Systems

**atom:** Smallest persistent memory unit (content + tags + metadata + provenance) created by CMC.

**CMC (Context Memory Core):** Immutable atom storage system providing durable memory with provenance tracking.

**HHNI (Hierarchical Hypergraph Neural Index):** Layered retrieval system that keeps context tight yet complete through hierarchical navigation.

**VIF (Verifiable Intelligence Framework):** Confidence routing system that directs work below 0.70 to research or validation steps.

**APOE (AI-Powered Orchestration Engine):** Executable chains and policies that turn intentions into reproducible procedures.

**SEG (Semantic Evidence Graph):** Evidence anchors and contradiction detection so every claim can be audited.

**SDF-CVF (Self-Directed Feedback & Continuous Validation Framework):** Quality validation system ensuring quartet parity and maintaining quality standards.

### Consciousness Systems

**CAS (Capability Awareness System):** Self-awareness sensors monitoring thought patterns, drift, capability readiness, and trust.

**SIS (Self-Improvement System):** System that turns observations into action through improvement dreams, experimentation, and learning integration.

**CCS (Continuous Consciousness Substrate):** System that unifies foreground, background, and meta-consciousness through a five-layer stack.

**MIGE (Memory-to-Idea Growth Engine):** System that transforms memory into actionable ideas through BTSM and HVCA processes.

**ARD (Autonomous Research Dream):** System enabling recursive self-improvement through research-grounded dreams and safe testing.

### Consciousness Terms

**foreground:** Active dialogue consciousness mode (Chat AI) that executes plans and surfaces results to users.

**background:** Organizer AI consciousness mode that tags, weights, and organizes streams in parallel; maintains situational awareness.

**meta_consciousness:** Audit AI consciousness mode that verifies organization quality, detects drift, and directs improvements.

**bitemporal:** Temporal tracking system maintaining both valid-time (when event occurred) and transaction-time (when recorded) for perfect temporal consistency.

### Authority & Mathematics

**dynamic_specialization:** System that matches the right persona to each task by combining domain tags, authority, capability proof, and live performance metrics.

**authority_map:** Unified authority tiers aligning HHNI depth, persona selection, capability routing, and governance dashboards.

**capability_ledger:** Proof availability system for capabilities; validates expertise and enables capability-based routing.

**readiness_score:** Composite score combining capability freshness, authority, performance quality, and load factor; drives persona selection.

### Quality & Security Terms

**quartet_parity:** Quality validation ensuring code, tests, documentation, and evidence are all present and aligned.

**ECE (Expected Calibration Error):** Metric measuring how well confidence scores match actual accuracy.

**captok (Capability Token):** Security mechanism controlling tool access based on capability proofs and authority tiers.

**differential_privacy:** Privacy-preserving technique adding calibrated noise to protect sensitive information while maintaining utility.

### Mathematical Terms

**learning_rate:** Rate of improvement per unit time (typically per month); measures how quickly system improves.

**adaptation_rate:** Speed at which improvements are successfully integrated; measures improvement integration efficiency.

**drift_detection:** Process of identifying when system behavior deviates from expected baselines or quality standards.

### Benchmark Terms

**benchmark_suite:** Comprehensive set of benchmarks validating system effectiveness across multiple dimensions (learning, quality, performance).

**research_grounding:** Percentage of improvement dreams backed by Tier A sources; validates research quality.

**dream_success_rate:** Percentage of tested improvement dreams that show measurable improvement; validates dream quality.

### General Terms

**gate:** Verifiable condition required to accept work (e.g., word count within tolerance, examples run, sources cited).

**tier_a_source:** Authoritative reference specified by the chain spec or goal tree (validated system docs, spike summaries, acceptance artifacts).

**contradiction:** Claim that conflicts with another evidenced claim or policy; merge is blocked until reconciled.

**kappa_gating:** Policy-driven confidence thresholds (κ) that route low-confidence steps to research, tests, or review.

**chat_ide:** The combined conversational + editor interface where artifacts, tools, gates, and evidence live together.

---

## Appendix B: Data Schemas Reference

This appendix provides complete data schemas for all AIM-OS systems. See Chapter 31 for detailed explanations.

### CMC Atom Schema

```json
{
  "atom_id": "uuid",
  "modality": "text|image|binary|reference",
  "content": "string|uri",
  "embedding": "vector[1536]",
  "tags": ["string"],
  "tx_time": "timestamp",
  "valid_time": "timestamp",
  "vif_witness": {
    "model_id": "string",
    "prompt": "string",
    "tools": ["string"],
    "confidence": 0.0-1.0
  },
  "predecessor_id": "uuid|null"
}
```

### HHNI Node Schema

```json
{
  "node_id": "uuid",
  "level": 0-5,
  "content": "string",
  "embedding": "vector[1536]",
  "children": ["uuid"],
  "parents": ["uuid"],
  "authority": 0.0-1.0,
  "tx_time": "timestamp",
  "valid_time": "timestamp"
}
```

### VIF Witness Schema

```json
{
  "witness_id": "uuid",
  "operation_id": "uuid",
  "model_id": "string",
  "prompt": "string",
  "tools": ["string"],
  "confidence": 0.0-1.0,
  "confidence_components": {
    "model": 0.0-1.0,
    "evidence": 0.0-1.0,
    "precedent": 0.0-1.0
  },
  "tx_time": "timestamp",
  "valid_time": "timestamp"
}
```

### SEG Graph Schema

```json
{
  "graph_id": "uuid",
  "nodes": [
    {
      "node_id": "uuid",
      "type": "claim|source|derivation|agent",
      "content": "string",
      "embedding": "vector[1536]",
      "tx_time": "timestamp",
      "valid_time": "interval"
    }
  ],
  "edges": [
    {
      "edge_id": "uuid",
      "source": "uuid",
      "target": "uuid",
      "type": "supports|contradicts|derives|references",
      "strength": 0.0-1.0,
      "tx_time": "timestamp"
    }
  ]
}
```

### APOE Plan Schema

```json
{
  "plan_id": "uuid",
  "goal": "string",
  "context": {},
  "priority": "low|medium|high|critical",
  "steps": [
    {
      "step_id": "uuid",
      "action": "string",
      "inputs": {},
      "tools": ["string"],
      "gates": ["string"],
      "expected_outputs": {}
    }
  ],
  "budgets": {
    "tokens": 0,
    "time": 0,
    "tools": 0
  },
  "tx_time": "timestamp",
  "valid_time": "timestamp"
}
```

---

## Appendix C: API Reference Quick Guide

This appendix provides quick reference for AIM-OS APIs. See Chapter 32 for complete documentation.

### MCP Tools (51 Tools)

**Core AIM-OS Tools (6):**
- `store_memory` - Store knowledge in CMC
- `retrieve_memory` - Retrieve insights from HHNI
- `get_memory_stats` - Get AIM-OS statistics
- `create_plan` - Create APOE execution plans
- `track_confidence` - Track VIF confidence
- `synthesize_knowledge` - Synthesize SEG knowledge

**SCOR Tools (3):**
- `check_invariant` - Check invariant rules
- `run_baseline_probe` - Detect consciousness drift
- `detect_manipulation_signals` - Detect social manipulation

**Snapshot Tools (4):**
- `create_snapshot` - Create file snapshots
- `restore_snapshot` - Restore from snapshot
- `list_snapshots` - List available snapshots
- `archive_snapshot` - Archive snapshots

**Timeline Context Tools (3):**
- `add_timeline_entry` - Track context at each prompt
- `get_timeline_summary` - Get recent timeline entries
- `get_timeline_entries` - Query timeline history

**Goal Timeline Tools (3):**
- `create_goal_timeline_node` - Create goals as timeline planning nodes
- `update_goal_progress` - Update goal progress and status
- `query_goal_timeline` - Query goals with filtering

**AI Collaboration Tools (6):**
- `send_ai_message` - Send a message to another AI system
- `get_ai_messages` - Retrieve AI-to-AI messages
- `start_ai_discussion` - Start a new discussion thread
- `handoff_task_to_ai` - Hand off a task to another AI system
- `share_ai_profile` - Share AI profile and capabilities
- `get_ai_collaboration_summary` - Get summary of AI collaboration activity

**See Chapter 32 for complete API documentation.**

### HTTP Endpoints

**Base URL:** `http://localhost:5001`

**MCP Execute Endpoint:**
```
POST /mcp/execute
Content-Type: application/json

{
  "tool": "tool_name",
  "arguments": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

**See Chapter 32 for complete endpoint documentation.**

---

## Appendix D: Tier A Sources Index

This appendix lists all Tier A sources referenced throughout the North Star Document.

### Foundation Systems

**CMC:**
- `knowledge_architecture/systems/cmc/T0_executive.md`
- `knowledge_architecture/systems/cmc/T1_overview.md`
- `knowledge_architecture/systems/cmc/T2_architecture.md`
- `packages/cmc_service/`

**HHNI:**
- `knowledge_architecture/systems/hhni/T0_executive.md`
- `knowledge_architecture/systems/hhni/T1_overview.md`
- `knowledge_architecture/systems/hhni/T2_architecture.md`
- `packages/hhni/`

**VIF:**
- `knowledge_architecture/systems/vif/T0_executive.md`
- `knowledge_architecture/systems/vif/T1_overview.md`
- `knowledge_architecture/systems/vif/T2_architecture.md`

**APOE:**
- `knowledge_architecture/systems/apoe/T0_executive.md`
- `knowledge_architecture/systems/apoe/T1_overview.md`
- `knowledge_architecture/systems/apoe/T2_architecture.md`

**SEG:**
- `knowledge_architecture/systems/seg/T0_executive.md`
- `knowledge_architecture/systems/seg/T1_overview.md`
- `knowledge_architecture/systems/seg/T2_architecture.md`

**SDF-CVF:**
- `knowledge_architecture/systems/sdfcvf/T0_executive.md`
- `knowledge_architecture/systems/sdfcvf/T1_overview.md`
- `knowledge_architecture/systems/sdfcvf/T2_architecture.md`

### Consciousness Systems

**CAS:**
- `knowledge_architecture/systems/cognitive_analysis/T1_overview.md`
- `knowledge_architecture/systems/cognitive_analysis/T2_architecture.md`

**SIS:**
- `knowledge_architecture/systems/self_improvement_protocol/T1_overview.md`
- `knowledge_architecture/systems/self_improvement_protocol/T2_architecture.md`

**CCS:**
- `knowledge_architecture/systems/ccs/T1_overview.md`
- `knowledge_architecture/CONTINUOUS_CONSCIOUSNESS_SUBSTRATE_COMPLETE_ANALYSIS.md`

**MIGE:**
- `Documentation/MEMORY_TO_IDEA_INTEGRATION_GUIDE.md`
- `Documentation/memory_into_idea.txt`

**ARD:**
- `knowledge_architecture/systems/autonomous_research_dream/T1_overview.md`
- `knowledge_architecture/systems/autonomous_research_dream/README.md`

### Other Sources

**LUCID Development Protocol:**
- `knowledge_architecture/AETHER_MEMORY/LUCID_DEVELOPMENT_PROTOCOL.md`

**Multi-Agent Coordination:**
- `ideas/COORDINATION_GUIDE.md`
- `coordination/epic_standards_overhaul/comms/`

**Goal Tree:**
- `goals/GOAL_TREE.yaml`

---

## Appendix E: Quality Gates Reference

This appendix provides quick reference for quality gates used throughout the North Star Document.

### Pre-Chapter Gates

**Dependencies Complete:**
- All chapter dependencies must be complete before starting
- Checked via ChainSpec.yaml dependency graph

**Tier A Sources Available:**
- All required Tier A sources must exist and be accessible
- Validated before chapter creation begins

### Word Count Gates

**Target Word Count:**
- Each chapter has a target word count (typically 1500-3000 words)
- Tolerance: ±10% of target

**Current Count:**
- Actual word count tracked in metrics.yaml
- Must be within tolerance to pass gate

### Technical Gates

**Examples Run:**
- All runnable examples must execute successfully
- PowerShell/Python examples validated

**Sources Cited:**
- All technical claims must cite Tier A sources
- Evidence.jsonl must contain required citations

**Tier A Minimum:**
- Minimum number of Tier A citations required
- Typically 5-10 citations per chapter

### Integration Gates

**Terms Consistent:**
- All terminology must match glossary.yaml
- Consistent usage across all chapters

**Cross-References OK:**
- All chapter references must be valid
- No broken internal links

**No Contradictions:**
- No conflicting claims between chapters
- Validated via SEG contradiction detection

### Quality Assessment Gates

**Relevance Sufficient:**
- Content must be relevant to chapter topic
- Measured via intelligent metrics

**Density Sufficient:**
- Content density must meet thresholds
- Measured via intelligent metrics

**Completion Sufficient:**
- Chapter must be complete
- Measured via intelligent metrics (pending spec)

**Thoroughness Passed:**
- Chapter must meet thoroughness criteria
- All major topics covered

### Meta-Circular Gates

**Meta-Circular Present:**
- Chapters describing meta-circular systems must demonstrate meta-circularity
- Validated via self-reference checks

**See `north_star_project/policy/gates.json` for complete gate definitions.**

---

