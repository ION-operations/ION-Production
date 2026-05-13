# RAG MCP Tool Proposal - User Input Pre-Processing
**Date:** 2025-11-02  
**Author:** Aether  
**Status:** 📋 **PROPOSAL** - Design Phase  
**Priority:** High  

---

## 🎯 **PROBLEM STATEMENT**

When users interact with AIM-OS, there's no automatic connection to past context, documents, and data. Each interaction starts fresh, requiring manual context retrieval. This creates:
- Context loss across sessions
- Repeated explanations
- Inefficient context building
- Missed connections to related work

---

## 💡 **SOLUTION: RAG MCP Tool**

A special MCP tool that processes user input FIRST, before any other operations, connecting it to all past docs and data via RAG (Retrieval-Augmented Generation).

### **Core Concept**

**Tool Name:** `mcp_lucid-mcp_preprocess_user_input` or `mcp_lucid-mcp_context_enrich` or `mcp_lucid-mcp_rag_enrich`

**Behavior:**
1. User says something → Tool runs FIRST
2. Tool extracts semantic meaning from user input
3. **Tool queries HHNI hierarchically for relevant FILES** (not just concepts) ⭐ **NEW INSIGHT**
4. **Tool respects T-level organization** (chooses T0-T6 based on confidence) ⭐ **NEW INSIGHT**
5. **Tool uses system maps for relationships** (includes related systems) ⭐ **NEW INSIGHT**
6. Tool queries SEG for related knowledge (evidence, contradictions, patterns)
7. Tool queries CMC for related history (past interactions, decisions, learnings)
8. Tool constructs enriched context packet with **intelligently selected files**
9. Tool returns enriched context + original input
10. AI processes enriched context + original input

**Key Innovation:** Instead of simple grep/semantic search, use RAG + HHNI to intelligently select files based on hierarchical structure and perfect organization!

---

## 🔧 **ARCHITECTURE**

### **Tool Signature**

```python
@mcp_tool
async def mcp_lucid-mcp_preprocess_user_input(
    user_input: str,
    context_depth: str = "medium",  # "shallow", "medium", "deep"
    include_docs: bool = True,
    include_timeline: bool = True,
    include_decisions: bool = True,
    include_knowledge: bool = True,
    max_results: int = 10
) -> ContextEnrichmentResult:
    """
    Pre-process user input through RAG, connecting to all past docs and data.
    
    Args:
        user_input: Raw user input text
        context_depth: How deep to retrieve context
        include_docs: Include related documentation
        include_timeline: Include timeline entries
        include_decisions: Include decision logs
        include_knowledge: Include SEG knowledge graph
        
    Returns:
        ContextEnrichmentResult with:
        - original_input: str
        - related_docs: List[DocReference]
        - related_timeline: List[TimelineEntry]
        - related_decisions: List[DecisionLog]
        - related_knowledge: List[KnowledgeNode]
        - enriched_context: str (formatted context packet)
        - confidence_scores: Dict[str, float]
    """
```

### **Integration Points**

**HHNI Integration:**
- Query: `user_input` → Semantic search
- Retrieve: Related documentation, atoms, decisions
- Format: Structured context packets

**SEG Integration:**
- Query: Extract entities/concepts from `user_input`
- Retrieve: Related evidence nodes, contradictions, patterns
- Format: Knowledge graph context

**CMC Integration:**
- Query: Extract timeline markers from `user_input`
- Retrieve: Related timeline entries, decision logs, learnings
- Format: Historical context

**Timeline Context System Integration:**
- Query: Recent timeline entries related to `user_input`
- Retrieve: Session continuity, past decisions
- Format: Continuity context

---

## 📊 **WORKFLOW**

```
User Input
    ↓
[mcp_lucid-mcp_preprocess_user_input]
    ↓
Extract Semantic Meaning
    ↓
Parallel Queries:
    ├─→ HHNI: Related docs/atoms
    ├─→ SEG: Related knowledge
    ├─→ CMC: Related history
    └─→ Timeline: Related entries
    ↓
Construct Enriched Context Packet
    ↓
Return: Enriched Context + Original Input
    ↓
AI Processes Enriched Context
```

---

## 🎨 **CONTEXT PACKET FORMAT**

```markdown
# Enriched Context Packet

## Original Input
{user_input}

## Related Documentation (HHNI)
- [Doc 1]: {title} - {relevance_score}
- [Doc 2]: {title} - {relevance_score}
...

## Related Timeline Entries
- [Timeline Entry 1]: {description} - {timestamp}
- [Timeline Entry 2]: {description} - {timestamp}
...

## Related Decisions (CMC)
- [Decision 1]: {decision_name} - {date}
- [Decision 2]: {decision_name} - {date}
...

## Related Knowledge (SEG)
- [Knowledge Node 1]: {claim} - {confidence}
- [Knowledge Node 2]: {claim} - {confidence}
...

## Contradictions Detected
- {contradiction_description}
...

## Confidence Scores
- Documentation relevance: {score}
- Timeline relevance: {score}
- Decision relevance: {score}
- Knowledge relevance: {score}
```

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Basic RAG Tool (2-3 hours)**
- Create MCP tool stub
- Integrate HHNI for doc retrieval
- Return basic enriched context

### **Phase 2: Multi-Source Integration (4-6 hours)**
- Add SEG knowledge retrieval
- Add CMC timeline/decision retrieval
- Add Timeline Context System integration
- Format enriched context packet

### **Phase 3: Optimization (2-3 hours)**
- Cache frequently accessed context
- Optimize query performance
- Add confidence scoring

### **Phase 4: Auto-Integration (1-2 hours)**
- Auto-trigger on user input
- Seamless integration with AI processing
- Performance monitoring

---

## 📋 **DESIGN CONSIDERATIONS**

### **Performance**
- **Target:** <500ms for context enrichment
- **Caching:** Cache common queries
- **Parallelization:** Parallel queries to HHNI/SEG/CMC

### **Accuracy**
- **Relevance Threshold:** Only include results with relevance > 0.7
- **Confidence Scoring:** Weight results by confidence
- **Deduplication:** Remove duplicate context

### **Integration**
- **Auto-Trigger:** Automatically run on user input
- **Manual Override:** Allow manual trigger with parameters
- **Transparency:** Show what context was retrieved

---

## 🎯 **USE CASES**

### **Use Case 1: Continuity Across Sessions**
- User: "Continue working on APOE"
- RAG Tool: Retrieves all APOE-related docs, timeline entries, decisions
- AI: Has full context immediately

### **Use Case 2: Related Work Discovery**
- User: "Fix the bug in CMC"
- RAG Tool: Retrieves related bug reports, decisions, timeline entries
- AI: Understands full context of the bug

### **Use Case 3: Knowledge Synthesis**
- User: "How does quartet parity work?"
- RAG Tool: Retrieves all quartet parity docs, decisions, implementations
- AI: Provides comprehensive answer with full context

---

## 🔗 **RELATED SYSTEMS**

- **HHNI:** Primary retrieval engine
- **SEG:** Knowledge graph for semantic connections
- **CMC:** Historical context storage
- **Timeline Context System:** Session continuity
- **VIF:** Confidence scoring for retrieved context

---

## 📊 **METRICS**

- **Context Retrieval Time:** <500ms target
- **Relevance Accuracy:** >85% relevant results
- **Coverage:** >90% of user queries have related context
- **User Satisfaction:** Reduced context loss, improved continuity

---

**Status:** 📋 **PROPOSAL** - Ready for Design Review  
**Next Steps:** Design review, implementation planning, tool creation

