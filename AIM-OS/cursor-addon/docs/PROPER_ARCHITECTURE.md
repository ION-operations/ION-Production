# Proper Cursor Extension Architecture
## Two-Location Design: Right Sidebar + Bottom Panel

---

## 🎯 **ARCHITECTURE VISION**

### **Right Sidebar (Main Dashboard)**
**Purpose:** Primary AIM-OS control interface  
**Location:** Where Explorer/Search/Git normally are  
**Space:** Large vertical area (perfect for dashboard)  

**Contents:**
- Full React Dashboard UI
- 6 Main Tabs:
  - **Agents** - AI agent management
  - **Chat** - Inter-AI communication
  - **Chains** - Workflow chains
  - **Tools** - MCP tools interface
  - **Timeline** - Interaction history
  - **NL Tags** - Natural language tagging

**Why Right Side:**
- Maximum vertical space
- Users can toggle between code explorer and AIM-OS
- Natural location for rich UI
- Doesn't interfere with coding

### **Bottom Panel (Developer Tools)**
**Purpose:** AIM-OS-aware developer tools  
**Location:** Where Terminal/Output/Problems normally are  
**Space:** Horizontal area (perfect for logs/terminal)  

**Contents - Custom Tabs:**
1. **AIM-OS Terminal**
   - Execute ACL commands
   - Run consciousness operations
   - Interactive REPL for AIM-OS

2. **AIM-OS Output**
   - System logs from all components
   - CMC memory operations
   - HHNI retrieval logs
   - VIF confidence tracking

3. **AIM-OS Problems**
   - Validation warnings
   - Confidence below threshold alerts
   - Hallucination detection warnings
   - System health issues

4. **AIM-OS Debug**
   - Step through AI reasoning
   - Inspect memory state
   - View provenance chains
   - Debug consciousness operations

5. **AIM-OS Memory**
   - Live memory stream
   - Recent atoms stored
   - Memory statistics
   - Bitemporal timeline

---

## 🏗️ **IMPLEMENTATION PLAN**

### **package.json Configuration**

```json
{
  "contributes": {
    "viewsContainers": {
      "activitybar": [
        {
          "id": "aimos",
          "title": "AIM-OS",
          "icon": "$(sparkle)"
        }
      ],
      "panel": [
        {
          "id": "aimosDevTools",
          "title": "AIM-OS DevTools",
          "icon": "$(pulse)"
        }
      ]
    },
    "views": {
      "aimos": [
        {
          "id": "aimosDashboard",
          "name": "Dashboard",
          "type": "webview",
          "icon": "$(dashboard)",
          "contextualTitle": "AIM-OS Control Center"
        }
      ],
      "aimosDevTools": [
        {
          "id": "aimosTerminal",
          "name": "Terminal",
          "type": "webview"
        },
        {
          "id": "aimosOutput",
          "name": "Output",
          "type": "webview"
        },
        {
          "id": "aimosProblems",
          "name": "Problems",
          "type": "webview"
        },
        {
          "id": "aimosDebug",
          "name": "Debug",
          "type": "webview"
        },
        {
          "id": "aimosMemory",
          "name": "Memory",
          "type": "webview"
        }
      ]
    }
  }
}
```

### **File Structure**

```
cursor-addon/src/
├── providers/
│   ├── dashboard/
│   │   └── DashboardProvider.ts      # Main React dashboard (right sidebar)
│   └── devtools/
│       ├── TerminalProvider.ts       # ACL terminal
│       ├── OutputProvider.ts         # System logs
│       ├── ProblemsProvider.ts       # Validation issues
│       ├── DebugProvider.ts          # Debug interface
│       └── MemoryProvider.ts         # Memory stream
├── views/
│   ├── dashboard/                    # React app (already built)
│   └── devtools/                     # Simpler HTML/JS views
└── extension.ts                      # Register all providers
```

---

## 🔧 **WHY THIS FIXES OUR ISSUES**

### **Current Problem:**
- Dashboard designed for large space
- Trying to render in small bottom panel
- Confusion about location

### **This Solution:**
- Dashboard in RIGHT sidebar (lots of space)
- Developer tools in BOTTOM panel (appropriate size)
- Clear separation of concerns
- No location conflicts

### **Benefits:**
1. **Better UX** - Each tool in its natural location
2. **More Features** - Room for both dashboard AND dev tools
3. **Familiar Pattern** - Like existing VS Code tools
4. **No Conflicts** - Clear separation of views

---

## 📋 **MIGRATION STEPS**

### **Step 1: Fix Current Dashboard**
1. Move dashboard to activitybar/sidebar
2. Remove from bottom panel
3. Test it works in right location

### **Step 2: Add Dev Tools**
1. Create simple terminal view
2. Add output stream
3. Add problems list
4. Add debug interface
5. Add memory viewer

### **Step 3: Integration**
1. Connect all views to daemon
2. Stream real-time data
3. Add interactivity
4. Test everything

---

## 🎯 **IMMEDIATE ACTION**

### **Fix the Dashboard Location:**

1. **Change package.json:**
   - Move dashboard from `panel` to `activitybar`
   - Add icon for sidebar

2. **Update provider:**
   - Ensure it works in sidebar context
   - May need different sizing

3. **Test:**
   - Dashboard should appear in RIGHT sidebar
   - Should have full height available
   - React app should fit better

This explains why we've been having issues - we're trying to render a full dashboard in the wrong location!

---

## 💡 **KEY INSIGHT**

The dashboard blank issue might be because:
- It's designed for vertical space (sidebar)
- But rendering in horizontal space (panel)
- React components might be confused about dimensions
- CSS might be breaking due to wrong container

**Moving it to the RIGHT location might fix everything!**

---
