# Lab crate dependency map (context_mapper_lab)

```
context_mapper_lab
├── tree-sitter      (0.26)   — parser runtime
├── tree-sitter-rust (0.24)   — Rust grammar; build script compiles C grammar (needs cc)
└── regex            (1.10)   — symbol_usage.rs (slice_contracts word-boundary matching)
```

Internal module dependency (no external beyond above):

- lib.rs re-exports: types, extractor, imports, resolver, symbol_usage, envelope
- extractor → types (Contract, ContractExtractor, ExtractedFile, ParseConfidence)
- imports → types (ImportRef)
- resolver → types (ImportRef, ExtractedFile); std::path, std::fs
- symbol_usage → types (Contract); regex
- envelope → types (Contract, ParseConfidence, ExtractedFile); std::collections::BTreeMap, std::path

No Tauri, no daemon, no workspace dependency.
