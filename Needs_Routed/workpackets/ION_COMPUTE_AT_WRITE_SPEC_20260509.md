# ION Compute-at-Write Write-Plane Spec

```yaml
workflow_object: CAW_EXTRACT_001_GOVERNED_WRITE_PLANE_SPEC
created_at: 2026-05-09T23:35:10Z
source_archive: /mnt/data/AIM-ION.zip
source_archive_sha256: 7c77d12a6a8cdbbdf08aced530463ea07f904e6af72b3a24ec6d74ce80b80da5
posture: CONSERVATIVE
source_status: UNTRUSTED_STAGE -> CARTOGRAPHED_WITNESS
accepted_ion_state_changed: false
external_connector_used: false
live_runtime_claimed: false
```

## 0. Executive Decision

AIMOS compute-at-write should be extracted into ION as **write-plane law**.

It should not be imported as an AIMOS memory stack, consciousness stack, package stack, or runtime claim.

The ION-compatible extraction is:

```text
Before material becomes retrievable ION context, it must be written through a governed plane:
quarantine -> parse -> classify -> evidence tag -> authority/risk tag -> retrieval zone
-> contradiction/collision scan -> proof gate -> provenance receipt -> stale-context propagation.
```

In shorter form:

```text
ION should pay the trust cost at write time, so future retrieval is cheaper, safer, and proof-bearing.
```

The strongest AIMOS source is `AIM-ION/canon/constitution/AETHER_ATLAS.md`, Book IX, which defines the inversion from compute-at-read to compute-at-write and names the ten-stage governed write path. This spec adapts that pattern into ION language and rejects AIMOS-specific overclaims.

---

## 1. Why This Matters For ION

ION already has the law:

```text
AI output is not state.
A file is not context because it exists.
A project is not ION-manageable because it was uploaded.
```

Compute-at-write gives the missing technical spine behind that law.

Without a write plane, ION can say:

```text
Do not trust raw input.
```

With a write plane, ION can say:

```text
Here is exactly how raw input becomes a candidate graph object, what proof it needs,
which retrieval zone it belongs to, and what future packets must inherit or avoid.
```

This is the bridge between Section 44 project ingestion and practical context-graph formation.

---

## 2. Source Posture

AIMOS material is treated as donor evidence, not current ION canon.

| Source class | Status in this pass |
|---|---|
| `AIM-ION.zip` | Untrusted archive, locally inspected |
| North Star V3 | Strong donor witness for evidence-gated production posture |
| Aether Atlas Book IX | Strong donor witness for compute-at-write write path |
| Aether Interface | Strong donor witness for capsule/checkpoint/receipt/atom schemas |
| CMC / HHNI / SEG / VIF / SDF-CVF packages | Code witness; not executed or accepted |
| AIMOS runtime claims | Witnessed claims only; not live-proven here |
| AIMOS consciousness / AGI vocabulary | Not imported into ION doctrine |

Non-claim:

```text
This spec does not prove AIMOS runtime health.
This spec does not prove CMC/HHNI/SEG/VIF/SDF-CVF test pass.
This spec does not promote AIMOS to ION canon.
```

---

## 3. Governing Principle

### 3.1 Old Pattern: Compute-at-Read

```text
raw material is stored quickly
retrieval repeatedly guesses what matters
the model repeatedly reconstructs provenance and authority
contradictions are noticed late
future workers inherit loose summaries
```

### 3.2 ION Pattern: Compute-at-Write

```text
material enters through quarantine
identity and structure are classified once
authority and evidence are tagged before retrieval
relationships and contradictions are recorded early
proof status is visible
future retrieval consumes governed graph objects, not blobs
```

### 3.3 Practical Law

```text
No object enters ACTIVE_CONTEXT until its write-plane receipt exists.
No object enters TRUSTED_RETRIEVAL until its evidence, authority, lineage, and zone are known.
No object supersedes another object without a propagation note.
No contradiction is silently compressed away.
```

---

## 4. ION Write-Plane State Machine

```text
UNTRUSTED_STAGE
  -> CANDIDATE_OBJECT
  -> CARTOGRAPHED_WITNESS
  -> PROVISIONAL_CONTEXT
  -> APPROVED_CONTEXT
  -> ACTIVE_RETRIEVAL
```

Side exits:

```text
QUARANTINED
SUPERSEDED
STALE_PENDING_REVIEW
REJECTED_WITNESS
SECRET_LOCKED
AUTHORITY_BLOCKED
PROOF_BLOCKED
```

### 4.1 State Definitions

| State | Meaning | May retrieval use it? | May future work inherit it? |
|---|---|---:|---:|
| `UNTRUSTED_STAGE` | Raw uploaded/imported material | No | No |
| `CANDIDATE_OBJECT` | Parsed enough to discuss | Only by explicit path | No |
| `CARTOGRAPHED_WITNESS` | Described, hashed, classified as witness | Yes, as witness | Yes, as witness only |
| `PROVISIONAL_CONTEXT` | Useful for a bounded packet, but not accepted | Yes, scoped | Yes, with warning |
| `APPROVED_CONTEXT` | Accepted for a domain/template | Yes | Yes |
| `ACTIVE_RETRIEVAL` | Indexed for normal context assembly | Yes | Yes |
| `QUARANTINED` | Dangerous/malformed/contradictory/secret-bearing | No, except audit | No |
| `SUPERSEDED` | Replaced by a newer object | Only lineage | Only lineage |
| `STALE_PENDING_REVIEW` | Downstream object touched by W10 propagation | Scoped warning | No new acceptance |
| `REJECTED_WITNESS` | Explicitly non-adopted | Only for audit | No |
| `SECRET_LOCKED` | Secret-bearing content; do not expose | No ordinary retrieval | No chat export |
| `AUTHORITY_BLOCKED` | Cannot classify authority | No | No |
| `PROOF_BLOCKED` | Needs validation | Scoped only | No accepted inheritance |

---

## 5. The Ten ION Write Stages

AIMOS names W1-W10. ION should preserve the shape but use ION-native names and authority boundaries.

| Stage | AIMOS donor | ION stage | Output |
|---|---|---|---|
| W1 | Intake | Quarantine Candidate Material | `write_intent` + staged object |
| W2 | Structural Parsing | Parse Structural Shape | `structure_descriptor` |
| W3 | Object Classification | Classify Object Family | `object_family` |
| W4 | Evidence Classification | Classify Evidence Posture | `evidence_posture` |
| W5 | Authority Classification | Classify Authority / Risk | `authority_class` + `risk_surface` |
| W6 | Zone Assignment | Assign Retrieval Zone | `retrieval_zone` |
| W7 | Contradiction Checking | Detect Contradictions / Collisions | `relation_edges` + `contradiction_records` |
| W8 | Verification | Run Proof Gates | `verification_witness` |
| W9 | Provenance Write | Write Receipt Candidate | `write_receipt` |
| W10 | Revision Propagation | Propagate Stale-Context Pressure | `propagation_notice` + next packet |

---

## 6. Stage Contracts

### ION-W1 — Quarantine Candidate Material

Purpose:

```text
Receive material without granting it context authority.
```

Inputs:

```yaml
source:
  kind: upload | repo | chat | note | tool_return | model_output | web_source | connector_return
  path_or_ref: string
  received_at: ISO-8601
  received_by: carrier/session
  declared_intent: string
```

Required actions:

```text
- Preserve raw source reference.
- Assign staging ID.
- Hash local bytes when possible.
- Detect archive/root/path hazards.
- Detect likely secret-bearing content.
- Prevent mutation of source material.
```

Outputs:

```yaml
status: UNTRUSTED_STAGE
write_intent_id: WRI-...
staging_ref: ...
source_hash: sha256 | null
secret_scan_status: clean | suspected | not_run
```

Failure exits:

```text
SECRET_LOCKED, QUARANTINED, AUTHORITY_BLOCKED
```

---

### ION-W2 — Parse Structural Shape

Purpose:

```text
Map what exists before claiming what it means.
```

Parsing regimes:

| Material | Structural parser |
|---|---|
| Repo/archive | file tree, root markers, package markers, CI markers |
| Code | AST / symbols / imports / tests / configs |
| Markdown/docs | headings, front matter, links, claims, diagrams |
| Chat/transcript | speakers, turns, decisions, tasks, commitments |
| Tool return | command, args, return code, stdout/stderr, artifact paths |
| Model output | proposal type, claims, assumptions, intended state delta |
| External source | title, author/org, date, URL/ref, retrieval timestamp |

Outputs:

```yaml
structure_descriptor:
  type: code_file | doc_file | archive | transcript | receipt | tool_return | model_output | dataset | unknown
  size: ...
  parsed_units:
    - id: ...
      kind: heading | function | class | decision | claim | task | evidence | config | test
```

Failure exits:

```text
QUARANTINED if malformed root or path hazard
PROOF_BLOCKED if parser confidence is too low
```

---

### ION-W3 — Classify Object Family

Purpose:

```text
Identify what kind of ION graph object this candidate may become.
```

Candidate families:

```yaml
object_family:
  - SOURCE_WITNESS
  - CONTEXT_ATOM
  - RECEIPT
  - TEMPLATE
  - DOMAIN_DESCRIPTOR
  - PACKET
  - DECISION
  - CLAIM
  - TASK
  - COMMITMENT
  - CODE_ARTIFACT
  - TEST_ARTIFACT
  - CONFIG_ARTIFACT
  - VALIDATION_ARTIFACT
  - EXPORT_BUNDLE
  - RISK_RECORD
  - SECRET_RECORD
  - UNKNOWN
```

Rule:

```text
UNKNOWN may not enter ACTIVE_RETRIEVAL.
```

---

### ION-W4 — Classify Evidence Posture

Purpose:

```text
Prevent confident language from outranking actual proof.
```

Recommended enum:

```yaml
evidence_posture:
  OBSERVED: directly observed in file/tool output
  EXECUTED: command/test/action actually run in this session
  SOURCED: supported by cited external/source material
  DERIVED: inferred from inspected material
  CLAIMED: asserted by a document or agent but not independently proven
  ASSUMED: operating assumption
  SPECULATIVE: future/idea/dreamspace
  CONTRADICTED: active conflict exists
  DEPRECATED: known old/superseded
  UNKNOWN: insufficient evidence
```

Promotion rule:

```text
CLAIMED may become SOURCED only with source proof.
SOURCED may become EXECUTED only with local execution proof.
DERIVED must remain marked as inference.
SPECULATIVE may not govern implementation.
CONTRADICTED may not enter active context except as a blocker.
```

---

### ION-W5 — Classify Authority And Risk

Purpose:

```text
Decide what the object may influence and what gates it needs.
```

ION authority classes:

```yaml
authority_class:
  HUMAN_DIRECTIVE: explicit current operator instruction
  ACCEPTED_RECEIPT: prior accepted workflow receipt
  CURRENT_CANON: accepted ION law/doc/template
  RUNTIME_PROOF: current validated tool/test/connector result
  PACKAGE_SOURCE: source material from mounted package
  PROJECT_SOURCE: source material from ingested project
  HISTORICAL_WITNESS: lineage evidence, not governing
  EXTERNAL_SOURCE: web/paper/vendor/source witness
  CANDIDATE_AI_OUTPUT: model-produced proposal
  UNKNOWN_AUTHORITY: cannot classify
```

Risk surfaces:

```yaml
risk_surface:
  - READ_ONLY
  - SECRET_BEARING
  - DEPLOYMENT_SURFACE
  - PRODUCTION_AUTHORITY
  - CONNECTOR_MUTATION
  - FINANCIAL
  - LEGAL
  - MEDICAL
  - SECURITY
  - USER_DATA
  - PUBLIC_CLAIM
  - LOW_RISK_DOCS
```

Authority rule:

```text
CANDIDATE_AI_OUTPUT cannot become CURRENT_CANON without settlement.
HISTORICAL_WITNESS cannot override CURRENT_CANON.
PACKAGE_SOURCE does not imply accepted state.
RUNTIME_PROOF outranks stale documentation only for the scoped runtime claim.
SECRET_BEARING cannot enter ordinary chat/export surfaces.
```

---

### ION-W6 — Assign Retrieval Zone

Purpose:

```text
Make retrieval safe by giving every object a zone.
```

Zones:

```yaml
retrieval_zone:
  ACTIVE_CANON: accepted law/templates/current docs
  OPERATIONAL_SUPPORT: live packet support, recent receipts, validation
  PROJECT_CONTEXT: project-specific approved context
  PROVISIONAL_WORKING: useful but unaccepted
  LINEAGE_ARCHIVE: historical witness
  RESEARCH_DREAMSPACE: speculative or future-facing
  QUARANTINE: unsafe, malformed, contradictory, secret, or blocked
  SECRET_LOCKBOX: sensitive content only via secure surfaces
```

Retrieval rule:

```text
Default retrieval may use ACTIVE_CANON, OPERATIONAL_SUPPORT, and approved PROJECT_CONTEXT.
PROVISIONAL_WORKING must be labeled.
LINEAGE_ARCHIVE and RESEARCH_DREAMSPACE cannot silently govern current work.
QUARANTINE and SECRET_LOCKBOX are excluded from normal model context.
```

---

### ION-W7 — Detect Contradictions And Collisions

Purpose:

```text
Stop conflicts from becoming hidden retrieval poison.
```

Minimum edge types:

```yaml
relation_edge:
  supports
  contradicts
  supersedes
  superseded_by
  derives_from
  references
  duplicates
  depends_on
  blocks
  resolves
  implements
  tests
  configures
  owns
  touches_surface
  mentions
  alternative_to
```

Collision checks:

```text
- Same name, different authority.
- Same claim, incompatible evidence.
- Same file/path, duplicate roots.
- Same decision, different current status.
- Same task, multiple next owners.
- Current doc conflicts with newer receipt.
- Runtime claim conflicts with live validation.
- Secret-bearing content appears in exportable path.
```

Contradiction states:

```yaml
contradiction_state:
  OPEN
  INVESTIGATING
  RESOLVED
  ESCALATED
  QUARANTINED
```

Rule:

```text
A contradiction does not need to be solved before work continues,
but it must be represented as a blocker, risk, or scoped uncertainty.
```

---

### ION-W8 — Run Proof Gates

Purpose:

```text
Verify enough for the object's intended use.
```

Gate levels:

| Gate | Intended use | Minimum proof |
|---|---|---|
| `G0_DESCRIPTIVE` | catalog only | path + hash + parser result |
| `G1_WITNESS` | cite as witness | source posture + evidence class |
| `G2_PROVISIONAL_CONTEXT` | use in bounded packet | contradiction scan + scope warning |
| `G3_APPROVED_CONTEXT` | normal domain context | settlement/approval receipt |
| `G4_STATE_DELTA` | change accepted state | validation + human/steward acceptance |
| `G5_EXTERNAL_MUTATION` | connector/write/deploy | policy + approval + execution receipt |
| `G6_HIGH_RISK` | legal/financial/medical/security/prod | human review + domain-specific proof |

AIMOS VIF maps here as witness metadata and confidence/risk gates. ION should not import opaque “deterministic replay” claims for hosted models; it should import the witness envelope idea.

---

### ION-W9 — Write Provenance / Receipt Candidate

Purpose:

```text
Make the write auditable and inheritable.
```

Minimum receipt:

```yaml
write_receipt:
  receipt_id: WR-...
  object_id: ...
  source_ref: ...
  source_hash: ...
  written_at: ISO-8601
  carrier: ...
  stage_results:
    W1: ...
    W2: ...
    W3: ...
    W4: ...
    W5: ...
    W6: ...
    W7: ...
    W8: ...
  accepted_state_changed: false
  retrieval_zone: ...
  evidence_posture: ...
  authority_class: ...
  contradictions:
    - ...
  proof_gates:
    highest_passed: ...
    failed:
      - ...
  next_packet: ...
```

Rule:

```text
A receipt candidate is not accepted canon merely because it exists.
```

---

### ION-W10 — Propagate Stale-Context And Next-Packet Pressure

Purpose:

```text
Make downstream effects explicit.
```

Propagation outputs:

```yaml
propagation_notice:
  revised_object: ...
  potentially_stale:
    - object_id: ...
      reason: ...
      action: update | mark_inconsistent | revalidate | quarantine | ignore
  indexes_updated:
    - ...
  context_packages_to_refresh:
    - ...
  receipts_to_review:
    - ...
  next_packets:
    - ...
```

Rule:

```text
A write is incomplete until affected downstream surfaces are updated,
marked stale, or explicitly deferred.
```

---

## 7. Write Regimes

### 7.1 Code Write Regime

Use for:

```text
source code, configs, schemas, tests, package manifests, CI files
```

Extra extraction:

```yaml
code_descriptor:
  language: ...
  symbols:
    - name: ...
      kind: function | class | module | type | constant
  imports: [...]
  exports: [...]
  tests_linked: [...]
  config_surfaces: [...]
  deployment_surfaces: [...]
```

Suggested proof gates:

```text
G0 path/hash
G1 AST/parse success
G2 test inventory
G3 run relevant tests if mutation intended
G4 SDF-CVF-style parity only for high-impact changes
```

ION import from AIMOS:

```text
Use SDF-CVF as optional high-risk parity discipline:
code/docs/tests/traces should not drift when accepted state changes.
```

Do not import:

```text
A universal semantic similarity threshold as a hard law.
A mandatory NL tag regime for every file.
```

---

### 7.2 Documentation / Canon Write Regime

Use for:

```text
docs, protocols, templates, laws, design notes, READMEs
```

Extra extraction:

```yaml
doc_descriptor:
  title: ...
  revision_marker: ...
  authority_claims: [...]
  supersedes: [...]
  claims:
    - claim_id: ...
      text: ...
      evidence_posture: ...
  instructions:
    - ...
  open_questions:
    - ...
```

Proof gates:

```text
- detect authority language
- detect supersession claims
- compare against current canon
- write conflict note if old docs disagree
- preserve non-claims
```

---

### 7.3 Chat / Note / Memory Write Regime

Use for:

```text
user chats, assistant outputs, planning notes, meeting notes, summaries
```

Extra extraction:

```yaml
conversation_descriptor:
  participants: [...]
  turns: [...]
  decisions:
    - ...
  tasks:
    - ...
  commitments:
    - normalized_time: ...
      timezone: ...
      uncertainty: ...
  claims:
    - ...
  preferences:
    - ...
  relationships:
    - ...
```

AIMOS donor idea:

```text
write-time relationship extraction:
same symbols + opposite polarity -> contradicts
same goal + different approach -> alternative_to
references as justification -> supports
code change unblocks task -> resolves
shared prerequisites -> depends_on
high overlap -> duplicates
```

ION safety rule:

```text
Memory may orient. Artifacts govern. Receipts inherit.
```

---

### 7.4 Tool Return / Connector Write Regime

Use for:

```text
tool outputs, command results, gateway returns, MCP status, file writes, validation runs
```

Extra extraction:

```yaml
tool_return_descriptor:
  tool_name: ...
  action_type: read | validate | write_draft | submit | mutate | execute
  inputs_redacted: true | false
  return_code: ...
  stdout_hash: ...
  stderr_hash: ...
  artifacts: [...]
  mutation_claimed: true | false
```

Rule:

```text
Tool visibility is not authority.
Connector reachability is not state.
Validation is not mutation.
A dry-run is not execution.
A draft is not accepted state.
```

---

### 7.5 Model Output Write Regime

Use for:

```text
AI plans, summaries, proposed patches, recommendations, analyses
```

Extra extraction:

```yaml
model_output_descriptor:
  output_type: answer | proposal | draft_patch | report | receipt_candidate | settlement_candidate
  claims: [...]
  assumptions: [...]
  intended_state_delta: ...
  proof_supplied: [...]
  proof_missing: [...]
```

Rule:

```text
Model output enters as CANDIDATE_AI_OUTPUT.
It may produce a candidate transition.
It does not become accepted state without settlement.
```

---

## 8. Minimal ION Context Atom

This is the smallest useful ION import from AIMOS CMC.

```yaml
ion_context_atom:
  atom_id: "atom:..."
  object_family: CLAIM | DECISION | RECEIPT | SOURCE_WITNESS | CODE_ARTIFACT | ...
  content_ref:
    inline: string | null
    uri: string | null
    media_type: string
    sha256: string | null
    size_bytes: integer | null
  source:
    source_ref: string
    source_hash: string | null
    received_at: ISO-8601
  evidence_posture: OBSERVED | EXECUTED | SOURCED | DERIVED | CLAIMED | ASSUMED | SPECULATIVE | CONTRADICTED | DEPRECATED | UNKNOWN
  authority_class: HUMAN_DIRECTIVE | ACCEPTED_RECEIPT | CURRENT_CANON | RUNTIME_PROOF | PACKAGE_SOURCE | PROJECT_SOURCE | HISTORICAL_WITNESS | EXTERNAL_SOURCE | CANDIDATE_AI_OUTPUT | UNKNOWN_AUTHORITY
  retrieval_zone: ACTIVE_CANON | OPERATIONAL_SUPPORT | PROJECT_CONTEXT | PROVISIONAL_WORKING | LINEAGE_ARCHIVE | RESEARCH_DREAMSPACE | QUARANTINE | SECRET_LOCKBOX
  risk_surface:
    - READ_ONLY
  relations:
    - edge_type: supports | contradicts | supersedes | derives_from | references | depends_on | ...
      target: object_id
      confidence: 0.0-1.0
  witness:
    carrier: string
    model_or_tool: string | null
    session_ref: string | null
    confidence: number | null
    uncertainty: string | null
  lifecycle:
    status: CANDIDATE_OBJECT | CARTOGRAPHED_WITNESS | PROVISIONAL_CONTEXT | APPROVED_CONTEXT | ACTIVE_RETRIEVAL | ...
    supersedes: object_id | null
    superseded_by: object_id | null
    stale_after: ISO-8601 | null
  receipt_ref: string
```

What to avoid from AIMOS CMC at first:

```text
- whole memory service
- MCP memory assumptions
- cross-model consciousness fields
- large payload or vector store commitments
- treating memory atoms as accepted truth
```

---

## 9. Minimal ION Evidence Graph

This is the smallest useful import from AIMOS SEG.

```yaml
ion_evidence_edge:
  edge_id: "edge:..."
  source_object: object_id
  target_object: object_id
  relation: supports | contradicts | derives_from | references | supersedes | duplicates | depends_on | resolves | blocks
  evidence_posture: OBSERVED | SOURCED | DERIVED | CLAIMED | ...
  confidence: 0.0-1.0
  created_at: ISO-8601
  created_by: carrier/session
  status: active | stale | disputed | resolved
  receipt_ref: string
```

Do not overclaim:

```text
An explicit evidence graph is not complete semantic truth.
It is an inspectable map of known relationships and conflicts.
```

---

## 10. Minimal ION Witness Envelope

This is the smallest useful import from AIMOS VIF.

```yaml
ion_witness:
  witness_id: "wit:..."
  operation_id: ...
  carrier: chatgpt | codex | mcp | action_gateway | python | human | other
  model_id: string | null
  tool_ids: []
  input_refs: []
  output_refs: []
  confidence:
    score: number | null
    band: high | medium | low | unknown
    threshold: number | null
    passed: boolean | null
  proof:
    commands_run: []
    return_codes: []
    artifacts: []
    hashes: []
  uncertainty:
    known_limits: []
    missing_proof: []
    stale_risk: []
  risk:
    task_criticality: low | routine | important | critical
    review_required: boolean
  created_at: ISO-8601
```

ION adaptation:

```text
Use witness envelopes for proof density and humility.
Do not promise deterministic replay for opaque hosted model calls.
```

---

## 11. Retrieval Compiler Hook

AIMOS HHNI is useful to ION as a **budgeted context compiler**, not necessarily as its exact hypergraph/vector machinery.

ION retrieval should assemble context from write-plane fields:

```text
role + domain + template + active packet + authority ceiling + proof obligation
-> eligible retrieval zones
-> candidate atoms
-> contradiction/staleness filter
-> token budget selection
-> context package with audit trail
```

Minimum output:

```yaml
context_compile_receipt:
  compile_id: ...
  requested_for:
    role: ...
    domain: ...
    template: ...
    packet: ...
  allowed_zones:
    - ACTIVE_CANON
    - OPERATIONAL_SUPPORT
    - PROJECT_CONTEXT
  excluded_zones:
    - QUARANTINE
    - SECRET_LOCKBOX
  selected_objects:
    - object_id: ...
      reason: ...
      tokens_estimated: ...
  omitted_load_bearing_objects:
    - object_id: ...
      reason: budget | stale | authority | secret | contradiction
  contradictions_active:
    - contradiction_id: ...
  token_budget:
    limit: ...
    used: ...
  receipt_ref: ...
```

---

## 12. Integration With Existing ION Concepts

### 12.1 Project Ingestion

Project ingestion becomes a batch application of the write plane:

```text
repo/archive
-> W1 quarantine
-> W2 file tree / package markers
-> W3 object families
-> W4 evidence posture
-> W5 authority/risk
-> W6 retrieval zones
-> W7 graph edges
-> W8 proof gates
-> W9 ingestion receipts
-> W10 stale/context pressure
```

### 12.2 Continuity Bridge

Continuity bridge becomes a semantic application of the write plane:

```text
prior chats / notes / memories / summaries
-> decisions, tasks, claims, commitments, preferences
-> each becomes a candidate atom
-> each gets evidence and authority labels
-> only accepted receipts govern future context
```

### 12.3 Receipts

Receipts become write-plane outputs, not decorative logs.

```text
Receipt = proof-bearing object that future retrieval can inherit.
```

### 12.4 Settlement

Settlement decides promotion:

```text
CARTOGRAPHED_WITNESS -> PROVISIONAL_CONTEXT
PROVISIONAL_CONTEXT -> APPROVED_CONTEXT
APPROVED_CONTEXT -> ACTIVE_RETRIEVAL
```

### 12.5 Persona Interface

Persona must not expose raw machinery unless useful, but the machinery must exist behind the response.

```text
Persona response should report:
- what was inspected
- what was produced
- what was validated
- what was not claimed
- what next packet follows
```

---

## 13. What Should Be Implemented First

### Phase 0 — Documentation / Template Only

Deliverables:

```text
ION_COMPUTE_AT_WRITE_SPEC.md
ION_WRITE_PLANE_SCHEMA.yaml
ION_WRITE_PLANE_CHECKLIST.md
```

No runtime claims.

### Phase 1 — File-Based Write Receipt

Implement a simple CLI/script that accepts one file/path and emits:

```text
object descriptor
evidence posture
authority class
retrieval zone
receipt JSON
```

No vector DB. No daemon. No MCP. No mutation.

### Phase 2 — Project Ingestion Pilot

Run on a small project or selected ION folder:

```text
manifest
file classes
risk classes
first context atoms
first graph edges
receipts
```

### Phase 3 — Relationship Graph

Add edges:

```text
implements / tests / configures / supports / contradicts / supersedes / depends_on
```

Use simple deterministic heuristics first.

### Phase 4 — Context Compiler

Create a context package from:

```text
domain + template + packet + retrieval zones + token budget
```

### Phase 5 — High-Risk Gates

Only after the above:

```text
SDF-CVF parity gates
VIF confidence thresholds
connector mutation policy gates
human settlement UI
```

---

## 14. What Is Valuable But Deferred

| AIMOS tech | ION disposition |
|---|---|
| CMC SQLite atom store | Import atom discipline first; defer service adoption |
| HHNI hypergraph/vector retrieval | Import budgeted compiler pattern first |
| VIF κ-gating | Import witness/risk threshold language; defer deterministic replay claims |
| SEG evidence graph | Import explicit edge types; defer full graph engine |
| SDF-CVF parity | Use optional high-risk gate; defer universal mandate |
| Project Truth pack | Convert to ION project-ingestion template |
| Agent living workspace | Adapt as domain context package pattern |
| Variable-density planning | Adopt for packet depth and proof depth |
| Chat significance | Adopt for continuity bridge and memory extraction |
| AIMOS tunnels / BAS / JOC | Product/carrier donor evidence only, not ION substrate |

---

## 15. Anti-Imports

Do not import these into ION from AIMOS:

```text
- consciousness or AGI claims as proof
- Aether sovereign identity as ION identity
- old completion percentages
- package count as runtime truth
- automatic acceptance of memory atoms
- autonomous commit/deploy behavior
- secret-bypass patterns
- whole JOC/BAS/MCP assumptions as core substrate
- strong replay claims for hosted opaque models
- mathematical/physics metaphors as required infrastructure
```

A useful compression:

```text
Import the write discipline.
Do not import the mythology as operating authority.
```

---

## 16. Acceptance Criteria For This Spec

This spec is ready for review if it provides:

```yaml
acceptance_criteria:
  - maps AIMOS W1-W10 into ION stages
  - defines object states and retrieval zones
  - defines evidence, authority, risk, and relation enums
  - defines receipt and propagation requirements
  - separates code/docs/chat/tool/model write regimes
  - identifies what to implement first
  - identifies what not to import
  - preserves AIMOS as donor witness, not canon
```

---

## 17. Next Packets

```yaml
next_packets:
  - packet_id: CAW_EXTRACT_002_WRITE_PLANE_CHECKLIST
    goal: Create an operator-facing checklist for manual or scripted write-plane review.
  - packet_id: CAW_EXTRACT_003_MINIMAL_FILE_INGEST_SCRIPT
    goal: Build a local script that emits a write receipt for one file or folder.
  - packet_id: CAW_EXTRACT_004_PROJECT_TRUTH_TO_ION_TEMPLATE
    goal: Convert AIMOS PROJECT_TRUTH pack into an ION project-ingestion template.
  - packet_id: CAW_EXTRACT_005_CONTEXT_ATOM_LEDGER_PILOT
    goal: Define a minimal JSONL atom ledger for ION receipts/context objects.
```

---

## 18. Source Evidence Manifest

The following paths were inspected as source witnesses. Hashes refer to files inside `/mnt/data/AIM-ION.zip`.

```json
[
  {
    "path": "AIM-ION/canon/constitution/AETHER_ATLAS.md",
    "sha256": "a33a78bc4302c02ab0558a95b9177b35fe00b5c5ab6684416ec45953bf493387",
    "size_bytes": 60294,
    "matched_terms": [
      "compute-at-write",
      "W1",
      "Evidence Classification",
      "Authority Classification",
      "Revision Propagation",
      "capsule",
      "checkpoint",
      "bitemporal",
      "budget",
      "contradicts",
      "\u03ba",
      "parity",
      "Project Truth"
    ]
  },
  {
    "path": "AIM-ION/canon/constitution/AETHER_INTERFACE.md",
    "sha256": "393a8922af5810d48f71b42f69aca0b1190d0536043c273c4f2e2d717864527b",
    "size_bytes": 27930,
    "matched_terms": [
      "Revision Propagation",
      "capsule",
      "checkpoint",
      "memory_atom",
      "append-only",
      "bitemporal"
    ]
  },
  {
    "path": "AIM-ION/canon/doctrine/AGENT_CONTEXT_ARCHITECTURE.md",
    "sha256": "f5565f472ba5acc060ad3a3f353c49592271047fdabde7ad7a99af5815ae30bb",
    "size_bytes": 33931,
    "matched_terms": [
      "capsule",
      "checkpoint",
      "budget",
      "variable-density"
    ]
  },
  {
    "path": "AIM-ION/canon/doctrine/VARIABLE_DENSITY_PLANNING.md",
    "sha256": "716a94dc1c872caa228441ff3862b22d193bfbbdfe37aebf6771ef209f1d0b29",
    "size_bytes": 20415,
    "matched_terms": [
      "capsule",
      "contradicts",
      "variable-density"
    ]
  },
  {
    "path": "AIM-ION/canon/north_star/NORTH_STAR_V3.md",
    "sha256": "652e435953e75f70f9a0fc5c8bc115119e9979c2ba9b55ef4ab38f4f04055932",
    "size_bytes": 9731,
    "matched_terms": [
      "capsule",
      "bitemporal",
      "\u03ba",
      "variable-density"
    ]
  },
  {
    "path": "AIM-ION/canon/doctrine/AIMOS_CONTEXT_INTEGRATION.md",
    "sha256": "f32e7eb8b1d41cf282faec1a61e036524c752811551d156dfdce4fec4711e8a6",
    "size_bytes": 31700,
    "matched_terms": [
      "W1",
      "capsule",
      "bitemporal",
      "budget",
      "\u03ba",
      "kappa"
    ]
  },
  {
    "path": "AIM-ION/ide_orchestration/prototypes/dac/AI_CHAT_SIGNIFICANCE_ENHANCEMENT.md",
    "sha256": "63b389496aee673ebd5d9c1e993bb0c4d12c345c9c08647fc0cdcad9b7840ea5",
    "size_bytes": 22317,
    "matched_terms": [
      "budget",
      "contradicts",
      "supports",
      "write-time"
    ]
  },
  {
    "path": "AIM-ION/PROJECT_TRUTH/README.md",
    "sha256": "1e2a5d2911f4c41e660851f81b2ea20b854307d144b17aac8b0b395a34368757",
    "size_bytes": 1055,
    "matched_terms": [
      "Project Truth"
    ]
  },
  {
    "path": "AIM-ION/packages/cmc_service/models.py",
    "sha256": "3d44f01410c8f5ea551bb205492a9ff254b5fbf15ebe0849fe03b09626eb1bdf",
    "size_bytes": 6388,
    "matched_terms": []
  },
  {
    "path": "AIM-ION/packages/cmc_service/repository.py",
    "sha256": "c89c527bb6c74d89e04132793837264d0301d317c15785b931d5482adc4c544b",
    "size_bytes": 36570,
    "matched_terms": [
      "checkpoint",
      "bitemporal",
      "budget"
    ]
  },
  {
    "path": "AIM-ION/packages/cmc_service/memory_store.py",
    "sha256": "bc38f0f8ef4a7f704163959412ce95f51119b4a7b860ae5990c2538463d767c2",
    "size_bytes": 29760,
    "matched_terms": []
  },
  {
    "path": "AIM-ION/packages/cmc_service/bitemporal_queries.py",
    "sha256": "b1caa8cbf3efec5f6e605c9915f580ecc031505e29f484f65429adbf23c74077",
    "size_bytes": 13261,
    "matched_terms": [
      "bitemporal"
    ]
  },
  {
    "path": "AIM-ION/packages/hhni/budget_manager.py",
    "sha256": "26727b9354d8c5af4192df6a8c47c6cd8d139f6904111c93a35600d2802fb8bd",
    "size_bytes": 11911,
    "matched_terms": [
      "budget"
    ]
  },
  {
    "path": "AIM-ION/packages/hhni/retrieval.py",
    "sha256": "fa52a5657257a28146e9bda32fd80cf38beb08b09ab3ca9cc6f6ecdc4ce976f4",
    "size_bytes": 23168,
    "matched_terms": [
      "budget",
      "parity",
      "quartet"
    ]
  },
  {
    "path": "AIM-ION/packages/hhni/conflict_resolver.py",
    "sha256": "2d186d60b2746dbab4d7aed0e214b3a451b4681a04c453b1d7f5dd27cd0528de",
    "size_bytes": 9526,
    "matched_terms": [
      "budget",
      "supports"
    ]
  },
  {
    "path": "AIM-ION/packages/seg/models.py",
    "sha256": "d03dc00c8c7e9135f6ca420de0725fae5de5435150fa87eb7285b1813a26f5d1",
    "size_bytes": 7498,
    "matched_terms": [
      "bitemporal",
      "contradicts",
      "supports"
    ]
  },
  {
    "path": "AIM-ION/packages/seg/seg_graph.py",
    "sha256": "897d02674a90016545b5f0298a27329f68d2eb993b4d66c397599634ffe542dd",
    "size_bytes": 15107,
    "matched_terms": [
      "bitemporal",
      "contradicts",
      "supports"
    ]
  },
  {
    "path": "AIM-ION/packages/seg/witness.py",
    "sha256": "4dfcf4c77f06f3fe245d9667f68e0b4cbfc2ae485e6bea00d86f2aa182134ebd",
    "size_bytes": 1353,
    "matched_terms": []
  },
  {
    "path": "AIM-ION/packages/vif/kappa_gate.py",
    "sha256": "93bde958c8d0cd972441457fc31d48565931cc1ba8ce3a35927f6d3f2e2a5d5c",
    "size_bytes": 12089,
    "matched_terms": [
      "\u03ba",
      "kappa"
    ]
  },
  {
    "path": "AIM-ION/packages/vif/witness.py",
    "sha256": "caf0a390a98e522caae78749008d43054bcb53b030ceae7b6493a4e2a96eb02e",
    "size_bytes": 8905,
    "matched_terms": [
      "\u03ba",
      "kappa"
    ]
  },
  {
    "path": "AIM-ION/packages/sdfcvf/quartet.py",
    "sha256": "a101e1cd7b621b34d67698feab21aaceac6b0d8126db5459e5242d681ef956f6",
    "size_bytes": 12469,
    "matched_terms": [
      "quartet"
    ]
  },
  {
    "path": "AIM-ION/packages/sdfcvf/parity.py",
    "sha256": "b54de2600fe9aa34db4ca1496227ba58aa6edefa3d6739079059e97440987c0c",
    "size_bytes": 14857,
    "matched_terms": [
      "parity",
      "quartet"
    ]
  },
  {
    "path": "AIM-ION/packages/sdfcvf/gates.py",
    "sha256": "895ca193fb6e93a731e3b4dc445bf1ca167b68b0a996d1f3f233d716be8fe328",
    "size_bytes": 8174,
    "matched_terms": [
      "parity",
      "quartet"
    ]
  }
]
```

---

## 19. Validation And Limits

Validation performed:

```text
- Inspected archive root and selected AIMOS source files.
- Located AIMOS compute-at-write source in AETHER_ATLAS Book IX.
- Inspected AETHER_INTERFACE schemas for capsules, checkpoints, receipts, revision receipts, compression receipts, and memory atoms.
- Inspected package code witnesses for CMC, HHNI, SEG, VIF, and SDF-CVF.
- Produced ION-native adaptation rather than importing AIMOS terms wholesale.
```

Validation not performed:

```text
- Did not execute AIMOS tests.
- Did not import AIMOS packages into ION.
- Did not call live MCP, Action Gateway, GitHub, daemon, or local hub.
- Did not verify runtime claims from AIMOS documents.
```

Non-claim:

```text
This is a candidate ION spec. It becomes accepted ION doctrine only after review and settlement.
```
