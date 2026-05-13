# Decision: `Documentation_Consolidated/` and Git

**Date:** 2026-04-05  
**Status:** Accepted

## Decision

Keep **`Documentation_Consolidated/`** **out of the Git index** for AIM-ION, as enforced by the inherited root [`.gitignore`](../../.gitignore) (`Documentation_Consolidated/` entry and related rules).

## Rationale

- Size (hundreds of MB) and many ignored binary types (`*.pdf`, archives, media).
- Keeps clones and CI fast; full corpus can remain on disk from rsync or live on NAS.

## Alternatives (if requirements change)

1. **Separate documentation-only repository** with its own `.gitignore` tuned for LFS.
2. **Git LFS** for PDFs/large assets in this repo after narrowing ignore rules.
3. **Partial track**: whitelist only selected subtrees (requires `.gitignore` surgery and maintenance).

## Review

Revisit when publishing or partnering needs a single clone with full papers archive.
