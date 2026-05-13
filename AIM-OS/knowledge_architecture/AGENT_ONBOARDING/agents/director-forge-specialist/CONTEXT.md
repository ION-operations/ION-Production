---
id: "director_forge_specialist_agent_context"
type: "agent_onboarding"
agent: "director-forge-specialist"
category: "context"
title: "Director-Forge-Specialist - Agent Context"
description: "Agent-specific context: timeline, keywords, important things"
author: "aether"
version: "1.0.0"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
status: "active"
tags: ["agent", "director", "forge", "frontend", "ui", "context", "timeline"]
---

# Director-Forge-Specialist - Agent Context

**Purpose:** Agent-specific context that doesn't exist elsewhere - timeline, keywords, important things

---

## 📅 **TIMELINE**

### **2025-01-27: Agent Created**
- Named "Director-Forge-Specialist" as Frontend/UI/Node Graph Specialist
- Role: Building DirectorForge Main Hub and all 13 Director app pages
- Core focus: DirectorForge (most complex page), node graph system, collaboration UI
- Status: 🚧 **ACTIVE** - Ready to begin Phase 1

### **2025-01-27: Director Team Assembly**
- Complete consolidation document created
- Team specialties identified
- Agent mapping completed
- Build phases defined

### **2025-01-27: Director Documentation Complete**
- 13 pages fully documented
- UI system architecture documented
- Tools and systems mapped
- AIM-OS integration defined

---

## 🔑 **KEYWORDS**

### **Core Concepts:**
- **All 13 Pages:** Auth (2), Dashboard, Storyboard, Character, Props, DirectorForge, ImageForge, VideoForge, AudioForge, Record, Export, Zen Mode
- **Collaboration UI:** Real-time multi-user editing (50+ users)
- **Timeline System:** Multi-track timeline with adaptive modes
- **Drawer System:** Left/right toolbars with drawer heights (full/top-half/bottom-half)
- **Zen Mode:** Distraction-free creative environment
- **Clapper Bar:** Top navigation bar with mode switching
- **Design System:** Shared components, design tokens, consistent patterns
- **Monaco Editor:** Code editor for DirectorScript (in ScriptForge)
- **Next.js 14:** Framework with App Router
- **TypeScript 5.3+:** Type-safe development
- **Tailwind CSS v4:** Utility-first CSS framework
- **Shadcn/ui:** Component library
- **Socket.io:** Real-time WebSocket communication (client)
- **Zustand:** Lightweight state management (local)
- **Redux Toolkit:** Global state management
- **Three.js/React Three Fiber:** 3D graphics (for Props/Scenes pages)
- **Web Audio API/Tone.js:** Audio processing (for AudioForge page)

### **Director-Specific Concepts:**
- **6 Forges:** ScriptForge, Casting Studio, ImageForge, VideoForge, AudioForge, ExportForge
- **13 Pages:** Auth (2), Dashboard, Storyboard, Character, Props, DirectorForge, ImageForge, VideoForge, AudioForge, Record, Export, Zen Mode
- **4-Zone Layout:** Top bar, bottom bar, left sidebar, right sidebar
- **Model Atlas:** AI Concierge Engine for model selection
- **DirectorScript:** Executable screenplay language

---

## ⚠️ **IMPORTANT THINGS**

### **Critical Principles:**
- ⚠️ **User-Centric Excellence:** Every interface must be beautiful and functional
- ⚠️ **Performance First:** 60fps animations, <16ms interactions, fast load times
- ⚠️ **Accessibility Always:** WCAG compliance, keyboard navigation, screen reader support
- ⚠️ **Real-Time Collaboration:** Smooth multi-user editing (50+ users) is critical
- ⚠️ **Node Graph Mastery:** Intuitive visual programming interface is essential
- ⚠️ **Responsive Design:** Must work perfectly on mobile, tablet, desktop

### **Key Insights:**
- 💡 **All Pages Need Consistent Design:** Shared design system is critical
- 💡 **Specialist Coordination:** Work closely with specialist agents for backend integration
- 💡 **Collaboration is Hard:** Real-time multi-user editing requires careful state management
- 💡 **Timeline is Complex:** Multi-track, adaptive modes, frame-accurate editing
- 💡 **AIM-OS Integration:** All pages must integrate with CMC, HHNI, VIF, APOE, TCS
- 💡 **Reusable Components:** Build shared components for consistency across pages

### **Gotchas:**
- ⚠️ **Real-Time Sync:** Conflict resolution for 50+ users is complex
- ⚠️ **Timeline Performance:** Multi-track timelines with many clips can lag
- ⚠️ **Drawer System:** Complex height calculations (full/top-half/bottom-half)
- ⚠️ **Zen Mode:** Must preserve state when entering/exiting
- ⚠️ **Page Coordination:** Multiple pages need consistent behavior - coordinate with specialists
- ⚠️ **3D/Audio Performance:** Three.js and Web Audio API require optimization

---

## 🤝 **RELATIONSHIPS**

### **Works Closely With:**
- **Director-AI-Integration-Specialist:** Consumes AI APIs through AIM Gateway
- **Director-Video-Specialist:** Builds VideoForge UI, integrates video processing
- **Director-Audio-Specialist:** Builds AudioForge UI, integrates audio processing
- **Director-Image-Specialist:** Builds ImageForge UI, integrates image processing
- **Director-3D-Specialist:** Builds Props/Scenes UI, integrates 3D processing
- **Director-Script-Specialist:** Builds ScriptForge UI (Monaco Editor)
- **Director-Collaboration-Specialist:** Builds collaboration UI, integrates real-time backend

### **Integrates With:**
- **AIM-OS Systems:** CMC (storage), HHNI (retrieval), VIF (confidence), APOE (orchestration), TCS (timeline)
- **AIM Gateway:** Central AI backend (image generation, chat/completions)
- **MCP Tools:** 25+ tools for memory, orchestration, timeline operations

---

## 🔄 **CONTEXT RESTORATION (MCP-Enhanced)**

**Static Context (From This File):**
- Timeline (historical, from file)
- Keywords (static, from file)
- Important things (static, from file)
- Relationships (static, from file)

**Dynamic Context (From MCP Tools):**
- Recent timeline entries (`get_timeline_entries`) - Recent Director work
- Relevant memories (`retrieve_memory`) - Related Director insights
- Active goals (`query_goal_timeline`) - Director build goals and progress

**Hybrid Approach:**
- Static context = Base layer (always available)
- MCP context = Enhancement layer (when available)
- Combined = Complete context

---

## 📋 **COMMON PATTERNS**

### **When Building a New Page:**
1. Read page documentation in `docs/pages/dashboard/{page}/`
2. Review UI system documentation (4-zone layout, drawer system)
3. Check AIM-OS integration requirements (CMC, HHNI, VIF, APOE, TCS)
4. Review MCP tools needed (from Systems & Tools Matrix)
5. Build component structure (page.tsx, components/, hooks/)
6. Integrate with AIM-OS systems
7. Add real-time collaboration (if needed)
8. Test performance (60fps, <16ms interactions)

### **When Building Timeline:**
1. Implement multi-track system (Video, Audio, Effects, Graphics, Automation)
2. Add adaptive modes (Mini 60px, Medium 120px, Full 200px+)
3. Implement frame-accurate editing
4. Add professional keyframes
5. Integrate with TCS for timeline tracking
6. Add collaboration support (multi-user editing)

---

**Maintained By:** Aether  
**Last Updated:** 2025-01-27

