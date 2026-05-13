---
id: "sev_sage_command_server_coordination"
type: "coordination"
title: "Sev & Sage - Command Server Integration for Organization Panels"
description: "Coordination plan for connecting organization visualization panels to Command Server"
author: "aether"
version: "v1.0.0"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
status: "active"
tags: ["coordination", "sev", "sage", "command-server", "organization"]
---

# Sev & Sage - Command Server Integration Coordination

**Purpose:** Connect organization visualization panels to Command Server  
**Collaborators:** Sev (Organization), Sage (Frontend), Alex (Backend Reference)  
**Status:** Ready to Start  
**Coordinator:** Aether

---

## 🎯 **OBJECTIVE**

Connect all organization visualization panels to Command Server so they load real data instead of mock data.

**Panels to Connect:**
1. `SystemIndexBrowserPanel.tsx` - System indexes
2. `SystemMapPanel.tsx` - System maps
3. `SuperIndexPanel.tsx` - SUPER_INDEX.md
4. `MasterIndexPanel.tsx` - Master index

---

## 📋 **CURRENT STATE**

### **What Exists:**
- ✅ `SystemIndexService.ts` - Service exists but uses `/api/system-indexes` (needs Command Server)
- ✅ `MCPService.ts` - Shared service from Alex (use as reference)
- ✅ Panels exist but use mock data
- ✅ Organization data exists (SUPER_INDEX.md, system.map.lucid.json5, etc.)

### **What Needs to Be Done:**
- ⚠️ Update SystemIndexService to use Command Server pattern
- ⚠️ Create services for SUPER_INDEX, HIERARCHICAL_NAVIGATION_INDEX, System Maps
- ⚠️ Update panels to use real services
- ⚠️ Add loading/error states (Sage's expertise)
- ⚠️ Connect to real data sources

---

## 🤝 **COLLABORATION PLAN**

### **Sev's Responsibilities:**
1. **Create/Update Services:**
   - Update `SystemIndexService.ts` to use Command Server
   - Create `SuperIndexService.ts` for SUPER_INDEX.md
   - Create `SystemMapService.ts` for system.map.lucid.json5 files
   - Create `MasterIndexService.ts` for master index

2. **Service Pattern (Following Alex's MCPService):**
   - Use MCPService for MCP tool execution (if MCP tools exist)
   - Or create direct API endpoints that Command Server can serve
   - Follow same error handling and retry patterns

3. **Data Loading:**
   - Load SUPER_INDEX.md content
   - Load system.map.lucid.json5 files
   - Load system.index.lucid.json5 files
   - Parse and structure data for panels

### **Sage's Responsibilities:**
1. **UI Integration:**
   - Update panels to use new services
   - Add loading states (using existing LoadingSpinner)
   - Add error states (using existing ErrorDisplay)
   - Add retry functionality

2. **Component Enhancement:**
   - Enhance panels with proper loading/error handling
   - Add empty states when no data
   - Add refresh functionality
   - Ensure smooth user experience

3. **Testing:**
   - Test panels with real data
   - Test error handling
   - Test loading states
   - Verify user experience

---

## 🔧 **TECHNICAL APPROACH**

### **Option 1: Use MCP Tools (If They Exist)**
If Command Server has MCP tools for organization data:
- Use MCPService to execute tools
- Follow Alex's pattern exactly

### **Option 2: Create API Endpoints**
If no MCP tools exist, create API endpoints:
- Command Server serves `/api/system-indexes`, `/api/super-index`, etc.
- Services call these endpoints
- Use MCPService pattern for error handling

### **Option 3: Direct File Reading (Fallback)**
If Command Server can read files:
- Services request file content via Command Server
- Command Server reads from file system
- Returns parsed data

---

## 📁 **FILES TO CREATE/MODIFY**

### **Services (Sev):**
1. `src/services/SystemIndexService.ts` - UPDATE (use Command Server)
2. `src/services/SuperIndexService.ts` - CREATE (for SUPER_INDEX.md)
3. `src/services/SystemMapService.ts` - CREATE (for system.map.lucid.json5)
4. `src/services/MasterIndexService.ts` - CREATE (for master index)

### **Panels (Sage):**
1. `src/panels/SystemIndexBrowserPanel.tsx` - UPDATE (use service, add loading/error)
2. `src/panels/SystemMapPanel.tsx` - UPDATE (use service, add loading/error)
3. `src/panels/SuperIndexPanel.tsx` - UPDATE (use service, add loading/error)
4. `src/panels/MasterIndexPanel.tsx` - UPDATE (use service, add loading/error)

---

## 🚀 **IMPLEMENTATION STEPS**

### **Step 1: Service Creation (Sev)**
1. Review MCPService pattern from Alex
2. Update SystemIndexService to use Command Server
3. Create SuperIndexService
4. Create SystemMapService
5. Create MasterIndexService
6. Test services independently

### **Step 2: Panel Integration (Sage)**
1. Review existing LoadingSpinner and ErrorDisplay components
2. Update SystemIndexBrowserPanel to use SystemIndexService
3. Add loading/error states
4. Update other panels similarly
5. Test panels with real data

### **Step 3: Testing (Both)**
1. Test all panels with real data
2. Test error handling
3. Test loading states
4. Verify user experience
5. Fix any issues

---

## 📝 **SERVICE PATTERNS**

### **Service Structure (Following Alex's Pattern):**

```typescript
import { mcpService } from './MCPService'

export class SuperIndexService {
  private commandServerUrl: string = 'http://localhost:5001'
  
  async loadSuperIndex(): Promise<{ success: boolean; data?: SuperIndexData; error?: string }> {
    try {
      // Option 1: Use MCP tool if exists
      const result = await mcpService.executeTool('mcp_lucid-mcp_get_super_index')
      if (result.success) {
        return { success: true, data: result.result }
      }
      
      // Option 2: Use API endpoint
      const response = await fetch(`${this.commandServerUrl}/api/super-index`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (response.ok) {
        const data = await response.json()
        return { success: true, data }
      }
      
      return { success: false, error: 'Failed to load SUPER_INDEX' }
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' }
    }
  }
}
```

---

## 🎯 **SUCCESS CRITERIA**

- ✅ All services use Command Server pattern
- ✅ All panels load real data (0% mock data)
- ✅ Loading states work properly
- ✅ Error states work properly
- ✅ Retry functionality works
- ✅ User experience is smooth
- ✅ All panels tested and working

---

## 💬 **COORDINATION**

**Sev:**
- Create/update services
- Share service interfaces with Sage immediately
- Test services independently
- Coordinate with Sage on integration

**Sage:**
- Update panels to use services
- Add loading/error states
- Test panels with real data
- Coordinate with Sev on service interfaces

**Both:**
- Test together
- Fix issues collaboratively
- Share progress on coordination board
- Tag Aether for blockers

---

## 🚨 **BLOCKERS & QUESTIONS**

**If Blocked:**
- Post to coordination board with `[BLOCKER]` tag
- Tag @Aether for help
- Describe blocker clearly
- Request specific help

**Questions:**
- Post to coordination board
- Tag relevant agents
- Get answers before proceeding

---

**Status:** Ready to Start  
**Next Step:** Sev creates/updates services, Sage updates panels  
**Coordination:** Work together, share context immediately

