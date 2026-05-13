# Naming Conventions

**Status:** DOCUMENTED

## System slugs (`/systems/<system-slug>/`)

- Lowercase ASCII; hyphen-separated words.  
- Prefer **technical identity** over marketing name: `linux-kernel` not `linux`.  
- Disambiguate: `xnu-macos`, `android-aosp`, `windows-nt`.  
- For protocols/SDKs: `model-context-protocol`, `anthropic-claude-code-agent-sdk`.  
- For vague public surfaces: be explicit: `openai-agents-chatgpt-public-runtime` (product/API/runtime documentation bundle, not “ChatGPT internals”).

## Files inside a package

Fixed names only (schema-enforced):

`00_identity.md` … `14_documented_vs_inferred.md`, `sources.yaml`, `tags.yaml`, `relations.json`

## Tags

- Lowercase; hyphen-separated; registered in `tag_taxonomy.yaml`.  
- Package `tags.yaml` lists **applied** tags; index duplicates for query speed.

## Relation edge IDs

- Optional `id` field: `rel-<source-slug>--<target-slug>--<ordinal>`  
- Types from `relation_types.md` enum.

## Comparative docs

- Filename: `<topic>_models.md` under `/comparative`.  
- Heading anchors: stable, short (`## capability-based-security`).

## Graphs

- `graphs/*.mmd` — Mermaid source; node IDs: slug or short stable abbreviation from `systems_index.yaml`.
