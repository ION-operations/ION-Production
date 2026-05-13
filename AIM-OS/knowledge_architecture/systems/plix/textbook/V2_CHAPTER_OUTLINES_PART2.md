# PLIX Textbook v2.0: Chapter Outlines (Part II)

**Status:** 📋 **IN PROGRESS**  
**Continuation:** Part III-VII outlines

---

## 📋 **PART III: INTEGRATION** (Chapters 11-15)

### **Chapter 11: CMC Integration: Intent-Aware Memory**
**Status:** ✅ Keep v1.0, enhance with tags  
**Word Count:** 2,500-3,000 (was 2,000-2,500)

**Enhancements:**
- ➕ Add tag storage in CMC
- ➕ Add tag-based queries
- ➕ Add bitemporal tag versioning

**Sections:**
1. Before PLIx: Fact Storage (keep)
2. After PLIx: Intent Memory (enhance with tags)
3. Transformation Details (enhance with tag storage)
4. Implementation Examples (enhance with tag examples)
5. **NEW:** Tag Storage in CMC
6. **NEW:** Tag-Based Queries

---

### **Chapter 12: VIF Integration: Intent-Aware Verification**
**Status:** ✅ Keep v1.0, enhance with tags  
**Word Count:** 2,500-3,000 (was 2,000-2,500)

**Enhancements:**
- ➕ Add tag-based witness generation
- ➕ Add tag confidence tracking
- ➕ Add tag-based verification

**Sections:**
1. Before PLIx: Execution Verification (keep)
2. After PLIx: Intent Verification (enhance with tags)
3. Intent Confidence Tracking (enhance with tags)
4. Intent Witness Creation (enhance with tags)
5. **NEW:** Tag-Based Witness Generation

---

### **Chapter 13: APOE Integration: Intent-Aware Orchestration**
**Status:** ✅ Keep v1.0, enhance with tags  
**Word Count:** 2,500-3,000 (was 2,000-2,500)

**Enhancements:**
- ➕ Add tag resolution in APOE
- ➕ Add tag-based capability routing
- ➕ Add tag-based execution planning

**Sections:**
1. Before PLIx: Plan Execution (keep)
2. After PLIx: Intent Achievement (enhance with tags)
3. PLIx IR → APOE Compilation (enhance with tags)
4. Intent Verification Integration (keep)
5. **NEW:** Tag Resolution in APOE
6. **NEW:** Tag-Based Capability Routing

---

### **Chapter 14: SEG Integration: Intent-Aware Evidence**
**Status:** ✅ Keep v1.0, enhance with tags  
**Word Count:** 2,500-3,000 (was 2,000-2,500)

**Enhancements:**
- ➕ Add tag-based evidence tracking
- ➕ Add tag lineage in SEG
- ➕ Add tag-based contradiction detection

**Sections:**
1. Before PLIx: Evidence Chains (keep)
2. After PLIx: Intent Lineage (enhance with tags)
3. Intent Evolution Tracking (enhance with tags)
4. Intent-Outcome Mapping (enhance with tags)
5. **NEW:** Tag-Based Evidence Tracking
6. **NEW:** Tag Lineage in SEG

---

### **Chapter 15: NEW - Tag Registry: Lifecycle and Governance** ⭐ **CRITICAL**
**Status:** 🆕 **NEW CHAPTER**  
**Word Count:** 3,000-3,500  
**Priority:** ⚠️ **HIGHEST**

**Sections:**

**15.1 Tag Registration Process**
- Registering new tags
- Authority tier requirements
- Tag metadata
- Registration examples

**15.2 Tag Resolution: Multi-Source Lookup**
- Resolution priority (Registry → HHNI → SEG → CMC)
- Cache-first resolution
- Fallback mechanisms
- Resolution examples

**15.3 Tag Queries**
- Query by namespace
- Query by path pattern
- Query by authority tier
- Query by date range
- Pagination support

**15.4 Rename Governance Workflow**
- Authority tier validation
- Dependent tracking
- Dependent acknowledgment
- Rename completion
- Rename examples

**15.5 Authority Tier System**
- Tier definitions (S, A, B, C)
- Tier validation
- Tier-based operations
- Tier examples

**15.6 Tag Lifecycle Examples**
- Complete lifecycle: Registration → Usage → Rename → Deprecation
- Real-world scenarios
- Best practices

**Learning Objectives:**
- Understand tag registration process
- Master tag resolution
- Use tag queries effectively
- Understand rename governance
- Apply authority tiers correctly

**Cross-References:**
- Chapter 5: Tag System (foundation)
- Chapter 20: PLIX-to-AIP Compiler (tag resolution in compiler)
- Spec Section 2.1: Tag System
- Spec Section 7.3: Registry API

---

## 📋 **PART IV: IMPLEMENTATION** (Chapters 16-20)

### **Chapter 16: PLIX Parser Implementation** ⭐ **RENAME & ENHANCE**
**Status:** 🔄 **RENAME from "CNL Compiler"**  
**Word Count:** 3,000-3,500 (was 2,000-2,500)  
**Priority:** ⚠️ **HIGH**

**Sections:**

**16.1 Parser Architecture**
- Lexical analysis
- Syntax analysis
- Semantic analysis
- Code generation

**16.2 Parsing Human-PLIX**
- Indentation-based parsing
- Optional delimiters (`{}`)
- Tag validation
- Constraint parsing

**16.3 Parsing Canonical JSON**
- JSON Schema validation
- Structure parsing
- Type validation
- Error detection

**16.4 Parsing S-Form**
- S-expression parsing
- Tokenization
- Structure parsing
- Error detection

**16.5 Tag Validation**
- Tag format validation
- Tag resolution checking
- Dangling reference detection
- Error reporting

**16.6 Error Detection and Reporting**
- Dangling references
- Malformed URNs
- Circular dependencies
- Indentation ambiguity
- Clear error messages

**16.7 Parser Implementation Examples**
- Complete parser code examples
- Test cases
- Edge case handling

**Learning Objectives:**
- Understand parser architecture
- Implement parser for all three forms
- Validate tags correctly
- Handle errors effectively

**Cross-References:**
- Chapter 6: Three Surface Forms (what to parse)
- Chapter 10: Error Taxonomy (error handling)
- Spec Section 3.3: Parser Edge Cases
- Spec Section 7.1: Parser API

---

### **Chapter 17: Runtime Implementation: Durable Execution and Recovery**
**Status:** ✅ Keep v1.0, enhance with errors  
**Word Count:** 2,500-3,000 (was 2,000-2,500)

**Enhancements:**
- ➕ Add error handling in runtime
- ➕ Add error action execution
- ➕ Add error recovery mechanisms

**Sections:**
1. Durable Execution Engine (keep)
2. Saga Pattern Implementation (keep)
3. Recovery Mechanisms (enhance with errors)
4. State Persistence (keep)
5. **NEW:** Error Handling in Runtime
6. **NEW:** Error Action Execution

---

### **Chapter 18: Provenance Emitters: PROV/OpenLineage**
**Status:** ✅ Keep v1.0, enhance with tags  
**Word Count:** 2,500-3,000 (was 2,000-2,500)

**Enhancements:**
- ➕ Add tag-based provenance
- ➕ Add tag lineage tracking

**Sections:**
1. PROV-JSON Emission (keep)
2. OpenLineage Events (keep)
3. SEG Integration (enhance with tags)
4. Provenance Queries (enhance with tags)
5. **NEW:** Tag-Based Provenance

---

### **Chapter 19: Policy Emission: OPA/Rego Integration**
**Status:** ✅ Keep v1.0, enhance with tags  
**Word Count:** 2,500-3,000 (was 2,000-2,500)

**Enhancements:**
- ➕ Add tag-based policy rules
- ➕ Add tag-based authorization

**Sections:**
1. OPA Integration (keep)
2. Rego Generation (keep)
3. Policy Evaluation (enhance with tags)
4. Policy Testing (keep)
5. **NEW:** Tag-Based Policy Rules

---

### **Chapter 20: NEW - PLIX-to-AIP Compiler: Complete Integration** ⭐ **CRITICAL**
**Status:** 🆕 **NEW CHAPTER**  
**Word Count:** 3,000-3,500  
**Priority:** ⚠️ **HIGHEST**

**Sections:**

**20.1 PLIX → AIP Graph Compilation**
- Mapping PLIX to AIP nodes
- Entity/action/capability nodes
- Constraint/test/evidence nodes
- Dependency/compensation edges
- Complete compilation examples

**20.2 Tag Resolution via HHNI/SEG/CMC**
- Multi-source tag resolution
- Resolution priority
- Resolution caching
- Resolution examples

**20.3 PLIX → APOE Execution Plan**
- Plan step mapping
- Dependency graph mapping
- Error clause → APOE gate mapping
- Retry specification → APOE budget mapping
- Complete compilation examples

**20.4 VIF Witness Requirement Generation**
- Plan-level witness requirements
- Step-level witness requirements
- Confidence threshold mapping
- Evidence type mapping
- Witness generation examples

**20.5 Complete Integration Examples**
- Database migration (full example)
- Room booking (full example)
- User authentication (full example)
- All showing PLIX → AIP → APOE → VIF flow

**20.6 Integration Best Practices**
- Tag usage best practices
- Constraint best practices
- Error handling best practices
- Performance optimization

**Learning Objectives:**
- Understand PLIX → AIP compilation
- Master tag resolution
- Understand APOE compilation
- Generate VIF witnesses
- Integrate with AIM-OS completely

**Cross-References:**
- Chapter 5: Tag System (tag resolution)
- Chapter 15: Tag Registry (registry integration)
- Chapter 11-14: AIM-OS Integration (all systems)
- Spec Section 4: Semantics (compilation semantics)
- Spec Section 7.2: Compiler API

---

**Status:** 📋 **IN PROGRESS**  
**Next:** Continue with Part V-VII outlines

