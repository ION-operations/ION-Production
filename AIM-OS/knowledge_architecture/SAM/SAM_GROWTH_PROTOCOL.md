# SAM Growth Protocol

**Purpose:** How to extend, maintain, and evolve the SAM (System Anatomy Mapping) documentation so it grows with the codebase and ensures total alignment for AI builders, UI, backend, plans, and goals.

**Date:** 2026-01-31  
**Status:** ACTIVE – Use this when adding or updating system maps  
**Audience:** AI builders, developers, maintainers  
**Canonical location:** `knowledge_architecture/SAM/SAM_GROWTH_PROTOCOL.md` (AIM-OS-wide). ProEarth also maintains `apps/ProEarth/GPTworking/earthdocs/SAM/SAM_GROWTH_PROTOCOL.md`.

---

## 1. When to Add or Update SAM

### Add a new subsystem map when:
- You introduce a **new major system** (e.g. smoke engine, LOD renderer, river network)
- You create a **new drawer panel** that drives engine behavior
- You add a **new data flow** (UI → bridge → engine) that other builders need to understand
- The **00_MASTER_PROJECT_SYSTEM_MAP** becomes too large (>500 lines) and a subsystem deserves its own file

### Update existing maps when:
- You change **component structure** (new files, moved modules)
- You change **data flow** (params, bridge, engine options)
- You fix **known gaps** (atmosphere disconnect, cloud layers, etc.)
- You add **new goals/plans** that affect code
- You discover **new failure modes** or invariants

### Don't create a map for:
- Trivial UI tweaks (color, layout)
- One-off fixes
- Deprecated systems (mark as deprecated in existing map; don't create new)

---

## 2. How to Add a Subsystem Map

### Step 1: Create the source file

**Path (example for ProEarth):** `earthdocs/SAM/sources/MASTER_{SYSTEM_NAME}_SYSTEM_MAP.md`  
**Generic:** Use your project’s SAM `sources/` folder and naming `MASTER_{SYSTEM_NAME}_SYSTEM_MAP.md`.

**Template:** Use the 5-dimension schema from SAM protocol:
1. **STRUCTURE** – Components, relationships, hierarchy
2. **BEHAVIOR** – Lifecycle, flows, operations
3. **INTERFACES** – Public API, UI↔backend contracts
4. **CONSTRAINTS** – Limits, invariants, failure modes
5. **EVIDENCE** – Status, tests, open gaps

**Tags:** Include `[TAG:SAM] [TAG:MASTER] [TAG:{SYSTEM}]` and section tags with `[END:TAG:*]` pairs.

**Example header:**
```markdown
# MASTER ATMOSPHERE SYSTEM MAP

**[TAG:SAM] [TAG:MASTER] [TAG:ATMOSPHERE]**

...
```

### Step 2: Add to sam.config.yaml

```yaml
phases:
  - name: "Subsystem Maps"
    id: "subsystems"
    order: 2
    files:
      - "sources/00_MASTER_PROJECT_SYSTEM_MAP.md"
      - "sources/MASTER_ATMOSPHERE_SYSTEM_MAP.md"   # NEW
```

### Step 3: Update SAM_MASTER_INDEX (or project index)

- Add to **Document Map** table
- Add to **Planned subsystem maps** (mark as "Started" or "Complete")
- Update **Code Anchors** if new key files
- Update **UI ↔ Backend Alignment** if new drawer/engine wiring

### Step 4: Link from 00_MASTER_PROJECT_SYSTEM_MAP

- Add a **Relationship** entry pointing to the new subsystem map
- Add a **Code relationships** row for key imports
- Optionally summarize in **Structure** or **Behavior** with "See MASTER_ATMOSPHERE_SYSTEM_MAP for detail"

---

## 3. NL / Syntax Descriptions (Required)

Every system map must include **comprehensive NL (natural language) descriptions** so that:
- AI builders understand **intent**, not just file paths
- Humans and AI use the **same vocabulary**
- Parameters, flows, and constraints are **explicitly named**

### What to include

| Element | NL description example |
|---------|-------------------------|
| **Params** | "`condenseThreshold` controls cloud over-formation; default 0.72. Higher = fewer clouds." |
| **Flow** | "AtmospherePanel onChange → atmosphereParams state → debounced applyAtmosphere → createAtmosphereOptions → recomputeAtmosphereV8." |
| **Invariant** | "FieldStack is single source of truth. Map and weather must read from same FieldStack." |
| **Failure mode** | "If bridge not called, UI changes never reach engine; user sees no change." |
| **Contract** | "AtmosphereParams.clouds.lowClouds.formationRate maps to AtmosphereV8Options.cloudFormRate (averaged with mid/high)." |

### Syntax conventions

- **Code:** `Backticks` for identifiers (params, functions, types)
- **Paths:** `world-engine-v8/core/AtmosphereV8.ts`
- **Types:** `AtmosphereParams`, `AtmosphereV8Options`
- **Flow:** Use `→` for "feeds into", `↓` for "then"

---

## 4. Code Relationship Indexing

When documenting a subsystem, index:

| Relationship type | What to capture |
|-------------------|-----------------|
| **Import** | File A imports X from file B |
| **Data flow** | UI state → bridge → engine options |
| **Callback** | onChange → applyAtmosphere → recomputeAtmosphereV8 |
| **Ref** | fieldsRef.current, atmosphereStateRef.current |
| **Dependency** | AtmosphereV8 depends on FieldStack having HEIGHT, HUMIDITY, PRESSURE |

### Format in Relationship Matrix

```markdown
| File | Imports from | Exports to |
|------|--------------|------------|
| WorldEngineStudioV12 | AtmosphereV8Bridge, AtmosphereV8 | — |
| AtmosphereV8Bridge | AtmosphereV8 (types) | mapAtmosphereParamsToV8Options |
```

---

## 5. UI ↔ Backend Alignment Rules

### Rule 1: Every editable param must have a trace

If a drawer edits a parameter, document:
- **UI param name** (e.g. `clouds.lowClouds.formationRate`)
- **Engine option name** (e.g. `cloudFormRate`)
- **Bridge function** (e.g. `mapAtmosphereParamsToV8Options`)
- **When applied** (e.g. on "Apply Changes" or debounced onChange)

### Rule 2: Gaps must be listed

If UI changes don't affect the map/simulation, add to **Open gaps** in 00_MASTER_PROJECT_SYSTEM_MAP §6 and to **Known gaps** in SAM_MASTER_INDEX §4.

### Rule 3: Bridge is canonical

The bridge (e.g. AtmosphereV8Bridge) is the **single mapping layer**. Don't bypass it. Document all param→option mappings in the subsystem map.

---

## 6. Goals ↔ Plans ↔ Code Traceability

When goals or plans change:
1. Update **Goals ↔ Plans ↔ Code** in SAM_MASTER_INDEX
2. Add **Goals ↔ Code traceability** in 00_MASTER_PROJECT_SYSTEM_MAP §7
3. Ensure subsystem maps reference the relevant plan doc

**Format:**
| Goal | Code / doc |
|------|------------|
| Ship AIM-OS v0.3 | goals/GOAL_TREE.yaml |
| Atmosphere drawer affects map | AtmosphereV8Bridge, applyAtmosphere |

---

## 7. Build Process (Future)

When the SAM compiler is wired:

```bash
# From earthdocs/SAM/ or project root
python scripts/build_monolith_v2.py
# OR
npm run build:sam
```

**Outputs:**
- `SAM_MASTER_MONOLITH.md` – Single file for AI/RAG
- `SAM_MANIFEST.json` – Section hashes, integrity root
- `SAM_INDEX.json` – Tag lookup, section IDs

**Until compiler is wired:** Edit sources directly; keep 00_MASTER_PROJECT_SYSTEM_MAP and SAM_MASTER_INDEX in sync manually.

---

## 8. Quality Checklist

Before committing SAM changes:

- [ ] All 5 dimensions present (Structure, Behavior, Interfaces, Constraints, Evidence)
- [ ] NL descriptions for params, flows, invariants
- [ ] Code relationships indexed (imports, data flow)
- [ ] UI ↔ backend alignment documented
- [ ] Open gaps listed (if any)
- [ ] Tags paired (`[TAG:X]` … `[END:TAG:X]`)
- [ ] SAM_MASTER_INDEX updated
- [ ] Links between docs correct

---

## 9. Maintenance Schedule

| Frequency | Action |
|-----------|--------|
| **Per feature** | Update SAM if new system or major wiring change |
| **Weekly** | Review open gaps; resolve or document blockers |
| **Per release** | Full SAM pass; update status, evidence, goals |
| **Per drift** | When code structure changes; update structure map and relationships |

---

**This protocol ensures SAM grows with the codebase and remains the single source of truth for system alignment.**

**Definitive SAM hub:** `knowledge_architecture/SAM/README.md`
