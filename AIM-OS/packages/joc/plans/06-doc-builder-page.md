# 06 — Doc Builder Page (Deep Plan)

> **High-end documentation system** — not a Markdown editor, a knowledge construction tool.

---

## What This Page Does

A documentation authoring and browsing system that leverages AIM-OS for:
1. **Multi-layer documentation** — L0 (overview) through L4 (implementation detail) following Aether Memory System architecture
2. **HHNI semantic search** — find docs by meaning, not just keywords
3. **Auto-generation** — generate documentation from code using NL Tags and AST analysis
4. **Evidence-backed docs** — every claim links to SEG evidence atoms
5. **Live validation** — VIF confidence scores on documentation accuracy

---

## Document Layer System (from Aether Memory System L0-L4)

| Layer | Name | Content | Audience |
|-------|------|---------|----------|
| L0 | Executive | 1-page overview, key decisions, status | Humans, new agents |
| L1 | Architecture | System design, component relationships, data flow | Architects, senior devs |
| L2 | Specification | API contracts, interface definitions, type specs | Developers |
| L3 | Implementation | Code walkthrough, algorithm details, edge cases | Implementers |
| L4 | Debug/Ops | Troubleshooting, performance tuning, operational procedures | Operators |

Each layer is a separate view of the same project/system, automatically cross-linked.

---

## Page Architecture

### Primary View: Document Browser
- Tree navigation by project → module → layer
- Search bar with HHNI semantic search
- Tag filter (NL Tags)
- Recently viewed / bookmarked

### Secondary View: Document Editor
- Rich Markdown editor with live preview
- Layer selector (L0-L4)
- Evidence insertion (link to SEG atoms)
- Confidence badge editor (VIF scores)
- Auto-complete from HHNI context

### Tertiary View: Auto-Generation
- Select a code file or module
- Extract NL Tags, function signatures, type definitions
- Generate doc skeleton at selected layer
- Human review and polish

### Quaternary View: Validation Dashboard
- List of all docs with confidence scores
- Staleness detector (doc age vs. code modification date)
- Coverage map (which modules have docs at which layers)
- Contradiction detector (doc claims vs. code reality via SEG)

---

## Left Drawer Contents (Page-Specific)

| Icon | Drawer | Content |
|------|--------|---------|
| 📚 | Library | Document tree browser |
| 🔍 | Search | HHNI semantic doc search |
| 🏷️ | NL Tags | Tag browser and filter |
| ✨ | Generate | Auto-generation controls |
| ✅ | Validate | Validation status overview |
| 📊 | Coverage | Layer coverage heat map |

---

## Implementation Phases

### Phase 1: Document Browser
- Tree navigation with project/module/layer hierarchy
- Markdown rendering
- HHNI search integration

### Phase 2: Document Editor
- Rich Markdown editing
- Layer metadata
- Evidence linking UI
- Save to CMC

### Phase 3: Auto-Generation
- Code file → NL Tags extraction
- Doc skeleton generation
- Layer-appropriate content

### Phase 4: Validation Dashboard
- Coverage map rendering
- Staleness detection
- Confidence score aggregation
