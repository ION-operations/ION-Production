---
id: "organic_data_freshness_T1_overview"
system: "organic_data_freshness"
component: null
level: "T1"
type: "overview"
title: "Organic Data Freshness System - Overview"
description: "500-word overview of system ensuring onboarding always uses current data"
audience: "developers, architects, quick understanding"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-06T22:05:00Z"
updated: "2025-11-06T22:05:00Z"
author: "aether"
status: "complete"
tags: ["protocol", "onboarding", "data_freshness", "auto_update", "organic"]
dependencies: ["ORGANIC_DATA_FRESHNESS_T0_EXECUTIVE.md"]
related_docs: ["ORGANIC_DATA_FRESHNESS_SYSTEM_DESIGN.md", "ORGANIC_DATA_FRESHNESS_COMPLETE.md", "ORGANIC_DATA_FRESHNESS_SDFCVF_RELATIONSHIP.md"]
version: "v1.0.0"
authoritative: false
source_of_truth: "scripts/detect_source_of_truth.py"
source_of_truth_type: "code"
auto_generated: false
auto_update: false
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# Organic Data Freshness System - Overview

**Date:** 2025-11-06  
**Purpose:** Ensure onboarding always uses current data through organization, tagging, and auto-update relationships  
**Status:** ✅ Complete (6 phases implemented)  
**Problem Solved:** Outdated information provided during onboarding due to lack of automatic prioritization

---

## 🎯 **CORE PRINCIPLE**

**If AIM-OS is correctly organized and protocols are met, onboarding should NATURALLY use current data. No manual fixes needed.**

The system prevents outdated data organically through:
1. **Leading Docs Tagged** - Metadata identifies authoritative sources (`authoritative: true`)
2. **Dependency Tracking** - Docs declare sources they depend on (`source_of_truth`)
3. **Auto-Update Relationships** - Dependent docs update when sources change
4. **Onboarding Prioritization** - Onboarding naturally loads leading docs first
5. **Protocol Enforcement** - Protocols ensure this behavior happens automatically

---

## 🏗️ **SYSTEM ARCHITECTURE (5 Layers)**

### **Layer 1: Leading Docs Identification**
- Metadata tag: `authoritative: true` or `source_of_truth: true`
- Leading docs: `SOURCE_OF_TRUTH.yaml`, `GOAL_TREE.yaml`, `SUPER_INDEX.md`, `LATEST_LOGS.md`, `onboarding_context.md`
- Detection: Scripts scan for authoritative metadata

### **Layer 2: Dependency Declaration**
- Metadata fields: `dependencies`, `source_of_truth`, `source_of_truth_type`
- Tracking: `scripts/track_doc_dependencies.py` builds dependency graph
- Storage: `cross_system_connections.yaml` includes `doc_dependencies` section

### **Layer 3: Auto-Update Relationships**
- Mechanism: `scripts/generate_cross_references.py` extends with auto-update methods
- Trigger: Source file changes detected
- Action: Dependent docs updated automatically

### **Layer 4: File System Monitoring**
- Monitor: `packages/mcp_data_integration/file_system_monitor.py` watches source files
- Detection: Real-time change detection
- Response: Triggers doc updates via `CrossReferenceGenerator`

### **Layer 5: Standalone Auto-Updater**
- Tool: `scripts/auto_update_dependent_docs.py`
- Features: Update from source, update all, check stale
- Integration: Can be called manually or via file monitor

---

## 🔄 **WORKFLOW**

1. **Source Changes** → File monitor detects change
2. **Dependency Lookup** → Find all dependent docs
3. **Auto-Update** → Update dependent docs from source
4. **Onboarding** → Load leading docs first (authoritative: true)
5. **Freshness Check** → Verify docs are current before use

---

## 🔗 **INTEGRATION**

**Complementary to SDF-CVF Quartet Parity:**
- **SDF-CVF:** Enforces semantic alignment (code/docs/tests/traces align semantically)
- **Organic Data Freshness:** Enforces temporal alignment (docs stay current with sources)
- **Together:** Complete quality assurance (semantic + temporal)

**Related Systems:**
- `cross_system_connections.yaml` - Dependency graph storage
- `generate_cross_references.py` - Cross-reference generation
- `file_system_monitor.py` - Real-time monitoring
- `GROUNDING.mdc` - Onboarding protocol enforcement

---

## ✅ **STATUS**

**Phase 1:** ✅ Metadata standards extended  
**Phase 2:** ✅ Dependency tracking implemented  
**Phase 3:** ✅ Auto-update relationships added  
**Phase 4:** ✅ File system monitoring extended  
**Phase 5:** ✅ Standalone auto-updater created  
**Phase 6:** ✅ Onboarding protocol enhanced

**Result:** System operational, outdated data prevented organically.

---

*Overview by: Aether*  
*Purpose: Quick understanding of Organic Data Freshness System*  
*Next: T2 Architecture for detailed design*

