# Boundaries — Unresolved Questions

## B001: AIM-OS-FRESH Scope
- **Question:** How deep should we survey AIM-OS-FRESH (7.5GB)?
- **Decision:** Survey key dirs, skip node_modules — per plan approval
- **Risk:** May miss important content in nested subdirectories
- **Status:** Accept risk; can revisit in G3

## B002: Forge/Nexus Build Integration
- **Question:** Braden mentioned Forge and Nexus have been working on a new ION build. How much of that work should be integrated vs. enhanced?
- **Decision:** Deferred — survey their work in G1 before deciding
- **Risk:** May duplicate or conflict with their approach
- **Status:** Need to review their build outputs

## B003: Cross-Repo Canonical Location
- **Question:** Should canon/ be in AIM-OS-GIT or its own repo?
- **Decision:** AIM-OS-GIT for now (approved in plan)
- **Risk:** May outgrow single repo
- **Status:** Accepted; can split later

## B004: How to Handle 27 Existing Indexes
- **Question:** Synthesize from existing, or build fresh?
- **Decision:** Start fresh in G1, cross-reference existing indexes as encountered
- **Risk:** Redundant work if existing indexes are comprehensive
- **Status:** Accepted; existing indexes provide validation points
