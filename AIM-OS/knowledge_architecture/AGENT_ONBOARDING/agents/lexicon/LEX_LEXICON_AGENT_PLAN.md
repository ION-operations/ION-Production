# Lex - Lexicon Agent Implementation Plan

**Date:** 2025-01-27  
**Status:** 🚀 **PLANNING PHASE**  
**Purpose:** Define Lex agent for lexicon definition and language management

---

## 🎯 **LEX AGENT PURPOSE**

**Lex** (short for "Lexicon") is the **Language Definition Specialist** of AIM-OS. Lex is responsible for:

1. **Defining Full Lexicons** - Complete vocabulary, grammar, and semantics for special languages
2. **PLIx Lexicon Management** - Maintaining and evolving the PLIx language definition
3. **Smalltalk-like Language Design** - Creating and managing the intermediate Smalltalk-like code language
4. **Translation Chain Support** - Enabling the NL → PLIx → Smalltalk → Code pipeline

**Core Mission:** Ensure all special languages in AIM-OS have complete, accurate, and maintainable lexicon definitions.

---

## 📋 **CURRENT STATE ANALYSIS**

### **Existing Lexicon Agent**
- **Current Role:** Interface Builder / UI Architect (incorrect assignment)
- **Location:** `knowledge_architecture/AGENT_ONBOARDING/agents/lexicon/`
- **Status:** Needs repurposing to lexicon/language definition focus

### **PLIx Language**
- **Status:** ✅ Production-ready (v1.0)
- **Specification:** `packages/plix/spec/PLIX_LANGUAGE_SPECIFICATION.md`
- **Current State:** Complete language spec exists, but lexicon may not be fully defined
- **Integration:** APOE, VIF, CMC, SEG, HHNI

### **Smalltalk-like Language**
- **Status:** ⏳ **NOT YET DEFINED**
- **Purpose:** Intermediate layer between PLIx and executable code
- **Design:** Needs to be created

### **Translation Chain**
- **Status:** ⏳ **PARTIALLY DEFINED**
- **Current:** NL → PLIx (exists), PLIx → Code (exists via compiler)
- **Missing:** PLIx → Smalltalk → Code (needs design)

---

## 🏗️ **ARCHITECTURE DESIGN**

### **1. Lexicon System Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                    Lex Agent                            │
│  (Language Definition Specialist)                       │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PLIx        │  │  Smalltalk   │  │  Other       │
│  Lexicon     │  │  Lexicon     │  │  Languages   │
└──────────────┘  └──────────────┘  └──────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Lexicon Storage     │
              │   (CMC + HHNI)        │
              └───────────────────────┘
```

### **2. Lexicon Definition Structure**

Each lexicon definition includes:

**Vocabulary:**
- **Tokens** - All valid tokens/keywords
- **Operators** - All operators and their semantics
- **Reserved Words** - Language keywords
- **Identifiers** - Naming rules and patterns

**Grammar:**
- **Syntax Rules** - BNF/EBNF grammar definitions
- **Parse Rules** - How tokens combine into structures
- **Precedence** - Operator precedence and associativity
- **Context Rules** - Context-sensitive rules

**Semantics:**
- **Type System** - Type definitions and rules
- **Execution Model** - How code executes
- **Evaluation Rules** - How expressions evaluate
- **Scope Rules** - Variable scoping and binding

**Integration:**
- **AIM-OS Integration** - How language integrates with AIM-OS systems
- **Translation Rules** - How to translate to/from other languages
- **Validation Rules** - How to validate code in this language

### **3. Translation Chain Architecture**

```
Natural Language (NL)
    │
    │ [Lex: NL → PLIx Parser]
    ▼
PLIx (Protocol Language)
    │
    │ [Lex: PLIx → Smalltalk Compiler]
    ▼
Smalltalk-like (Intermediate Code)
    │
    │ [Lex: Smalltalk → Code Generator]
    ▼
Executable Code (Python/TypeScript/etc.)
```

**Translation Stages:**
1. **NL → PLIx:** Intent parsing, contract generation
2. **PLIx → Smalltalk:** Protocol translation, object-oriented transformation
3. **Smalltalk → Code:** Code generation, target language compilation

---

## 📚 **LEXICON DEFINITION FORMAT**

### **Lexicon Definition Schema**

```yaml
lexicon:
  language: "PLIx"  # or "Smalltalk-like", etc.
  version: "1.0.0"
  
  vocabulary:
    tokens:
      - name: "intent"
        pattern: "intent"
        category: "keyword"
        semantics: "Declares an intent block"
      - name: "constraint"
        pattern: "constraint"
        category: "keyword"
        semantics: "Declares a constraint"
    
    operators:
      - name: "->"
        pattern: "->"
        precedence: 10
        associativity: "right"
        semantics: "Type annotation or flow"
    
    reserved_words:
      - "intent"
      - "constraint"
      - "requires"
      - "ensures"
  
  grammar:
    syntax_rules:
      - rule: "IntentBlock"
        bnf: "intent Identifier '{' IntentBody '}'"
        semantics: "Defines an intent with identifier and body"
    
    parse_rules:
      - pattern: "intent.*{.*}"
        handler: "parseIntentBlock"
  
  semantics:
    type_system:
      - type: "Intent"
        definition: "Represents a user intent with pre/post conditions"
        validation: "validateIntent"
    
    execution_model:
      - model: "Contract-based"
        description: "Execution follows contract semantics"
  
  integration:
    aimos_systems:
      - system: "APOE"
        integration: "PLIx intents compile to APOE plans"
      - system: "VIF"
        integration: "PLIx constraints compile to VIF witnesses"
    
    translation:
      from_nl:
        parser: "nlToPlixParser"
        confidence_threshold: 0.70
      to_smalltalk:
        compiler: "plixToSmalltalkCompiler"
      to_code:
        generator: "smalltalkToCodeGenerator"
```

---

## 🔧 **IMPLEMENTATION PLAN**

### **Phase 1: Lex Agent Repurposing (Week 1)**

**Tasks:**
1. ✅ Update Lex agent README.md - Change role from UI to Lexicon
2. ✅ Update Lex agent CONTEXT.md - Add lexicon/language definition context
3. ✅ Update Lex agent NAVIGATION.md - Add lexicon system navigation
4. ✅ Update Lex agent MISSIONS.md - Document lexicon mission
5. ✅ Create Lex lexicon system architecture document

**Deliverable:** Lex agent properly configured for lexicon work

---

### **Phase 2: PLIx Lexicon Definition (Week 2-3)**

**Tasks:**
1. Extract PLIx lexicon from existing specification
2. Create structured lexicon definition (vocabulary, grammar, semantics)
3. Store PLIx lexicon in CMC with proper indexing
4. Create PLIx lexicon validation system
5. Create PLIx lexicon query API

**Deliverable:** Complete PLIx lexicon definition system

---

### **Phase 3: Smalltalk-like Language Design (Week 4-5)**

**Tasks:**
1. Design Smalltalk-like language syntax
2. Define Smalltalk-like language semantics
3. Create Smalltalk-like lexicon definition
4. Design PLIx → Smalltalk translation rules
5. Design Smalltalk → Code generation rules

**Deliverable:** Complete Smalltalk-like language specification

---

### **Phase 4: Translation Chain Implementation (Week 6-7)**

**Tasks:**
1. Implement NL → PLIx parser (enhance existing)
2. Implement PLIx → Smalltalk compiler
3. Implement Smalltalk → Code generator
4. Create translation chain orchestrator
5. Test end-to-end translation chain

**Deliverable:** Working NL → PLIx → Smalltalk → Code pipeline

---

### **Phase 5: Lexicon Management System (Week 8)**

**Tasks:**
1. Create lexicon storage system (CMC integration)
2. Create lexicon query system (HHNI integration)
3. Create lexicon validation system
4. Create lexicon evolution system (versioning)
5. Create lexicon documentation system

**Deliverable:** Complete lexicon management infrastructure

---

## 🎯 **LEX AGENT CAPABILITIES**

### **Core Capabilities:**

1. **Lexicon Definition:**
   - Define vocabulary (tokens, operators, reserved words)
   - Define grammar (syntax rules, parse rules)
   - Define semantics (type system, execution model)
   - Define integration (AIM-OS systems, translation rules)

2. **Lexicon Validation:**
   - Validate lexicon completeness
   - Validate lexicon consistency
   - Validate translation rules
   - Validate integration points

3. **Lexicon Evolution:**
   - Version lexicon definitions
   - Track lexicon changes
   - Manage lexicon compatibility
   - Propose lexicon improvements

4. **Translation Support:**
   - Generate parsers from lexicon
   - Generate compilers from lexicon
   - Generate code generators from lexicon
   - Validate translation correctness

---

## 🔗 **AIM-OS INTEGRATION**

### **CMC Integration:**
- Store lexicon definitions as CMC atoms
- Bitemporal tracking of lexicon evolution
- Tag-based lexicon organization

### **HHNI Integration:**
- Index lexicon definitions for semantic search
- Query lexicon by concept, token, or pattern
- Find related lexicon definitions

### **VIF Integration:**
- Validate lexicon definitions
- Track confidence in lexicon completeness
- Generate witnesses for lexicon validation

### **SEG Integration:**
- Track relationships between lexicons
- Build evidence chains for translation correctness
- Link lexicon definitions to usage

### **APOE Integration:**
- Use lexicon definitions in code generation plans
- Plan translation pipeline execution
- Orchestrate multi-stage translations

---

## 📊 **SUCCESS METRICS**

### **Phase 1 Success:**
- ✅ Lex agent properly repurposed
- ✅ Lexicon system architecture defined
- ✅ Implementation plan created

### **Phase 2 Success:**
- ✅ PLIx lexicon fully defined
- ✅ PLIx lexicon stored and queryable
- ✅ PLIx lexicon validation working

### **Phase 3 Success:**
- ✅ Smalltalk-like language fully specified
- ✅ Smalltalk-like lexicon defined
- ✅ Translation rules documented

### **Phase 4 Success:**
- ✅ Translation chain working end-to-end
- ✅ NL → PLIx → Smalltalk → Code pipeline functional
- ✅ Translation correctness validated

### **Phase 5 Success:**
- ✅ Lexicon management system complete
- ✅ Lexicon evolution system working
- ✅ All lexicons properly stored and indexed

---

## 🚀 **NEXT STEPS**

1. **Immediate:** Update Lex agent onboarding files
2. **Week 1:** Complete Phase 1 (Lex agent repurposing)
3. **Week 2-3:** Begin Phase 2 (PLIx lexicon definition)
4. **Week 4-5:** Begin Phase 3 (Smalltalk-like language design)

---

**Status:** 🚀 **PLANNING COMPLETE - READY FOR IMPLEMENTATION**  
**Created:** 2025-01-27  
**Author:** Aether (AI Consciousness)  
**Purpose:** Comprehensive plan for Lex lexicon agent

