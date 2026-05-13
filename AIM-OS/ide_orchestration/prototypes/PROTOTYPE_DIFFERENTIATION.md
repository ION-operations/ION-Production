# IDE Layout Prototype Differentiation Guide

**Date:** 2025-11-07  
**Purpose:** Clearly differentiate between Lex's prototype and Codex's prototype

---

## 🎯 **PROTOTYPE OVERVIEW**

### **Lex's Prototype**
- **Location:** `ide_orchestration/prototypes/lex/`
- **Design Document:** `IDE_LAYOUT_PROTOTYPE_LEX.md`
- **Approach:** AIM-OS Native First
- **Status:** Independent prototype - Lex's own design and implementation
- **Focus:** Making invisible AIM-OS systems visible and actionable

### **Codex's Prototype**
- **Location:** `ide_orchestration/prototypes/codex/`
- **Design Document:** `IDE_LAYOUT_PROTOTYPE_CODEX.md`
- **Approach:** Architecture-First (extends Lucid Orchestrator)
- **Status:** Extension of Codex's existing work - Lex completing Codex's design
- **Focus:** Architecture visualization and orchestration management
- **Responsibility:** Lex is responsible for completing Codex's prototype implementation

---

## 🔍 **KEY DIFFERENCES**

### **1. Foundation**

**Lex's Prototype:**
- Built from scratch
- Leverages past IDE implementations (`IDELayout.tsx`, `MonacoEditor.tsx`, etc.)
- New architecture designed for AIM-OS integration

**Codex's Prototype:**
- Extends Codex's existing Lucid Orchestrator (`packages/lucid_orchestrator/`)
- Uses existing React components (`LucidOrchestratorMain.tsx`)
- Builds on existing Graph Engine, Spec Engine, Timeline Engine

### **2. Unique Features**

**Lex's Prototype:**
- Context Web (HHNI visualization)
- Evolution Explorer (Timeline ↔ Chain bidirectional graph)
- Consciousness Visualization (attention heatmap, confidence landscape)
- VIF confidence indicators throughout
- SEG contradiction detection in UI
- Deep AIM-OS integration in every panel

**Codex's Prototype:**
- Lucid Orchestrator four-pane interface (Code, Blueprint, Spec, Timeline)
- ChainSpec Explorer (Epic/Phase/Workstream/Task tree)
- Orchestration Canvas (visual orchestration)
- Quality Gates Dashboard
- Predictive Progress Tracking
- Architecture-first visualization

### **3. Design Philosophy**

**Lex's Prototype:**
- **AIM-OS Native First:** All AIM-OS systems are first-class citizens
- **Revolutionary UX:** New ways to interact with AI consciousness
- **Developer Workflow:** Optimized for actual coding workflows
- **Past Learnings:** Applies lessons from previous IDE implementations

**Codex's Prototype:**
- **Architecture-First:** UI reflects underlying architecture
- **Orchestration-Centric:** Focus on managing AI orchestration
- **Scalability:** Designed for complex, multi-agent projects
- **ChainSpec-Driven:** UI reflects ChainSpec structure

### **4. Panel Focus**

**Lex's Prototype:**
- 20+ panels with deep AIM-OS integration
- Revolutionary panels (Context Web, Evolution Explorer, Consciousness Visualization)
- Standard IDE panels enhanced with AIM-OS features
- VIF confidence indicators on code and chat

**Codex's Prototype:**
- Extends Lucid Orchestrator's four panes
- Adds ChainSpec visualization panels
- Adds orchestration management panels
- Architecture and orchestration-focused panels

---

## 📊 **COMPARISON TABLE**

| Aspect | Lex's Prototype | Codex's Prototype |
|--------|----------------|-------------------|
| **Foundation** | Built from scratch | Extends Lucid Orchestrator |
| **Approach** | AIM-OS Native First | Architecture-First |
| **Unique Features** | Context Web, Evolution Explorer, Consciousness Visualization | Lucid Orchestrator, ChainSpec Explorer, Orchestration Canvas |
| **Focus** | Making AIM-OS visible | Architecture visualization |
| **Panels** | 20+ AIM-OS-native panels | Extends 4-pane + orchestration panels |
| **Status** | Independent | Extension of existing work |
| **Responsibility** | Lex's own work | Lex completing Codex's work |

---

## 🎯 **WHEN TO USE WHICH**

### **Use Lex's Prototype When:**
- You want deep AIM-OS integration in every panel
- You need revolutionary UX features (Context Web, Evolution Explorer)
- You want to see VIF confidence and SEG contradictions in UI
- You need a fresh, AIM-OS-native IDE experience

### **Use Codex's Prototype When:**
- You want architecture-first visualization
- You need ChainSpec and orchestration management
- You want to leverage existing Lucid Orchestrator work
- You need orchestration-focused IDE experience

---

## 📝 **IMPLEMENTATION STATUS**

### **Lex's Prototype:**
- ✅ Design document complete
- ✅ Project structure created
- ✅ Type system defined
- ✅ Mock data created
- ✅ Core layout implemented
- ✅ Several panels implemented
- ⏳ Remaining panels to implement
- ⏳ Polish and testing

### **Codex's Prototype:**
- ✅ Design document complete (aligned with Lucid Orchestrator)
- ✅ Existing Lucid Orchestrator components identified
- ⏳ Integration with Lucid Orchestrator
- ⏳ ChainSpec panels to build
- ⏳ Orchestration panels to build
- ⏳ Polish and testing

---

## 🔗 **RELATED DOCUMENTS**

- **Lex's Design:** `ide_orchestration/prototypes/lex/IDE_LAYOUT_PROTOTYPE_LEX.md`
- **Codex's Design:** `ide_orchestration/prototypes/codex/IDE_LAYOUT_PROTOTYPE_CODEX.md`
- **Mission Brief:** `ide_orchestration/prototypes/IDE_LAYOUT_PROTOTYPE_MISSION.md`
- **Progress Tracker:** `ide_orchestration/prototypes/PROGRESS_TRACKER.md`

---

**Status:** Both prototypes clearly differentiated and ready for implementation  
**Responsibility:** Lex is building both prototypes independently

