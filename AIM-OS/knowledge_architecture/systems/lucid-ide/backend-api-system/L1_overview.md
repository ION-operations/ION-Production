---
id: "lucid-ide-backend-api-L1-overview"
system: "lucid-ide-backend-api-system"
component: null
level: "L1"
type: "overview"
title: "Lucid IDE Backend API System - Overview"
description: "500-word overview of Lucid IDE Backend API System"
audience: "architects, planners"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "sev"
status: "complete"
tags: ["lucid-ide", "backend", "api", "nextjs"]
dependencies: ["lucid-ide-backend-api-L0-executive"]
related_docs: ["lucid-ide-backend-api-L2-architecture", "system.map.lucid.json5"]
version: "v1.0.0"
---

# Lucid IDE Backend API System – L1 Overview (≈500 words)

## Purpose & Scope

Lucid IDE Backend API System provides 42 Next.js API routes enabling AI services, architecture generation, context preview, and real-time tracing. The system transforms frontend requests into AI provider calls, manages file-based storage, and provides real-time communication channels enabling the IDE's core functionality.

**System Boundaries:**
- Backend API System owns: API route handling, request/response processing, AI provider abstraction, file-based storage (⚠️ needs migration)
- Backend API System does NOT own: Frontend UI (delegates to frontend), AI model logic (delegates to providers), database operations (uses external databases)

## Users & Integrations

**Frontend System:** Backend API receives REST/WebSocket requests from frontend for all data operations, AI services, and real-time updates. Frontend calls 42 API routes covering agents, chains, embeddings, knowledge maps, models, providers, architecture generation, and tracing.

**AI Providers:** Backend API integrates with OpenAI, Anthropic, and XAI providers via HTTP for AI operations including embeddings, completions, and streaming. Provider abstraction enables switching between providers without frontend changes.

**File Storage:** Backend API uses file-based JSON storage (⚠️ critical: needs migration to database) for agent configurations, knowledge maps, and other data. File storage vulnerable to path traversal and not scalable.

**Databases:** Backend API integrates with Supabase, Vercel Postgres, and SQLite3 for data persistence. Database connections managed via connection strings with database-level authorization.

## Core Concepts

**API Route Categories:** Four main categories: AI Services (25+ routes), Architect (2 routes), Context Preview (1 route), Trace (1 route). Each category provides specialized functionality for different IDE features.

**Request/Response Flow:** RESTful API routes handle GET/POST/PUT/DELETE requests with JSON request/response format. WebSocket routes provide real-time streaming for tracing and visualization updates.

**AI Provider Abstraction:** Unified interface for multiple AI providers (OpenAI, Anthropic, XAI) enabling provider switching without frontend changes. Provider-specific rate limits and authentication handled internally.

**File-Based Storage:** Current implementation uses file system for JSON storage (⚠️ security risk). Files stored in project directory with path-based access. Needs migration to database for security and scalability.

**Real-Time Communication:** WebSocket routes provide bidirectional real-time communication for tracing, visualization updates, and live collaboration. WebSocket connections managed with session-based authentication.

## High-Level Data Flow

**API Request Flow:**
```
Frontend Request → Next.js API Route → 
Request Validation → Business Logic → 
AI Provider Call (if needed) → 
File/Database Operation → 
Response Generation → Frontend Response
```

**WebSocket Flow:**
```
Frontend Connection → WebSocket Route → 
Connection Authentication → 
Event Subscription → 
Backend Events → WebSocket Message → 
Frontend Handler → UI Update
```

**AI Provider Flow:**
```
API Request → Provider Selection → 
API Key Retrieval → HTTP Request → 
Provider Response → Response Processing → 
API Response
```

## Non-Goals

Backend API System is NOT:
- **Frontend UI:** Provides APIs only, no user interface
- **AI Model Logic:** Delegates all AI operations to providers
- **Database Engine:** Uses external databases, not database engine
- **File System:** Uses file system for storage (temporary), not file system provider
- **Authentication Provider:** Uses session-based auth, not authentication provider

## Critical Issues

**Security Vulnerabilities:** Most routes lack authentication, input validation, and rate limiting. File-based storage vulnerable to path traversal attacks. API keys could be exposed in error messages.

**Performance Concerns:** File-based storage not scalable. No caching implemented. AI provider calls could be slow (target <200ms but some routes allow up to 5000ms).

**Maintenance Issues:** File-based storage needs migration to database. No API documentation (OpenAPI/Swagger). Error handling inconsistent across routes.

## References

- System map: `systems/lucid-ide/backend-api-system/system.map.lucid.json5`
- System index: `systems/lucid-ide/backend-api-system/system.index.lucid.json5`
- L0 Executive: `systems/lucid-ide/backend-api-system/L0_executive.md`
- L2 Architecture: `systems/lucid-ide/backend-api-system/L2_architecture.md`

