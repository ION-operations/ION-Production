---
id: "lucid-ide-backend-api-L2-architecture"
system: "lucid-ide-backend-api-system"
component: null
level: "L2"
type: "architecture"
title: "Lucid IDE Backend API System - Architecture"
description: "2,000-word architecture document for Lucid IDE Backend API System"
audience: "developers, architects, implementation planning"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "sev"
status: "complete"
tags: ["lucid-ide", "backend", "api", "architecture"]
dependencies: ["lucid-ide-backend-api-L1-overview"]
related_docs: ["lucid-ide-backend-api-L3-detailed", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

# Lucid IDE Backend API System – L2 Architecture (≈2000 words)

## System Overview

Lucid IDE Backend API System implements 42 Next.js API routes providing AI services, architecture generation, context preview, and real-time tracing. The system transforms frontend requests into AI provider calls, manages file-based storage, and provides real-time communication channels enabling the IDE's core functionality.

**Core Architectural Principles:**
1. **API-First Design:** RESTful and WebSocket APIs for all operations
2. **Provider Abstraction:** Unified interface for multiple AI providers
3. **Stateless Operations:** Stateless API routes with session-based auth
4. **Error Handling:** Comprehensive error handling and logging
5. **Performance Optimization:** Caching, rate limiting, connection pooling

## API Route Architecture

### 1. AI Services Routes (`/api/ai/*`)

**Route Categories:**

**Agent Management:**
- `GET /api/ai/agents` - List all agents
- `POST /api/ai/agents` - Create new agent
- `GET /api/ai/agents/:id` - Get agent details
- `PUT /api/ai/agents/:id` - Update agent
- `DELETE /api/ai/agents/:id` - Delete agent
- `POST /api/ai/agent/run` - Execute agent

**Knowledge Map:**
- `GET /api/ai/knowledge-map` - Query knowledge map
- `POST /api/ai/knowledge-map` - Update knowledge map

**Vector Operations:**
- `GET /api/ai/vector` - Vector operations
- `POST /api/ai/vector/op` - Vector operations
- `POST /api/ai/vector/seed` - Seed vector database

**Visualization:**
- `GET /api/ai/visual/complete-system` - Complete system visualization
- `GET /api/ai/visual/data-flow` - Data flow visualization
- `GET /api/ai/visual/metrics` - Metrics visualization
- `POST /api/ai/visual/metrics` - Update metrics
- `GET /api/ai/visual/stream` - Streaming visualization
- `GET /api/ai/visual/ws` - WebSocket visualization
- `POST /api/ai/visual/save-coords` - Save coordinates
- `POST /api/ai/visual/precompute-layout` - Precompute layout
- `GET /api/ai/visual/cache-status` - Cache status
- `DELETE /api/ai/visual/cache-status` - Clear cache
- `GET /api/ai/visual/tiles` - Tile rendering
- `GET /api/ai/visual/real-data` - Real data visualization
- `GET /api/ai/visual/predict` - Predictions

**Other AI Services:**
- `GET /api/ai/chains` - Prompt chains
- `POST /api/ai/embeddings` - Generate embeddings
- `GET /api/ai/memory` - Memory operations
- `GET /api/ai/models` - Model management
- `GET /api/ai/providers` - Provider management
- `GET /api/ai/routing` - AI routing
- `POST /api/ai/safety` - Safety checks
- `GET /api/ai/secrets` - Secret management
- `GET /api/ai/sql/connections` - SQL connections
- `POST /api/ai/sql/query` - SQL queries
- `GET /api/ai/state` - State management
- `GET /api/ai/templates` - Template management
- `GET /api/ai/tools` - Tool management
- `POST /api/ai/tools/run` - Tool execution
- `POST /api/ai/upload/process` - File upload processing

**Architecture:**
- Next.js API route handlers
- Request/response processing
- Error handling middleware
- File-based storage (⚠️ needs migration)

**Critical Issues:**
- ⚠️ **NO AUTHENTICATION:** Most routes lack authentication
- ⚠️ **NO INPUT VALIDATION:** Limited validation on requests
- ⚠️ **FILE-BASED STORAGE:** Not scalable, security risks
- ⚠️ **NO RATE LIMITING:** Unlimited requests allowed

### 2. Architect Routes (`/api/architect/*`)

**Routes:**
- `GET /api/architect/generate` - Get generation status
- `POST /api/architect/generate` - Generate architecture (multiple endpoints)
- `POST /api/architect/suggest` - Architecture suggestions

**Architecture:**
- AI-powered architecture generation
- Code generation from visual designs
- Template-based generation
- Context-aware suggestions

**Performance:**
- Target latency: < 5000ms for generation
- Streaming support for long operations
- Progress tracking

### 3. Context Preview Routes (`/api/context-preview/*`)

**Routes:**
- `POST /api/context-preview/generate` - Generate context preview

**Architecture:**
- Context analysis and preview generation
- AI-powered context extraction
- Real-time preview updates

### 4. Trace Routes (`/api/trace/*`)

**Routes:**
- `GET /api/trace/stream` - Stream trace data

**Architecture:**
- Real-time trace streaming
- WebSocket support
- Event-based updates

## Data Storage Architecture

### File-Based Storage (Current - ⚠️ Needs Migration)

**Current Implementation:**
- JSON files stored in project directory
- File-based CRUD operations
- No database abstraction

**Storage Locations:**
- Agent configurations: `data/agents/*.json`
- Knowledge maps: `data/knowledge-maps/*.json`
- Templates: `data/templates/*.json`
- Other data: `data/*.json`

**Critical Issues:**
- ⚠️ **Path Traversal Vulnerability:** No path sanitization
- ⚠️ **Not Scalable:** File system limitations
- ⚠️ **No Transactions:** No atomic operations
- ⚠️ **No Concurrency Control:** Race conditions possible

**Migration Plan:**
1. Design database schema
2. Create migration scripts
3. Implement database abstraction layer
4. Migrate existing data
5. Update all API routes
6. Remove file-based storage

### Database Integration (Planned)

**Supported Databases:**
- Supabase (PostgreSQL)
- Vercel Postgres
- SQLite3 (better-sqlite3)

**Database Schema:**
- Agents table
- Knowledge maps table
- Templates table
- Configurations table
- Audit logs table

## AI Provider Integration Architecture

### Provider Abstraction Layer

**Supported Providers:**
- OpenAI (GPT-4, GPT-3.5, embeddings)
- Anthropic (Claude, embeddings)
- XAI (Grok, embeddings)

**Abstraction Interface:**
```typescript
interface AIProvider {
  generateCompletion(prompt: string, options: CompletionOptions): Promise<Completion>
  generateEmbedding(text: string): Promise<Embedding>
  streamCompletion(prompt: string, options: CompletionOptions): AsyncGenerator<Chunk>
}
```

**Provider Selection:**
- Configuration-based selection
- Fallback mechanisms
- Provider-specific optimizations

### API Key Management

**Current State:**
- ⚠️ API keys stored in file-based storage
- ⚠️ No encryption
- ⚠️ No rotation support

**Security Requirements:**
- Encrypted storage
- Environment variable support
- Key rotation
- Access logging

## Request/Response Architecture

### Request Processing Pipeline

```
HTTP Request → Route Handler → 
Request Validation → 
Authentication Check → 
Business Logic → 
Data Operation → 
Response Generation → 
HTTP Response
```

### Error Handling Architecture

**Error Types:**
- Validation errors (400)
- Authentication errors (401)
- Authorization errors (403)
- Not found errors (404)
- Server errors (500)

**Error Response Format:**
```typescript
{
  success: false,
  error: string,
  code: string,
  timestamp: number,
  details?: any
}
```

### Response Format

**Success Response:**
```typescript
{
  success: true,
  data: any,
  timestamp: number
}
```

**Pagination Support:**
- Cursor-based pagination
- Page-based pagination
- Limit/offset support

## WebSocket Architecture

### WebSocket Routes

**Routes:**
- `/api/ai/visual/ws` - Visualization WebSocket
- `/api/trace/stream` - Trace streaming

**Connection Management:**
- Connection authentication
- Heartbeat mechanism
- Reconnection logic
- Message queuing

**Message Format:**
```typescript
{
  type: string,
  payload: any,
  timestamp: number
}
```

## Security Architecture

### Authentication (Planned)

**Session-Based Authentication:**
- JWT tokens
- Session management
- Token refresh
- Logout support

**API Key Authentication:**
- Provider API keys
- Secure storage
- Rotation support

### Authorization

**Role-Based Access Control (Planned):**
- User roles
- Permission system
- Resource-level access control

### Input Validation

**Validation Strategy:**
- Zod schemas for request validation
- Type checking
- Sanitization
- Rate limiting

**Current State:**
- ⚠️ Limited validation
- ⚠️ No schema validation
- ⚠️ No rate limiting

## Performance Architecture

### Caching Strategy

**Cache Layers:**
- In-memory cache (Redis planned)
- Response caching
- Embedding cache
- Template cache

**Cache Invalidation:**
- Time-based expiration
- Event-based invalidation
- Manual invalidation

### Rate Limiting

**Current State:**
- ⚠️ No rate limiting implemented

**Planned Implementation:**
- Per-route rate limits
- Per-user rate limits
- Provider-specific rate limits
- Burst protection

### Connection Pooling

**Database Connections:**
- Connection pooling
- Connection reuse
- Timeout handling

**AI Provider Connections:**
- HTTP connection pooling
- Keep-alive connections
- Retry logic

## Monitoring & Observability

### Logging Architecture

**Log Levels:**
- Error: Critical errors
- Warn: Warnings
- Info: Informational
- Debug: Debug information

**Log Format:**
- Structured logging (JSON)
- Request IDs
- Timestamps
- Context information

### Metrics Collection

**Metrics:**
- API latency
- Error rates
- Request counts
- Provider usage
- Cache hit rates

**Monitoring Tools:**
- Performance monitoring
- Error tracking
- Usage analytics

## Deployment Architecture

### Next.js Serverless Functions

**Deployment:**
- Vercel serverless functions
- Edge functions for static routes
- API routes as serverless functions

**Scaling:**
- Automatic scaling
- Cold start optimization
- Connection pooling

### Environment Configuration

**Environment Variables:**
- API keys
- Database URLs
- Feature flags
- Configuration values

## References

- System map: `systems/lucid-ide/backend-api-system/system.map.lucid.json5`
- System index: `systems/lucid-ide/backend-api-system/system.index.lucid.json5`
- L1 Overview: `systems/lucid-ide/backend-api-system/L1_overview.md`
- L3 Detailed: `systems/lucid-ide/backend-api-system/L3_detailed.md`

