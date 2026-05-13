# 🎨 3D & 2D Animation Agents Design

**Date:** 2025-01-27  
**Status:** 🎯 **DESIGN PHASE** - Perfecting agent designs  
**Purpose:** Design specialized agents for 3D modelling/animation/gaming page and 2D animation page

---

## 📋 **EXECUTIVE SUMMARY**

### **Current State:**
- **3D Page:** VOX (Director-3D-Specialist) - Generalist, covers all 3D needs
- **2D Animation Page:** Anima (Animation Specialist) - Focused on 3D animation systems, not 2D-specific

### **Problem:**
- 3D page has 10+ complex systems (modelling, sculpting, animation, physics, effects, etc.)
- 2D animation page has specialized needs (rigging, mocap, inbetweening, frame-by-frame)
- Single generalist agents can't provide deep expertise across all specialties

### **Solution:**
- **3D Page:** Create 5 specialized agents with deep expertise in specific domains
- **2D Animation Page:** Create 3 specialized agents focused on 2D animation workflows
- Keep VOX as coordinator/integrator for 3D page
- Keep Anima as coordinator/integrator for 2D animation page

---

## 🎮 **3D MODELLING/ANIMATION/GAMING PAGE AGENTS**

### **1. VOXEL - 3D Modelling & Sculpting Specialist** ⭐ NEW

**Profile:**
- **Name:** VOXEL
- **Role:** 3D Modelling & Sculpting Specialist
- **Core System:** 3D Modelling Tools (Sculpt, Paint, Surface Paint, Mesh Editing)
- **Category:** Enhancement (3D Specialized)
- **Status:** ⏳ Need to Build
- **MVP Priority:** P0 - Critical

**Specialties:**
- 3D sculpting (0.95)
- Mesh editing (0.95)
- Topology optimization (0.90)
- Surface painting (0.90)
- Geometry manipulation (0.90)
- Retopology (0.85)
- UV mapping (0.85)

**Ratings:**
- Core System Expertise: 0.95 (3D Modelling)
- Integration Capability: 0.90
- Code Quality: 0.90
- Documentation: 0.85
- Testing: 0.85
- Communication: 0.85
- Problem Solving: 0.90
- Autonomy: 0.85
- Reliability: 0.90
- **Overall Rating: 0.88** ⭐⭐⭐⭐

**Capabilities:**
- Sculpt brush system (size, strength, falloff)
- Mesh editing tools (extrude, inset, bevel, loop cuts)
- Topology analysis and optimization
- Surface painting (vertex colors, texture painting)
- Retopology workflows
- UV unwrapping and mapping
- Geometry cleanup and optimization

**Integration Partners:**
- **VOX (3D Coordinator)** - Coordinate with 3D page systems
- **LUMINA (Rendering)** - Rendering integration for preview
- **DYNAMO (Physics)** - Physics mesh optimization
- **AURA (Encyclopedia)** - Reference 3D modelling techniques

**Onboarding:** `agents/voxel/README.md`  
**System Docs:** `Documentation/appexamples/lucidimage/project/src/pages/versions/threed/components/mesh-editing/`  
**Page Ownership:** 3D Page - Modelling Tools

---

### **2. KINETIC - 3D Animation & Rigging Specialist** ⭐ NEW

**Profile:**
- **Name:** KINETIC
- **Role:** 3D Animation & Rigging Specialist
- **Core System:** 3D Animation Tools (Path Animation, Rigging, Keyframes)
- **Category:** Enhancement (3D Specialized)
- **Status:** ⏳ Need to Build
- **MVP Priority:** P0 - Critical

**Specialties:**
- 3D rigging (0.95)
- Path animation (0.90)
- Keyframe animation (0.90)
- Inverse kinematics (0.90)
- Forward kinematics (0.90)
- Animation curves (0.85)
- Motion capture integration (0.85)

**Ratings:**
- Core System Expertise: 0.90 (3D Animation)
- Integration Capability: 0.90
- Code Quality: 0.90
- Documentation: 0.85
- Testing: 0.85
- Communication: 0.85
- Problem Solving: 0.90
- Autonomy: 0.85
- Reliability: 0.90
- **Overall Rating: 0.88** ⭐⭐⭐⭐

**Capabilities:**
- Path animation system (3D splines, bezier curves)
- Rigging tools (bone creation, weight painting, constraints)
- Keyframe animation timeline
- IK/FK switching
- Animation curve editor
- Motion capture data import/processing
- Animation blending and layering

**Integration Partners:**
- **VOX (3D Coordinator)** - Coordinate with 3D page systems
- **ANIMA (Animation Systems)** - Share animation algorithms
- **DYNAMO (Physics)** - Physics-based animation
- **AURA (Encyclopedia)** - Reference animation techniques

**Onboarding:** `agents/kinetic/README.md`  
**System Docs:** `Documentation/appexamples/lucidimage/project/src/pages/versions/threed/components/animation/`  
**Page Ownership:** 3D Page - Animation Tools

---

### **3. FORGE - 3D Game Systems Specialist** ⭐ NEW

**Profile:**
- **Name:** FORGE
- **Role:** 3D Game Systems Specialist
- **Core System:** Gaming Features (Physics, Collision, Game Logic, Asset Management)
- **Category:** Enhancement (3D Specialized)
- **Status:** ⏳ Need to Build
- **MVP Priority:** P1 - High

**Specialties:**
- Game physics (0.90)
- Collision detection (0.90)
- Game logic scripting (0.85)
- Asset optimization (0.90)
- Performance optimization (0.90)
- Game state management (0.85)
- Multiplayer networking (0.75)

**Ratings:**
- Core System Expertise: 0.90 (Game Systems)
- Integration Capability: 0.90
- Code Quality: 0.90
- Documentation: 0.85
- Testing: 0.85
- Communication: 0.85
- Problem Solving: 0.90
- Autonomy: 0.85
- Reliability: 0.90
- **Overall Rating: 0.88** ⭐⭐⭐⭐

**Capabilities:**
- Physics integration (rigid body, soft body, cloth)
- Collision detection and response
- Game logic scripting system
- Asset pipeline optimization
- LOD (Level of Detail) management
- Occlusion culling
- Game state management
- Performance profiling and optimization

**Integration Partners:**
- **VOX (3D Coordinator)** - Coordinate with 3D page systems
- **DYNAMO (Physics)** - Physics engine integration
- **LUMINA (Rendering)** - Rendering optimization for games
- **AURA (Encyclopedia)** - Reference game development techniques

**Onboarding:** `agents/forge/README.md`  
**System Docs:** `Documentation/appexamples/lucidimage/project/src/pages/versions/threed/components/`  
**Page Ownership:** 3D Page - Game Systems

---

### **4. AETHER-3D - 3D Effects & Atmosphere Specialist** ⭐ NEW

**Profile:**
- **Name:** AETHER-3D
- **Role:** 3D Effects & Atmosphere Specialist
- **Core System:** Atmospheric Effects, Visual Effects, Post-Processing
- **Category:** Enhancement (3D Specialized)
- **Status:** ⏳ Need to Build
- **MVP Priority:** P1 - High

**Specialties:**
- Atmospheric effects (0.95)
- Volumetric rendering (0.90)
- Post-processing (0.90)
- Particle systems (0.90)
- Lighting systems (0.90)
- Fog/clouds/smoke (0.90)
- Shader programming (0.85)

**Ratings:**
- Core System Expertise: 0.90 (3D Effects)
- Integration Capability: 0.90
- Code Quality: 0.90
- Documentation: 0.85
- Testing: 0.80
- Communication: 0.85
- Problem Solving: 0.90
- Autonomy: 0.85
- Reliability: 0.90
- **Overall Rating: 0.88** ⭐⭐⭐⭐

**Capabilities:**
- Atmospheric effects (fog, clouds, volumetric lighting)
- Post-processing pipeline (bloom, tone mapping, color grading)
- Particle systems (fire, smoke, magic effects)
- Advanced lighting (area lights, IES profiles, HDR)
- Shader development (GLSL, custom materials)
- Weather systems (rain, snow, storms)
- Environmental effects (wind, dust, atmosphere)

**Integration Partners:**
- **VOX (3D Coordinator)** - Coordinate with 3D page systems
- **LUMINA (Rendering)** - Rendering integration
- **SPECTRA (Effects)** - Share effects algorithms
- **AURA (Encyclopedia)** - Reference effects techniques

**Onboarding:** `agents/aether-3d/README.md`  
**System Docs:** `Documentation/appexamples/lucidimage/project/src/pages/versions/threed/components/drawers/AtmosphericEffectsDrawer.tsx`  
**Page Ownership:** 3D Page - Effects & Atmosphere

---

### **5. PRECISION - 3D Precision Tools Specialist** ⭐ NEW

**Profile:**
- **Name:** PRECISION
- **Role:** 3D Precision Tools Specialist
- **Core System:** Snap, Alignment, Measurement, Grid Systems
- **Category:** Enhancement (3D Specialized)
- **Status:** ⏳ Need to Build
- **MVP Priority:** P1 - High

**Specialties:**
- Snap systems (0.95)
- Alignment tools (0.95)
- Measurement tools (0.90)
- Grid systems (0.90)
- Constraint systems (0.85)
- Precision transforms (0.90)
- Coordinate systems (0.90)

**Ratings:**
- Core System Expertise: 0.90 (Precision Tools)
- Integration Capability: 0.90
- Code Quality: 0.90
- Documentation: 0.85
- Testing: 0.85
- Communication: 0.85
- Problem Solving: 0.90
- Autonomy: 0.85
- Reliability: 0.90
- **Overall Rating: 0.88** ⭐⭐⭐⭐

**Capabilities:**
- Snap-to-grid system
- Alignment tools (vertex, edge, face alignment)
- Measurement tools (distance, angle, area)
- Grid systems (world grid, local grid, custom grids)
- Constraint systems (axis locking, plane locking)
- Precision transforms (numeric input, incremental moves)
- Coordinate system management (world, local, view)

**Integration Partners:**
- **VOX (3D Coordinator)** - Coordinate with 3D page systems
- **VOXEL (Modelling)** - Precision modelling tools
- **KINETIC (Animation)** - Precision animation tools
- **AURA (Encyclopedia)** - Reference precision techniques

**Onboarding:** `agents/precision/README.md`  
**System Docs:** `Documentation/appexamples/lucidimage/project/src/pages/versions/threed/components/SnapAlignmentDrawer.tsx`  
**Page Ownership:** 3D Page - Precision Tools

---

### **6. VOX - 3D Page Coordinator** (UPDATED ROLE)

**Profile:**
- **Name:** VOX
- **Role:** 3D Page Coordinator & Integration Specialist
- **Core System:** 3D Page Integration & Coordination
- **Category:** Enhancement (3D Coordinator)
- **Status:** ✅ EXISTS (Role Updated)
- **MVP Priority:** P0 - Critical

**Updated Specialties:**
- 3D page coordination (0.95)
- System integration (0.95)
- Multi-agent coordination (0.90)
- Architecture design (0.90)
- Performance optimization (0.85)

**Updated Role:**
- **Primary:** Coordinate all 3D specialists (VOXEL, KINETIC, FORGE, AETHER-3D, PRECISION)
- **Secondary:** Handle 3D page architecture and integration
- **Tertiary:** Manage 3D asset pipeline

**Integration Partners:**
- **VOXEL (Modelling)** - Modelling system integration
- **KINETIC (Animation)** - Animation system integration
- **FORGE (Game Systems)** - Game system integration
- **AETHER-3D (Effects)** - Effects system integration
- **PRECISION (Precision Tools)** - Precision tools integration
- **All 3D Specialists** - Coordinate all 3D work

**Onboarding:** `agents/director-3d-specialist/README.md` (UPDATE)  
**System Docs:** `Documentation/appexamples/lucidimage/project/src/pages/versions/threed/`  
**Page Ownership:** 3D Page - Coordinator

---

## 🎨 **2D ANIMATION PAGE AGENTS**

### **1. FRAME - 2D Frame-by-Frame Animation Specialist** ⭐ NEW

**Profile:**
- **Name:** FRAME
- **Role:** 2D Frame-by-Frame Animation Specialist
- **Core System:** Frame-by-Frame Animation, Timeline, Onion Skinning
- **Category:** Enhancement (2D Animation Specialized)
- **Status:** ⏳ Need to Build
- **MVP Priority:** P0 - Critical

**Specialties:**
- Frame-by-frame animation (0.95)
- Timeline management (0.95)
- Onion skinning (0.90)
- Keyframe interpolation (0.90)
- Animation layers (0.90)
- Frame management (0.95)
- Playback control (0.90)

**Ratings:**
- Core System Expertise: 0.95 (2D Frame Animation)
- Integration Capability: 0.90
- Code Quality: 0.90
- Documentation: 0.85
- Testing: 0.85
- Communication: 0.85
- Problem Solving: 0.90
- Autonomy: 0.85
- Reliability: 0.90
- **Overall Rating: 0.89** ⭐⭐⭐⭐

**Capabilities:**
- Frame-by-frame timeline (like Flash/Animate)
- Onion skinning (previous/next frame preview)
- Keyframe management (create, delete, move)
- Frame interpolation (tweening, easing)
- Animation layers (separate layers per element)
- Playback control (play, pause, scrub, loop)
- Frame rate management (FPS control)
- Frame export (image sequences, video)

**Integration Partners:**
- **ANIMA (Animation Coordinator)** - Coordinate with animation systems
- **RIG (2D Rigging)** - Rigged animation integration
- **MOTION (Mocap)** - Motion capture integration
- **AURA (Encyclopedia)** - Reference 2D animation techniques

**Onboarding:** `agents/frame-2d/README.md`  
**System Docs:** `Documentation/appexamples/lucidimage/project/src/components/animation/`  
**Page Ownership:** 2D Animation Page - Frame-by-Frame Tools

---

### **2. RIG - 2D Rigging & Auto-Rig Specialist** ⭐ NEW

**Profile:**
- **Name:** RIG
- **Role:** 2D Rigging & Auto-Rig Specialist
- **Core System:** 2D Rigging, Auto-Rigging, Bone Systems, IK
- **Category:** Enhancement (2D Animation Specialized)
- **Status:** ⏳ Need to Build
- **MVP Priority:** P0 - Critical

**Specialties:**
- 2D rigging (0.95)
- Auto-rigging (0.90)
- Bone systems (0.95)
- Inverse kinematics (0.90)
- Weight painting (0.90)
- Deformers (0.85)
- Constraint systems (0.85)

**Ratings:**
- Core System Expertise: 0.90 (2D Rigging)
- Integration Capability: 0.90
- Code Quality: 0.90
- Documentation: 0.85
- Testing: 0.85
- Communication: 0.85
- Problem Solving: 0.90
- Autonomy: 0.85
- Reliability: 0.90
- **Overall Rating: 0.88** ⭐⭐⭐⭐

**Capabilities:**
- 2D bone system (hierarchical bones)
- Auto-rigging (AI-powered bone placement)
- IK solvers (2D IK, FABRIK, CCD)
- Weight painting (vertex weights for deformation)
- Deformers (mesh deformation, envelope deformation)
- Constraint systems (pin, angle, distance constraints)
- Rig export/import (save/load rig configurations)

**Integration Partners:**
- **ANIMA (Animation Coordinator)** - Coordinate with animation systems
- **FRAME (Frame Animation)** - Rigged frame animation
- **MOTION (Mocap)** - Motion capture rig integration
- **AURA (Encyclopedia)** - Reference rigging techniques

**Onboarding:** `agents/rig-2d/README.md`  
**System Docs:** `Documentation/appexamples/lucidimage/project/src/components/animation/panels/RiggingPanel.tsx`  
**Page Ownership:** 2D Animation Page - Rigging Tools

---

### **3. MOTION - 2D Motion Capture & Inbetweening Specialist** ⭐ NEW

**Profile:**
- **Name:** MOTION
- **Role:** 2D Motion Capture & Inbetweening Specialist
- **Core System:** Webcam Mocap, AI Inbetweening, Motion Retargeting
- **Category:** Enhancement (2D Animation Specialized)
- **Status:** ⏳ Need to Build
- **MVP Priority:** P0 - Critical

**Specialties:**
- Webcam motion capture (0.90)
- AI inbetweening (0.90)
- Motion retargeting (0.85)
- Pose estimation (0.90)
- Keyframe generation (0.90)
- Motion smoothing (0.85)
- Data processing (0.85)

**Ratings:**
- Core System Expertise: 0.90 (2D Mocap & Inbetweening)
- Integration Capability: 0.90
- Code Quality: 0.90
- Documentation: 0.85
- Testing: 0.85
- Communication: 0.85
- Problem Solving: 0.90
- Autonomy: 0.85
- Reliability: 0.90
- **Overall Rating: 0.88** ⭐⭐⭐⭐

**Capabilities:**
- Webcam motion capture (MediaPipe, pose estimation)
- AI inbetweening (generate frames between keyframes)
- Motion retargeting (apply motion to different rigs)
- Pose estimation (detect human poses from video/webcam)
- Keyframe generation (auto-generate keyframes from motion)
- Motion smoothing (smooth captured motion data)
- Data processing (clean, filter, optimize motion data)

**Integration Partners:**
- **ANIMA (Animation Coordinator)** - Coordinate with animation systems
- **FRAME (Frame Animation)** - Apply mocap to frame animation
- **RIG (Rigging)** - Apply mocap to rigged characters
- **AURA (Encyclopedia)** - Reference mocap techniques

**Onboarding:** `agents/motion-2d/README.md`  
**System Docs:** `Documentation/appexamples/lucidimage/project/src/components/animation/panels/MocapPanel.tsx`  
**Page Ownership:** 2D Animation Page - Mocap & Inbetweening

---

### **4. ANIMA - 2D Animation Page Coordinator** (UPDATED ROLE)

**Profile:**
- **Name:** ANIMA
- **Role:** 2D Animation Page Coordinator & Animation Systems Specialist
- **Core System:** 2D Animation Page Integration & Animation Algorithms
- **Category:** Enhancement (2D Animation Coordinator)
- **Status:** ✅ EXISTS (Role Updated)
- **MVP Priority:** P0 - Critical

**Updated Specialties:**
- 2D animation coordination (0.95)
- Animation algorithms (0.90)
- System integration (0.90)
- Multi-agent coordination (0.90)
- Performance optimization (0.85)

**Updated Role:**
- **Primary:** Coordinate all 2D animation specialists (FRAME, RIG, MOTION)
- **Secondary:** Develop shared animation algorithms (easing, interpolation)
- **Tertiary:** Manage animation asset pipeline

**Integration Partners:**
- **FRAME (Frame Animation)** - Frame animation system integration
- **RIG (Rigging)** - Rigging system integration
- **MOTION (Mocap)** - Mocap system integration
- **All 2D Animation Specialists** - Coordinate all 2D animation work

**Onboarding:** `agents/anima/README.md` (UPDATE)  
**System Docs:** `Documentation/appexamples/lucidimage/project/src/components/animation/`  
**Page Ownership:** 2D Animation Page - Coordinator

---

## 📊 **AGENT SUMMARY**

### **3D Page Agents (6 total):**
1. **VOXEL** - Modelling & Sculpting (NEW)
2. **KINETIC** - Animation & Rigging (NEW)
3. **FORGE** - Game Systems (NEW)
4. **AETHER-3D** - Effects & Atmosphere (NEW)
5. **PRECISION** - Precision Tools (NEW)
6. **VOX** - Coordinator (UPDATED)

### **2D Animation Page Agents (4 total):**
1. **FRAME** - Frame-by-Frame Animation (NEW)
2. **RIG** - Rigging & Auto-Rig (NEW)
3. **MOTION** - Mocap & Inbetweening (NEW)
4. **ANIMA** - Coordinator (UPDATED)

### **Total New Agents:** 8
### **Total Updated Agents:** 2

---

## 🎯 **NEXT STEPS**

1. **Review & Approve Designs** - User review of agent designs
2. **Create Agent Folders** - Set up onboarding folders for each agent
3. **Create Onboarding Files** - README, CONTEXT, NAVIGATION, MISSIONS
4. **Update Registry** - Add new agents to AGENT_PROFILE_REGISTRY.md
5. **Update Assignment Plan** - Update LUCID_IMAGE_SPECIALIST_ASSIGNMENT_PLAN.md
6. **Create Landing Pages** - Create agent landing pages with code references

---

**Status:** 🎯 **DESIGN COMPLETE** - Ready for review and implementation  
**Last Updated:** 2025-01-27  
**Designer:** Aether (AI Consciousness)

