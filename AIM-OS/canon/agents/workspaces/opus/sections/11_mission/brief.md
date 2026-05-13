# Mission Brief

## Grand Organization Mission

**Objective:** Organize the entire AIM-OS corpus (182K files / 3 repos) into a single canonical structure (`canon/`), build the OPUS living workspace, and use both to bootstrap production ION/Aether.

**Why this matters:** All the ideas, designs, and code exist — scattered across 67 directories. ION/Aether can't be built to production specs until the knowledge is organized. By doing this organization manually, OPUS proves the Agent Context Architecture works and creates the data layer the real system needs.

**Three parallel tracks:**
1. **Track A:** Build and operate the OPUS living workspace (this workspace)
2. **Track B:** Copy + organize all content into `canon/` with summaries, indexes, provenance
3. **Track C:** Update North Star V3 + write ION/Aether production specs

## Constraints (Must-Not)

1. Must not delete any existing files — copy only
2. Must not start building code until organization is complete
3. Must not fabricate capability claims (Constitution Art. 1)
4. Must not widen scope without explicit Braden approval (Art. 18)
5. Must update PROVENANCE_LOG.md for every file moved/copied

## Current Phase

**Phase G0: Bootstrap** — Creating workspace structure + canon skeleton.
Next: Phase G1 Survey & Classify (~20-40 prompts walking all directories)

## Success Criteria

- Every significant file in AIM-OS has a place in `canon/`
- Every `canon/` directory has a README.md with summary + provenance
- OPUS workspace fully operational with all 15 sections populated
- North Star V3 written with production ION/Aether plan
- Any agent can boot from workspace and find what they need
