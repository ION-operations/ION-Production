# Lane B - Mapper Adapter Contract v0.1

Status: Contract phase (no live integration)  
Date: 2026-03-01  
Lane: B (Contextual Sync convergence)

---

## Mission Scope

This document defines the bridge contract between:

- live mapper-side outputs in `context_capsule_wire_and_mapper_v1/context_mapper_lab`
- and the Shadow BCI emitter input shape used by `shadow_sync/shadow_bci_v1_emitter.py`

This is a convergence contract only. It does not wire runtime emission.

---

## 1) Live Mapper Surfaces (Observed Reality)

Observed code surfaces used as source-of-truth:

- `context_mapper_lab/src/types.rs`
  - `ParseConfidence { High | Degraded | Fallback }`
  - `Contract { kind, name, signature }`
  - `ExtractedFile { path, imports, contracts, confidence }`
- `context_mapper_lab/src/extractor.rs`
  - `TreeSitterExtractor.extract(path, contents) -> ExtractedFile`
- `context_mapper_lab/src/resolver.rs`
  - `resolve_imports(crate_root, extracted.imports) -> Vec<PathBuf>`
  - `resolve_reexports(...)` currently placeholder
- `context_mapper_lab/src/envelope.rs`
  - `Envelope::from_extracted(file)` and `meta()` (`confidence`, `contract_count`)
- `context_mapper_lab/src/symbol_usage.rs`
  - `collect_usage(...)` currently placeholder
- `context_mapper_lab/src/main.rs`
  - demonstrates availability of source text at call-site (`read_to_string`) plus extracted + resolved outputs in one flow

### Current guaranteed mapper facts

- Extracted file path (`ExtractedFile.path`)
- Raw import lines (`ExtractedFile.imports`)
- Public contract list (`ExtractedFile.contracts`)
- Parse confidence enum (`ExtractedFile.confidence`)
- Resolved local dependency file paths (`resolve_imports` output)

### Current partial/placeholder surfaces

- `resolve_reexports`: placeholder in this live capsule
- `symbol_usage.collect_usage`: placeholder in this live capsule
- Rich envelope transport format: not active in live capsule (shape only)

---

## 2) Proposed Minimal Adapter Shape

Adapter contract shape (smallest viable bridge):

```json
{
  "source_path": "string",
  "source_text": "string",
  "imports": ["string"],
  "contracts": [
    { "kind": "string", "name": "string", "signature": "string|null" }
  ],
  "parse_confidence": "High|Degraded|Fallback",
  "resolved_dependencies": ["string"],
  "observed_at": "ISO-8601 timestamp (optional)"
}
```

Adapter name:

- `ShadowBciEmitterInput` (conceptual contract name)

This shape is intentionally close to live mapper reality and directly consumable by current emitter v0.

---

## 3) Field-Level Mapping Table

Legend:

- `exact now` = directly present in live outputs
- `derived now` = deterministically derivable from live outputs/call-site
- `partial now` = partially available, known caveats
- `missing now` = unavailable in live mapper output

### 3.1 Core adapter fields

| Adapter field | Source in live mapper flow | Transform | Certainty |
|---|---|---|---|
| `source_path` | `ExtractedFile.path` | direct copy | exact now |
| `source_text` | caller-side file read (`main.rs` currently reads via `read_to_string`) | pass-through | derived now |
| `imports` | `ExtractedFile.imports` | direct copy | exact now |
| `contracts[].kind` | `ExtractedFile.contracts[].kind` | direct copy | exact now |
| `contracts[].name` | `ExtractedFile.contracts[].name` | direct copy | exact now |
| `contracts[].signature` | `ExtractedFile.contracts[].signature` | direct copy (`Option<String> -> string|null`) | partial now (can be null) |
| `parse_confidence` | `ExtractedFile.confidence` | enum string conversion | exact now |
| `resolved_dependencies` | `resolve_imports(...) -> Vec<PathBuf>` | path stringify + slash normalization | derived now |
| `observed_at` | none in mapper outputs | stamp at adapter invocation time or caller-provided timestamp | derived now |

### 3.2 File snapshot atom inputs (`bci_atom` fact_type=`file_snapshot`)

| Field used by emitter | Source | Transform | Certainty |
|---|---|---|---|
| `source_path` | `ExtractedFile.path` | direct | exact now |
| `parse_confidence` | `ExtractedFile.confidence` | enum -> string | exact now |
| `import_count` | `len(ExtractedFile.imports)` | count | derived now |
| `contract_count` | `len(ExtractedFile.contracts)` | count | derived now |
| `resolved_dependency_count` | `len(resolve_imports(...))` | count | derived now |
| `source_text_sha256` | caller source text | sha256 | derived now |

### 3.3 Import atoms (`bci_atom` fact_type=`import_decl`)

| Field | Source | Transform | Certainty |
|---|---|---|---|
| `import_decl` | `ExtractedFile.imports[i]` | direct | exact now |
| `ordinal` | import position | enumerate | derived now |
| relation to file atom | file atom id | record-link | derived now |

### 3.4 Contract atoms (`bci_atom` fact_type=`contract_decl`)

| Field | Source | Transform | Certainty |
|---|---|---|---|
| `contract_kind` | `Contract.kind` | direct | exact now |
| `contract_name` | `Contract.name` | direct | exact now |
| `contract_signature` | `Contract.signature` | direct (`null` allowed) | partial now |
| relation to file atom | file atom id | record-link | derived now |

### 3.5 L0 boundary view (`bci_boundary_view`, `view_level=L0`)

| Field | Source | Transform | Certainty |
|---|---|---|---|
| `source_path` | `ExtractedFile.path` | direct | exact now |
| `summary` | imports/contracts/confidence | deterministic summary string | derived now |
| `contract_names` | `contracts[].name` | list projection | derived now |
| `resolved_dependencies` | resolver output | stringify paths | derived now |

### 3.6 L5 boundary view (`bci_boundary_view`, `view_level=L5`)

| Field | Source | Transform | Certainty |
|---|---|---|---|
| `source_text` | caller source text | direct | derived now |
| `imports` | `ExtractedFile.imports` | direct | exact now |
| `contracts` | `ExtractedFile.contracts` | direct structural projection | exact now |
| `parse_confidence` | `ExtractedFile.confidence` | enum -> string | exact now |

---

## 4) Emit Classification

## A) Emit now

- `source_path`
- `imports`
- `contracts` (`kind`, `name`, optional `signature`)
- `parse_confidence`
- local `resolved_dependencies` from `resolve_imports`
- file/import/contract atoms
- L0 and L5 boundary views

## B) Emit with adapter derivation

- `source_text` (from call-site input/read)
- `observed_at` timestamp
- path normalization (`PathBuf -> string`)
- hash/count/summary fields (`source_text_sha256`, counts, summary sentence)
- intra-record relations (`derived_from` links)

## C) Not ready yet

- Deep re-export certainty (live `resolve_reexports` placeholder)
- Symbol-usage truth for precision slicing (`collect_usage` placeholder)
- Contradiction and drift states over historical deltas
- Advisory sync-state derivation from multi-run comparisons
- Robust provenance such as source contract file-path per contract in current live capsule

---

## 5) Candidate Passive Hook Points

### Candidate 1: After extraction (`extractor.extract`)

- Pros: earliest deterministic output; minimal dependencies
- Cons: no resolved dependency set yet; weaker L0 utility
- Classification: possible but less complete

### Candidate 2: After resolution (`resolve_imports`) in mapper orchestration flow

- Pros: has extracted + resolved deps + caller source text available; enough for atoms + L0/L5; still observational
- Cons: requires one orchestration boundary call site
- Classification: **recommended safest first passive hook**

### Candidate 3: After envelope assembly (`Envelope::from_extracted` / `meta`)

- Pros: has confidence + contract count
- Cons: current live envelope does not carry resolved deps; may force extra coupling
- Classification: safe later, but weaker first hook

## Recommended first passive hook

Use **Candidate 2**: adapter invocation at the orchestration boundary immediately after `resolve_imports` completes and before any response delivery.

Why safest:

- observational-only behavior
- low blast radius (single call boundary)
- complete enough for current emitter contract
- does not mutate mapper parse/resolution logic

---

## 6) Smallest Merge-Safe Adapter Module Shape

Minimal module functions:

1. `adapt_live_mapper_snapshot(snapshot) -> ShadowBciEmitterInput`
2. `validate_adapter_input_shape(input) -> bool/error`
3. optional `emit_probe(input)` for isolated verification only

Required input to adapter:

- `target_source` (caller text)
- `extracted_file` (`path`, `imports`, `contracts`, `confidence`)
- `resolved_local_files` (`Vec<PathBuf>` converted to strings)

No runtime routing changes, no daemon coupling, no kernel coupling.

---

## 7) Contract Conclusion

The current live mapper capsule already provides enough deterministic data to power a passive Shadow BCI emission path for:

- file/import/contract atoms
- L0 and L5 boundary views

A thin adapter at the post-resolution orchestration boundary is sufficient for first merge-safe passive emission behind a feature flag in a later phase.
