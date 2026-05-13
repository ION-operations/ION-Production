# APOE System Map

**Created By:** Alex (APOE System Specialist)  
**Date:** 2025-01-27  
**Status:** Complete  
**Purpose:** Comprehensive system map of APOE showing internal structure, relationships, and data flows

---

## 📋 **EXECUTIVE SUMMARY**

This document provides a comprehensive system map of APOE (AI-Powered Orchestration Engine), showing:
- **8 Internal Components** (core orchestration components)
- **6 Integration Ports** (connections to other AIM-OS systems)
- **8 Internal Edges** (data flows between components)
- **6 External Edges** (data flows to external systems)
- **Risk Overlay** (performance hotspots, security sensitive ports, governance touchpoints)
- **Monitoring** (key metrics and alerts)

**Source:** Based on `system.map.lucid.json5` and `system.index.lucid.json5`

---

## 🏗️ **INTERNAL COMPONENTS**

### **1. ACL Compiler (`aclCompiler`)**
- **Kind:** Core Component
- **Status:** Production
- **Responsibility:** Compiles ACL text into typed, executable plans (ACL → DAG)
- **Performance Budget:** 100ms
- **Security Level:** High
- **Must Never:**
  - Allow invalid ACL syntax
  - Skip type checking
  - Generate plans without budgets
  - Create circular dependencies
- **Files:** `acl_parser.py`, `plix_compiler/plix_to_acl_compiler.py`

### **2. DAG Executor (`dagExecutor`)**
- **Kind:** Core Component
- **Status:** Production
- **Responsibility:** Executes plans as directed acyclic graphs with topological sorting
- **Performance Budget:** 50ms
- **Security Level:** High
- **Must Never:**
  - Execute steps out of order
  - Skip dependency resolution
  - Allow circular execution
  - Lose execution state
- **Files:** `executor.py`, `parallel_execution.py`

### **3. Role Dispatcher (`roleDispatcher`)**
- **Kind:** Orchestration Component
- **Status:** Production
- **Responsibility:** Dispatches steps to appropriate role agents (8 roles: Planner, Retriever, Reasoner, Verifier, Builder, Critic, Operator, Witness)
- **Performance Budget:** 20ms
- **Security Level:** Critical
- **Must Never:**
  - Dispatch to wrong role
  - Skip contract enforcement
  - Allow budget violations
  - Skip VIF witness generation
- **Files:** `role_dispatcher.py`, `roles.py`

### **4. Gate Manager (`gateManager`)**
- **Kind:** Gating Component
- **Status:** Production
- **Responsibility:** Enforces quality, safety, and policy gates with PASS/FAIL/WARN/ABSTAIN routing
- **Performance Budget:** 15ms
- **Security Level:** Critical
- **Must Never:**
  - Bypass gates
  - Skip gate evaluation
  - Allow unsafe operations
  - Lose gate decision reasoning
- **Files:** `advanced_gates.py`, `models.py` (Gate model)

### **5. Budget Tracker (`budgetTracker`)**
- **Kind:** Tracking Component
- **Status:** Production
- **Responsibility:** Tracks and enforces resource budgets (tokens, time, tools)
- **Performance Budget:** 5ms
- **Security Level:** High
- **Must Never:**
  - Allow budget violations
  - Lose budget tracking
  - Skip budget enforcement
  - Exceed resource limits
- **Files:** `budget_pooling.py`, `models.py` (Budget model)

### **6. VIF Witness Generator (`vifWitnessGenerator`)**
- **Kind:** Witness Component
- **Status:** Production
- **Responsibility:** Generates VIF witnesses for every step execution
- **Performance Budget:** 10ms
- **Security Level:** Critical
- **Must Never:**
  - Skip witness generation
  - Lose provenance information
  - Allow witness tampering
  - Create incomplete witnesses
- **Files:** `vif_integration.py`

### **7. DEPP Rewriter (`deppRewriter`)**
- **Kind:** Optimization Component
- **Status:** Development (functional but marked as development)
- **Responsibility:** Self-rewriting plans using SEG evidence for continuous improvement
- **Performance Budget:** 200ms
- **Security Level:** Medium
- **Must Never:**
  - Rewrite plans without evidence
  - Lose plan history
  - Create worse plans
  - Break plan semantics
- **Files:** `depp.py` (SelfModifyingPlan)

### **8. State Manager (`stateManager`)**
- **Kind:** State Component
- **Status:** Production
- **Responsibility:** Manages execution state and enables resumption/recovery
- **Performance Budget:** 30ms
- **Security Level:** High
- **Must Never:**
  - Lose execution state
  - Create inconsistent states
  - Allow state corruption
  - Skip state snapshots
- **Files:** `models.py` (CompensationStep, RetryPolicy), `error_recovery.py`

---

## 🔗 **INTEGRATION PORTS**

### **1. HHNI Integration (`hhniIntegration`)**
- **Direction:** Bidirectional
- **Connects To:** `hhni.hierarchicalHypergraph`
- **Protocol:** Internal API
- **Security Level:** High
- **Data Exchanged:**
  - Context retrieval requests
  - Optimized context
  - Budget-aware queries
  - Retrieval witnesses
- **Purpose:** Context retrieval for Retriever role
- **Files:** `role_dispatcher.py` (Retriever role), `integration/hhni_indexing.py`

### **2. VIF Integration (`vifIntegration`)**
- **Direction:** Bidirectional
- **Connects To:** `vif.verifiableIntelligence`
- **Protocol:** Internal API
- **Security Level:** Critical
- **Data Exchanged:**
  - Execution witnesses
  - Confidence scores
  - Provenance traces
  - Verification requests
- **Purpose:** Witness generation and confidence gating
- **Files:** `vif_integration.py`

### **3. CMC Integration (`cmcIntegration`)**
- **Direction:** Bidirectional
- **Connects To:** `cmc.contextMemoryCore`
- **Protocol:** Internal API
- **Security Level:** High
- **Data Exchanged:**
  - Execution state
  - Plan artifacts
  - Step results
  - State snapshots
- **Purpose:** Execution state storage and persistence
- **Files:** `cmc_integration.py`, `integration/cmc_storage.py`

### **4. SEG Integration (`segIntegration`)**
- **Direction:** Bidirectional
- **Connects To:** `seg.sharedEvidenceGraph`
- **Protocol:** Internal API
- **Security Level:** High
- **Data Exchanged:**
  - Execution traces
  - Evidence nodes
  - Synthesis requests
  - Plan effectiveness data
- **Purpose:** Execution trace synthesis and DEPP evidence
- **Files:** `integration/seg_synthesis.py`

### **5. SDF-CVF Integration (`sdfcvfIntegration`)**
- **Direction:** Bidirectional
- **Connects To:** `sdfcvf.atomicEvolution`
- **Protocol:** Internal API
- **Security Level:** High
- **Data Exchanged:**
  - Quality gate status
  - Parity checks
  - Evolution artifacts
  - Trace emissions
- **Purpose:** Quality gate enforcement and quartet parity
- **Files:** `purity_validation/` (PLIx integration)

### **6. LLM Integration (`llmIntegration`)**
- **Direction:** Outbound
- **Connects To:** `llm.external`
- **Protocol:** API
- **Security Level:** Medium
- **Data Exchanged:**
  - Role execution requests
  - LLM responses
  - Token usage data
  - Model outputs
- **Purpose:** Role execution (all 8 roles can use LLMs)
- **Files:** `role_dispatcher.py`, `model_selector.py`, `execution_orchestrator.py`

---

## 🔄 **INTERNAL DATA FLOWS**

### **1. ACL Compiler → DAG Executor**
- **Type:** Provides Executable Plan
- **Data Flow:** Compiled Plan → DAG Execution
- **Purpose:** Compilation result feeds execution

### **2. DAG Executor → Role Dispatcher**
- **Type:** Provides Execution Steps
- **Data Flow:** Step Requests → Role Dispatch
- **Purpose:** Steps ready for execution are dispatched to roles

### **3. Role Dispatcher → Budget Tracker**
- **Type:** Requests Budget Check
- **Data Flow:** Step Budgets → Budget Validation
- **Purpose:** Budget validation before step execution

### **4. Budget Tracker → Gate Manager**
- **Type:** Provides Budget Status
- **Data Flow:** Budget Status → Gate Evaluation
- **Purpose:** Budget status informs gate decisions

### **5. Gate Manager → DAG Executor**
- **Type:** Provides Gate Decisions
- **Data Flow:** Gate Results → Execution Control
- **Purpose:** Gate decisions control execution flow

### **6. Role Dispatcher → VIF Witness Generator**
- **Type:** Triggers Witness
- **Data Flow:** Step Executions → Witness Generation
- **Purpose:** Every step execution generates a witness

### **7. VIF Witness Generator → State Manager**
- **Type:** Provides Provenance
- **Data Flow:** Witnesses → State Records
- **Purpose:** Witnesses stored in execution state

### **8. State Manager → DAG Executor**
- **Type:** Provides State
- **Data Flow:** Execution State → Step Context
- **Purpose:** Execution state provides context for steps

### **9. DEPP Rewriter → ACL Compiler**
- **Type:** Provides Improved Plans
- **Data Flow:** Rewritten Plans → Compilation
- **Purpose:** Self-modified plans are recompiled

---

## 🌐 **EXTERNAL DATA FLOWS**

### **1. HHNI Integration → HHNI System**
- **Type:** Retrieves Context
- **Data Flow:** Queries → Optimized Context
- **Purpose:** Context retrieval for orchestration

### **2. VIF Integration → VIF System**
- **Type:** Emits Witnesses
- **Data Flow:** Execution Data → Provenance Traces
- **Purpose:** Complete provenance tracking

### **3. CMC Integration → CMC System**
- **Type:** Stores Execution State
- **Data Flow:** Execution Data → Persistent Storage
- **Purpose:** Execution state persistence

### **4. SEG Integration → SEG System**
- **Type:** Provides Execution Traces
- **Data Flow:** Execution Data → Evidence Nodes
- **Purpose:** Execution trace synthesis

### **5. SDF-CVF Integration → SDF-CVF System**
- **Type:** Respects Quartet Parity
- **Data Flow:** Execution Data → Quality Validation
- **Purpose:** Quality gate enforcement

### **6. LLM Integration → LLM Providers**
- **Type:** Executes Role Steps
- **Data Flow:** Role Requests → Model Outputs
- **Purpose:** Role execution via LLMs

---

## ⚠️ **RISK OVERLAY**

### **Performance Hotspots:**
1. **ACL Compiler** - 100ms budget (compilation can be slow)
2. **DAG Executor** - 50ms budget (execution coordination)
3. **Role Dispatcher** - 20ms budget (role selection)
4. **DEPP Rewriter** - 200ms budget (plan rewriting)

### **Security Sensitive Ports:**
1. **VIF Integration** - Critical (witness generation)
2. **CMC Integration** - High (state storage)
3. **LLM Integration** - Medium (external API)

### **Governance Touchpoints:**
1. **Gate Manager** - Quality/safety enforcement
2. **Budget Tracker** - Resource limits
3. **VIF Witness Generator** - Provenance integrity

### **Critical Failure Modes:**
1. **Gate bypass or failure** - Unsafe operations executed
2. **Budget violation** - Resource exhaustion
3. **Witness generation failure** - Provenance lost
4. **State corruption or loss** - Execution unrecoverable
5. **Role dispatch errors** - Wrong role assigned

### **Blast Radius:**
- **ACL Compiler:** All plan executions
- **Gate Manager:** Execution safety
- **Budget Tracker:** Resource limits
- **VIF Witness Generator:** Provenance integrity
- **Role Dispatcher:** Execution quality

---

## 📊 **MONITORING**

### **Key Metrics:**
1. **Plan Compilation Time** - ACL → DAG compilation duration
2. **Execution Success Rate** - Percentage of successful plan executions
3. **Budget Compliance Rate** - Percentage of executions within budget
4. **Gate Pass Rate** - Percentage of gates that pass
5. **Witness Generation Rate** - Percentage of steps with witnesses
6. **Role Execution Latency** - Time to execute role steps

### **Alerts:**
1. **Gate Bypass Detected** - Critical security alert
2. **Budget Violation** - Resource limit exceeded
3. **Witness Generation Failure** - Provenance lost
4. **State Corruption Detected** - Execution state invalid
5. **Role Dispatch Errors** - Wrong role assigned
6. **Execution Timeout** - Plan execution exceeded time limit

---

## 🔍 **CAS INTEGRATION (OBSERVATION)**

**Note:** CAS (Cognitive Analysis System) is listed as a child system in APOE's lineage (`system.index.lucid.json5`), but there is **no explicit integration port** in the system map. This suggests CAS observes APOE execution through indirect means:

1. **Via VIF Witnesses** - CAS analyzes VIF witness envelopes for cognitive patterns
2. **Via CMC State** - CAS analyzes execution state stored in CMC
3. **Via SEG Traces** - CAS analyzes execution traces synthesized in SEG
4. **Via Timeline Entries** - CAS analyzes timeline entries created during execution

**Purpose:** CAS observes APOE decision-making processes for cognitive analysis and introspection.

**Files:** (No direct integration files - observation via other systems)

---

## 📋 **SUMMARY**

**APOE System Map:**
- **8 Internal Components** - All production-ready (except DEPP marked as development)
- **6 Integration Ports** - All required, bidirectional (except LLM outbound)
- **8 Internal Edges** - Complete data flow between components
- **6 External Edges** - Complete data flow to external systems
- **Risk Overlay** - Performance hotspots, security ports, governance touchpoints identified
- **Monitoring** - Key metrics and alerts defined

**Status:** Production-ready orchestration system with comprehensive integration and monitoring.

---

**Status:** System Map Complete ✅  
**Next:** Coordinate with other specialists on integration points, update documentation

