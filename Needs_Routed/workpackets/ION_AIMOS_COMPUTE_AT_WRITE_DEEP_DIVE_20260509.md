# ION ← AIMOS Compute-at-Write Deep Dive

```yaml
workflow_object: aimos_compute_at_write_technical_excavation
created_at: 2026-05-09T23:08:12Z
source_archive: /mnt/data/AIM-ION.zip
source_archive_sha256: 7c77d12a6a8cdbbdf08aced530463ea07f904e6af72b3a24ec6d74ce80b80da5
posture: CONSERVATIVE
source_status: UNTRUSTED_STAGE -> CARTOGRAPHED_WITNESS
accepted_ion_state_changed: false
external_connector_used: false
live_runtime_claimed: false
```

## Executive Finding

The most valuable AIMOS technical seam for ION is **compute-at-write**.

In AIMOS, compute-at-write is not just an indexing optimization. It is a write-plane discipline:

```text
pay the reasoning / classification / provenance / contradiction cost when material enters the system
so later retrieval, continuation, and agent action are cheap, deterministic, and proof-bearing
```

The best ION integration is therefore **not** to import AIMOS wholesale. The best integration is to adapt compute-at-write into ION's project-ingestion, context-graph, receipt, and continuity-export layers.

Strong compression:

```text
AIMOS compute-at-write = governed ingestion + evidence classification + authority classification + contradiction scan + provenance write + downstream invalidation.

ION-compatible form = write-plane law for candidate context objects before they can become retrievable state.
```

## What Compute-at-Write Actually Means

AIMOS makes a deliberate inversion:

| Old pattern | AIMOS pattern |
|---|---|
| compute-at-read | compute-at-write |
| ingest lazily | ingest through disciplined write gates |
| store weakly structured blobs | store classified, linked, provenanced atoms |
| retrieval guesses repeatedly | retrieval consumes already-governed graph objects |
| the model pays the reasoning tax every run | the system pays the reasoning tax once at write time |
| fast to dump, expensive to trust | slower to ingest, cheaper to inherit |

This is directly compatible with ION's law that raw files, memories, summaries, and model outputs are not state. They become useful only after their identity, authority, evidence class, lineage, risk, and receipt path are known.

## The AIMOS Write Plane

The strongest source is the Aether Atlas Book IX write path. It defines a ten-stage governed-write protocol:

```text
W1  Intake
W2  Structural Parsing
W3  Object Classification
W4  Evidence Classification
W5  Authority Classification
W6  Zone Assignment
W7  Contradiction Checking
W8  Verification
W9  Provenance Write
W10 Revision Propagation
```

ION should adopt the shape, not the exact names.

### ION-Adapted Write Plane

```text
ION-W1  Quarantine candidate material
ION-W2  Parse structural shape
ION-W3  Classify object family
ION-W4  Classify evidence posture
ION-W5  Classify authority / risk surface
ION-W6  Assign retrieval zone
ION-W7  Detect contradictions and collisions
ION-W8  Run proof gates / validation gates
ION-W9  Write provenance / receipt candidate
ION-W10 Propagate stale-context and next-packet pressure
```

### Why This Matters

Project ingestion currently says: do not trust a repo just because it has been uploaded.

Compute-at-write gives the missing technical machinery:

```text
upload
-> quarantine
-> object classification
-> evidence and authority classification
-> contradiction scan
-> verification gate
-> provenance write
-> context graph node
-> receipt / export
```

That is exactly the bridge from “external pile” to “ION-manageable state.”

## Related AIMOS Tech That Still Looks Valuable

### 1. CMC / Content Memory Core

**Best useful idea:** append-only memory atoms with bitemporal provenance, snapshots, payload offload, tag indexes, quarantine on corruption, and deterministic snapshot IDs.

ION import target:

```text
minimal atom ledger for receipts, context objects, source witnesses, and project-ingestion nodes
```

Do **not** import CMC as the whole ION memory system yet. Import the atom discipline first:

```yaml
ion_context_atom:
  id: stable identifier
  object_family: file | receipt | decision | claim | source | packet | validation
  content_ref: inline text or artifact path
  source_ref: archive/path/tool/user/session
  evidence_class: observed | sourced | derived | assumed | speculative | contradicted
  authority_class: accepted | candidate | witness | historical | quarantine
  valid_time: what time the claim/object concerns
  transaction_time: when ION recorded it
  provenance_hash: content hash
  supersedes: optional prior atom ids
  receipt_ref: optional receipt
```

### 2. HHNI / Hierarchical Hypergraph Neural Index

**Best useful idea:** retrieval should be budget-aware, multi-resolution, auditable, and able to select context at different densities.

Useful pieces:

```text
coarse retrieval
-> relevance filtering
-> graph/relationship refinement
-> token budget optimization
-> selected context with audit trail
```

ION import target:

```text
context-package compiler with density levels and retrieval audit trail
```

Defer or downscope:

```text
DVNS physics
fractal six-resolution indexing
neural/physics metaphor as core doctrine
```

These may be interesting, but ION should first ship a simpler, measurable context-budget compiler.

### 3. VIF / Verifiable Inference Framework

**Best useful idea:** every important AI-mediated state transition should carry model/provider/config/context/tool/proof witness metadata.

ION import target:

```text
receipt witness extensions
```

Minimal useful witness fields:

```yaml
model_witness:
  carrier: ChatGPT | Codex | local_tool | other
  model_or_executor: observed name if available
  tool_calls: names and outputs, not secrets
  prompt_or_packet_hash: optional
  context_refs: source paths / receipts / atoms
  confidence_posture: not numeric theater unless calibrated
  validation_performed: true | false
  validation_artifacts: paths
  limits: explicit non-claims
```

Also useful is **κ-gating** as an idea:

```text
higher-risk actions require higher proof/confidence and stronger human settlement
```

But ION should not overclaim deterministic replay for hosted models unless prompts, context, tools, versions, and outputs are actually capturable.

### 4. SEG / Semantic Evidence Graph

**Best useful idea:** claims, evidence, contradictions, support, derivation, and time should be graph objects.

ION import target:

```text
evidence / contradiction sidecar graph for context ingestion and settlement
```

Useful relationship families:

```text
supports
contradicts
derives_from
references
duplicates
supersedes
blocks
resolves
depends_on
alternative_to
```

Important maturity note: the inspected SEG implementation appears strongest as a typed graph store. Its contradiction detection is mostly explicit-edge based. ION should not treat it as a finished semantic contradiction reasoner.

### 5. SDF-CVF / Quartet-Quintet Parity

**Best useful idea:** code, docs, tests, traces, and tags should not drift silently.

ION import target:

```text
optional proof gate for high-risk implementation or documentation changes
```

Useful checks:

```text
code has tests
docs match changed code
tests cover public symbols
traces or receipts exist for claimed behavior
semantic tags / names align with implementation
```

Do **not** make global NL-tagging a required core law. It is too heavy as a first ION import. Use it as a proof gate for domains that need it.

### 6. Agent Living Workspace

**Best useful idea:** each long-running agent/domain needs a structured workspace, not just a chat transcript.

The AIMOS 15-section workspace is valuable as a donor pattern:

```text
doctrine
orchestration
rolling context
goals
issues
user
relationships
comms
self
history
mission
evidence
cognitive
boundaries
output
```

ION import target:

```text
optional domain workspace template
```

Do not import the whole structure as mandatory. For ION, a reduced version is likely better:

```text
law / objective / context / evidence / risks / open loops / outputs / receipts
```

### 7. Variable-Density Planning

**Best useful idea:** not every future step deserves the same planning depth.

AIMOS has a good planning density ladder:

```text
Class 0: intent + gate
Class 1: objective + task list + gate
Class 2: task + verification + decisions
Class 3: full blueprint with files/commands/rollback
Class 4: self-modification or high-risk blueprint
```

ION import target:

```text
packet planning depth field
```

Example:

```yaml
packet_density:
  class: 2
  reason: medium-risk doc extraction with bounded artifact output
  upgrade_to_class_3_if:
    - code mutation requested
    - connector mutation requested
    - authority boundary unclear
```

### 8. Project Truth Pack

**Best useful idea:** before rebuilding, extract project truth.

This is one of the most immediately useful AIMOS patterns for ION project ingestion.

ION import target:

```text
project_ingestion_truth_pack template
```

Sections worth porting:

```text
canonical system index
canonical doc index
already-built registry
breakage and drift report
operational definition
operational spine
next bounded task
```

This directly protects ION from one of the most expensive AI failures:

```text
the model fails to locate existing implementation
-> invents a new plan
-> rebuilds or overwrites live intent
```

### 9. Chat Significance / Write-Time Relationship Extraction

**Best useful idea:** relationship edges should be extracted as work is written, not reconstructed months later.

Useful AIMOS edge families:

```text
supports
contradicts
alternative_to
resolves
depends_on
duplicates
references
```

ION import target:

```text
write-time relation typing for receipts, chat-derived commitments, and project-ingestion notes
```

This can power an operator review surface:

```text
new note contradicts prior accepted decision
new code resolves open issue
new plan duplicates existing plan
new source supersedes stale witness
```

### 10. Security / Audit Hardening

Useful ideas:

```text
hash chaining
Merkle-style integrity checks
write-rate limits
propagation-depth limits
LLM-call limits
secret-bearing / deployment-surface classification
quarantine for corrupt or unsafe inputs
```

ION already has the authority vocabulary. AIMOS adds some technical guardrail shapes.

## What Should Not Be Imported First

These are interesting but should not be first-class ION imports now:

```text
full AIMOS identity / consciousness / AGI vocabulary
the whole AIMOS package stack
JOC/BAS browser operating center as ION core
MCP assumptions as required substrate
DVNS/quaternion/physics metaphors as core retrieval law
global NL-tag mandate
autonomous commit or deployment behaviors
old completion percentages and package-count claims
model-provider claims without current validation
```

Reason:

```text
ION needs compact, proof-bearing, operator-settled continuity.
AIMOS contains many valuable mechanisms, but also a lot of architectural sprawl and historical ambition.
```

## Recommended ION Integration Strategy

### Phase A — Spec Extraction

Create one small ION spec:

```text
ION_COMPUTE_AT_WRITE_SPEC.md
```

Purpose:

```text
define what must happen before any imported material becomes retrievable ION context
```

### Phase B — Minimal Object Schema

Create a minimal schema:

```text
ion_context_atom.json
ion_write_receipt.json
ion_relation_edge.json
```

No database required at first. JSONL + manifest is enough.

### Phase C — Project Ingestion Pilot

Use compute-at-write only for project ingestion first:

```text
archive/repo
-> quarantine
-> tree map
-> object atoms
-> evidence/authority classification
-> relation graph
-> truth pack
-> ingestion receipt
```

### Phase D — Receipt Witness Extensions

Extend ION receipts with VIF-like witness metadata:

```text
carrier/model/tool/context/proof/limits
```

### Phase E — Budgeted Context Compiler

Add HHNI-inspired but simpler context packaging:

```text
context objects
-> relevance score
-> authority score
-> recency / dependency score
-> token budget
-> context package + retrieval receipt
```

### Phase F — Optional High-Risk Gates

Only after the above:

```text
SDF-CVF parity gate
SEG contradiction graph
operator settlement UI heatmap
```

## Proposed Extraction Packets

```yaml
- packet_id: CAW_EXTRACT_001_GOVERNED_WRITE_PLANE_SPEC
  goal: Adapt AIMOS W1-W10 into ION write-plane law.
  output: ION_COMPUTE_AT_WRITE_SPEC.md
  priority: highest

- packet_id: CAW_EXTRACT_002_CONTEXT_ATOM_SCHEMA
  goal: Define minimal ION context atom and relation edge schemas.
  output: ion_context_atom.schema.json, ion_relation_edge.schema.json
  priority: high

- packet_id: CAW_EXTRACT_003_RECEIPT_WITNESS_EXTENSIONS
  goal: Import VIF-like witness fields into ION receipts.
  output: ION_RECEIPT_WITNESS_EXTENSION.md
  priority: high

- packet_id: CAW_EXTRACT_004_PROJECT_TRUTH_PACK_TEMPLATE
  goal: Turn AIMOS Project Truth into an ION project-ingestion template.
  output: ION_PROJECT_TRUTH_PACK_TEMPLATE.md
  priority: high

- packet_id: CAW_EXTRACT_005_CONTEXT_BUDGET_COMPILER
  goal: Import the useful HHNI pattern without importing the whole HHNI system.
  output: ION_CONTEXT_BUDGET_COMPILER_SPEC.md
  priority: medium

- packet_id: CAW_EXTRACT_006_EVIDENCE_RELATION_GRAPH
  goal: Define supports/contradicts/supersedes/depends_on/resolves edges for ION.
  output: ION_EVIDENCE_RELATION_GRAPH_SPEC.md
  priority: medium

- packet_id: CAW_EXTRACT_007_PARITY_GATE_PROFILE
  goal: Define when SDF-CVF-like code/docs/tests/traces parity gates apply.
  output: ION_PARITY_GATE_PROFILE.md
  priority: medium
```

## Recommended First Move

The best next move is **CAW_EXTRACT_001_GOVERNED_WRITE_PLANE_SPEC**.

Do not start by porting packages. Start by porting the law:

```text
Before anything becomes retrievable ION context, it must pass a write-plane:
quarantine, parse, classify, evidence-tag, authority-tag, zone, contradiction-check, verify, prove, propagate.
```

That gives ION the valuable part of AIMOS immediately while avoiding package sprawl.

## Source Evidence

| Source | Bytes | SHA-256 prefix |
|---|---:|---|
| `AIM-ION/canon/constitution/AETHER_ATLAS.md` | 60294 | `a33a78bc4302c02a…` |
| `AIM-ION/docs/Aether-OS/AETHER_ATLAS.md` | 60294 | `a33a78bc4302c02a…` |
| `AIM-ION/docs/Aether-OS/AIMOS_CONTEXT_INTEGRATION.md` | 31700 | `f32e7eb8b1d41cf2…` |
| `AIM-ION/docs/Aether-OS/ION_ENGINE_SPEC.md` | 21953 | `c5aa2e6c142bc85b…` |
| `AIM-ION/canon/north_star/NORTH_STAR_V3.md` | 9731 | `652e435953e75f70…` |
| `AIM-ION/canon/constitution/AETHER_CONSTITUTION.md` | 20306 | `0216a2bc378447ec…` |
| `AIM-ION/docs/Aether-OS/AETHER_INTERFACE.md` | 27930 | `393a8922af5810d4…` |
| `AIM-ION/canon/doctrine/AGENT_CONTEXT_ARCHITECTURE.md` | 33931 | `f5565f472ba5acc0…` |
| `AIM-ION/canon/doctrine/VARIABLE_DENSITY_PLANNING.md` | 20415 | `716a94dc1c872caa…` |
| `AIM-ION/docs/Aether-OS/AETHER_INTEGRATION_SPEC.md` | 27517 | `8ed00d809d659a41…` |
| `AIM-ION/north_star_project/chapters/05_cmc/chapter.md` | 24506 | `2e23f7f848ce940d…` |
| `AIM-ION/packages/cmc_service/memory_store.py` | 29760 | `bc38f0f8ef4a7f70…` |
| `AIM-ION/packages/cmc_service/store_io.py` | 4123 | `3d5bb6866ba63a01…` |
| `AIM-ION/packages/cmc_service/models.py` | 6388 | `3d44f01410c8f5ea…` |
| `AIM-ION/packages/hhni/retrieval.py` | 23168 | `fa52a5657257a281…` |
| `AIM-ION/packages/hhni/budget_manager.py` | 11911 | `26727b9354d8c5af…` |
| `AIM-ION/packages/vif/kappa_gate.py` | 12089 | `93bde958c8d0cd97…` |
| `AIM-ION/packages/vif/witness.py` | 8905 | `caf0a390a98e522c…` |
| `AIM-ION/packages/seg/models.py` | 7498 | `d03dc00c8c7e9135…` |
| `AIM-ION/packages/seg/seg_graph.py` | 15107 | `897d02674a900165…` |
| `AIM-ION/packages/sdfcvf/quintet.py` | 30051 | `a8d23b72a872e6a9…` |
| `AIM-ION/packages/timeline_context_system/adaptive_context_dumping.py` | 28782 | `0e6860592d0993d7…` |
| `AIM-ION/ide_orchestration/prototypes/dac/AI_CHAT_SIGNIFICANCE_ENHANCEMENT.md` | 22317 | `63b389496aee673e…` |
| `AIM-ION/PROJECT_TRUTH/README.md` | 1055 | `1e2a5d2911f4c41e…` |
| `AIM-ION/PROJECT_TRUTH/01_canonical_system_index.md` | 7247 | `8ab3f2a54040ae49…` |
| `AIM-ION/PROJECT_TRUTH/03_already_built_registry.md` | 4619 | `216b041259f2a571…` |
| `AIM-ION/PROJECT_TRUTH/04_breakage_and_drift_report.md` | 5003 | `bb56b55f69e99d9b…` |
| `AIM-ION/PROJECT_TRUTH/06_operational_spine.md` | 2374 | `a3e5add11efedcdb…` |
| `AIM-ION/PROJECT_TRUTH/07_next_bounded_task.md` | 2856 | `45a8b88999a0984c…` |
| `AIM-ION/analysis/raw/A Total System of Memory.txt` | 476562 | `b04be5fce408506c…` |
| `AIM-ION/knowledge_architecture/FLOATING_FILES_ORGANIZED/DEVELOPMENT_TOOLS/CONFIGURATION_FILES/core_total_system_memory.txt` | 476561 | `8f50b4a9074d52c3…` |

## Validation And Limits

```yaml
validated:
  archive_readable: true
  relevant_paths_hashed: true
  north_star_and_constitution_sources_inspected: true
  compute_at_write_sources_identified: true
  package_code_sampled:
    - cmc_service
    - hhni
    - vif
    - seg
    - sdfcvf
    - timeline_context_system
not_validated:
  tests_not_run: true
  operation_victus_runtime_source_not_revalidated: true
  live_mcp_or_gateway_not_used: true
  package_claims_not_accepted_as_current_runtime_state: true
```
