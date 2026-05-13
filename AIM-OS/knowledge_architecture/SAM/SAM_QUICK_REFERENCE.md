# SAM Quick Reference Card
**One-Page Guide to System Anatomy Mapping**

**Version:** 3.0.0 | **Status:** Production Ready | **Date:** 2026-01-15

---

## 🎯 CORE CONCEPT

**SAM** = Compiler-based documentation methodology that transforms **canonical sources** into **compiled monolith** with **cryptographic evidence**.

```
Sources (Truth) → [Compiler] → Monolith (Distribution) + Evidence (Proof)
```

---

## 📐 FIVE DIMENSIONS (Universal Schema)

Every system map contains:

1. **STRUCTURE** `[TAG:STRUCTURE]` - What it is (components, relationships)
2. **BEHAVIOR** `[TAG:BEHAVIOR]` - How it works (flows, operations)
3. **INTERFACES** `[TAG:INTEGRATION]` - How to use it (APIs, contracts)
4. **CONSTRAINTS** `[TAG:PERFORMANCE]` `[TAG:DEPENDENCY]` - What it cannot do (limits, assumptions)
5. **EVIDENCE** `[TAG:SUMMARY]` - Proof it works (tests, metrics)

---

## 🏗️ THREE ARTIFACTS (Non-Negotiable)

| Artifact | Type | Editable | Purpose |
|----------|------|----------|---------|
| **Canonical Sources** | `MASTER_*.md` | ✅ YES | Source of truth |
| **Compiled Monolith** | `SAM_MASTER_MONOLITH.md` | ❌ NO | AI/RAG consumption |
| **Build Evidence** | `SAM_MANIFEST.json` + `SAM_INDEX.json` | ❌ NO | Cryptographic proof |

---

## ⚙️ KEY COMMANDS

```bash
# Build artifacts
python scripts/build_monolith_v2.py

# Detect changes
python scripts/sam_patch.py detect-changes

# Extract patch (if monolith edited)
python scripts/sam_patch.py extract-patch --output patch.json

# Apply patch
python scripts/sam_patch.py apply-patch --patch patch.json

# Verify integrity (future)
sam verify
```

---

## 📊 QUALITY FORMULA

```
Perfection Score = (
    0.25 × Completeness +
    0.25 × Consistency +
    0.20 × Evidence +
    0.15 × Readability +
    0.15 × Maintenance
)
```

**Target:** ≥ 90/100 for production-ready

---

## 🏷️ TAG RULES

1. ✅ All tags MUST be registered (`sam_tags_registry.yaml`)
2. ✅ Paired tags MUST have end markers (`[END:TAG:*]`)
3. ✅ Tags CANNOT nest
4. ❌ Unknown tags FAIL build (strict mode)

---

## 📁 FILE STRUCTURE

```
project/
├── sam.config.yaml              # Build configuration
├── sam_tags_registry.yaml       # Tag governance
├── scripts/
│   ├── build_monolith_v2.py    # Compiler
│   └── sam_patch.py            # Patch channel
├── sources/
│   ├── MASTER_SYSTEM_A_MAP.md  # Canonical source 1
│   ├── MASTER_SYSTEM_B_MAP.md  # Canonical source 2
│   └── ...
├── SAM_MASTER_MONOLITH.md      # Compiled artifact (DO NOT EDIT)
├── SAM_MANIFEST.json           # Build evidence
└── SAM_INDEX.json              # Machine index
```

---

## 🔧 QUICK SETUP

1. **Create config files**: `sam.config.yaml`, `sam_tags_registry.yaml`
2. **Create source file**: `sources/MASTER_SYSTEM_MAP.md` (use template)
3. **Build**: `python scripts/build_monolith_v2.py`
4. **Verify**: Check `SAM_MANIFEST.json` for perfection score

---

## 📖 SECTION TEMPLATE

```markdown
## X. SECTION NAME

**[TAG:SECTION_TYPE] [TAG:SYSTEM_NAME]**

[Content here]

**[END:TAG:SECTION_TYPE]**
```

---

## 🎨 CONFIG TEMPLATE

```yaml
version: "3.0.0"
build:
  monolith_output: "SAM_MASTER_MONOLITH.md"
  manifest_output: "SAM_MANIFEST.json"
  index_output: "SAM_INDEX.json"
  deterministic: true

phases:
  - name: "Phase Name"
    id: "phase_id"
    order: 1
    files:
      - "sources/MASTER_FILE.md"

tags:
  registry_file: "sam_tags_registry.yaml"
  strict_mode: true

index:
  generate: true
  include_dependencies: true
  include_tags: true
```

---

## 🚨 COMMON MISTAKES

| Mistake | Fix |
|---------|-----|
| Edit monolith directly | ❌ Edit sources, rebuild |
| Unknown tags | ❌ Add to registry first |
| Missing end tags | ❌ Add `[END:TAG:*]` markers |
| Nested tags | ❌ Flatten structure |
| No evidence | ❌ Add tests/metrics |

---

## ⚡ WORKFLOW

```
1. Edit source file (MASTER_*.md)
   ↓
2. Run build script
   ↓
3. Verify artifacts generated
   ↓
4. Commit all (sources + artifacts)
   ↓
5. Repeat
```

---

## 📈 SUCCESS METRICS

**✅ Good SAM:**
- Perfection score ≥ 90
- All 5 dimensions present
- All tags registered
- Build < 5 seconds
- Evidence-based

**❌ Bad SAM:**
- Missing dimensions
- Unknown tags
- No evidence
- Outdated (>30 days)

---

## 🔗 FULL DOCUMENTATION (AIM-OS definitive)

**This folder:** `knowledge_architecture/SAM/` – hub and quick reference.

**Complete protocol:** `knowledge_architecture/PROTOCOLS/SAM_PROTOCOL_COMPLETE.md`

**Protocol index:** `knowledge_architecture/PROTOCOLS/SAM_PROTOCOL_INDEX.md`

**How to add/update maps:** `knowledge_architecture/SAM/SAM_GROWTH_PROTOCOL.md`

---

## 💡 KEY PRINCIPLES

1. **SAM is a compiler** (not a file)
2. **Sources are truth** (monolith is artifact)
3. **Evidence is proof** (cryptographic verification)
4. **Universal schema** (5 dimensions always)
5. **Tag governance** (registry prevents sprawl)

---

## 🎯 REMEMBER

- ✅ **Edit sources** (MASTER_*.md)
- ❌ **Never edit monolith** (auto-generated)
- ✅ **Use templates** (universal schema)
- ✅ **Register tags** (before using)
- ✅ **Provide evidence** (tests, metrics)
- ✅ **Rebuild after changes** (keep in sync)

---

**For details, see [SAM_PROTOCOL_COMPLETE.md](../PROTOCOLS/SAM_PROTOCOL_COMPLETE.md).**
