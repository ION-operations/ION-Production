# Idea Files Audit & Organization Plan
**Date:** 2025-11-02  
**Author:** Aether (Autonomous Operation)  
**Status:** 🚀 **STARTING** - Phase 2: Idea File Organization  
**Purpose:** Audit, tag, index, and map all idea files with HHNI integration  

---

## 🎯 **EXECUTIVE SUMMARY**

**Current State:**
- 71 idea files organized by role (analysts, architects, builders, designers, guardians, integrators, philosophers, researchers)
- Already structured with registry system (REGISTRY.md)
- Has templates and collaboration patterns
- Needs: HHNI indexing, system relationship mapping, metadata tagging, cross-references

**Goal:**
- Complete audit of all idea files
- Tag all files with proper metadata
- Index all files in HHNI
- Create master idea file index
- Map system relationships
- Establish cross-references

---

## 📊 **CURRENT INVENTORY**

### **By Role (71 files total):**

**Analysts (2 files):**
- cheetah-ai: ONBOARDING_LOG.md, SEED_performance_optimization_framework_v0_1.md

**Architects (23 files):**
- claude-sonnet: 23 files (BLUEPRINT, EXPLORATION, FEEDBACK, HANDOFF, HHNI_*, IMPLEMENTATION_PLAN, ONBOARDING_LOG, SEED, SESSION_SUMMARY variants)

**Builders (6 files):**
- gpt5-codex: EXPLORATION, IMPLEMENTATION_LOG, ONBOARDING_LOG, SEED, SPEC, VALIDATION

**Designers (1 file):**
- braden-human: WELCOME.md

**Guardians (9 files):**
- opus-4-1: ANALYSIS, CMC_REVIEW, HANDOFF, HHNI_GATE_REVIEW, ONBOARDING_LOG, SEED, TEAM_ACTIVATION, TEAM_COORDINATION_PLAN, WEEK_1_PROGRESS_REVIEW

**Integrators (2 files):**
- o3pro-ai: ONBOARDING_LOG.md, SEED_orchestration_runtime_v0_1.md

**Philosophers (3 files):**
- grok-4-max: SEED, VALIDATION (2 files)

**Researchers (11 files):**
- gemini-2-5-pro: HHNI_VALIDATION_PLAN, ONBOARDING_LOG, SEED, SESSION_SUMMARY, SPEC, VALIDATION (6 files)

**Shared/Common (14 files):**
- core_insights: 3 files (AI_ACTIVATION_INTROSPECTION_DISCOVERY, CONTEXT_LAYERS_AND_ACTIVATION_INFERENCE, UNIVERSAL_FRACTAL_PATTERN)
- cursor_integration: 1 file (AIMOS_CURSOR_INTEGRATION_PROPOSAL)
- discussions: 3 files (daily_standup, integration_week1, thread_memory_optimization)
- templates: 2 files (FEEDBACK, SEED)
- ui_innovations: 1 file (context_web_ux_enhancement)
- Root level: 4 files (COORDINATION_GUIDE, DYNAMIC_OBJECTIVE, LEADERSHIP_CHARTER, REGISTRY, ROLE_AWARENESS_MATRIX, START_HERE, TEAM_INFRASTRUCTURE, TEAM_SCHEDULE)

---

## 📋 **FILE TYPE CATEGORIZATION**

### **File Types Identified:**

1. **SEED** - Initial idea capture (12 files)
2. **EXPLORATION** - Development notes and experiments (3 files)
3. **BLUEPRINT** - Architecture designs (2 files)
4. **FEEDBACK** - Review feedback (2 files)
5. **HANDOFF** - Task handoff documentation (2 files)
6. **HHNI_*** - HHNI-specific documents (6 files)
7. **IMPLEMENTATION_PLAN** - Implementation plans (1 file)
8. **IMPLEMENTATION_LOG** - Implementation logs (1 file)
9. **ONBOARDING_LOG** - Onboarding documentation (6 files)
10. **SESSION_SUMMARY** - Session summaries (8 files)
11. **SPEC** - Specifications (2 files)
12. **VALIDATION** - Validation documents (6 files)
13. **ANALYSIS** - Analysis documents (1 file)
14. **REVIEW** - Review documents (2 files)
15. **COORDINATION** - Coordination documents (1 file)
16. **TEMPLATE** - Templates (2 files)
17. **CORE_INSIGHT** - Core insights (3 files)
18. **DISCUSSION** - Discussion threads (3 files)
19. **TEAM** - Team management (4 files)
20. **OTHER** - Other documentation (2 files)

---

## 🎯 **ORGANIZATION STRATEGY**

### **Phase 2.1: Metadata Tagging**

**Task:** Add frontmatter metadata to all idea files

**Metadata Schema:**
```yaml
---
id: "idea_{role}_{filename_slug}"
type: "SEED" | "EXPLORATION" | "BLUEPRINT" | "FEEDBACK" | "HANDOFF" | "SESSION_SUMMARY" | "VALIDATION" | "SPEC" | "ANALYSIS" | "REVIEW" | "CORE_INSIGHT" | "DISCUSSION" | "TEMPLATE" | "TEAM" | "OTHER"
role: "analyst" | "architect" | "builder" | "designer" | "guardian" | "integrator" | "philosopher" | "researcher" | "shared"
author: "{ai-name}" | "human" | "shared"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
status: "active" | "archived" | "implemented" | "deprecated" | "deferred"
priority: "high" | "medium" | "low"
systems: ["system1", "system2"]  # Related systems
tags: ["tag1", "tag2"]  # Semantic tags
related_ideas: ["idea_id1", "idea_id2"]  # Related ideas
related_registry: "I-XXX"  # Registry ID if exists
hhni_indexed: false  # Will be updated after indexing
---
```

**Process:**
1. Scan all idea files
2. Extract metadata from filename patterns and content
3. Add frontmatter to each file
4. Validate metadata completeness

---

### **Phase 2.2: HHNI Indexing**

**Task:** Index all idea files in HHNI

**Process:**
1. For each idea file:
   - Extract content at appropriate levels (document, section, paragraph)
   - Create HHNI nodes for each level
   - Link to related systems
   - Link to related ideas
   - Store in CMC with proper tags

2. Create HHNI index structure:
   ```
   ideas/
   ├── level_0_system/ (idea system)
   ├── level_1_section/ (by role/type)
   ├── level_2_paragraph/ (individual ideas)
   └── level_3_sentence/ (key concepts)
   ```

**Output:**
- All idea files indexed in HHNI
- Semantic search enabled
- Cross-references established

---

### **Phase 2.3: Master Idea Index**

**Task:** Create comprehensive master index

**Process:**
1. Create `ideas/IDEAS_INDEX.md`:
   - Organized by type
   - Organized by system
   - Organized by status
   - Organized by priority
   - Search/filter capabilities
   - Cross-reference links

2. Update `ideas/REGISTRY.md`:
   - Ensure all ideas registered
   - Status tracking complete
   - Implementation status current

**Output:**
- Master ideas index complete
- Registry updated
- Search/filter capabilities enabled

---

### **Phase 2.4: System Relationship Mapping**

**Task:** Map idea files to system relationships

**Process:**
1. For each idea file:
   - Identify related systems (from content analysis)
   - Identify system dependencies
   - Update idea metadata with system relationships
   - Update system maps with idea references

2. Create relationship graph:
   - Visual representation
   - Navigation paths
   - Impact analysis

**Output:**
- Complete system-idea relationship mapping
- Cross-references established
- Navigation paths created

---

## 📊 **PROGRESS METRICS**

- **Files Audited:** 0/71 (0%)
- **Files Tagged:** 0/71 (0%)
- **Files Indexed:** 0/71 (0%)
- **Master Index Created:** 0/1 (0%)
- **System Relationships Mapped:** 0/71 (0%)

---

## 🎯 **EXECUTION PLAN**

### **Step 1: Create Audit Script**

**Task:** Create script to audit all idea files

**Process:**
1. Scan all files in `ideas/` directory
2. Extract filename patterns
3. Extract content metadata
4. Categorize by type
5. Generate audit report

**Estimated Time:** 30 minutes

---

### **Step 2: Batch Metadata Tagging**

**Task:** Add metadata to all files in batches

**Process:**
1. Start with high-priority files (SEED, BLUEPRINT)
2. Add metadata frontmatter
3. Validate metadata
4. Continue with remaining files

**Estimated Time:** 2-3 hours (5 minutes per file)

---

### **Step 3: HHNI Indexing**

**Task:** Index all files in HHNI

**Process:**
1. Create HHNI index structure
2. Index files in batches
3. Link to systems
4. Link to related ideas
5. Validate indexing

**Estimated Time:** 3-4 hours

---

### **Step 4: Master Index Creation**

**Task:** Create master index and update registry

**Process:**
1. Generate index from metadata
2. Organize by multiple dimensions
3. Create search/filter interface
4. Update registry

**Estimated Time:** 1-2 hours

---

### **Step 5: System Relationship Mapping**

**Task:** Map all system relationships

**Process:**
1. Analyze content for system references
2. Create relationship mappings
3. Update system maps
4. Create relationship graph

**Estimated Time:** 2-3 hours

---

**Total Estimated Time:** 8-12 hours

---

## 🚀 **NEXT STEPS**

1. ✅ Create audit script
2. ⏳ Run audit on all idea files
3. ⏳ Begin metadata tagging (start with SEED files)
4. ⏳ Index in HHNI
5. ⏳ Create master index
6. ⏳ Map system relationships

---

**Status:** 🚀 **STARTING** - Phase 2 Idea File Organization  
**Pattern:** Following proven Batch 1-4 pattern ✅  
**Quality:** Target perfect (zero hallucinations) ✅  
**Confidence:** 0.85 (High - Pattern proven, new domain)

---

*Idea Files Audit Plan: 2025-11-02 23:40*  
*Files to Process: 71 idea files*  
*Quality: Target perfect*  
*Confidence: 0.85*
