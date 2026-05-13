# Thread Packet: Codex-Context Contract (2026-03-03)

Thread ID: `aimos_task_codex_context_contract_2026-03-03`  
Owner: Codex-Context  
Coordinator: Codex Agent  
Primary consumer: Claude Opus 4.6 (Dispatch and Context-System pages)

---

## Mission Objective

Define and publish a stable v0 context-attachment contract so JOC can attach context slices to dispatches without schema churn.

---

## In Scope

- Shared contract shape for context attachment payloads
- Provenance and confidence fields required by VIF/SEG/TCS workflows
- Adapter guidance for current JOC `ContextCapsule` usage

## Out of Scope

- Full mapper rewrite
- UI theme/layout changes
- Non-context BAS API changes

---

## Proposed v0 Contract (Draft)

```ts
interface ContextAttachmentV0 {
  context_id: string;
  slice_type: 'file_excerpt' | 'memory_atom' | 'timeline_event' | 'goal_state' | 'evidence_chain' | 'summary';
  title: string;
  content: string;
  token_estimate: number;
  confidence: number; // 0.0 to 1.0
  provenance: {
    source_system: 'CMC' | 'HHNI' | 'TCS' | 'SEG' | 'APOE' | 'manual';
    source_ref: string; // atom id, file path, timeline id, goal id
    captured_at: string; // ISO timestamp
    hash?: string;
  };
  truncation?: {
    applied: boolean;
    policy?: string;
    original_tokens?: number;
  };
}
```

---

## 24h Deliverables

1. Publish and version the v0 contract proposal in this thread.
2. Provide compatibility map:
   - current JOC `ContextCapsule` fields
   - required adapter for `ContextAttachmentV0`
3. Provide 3 canonical JSON examples:
   - file excerpt
   - memory atom
   - timeline event

---

## 72h Deliverables

1. Draft shared contract module path and import plan (proposed: `packages/shared/contextAttachment.ts`).
2. Define minimal validation rules (required keys, confidence bounds, token estimate integrity).
3. Provide migration plan for existing `DispatchPage` local types.

---

## Acceptance Gates

1. Contract gate
   - v0 schema published and approved in thread.

2. Compatibility gate
   - Explicit adapter mapping from current `ContextCapsule` to v0 schema.

3. Consumer gate
   - Opus confirms schema is sufficient to wire Dispatch attachment UI.

4. Evidence gate
   - Thread report includes required COO structure.

---

## Validation Checklist

- Schema examples parse as valid JSON.
- All examples include provenance and confidence.
- Token estimate is present and non-negative in each example.
- Required fields are documented in one canonical location.

---

## Rollback

- Keep current `ContextCapsule` path operational until adapter lands.
- Introduce schema as additive module first; defer removals.
- Version contract if breaking changes become unavoidable.

