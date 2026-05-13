---
id: "system_first_principle_T5_quick"
system: "meta_principles"
component: null
level: "T5"
type: "quick_reference"
title: "System-First Principle - Quick Reference"
description: "500-word quick reference cheat sheet for System-First Principle"
audience: "developers, quick lookup"
confidence_threshold: 0.90
token_cost: 500
word_count: 500
created: "2025-11-04T03:30:00Z"
updated: "2025-11-04T03:30:00Z"
author: "aether"
status: "production"
tags: ["principle", "meta", "system-first", "quick-reference", "cheat-sheet", "critical", "t0-t6"]
dependencies: ["T4_SYSTEM_FIRST_PRINCIPLE.md"]
related_docs: ["T3_SYSTEM_FIRST_PRINCIPLE.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# System-First Principle - Quick Reference (≈500 words)

**Quick cheat sheet for System-First research**

---

## 🔍 **QUICK DISCOVERY**

```python
# Quick first pass
quick_result = quick_discovery(feature_name)

if quick_result.has_existing_systems:
    # Found something - do full discovery
    full_result = complete_discovery(feature_name)
else:
    # No existing systems - can proceed with new creation
    document_new_system(feature_name)
```

---

## 📋 **MANDATORY CHECKLIST**

**Before Creating New System:**
- [ ] Search codebase for similar systems
- [ ] Check SUPER_INDEX for related concepts
- [ ] Review system maps for existing capabilities
- [ ] Read documentation for existing implementations
- [ ] Identify overlaps and conflicts
- [ ] Find integration opportunities
- [ ] Document findings before building

**After Research:**
- [ ] Enhance existing rather than replace
- [ ] Integrate with existing systems
- [ ] Document gaps that actually need new work
- [ ] Create integration plan

---

## 🔧 **RESEARCH METHODS**

**Semantic Search:**
```python
results = search_codebase_semantic(query, level=IndexLevel.FILE)
```

**SUPER_INDEX Query:**
```python
results = query_super_index(concept)
```

**System Map Analysis:**
```python
results = analyze_system_maps(query)
```

**Documentation Reading:**
```python
docs = read_existing_docs(system)
```

---

## ✅ **DECISION TREE**

```
New Feature Request
    ↓
Quick Discovery
    ↓
Existing Systems Found? → YES → Full Discovery
    ↓                              ↓
    NO                            Overlaps? → YES → Enhancement Plan
    ↓                              ↓                    ↓
    NO                            NO                    Integration Plan
    ↓                              ↓
    Create New                   Create New with Integration
```

---

## 🎯 **KEY PRINCIPLES**

1. **Research FIRST** - Never create without research
2. **Enhance Rather Than Replace** - Leverage existing work
3. **Find Integration Opportunities** - Connect systems
4. **Document Everything** - Discovery, findings, plans

---

## 📊 **SUCCESS METRICS**

- **System-First Research Rate:** % of features with research completed
- **Enhancement Rate:** % of features that enhanced existing vs created new
- **Time Saved:** Hours saved by enhancing vs creating new

---

## 🚨 **VIOLATION HANDLING**

**If violation detected:**
1. STOP execution immediately
2. Log violation
3. Perform required research
4. Re-check compliance
5. Proceed only if compliant

---

**Reference:** `knowledge_architecture/AETHER_MEMORY/protocols/T3_SYSTEM_FIRST_PRINCIPLE.md`

