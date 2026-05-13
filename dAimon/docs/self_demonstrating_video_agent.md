# Self-Demonstrating Video Agent

The demo video should be governed by dAimon instead of merely describing dAimon. The video package is itself an AI work product with claims, evidence, exclusions, and receipts.

## Objective

```text
Create a contest demo video that proves the dAimon vertical slice without overclaiming the full enterprise product.
```

## Core Flow

```text
objective
-> classify required claims
-> map demo domains
-> derive storyboard roles
-> generate script
-> gather proof artifacts
-> mark non-claims
-> create shot list
-> produce narration
-> validate claims against receipts
-> export submission bundle
```

## Roles

### Narrative Architect

Purpose:

- Turn the trust failure mode into a clear opening.
- Keep the product line simple: dAimon is governed inheritance, not memory.
- Preserve the three-layer architecture without making the demo feel abstract.

Authority ceiling:

- Can propose narrative and scene order.
- Cannot claim proof that is not in the artifact inventory.

Expected output:

- Opening script.
- Scene sequence.
- Closing line.

### Proof Curator

Purpose:

- Collect artifacts that support each demo claim.
- Link screenshots, local outputs, MongoDB trace outputs, receipts, and validation results.

Authority ceiling:

- Can classify proof strength.
- Cannot upgrade roadmap items to proven claims.

Expected output:

- Proof inventory.
- Artifact-to-claim map.

### Demo Director

Purpose:

- Convert the narrative into shots and screen actions.
- Decide what appears on screen for each claim.

Authority ceiling:

- Can choose visual presentation.
- Cannot hide missing proof behind vague narration.

Expected output:

- Shot list.
- Screen capture plan.
- Timing plan.

### Claim Auditor

Purpose:

- Review every spoken and written claim.
- Mark each claim as proven, local-only, live, roadmap, or non-claim.
- Force edits when a claim exceeds proof.

Authority ceiling:

- Can reject or downgrade demo claims.
- Cannot accept product state outside demo package.

Expected output:

- Claim audit matrix.
- Required edits.
- Claim audit receipt.

### Storyboard Generator

Purpose:

- Draft storyboard panels from the accepted narrative.
- Keep each panel attached to a proof artifact or conceptual label.

Authority ceiling:

- Can create candidate storyboard assets.
- Cannot finalize unsupported scenes.

Expected output:

- Storyboard.
- Scene labels.

### Asset Compiler

Purpose:

- Gather screenshots, terminal recordings, dashboard captures, sample outputs, and diagrams.
- Keep assets organized for final packaging.

Authority ceiling:

- Can package assets.
- Cannot modify proof artifacts to imply behavior not shown.

Expected output:

- Asset manifest.
- Media folder structure.

### Submission Packager

Purpose:

- Assemble final video, README links, proof references, and non-claim statement.

Authority ceiling:

- Can package accepted materials.
- Cannot bypass claim audit.

Expected output:

- Submission checklist.
- Final package receipt.

## Claim Statuses

Use these statuses for every claim:

- `proven_local`: proven by local repo artifact or command.
- `proven_live_mongodb`: proven by MongoDB live readiness or seed trace.
- `proven_live_google`: proven by Google hosted runtime or Gemini/Agent Builder handoff.
- `roadmap`: architecture direction, not yet built.
- `non_claim`: explicitly excluded from current proof.
- `unsupported`: must be removed or revised before release.

## Required Proof Artifacts

Minimum artifacts:

- `sample_outputs/local_demo_summary.json`
- `sample_outputs/local_mcp_trace.json`
- `sample_outputs/mongodb_live_readiness.json`
- `sample_outputs/mongodb_candidate_seed_summary.json`
- `sample_outputs/mongodb_candidate_seed_mcp_trace.json`
- `sample_outputs/orchestration_validation.json`
- `orchestration/product_layers.json`
- `orchestration/domain_registry.json`
- `orchestration/template_registry.json`
- `orchestration/receipt_registry.json`
- `orchestration/build_roadmap.json`
- `orchestration/test_matrix.json`

Optional live artifacts:

- Google Cloud Run health output.
- Cloud deployment receipt.
- Gemini or Agent Builder handoff receipt.
- Dashboard screenshots.
- `sample_outputs/demo_evidence_package.json`
- `sample_outputs/demo_video_claims.json`
- `sample_outputs/agent_builder_mcp_trace_validation.json`

## Scene Plan

### Scene 1: Failure Mode

Claim:

```text
AI output often becomes inherited context without proof, authority, or settlement.
```

Status:

```text
conceptual framing
```

Visual:

- Messy bundle of AI work.
- Candidate objects not yet trusted.

### Scene 2: dAimon Principle

Claim:

```text
AI output is not state. It is a candidate transition.
```

Status:

```text
product principle
```

Visual:

- Flow: import -> classify -> route -> settle -> receipt -> inherit.

### Scene 3: Local Continuity Proof

Claim:

```text
dAimon can classify and settle local candidate objects.
```

Status:

```text
proven_local
```

Proof:

- `sample_outputs/local_demo_summary.json`

Visual:

- Terminal command or dashboard view.
- Object counts and settlement status.

### Scene 4: Accepted-Only Visibility Trace

Claim:

```text
dAimon returns accepted objects with receipt citations and excludes non-inheritable witness.
```

Status:

```text
proven_local
```

Proof:

- `sample_outputs/local_mcp_trace.json`

Visual:

- Considered, returned, excluded sections.

### Scene 5: MongoDB Atlas Proof

Claim:

```text
dAimon can seed and inspect MongoDB-backed candidate state for the contest slice.
```

Status:

```text
proven_live_mongodb
```

Proof:

- `sample_outputs/mongodb_live_readiness.json`
- `sample_outputs/mongodb_candidate_seed_summary.json`
- `sample_outputs/mongodb_candidate_seed_mcp_trace.json`

Visual:

- Redacted readiness summary.
- MongoDB trace counts.

### Scene 6: Orchestration Layer

Claim:

```text
dAimon defines domains, templates, receipts, tests, and management cadence as governed contracts.
```

Status:

```text
proven_local
```

Proof:

- `orchestration/*.json`
- `sample_outputs/orchestration_validation.json`

Visual:

- Layer and domain registries.
- Validation command result.

### Scene 7: Google and Gemini Direction

Claim:

```text
The architecture is designed for Google Cloud, Gemini, and Agent Builder handoff.
```

Status:

```text
roadmap until live proof exists
```

Proof:

- `orchestration/build_roadmap.json`
- Google live artifacts if completed.

Visual:

- Route diagram.
- If live proof exists, show health or handoff receipt.

### Scene 8: The Demo Governs Itself

Claim:

```text
The demo package is governed by claim audit, proof mapping, and non-claims.
```

Status:

```text
proven_local after claim audit artifact exists
```

Proof:

- This document.
- Claim audit receipt once generated.

Visual:

- Claim matrix.
- Supported versus roadmap claims.

## Non-Claims To Include

The demo should explicitly avoid claiming:

- Production readiness.
- Legal compliance certification.
- Complete Google integration unless live proof exists.
- Complete MongoDB MCP production integration.
- Fully autonomous governance.
- That receipts make every underlying statement objectively true.
- That human review is unnecessary.

## Submission Bundle Checklist

- Final script.
- Shot list.
- Claim inventory.
- Proof inventory.
- Non-claim section.
- Final video.
- README link to proof artifacts.
- Release or demo claim receipt.

## Acceptance Criteria

The video package is accepted only when:

- Every claim has a status.
- Every proven claim has an artifact.
- Every roadmap statement is clearly future-facing.
- Unsupported claims are removed.
- The final package shows dAimon governing the demo itself.
