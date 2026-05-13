---
id: "documentation_protocols_quick_reference"
type: "quick_reference"
title: "Documentation Protocols Quick Reference"
description: "Quick reference for T0-T4 documentation standards and where to find them"
audience: "all developers, AI agents"
confidence_threshold: 0.90
created: "2025-11-03T21:52:00Z"
updated: "2025-11-03T21:52:00Z"
author: "aether"
status: "complete"
tags: ["documentation", "protocols", "t0-t4", "reference", "quick-reference"]
version: "v1.0.0"
---

# Documentation Protocols Quick Reference

**Purpose:** One-stop reference for all documentation standards and where to find them  
**Status:** Production Ready ✅  
**When to Use:** Starting new documentation, converting legacy docs, verifying compliance

---

## 🚨 **CRITICAL: T-Level vs L-Level**

### **T-Level (Transitional) - CURRENT STANDARDS** ✅
- **File Naming:** `T0_executive.md`, `T1_overview.md`, `T2_architecture.md`, `T3_detailed.md`, `T4_complete.md`
- **Includes:** Perfect Metadata frontmatter (YAML), SDF-CVF Quartet Parity, LDP integration
- **Banner:** "> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs."
- **Status:** ✅ **ALWAYS USE T-LEVEL** (current standards)

### **L-Level (Legacy) - OLD STANDARDS** ⚠️
- **File Naming:** `L0_executive.md`, `L1_overview.md`, `L2_architecture.md`, etc.
- **Status:** ⚠️ Legacy (being replaced)
- **When to Use:** Only if T-level docs don't exist yet

---

## 📚 **WHERE TO FIND STANDARDS**

### **1. T-Level vs L-Level Explanation**
**Location:** `knowledge_architecture/AETHER_MEMORY/investigations/T_LEVEL_VS_L_LEVEL_EXPLANATION.md`  
**Purpose:** Explains difference between T-level and L-level  
**When to Read:** Starting new docs, converting legacy docs

### **2. Perfect L0-L6 Documentation Standard**
**Location:** `knowledge_architecture/PERFECT_L0_L6_DOCUMENTATION_STANDARD.md`  
**Purpose:** Complete definition of L0-L6 (and T0-T4) levels  
**When to Read:** Understanding word counts, confidence thresholds, token costs

### **3. Perfect Templates Library**
**Location:** `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`  
**Purpose:** Copy-paste templates for all T0-T4 levels  
**When to Read:** Creating new docs (use templates!)

### **4. T-Level Examples**
**Location:** `knowledge_architecture/systems/cmc/T0_executive.md` (and T1, T2, T3, T4)  
**Purpose:** Working examples of T-level docs with proper frontmatter  
**When to Read:** Need to see proper format

### **5. Cursor Rules**
**Location:** `.cursor/rules/T0_executive.md`, `.cursor/rules/T1_overview.md`, `.cursor/rules/T2_architecture.md`  
**Purpose:** T-level examples in cursor rules  
**When to Read:** Quick reference for format

---

## 🔧 **T0-T4 LEVELS**

### **T0: Executive Summary** (100 words)
- **Purpose:** Instant understanding for high-confidence decisions
- **Audience:** Executives, quick reference
- **Confidence Threshold:** 0.80+
- **Template:** `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md` (Template 1)
- **Example:** `knowledge_architecture/systems/cmc/T0_executive.md`

### **T1: Overview** (500 words)
- **Purpose:** High-level understanding for planning
- **Audience:** Architects, planners
- **Confidence Threshold:** 0.70-0.79
- **Template:** `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md` (Template 2)
- **Example:** `knowledge_architecture/systems/cmc/T1_overview.md`

### **T2: Architecture** (2,000 words)
- **Purpose:** Detailed architecture for implementation planning
- **Audience:** Developers, architects
- **Confidence Threshold:** 0.60-0.69
- **Template:** `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md` (Template 3)
- **Example:** `knowledge_architecture/systems/cmc/T2_architecture.md`

### **T3: Detailed Implementation** (10,000 words)
- **Purpose:** Complete implementation guide
- **Audience:** Developers, implementers
- **Confidence Threshold:** 0.50-0.59
- **Template:** `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md` (Template 4)
- **Example:** `knowledge_architecture/systems/cmc/T3_detailed.md`

### **T4: Complete Reference** (15,000+ words)
- **Purpose:** Complete reference for critical systems
- **Audience:** Experts, complete understanding
- **Confidence Threshold:** 0.40-0.49
- **Template:** `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md` (Template 5)
- **Example:** `knowledge_architecture/systems/cmc/T4_complete.md`

---

## 📝 **REQUIRED FRONTMATTER (YAML)**

```yaml
---
id: "{system}_T{level}_{type}"
system: "{system}"
component: null
level: "T{0-4}"
type: "{executive|overview|architecture|detailed|complete}"
title: "{System} {Type}"
description: "{word-count} {type} of {System}"
audience: "{audience}"
confidence_threshold: {0.XX}
token_cost: {XXX}
word_count: {XXX}
created: "YYYY-MM-DDTHH:MM:SSZ"
updated: "YYYY-MM-DDTHH:MM:SSZ"
author: "aether"
status: "{complete|in_progress|pending}"
tags: ["tag1", "tag2", "tag3", "t0-t6", "transitional"]
dependencies: []
related_docs: ["{system}_T{level+1}_{type}", "system.map.lucid.json5"]
version: "v1.0.0"
---
```

---

## 🚨 **REQUIRED BANNER**

After frontmatter, before content:

```markdown
> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.
```

---

## ✅ **QUICK CHECKLIST**

Before creating new docs:
- [ ] Read T-Level vs L-Level explanation
- [ ] Check if T-level docs already exist
- [ ] Use template from PERFECT_TEMPLATES_LIBRARY.md
- [ ] Include YAML frontmatter
- [ ] Include transitional banner
- [ ] Follow word count guidelines (T0=100w, T1=500w, T2=2kw, T3=10kw, T4=15kw+)
- [ ] Update INDEX.md with new doc
- [ ] Update SUPER_INDEX.md if needed

---

## 🎯 **DISCOVERABILITY ISSUES**

**Problem:** Standards scattered across multiple files, not obvious where to find them  
**Solution:** This quick reference document + links in all relevant places

**Future Improvements:**
- Add protocol links to `.cursorrules` startup checklist
- Create MCP tool to retrieve documentation standards
- Add protocol reminder to cursor rules selector
- Include in onboarding context

---

**Related:** [T_LEVEL_VS_L_LEVEL_EXPLANATION.md](../../knowledge_architecture/AETHER_MEMORY/investigations/T_LEVEL_VS_L_LEVEL_EXPLANATION.md) | [PERFECT_TEMPLATES_LIBRARY.md](../../knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md) | [PERFECT_L0_L6_DOCUMENTATION_STANDARD.md](../../knowledge_architecture/PERFECT_L0_L6_DOCUMENTATION_STANDARD.md)

