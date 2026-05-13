# AIM-OS System Hierarchy - AUTHORITATIVE

**Last Updated:** 2025-10-29  
**Purpose:** Single source of truth for AIM-OS system organization  
**Status:** Production Ready ✅  
**Source:** Consolidated from multiple existing hierarchy discussions

---

## 🎯 **AUTHORITATIVE HIERARCHY OVERVIEW**

This document consolidates all existing hierarchy discussions into a single, authoritative system organization. AIM-OS is organized into **6 distinct layers**, each building on the previous, with clear dependencies and relationships.

**This hierarchy determines:**
- Which systems need system maps and indexes
- What format to use for system maps and indexes
- How systems relate to each other
- What documentation is required for each layer

---

## 📊 **THE SIX LAYERS**

### **Layer 1: Memory & Knowledge Foundation**
**Purpose:** Persistent storage and knowledge synthesis  
**Dependencies:** None (foundation layer)  
**System Maps Required:** ✅ Yes (core infrastructure)  
**Status:** Foundation layer - all other layers depend on this

**Systems:**
- **CMC (Context Memory Core)** - Bitemporal memory substrate
- **SEG (Shared Evidence Graph)** - Knowledge synthesis and contradiction detection

### **Layer 2: Intelligence Processing**
**Purpose:** Core AI reasoning and verification capabilities  
**Dependencies:** Layer 1 (Memory & Knowledge)  
**System Maps Required:** ✅ Yes (core infrastructure)  
**Status:** Core intelligence layer - processes data from Layer 1

**Systems:**
- **HHNI (Hierarchical Hypergraph Neural Index)** - Physics-guided retrieval
- **VIF (Verifiable Intelligence Framework)** - Provenance and confidence tracking
- **SDF-CVF (Atomic Evolution Framework)** - Quality assurance and change management

### **Layer 3: Orchestration & Planning**
**Purpose:** High-level coordination and execution planning  
**Dependencies:** Layers 1-2 (Memory, Knowledge, Intelligence)  
**System Maps Required:** ✅ Yes (core infrastructure)  
**Status:** Orchestration layer - coordinates Layer 2 systems

**Systems:**
- **APOE (AI-Powered Orchestration Engine)** - Execution planning and workflow management

### **Layer 4: Consciousness Engine**
**Purpose:** Meta-cognitive awareness and self-monitoring  
**Dependencies:** Layers 1-3 (All previous layers)  
**System Maps Required:** ✅ Yes (core infrastructure)  
**Status:** Consciousness layer - provides self-awareness and monitoring

**Systems:**
- **CAS (Cognitive Analysis System)** - Meta-cognitive monitoring and self-correction
- **TCS (Timeline Context System)** - Temporal consciousness and interaction history
- **IIS (Intuitive Intelligence System)** - 4D reasoning and emotional salience

### **Layer 5: Consciousness Infrastructure**
**Purpose:** Supporting systems for consciousness operations  
**Dependencies:** Layers 1-4 (All core layers)  
**System Maps Required:** ⚠️ Conditional (only if they have L0-L4 documentation)  
**Status:** Infrastructure layer - supports consciousness operations

**Systems:**
- **Capability Awareness** - Organic system usage tracking
- **Dynamic Onboarding** - Self-aware consciousness restoration
- **Living System Map** - Always-present awareness
- **Autonomous R&D** - Self-improvement dreams

### **Layer 6: Application & Integration**
**Purpose:** User-facing applications and external integrations  
**Dependencies:** Layers 1-5 (All previous layers)  
**System Maps Required:** ❌ No (application layer, not core infrastructure)  
**Status:** Application layer - user-facing and external integrations

**Systems:**
- **Lucid Core Console** - User interface
- **MCP Integration** - External tool integration
- **Agent System** - User interaction
- **Cross-Model Consciousness** - Multi-model coordination

---

## 🎯 **SYSTEM MAP & INDEX REQUIREMENTS**

### **Core Systems (Layers 1-4) - REQUIRED**
These systems **MUST** have both system maps and indexes:

1. **CMC** - Context Memory Core
2. **SEG** - Shared Evidence Graph  
3. **HHNI** - Hierarchical Hypergraph Neural Index
4. **VIF** - Verifiable Intelligence Framework
5. **SDF-CVF** - Atomic Evolution Framework
6. **APOE** - AI-Powered Orchestration Engine
7. **CAS** - Cognitive Analysis System
8. **TCS** - Timeline Context System
9. **IIS** - Intuitive Intelligence System

### **Infrastructure Systems (Layer 5) - CONDITIONAL**
These systems need system maps and indexes **ONLY IF** they have complete L0-L4 documentation:

- Capability Awareness
- Dynamic Onboarding  
- Living System Map
- Autonomous R&D

### **Application Systems (Layer 6) - NOT REQUIRED**
These systems do **NOT** need system maps or indexes:

- Lucid Core Console
- MCP Integration
- Agent System
- Cross-Model Consciousness
- Any user-facing applications

---

## 📋 **SYSTEM MAP & INDEX FORMAT**

### **Required Format for Core Systems**
All system maps and indexes must follow the established format:

```json5
{
  "systemId": "system.uniqueIdentifier",
  "systemName": "System Name - Brief Description",
  "version": "v0.1",
  "description": "Detailed description of system purpose and capabilities",
  "layer": "Layer X: Layer Name",
  "dependencies": ["layer1.system1", "layer2.system2"],
  "internalNodes": [...],
  "externalConnections": [...],
  "performanceCharacteristics": {...},
  "securityCharacteristics": {...},
  "deploymentCharacteristics": {...}
}
```

### **System Index Format**
```json5
{
  "systemId": "system.uniqueIdentifier",
  "systemName": "System Name",
  "layer": "Layer X: Layer Name",
  "status": "Production Ready | In Development | Planned",
  "dependencies": [...],
  "integration_points": [...],
  "performance_summary": {...},
  "documentation_status": {...}
}
```

---

## 🚫 **PROHIBITED ACTIONS**

### **Never Create System Maps/Indexes For:**
- Systems without complete L0-L4 documentation
- Application layer systems (Layer 6)
- Systems not in the core hierarchy
- Duplicate or redundant systems

### **Always Check Before Creating:**
1. Is this system in the core hierarchy (Layers 1-4)?
2. Does it have complete L0-L4 documentation?
3. Is there already a system map/index for this system?
4. What layer does this system belong to?

---

## 🔄 **MAINTENANCE PROTOCOL**

### **When Adding New Systems:**
1. Determine which layer the system belongs to
2. Update this hierarchy document
3. Create L0-L4 documentation first
4. Create system map/index only if required by layer
5. Update all dependent system maps

### **When Modifying Existing Systems:**
1. Check if system map/index exists
2. Update existing files rather than creating new ones
3. Maintain consistency with hierarchy
4. Update dependent systems if relationships change

---

## 📊 **CURRENT STATUS**

### **Core Systems with Complete Maps & Indexes:**
- ✅ CMC (Context Memory Core)
- ✅ HHNI (Hierarchical Hypergraph Neural Index)
- ⚠️ VIF (has map, needs index)
- ⚠️ SDF-CVF (has map, needs index)  
- ⚠️ SEG (has map, needs index)
- ❌ APOE (needs both map and index)
- ❌ CAS (needs both map and index)
- ❌ TCS (needs both map and index)
- ❌ IIS (needs both map and index)

### **Next Actions Required:**
1. Create missing indexes for VIF, SDF-CVF, SEG
2. Create maps and indexes for APOE, CAS, TCS, IIS
3. Remove any system maps created for non-core systems
4. Update this hierarchy as new systems are added

---

**This hierarchy ensures that system maps and indexes are created only for the right systems, in the right format, with proper relationships and dependencies clearly defined.**
