---
id: "lucid-ide-knowledge-map-L2-architecture"
system: "lucid-ide-knowledge-map-system"
component: null
level: "L2"
type: "architecture"
title: "Lucid IDE Knowledge Map System - Architecture"
description: "2,000-word architecture document for Lucid IDE Knowledge Map System"
audience: "developers, architects, implementation planning"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "sev"
status: "complete"
tags: ["lucid-ide", "knowledge-map", "architecture"]
dependencies: ["lucid-ide-knowledge-map-L1-overview"]
related_docs: ["lucid-ide-knowledge-map-L3-detailed", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

# Lucid IDE Knowledge Map System – L2 Architecture (≈2000 words)

## System Overview

Lucid IDE Knowledge Map System implements vector database and semantic relationship mapping with knowledge map visualization, component analysis, and AI-powered context retrieval. The system transforms codebase into semantic knowledge graph enabling understanding of relationships, dependencies, and context.

**Core Architectural Principles:**
1. **Vector-First:** Vector embeddings for semantic search
2. **Relationship Mapping:** Semantic relationship identification
3. **3D Visualization:** Interactive 3D knowledge graph
4. **AI-Powered:** AI providers for embeddings
5. **Real-Time Updates:** Live knowledge map updates

## API Architecture

### Knowledge Map API Route (`app/api/ai/knowledge-map/route.ts`)

**Purpose:** Knowledge map API route providing GET/POST endpoints

**Architecture:**
- GET endpoint for querying knowledge map
- POST endpoint for knowledge map operations
- Query filtering support
- Component info retrieval
- Related component discovery

**GET Endpoint:**
- Query parameter filtering
- Force refresh support
- Filtered data response
- Full context response

**POST Endpoint:**
- Component info retrieval
- Related component discovery
- Relationship queries
- Knowledge map updates

**Query Filtering:**
- Component analysis queries
- System health queries
- Dependency chain queries
- Recommendation queries

## Integration Architecture

### AIKnowledgeMapIntegration (`lib/ai-knowledge-map-integration.ts`)

**Purpose:** Singleton service managing knowledge map data and operations

**Architecture:**
- Singleton pattern
- Knowledge map data management
- Component analysis
- Relationship mapping
- Backend API integration

**Key Operations:**
- `getInstance()` - Get singleton instance
- `getKnowledgeMapData()` - Get knowledge map data
- `getAIKnowledgeMapContext()` - Get AI context
- `getComponentInfo()` - Get component information
- `getRelatedComponents()` - Get related components

**Data Management:**
- Knowledge map caching
- Component data storage
- Relationship storage
- Analysis results storage

## Visualization Architecture

### Knowledge Map Panel (`components/ai-studio/KnowledgeMapPanel.tsx`)

**Purpose:** 3D knowledge map visualization UI

**Architecture:**
- Three.js 3D scene
- Spherical flow physics
- Predictive flow models
- RL-GODN agents
- Interactive controls

**Key Features:**
- 3D knowledge graph
- Node/edge interaction
- Query interface
- Real-time updates
- Multiple visualization modes

**Critical Issues:**
- ⚠️ **EXTREMELY LARGE:** 3700+ lines ⚠️ CRITICAL
- ⚠️ Needs urgent refactoring

**Refactoring Recommendations:**
1. Extract Three.js scene component
2. Extract physics engine
3. Extract controls component
4. Extract query interface
5. Code splitting

## Vector Database Architecture

### Vector Operations

**Operations:**
- Embedding storage
- Similarity search
- Vector indexing
- Relationship mapping

**Storage:**
- Vector database (external)
- Embedding cache
- Index storage
- Metadata storage

### Embedding Generation

**Generation Process:**
1. Component extraction
2. Text preprocessing
3. AI provider call
4. Embedding generation
5. Vector storage

**AI Provider Integration:**
- OpenAI embeddings
- Anthropic embeddings
- XAI embeddings
- Fallback mechanisms

## Relationship Mapping Architecture

### Relationship Types

**Semantic Relationships:**
- Similarity relationships
- Sequence relationships
- Chain relationships
- Tool relationships
- Policy relationships
- Route relationships
- SQL relationships

**Relationship Detection:**
- Vector similarity
- Pattern matching
- Dependency analysis
- Code analysis

### Relationship Visualization

**Visualization:**
- 3D graph rendering
- Edge rendering
- Relationship strength
- Relationship types

## Query Architecture

### Query Types

**Query Categories:**
- Component queries
- Health queries
- Dependency queries
- Recommendation queries
- Full context queries

### Query Processing

**Processing Pipeline:**
```
User Query → Query Parsing → 
Filter Selection → Vector Search → 
Similarity Matching → Component Retrieval → 
Relationship Analysis → Response Generation
```

## Performance Architecture

### Vector Search Performance

**Optimization Strategies:**
- Vector indexing
- Caching
- Batch operations
- Parallel processing

**Target Metrics:**
- Search time: <200ms
- Embedding generation: <1000ms
- API latency: <200ms

### Visualization Performance

**Optimization Strategies:**
- WebGL optimization
- Node culling
- Edge culling
- LOD system

**Target Metrics:**
- FPS: 60fps
- Render time: <16ms
- Memory: <500MB

## Security Architecture

### API Key Security

**Security Measures:**
- Secure storage
- Never log keys
- Encrypted transmission
- Rotation support

### Data Protection

**Protection Measures:**
- Embedding encryption
- Access controls
- Audit logging
- Data sanitization

## References

- System map: `systems/lucid-ide/knowledge-map-system/system.map.lucid.json5`
- System index: `systems/lucid-ide/knowledge-map-system/system.index.lucid.json5`
- L1 Overview: `systems/lucid-ide/knowledge-map-system/L1_overview.md`
- L3 Detailed: `systems/lucid-ide/knowledge-map-system/knowledge-map-system/L3_detailed.md`

