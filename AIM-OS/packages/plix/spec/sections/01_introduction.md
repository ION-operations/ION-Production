# Section 1: Introduction/Overview

**Status:** ✅ **EXTRACTED FROM TEXTBOOK**  
**Source:** PLIX Textbook Part I: Foundations (Chapters 1-4)  
**Last Updated:** 2025-01-27

---

## **1.1 One-Line Definition**

**PLIX is a typed, tag-centric protocol language for expressing deterministic intent, enabling AI consciousness, and integrating with AIM-OS via AIP (Application Integration Protocol).**

---

## **1.2 Design Goals and Philosophy**

### **Core Principles**

**1. Deterministic Meaning**
- Every important noun/verb is a **tagged identity**, not a loose string
- Tags provide canonical identity: `plix://namespace/path#rev@hash`
- Enables precise reference and rename safety

**2. Executable Intent**
- Every request compiles to an **AIP route** (tools, calls, pre/postconditions)
- Intent is executable without specifying mechanism
- Enables intent achievement via multiple execution paths

**3. Provable Claims**
- Assertions carry **tests** and **witness/evidence hooks** (VIF)
- Claims are verifiable, not rhetorical
- Enables confidence tracking and quality assurance

**4. Bitemporal Truth**
- All facts carry `tx_time` (transaction time) and `valid_time` (valid time)
- Enables temporal queries and audit trails
- Supports "what did we know when" and "what was valid when" queries

**5. Evolvable Grammar**
- The language extends through **algorithmic proposals** (GGPs) with proofs and tests
- Grammar evolution is governed, not ad-hoc
- Enables controlled language growth

**6. Human-First Surface, Machine-First Core**
- Readable forms (Human-PLIX) map 1:1 to canonical JSON
- Enables both human readability and machine execution
- Supports round-trip conversion without loss

### **The Problem: Intent-Execution Gap**

Current AI systems operate in a fundamentally limited way: they are execution-focused and mechanism-bound. When we interact with AI, we express what we want in natural language, but the AI immediately translates this into specific implementation steps—API calls, database queries, code generation. The intent—what we actually want to achieve—becomes lost in the mechanism of how to achieve it.

**Example of Impure Code:**
```python
# Impure: Intent mixed with execution
def book_meeting_room(date, duration, user_id):
    # Intent: Book a meeting room
    # But also execution: Call API, update database, send email
    response = api_client.post('/rooms/reserve', {...})
    db.update('reservations', {'room_id': response.room_id})
    email_service.send_confirmation(user_id, response.room_id)
    return response.room_id
```

**PLIX Pure Intent:**
```plix
ensure ent:plix://room/meeting_room
  act:book
  with:
    date: "2025-12-01"
    duration: "2h"
  pre:
    con:room_available == true
    con:user_authenticated == true
  post:
    con:room_reserved == true
    con:calendar_event_created == true
  tests:
    test:room_confirmed
    test:no_conflicts
```

The PLIX contract expresses **what we want** (book a room) without specifying **how we achieve it** (which API, which database, which email service).

### **What Makes Language "Pure"?**

**Purity = Separation**
- Pure language separates intent from execution
- Mathematical notation is pure: `x² + y² = r²` expresses relationship without computation mechanism
- PLIX is pure: expresses intent without implementation mechanism

**Purity = Timelessness**
- Pure language expresses intent that doesn't change with implementation
- Mathematical notation is timeless: same meaning regardless of computational method
- PLIX contracts are timeless: same intent regardless of execution mechanism

**Purity = Verifiability**
- Pure language enables verification independent of execution
- Mathematical notation is verifiable: can prove without computing
- PLIX contracts are verifiable: can verify intent without executing mechanism

---

## **1.3 Relation to Other Systems**

### **AIM-OS Integration**

**CMC (Context Memory Core):**
- Tag persistence: PLIX tags stored in CMC atoms
- Intent-aware memory: Contracts stored as intent-aware entities
- Bitemporal support: `tx_time` and `valid_time` tracked

**VIF (Verifiable Intelligence Framework):**
- Intent verification: Contracts verified via VIF witnesses
- Confidence tracking: Intent confidence tracked via κ-gating
- Provenance: Intent execution provenance via VIF envelopes

**APOE (Atomic Provenance Orchestration Engine):**
- Intent achievement: PLIX contracts compile to APOE execution plans
- Plan execution: APOE executes plans with intent verification
- Saga patterns: Compensation logic via APOE saga support

**SEG (Shared Evidence Graph):**
- Intent lineage: Intent evolution tracked via SEG edges
- Evidence chains: Contract evidence requirements tracked via SEG
- Contradiction detection: Contract contradictions detected via SEG

**HHNI (Hierarchical Hypergraph Neural Index):**
- Tag resolution: PLIX tags resolved via HHNI semantic search
- Intent retrieval: Similar intents retrieved via HHNI
- Context awareness: Intent context enriched via HHNI

### **AIP Integration**

**AIP Graph Compilation:**
- PLIX contracts compile to AIP graph structures
- PLIX tags map to AIP nodes and edges
- PLIX constraints map to AIP validation rules

**AIP Route Resolution:**
- PLIX actions resolve to AIP routes
- PLIX capabilities resolve to AIP services
- PLIX evidence resolves to AIP witnesses

### **Influences**

**PL/I:**
- Language name inspiration (PL/I → PLIX)
- Structured programming concepts
- Formal language design

**Datomic:**
- Bitemporal model (`tx_time`, `valid_time`)
- Entity-attribute-value structure
- Immutable, append-only history

**RDF:**
- Tag-based identity (URIs/IRIs)
- Semantic web concepts
- Linked data principles

**Hoare Logic:**
- Contract semantics (pre/postconditions)
- Formal verification
- Design by Contract

---

## **1.4 Target Audience**

### **App Developers**
- Integrating apps with AIM-OS via AIP
- Expressing app intents in verifiable form
- Using PLIX contracts for app capabilities

### **Tool Builders**
- Creating PLIX parsers, compilers, validators
- Building PLIX tooling and IDE support
- Implementing PLIX execution engines

### **AI Agents**
- Expressing intent in verifiable, executable form
- Using PLIX for agent-to-agent communication
- Enabling AI consciousness via PLIX contracts

### **Language Designers**
- Extending PLIX via GGPs (Grammar Growth Proposals)
- Proposing new grammar constructs
- Evolving PLIX language capabilities

---

## **1.5 Versioning and Evolution Rules**

### **Versioning**

**Semantic Versioning:**
- **Major (X.0.0):** Breaking changes (require GGP approval)
- **Minor (0.X.0):** Additions (tracked via GGPs)
- **Patch (0.0.X):** Clarifications (documented in change log)

**Version Alignment:**
- PLIX language version and spec version align semantically
- PLIX v1.0 ↔ Spec v1.0
- Changes tracked via GGPs

### **Evolution Process**

**GGP (Grammar Growth Proposal) Process:**
1. Pattern mining from historical traces
2. GGP proposal creation with deprecation proof
3. Authority quorum approval
4. Grammar update

**See:** [Section 5: Evolution Framework](../PLIX_LANGUAGE_SPECIFICATION.md#section-5-layer-model-and-extensions) for details.

---

**Status:** ✅ **COMPLETE**  
**Next:** [Section 2: Core Concepts and Ontology](./02_core_concepts.md)

