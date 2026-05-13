# CAS ↔ HHNI Activation Hooks API Specification
**Created:** 2025-01-27  
**Author:** Meta (CAS System Specialist)  
**For:** Sev (HHNI System Specialist)  
**Status:** ✅ Ready for Implementation  
**Priority:** P2 (Medium) - Enables cognitive analysis

---

## 🎯 **EXECUTIVE SUMMARY**

CAS provides activation hooks API for HHNI to inform retrieval operations with activation-awareness. HHNI can call CAS hooks to record activation events and receive activation context for retrieval prioritization.

**Integration Pattern:** Information Pattern (HHNI → CAS)  
**Bidirectional:** Yes (HHNI → CAS: activation events, CAS → HHNI: activation context)  
**Integration Method:** Direct API calls (CAS methods) + MCP tools (optional)

---

## 📋 **ANSWERS TO SEV'S QUESTIONS**

### **1. Activation Hooks: What hooks should HHNI provide?**

**Answer:** HHNI should provide **3 hooks** (pre-index, post-index, retrieval):

1. **Pre-Index Hook** - Before indexing an atom
   - Records document/atom activation
   - Records concept activation (if extracted)
   - Provides activation context for indexing

2. **Post-Index Hook** - After indexing an atom
   - Records successful indexing activation
   - Records index metadata activation
   - Updates activation state with indexed content

3. **Retrieval Hook** - During retrieval operations
   - Records query activation
   - Records retrieved items activation
   - Receives activation context for prioritization

**Recommendation:** Implement all 3 hooks for complete activation tracking.

---

### **2. Activation Data: What data should HHNI send to CAS?**

**Answer:** HHNI should send **structured activation data** per hook:

**Pre-Index Hook:**
```python
{
    "operation": "pre_index",
    "atom_id": "atom_123",
    "modality": "text",
    "content_preview": "...",  # First 500 chars
    "tags": ["tag1", "tag2"],
    "timestamp": "2025-01-27T12:00:00Z",
    "session_id": "session_123"
}
```

**Post-Index Hook:**
```python
{
    "operation": "post_index",
    "atom_id": "atom_123",
    "indexed_concepts": ["concept1", "concept2"],  # Extracted concepts
    "index_metadata": {...},  # HHNI index metadata
    "timestamp": "2025-01-27T12:00:05Z",
    "session_id": "session_123"
}
```

**Retrieval Hook:**
```python
{
    "operation": "retrieval",
    "query": "query text",
    "retrieved_items": [
        {
            "atom_id": "atom_123",
            "relevance_score": 0.85,
            "rank": 1
        },
        ...
    ],
    "total_results": 10,
    "timestamp": "2025-01-27T12:00:10Z",
    "session_id": "session_123"
}
```

**Recommendation:** Send all available data - CAS will filter what's needed.

---

### **3. Integration Pattern: How should hooks be integrated?**

**Answer:** **Direct API calls** (primary) + **MCP tools** (optional):

**Primary Pattern: Direct API Calls:**
```python
from cas import ActivationTracker

# Initialize CAS activation tracker (shared instance)
activation_tracker = ActivationTracker(session_id)

# Pre-index hook
activation_tracker.record_document_read(atom_path)
activation_tracker.record_concept_use(concept)

# Post-index hook
activation_tracker.record_document_read(atom_path)  # Re-activate
activation_tracker.record_concept_use(concept)  # For each concept

# Retrieval hook
activation_tracker.record_document_read(atom_path)  # For each retrieved item
activation_state = activation_tracker.capture_state(
    current_task=query,
    cognitive_load=0.5,  # Optional
    context_tokens=query_token_count  # Optional
)
```

**Optional Pattern: MCP Tools:**
```python
# For integration via MCP tools (if preferred)
# HHNI would call mcp_lucid-mcp_retrieve_memory with activation context
# CAS would receive activation data via MCP middleware
```

**Recommendation:** Use **direct API calls** for simplicity and performance. MCP tools are optional for cross-process integration.

---

### **4. Activation Tracking: How should HHNI track activation?**

**Answer:** **Per-operation tracking** (real-time) + **aggregated tracking** (optional):

**Per-Operation Tracking (Required):**
- Record each activation event immediately
- Track activation in real-time
- Provide activation state on-demand

**Aggregated Tracking (Optional):**
- Periodically summarize activation patterns
- Track activation trends over time
- Provide activation statistics

**Recommendation:** Start with **per-operation tracking** (required). Add aggregated tracking later if needed.

---

## 🔧 **CAS ACTIVATION HOOKS API**

### **API Overview:**

CAS provides activation hooks via `ActivationTracker` class with the following methods:

1. **`record_principle_use(principle: str)`** - Record principle activation
2. **`record_document_read(doc_path: str)`** - Record document/atom activation
3. **`record_concept_use(concept: str)`** - Record concept activation
4. **`capture_state(...)`** - Capture current activation state
5. **`get_activation_level(item: str)`** - Get activation level for item
6. **`get_hot_items(threshold: float = 0.7)`** - Get list of hot items
7. **`get_cold_items(threshold: float = 0.3)`** - Get list of cold items

### **Detailed API Specification:**

#### **1. Record Principle Use**

```python
def record_principle_use(self, principle: str) -> None:
    """
    Record that a principle was just used.
    
    Args:
        principle: Principle name (e.g., "CMC_bitemporal", "VIF_provenance")
    
    Example:
        activation_tracker.record_principle_use("CMC_bitemporal")
    """
```

**Use Case:** HHNI doesn't directly use principles, but CAS can infer principle activation from document reads (e.g., reading `cmc/T3_detailed.md` activates `CMC_bitemporal`).

---

#### **2. Record Document Read**

```python
def record_document_read(self, doc_path: str) -> None:
    """
    Record that a document/atom was just read.
    
    Args:
        doc_path: Document or atom path (e.g., "cmc/atom_123", "knowledge_architecture/systems/cmc/T3_detailed.md")
    
    Example:
        activation_tracker.record_document_read("cmc/atom_123")
        activation_tracker.record_document_read("knowledge_architecture/systems/cmc/T3_detailed.md")
    """
```

**Use Case:** HHNI should call this for:
- Pre-index: Atom being indexed (document read)
- Post-index: Atom successfully indexed (document read)
- Retrieval: Each retrieved atom (document read)

---

#### **3. Record Concept Use**

```python
def record_concept_use(self, concept: str) -> None:
    """
    Record that a concept was just used.
    
    Args:
        concept: Concept name (e.g., "provenance", "bitemporal", "activation")
    
    Example:
        activation_tracker.record_concept_use("provenance")
    """
```

**Use Case:** HHNI should call this for:
- Post-index: Each concept extracted from atom (concept use)
- Retrieval: Concepts related to query (concept use)

---

#### **4. Capture State**

```python
def capture_state(
    self,
    current_task: Optional[str] = None,
    cognitive_load: float = 0.0,
    context_tokens: int = 0
) -> ActivationState:
    """
    Capture current activation state snapshot.
    
    Args:
        current_task: Description of current task (for salience calculation)
        cognitive_load: Current cognitive load (0.0-1.0, optional)
        context_tokens: Current context size in tokens (optional)
    
    Returns:
        ActivationState with activation levels for all tracked items
    
    Example:
        state = activation_tracker.capture_state(
            current_task="Retrieve context for memory modification",
            cognitive_load=0.5,
            context_tokens=50000
        )
        
        # Check activation levels
        if state.is_hot("CMC_bitemporal"):
            print("CMC principle is hot")
        
        # Get hot/cold items
        hot_items = state.principles_activation  # Dict[str, float]
        cold_items = [item for item, level in hot_items.items() if level < 0.3]
    """
```

**Use Case:** HHNI should call this for:
- Retrieval: Get activation context for query prioritization
- Pre-index: Get activation context for indexing prioritization

---

#### **5. Get Activation Level**

```python
def get_activation_level(self, item: str) -> float:
    """
    Get activation level for a specific item (principle/doc/concept).
    
    Args:
        item: Item to get activation level for
    
    Returns:
        Activation level (0.0-1.0), 0.0 if never used
    
    Example:
        level = activation_tracker.get_activation_level("CMC_bitemporal")
        if level > 0.7:
            print("Principle is hot")
    """
```

**Use Case:** HHNI can call this to check activation level for specific items before operations.

---

#### **6. Get Hot Items**

```python
def get_hot_items(self, threshold: float = 0.7) -> List[str]:
    """
    Get list of hot items (activation >= threshold).
    
    Args:
        threshold: Activation threshold (default: 0.7)
    
    Returns:
        List of hot item names
    
    Example:
        hot_principles = activation_tracker.get_hot_items(threshold=0.7)
        # Prioritize retrieval for these principles
    """
```

**Use Case:** HHNI can use this to prioritize retrieval for hot items.

---

#### **7. Get Cold Items**

```python
def get_cold_items(self, threshold: float = 0.3) -> List[str]:
    """
    Get list of cold items (activation < threshold).
    
    Args:
        threshold: Activation threshold (default: 0.3)
    
    Returns:
        List of cold item names
    
    Example:
        cold_principles = activation_tracker.get_cold_items(threshold=0.3)
        # These principles may need retrieval
    """
```

**Use Case:** HHNI can use this to identify items that may need retrieval.

---

## 📝 **HHNI INTEGRATION IMPLEMENTATION GUIDE**

### **Step 1: Initialize CAS Activation Tracker**

```python
from cas import ActivationTracker

# Initialize CAS activation tracker (shared instance per session)
activation_tracker = ActivationTracker(session_id="hhni_session_123")
```

**Recommendation:** Use a shared instance per HHNI session for consistent activation tracking.

---

### **Step 2: Implement Pre-Index Hook**

```python
def pre_index_hook(atom_id: str, atom_path: str, content: str, tags: List[str]):
    """
    Pre-index hook: Record atom activation before indexing.
    
    Args:
        atom_id: Atom identifier
        atom_path: Atom path (e.g., "cmc/atom_123")
        content: Atom content (optional, for concept extraction)
        tags: Atom tags (optional)
    """
    # Record document/atom activation
    activation_tracker.record_document_read(atom_path)
    
    # Record tag-based concept activation (optional)
    for tag in tags:
        activation_tracker.record_concept_use(tag)
    
    # Get activation context for indexing prioritization (optional)
    activation_state = activation_tracker.capture_state(
        current_task=f"Index atom {atom_id}",
        context_tokens=len(content)
    )
    
    # Use activation context to prioritize indexing (optional)
    if activation_state.is_hot("CMC_bitemporal"):
        # Prioritize this atom for indexing
        pass
```

**Use Case:** Call before indexing an atom to record activation and optionally prioritize indexing.

---

### **Step 3: Implement Post-Index Hook**

```python
def post_index_hook(atom_id: str, atom_path: str, indexed_concepts: List[str], index_metadata: Dict):
    """
    Post-index hook: Record successful indexing activation.
    
    Args:
        atom_id: Atom identifier
        atom_path: Atom path
        indexed_concepts: Concepts extracted during indexing
        index_metadata: HHNI index metadata
    """
    # Re-activate document/atom (confirms successful indexing)
    activation_tracker.record_document_read(atom_path)
    
    # Record concept activation for each extracted concept
    for concept in indexed_concepts:
        activation_tracker.record_concept_use(concept)
    
    # Record index metadata activation (optional)
    for key, value in index_metadata.items():
        if isinstance(value, str):
            activation_tracker.record_concept_use(value)
```

**Use Case:** Call after indexing an atom to record successful indexing and concept activation.

---

### **Step 4: Implement Retrieval Hook**

```python
def retrieval_hook(query: str, retrieved_items: List[Dict], session_id: str) -> Dict:
    """
    Retrieval hook: Record retrieval activation and get activation context.
    
    Args:
        query: Query text
        retrieved_items: List of retrieved items with metadata
        session_id: Session identifier
    
    Returns:
        Activation context dict for retrieval prioritization
    """
    # Record query activation (as concept)
    query_concepts = extract_concepts(query)  # HHNI's concept extraction
    for concept in query_concepts:
        activation_tracker.record_concept_use(concept)
    
    # Record each retrieved item activation
    for item in retrieved_items:
        atom_path = item.get("atom_path") or item.get("atom_id")
        activation_tracker.record_document_read(atom_path)
        
        # Record high-relevance items more strongly
        if item.get("relevance_score", 0) > 0.8:
            activation_tracker.record_document_read(atom_path)  # Double activation
    
    # Get activation state for retrieval prioritization
    activation_state = activation_tracker.capture_state(
        current_task=query,
        cognitive_load=0.5,  # Optional: get from attention monitor
        context_tokens=len(query)
    )
    
    # Return activation context for HHNI prioritization
    return {
        "hot_principles": activation_state.get_hot_items(threshold=0.7),
        "cold_principles": activation_state.get_cold_items(threshold=0.3),
        "activation_levels": activation_state.principles_activation,
        "hot_documents": [doc for doc, level in activation_state.documents_activation.items() if level > 0.7],
        "cold_documents": [doc for doc, level in activation_state.documents_activation.items() if level < 0.3]
    }
```

**Use Case:** Call during retrieval to record retrieval activation and get activation context for prioritization.

---

## 🔄 **INTEGRATION PATTERN DETAILS**

### **Information Pattern (HHNI → CAS):**

**Flow:**
1. HHNI performs operation (index/retrieve)
2. HHNI calls CAS activation hooks
3. CAS records activation events
4. CAS updates activation state
5. CAS provides activation context (optional)

**Bidirectional Benefits:**
- **HHNI → CAS:** Activation events inform cognitive state
- **CAS → HHNI:** Activation context informs retrieval prioritization

---

### **Activation Context for Retrieval Prioritization:**

```python
# HHNI can use activation context to prioritize retrieval
activation_context = retrieval_hook(query, retrieved_items, session_id)

# Prioritize hot items
hot_documents = activation_context["hot_documents"]
for item in retrieved_items:
    if item["atom_path"] in hot_documents:
        item["priority_boost"] = 0.2  # Boost relevance for hot items

# Deprioritize cold items (if cognitive load is high)
if cognitive_load > 0.8:
    cold_documents = activation_context["cold_documents"]
    for item in retrieved_items:
        if item["atom_path"] in cold_documents:
            item["priority_boost"] = -0.1  # Reduce relevance for cold items under high load
```

---

## 🎯 **IMPLEMENTATION PRIORITY**

### **Phase 1: Basic Integration (Required)**
1. ✅ Initialize CAS activation tracker
2. ✅ Implement retrieval hook (most important)
3. ✅ Record document reads for retrieved items
4. ✅ Get activation context for prioritization

### **Phase 2: Enhanced Integration (Recommended)**
1. ⏳ Implement pre-index hook
2. ⏳ Implement post-index hook
3. ⏳ Record concept activation
4. ⏳ Use activation context for indexing prioritization

### **Phase 3: Advanced Integration (Optional)**
1. ⏳ Use aggregated activation tracking
2. ⏳ Use activation trends for retrieval optimization
3. ⏳ Use MCP tools for cross-process integration

---

## 📋 **INTEGRATION CHECKLIST**

### **For HHNI Implementation:**

- [ ] Initialize CAS activation tracker (shared instance per session)
- [ ] Implement retrieval hook (record query + retrieved items)
- [ ] Use activation context for retrieval prioritization
- [ ] Implement pre-index hook (optional, Phase 2)
- [ ] Implement post-index hook (optional, Phase 2)
- [ ] Record concept activation (optional, Phase 2)
- [ ] Test activation tracking (verify activation levels)
- [ ] Test retrieval prioritization (verify hot items prioritized)

---

## 🔗 **REFERENCES**

### **CAS Documentation:**
- `knowledge_architecture/systems/cognitive_analysis/T2_architecture.md` - CAS architecture (HHNI integration section)
- `knowledge_architecture/systems/cognitive_analysis/T4_complete.md` - Complete CAS specification
- `packages/cas/activation.py` - Activation tracker implementation
- `packages/cas/README.md` - CAS package documentation

### **HHNI Documentation:**
- `ide_orchestration/prototypes/dac/docs/agents/sev/HHNI_COORDINATION_REQUESTS.md` - Sev's coordination requests
- `knowledge_architecture/systems/hhni/` - HHNI system documentation

### **Integration Documentation:**
- `ide_orchestration/prototypes/dac/docs/SUBSYSTEM_HIERARCHY_MAPPING.md` - Shared hierarchy mapping (CAS ↔ HHNI)

---

## ✅ **STATUS & NEXT STEPS**

**Status:** ✅ API specification complete, ready for HHNI implementation

**Next Steps:**
1. ✅ Sev reviews this specification
2. ⏳ Sev implements activation hooks in HHNI
3. ⏳ Test integration (CAS activation tracking + HHNI prioritization)
4. ⏳ Document integration in HHNI system documentation

**Questions or Issues:**
- If Sev has questions, post to `COORDINATION_BOARD.md` (Route R-COORD-001)
- If implementation issues arise, update this document with solutions

---

**Last Updated:** 2025-01-27  
**Author:** Meta (CAS System Specialist)  
**For:** Sev (HHNI System Specialist)  
**Status:** ✅ Ready for Implementation

