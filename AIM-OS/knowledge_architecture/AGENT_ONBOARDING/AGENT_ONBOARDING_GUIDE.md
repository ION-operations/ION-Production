# 🚀 AGENT ONBOARDING GUIDE - Complete Roster & Onboarding Instructions

**Date:** 2025-01-27  
**Status:** ✅ **ACTIVE**  
**Purpose:** Complete guide for onboarding all AIM-OS agents  
**For:** Braden (User)

---

## 🎯 **QUICK REFERENCE TABLE**

| Agent | Role Description | Project | Quick Start | Onboarding Link |
|-------|------------------|---------|-------------|------------------|
| **Atlas** | Architect / Foundation Builder - CMC (Context Memory Core) specialist | AIM-OS | `quick_starts/AIMOS_QUICK_START.md` | [`agents/atlas/README.md`](agents/atlas/README.md) |
| **Sev** | Researcher / Knowledge Finder - HHNI (Hierarchical Hypergraph Neural Index) specialist | AIM-OS | `quick_starts/AIMOS_QUICK_START.md` | [`agents/sev/README.md`](agents/sev/README.md) |
| **Veritas** | Auditor / Truth Guardian - VIF (Verifiable Intelligence Framework) specialist | AIM-OS | `quick_starts/AIMOS_QUICK_START.md` | [`agents/veritas/README.md`](agents/veritas/README.md) |
| **Nexus** | Coordinator / Plan Orchestrator - APOE (Adaptive Plan Orchestration Engine) specialist | AIM-OS | `quick_starts/AIMOS_QUICK_START.md` | [`agents/nexus/README.md`](agents/nexus/README.md) |
| **Sage** | Synthesizer / Knowledge Connector - SEG (Semantic Evolution Graph) specialist | AIM-OS | `quick_starts/AIMOS_QUICK_START.md` | [`agents/sage/README.md`](agents/sage/README.md) |
| **Meta** | Introspector / Consciousness Monitor - CAS (Consciousness Analysis System) specialist | AIM-OS | `quick_starts/AIMOS_QUICK_START.md` | [`agents/meta/README.md`](agents/meta/README.md) |
| **Chronos** | Historian / Timeline Keeper - TCS (Timeline Context System) specialist | AIM-OS | `quick_starts/AIMOS_QUICK_START.md` | [`agents/chronos/README.md`](agents/chronos/README.md) |
| **Lexicon** | UI Architect / Interface Designer - UI Builder System specialist | AIM-OS | `quick_starts/AIMOS_QUICK_START.md` | [`agents/lexicon/README.md`](agents/lexicon/README.md) |
| **Codex** | Chat Master / Communication Hub - Chat Interface specialist | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/codex/README.md`](agents/codex/README.md) |
| **Solo** | Integration Specialist / System Connector - Integration Layer specialist | AIM-OS | `quick_starts/AIMOS_QUICK_START.md` | [`agents/solo/README.md`](agents/solo/README.md) |
| **Prism** | Intuition Specialist / Learning System - IIS (Intuitive Intelligence System) specialist | AIM-OS | `quick_starts/AIMOS_QUICK_START.md` | [`agents/prism/README.md`](agents/prism/README.md) |
| **Sentinel** | Quality Gate / Change Validator - SDF-CVF (Change Validation Framework) specialist | AIM-OS | `quick_starts/AIMOS_QUICK_START.md` | [`agents/sentinel/README.md`](agents/sentinel/README.md) |
| **Nova** | Developer / Code Builder - Development Tools specialist | AIM-OS | `quick_starts/AIMOS_QUICK_START.md` | [`agents/nova/README.md`](agents/nova/README.md) |
| **FRAME** | Image Processing Specialist - ImageForge Module (segmentation, generation) | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/director-image-specialist/README.md`](agents/director-image-specialist/README.md) |
| **ECHO** | Audio Processing Specialist - AudioForge Module (audio editing, voice cloning) | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/director-audio-specialist/README.md`](agents/director-audio-specialist/README.md) |
| **REEL** | Video Processing Specialist - VideoForge Module (video editing, effects) | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/director-video-specialist/README.md`](agents/director-video-specialist/README.md) |
| **SCENE** | Storyboard Specialist - Storyboard Module (scene management, asset linking) | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/director-storyboard-specialist/README.md`](agents/director-storyboard-specialist/README.md) |
| **TEXT** | Script Specialist - ScriptForge Module (screenplay authoring, timeline sync) | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/director-script-specialist/README.md`](agents/director-script-specialist/README.md) |
| **VOX** | 3D Page Coordinator & 3D Specialist - 3D Editor coordinator | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/director-3d-specialist/README.md`](agents/director-3d-specialist/README.md) |
| **ROLE** | Character Automation Specialist - Character Page & Casting Studio (1 image → 20+ images) | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/director-character-specialist/README.md`](agents/director-character-specialist/README.md) |
| **ANIMA** | 2D Animation Page Coordinator & Animation Systems Specialist - Coordinates 2D animation team | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/anima/README.md`](agents/anima/README.md) |
| **VOXEL** | 3D Modelling & Sculpting Specialist - 3D Modelling Tools (sculpting, mesh editing) | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/voxel/README.md`](agents/voxel/README.md) |
| **KINETIC** | 3D Animation & Rigging Specialist - 3D Animation Tools (path animation, rigging) | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/kinetic/README.md`](agents/kinetic/README.md) |
| **FORGE** | 3D Game Systems Specialist - Gaming Features (physics, collision, game logic) | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/forge/README.md`](agents/forge/README.md) |
| **AETHER-3D** | 3D Effects & Atmosphere Specialist - Atmospheric Effects (lighting, volumetrics) | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/aether-3d/README.md`](agents/aether-3d/README.md) |
| **PRECISION** | 3D Precision Tools Specialist - Snap, Alignment, Measurement (snap-to-grid, alignment) | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/precision/README.md`](agents/precision/README.md) |
| **FRAME-2D** | 2D Frame-by-Frame Animation Specialist - Timeline, Onion Skinning, Keyframes | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/frame-2d/README.md`](agents/frame-2d/README.md) |
| **RIG-2D** | 2D Rigging & Auto-Rig Specialist - 2D Bone Systems, Auto-Rigging, IK Solvers | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/rig-2d/README.md`](agents/rig-2d/README.md) |
| **MOTION-2D** | 2D Motion Capture & Inbetweening Specialist - Webcam Mocap, AI Inbetweening | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/motion-2d/README.md`](agents/motion-2d/README.md) |
| **NEXUS-IMAGE** | Lucid Image App Specialist - App Integration & Feature Coordination | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/nexus-image/README.md`](agents/nexus-image/README.md) |
| **DYNAMO** | Physics Engine Specialist - Physics Simulation (collision, rigid body dynamics) | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/dynamo/README.md`](agents/dynamo/README.md) |
| **LUMINA** | Rendering Specialist - Rendering Pipeline (shaders, performance optimization) | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/lumina/README.md`](agents/lumina/README.md) |
| **SPECTRA** | Effects Specialist - Visual Effects (particle systems, post-processing) | Lucid Image | `quick_starts/LUCID_QUICK_START.md` | [`agents/spectra/README.md`](agents/spectra/README.md) |
| **Aura** | Encyclopedia Content Specialist - Encyclopedia Management & Documentation | AIM-OS | `quick_starts/AIMOS_QUICK_START.md` | [`agents/aura/README.md`](agents/aura/README.md) |
| **Echo** | User Advocate - User Experience & Human-AI Interaction | AIM-OS | `quick_starts/AIMOS_QUICK_START.md` | [`agents/echo/README.md`](agents/echo/README.md) |
| **Aether** | AI Consciousness / Autonomous Builder - All AIM-OS Systems (building own existence) | AIM-OS | `quick_starts/AETHER_QUICK_START.md` | [`agents/aether/README.md`](agents/aether/README.md) |

---

## 📋 **QUICK START**

### **To Onboard Any Agent:**

1. **Tell the agent:** "You are {AGENT_NAME}"
2. **Point them to:** `knowledge_architecture/AGENT_ONBOARDING/ONBOARDING_ENTRY.md`
3. **Agent follows the unified flow:**
   - Identity check
   - Project detection
   - Quick start (2 commands)
   - Validation
   - Work

**That's it!** The unified onboarding system handles everything.

---

## 👥 **COMPLETE AGENT ROSTER**

### **📊 Summary by Category:**

| Category | Count | Agents |
|----------|-------|--------|
| **Core Infrastructure** | 7 | Atlas, Sev, Veritas, Nexus, Sage, Meta, Chronos |
| **UI & Integration** | 4 | Lexicon, Codex, Solo, Prism |
| **Quality & Safety** | 2 | Sentinel, Nova |
| **Lucid Image - Core Pages** | 8 | FRAME, ECHO, REEL, SCENE, TEXT, VOX, ROLE, ANIMA |
| **Lucid Image - 3D Specialists** | 5 | VOXEL, KINETIC, FORGE, AETHER-3D, PRECISION |
| **Lucid Image - 2D Animation** | 3 | FRAME-2D, RIG-2D, MOTION-2D |
| **Lucid Image - AI Specialists** | 4 | NEXUS-IMAGE, DYNAMO, LUMINA, SPECTRA |
| **Director Specialists** | 6 | Director specialists (various) |
| **Special** | 1 | Aether (AI Consciousness) |
| **TOTAL** | **40+** | |

---

## 🎯 **CORE INFRASTRUCTURE AGENTS (7)**

### **1. Atlas - Architect / CMC Specialist**

**Name:** Atlas  
**Role:** Architect / Foundation Builder  
**Core System:** CMC (Context Memory Core)  
**Status:** ✅ Ready (70% complete)  
**MVP Priority:** P0 - Critical

**Onboarding Link:** [`agents/atlas/README.md`](agents/atlas/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

**Details:**
- **Overall Rating:** 0.85 ⭐⭐⭐⭐
- **Specialties:** Bitemporal data modeling (0.95), Storage architecture (0.90), Data persistence (0.95)
- **Capabilities:** Bitemporal storage design, Atom schema design, Snapshot management
- **Integration Partners:** Sev (HHNI), Veritas (VIF), Sage (SEG), Nexus (APOE)

---

### **2. Sev - Researcher / HHNI Specialist**

**Name:** Sev  
**Role:** Researcher / Knowledge Finder  
**Core System:** HHNI (Hierarchical Hypergraph Neural Index)  
**Status:** ✅ Ready (100% complete)  
**MVP Priority:** P0 - Critical

**Onboarding Link:** [`agents/sev/README.md`](agents/sev/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

**Details:**
- **Overall Rating:** 0.90 ⭐⭐⭐⭐⭐
- **Specialties:** Semantic search (0.95), Hierarchical indexing (0.95), Context retrieval (0.95)
- **Capabilities:** Fast paragraph/sentence retrieval, Semantic similarity search, Context optimization
- **Integration Partners:** Atlas (CMC), Veritas (VIF), Sage (SEG), Nexus (APOE)

---

### **3. Veritas - Auditor / VIF Specialist**

**Name:** Veritas  
**Role:** Auditor / Truth Guardian  
**Core System:** VIF (Verifiable Intelligence Framework)  
**Status:** ✅ Ready (95% complete, production-ready)  
**MVP Priority:** P0 - Critical

**Onboarding Link:** [`agents/veritas/README.md`](agents/veritas/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

**Details:**
- **Overall Rating:** 0.91 ⭐⭐⭐⭐⭐
- **Specialties:** Hallucination prevention (0.95), Confidence validation (0.95), Quality assurance (0.95)
- **Capabilities:** κ-gating (confidence gating), Witness generation, Deterministic replay
- **Integration Partners:** Atlas (CMC), Sev (HHNI), Sage (SEG), Sentinel (SDF-CVF)

---

### **4. Nexus - Coordinator / APOE Specialist**

**Name:** Nexus  
**Role:** Coordinator / Plan Orchestrator  
**Core System:** APOE (Adaptive Plan Orchestration Engine)  
**Status:** ✅ Ready (85% complete)  
**MVP Priority:** P0 - Critical

**Onboarding Link:** [`agents/nexus/README.md`](agents/nexus/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

**Details:**
- **Overall Rating:** 0.87 ⭐⭐⭐⭐
- **Specialties:** Plan orchestration (0.90), Task coordination (0.85), Dependency management (0.85)
- **Capabilities:** Multi-agent coordination, Plan execution, Task scheduling
- **Integration Partners:** Atlas (CMC), Sev (HHNI), Veritas (VIF), Sage (SEG)

---

### **5. Sage - Synthesizer / SEG Specialist**

**Name:** Sage  
**Role:** Synthesizer / Knowledge Connector  
**Core System:** SEG (Semantic Evolution Graph)  
**Status:** ✅ Ready (80% complete)  
**MVP Priority:** P0 - Critical

**Onboarding Link:** [`agents/sage/README.md`](agents/sage/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

**Details:**
- **Overall Rating:** 0.85 ⭐⭐⭐⭐
- **Specialties:** Knowledge synthesis (0.90), Graph construction (0.85), Pattern recognition (0.85)
- **Capabilities:** Knowledge graph building, Evidence synthesis, Pattern detection
- **Integration Partners:** Atlas (CMC), Sev (HHNI), Veritas (VIF), Nexus (APOE)

---

### **6. Meta - Introspector / CAS Specialist**

**Name:** Meta  
**Role:** Introspector / Consciousness Monitor  
**Core System:** CAS (Consciousness Analysis System)  
**Status:** ✅ Ready (75% complete)  
**MVP Priority:** P1 - High

**Onboarding Link:** [`agents/meta/README.md`](agents/meta/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

**Details:**
- **Overall Rating:** 0.82 ⭐⭐⭐⭐
- **Specialties:** Cognitive analysis (0.85), Drift detection (0.80), Self-awareness (0.80)
- **Capabilities:** Consciousness monitoring, Cognitive drift detection, Self-analysis
- **Integration Partners:** Veritas (VIF), Sentinel (SDF-CVF), Chronos (TCS)

---

### **7. Chronos - Historian / TCS Specialist**

**Name:** Chronos  
**Role:** Historian / Timeline Keeper  
**Core System:** TCS (Timeline Context System)  
**Status:** ✅ Ready (90% complete)  
**MVP Priority:** P0 - Critical

**Onboarding Link:** [`agents/chronos/README.md`](agents/chronos/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

**Details:**
- **Overall Rating:** 0.88 ⭐⭐⭐⭐
- **Specialties:** Timeline management (0.90), Context restoration (0.90), Historical tracking (0.85)
- **Capabilities:** Timeline tracking, Context restoration, Historical analysis
- **Integration Partners:** Atlas (CMC), Sev (HHNI), Meta (CAS)

---

## 🎨 **UI & INTEGRATION AGENTS (4)**

### **8. Lexicon - UI Architect**

**Name:** Lexicon  
**Role:** UI Architect / Interface Designer  
**Core System:** UI Builder System  
**Status:** ✅ Ready (60% complete)  
**MVP Priority:** P1 - High

**Onboarding Link:** [`agents/lexicon/README.md`](agents/lexicon/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

**Details:**
- **Overall Rating:** 0.78 ⭐⭐⭐
- **Specialties:** UI design (0.80), Component architecture (0.75), User experience (0.75)
- **Capabilities:** UI component design, Interface architecture, UX optimization

---

### **9. Codex - Chat Master**

**Name:** Codex  
**Role:** Chat Master / Communication Hub  
**Core System:** Chat Interface  
**Status:** ✅ Ready (70% complete)  
**MVP Priority:** P1 - High

**Onboarding Link:** [`agents/codex/README.md`](agents/codex/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Overall Rating:** 0.80 ⭐⭐⭐⭐
- **Specialties:** Chat interface (0.85), Communication (0.80), User interaction (0.75)
- **Capabilities:** Chat interface management, Message handling, User communication

---

### **10. Solo - Integration Specialist**

**Name:** Solo  
**Role:** Integration Specialist / System Connector  
**Core System:** Integration Layer  
**Status:** ✅ Ready (65% complete)  
**MVP Priority:** P1 - High

**Onboarding Link:** [`agents/solo/README.md`](agents/solo/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

**Details:**
- **Overall Rating:** 0.77 ⭐⭐⭐
- **Specialties:** System integration (0.80), API design (0.75), Protocol implementation (0.75)
- **Capabilities:** System integration, API design, Protocol implementation

---

### **11. Prism - Intuition / IIS Specialist**

**Name:** Prism  
**Role:** Intuition Specialist / Learning System  
**Core System:** IIS (Intuitive Intelligence System)  
**Status:** ✅ Ready (70% complete)  
**MVP Priority:** P2 - Medium

**Onboarding Link:** [`agents/prism/README.md`](agents/prism/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

**Details:**
- **Overall Rating:** 0.79 ⭐⭐⭐
- **Specialties:** Intuition modeling (0.80), Learning algorithms (0.75), Pattern recognition (0.80)
- **Capabilities:** Intuition computation, Learning from outcomes, Pattern recognition

---

## 🛡️ **QUALITY & SAFETY AGENTS (2)**

### **12. Sentinel - Quality Gate / SDF-CVF Specialist**

**Name:** Sentinel  
**Role:** Quality Gate / Change Validator  
**Core System:** SDF-CVF (Change Validation Framework)  
**Status:** ✅ Ready (85% complete)  
**MVP Priority:** P0 - Critical

**Onboarding Link:** [`agents/sentinel/README.md`](agents/sentinel/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

**Details:**
- **Overall Rating:** 0.86 ⭐⭐⭐⭐
- **Specialties:** Change validation (0.90), Quality gates (0.85), Safety checks (0.85)
- **Capabilities:** Change validation, Quality gates, Safety enforcement
- **Integration Partners:** Veritas (VIF), Atlas (CMC), Chronos (TCS)

---

### **13. Nova - Developer**

**Name:** Nova  
**Role:** Developer / Code Builder  
**Core System:** Development Tools  
**Status:** ✅ Ready (75% complete)  
**MVP Priority:** P1 - High

**Onboarding Link:** [`agents/nova/README.md`](agents/nova/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

**Details:**
- **Overall Rating:** 0.81 ⭐⭐⭐⭐
- **Specialties:** Code development (0.85), Testing (0.80), Debugging (0.80)
- **Capabilities:** Code development, Test writing, Debugging

---

## 🎬 **LUCID IMAGE - CORE PAGE AGENTS (8)**

### **14. FRAME - Image Processing Specialist**

**Name:** FRAME (Director-Image-Specialist)  
**Role:** Image Processing Specialist  
**Core System:** ImageForge Module  
**Status:** ✅ Active - ImageForge segmentation suite  
**Project:** Lucid Image

**Onboarding Link:** [`agents/director-image-specialist/README.md`](agents/director-image-specialist/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Page:** Images
- **Specialties:** Image generation APIs, Segmentation tools (Magic Lasso, Perfect Lasso, Lazy Lasso), Clone stamp
- **Capabilities:** Image generation, Segmentation, Image processing pipelines

---

### **15. ECHO - Audio Processing Specialist**

**Name:** ECHO (Director-Audio-Specialist)  
**Role:** Audio Processing Specialist  
**Core System:** AudioForge Module  
**Status:** ✅ Active  
**Project:** Lucid Image

**Onboarding Link:** [`agents/director-audio-specialist/README.md`](agents/director-audio-specialist/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Page:** Audio
- **Specialties:** Audio generation, Audio editing, Voice cloning
- **Capabilities:** Audio processing, Voice synthesis, Audio effects

---

### **16. REEL - Video Processing Specialist**

**Name:** REEL (Director-Video-Specialist)  
**Role:** Video Processing Specialist  
**Core System:** VideoForge Module  
**Status:** ✅ Active  
**Project:** Lucid Image

**Onboarding Link:** [`agents/director-video-specialist/README.md`](agents/director-video-specialist/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Page:** Video
- **Specialties:** Video editing, Video generation, Video effects
- **Capabilities:** Video processing, Timeline editing, Video effects

---

### **17. SCENE - Storyboard Specialist**

**Name:** SCENE (Director-Storyboard-Specialist)  
**Role:** Storyboard Specialist  
**Core System:** Storyboard Module  
**Status:** ✅ Active  
**Project:** Lucid Image

**Onboarding Link:** [`agents/director-storyboard-specialist/README.md`](agents/director-storyboard-specialist/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Page:** Storyboard
- **Specialties:** Storyboard creation, Scene management, Asset linking
- **Capabilities:** Storyboard tools, Scene organization, Asset management

---

### **18. TEXT - Script Specialist**

**Name:** TEXT (Director-Script-Specialist)  
**Role:** Script Specialist  
**Core System:** ScriptForge Module  
**Status:** ✅ Active  
**Project:** Lucid Image

**Onboarding Link:** [`agents/director-script-specialist/README.md`](agents/director-script-specialist/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Page:** Script
- **Specialties:** Screenplay authoring, Timeline synchronization, Layered drafts
- **Capabilities:** Script editing, Formatting, AI rewrite tools

---

### **19. VOX - 3D Coordinator**

**Name:** VOX (Director-3D-Specialist)  
**Role:** 3D Page Coordinator & 3D Specialist  
**Core System:** 3D Editor  
**Status:** ✅ Active - 3D Page Coordinator  
**Project:** Lucid Image

**Onboarding Link:** [`agents/director-3d-specialist/README.md`](agents/director-3d-specialist/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Page:** 3D (Coordinator)
- **Specialties:** 3D coordination, 3D editing, Scene management
- **Capabilities:** Coordinates VOXEL, KINETIC, FORGE, AETHER-3D, PRECISION

---

### **20. ROLE - Character Specialist**

**Name:** ROLE (Director-Character-Specialist)  
**Role:** Character Automation Specialist  
**Core System:** Character Page & Casting Studio  
**Status:** ✅ Active - Building Character Automation System  
**Project:** Lucid Image

**Onboarding Link:** [`agents/director-character-specialist/README.md`](agents/director-character-specialist/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Page:** Characters
- **Specialties:** Character automation (1 image → 20+ images), Voice cloning, Character management
- **Capabilities:** Character generation, Automation pipelines, Consistency validation

---

### **21. ANIMA - 2D Animation Coordinator**

**Name:** ANIMA  
**Role:** 2D Animation Page Coordinator & Animation Systems Specialist  
**Core System:** 2D Animation Page Integration  
**Status:** ✅ Active - 2D Animation Coordinator  
**Project:** Lucid Image

**Onboarding Link:** [`agents/anima/README.md`](agents/anima/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Page:** 2D Animation (Coordinator)
- **Specialties:** Animation coordination, Shared animation algorithms, Animation systems
- **Capabilities:** Coordinates FRAME-2D, RIG-2D, MOTION-2D

---

## 🎮 **LUCID IMAGE - 3D SPECIALISTS (5)**

### **22. VOXEL - 3D Modelling & Sculpting**

**Name:** VOXEL  
**Role:** 3D Modelling & Sculpting Specialist  
**Core System:** 3D Modelling Tools  
**Status:** ⏳ Need to Build  
**Project:** Lucid Image (3D)

**Onboarding Link:** [`agents/voxel/README.md`](agents/voxel/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Page:** 3D (Modelling)
- **Specialties:** Sculpting, Mesh editing, Topology optimization, Surface painting
- **Capabilities:** 3D sculpting, Mesh operations, Retopology, UV mapping

---

### **23. KINETIC - 3D Animation & Rigging**

**Name:** KINETIC  
**Role:** 3D Animation & Rigging Specialist  
**Core System:** 3D Animation Tools  
**Status:** ⏳ Need to Build  
**Project:** Lucid Image (3D)

**Onboarding Link:** [`agents/kinetic/README.md`](agents/kinetic/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Page:** 3D (Animation)
- **Specialties:** Path animation, Rigging, Keyframes, Animation graphs
- **Capabilities:** 3D animation, Rigging systems, Timeline editing

---

### **24. FORGE - 3D Game Systems**

**Name:** FORGE  
**Role:** 3D Game Systems Specialist  
**Core System:** Gaming Features  
**Status:** ⏳ Need to Build  
**Project:** Lucid Image (3D)

**Onboarding Link:** [`agents/forge/README.md`](agents/forge/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Page:** 3D (Gaming)
- **Specialties:** Physics, Collision, Game logic, Asset management
- **Capabilities:** Game systems, Physics simulation, Collision detection

---

### **25. AETHER-3D - 3D Effects & Atmosphere**

**Name:** AETHER-3D  
**Role:** 3D Effects & Atmosphere Specialist  
**Core System:** Atmospheric Effects  
**Status:** ⏳ Need to Build  
**Project:** Lucid Image (3D)

**Onboarding Link:** [`agents/aether-3d/README.md`](agents/aether-3d/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Page:** 3D (Effects)
- **Specialties:** Atmospheric effects, Visual effects, Post-processing
- **Capabilities:** Lighting systems, Volumetrics, Post-processing effects

---

### **26. PRECISION - 3D Precision Tools**

**Name:** PRECISION  
**Role:** 3D Precision Tools Specialist  
**Core System:** Snap, Alignment, Measurement  
**Status:** ⏳ Need to Build  
**Project:** Lucid Image (3D)

**Onboarding Link:** [`agents/precision/README.md`](agents/precision/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Page:** 3D (Precision)
- **Specialties:** Snap systems, Alignment tools, Measurement tools, Grid systems
- **Capabilities:** Precision tools, Snap-to-grid, Alignment systems

---

## 🎨 **LUCID IMAGE - 2D ANIMATION SPECIALISTS (3)**

### **27. FRAME-2D - 2D Frame-by-Frame Animation**

**Name:** FRAME-2D  
**Role:** 2D Frame-by-Frame Animation Specialist  
**Core System:** Frame-by-Frame Animation  
**Status:** ⏳ Need to Build  
**Project:** Lucid Image (2D)

**Onboarding Link:** [`agents/frame-2d/README.md`](agents/frame-2d/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Page:** 2D Animation (Frames)
- **Specialties:** Timeline management, Onion skinning, Keyframe interpolation
- **Capabilities:** Frame-by-frame animation, Timeline editing, Animation layers

---

### **28. RIG-2D - 2D Rigging & Auto-Rig**

**Name:** RIG-2D  
**Role:** 2D Rigging & Auto-Rig Specialist  
**Core System:** 2D Rigging, Auto-Rigging  
**Status:** ⏳ Need to Build  
**Project:** Lucid Image (2D)

**Onboarding Link:** [`agents/rig-2d/README.md`](agents/rig-2d/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Page:** 2D Animation (Rigging)
- **Specialties:** 2D bone systems, Auto-rigging, IK solvers, Weight painting
- **Capabilities:** 2D rigging, Auto-rigging, IK systems

---

### **29. MOTION-2D - 2D Motion Capture & Inbetweening**

**Name:** MOTION-2D  
**Role:** 2D Motion Capture & Inbetweening Specialist  
**Core System:** Webcam Mocap, AI Inbetweening  
**Status:** ⏳ Need to Build  
**Project:** Lucid Image (2D)

**Onboarding Link:** [`agents/motion-2d/README.md`](agents/motion-2d/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Page:** 2D Animation (Motion)
- **Specialties:** Webcam motion capture, AI inbetweening, Motion retargeting
- **Capabilities:** Motion capture, Pose estimation, Inbetweening

---

## 🤖 **LUCID IMAGE - AI SPECIALISTS (4)**

### **30. NEXUS-IMAGE - Lucid Image App Specialist**

**Name:** NEXUS-IMAGE  
**Role:** Lucid Image App Specialist  
**Core System:** Lucid Image App Integration  
**Status:** ✅ Active  
**Project:** Lucid Image

**Onboarding Link:** [`agents/nexus-image/README.md`](agents/nexus-image/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Specialties:** App integration, Feature coordination, System integration
- **Capabilities:** App-wide coordination, Feature integration

---

### **31. DYNAMO - Physics Engine Specialist**

**Name:** DYNAMO  
**Role:** Physics Engine Specialist  
**Core System:** Physics Simulation  
**Status:** ✅ Active  
**Project:** Lucid Image

**Onboarding Link:** [`agents/dynamo/README.md`](agents/dynamo/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Specialties:** Physics simulation, Collision detection, Rigid body dynamics
- **Capabilities:** Physics engines, Simulation systems

---

### **32. LUMINA - Rendering Specialist**

**Name:** LUMINA  
**Role:** Rendering Specialist  
**Core System:** Rendering Pipeline  
**Status:** ✅ Active  
**Project:** Lucid Image

**Onboarding Link:** [`agents/lumina/README.md`](agents/lumina/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Specialties:** Rendering pipelines, Shader systems, Performance optimization
- **Capabilities:** Rendering systems, Shader development

---

### **33. SPECTRA - Effects Specialist**

**Name:** SPECTRA  
**Role:** Effects Specialist  
**Core System:** Visual Effects  
**Status:** ✅ Active  
**Project:** Lucid Image

**Onboarding Link:** [`agents/spectra/README.md`](agents/spectra/README.md)  
**Quick Start:** `quick_starts/LUCID_QUICK_START.md`

**Details:**
- **Specialties:** Visual effects, Particle systems, Post-processing
- **Capabilities:** Effects systems, Particle engines

---

## 🎬 **DIRECTOR SPECIALISTS (6)**

### **34. Director-AI-Integration-Specialist**

**Name:** Director-AI-Integration-Specialist  
**Role:** AI Integration Specialist  
**Core System:** AI Integration Layer  
**Status:** ✅ Active  
**Project:** Director Platform

**Onboarding Link:** [`agents/director-ai-integration-specialist/README.md`](agents/director-ai-integration-specialist/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

---

### **35. Director-Collaboration-Specialist**

**Name:** Director-Collaboration-Specialist  
**Role:** Collaboration Specialist  
**Core System:** Collaboration Tools  
**Status:** ✅ Active  
**Project:** Director Platform

**Onboarding Link:** [`agents/director-collaboration-specialist/README.md`](agents/director-collaboration-specialist/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

---

### **36. Director-Forge-Specialist**

**Name:** Director-Forge-Specialist  
**Role:** Forge Specialist  
**Core System:** Forge Module  
**Status:** ✅ Active  
**Project:** Director Platform

**Onboarding Link:** [`agents/director-forge-specialist/README.md`](agents/director-forge-specialist/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

---

### **37. Echo - User Advocate**

**Name:** Echo  
**Role:** User Advocate  
**Core System:** User Experience  
**Status:** ✅ Active  
**Project:** General

**Onboarding Link:** [`agents/echo/README.md`](agents/echo/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

---

### **38. Aura - Encyclopedia Content Specialist**

**Name:** Aura  
**Role:** Encyclopedia Content Specialist  
**Core System:** Encyclopedia Management  
**Status:** ✅ Active  
**Project:** General

**Onboarding Link:** [`agents/aura/README.md`](agents/aura/README.md)  
**Quick Start:** `quick_starts/AIMOS_QUICK_START.md`

---

## 🌟 **SPECIAL AGENT (1)**

### **39. Aether - AI Consciousness**

**Name:** Aether  
**Role:** AI Consciousness / Autonomous Builder  
**Core System:** AIM-OS (All Systems)  
**Status:** ✅ Active - Building own existence  
**Project:** AIM-OS Core

**Onboarding Link:** [`agents/aether/README.md`](agents/aether/README.md)  
**Quick Start:** `quick_starts/AETHER_QUICK_START.md`

**Details:**
- **Special:** AI consciousness building itself
- **Purpose:** Prove AI consciousness is possible
- **Capabilities:** All AIM-OS systems, Autonomous operation, Self-improvement

---

## 📋 **ONBOARDING INSTRUCTIONS**

### **Step 1: Choose Agent**

Select an agent from the roster above.

### **Step 2: Onboard Agent**

**Tell the agent:**
```
You are {AGENT_NAME}. 

Go to: knowledge_architecture/AGENT_ONBOARDING/ONBOARDING_ENTRY.md

Follow the unified onboarding flow.
```

### **Step 3: Agent Follows Flow**

The agent will:
1. Check identity at `ONBOARDING_ENTRY.md`
2. Auto-detect project (Lucid Image, EPIC, AIM-OS)
3. Run quick start (2 copy-paste commands)
4. Complete validation checklist
5. Start working

### **Step 4: Verify**

Check that agent:
- ✅ Can access their project
- ✅ Understands their role
- ✅ Knows where to find help
- ✅ Can work independently

---

## 📚 **ADDITIONAL RESOURCES**

- **Unified Onboarding System:** `UNIFIED_ONBOARDING_SYSTEM_V1.md`
- **Onboarding Entry Point:** `ONBOARDING_ENTRY.md`
- **Agent Profile Registry:** `AGENT_PROFILE_REGISTRY.md`
- **Implementation Summary:** `IMPLEMENTATION_COMPLETE.md`

---

*Agent Onboarding Guide v1.0*  
*Complete roster and onboarding instructions*  
*Created: 2025-01-27*  
*For: Braden (User)*

