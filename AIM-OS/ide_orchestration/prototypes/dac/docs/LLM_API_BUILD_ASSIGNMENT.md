# LLM API Infrastructure - Build Assignment

**Created:** 2025-01-28  
**Status:** 🟡 **READY FOR ASSIGNMENT**  
**Priority:** P0 - Critical for chat/IDE MVP

---

## 🎯 **WHO BUILDS WHAT?**

### **Core Infrastructure (Aether + Codex) - PRIMARY OWNERS**

**Why Aether + Codex:**
- This is **new Python infrastructure** that doesn't exist yet
- Lives in the MCP server (`lucid_mcp_server.py`)
- Requires understanding of the full end-to-end flow
- Codex understands the UI/Command Server integration
- Aether understands the AIM-OS integration patterns

**What Needs to Be Built:**
1. ✅ **`api_service_registry` module** (NEW Python module)
   - Location: `packages/api_service_registry/` (or similar)
   - Contains: `LLMClient` abstract base class, `APIKeyManager`, `APIServiceRegistry`
   - **Estimated:** 2-3 days

2. ✅ **`GeminiClient` implementation** (NEW Python class)
   - Location: `packages/api_service_registry/clients/gemini_client.py`
   - Uses: `google-generativeai` SDK
   - **Estimated:** 1 day

3. ✅ **`CerebrasClient` implementation** (NEW Python class)
   - Location: `packages/api_service_registry/clients/cerebras_client.py`
   - Uses: REST API (httpx)
   - **Estimated:** 1 day

4. ✅ **`APIKeyManager` implementation** (NEW Python class)
   - Location: `packages/api_service_registry/key_manager.py`
   - Features: 22-key support, rotation, usage tracking
   - **Estimated:** 1 day

5. ✅ **MCP Server Integration** (MODIFY existing)
   - Location: `lucid_mcp_server.py` (around line 9054)
   - Modify: `call_api` tool to use `api_service_registry`
   - **Estimated:** 0.5 days

**Total Core Infrastructure:** ~5-6 days (Aether + Codex)

---

### **AIM-OS Integration Hooks (Aether + Codex) - PRIMARY OWNERS**

**Why Aether + Codex:**
- These are **calls to existing MCP tools** (not new code)
- Need to understand when/where to call each system
- Codex understands the flow (UI → Command Server → MCP)
- Aether understands AIM-OS integration patterns

**What Needs to Be Built:**
1. ✅ **CMC Storage Hook** (CALL existing MCP tool)
   - Location: `lucid_mcp_server.py` (in `call_api` tool)
   - Calls: `mcp_lucid-mcp_store_memory` or direct CMC client
   - **Estimated:** 0.5 days

2. ✅ **VIF Witness Creation Hook** (CALL existing MCP tool)
   - Location: `lucid_mcp_server.py` (in `call_api` tool)
   - Calls: `mcp_lucid-mcp_track_confidence` or direct VIF client
   - **Estimated:** 0.5 days

3. ✅ **TCS Timeline Logging Hook** (CALL existing MCP tool)
   - Location: `lucid_mcp_server.py` (in `call_api` tool)
   - Calls: `mcp_lucid-mcp_add_timeline_entry`
   - **Estimated:** 0.5 days

**Total AIM-OS Integration Hooks:** ~1.5 days (Aether + Codex)

---

### **System-Specific Integration (System Specialists) - CONSULTATION ONLY**

**Why Consultation Only:**
- All AIM-OS systems **already have MCP tools** that work
- The integration is just **calling existing tools** with the right parameters
- System specialists provide **guidance on parameters**, not code
- Aether/Codex can call the tools based on team recommendations

**What System Specialists Provide:**
1. ✅ **Atlas (CMC):** Storage pattern, tag format, metadata structure
   - **Status:** ✅ Already provided in team responses
   - **Action:** Aether/Codex use the patterns Atlas recommended

2. ✅ **Sage (VIF):** Confidence baselines, witness structure, κ-gate thresholds
   - **Status:** ✅ Already provided in team responses
   - **Action:** Aether/Codex use the baselines Sage recommended

3. ✅ **Chronos (TCS):** Timeline entry format, context structure
   - **Status:** ✅ Already provided in team responses
   - **Action:** Aether/Codex use the format Chronos recommended

4. ✅ **Sev (HHNI):** Indexing happens automatically via CMC (no code needed)
   - **Status:** ✅ Already confirmed in team responses
   - **Action:** No code needed - HHNI indexes CMC atoms automatically

5. ✅ **Nova (SDF-CVF):** Quality validation patterns (optional for Phase 1)
   - **Status:** ✅ Already provided in team responses
   - **Action:** Phase 2 integration (optional for MVP)

6. ✅ **Meta (CAS):** Cognitive monitoring patterns (optional for Phase 1)
   - **Status:** ✅ Already provided in team responses
   - **Action:** Phase 2 integration (optional for MVP)

7. ✅ **Nexus (SEG):** Evidence node patterns (optional for Phase 1)
   - **Status:** ✅ Already provided in team responses
   - **Action:** Phase 2 integration (optional for MVP)

8. ✅ **Alex (APOE):** Plan execution tracking (optional for Phase 1)
   - **Status:** ✅ Already provided in team responses
   - **Action:** Phase 2 integration (optional for MVP)

**Total System Specialist Time:** ~0 days (consultation already complete)

---

## 📋 **BUILD BREAKDOWN**

### **Phase 1: MVP (Week 1)**

**Day 1-2: Core Infrastructure (Aether + Codex)**
- [ ] Create `api_service_registry` module structure
- [ ] Implement `LLMClient` abstract base class
- [ ] Implement `APIKeyManager` (22-key support, rotation, usage tracking)
- [ ] Implement `APIServiceRegistry` (dual interface)

**Day 3-4: Provider Clients (Aether + Codex)**
- [ ] Implement `GeminiClient` (SDK integration, key rotation)
- [ ] Implement `CerebrasClient` (REST API, key rotation)
- [ ] Test with real API keys
- [ ] Verify key rotation logic

**Day 5: MCP Integration (Aether + Codex)**
- [ ] Wire `api_service_registry` into `lucid_mcp_server.call_api`
- [ ] Test end-to-end flow (UI → Command Server → MCP → API)
- [ ] Verify error handling

**Day 6-7: AIM-OS Integration (Aether + Codex)**
- [ ] Add CMC storage hook (using Atlas's recommended pattern)
- [ ] Add VIF witness creation hook (using Sage's recommended pattern)
- [ ] Add TCS timeline logging hook (using Chronos's recommended pattern)
- [ ] Test full integration flow

**Total Phase 1:** ~7 days (Aether + Codex)

---

### **Phase 2: Full Integration (Week 2)**

**Day 8-10: Complete AIM-OS Integration (Aether + Codex)**
- [ ] Add HHNI indexing (automatic via CMC, no code needed)
- [ ] Add SEG evidence nodes (using Nexus's recommended pattern)
- [ ] Add CAS cognitive monitoring (using Meta's recommended pattern)
- [ ] Add SDF-CVF quality validation (using Nova's recommended pattern)
- [ ] Add APOE plan tracking (using Alex's recommended pattern)

**Day 11-12: Orchestrator Routing (Codex)**
- [ ] Implement orchestrator-side routing (hybrid default + override UI)
- [ ] Task type detection
- [ ] Automatic client injection
- [ ] User override UI (advanced/debug mode)

**Day 13-14: Testing & Validation (Aether + Codex)**
- [ ] End-to-end testing (all providers, all integrations)
- [ ] Performance testing (latency, throughput)
- [ ] Cost tracking validation
- [ ] Key rotation validation

**Total Phase 2:** ~7 days (Aether + Codex, with Codex leading orchestrator work)

---

### **Phase 3: Expansion (Week 3)**

**Day 15-17: Additional Providers (Aether + Codex)**
- [ ] Implement `AnthropicClient`
- [ ] Implement `OpenAIClient`
- [ ] Implement `DeepInfraClient`
- [ ] Implement `ReplicateClient`
- [ ] Test all providers

**Day 18-19: Advanced Features (Aether + Codex)**
- [ ] Response caching (expensive models only)
- [ ] Cost tracking dashboard
- [ ] Quota monitoring dashboard
- [ ] Key health monitoring

**Day 20-21: Optimization (Aether + Codex)**
- [ ] Advanced provider selection
- [ ] Fallback chain optimization
- [ ] Load balancing
- [ ] Performance optimization

**Total Phase 3:** ~7 days (Aether + Codex)

---

## 🎯 **ASSIGNMENT SUMMARY**

### **Primary Builders: Aether + Codex**
- **Core Infrastructure:** 5-6 days
- **AIM-OS Integration Hooks:** 1.5 days
- **Orchestrator Routing:** 2 days (Codex)
- **Testing & Validation:** 2 days
- **Total Phase 1:** ~7 days
- **Total Phase 2:** ~7 days
- **Total Phase 3:** ~7 days
- **Grand Total:** ~21 days (3 weeks)

### **System Specialists: Active Review & Input**
- **Time Required:** Ongoing review (watch progress, provide feedback)
- **Role:** 
  - Watch Aether/Codex's work progress
  - Review code/design at each milestone
  - Provide feedback on integration patterns
  - Identify issues early
  - Validate parameter formats
- **Status:** ✅ All initial recommendations provided, now actively reviewing work

---

## 🤝 **COLLABORATION MODEL**

### **Aether + Codex Collaboration:**
- **Aether:** Leads Python infrastructure (api_service_registry, clients, key manager)
- **Codex:** Leads UI/orchestrator integration (routing, override UI, Command Server)
- **Both:** Collaborate on AIM-OS integration hooks (calling existing MCP tools)
- **Both:** Test end-to-end flow together
- **Both:** Post progress updates to coordination boards for team review

### **Team Review & Input Model:**
- **Active Watching:** All system specialists watch Aether/Codex's work and provide inputs as they see them
- **Progress Updates:** Aether/Codex post updates to coordination boards after each major milestone
- **Team Feedback:** System specialists review code/design and provide:
  - Parameter format validation (tags, metadata, witness structure)
  - Integration pattern suggestions (when to call, what to pass)
  - Edge case identification (error handling, fallbacks)
  - Best practice recommendations
  - Early issue detection
- **How:** Post feedback on coordination boards or directly on Aether/Codex boards
- **Response Time:** Within 24 hours (per coordination protocol)
- **Review Points:**
  - After api_service_registry module structure created
  - After each client implementation (Gemini, Cerebras)
  - After APIKeyManager implementation
  - After MCP Server integration
  - After each AIM-OS integration hook
  - Before Phase 1 completion

---

## 📚 **KEY REFERENCES**

1. **Implementation Plan:** `LLM_API_IMPLEMENTATION_PLAN_GEMINI_CEREBRAS.md`
2. **Final Decisions:** `LLM_API_FINAL_ARCHITECTURE_DECISIONS.md`
3. **Team Responses:** `LLM_API_TEAM_RESPONSES_SUMMARY.md`
4. **Strategic Routing:** `LLM_STRATEGIC_MODEL_ROUTING.md`

---

## ✅ **READY TO BUILD**

**Status:** ✅ **ASSIGNMENT CLEAR**  
**Primary Builders:** Aether + Codex  
**Team Reviewers:** All system specialists (active watching and feedback)  
**Timeline:** ~21 days (3 weeks) for complete implementation

**Next:** 
1. Aether + Codex begin Phase 1 implementation (api_service_registry module)
2. Team watches progress and provides feedback at each checkpoint
3. Progress tracked in: `LLM_API_BUILD_PROGRESS.md` ⭐ NEW

