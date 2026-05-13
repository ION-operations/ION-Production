# SEG Usage Envelope

**System:** Shared Evidence Graph (SEG)  
**Version:** v2.2.0  
**Purpose:** Human-centered design documentation for SEG usage patterns  
**Last Updated:** 2025-11-03  

---

## 🎯 **Primary Use Cases**

### **1. Contradiction Detection**
**Human Goal:** "I need to know if the AI is giving me contradictory information"

**Canonical Workflow:**
1. Human asks AI multiple questions over time
2. AI stores all claims in SEG with provenance
3. SEG automatically detects contradictions
4. AI alerts human to contradictory claims
5. Human resolves contradictions with new information

**Success Signals:**
- Contradictions detected automatically
- Detection happens quickly (< 100ms)
- False positive rate < 5%
- Human notified clearly of conflicts

### **2. Knowledge Synthesis**
**Human Goal:** "I want the AI to synthesize knowledge from multiple sources into coherent understanding"

**Canonical Workflow:**
1. Human provides information from multiple sources
2. AI stores each claim in SEG with provenance
3. SEG builds evidence graph linking related claims
4. AI synthesizes coherent view from evidence
5. Human gets unified, well-supported knowledge

**Success Signals:**
- Evidence from multiple sources integrated
- Synthesis respects provenance strength
- Conflicting evidence handled gracefully
- Human gets coherent unified view

### **3. Provenance Tracing**
**Human Goal:** "I need to trace where this knowledge came from"

**Canonical Workflow:**
1. Human questions source of AI knowledge
2. AI queries SEG for claim provenance
3. SEG returns complete evidence chain
4. AI shows: original source → intermediate derivations → final claim
5. Human understands complete knowledge lineage

**Success Signals:**
- Complete provenance chains available
- Source attribution accurate
- Derivation steps clear
- Human can validate knowledge source

---

## 🔧 **Edge Uses**

### **1. Research Literature Review**
**Power User Workflow:** "I'm reviewing research papers and need to track claims and evidence"

**Process:**
- Store each research claim in SEG
- Link claims through citations
- Build evidence graph of research domain
- Query for supporting/contradicting evidence
- Synthesize research consensus

**When Useful:**
- Academic research
- Literature reviews
- Meta-analysis
- Knowledge gap identification

### **2. Collaborative Knowledge Building**
**Power User Workflow:** "Multiple AI agents are contributing knowledge, need to maintain consistency"

**Process:**
- Each agent stores claims in shared SEG
- SEG detects contradictions between agents
- Conflicts resolved through evidence strength
- Consensus emerges from evidence graph
- Collective knowledge maintained

**When Useful:**
- Multi-agent collaboration
- Distributed knowledge building
- Consensus formation
- Collective intelligence

### **3. Knowledge Evolution Tracking**
**Power User Workflow:** "I want to see how understanding evolved over time"

**Process:**
- SEG integrates with CMC bitemporal storage
- Query SEG at different time points
- See how evidence graph changed
- Track knowledge evolution
- Understand paradigm shifts

**When Useful:**
- Scientific discovery tracking
- Understanding concept evolution
- Learning from mistakes
- Historical analysis

---

## ⚠️ **Abuse / Misuse / Dangerous Use**

### **1. Graph Poisoning**
**Danger:** "What if someone injects false claims to corrupt the knowledge graph?"

**Attack Vector:**
- Injecting false claims with fake provenance
- Creating fake evidence links
- Manipulating contradiction detection
- Corrupting graph structure

**Mitigation:**
- VIF witness verification for all claims
- Provenance validation before storage
- Access control and authentication
- Graph integrity checks

**Detection:**
- Monitor for unusual claim patterns
- Validate provenance chains
- Check for orphaned nodes
- Alert on graph structural anomalies

### **2. Contradiction Manipulation**
**Danger:** "What if someone manipulates contradiction detection to hide conflicts?"

**Attack Vector:**
- Modifying semantic similarity thresholds
- Tampering with stance detection
- Corrupting contradiction scoring
- Hiding contradictory evidence

**Mitigation:**
- Contradiction detection parameters audited
- Multiple detection methods
- Threshold validation
- Audit trail for all detections

**Detection:**
- Monitor contradiction detection rates
- Validate semantic similarity calculations
- Check for suppressed contradictions
- Alert on unusual detection patterns

### **3. Evidence Graph Overload**
**Danger:** "What if the graph grows too large and becomes unusable?"

**Attack Vector:**
- Flooding with trivial claims
- Creating excessive evidence links
- Exhausting graph database capacity
- Causing performance degradation

**Mitigation:**
- Claim quality filtering
- Evidence strength thresholding
- Graph pruning and archival
- Resource quotas and budgets

**Detection:**
- Monitor graph size and growth rate
- Alert on excessive claim rates
- Track query performance degradation
- Implement capacity planning

---

## 🎛️ **Impact Surfaces**

### **Performance Impact**
**Latency:**
- Claim storage: ~15ms per claim
- Contradiction detection: ~50ms per claim pair
- Evidence synthesis: ~100ms per synthesis operation
- Provenance query: ~20ms per query

**Throughput:**
- Can process 100+ claims/second
- Contradiction detection scales O(n²) with claims
- Graph queries scale O(log n) with proper indexing

**Resource Usage:**
- Memory: ~1KB per claim node
- Storage: ~10KB per claim with full provenance (in CMC)
- Graph database: Scales with claim count and evidence links

### **System Dependencies**
**SEG Depends On:**
- CMC: Stores graph nodes/edges as atoms
- VIF: Provides provenance for claims
- HHNI: Retrieves related evidence

**Systems Depending On SEG:**
- VIF: Uses evidence graph for witness validation
- APOE: Uses evidence chains for reasoning

**Impact of SEG Failure:**
- CRITICAL: Contradiction detection unavailable
- HIGH: Knowledge synthesis degraded
- MEDIUM: Provenance tracing incomplete

### **User Experience Impact**
**Positive:**
- Automatic contradiction detection
- Synthesized coherent knowledge
- Complete provenance transparency
- Research support

**Negative:**
- Performance overhead (~50-100ms for synthesis)
- Complexity in understanding evidence graphs
- Learning curve for graph queries
- Potential information overload with large graphs

---

## 📊 **Key Metrics**

### **Quality Metrics**
- **Contradiction Detection Accuracy:** Target > 90%
- **False Positive Rate:** Target < 5%
- **Provenance Chain Completeness:** Target 100%
- **Evidence Synthesis Quality:** Target > 85% user satisfaction

### **Performance Metrics**
- **Claim Storage Latency:** Target < 15ms
- **Contradiction Detection Latency:** Target < 50ms per pair
- **Evidence Synthesis Latency:** Target < 100ms
- **Provenance Query Latency:** Target < 20ms

### **Reliability Metrics**
- **Graph Integrity:** Target 100% (no orphaned nodes)
- **Provenance Completeness:** Target 100%
- **Contradiction Detection Coverage:** Target > 95% of conflicts detected

---

## 🚧 **Boundaries & Limitations**

### **What SEG Does**
✅ Detects contradictions between claims  
✅ Builds evidence graphs with provenance  
✅ Synthesizes knowledge from multiple sources  
✅ Tracks claim evolution over time  
✅ Provides complete provenance tracing  

### **What SEG Does NOT Do**
❌ Resolve contradictions automatically (requires human/HITL)  
❌ Validate truth of claims (relies on VIF provenance)  
❌ Generate new knowledge (only synthesizes existing)  
❌ Guarantee contradiction detection (depends on semantic similarity)  
❌ Store claims (delegates to CMC)  

### **When to Use SEG**
- ✅ Research and knowledge synthesis
- ✅ Multi-source information integration
- ✅ Contradiction detection needs
- ✅ Provenance tracking requirements
- ✅ Collaborative knowledge building

### **When NOT to Use SEG**
- ❌ Simple fact storage without relationships
- ❌ Performance-critical paths (< 50ms budgets)
- ❌ Single-source information
- ❌ When contradictions are irrelevant

---

## 🔗 **Integration Patterns**

### **SEG + CMC: Evidence Storage**
```
Claim → SEG Processes → Store as CMC Atom → Bitemporal Tracking
```
- Claims stored with valid time and transaction time
- Evidence graph persists in CMC
- Time-travel queries on knowledge evolution

### **SEG + VIF: Verified Claims**
```
Claim + VIF Witness → SEG Validates → Store with Provenance
```
- Every claim has VIF provenance
- Witness chains tracked in graph
- Trust maintained through verification

### **SEG + APOE: Evidence-Based Reasoning**
```
APOE Reasoning Step → SEG Provides Evidence → Decision with Support
```
- APOE queries SEG for supporting evidence
- Evidence strengthens reasoning
- Contradictions flagged for HITL

---

**Status:** Production-ready knowledge synthesis and contradiction detection  
**Target Audience:** All systems requiring knowledge integration and consistency  
**Key Benefit:** Makes AI knowledge coherent, traceable, and contradiction-aware
