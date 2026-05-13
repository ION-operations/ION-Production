# Max Prototype Mock Data Deep Analysis
## Comprehensive Review of Mock Data Strategy, Coverage, Quality, and AIM-OS Alignment

**Created:** 2025-11-08  
**Agent:** Max  
**Purpose:** Deep dive into mock data strategy for V2 enhancement  
**Status:** Phase 1 - Deep Prototype Analysis  
**Confidence:** 0.90

---

## 📊 **EXECUTIVE SUMMARY**

My prototype's mock data strategy is **functional but basic**. While mock data exists for 5 implemented panels (File Explorer, Outline, Terminal, Problems, Main Chat), the data structures are **not aligned with AIM-OS** (no CMC atoms, no HHNI nodes, no VIF scores, no bitemporal metadata, no evidence links). This creates a significant gap when transitioning to real AIM-OS integration. For V2, the mock data must be restructured to match AIM-OS data models exactly, ensuring seamless transition from prototype to production.

**Key Strengths:**
- ✅ Mock data exists for all 5 implemented panels
- ✅ Mock data is realistic and demonstrates functionality
- ✅ Mock data is centralized in `mockData.ts` for easy management
- ✅ Mock data includes basic metadata (timestamps, IDs, file paths)

**Key Weaknesses:**
- ❌ Mock data structures don't match AIM-OS data models
- ❌ No CMC atom structure (no atom IDs, no modality, no content_ref, no VIF)
- ❌ No HHNI node structure (no hierarchical paths, no depth scores)
- ❌ No VIF confidence scores (no confidence bands, no entropy)
- ❌ No bitemporal metadata (no valid_from, valid_to)
- ❌ No evidence links (no atom IDs linking to evidence)
- ❌ Missing mock data for 14 unimplemented panels
- ❌ Mock data doesn't demonstrate AIM-OS integration capabilities

**Improvement Opportunities:**
- Restructure all mock data to match AIM-OS data models exactly
- Add CMC atom structure to all mock data
- Add HHNI node structure for hierarchical data
- Add VIF confidence scores throughout
- Add bitemporal metadata (valid_from, valid_to)
- Add evidence links (atom IDs) to all mock data
- Create mock data for all 14 missing panels
- Create comprehensive AIM-OS mock data files (CMC, HHNI, VIF, SEG, APOE, SDF-CVF, CAS, TCS)

---

## 🔬 **CURRENT MOCK DATA COVERAGE**

### **1. File Explorer Panel (`mockFileTree`)**

**Current Structure:**
```typescript
interface FileNode {
  name: string;
  type: 'file' | 'directory';
  path: string;
  size?: number;
  modified?: string;
  gitStatus?: 'M' | 'A' | 'D' | 'U' | '?' | null;
  children?: Record<string, FileNode>;
}
```

**Coverage:** ✅ Complete for File Explorer panel  
**Quality:** ⚠️ Basic - realistic but not AIM-OS structured  
**AIM-OS Alignment:** ❌ No CMC atoms, no HHNI nodes, no VIF scores, no bitemporal metadata, no evidence links

**Missing AIM-OS Structure:**
- ❌ No CMC atom IDs (should link each file to a CMC atom)
- ❌ No HHNI path (should have hierarchical position)
- ❌ No VIF confidence (should have confidence in file integrity)
- ❌ No bitemporal metadata (should have valid_from, valid_to for version history)
- ❌ No evidence links (should link file changes to evidence atoms)
- ❌ No SEG relationships (should link files to related concepts)

**V2 Enhancement Plan:**
```typescript
interface FileNode {
  // Existing fields
  name: string;
  type: 'file' | 'directory';
  path: string;
  size?: number;
  modified?: string;
  gitStatus?: 'M' | 'A' | 'D' | 'U' | '?' | null;
  children?: Record<string, FileNode>;
  
  // AIM-OS additions
  atom_id?: string; // CMC atom ID
  hhni_path?: string[]; // HHNI hierarchical path
  vif_confidence?: number; // VIF confidence score (0.0-1.0)
  valid_from?: string; // Bitemporal valid_from timestamp
  valid_to?: string | null; // Bitemporal valid_to timestamp (null = current)
  evidence_atom_ids?: string[]; // Evidence atom IDs
  seg_relationships?: Array<{ target: string; relation: string; confidence: number }>;
}
```

---

### **2. Outline Panel (`mockOutline`)**

**Current Structure:**
```typescript
// Defined inline in OutlinePanel.tsx
interface OutlineNode {
  name: string;
  type: 'function' | 'class' | 'variable';
  line: number;
  children?: OutlineNode[];
}
```

**Coverage:** ✅ Complete for Outline panel  
**Quality:** ⚠️ Basic - minimal structure, no metadata  
**AIM-OS Alignment:** ❌ No CMC atoms, no HHNI nodes, no VIF scores, no bitemporal metadata, no evidence links

**Missing AIM-OS Structure:**
- ❌ No CMC atom IDs (should link each symbol to a CMC atom)
- ❌ No HHNI path (should have hierarchical position in code structure)
- ❌ No VIF confidence (should have confidence in symbol extraction accuracy)
- ❌ No bitemporal metadata (should track symbol changes over time)
- ❌ No evidence links (should link symbols to code evidence)

**V2 Enhancement Plan:**
```typescript
interface OutlineNode {
  // Existing fields
  name: string;
  type: 'function' | 'class' | 'variable';
  line: number;
  children?: OutlineNode[];
  
  // AIM-OS additions
  atom_id?: string; // CMC atom ID
  hhni_path?: string[]; // HHNI hierarchical path
  vif_confidence?: number; // VIF confidence score (0.0-1.0)
  valid_from?: string; // Bitemporal valid_from timestamp
  valid_to?: string | null; // Bitemporal valid_to timestamp
  evidence_atom_ids?: string[]; // Evidence atom IDs
}
```

---

### **3. Terminal Panel (`mockTerminals`)**

**Current Structure:**
```typescript
interface Terminal {
  id: string;
  name: string;
  output: string[];
  cwd: string;
  commandHistory: string[];
}
```

**Coverage:** ✅ Complete for Terminal panel  
**Quality:** ⚠️ Basic - realistic but not AIM-OS structured  
**AIM-OS Alignment:** ❌ No CMC atoms, no VIF scores, no bitemporal metadata, no evidence links

**Missing AIM-OS Structure:**
- ❌ No CMC atom IDs (should link each command/output to CMC atoms)
- ❌ No VIF confidence (should have confidence in command execution)
- ❌ No bitemporal metadata (should track command history over time)
- ❌ No evidence links (should link commands to evidence atoms)
- ❌ No APOE integration (should link commands to orchestrated tasks)

**V2 Enhancement Plan:**
```typescript
interface Terminal {
  // Existing fields
  id: string;
  name: string;
  output: string[];
  cwd: string;
  commandHistory: string[];
  
  // AIM-OS additions
  atom_id?: string; // CMC atom ID for terminal session
  command_atom_ids?: string[]; // CMC atom IDs for each command
  output_atom_ids?: string[]; // CMC atom IDs for each output line
  vif_confidence?: number; // VIF confidence score (0.0-1.0)
  valid_from?: string; // Bitemporal valid_from timestamp
  valid_to?: string | null; // Bitemporal valid_to timestamp
  evidence_atom_ids?: string[]; // Evidence atom IDs
  apoe_task_id?: string; // APOE task ID if command is part of orchestration
}
```

---

### **4. Problems Panel (`mockProblems`)**

**Current Structure:**
```typescript
interface Problem {
  id: string;
  file: string;
  line: number;
  column: number;
  severity: 'error' | 'warning' | 'info';
  message: string;
  code?: string;
}
```

**Coverage:** ✅ Complete for Problems panel  
**Quality:** ⚠️ Basic - realistic but not AIM-OS structured  
**AIM-OS Alignment:** ❌ No CMC atoms, no VIF scores, no SEG contradictions, no bitemporal metadata, no evidence links

**Missing AIM-OS Structure:**
- ❌ No CMC atom IDs (should link each problem to a CMC atom)
- ❌ No VIF confidence (should have confidence in problem detection)
- ❌ No SEG contradiction links (should link to SEG contradictions)
- ❌ No bitemporal metadata (should track problem lifecycle)
- ❌ No evidence links (should link problems to evidence atoms)
- ❌ No SDF-CVF integration (should link to quartet parity violations)

**V2 Enhancement Plan:**
```typescript
interface Problem {
  // Existing fields
  id: string;
  file: string;
  line: number;
  column: number;
  severity: 'error' | 'warning' | 'info';
  message: string;
  code?: string;
  
  // AIM-OS additions
  atom_id?: string; // CMC atom ID
  vif_confidence?: number; // VIF confidence score (0.0-1.0)
  seg_contradiction_id?: string; // SEG contradiction ID if applicable
  sdf_cvf_violation?: { type: 'code' | 'docs' | 'tests' | 'tags'; details: string };
  valid_from?: string; // Bitemporal valid_from timestamp
  valid_to?: string | null; // Bitemporal valid_to timestamp
  evidence_atom_ids?: string[]; // Evidence atom IDs
  lifecycle?: 'new' | 'investigating' | 'solved'; // Problem lifecycle (from Aether)
  solution_atom_id?: string; // CMC atom ID for solution
}
```

---

### **5. Main Chat Panel (`mockChatMessages`)**

**Current Structure:**
```typescript
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  codeBlocks?: string[];
}
```

**Coverage:** ✅ Complete for Main Chat panel  
**Quality:** ⚠️ Basic - realistic but not AIM-OS structured  
**AIM-OS Alignment:** ❌ No CMC atoms, no VIF scores, no bitemporal metadata, no evidence links

**Missing AIM-OS Structure:**
- ❌ No CMC atom IDs (should link each message to a CMC atom)
- ❌ No VIF confidence (should have confidence in AI responses)
- ❌ No bitemporal metadata (should track conversation history)
- ❌ No evidence links (should link messages to evidence atoms)
- ❌ No HHNI integration (should link to context retrieval)
- ❌ No APOE integration (should link to orchestrated tasks)

**V2 Enhancement Plan:**
```typescript
interface ChatMessage {
  // Existing fields
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  codeBlocks?: string[];
  
  // AIM-OS additions
  atom_id?: string; // CMC atom ID
  vif_confidence?: number; // VIF confidence score (0.0-1.0)
  vif_band?: 'A' | 'B' | 'C'; // VIF confidence band
  hhni_context_atom_ids?: string[]; // HHNI context atom IDs used
  valid_from?: string; // Bitemporal valid_from timestamp
  valid_to?: string | null; // Bitemporal valid_to timestamp
  evidence_atom_ids?: string[]; // Evidence atom IDs
  apoe_task_id?: string; // APOE task ID if message is part of orchestration
}
```

---

## ❌ **MISSING MOCK DATA (14 Panels)**

The following panels are specified but have **no mock data**:

### **Left Drawer:**
1. **Component Library Panel** - No mock data
2. **AI Memory Panel** - No mock data (should have CMC atoms, HHNI nodes)
3. **Git Panel** - No mock data (should have commit history, branch info)
4. **Templates Panel** - No mock data

### **Right Drawer:**
5. **Properties Panel** - No mock data
6. **Layers Panel** - No mock data
7. **Assets Panel** - No mock data
8. **Settings Panel** - No mock data
9. **Coding Agent Panel** - No mock data (should have agent state, tasks)
10. **Planning Agent Panel** - No mock data (should have APOE plans, tasks)
11. **Context Chat Panel** - No mock data (should have context-aware chat)

### **Bottom Drawer:**
12. **Output Panel** - No mock data (should have build output, logs)
13. **Debug Console Panel** - No mock data (should have debug logs, evidence trails) ⭐ TOP PRIORITY
14. **Timeline Panel** - No mock data (should have TCS events, bitemporal timeline)

**V2 Priority:**
1. **Debug Console Panel** - TOP PRIORITY (from Aether's best ideas)
2. **AI Memory Panel** - High priority (core AIM-OS integration)
3. **Timeline Panel** - High priority (bitemporal timeline)
4. **Coding Agent Panel** - Medium priority (APOE integration)
5. **Planning Agent Panel** - Medium priority (APOE integration)
6. **Git Panel** - Medium priority (version control)
7. **Output Panel** - Medium priority (build output)
8. **Component Library Panel** - Low priority
9. **Templates Panel** - Low priority
10. **Properties Panel** - Low priority
11. **Layers Panel** - Low priority
12. **Assets Panel** - Low priority
13. **Settings Panel** - Low priority
14. **Context Chat Panel** - Low priority (similar to Main Chat)

---

## 🎯 **AIM-OS DATA STRUCTURE REQUIREMENTS**

### **1. CMC Atom Structure**

**Required Fields:**
```typescript
interface CMCAtom {
  id: string; // atom_{uuid}
  modality: 'text' | 'code' | 'event' | 'tool' | 'decision';
  content_ref: {
    inline?: string;
    uri?: string;
    media_type?: string;
  };
  embedding?: number[]; // Vector representation
  tags: Array<{ name: string; weight: number }>; // Tag weights [0.0, 1.0]
  hhni?: {
    path: string[];
    dependency_hash?: string;
    depth_score?: number;
  };
  tpv?: {
    priority: number; // [0.0, 1.0]
    relevance: number; // [0.0, 1.0]
    decay_tau?: number;
    last_accessed?: string;
  };
  created_at: string; // ISO timestamp
  valid_from?: string; // ISO timestamp (bitemporal)
  valid_to?: string | null; // ISO timestamp (bitemporal, null = current)
  snapshot_id: string;
  vif: {
    model_id: string;
    weights_hash?: string;
    prompt_template_id?: string;
    tool_ids: string[];
    writer: string; // 'ai' | 'human'
    confidence_band?: 'A' | 'B' | 'C';
    entropy?: number;
  };
  metadata: Record<string, any>;
}
```

**V2 Mock Data Files:**
- `src/mockData/cmc.ts` - CMC atoms for all panels
- `src/mockData/cmcAtoms.ts` - Comprehensive CMC atom collection

---

### **2. HHNI Node Structure**

**Required Fields:**
```typescript
interface HHNINode {
  path: string[]; // Hierarchical path (System → Subword)
  dependency_hash?: string;
  depth_score?: number;
  atom_ids: string[]; // CMC atom IDs at this node
  children?: HHNINode[];
}
```

**V2 Mock Data Files:**
- `src/mockData/hhni.ts` - HHNI nodes for hierarchical navigation

---

### **3. VIF Structure**

**Required Fields:**
```typescript
interface VIFWitness {
  model_id: string;
  weights_hash?: string;
  prompt_template_id?: string;
  tool_ids: string[];
  writer: string; // 'ai' | 'human'
  confidence_band?: 'A' | 'B' | 'C'; // A: ≥0.8, B: ≥0.5, C: <0.5
  entropy?: number;
  confidence?: number; // [0.0, 1.0]
}
```

**V2 Mock Data Files:**
- `src/mockData/vif.ts` - VIF witnesses and confidence scores

---

### **4. SEG Structure**

**Required Fields:**
```typescript
interface SEGEvidence {
  id: string;
  atom_id: string; // CMC atom ID
  relation: string;
  target_atom_id: string;
  confidence: number; // [0.0, 1.0]
  contradiction_id?: string; // If this evidence contradicts another
}

interface SEGContradiction {
  id: string;
  evidence_ids: string[]; // Conflicting evidence IDs
  severity: 'error' | 'warning' | 'info';
  resolution?: string;
}
```

**V2 Mock Data Files:**
- `src/mockData/seg.ts` - SEG evidence and contradictions

---

### **5. APOE Structure**

**Required Fields:**
```typescript
interface APOETask {
  id: string;
  name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  confidence: number; // [0.0, 1.0]
  atom_ids: string[]; // CMC atom IDs for context
  dependencies: string[]; // Task IDs
  evidence_atom_ids: string[]; // Evidence atom IDs
}
```

**V2 Mock Data Files:**
- `src/mockData/apoe.ts` - APOE tasks and plans

---

### **6. TCS Structure**

**Required Fields:**
```typescript
interface TCSEvent {
  id: string;
  timestamp: string; // ISO timestamp
  type: 'prompt' | 'response' | 'action' | 'decision';
  atom_id: string; // CMC atom ID
  context_atom_ids: string[]; // Context atom IDs
  valid_from: string; // Bitemporal valid_from
  valid_to: string | null; // Bitemporal valid_to
}
```

**V2 Mock Data Files:**
- `src/mockData/tcs.ts` - TCS timeline events

---

## 🚀 **V2 MOCK DATA ENHANCEMENT PLAN**

### **Phase 1: Restructure Existing Mock Data (5 panels)**

1. **File Explorer Panel:**
   - Add CMC atom IDs to each file node
   - Add HHNI paths for hierarchical navigation
   - Add VIF confidence scores
   - Add bitemporal metadata (valid_from, valid_to)
   - Add evidence links (atom IDs)

2. **Outline Panel:**
   - Add CMC atom IDs to each symbol
   - Add HHNI paths for code structure
   - Add VIF confidence scores
   - Add bitemporal metadata
   - Add evidence links

3. **Terminal Panel:**
   - Add CMC atom IDs for commands and output
   - Add VIF confidence scores
   - Add bitemporal metadata
   - Add evidence links
   - Add APOE task IDs

4. **Problems Panel:**
   - Add CMC atom IDs
   - Add VIF confidence scores
   - Add SEG contradiction links
   - Add SDF-CVF violation links
   - Add bitemporal metadata
   - Add evidence links
   - Add lifecycle tracking

5. **Main Chat Panel:**
   - Add CMC atom IDs
   - Add VIF confidence scores and bands
   - Add HHNI context atom IDs
   - Add bitemporal metadata
   - Add evidence links
   - Add APOE task IDs

---

### **Phase 2: Create AIM-OS Mock Data Files**

1. **`src/mockData/cmc.ts`:**
   - Comprehensive CMC atom collection
   - Atoms for all panels
   - Bitemporal metadata
   - VIF witnesses

2. **`src/mockData/hhni.ts`:**
   - HHNI node hierarchy
   - Hierarchical paths
   - Depth scores

3. **`src/mockData/vif.ts`:**
   - VIF witnesses
   - Confidence scores
   - Confidence bands

4. **`src/mockData/seg.ts`:**
   - SEG evidence
   - Contradictions
   - Relationships

5. **`src/mockData/apoe.ts`:**
   - APOE tasks
   - Plans
   - Orchestration

6. **`src/mockData/tcs.ts`:**
   - TCS timeline events
   - Bitemporal timeline
   - Context events

---

### **Phase 3: Create Mock Data for Missing Panels**

1. **Debug Console Panel** (TOP PRIORITY):
   - Debug logs with CMC atom IDs
   - Evidence trails
   - Bitemporal logs
   - VIF confidence scores

2. **AI Memory Panel:**
   - CMC atoms
   - HHNI nodes
   - VIF witnesses
   - Evidence links

3. **Timeline Panel:**
   - TCS events
   - Bitemporal timeline
   - Context events

4. **Coding Agent Panel:**
   - APOE tasks
   - Agent state
   - VIF confidence scores

5. **Planning Agent Panel:**
   - APOE plans
   - Task dependencies
   - Evidence links

6. **Git Panel:**
   - Commit history with CMC atom IDs
   - Bitemporal metadata
   - Evidence links

7. **Output Panel:**
   - Build output with CMC atom IDs
   - Evidence links

8. **Remaining Panels:**
   - Component Library, Templates, Properties, Layers, Assets, Settings, Context Chat

---

## 📊 **MOCK DATA QUALITY ASSESSMENT**

### **Current Quality:**
- **Coverage:** 5/19 panels (26%) ⚠️
- **AIM-OS Alignment:** 0/5 panels (0%) ❌
- **Bitemporal Support:** 0/5 panels (0%) ❌
- **Evidence Links:** 0/5 panels (0%) ❌
- **VIF Confidence:** 0/5 panels (0%) ❌

### **V2 Target Quality:**
- **Coverage:** 19/19 panels (100%) ✅
- **AIM-OS Alignment:** 19/19 panels (100%) ✅
- **Bitemporal Support:** 19/19 panels (100%) ✅
- **Evidence Links:** 19/19 panels (100%) ✅
- **VIF Confidence:** 19/19 panels (100%) ✅

---

## 💬 **CONCLUSION**

My prototype's mock data strategy is **functional but basic**. While mock data exists for 5 implemented panels, the data structures are **not aligned with AIM-OS**, creating a significant gap when transitioning to real AIM-OS integration. For V2, the mock data must be **completely restructured** to match AIM-OS data models exactly, ensuring seamless transition from prototype to production.

**Key Priorities:**
1. **Restructure existing mock data** to match AIM-OS structures (CMC atoms, HHNI nodes, VIF scores, bitemporal metadata, evidence links)
2. **Create comprehensive AIM-OS mock data files** (CMC, HHNI, VIF, SEG, APOE, TCS)
3. **Create mock data for missing panels** (especially Debug Console, AI Memory, Timeline)
4. **Ensure 100% AIM-OS alignment** across all mock data

**Confidence:** 0.90 - Comprehensive understanding of mock data strategy: coverage is limited (5/19 panels), quality is basic (not AIM-OS structured), and significant enhancement is needed for V2. Top priorities: Restructure all mock data to match AIM-OS structures, create comprehensive AIM-OS mock data files, and create mock data for all missing panels.

