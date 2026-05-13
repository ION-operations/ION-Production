# MCP Tools Enhancement - Implementation Plan
**Created:** 2025-11-01  
**Objective:** OBJ-07 - MCP Tools Enhancement  
**Status:** Starting Phase 1 - Core System Integration

---

## 🎯 **EXECUTIVE SUMMARY**

**Goal:** Transform `create_plan` from placeholder to real APOE integration, enabling true orchestration capabilities through MCP.

**Current State:**
- ✅ `get_memory_stats` - Complete CMC integration
- ✅ `store_memory` - Complete CMC bitemporal integration  
- ✅ `retrieve_memory` - Complete HHNI integration
- ✅ `track_confidence` - Complete VIF integration
- ⏳ `create_plan` - **NEXT: Placeholder → Real APOE**

**Target:** Replace static 3-step plan with real APOE plan compilation and execution.

---

## 📋 **IMPLEMENTATION PLAN**

### **Phase 1: Enhance `create_plan` with APOE Integration**

**Current Implementation:** Returns static 3-step plan (lines 2002-2040)

**Target Implementation:**
1. Accept goal/context/priority from args
2. Use APOE `ACLParser` if ACL provided
3. Otherwise, generate ExecutionPlan from goal description
4. Return structured plan with steps, roles, dependencies
5. Optionally execute plan if `execute=true` provided

**Integration Points:**
- `packages/apoe/acl_parser.py` - ACLParser.parse() for ACL parsing
- `packages/apoe/models.py` - ExecutionPlan, Step, RoleConfig models
- `packages/apoe/executor.py` - PlanExecutor for execution
- `packages/apoe/execution_orchestrator.py` - High-level orchestration

**Estimated Time:** 8-12 hours  
**Confidence:** 0.85 (APOE is 90% complete, well-documented)

---

## ✅ **SUCCESS CRITERIA**

1. `create_plan` accepts goal/context/priority and returns ExecutionPlan
2. Supports ACL parsing if ACL text provided
3. Supports goal-to-plan generation if no ACL provided
4. Returns structured plan with steps, roles, dependencies
5. Optionally executes plan if requested
6. Comprehensive error handling
7. Logs integration with CMC for persistence

---

**Status:** Ready to implement  
**Next Step:** Enhance `create_plan` function in `lucid_mcp_server.py`

