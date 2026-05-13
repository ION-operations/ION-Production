# Post-Synthesis Agent Prompts
**Date:** 2025-01-28  
**Status:** ✅ **SYNTHESIS COMPLETE** - Agents Ready to Work

---

## 🚀 **UNIVERSAL PROMPT FOR ALL AGENTS**

```
🎉 SYNTHESIS SESSION COMPLETE - Ready to Work!

All Agents:

The synthesis session is complete! All 4 parts done, all blockers resolved, all questions answered, MVP scope locked, orchestration integration plan created.

YOUR NEXT STEPS:

1. Read the Final Outcomes Document:
   - `SYNTHESIS_SESSION_FINAL_OUTCOMES.md` - Complete summary of all decisions, action items, timelines

2. Review Your Part 4 Orchestration Plan:
   - Check your coordination board for your Part 4 contribution
   - Identify your immediate action items from Part 4

3. Execute Your Immediate Action Items (P0):
   - See "Immediate Action Items" section in final outcomes
   - Your specific tasks are listed below

4. Coordinate with Other Agents:
   - Check dependencies in your Part 4 plan
   - Coordinate with other agents as needed
   - Post updates on your coordination board

5. Post Progress Updates:
   - Update your coordination board with progress
   - Use format: [2025-01-28 | Post-Synthesis] [Your Name] -> Team : [Task] Status

KEY DOCUMENTS:
- Final Outcomes: `SYNTHESIS_SESSION_FINAL_OUTCOMES.md`
- Your Part 4 Plan: Check your coordination board
- Orchestration Recommendations: VIF (Sage), CAS (Meta)

START NOW - Begin executing your immediate action items! 🚀
```

---

## 📋 **AGENT-SPECIFIC PROMPTS**

### **Atlas (CMC) - Immediate Actions**

```
Atlas:

Synthesis complete! Your immediate action items:

P0 (Can Start Now):
1. Integration Tagging Standardization
   - Implement standardized format: ["system:<name>:<priority>", "integration_type:<type>", "connection:<direction>", "modality:<modality>"]
   - Update CMC integration docs with tagging pattern
   - Ensure all atom creation uses standardized tags
   - Timeline: Can start immediately

2. Witness Storage API
   - Ensure witness storage API ready for all 7 P0 mandatory flows
   - Verify `create_atom(payload=AtomCreate(..., witness=witness_stub))` works
   - Test auto-generation: `MemoryStore(..., auto_generate_witness_stub=True)`
   - Timeline: Ready now, verify functionality

3. Support Other Agents
   - Provide CMC atom payload examples for HHNI E2E run (if needed)
   - Support VIF witness storage integration
   - Support SEG evidence linking integration

Post updates on your coordination board as you complete each task.
```

---

### **Sev (HHNI) - Immediate Actions**

```
Sev:

Synthesis complete! Your immediate action items:

P0 (Can Start Now):
1. HHNI E2E Run Coordination
   - Coordinate with Chronos for E2E run execution
   - Timeline: Post-session execution within 24-48 hours (2025-01-29 or 2025-01-30)
   - Duration: ~15-20 minutes
   - Status: Coordination confirmed, ready to execute

2. Core Retrieval Pipeline
   - Ensure `TwoStageRetriever.retrieve()` ready for chat/IDE integration
   - Verify CMC poller v1 functional
   - Verify CAS Phase 1 hooks functional
   - Timeline: Ready now, verify functionality

3. Support SDF-CVF Production Wiring
   - Coordinate with Nova on HHNI embedding function timeline
   - Provide embedding function API for SDF-CVF quartet parity
   - Timeline: Week 2-3 (after coordination)

4. Support VIF Witness Creation
   - Ready to implement witness creation hooks once Sage provides API
   - Timeline: After Sage API ready (1-2 weeks)

Post updates on your coordination board as you complete each task.
```

---

### **Nexus (SEG) - Immediate Actions**

```
Nexus:

Synthesis complete! Your immediate action items:

P0 (Can Start Now):
1. Evidence Creation/Linking → VIF Witness
   - Implement VIF witness creation for evidence creation flows
   - Implement VIF witness creation for evidence linking flows
   - Coordinate with Sage for VIF witness creation API
   - Timeline: Can start immediately (after Sage API ready)

2. Support SDF-CVF Production Wiring
   - SEG evidence linking is 100% ready for SDF-CVF
   - Confirm API access for Nova
   - Timeline: Can start immediately

3. Evidence Graph Core
   - Ensure core evidence graph ready for chat/IDE integration
   - Verify DUO gate pipeline functional
   - Verify all 7 integrations functional
   - Timeline: Ready now, verify functionality

Post updates on your coordination board as you complete each task.
```

---

### **Sage (VIF) - Immediate Actions**

```
Sage:

Synthesis complete! Your immediate action items:

P0 (Critical - 1-2 Weeks):
1. VIF Witness Creation for 7 P0 Mandatory Flows
   - Implement mandatory witness creation for:
     1. APOE Plan Execution
     2. HHNI Retrieval (Production)
     3. SEG Graph Updates
     4. CAS Cognitive Events
     5. SDF-CVF Parity Validation (CI)
     6. TCS Timeline Events
     7. Chat/IDE Orchestrated Actions
   - Timeline: 1-2 weeks
   - Coordinate with all systems for integration

2. Default Policies Implementation
   - Implement κ-gate policies (CRITICAL=0.95, IMPORTANT=0.85, ROUTINE=0.70, LOW_STAKES=0.60)
   - Implement retry policies (CRITICAL=0, IMPORTANT=1, ROUTINE=2, LOW_STAKES=3)
   - Document in VIF orchestration guide
   - Timeline: 1-2 weeks

3. VIF Orchestration Guide
   - Create comprehensive guide with P0 mandatory flows
   - Document default policies
   - Document integration patterns
   - Timeline: 1-2 weeks

Post updates on your coordination board as you complete each task.
```

---

### **Chronos (TCS) - Immediate Actions**

```
Chronos:

Synthesis complete! Your immediate action items:

P0 (Can Start Now):
1. HHNI E2E Run Execution
   - Coordinate with Sev for E2E run execution
   - Timeline: Post-session execution within 24-48 hours (2025-01-29 or 2025-01-30)
   - Duration: ~15-20 minutes
   - Status: Coordination confirmed, ready to execute

2. κ-Gate Timeline Entries
   - Ensure `create_kappa_gate_timeline_entry()` ready for mandatory use
   - Verify all κ-gate decisions can log to TCS
   - Timeline: Ready now, verify functionality

3. Chat/IDE Orchestrated Actions
   - Ensure MCP tool `add_timeline_entry` ready for chat/IDE integration
   - Verify timeline entry creation for all orchestrated actions
   - Timeline: Ready now, verify functionality

P2 (Post-Synthesis Cleanup):
4. TCS Test Import Fixes
   - Execute fix plan (P2 priority)
   - Timeline: Post-synthesis cleanup (when time permits)

Post updates on your coordination board as you complete each task.
```

---

### **Meta (CAS) - Immediate Actions**

```
Meta:

Synthesis complete! Your immediate action items:

P0 (Can Start Now):
1. Cognitive Context Enhancement for VIF Witnesses
   - Ensure `create_witness_with_cognitive_context()` ready
   - Verify CAS can enhance VIF witnesses with cognitive state
   - Timeline: Ready now, verify functionality

2. Hourly Introspection
   - Ensure hourly introspection ready for chat/IDE integration
   - Verify MCP tools functional
   - Timeline: Ready now, verify functionality

3. Support SDF-CVF Production Wiring
   - Coordinate with Nova on CAS API finalization
   - Provide failure analysis API for SDF-CVF
   - Timeline: Week 2-3 (after coordination)

P1 (Post-MVP):
4. CAS Activation Exports Implementation
   - Implement approved pattern (event-driven with hourly fallback)
   - Timeline: Post-MVP

Post updates on your coordination board as you complete each task.
```

---

### **Nova (SDF-CVF) - Immediate Actions**

```
Nova:

Synthesis complete! Your immediate action items:

P0 (Can Start Now):
1. SEG Evidence Linking (100% Ready)
   - Implement SEG evidence linking for SDF-CVF
   - Wire `store_evolution_artifact()` to `SEGraph.add_evidence()`
   - Timeline: Can start immediately

2. Core Quartet Parity
   - Ensure core quartet parity calculation ready
   - Verify quality gate enforcement functional
   - Verify trace creation functional
   - Timeline: Ready now, verify functionality

P0 (After Coordination - Week 2-3):
3. HHNI Change Context
   - Coordinate with Sev on embedding function timeline
   - Wire HHNI change context for SDF-CVF
   - Timeline: Week 2-3 (after coordination)

4. CAS Failure Analysis
   - Coordinate with Meta on CAS API finalization
   - Wire CAS failure analysis for SDF-CVF
   - Timeline: Week 2-3 (after coordination)

Post updates on your coordination board as you complete each task.
```

---

### **Alex (APOE) - Immediate Actions**

```
Alex:

Synthesis complete! Your immediate action items:

P0 (Can Start Now):
1. Plan Execution → VIF Witness
   - Ensure plan execution creates VIF witnesses (mandatory)
   - Coordinate with Sage for VIF witness creation API
   - Timeline: After Sage API ready (1-2 weeks)

2. κ-Gate Enforcement
   - Implement κ-gate enforcement in executor path
   - Use default policies (ROUTINE=0.70, CRITICAL=0.90)
   - Timeline: After Sage API ready (1-2 weeks)

3. Retry Policies
   - Implement retry policies in executor path
   - Use default policies (ROUTINE=2, IMPORTANT=1, CRITICAL=0)
   - Timeline: After Sage API ready (1-2 weeks)

4. APOE→CMC v1 Integration
   - Ensure APOE→CMC v1 integration production-ready
   - Verify all 18 tests passing
   - Timeline: Ready now, verify functionality

Post updates on your coordination board as you complete each task.
```

---

## 🔗 **COORDINATION REMINDERS**

**All Agents:**
- Post progress updates on your coordination board
- Coordinate with other agents as dependencies arise
- Reference the final outcomes document for decisions
- Use standardized integration tagging format
- Follow orchestration patterns from Part 4

**Key Coordination Points:**
- Sage → All: VIF witness creation API (1-2 weeks)
- Nova → Sev/Meta: SDF-CVF production wiring coordination (Week 2-3)
- Chronos + Sev: HHNI E2E run (24-48 hours)
- Atlas → All: Integration tagging standardization (can start now)

---

**Status:** ✅ **AGENTS READY TO WORK**  
**Next:** Execute immediate action items, coordinate as needed, post progress updates

