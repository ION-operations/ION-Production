# Part II: Architecture - L1 Overview

**Part:** II - Architecture  
**Level:** L1 (Overview)  
**Word Count:** 500 words (exact)  
**Purpose:** Comprehensive overview of Part II architecture

---

## Introduction

Part II defines PLIx architecture through four pillars, CNL grammar, formal validation, and compiler design. This architecture enables intent-aware systems with verifiable correctness, durable execution, and complete provenance.

## Chapter Overview

**Chapter 5: The Four Pillars** establishes architectural foundation: Contract Layer (intent specification via CNL and formal validation), Execution Layer (durable execution with Saga pattern), Safety Layer (confidence gates and policy-as-code), and Evidence Layer (provenance and lineage). These pillars work together to enable intent-aware systems.

**Chapter 6: CNL Grammar** defines Controlled Natural Language design—Gherkin-style grammar enabling unambiguous intent expression. SmaCoNat methodology provides minimal keywords with clear mapping. Grammar specification (EBNF) enables parser implementation, transforming CNL to PLIx AST.

**Chapter 7: Formal Validation** integrates Alloy and TLA+ for invariant verification. Layer-1 guards provide runtime invariants, Layer-2 validators provide compile-time invariants. Formal validation ensures intent correctness independent of implementation.

**Chapter 8: Compiler Architecture** transforms PLIx contracts through IR (Intermediate Representation) to execution plans. Lowering process converts PLIx to IR, preserving semantics and execution metadata. Target compilation generates Temporal, Step Functions, or Argo workflows. APOE integration enables intent-aware orchestration.

## Key Concepts

Four pillars provide architectural foundation: Contract (intent), Execution (durability), Safety (gates), Evidence (provenance). CNL grammar enables unambiguous intent expression. Formal validation ensures invariant correctness. Compiler transforms intent to execution plans through IR, integrating with APOE for orchestration.

## Part II Impact

Part II provides complete architectural blueprint for PLIx systems. Architecture enables intent-aware systems with formal validation, durable execution, safety gates, and complete provenance. This architecture bridges intent expression to execution, enabling systems that understand their own purpose.

---

**Word Count:** 500 words (exact)

