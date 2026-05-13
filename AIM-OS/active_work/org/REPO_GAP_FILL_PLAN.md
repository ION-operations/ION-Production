# Repo Gap-Fill Plan

Goal: Inventory and create missing files/templates per the 32+ standards.

## Inventory Commands (manual run)
- Find systems missing L0–L6: search `knowledge_architecture/systems/*` for absent L{0-4}
- Find missing maps/indexes: locate `system.map.lucid.json5` / `system.index.lucid.json5`
- Detect missing metadata: grep required frontmatter keys

## Actions
- Create shells for missing docs using templates
- Normalize formats to standards
- Add to validation checklist
- Submit small PRs per subsystem

## Exit Criteria
- 100% L0–L6 coverage (where required)
- 100% maps/indexes coverage (core layers)
- Validation pass = 100%
