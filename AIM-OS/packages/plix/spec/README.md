# PLIX Language Specification - Directory Structure

**Purpose:** Formal reference specification for PLIX language  
**Status:** 🚧 **IN PROGRESS**  
**Version:** 1.0.0

---

## 📁 **DIRECTORY STRUCTURE**

```
packages/plix/spec/
├── PLIX_LANGUAGE_SPECIFICATION.md  # Main specification document
├── sections/
│   ├── 01_introduction.md          # Section 1: Introduction/Overview
│   ├── 02_core_concepts.md         # Section 2: Core Concepts and Ontology
│   ├── 03_syntax.md                 # Section 3: Syntax (Grammar)
│   ├── 04_semantics.md              # Section 4: Semantics (Meaning and Execution)
│   ├── 05_evolution.md              # Section 5: Layer Model and Extensions
│   ├── 06_examples.md               # Section 6: Examples and Use Cases
│   ├── 07_tooling.md                # Section 7: Tooling and Implementation
│   ├── 08_appendices.md             # Section 8: Appendices/Reference Sections
│   └── 09_conformance.md            # Section 9: Conformance and Testing
├── lexicon/
│   ├── lexicon_table.md             # Complete lexicon table (auto-generated)
│   ├── tag_prefixes.md              # Tag prefix reference
│   ├── operators.md                 # Operator reference
│   ├── keywords.md                  # Keyword reference
│   └── types.md                     # Type reference
├── schemas/
│   ├── canonical.json               # Canonical JSON Schema
│   └── sform.ebnf                   # S-form EBNF grammar
└── scripts/
    ├── generate_lexicon.ts          # Auto-generate lexicon from registry + parser
    ├── validate_spec.ts             # Validate spec completeness
    └── build_spec.ts                # Build HTML/PDF from Markdown
```

---

## 📋 **FILE DESCRIPTIONS**

### **Main Specification**
- `PLIX_LANGUAGE_SPECIFICATION.md` - Master specification document with table of contents and cross-references

### **Section Files**
- `sections/01_introduction.md` - Introduction, design goals, target audience
- `sections/02_core_concepts.md` - Tag system, bitemporal model, authority tiers, lexicon
- `sections/03_syntax.md` - EBNF grammar, surface forms, parser edge cases, JSON Schema
- `sections/04_semantics.md` - Operational pipeline, Hoare logic, type system, effect system
- `sections/05_evolution.md` - Layer model, GGP system, evolution framework
- `sections/06_examples.md` - Cross-domain examples, tutorials, anti-examples
- `sections/07_tooling.md` - Parser API, Compiler API, Registry API, GGP API, security notes
- `sections/08_appendices.md` - Tag registry, comparison matrix, keyword index, bibliography
- `sections/09_conformance.md` - Conformance levels, test suites, validation tools

### **Lexicon Files**
- `lexicon/lexicon_table.md` - Complete lexicon table (auto-generated)
- `lexicon/tag_prefixes.md` - Tag prefix reference
- `lexicon/operators.md` - Operator reference
- `lexicon/keywords.md` - Keyword reference
- `lexicon/types.md` - Type reference

### **Schema Files**
- `schemas/canonical.json` - Canonical JSON Schema (from GRAMMAR_SPECIFICATION_V2.md)
- `schemas/sform.ebnf` - S-form EBNF grammar

### **Scripts**
- `scripts/generate_lexicon.ts` - Auto-generate lexicon from Phase 3 Registry + Phase 1 Parser
- `scripts/validate_spec.ts` - Validate spec completeness and cross-references
- `scripts/build_spec.ts` - Build HTML/PDF from Markdown (via Pandoc/MkDocs)

---

## 🔄 **WORKFLOW**

1. **Extract from Textbook:** Pull reference sections from textbook into spec format
2. **Generate Lexicon:** Auto-generate lexicon table from registry + parser
3. **Formalize Semantics:** Add Hoare triples and predicate logic notation
4. **Populate Examples:** Extract examples from textbook and Phase 1-4
5. **Create Test Suites:** Organize Phase 1-4 tests into conformance levels
6. **Build Spec:** Generate HTML/PDF from Markdown

---

**Status:** 🚧 **IN PROGRESS**  
**Next:** Extract reference sections from textbook

