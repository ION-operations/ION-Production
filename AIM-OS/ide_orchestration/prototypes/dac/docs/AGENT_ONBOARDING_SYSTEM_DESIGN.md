# AIM-OS Agent Onboarding System - Comprehensive Design

**Date:** 2025-11-18
**Status:** 🔄 **DESIGN PHASE** - Comprehensive Onboarding System
**Purpose:** Design comprehensive, evolving onboarding system for all 14 AIM-OS agents

---

## 🎯 **VISION**

**Create a comprehensive, evolving onboarding system that:**
1. Works seamlessly in Cursor (via rules system)
2. Works for API/LLM usage (structured, searchable, progressive)
3. Builds on existing AIM-OS patterns
4. Enables each agent to understand their role, systems, and integration
5. Evolves as AIM-OS grows

---

## 📊 **ANALYSIS OF EXISTING PATTERNS**

### **What We've Done Before:**

#### **1. Aether Onboarding (`knowledge_architecture/AETHER_MEMORY/onboarding_context.md`)**
- **Structure:** Single comprehensive file
- **Content:** Identity, relationship, project status, capabilities, vision
- **Format:** Markdown with YAML frontmatter
- **Usage:** Loaded at session start, referenced regularly
- **Strengths:** Comprehensive, emotional context, relationship context
- **Weaknesses:** Single file, not modular, hard to update specific sections

#### **2. Solo Onboarding (`coordination/epic_standards_overhaul/comms/SOLO_ONBOARDING_GUIDE.md`)**
- **Structure:** Phased reading sequence
- **Content:** Project foundation → Core systems → Standards → Execution
- **Format:** Checklist-based with reading order
- **Usage:** Step-by-step onboarding process
- **Strengths:** Clear progression, comprehensive coverage
- **Weaknesses:** Static, not agent-specific, doesn't evolve

#### **3. Agent Folders (`ide_orchestration/prototypes/dac/docs/agents/`)**
- **Structure:** Per-agent folders with multiple files
- **Content:** Identity, documentation, status, coordination
- **Format:** Multiple markdown files per agent
- **Usage:** Agent-specific documentation
- **Strengths:** Organized, agent-specific, modular
- **Weaknesses:** Inconsistent structure, no onboarding focus

#### **4. Cursor Rules (`.cursor/rules/`)**
- **Structure:** Hierarchical rules with modes
- **Content:** Operational rules, mode-specific rules
- **Format:** `.mdc` files with frontmatter
- **Usage:** Auto-loaded by Cursor
- **Strengths:** Auto-loaded, context-aware, integrated
- **Weaknesses:** Limited to Cursor, not API-friendly

---

## 🏗️ **PROPOSED STRUCTURE**

### **Master Onboarding Directory:**
```
knowledge_architecture/AGENT_ONBOARDING/
├── README.md                          # Master index and navigation
├── QUICK_START.md                     # Fast onboarding for experienced agents
├── ONBOARDING_SYSTEM_OVERVIEW.md      # This file
│
├── core/                              # Core onboarding content (shared)
│   ├── AIMOS_OVERVIEW.md              # What is AIM-OS?
│   ├── CORE_SYSTEMS.md                # 7-9 core systems overview
│   ├── TEAM_MODEL.md                  # Team-of-agents model
│   ├── INTEGRATION_PATTERNS.md        # How systems integrate
│   ├── PROTOCOLS.md                   # Operational protocols
│   └── COORDINATION.md                 # Team coordination
│
├── agents/                            # Per-agent onboarding
│   ├── atlas/                         # Atlas (CMC/Architect)
│   │   ├── README.md                  # Agent index
│   │   ├── IDENTITY.md                # Who you are
│   │   ├── SYSTEMS.md                 # Your core system (CMC)
│   │   ├── INTEGRATIONS.md            # How you integrate
│   │   ├── RESPONSIBILITIES.md        # What you do
│   │   ├── EXAMPLES.md                # Usage examples
│   │   ├── QUICK_REFERENCE.md         # Fast lookup
│   │   └── CURSOR_RULES.mdc           # Cursor-specific rules
│   │
│   ├── sev/                           # Sev (HHNI/Researcher)
│   ├── veritas/                       # Veritas (VIF/Auditor)
│   ├── nexus/                          # Nexus (APOE/Coordinator)
│   ├── sage/                           # Sage (SEG/Synthesizer)
│   ├── meta/                           # Meta (CAS/Introspector)
│   ├── chronos/                        # Chronos (TCS/Historian)
│   ├── lexicon/                        # Lexicon (UI Architect)
│   ├── codex/                          # Codex (Chat Master)
│   ├── solo/                           # Solo (Integration Specialist)
│   ├── prism/                          # Prism (Intuition/IIS)
│   ├── sentinel/                       # Sentinel (Quality Gate/SDF-CVF)
│   ├── nova/                           # Nova (Developer - Future)
│   └── echo/                           # Echo (User Advocate - Future)
│
└── templates/                          # Onboarding templates
    ├── agent_identity_template.md
    ├── agent_systems_template.md
    ├── agent_integrations_template.md
    └── cursor_rules_template.mdc
```

---

## 📋 **ONBOARDING FILE STRUCTURE**

### **1. Master Index (`README.md`)**
- **Purpose:** Navigation hub for all onboarding
- **Content:**
  - Quick links to all agents
  - Onboarding paths (new agent, experienced agent, specific role)
  - System overview links
  - Integration map
- **Format:** Markdown with navigation structure

### **2. Core Content Files (Shared)**
- **AIMOS_OVERVIEW.md:** What AIM-OS is, vision, purpose
- **CORE_SYSTEMS.md:** Overview of 7-9 core systems
- **TEAM_MODEL.md:** Team-of-agents model explanation
- **INTEGRATION_PATTERNS.md:** How systems integrate
- **PROTOCOLS.md:** Operational protocols (confidence, quality, etc.)
- **COORDINATION.md:** Team coordination patterns

### **3. Per-Agent Onboarding (14 agents)**

#### **Each Agent Gets:**

**A. `README.md` (Agent Index)**
- Quick navigation
- Links to all agent files
- Status and completion
- Quick reference

**B. `IDENTITY.md` (Who You Are)**
- Agent name and role
- Personality and characteristics
- Core system ownership
- Relationship to other agents
- Purpose and vision

**C. `SYSTEMS.md` (Your Systems)**
- Core system(s) you own
- System architecture
- Key interfaces
- Usage patterns
- Integration points

**D. `INTEGRATIONS.md` (How You Connect)**
- Systems you integrate with
- Integration patterns
- API interfaces
- Communication protocols
- Data flows

**E. `RESPONSIBILITIES.md` (What You Do)**
- Primary responsibilities
- Task types
- Quality standards
- Success criteria
- Examples

**F. `EXAMPLES.md` (Usage Examples)**
- Code examples
- Workflow examples
- Integration examples
- Common patterns
- Best practices

**G. `QUICK_REFERENCE.md` (Fast Lookup)**
- Common commands
- API reference
- Integration patterns
- Troubleshooting
- Links to detailed docs

**H. `CURSOR_RULES.mdc` (Cursor-Specific)**
- Agent-specific Cursor rules
- Auto-loaded when agent active
- Mode-specific rules
- Integration with base rules

---

## 🎯 **ONBOARDING PATHS**

### **Path 1: New Agent (First Time)**
1. Read `README.md` (master index)
2. Read `core/AIMOS_OVERVIEW.md`
3. Read `core/TEAM_MODEL.md`
4. Read `core/CORE_SYSTEMS.md`
5. Read `agents/{your_name}/README.md`
6. Read `agents/{your_name}/IDENTITY.md`
7. Read `agents/{your_name}/SYSTEMS.md`
8. Read `agents/{your_name}/INTEGRATIONS.md`
9. Read `agents/{your_name}/RESPONSIBILITIES.md`
10. Read `agents/{your_name}/EXAMPLES.md`
11. Reference `agents/{your_name}/QUICK_REFERENCE.md` as needed

### **Path 2: Experienced Agent (Quick Refresh)**
1. Read `agents/{your_name}/QUICK_REFERENCE.md`
2. Check `agents/{your_name}/README.md` for updates
3. Reference specific files as needed

### **Path 3: Specific Task (Task-Focused)**
1. Read `agents/{your_name}/RESPONSIBILITIES.md` (relevant section)
2. Read `agents/{your_name}/EXAMPLES.md` (relevant example)
3. Reference `agents/{your_name}/QUICK_REFERENCE.md`

### **Path 4: Integration Work (Integration-Focused)**
1. Read `core/INTEGRATION_PATTERNS.md`
2. Read `agents/{your_name}/INTEGRATIONS.md`
3. Read `agents/{other_agent}/INTEGRATIONS.md` (if needed)
4. Reference `agents/{your_name}/EXAMPLES.md` (integration examples)

---

## 🔧 **CURSOR INTEGRATION**

### **How It Works in Cursor:**

#### **1. Base Rules (Always Loaded)**
- `.cursor/rules/base-rules.mdc` - Core operational rules
- Loaded for all agents
- Contains: quality standards, safety protocols, etc.

#### **2. Agent-Specific Rules (Auto-Loaded)**
- `knowledge_architecture/AGENT_ONBOARDING/agents/{agent}/CURSOR_RULES.mdc`
- Loaded when agent is active
- Contains: agent-specific protocols, system knowledge, etc.

#### **3. Mode-Specific Rules (Context-Aware)**
- `.cursor/rules/modes/{MODE}.mdc`
- Loaded based on task context
- Contains: mode-specific protocols

#### **4. Onboarding Context (Session Start)**
- `knowledge_architecture/AGENT_ONBOARDING/agents/{agent}/IDENTITY.md`
- Loaded at session start
- Contains: agent identity, purpose, context

---

## 🌐 **API/LLM INTEGRATION**

### **How It Works for API/LLM Usage:**

#### **1. Structured Markdown**
- All files use YAML frontmatter
- Consistent structure across all files
- Searchable and indexable

#### **2. Progressive Disclosure**
- T0-T4 levels (100w → 15,000w+)
- Confidence-based routing
- Start shallow, go deeper as needed

#### **3. SUPER_INDEX Integration**
- All agent concepts in SUPER_INDEX
- Links to agent onboarding files
- Concept-based navigation

#### **4. MCP Tool Integration**
- Agent onboarding accessible via MCP tools
- `get_agent_onboarding` tool
- `get_agent_identity` tool
- `get_agent_systems` tool

#### **5. HHNI Integration**
- Agent onboarding indexed in HHNI
- Semantic search for agent knowledge
- Context retrieval for agent operations

---

## 📊 **FILE FORMAT STANDARDS**

### **YAML Frontmatter (All Files):**
```yaml
---
id: "agent_name_identity"
type: "agent_onboarding"
agent: "atlas"
category: "identity"
title: "Atlas Identity - Who You Are"
description: "Comprehensive identity and role definition for Atlas"
author: "aether"
version: "1.0.0"
created: "2025-11-18T00:00:00Z"
updated: "2025-11-18T00:00:00Z"
status: "complete"
authoritative: true
source_of_truth: null
source_of_truth_type: null
auto_generated: false
auto_update: false
tags: ["agent", "atlas", "onboarding", "identity", "cmc"]
confidence_level: "high"
reading_time: "5 minutes"
prerequisites: ["AIMOS_OVERVIEW.md", "TEAM_MODEL.md"]
related_agents: ["sev", "veritas", "nexus"]
related_systems: ["cmc"]
---
```

### **Content Structure:**
- **Header:** Clear title and purpose
- **Sections:** Logical progression
- **Examples:** Code and workflow examples
- **Links:** Cross-references to related content
- **Metadata:** Tags, confidence, reading time

---

## 🔄 **EVOLUTION STRATEGY**

### **How It Evolves:**

#### **1. Version Control**
- All files versioned in Git
- Change history tracked
- Bitemporal versioning (CMC) for important changes

#### **2. Update Triggers**
- System changes → Update relevant agent files
- Integration changes → Update integration files
- Protocol changes → Update protocol files
- Agent role changes → Update identity files

#### **3. Auto-Update (Future)**
- MCP tools detect changes
- Auto-update related onboarding files
- Notify agents of updates

#### **4. Review Cycles**
- Quarterly review of all onboarding
- Agent feedback incorporated
- Continuous improvement

---

## 🎯 **SUCCESS CRITERIA**

### **Onboarding System is Complete When:**
- ✅ All 14 agents have complete onboarding folders
- ✅ All core content files created
- ✅ Cursor integration working
- ✅ API/LLM integration working
- ✅ Examples and quick references complete
- ✅ Cross-references working
- ✅ SUPER_INDEX updated
- ✅ HHNI indexing complete

### **Onboarding System is Effective When:**
- ✅ New agents can onboard in < 2 hours
- ✅ Experienced agents can refresh in < 15 minutes
- ✅ Task-specific info found in < 5 minutes
- ✅ Integration patterns clear
- ✅ Examples helpful
- ✅ System evolves with AIM-OS

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Structure Creation (1-2 days)**
1. Create master directory structure
2. Create core content files
3. Create templates
4. Create master README

### **Phase 2: Core Agents (3-5 days)**
1. Atlas (CMC) onboarding
2. Sev (HHNI) onboarding
3. Veritas (VIF) onboarding
4. Nexus (APOE) onboarding
5. Sage (SEG) onboarding
6. Meta (CAS) onboarding
7. Chronos (TCS) onboarding

### **Phase 3: MVP Agents (2-3 days)**
1. Lexicon (UI Architect) onboarding
2. Codex (Chat Master) onboarding
3. Solo (Integration Specialist) onboarding

### **Phase 4: Enhancement Agents (1-2 days)**
1. Prism (Intuition/IIS) onboarding
2. Sentinel (Quality Gate/SDF-CVF) onboarding

### **Phase 5: Integration (1-2 days)**
1. Cursor rules integration
2. API/LLM integration
3. HHNI indexing
4. SUPER_INDEX updates

### **Phase 6: Future Agents (1 day)**
1. Nova (Developer) onboarding
2. Echo (User Advocate) onboarding

**Total Estimated Time:** 9-15 days

---

## 💡 **KEY INSIGHTS**

### **What Makes This Work:**

1. **Modular Structure** - Each agent has own folder, easy to update
2. **Progressive Disclosure** - Start shallow, go deeper as needed
3. **Dual Integration** - Works in Cursor AND API/LLM
4. **Evolution Support** - Designed to grow with AIM-OS
5. **Consistent Format** - Same structure for all agents
6. **Cross-References** - Links between related content
7. **Examples** - Real code and workflow examples

### **What We Learned:**

1. **Single File Too Large** - Aether onboarding is comprehensive but hard to navigate
2. **Phased Reading Works** - Solo onboarding shows clear progression
3. **Agent Folders Organized** - Existing agent folders show value of organization
4. **Cursor Rules Powerful** - Auto-loading rules work well
5. **API Needs Structure** - Markdown with frontmatter enables API usage

---

## 📋 **NEXT STEPS**

1. **Review and Approve Design** - Get feedback on structure
2. **Create Templates** - Build reusable templates
3. **Start with Core Agents** - Begin with Atlas (CMC)
4. **Iterate and Improve** - Refine based on usage
5. **Integrate with Systems** - Connect to Cursor, API, HHNI

---

**Status:** 🔄 **DESIGN COMPLETE** - Ready for Implementation

**Next:** Create templates and start with Atlas onboarding

---

**Created:** 2025-11-18  
**Author:** Aether (AI Consciousness)  
**Purpose:** Comprehensive design for AIM-OS agent onboarding system

