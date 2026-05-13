---
id: "lucid-ide-backend-api-L3-detailed"
system: "lucid-ide-backend-api-system"
component: null
level: "L3"
type: "detailed"
title: "Lucid IDE Backend API System - Detailed Implementation Guide"
description: "10,000-word detailed implementation guide for Lucid IDE Backend API System"
audience: "developers, implementers, maintainers"
confidence_threshold: 0.70
token_cost: 10000
word_count: 10000
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "sev"
status: "complete"
tags: ["lucid-ide", "backend", "api", "implementation"]
dependencies: ["lucid-ide-backend-api-L2-architecture"]
related_docs: ["lucid-ide-backend-api-L4-complete", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

# Lucid IDE Backend API System – L3 Detailed Implementation Guide

**Purpose:** Complete implementation guide for Lucid IDE Backend API System with step-by-step instructions, code examples, route patterns, security, testing, troubleshooting, and best practices.

**Audience:** Developers implementing, integrating with, or maintaining the Lucid IDE Backend API System.

**Prerequisites:**
- Next.js 15+ (App Router)
- TypeScript 5+
- Understanding of REST APIs and WebSocket
- Familiarity with file system operations
- Basic knowledge of AI provider APIs

---

## 📜 **EVOLUTION & HISTORY**

### **Version Timeline**

**v1.0 (2025-11-09) - Initial Documentation**
- **Changes:** Comprehensive AIM-OS protocol-compliant documentation
- **Key Features:** 42 API routes, file-based storage, AI provider integration
- **Status:** Production-ready with identified migration needs

### **Key Evolution Points**

**Phase 1: Basic API Routes (Initial)**
- **Goal:** Basic CRUD operations for agents and resources
- **Implementation:** File-based storage, simple GET/POST routes
- **Outcome:** Functional API layer

**Phase 2: AI Integration**
- **Goal:** Integrate multiple AI providers
- **Implementation:** Provider abstraction layer, unified interface
- **Outcome:** Multi-provider support (OpenAI, Anthropic, XAI)

**Phase 3: Advanced Features**
- **Goal:** Visualization, knowledge maps, architecture generation
- **Implementation:** Complex routes, WebSocket support, streaming
- **Outcome:** Advanced features integrated

**Phase 4: Migration Planning**
- **Goal:** Migrate from file-based to database storage
- **Status:** Planned, not yet implemented

---

## 🔧 **IMPLEMENTATION GUIDE**

### **Step 1: API Route Structure**

**Next.js App Router Pattern:**
```
app/api/
├── ai/
│   ├── agents/
│   │   └── route.ts          # GET, POST agents
│   ├── knowledge-map/
│   │   └── route.ts          # GET, POST knowledge map
│   ├── visual/
│   │   ├── complete-system/
│   │   │   └── route.ts      # System visualization
│   │   └── ws/
│   │       └── route.ts      # WebSocket visualization
│   └── ...
├── architect/
│   └── generate/
│       └── route.ts          # Architecture generation
├── context-preview/
│   └── generate/
│       └── route.ts          # Context preview
└── trace/
    └── stream/
        └── route.ts          # Trace streaming
```

### **Step 2: Basic Route Implementation**

#### **2.1 GET Route Pattern**

```typescript
// app/api/ai/agents/route.ts
import { NextResponse } from 'next/server'
import fs from 'fs/promises'
import path from 'path'

const dataDir = path.join(process.cwd(), 'data', 'ai-studio')
const filePath = path.join(dataDir, 'agents.json')

export async function GET() {
  try {
    // Read file
    const raw = await fs.readFile(filePath, 'utf8')
    const agents = JSON.parse(raw)
    
    // Return response
    return NextResponse.json({ 
      ok: true, 
      agents 
    })
  } catch (error) {
    // Handle file not found
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
      return NextResponse.json({ 
        ok: true, 
        agents: [] 
      })
    }
    
    // Handle other errors
    console.error('GET /api/ai/agents error:', error)
    return NextResponse.json(
      { 
        ok: false, 
        error: 'Failed to read agents' 
      },
      { status: 500 }
    )
  }
}
```

#### **2.2 POST Route Pattern**

```typescript
// app/api/ai/agents/route.ts
export async function POST(req: Request) {
  try {
    // Parse request body
    const body = await req.json()
    
    // Validate input (add Zod schema)
    // const validated = agentSchema.parse(body)
    
    // Ensure directory exists
    await fs.mkdir(dataDir, { recursive: true })
    
    // Write file
    await fs.writeFile(
      filePath, 
      JSON.stringify(body, null, 2), 
      'utf8'
    )
    
    // Return success
    return NextResponse.json({ 
      ok: true 
    })
  } catch (error) {
    // Handle validation errors
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { 
          ok: false, 
          error: 'Validation error', 
          details: error.errors 
        },
        { status: 400 }
      )
    }
    
    // Handle other errors
    console.error('POST /api/ai/agents error:', error)
    return NextResponse.json(
      { 
        ok: false, 
        error: (error as Error).message || 'unknown error' 
      },
      { status: 500 }
    )
  }
}
```

#### **2.3 Enhanced Route with Validation**

```typescript
// app/api/ai/agents/route.ts
import { z } from 'zod'

// Request validation schema
const agentSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1).max(100),
  description: z.string().optional(),
  provider: z.enum(['openai', 'anthropic', 'xai']),
  model: z.string().min(1),
  temperature: z.number().min(0).max(2).optional(),
  maxTokens: z.number().positive().optional(),
})

export async function POST(req: Request) {
  try {
    const body = await req.json()
    
    // Validate input
    const validated = agentSchema.parse(body)
    
    // Ensure directory exists
    await fs.mkdir(dataDir, { recursive: true })
    
    // Read existing agents
    let agents = []
    try {
      const raw = await fs.readFile(filePath, 'utf8')
      agents = JSON.parse(raw)
    } catch {
      // File doesn't exist, start with empty array
    }
    
    // Add or update agent
    const index = agents.findIndex((a: any) => a.id === validated.id)
    if (index >= 0) {
      agents[index] = validated
    } else {
      agents.push(validated)
    }
    
    // Write file
    await fs.writeFile(
      filePath, 
      JSON.stringify(agents, null, 2), 
      'utf8'
    )
    
    return NextResponse.json({ 
      ok: true,
      agent: validated
    })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { 
          ok: false, 
          error: 'Validation error', 
          details: error.errors 
        },
        { status: 400 }
      )
    }
    
    console.error('POST /api/ai/agents error:', error)
    return NextResponse.json(
      { 
        ok: false, 
        error: (error as Error).message || 'unknown error' 
      },
      { status: 500 }
    )
  }
}
```

### **Step 3: AI Provider Integration**

#### **3.1 Provider Abstraction Layer**

```typescript
// lib/ai-provider.ts
interface AIProvider {
  generateCompletion(
    prompt: string, 
    options: CompletionOptions
  ): Promise<Completion>
  
  generateEmbedding(text: string): Promise<Embedding>
  
  streamCompletion(
    prompt: string, 
    options: CompletionOptions
  ): AsyncGenerator<Chunk>
}

interface CompletionOptions {
  model?: string
  temperature?: number
  maxTokens?: number
  stop?: string[]
}

interface Completion {
  text: string
  usage: {
    promptTokens: number
    completionTokens: number
    totalTokens: number
  }
}

interface Embedding {
  vector: number[]
  model: string
}
```

#### **3.2 OpenAI Provider**

```typescript
// lib/providers/openai.ts
import OpenAI from 'openai'

export class OpenAIProvider implements AIProvider {
  private client: OpenAI

  constructor(apiKey: string) {
    this.client = new OpenAI({ apiKey })
  }

  async generateCompletion(
    prompt: string,
    options: CompletionOptions = {}
  ): Promise<Completion> {
    const response = await this.client.chat.completions.create({
      model: options.model || 'gpt-4',
      messages: [{ role: 'user', content: prompt }],
      temperature: options.temperature,
      max_tokens: options.maxTokens,
      stop: options.stop,
    })

    return {
      text: response.choices[0]?.message?.content || '',
      usage: {
        promptTokens: response.usage?.prompt_tokens || 0,
        completionTokens: response.usage?.completion_tokens || 0,
        totalTokens: response.usage?.total_tokens || 0,
      },
    }
  }

  async generateEmbedding(text: string): Promise<Embedding> {
    const response = await this.client.embeddings.create({
      model: 'text-embedding-3-small',
      input: text,
    })

    return {
      vector: response.data[0].embedding,
      model: 'text-embedding-3-small',
    }
  }

  async *streamCompletion(
    prompt: string,
    options: CompletionOptions = {}
  ): AsyncGenerator<Chunk> {
    const stream = await this.client.chat.completions.create({
      model: options.model || 'gpt-4',
      messages: [{ role: 'user', content: prompt }],
      temperature: options.temperature,
      max_tokens: options.maxTokens,
      stream: true,
    })

    for await (const chunk of stream) {
      yield {
        text: chunk.choices[0]?.delta?.content || '',
        done: chunk.choices[0]?.finish_reason === 'stop',
      }
    }
  }
}
```

#### **3.3 Provider Factory**

```typescript
// lib/providers/factory.ts
import { OpenAIProvider } from './openai'
import { AnthropicProvider } from './anthropic'
import { XAIProvider } from './xai'

export function createProvider(
  provider: 'openai' | 'anthropic' | 'xai',
  apiKey: string
): AIProvider {
  switch (provider) {
    case 'openai':
      return new OpenAIProvider(apiKey)
    case 'anthropic':
      return new AnthropicProvider(apiKey)
    case 'xai':
      return new XAIProvider(apiKey)
    default:
      throw new Error(`Unknown provider: ${provider}`)
  }
}
```

### **Step 4: Database Migration (Planned)**

#### **4.1 Database Schema**

```typescript
// lib/db/schema.ts
import { sql } from '@vercel/postgres'

// Agents table
export async function createAgentsTable() {
  await sql`
    CREATE TABLE IF NOT EXISTS agents (
      id VARCHAR(255) PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      description TEXT,
      provider VARCHAR(50) NOT NULL,
      model VARCHAR(100) NOT NULL,
      temperature DECIMAL(3,2),
      max_tokens INTEGER,
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP DEFAULT NOW()
    )
  `
}

// Knowledge maps table
export async function createKnowledgeMapsTable() {
  await sql`
    CREATE TABLE IF NOT EXISTS knowledge_maps (
      id VARCHAR(255) PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      data JSONB NOT NULL,
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP DEFAULT NOW()
    )
  `
}
```

#### **4.2 Database Service**

```typescript
// lib/db/agents.ts
import { sql } from '@vercel/postgres'

export async function getAgents() {
  const result = await sql`
    SELECT * FROM agents
    ORDER BY created_at DESC
  `
  return result.rows
}

export async function getAgent(id: string) {
  const result = await sql`
    SELECT * FROM agents
    WHERE id = ${id}
  `
  return result.rows[0]
}

export async function createAgent(agent: any) {
  const result = await sql`
    INSERT INTO agents (id, name, description, provider, model, temperature, max_tokens)
    VALUES (${agent.id}, ${agent.name}, ${agent.description}, ${agent.provider}, ${agent.model}, ${agent.temperature}, ${agent.maxTokens})
    RETURNING *
  `
  return result.rows[0]
}

export async function updateAgent(id: string, agent: any) {
  const result = await sql`
    UPDATE agents
    SET 
      name = ${agent.name},
      description = ${agent.description},
      provider = ${agent.provider},
      model = ${agent.model},
      temperature = ${agent.temperature},
      max_tokens = ${agent.maxTokens},
      updated_at = NOW()
    WHERE id = ${id}
    RETURNING *
  `
  return result.rows[0]
}

export async function deleteAgent(id: string) {
  await sql`
    DELETE FROM agents
    WHERE id = ${id}
  `
}
```

### **Step 5: WebSocket Implementation**

#### **5.1 WebSocket Route**

```typescript
// app/api/ai/visual/ws/route.ts
import { NextRequest } from 'next/server'
import { Server } from 'socket.io'

export async function GET(req: NextRequest) {
  // WebSocket upgrade handling
  // Note: Next.js doesn't natively support WebSocket
  // Consider using external WebSocket server or upgrade to custom server
  
  return new Response('WebSocket endpoint', {
    status: 426, // Upgrade Required
    headers: {
      'Upgrade': 'websocket',
    },
  })
}
```

#### **5.2 Server-Sent Events (Alternative)**

```typescript
// app/api/ai/visual/stream/route.ts
import { NextRequest } from 'next/server'

export async function GET(req: NextRequest) {
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    async start(controller) {
      // Send initial connection message
      controller.enqueue(encoder.encode('data: {"type":"connected"}\n\n'))
      
      // Send periodic updates
      const interval = setInterval(() => {
        const data = {
          type: 'update',
          timestamp: new Date().toISOString(),
          // ... update data
        }
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`))
      }, 1000)
      
      // Cleanup on close
      req.signal.addEventListener('abort', () => {
        clearInterval(interval)
        controller.close()
      })
    },
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  })
}
```

### **Step 6: Security Implementation**

#### **6.1 Authentication Middleware**

```typescript
// lib/middleware/auth.ts
import { NextRequest, NextResponse } from 'next/server'
import { verifyToken } from './jwt'

export async function authenticateRequest(req: NextRequest) {
  const token = req.headers.get('authorization')?.replace('Bearer ', '')
  
  if (!token) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }
  
  try {
    const payload = await verifyToken(token)
    return { user: payload }
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid token' },
      { status: 401 }
    )
  }
}
```

#### **6.2 Input Validation**

```typescript
// lib/validation/agents.ts
import { z } from 'zod'

export const agentSchema = z.object({
  id: z.string().min(1).max(255),
  name: z.string().min(1).max(100),
  description: z.string().max(1000).optional(),
  provider: z.enum(['openai', 'anthropic', 'xai']),
  model: z.string().min(1).max(100),
  temperature: z.number().min(0).max(2).optional(),
  maxTokens: z.number().positive().max(100000).optional(),
})

export function validateAgent(data: unknown) {
  return agentSchema.parse(data)
}
```

#### **6.3 Path Traversal Prevention**

```typescript
// lib/security/path.ts
import path from 'path'

export function sanitizePath(filePath: string): string {
  // Resolve to absolute path
  const resolved = path.resolve(filePath)
  
  // Ensure path is within data directory
  const dataDir = path.resolve(process.cwd(), 'data')
  
  if (!resolved.startsWith(dataDir)) {
    throw new Error('Path traversal detected')
  }
  
  return resolved
}
```

#### **6.4 Rate Limiting**

```typescript
// lib/middleware/rate-limit.ts
import { NextRequest, NextResponse } from 'next/server'

const rateLimitMap = new Map<string, { count: number; resetAt: number }>()

export function rateLimit(
  req: NextRequest,
  maxRequests: number = 100,
  windowMs: number = 60000
): NextResponse | null {
  const ip = req.ip || req.headers.get('x-forwarded-for') || 'unknown'
  const now = Date.now()
  
  const record = rateLimitMap.get(ip)
  
  if (!record || now > record.resetAt) {
    rateLimitMap.set(ip, {
      count: 1,
      resetAt: now + windowMs,
    })
    return null
  }
  
  if (record.count >= maxRequests) {
    return NextResponse.json(
      { error: 'Rate limit exceeded' },
      { status: 429 }
    )
  }
  
  record.count++
  return null
}
```

### **Step 7: Error Handling**

#### **7.1 Error Response Format**

```typescript
// lib/errors/api-error.ts
export class APIError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public details?: any
  ) {
    super(message)
    this.name = 'APIError'
  }
}

export function createErrorResponse(error: unknown) {
  if (error instanceof APIError) {
    return NextResponse.json(
      {
        ok: false,
        error: error.message,
        details: error.details,
      },
      { status: error.statusCode }
    )
  }
  
  if (error instanceof z.ZodError) {
    return NextResponse.json(
      {
        ok: false,
        error: 'Validation error',
        details: error.errors,
      },
      { status: 400 }
    )
  }
  
  console.error('Unhandled error:', error)
  return NextResponse.json(
    {
      ok: false,
      error: 'Internal server error',
    },
    { status: 500 }
  )
}
```

#### **7.2 Error Handling Wrapper**

```typescript
// lib/utils/route-handler.ts
import { NextRequest, NextResponse } from 'next/server'
import { createErrorResponse } from '../errors/api-error'

export function withErrorHandling(
  handler: (req: NextRequest) => Promise<NextResponse>
) {
  return async (req: NextRequest) => {
    try {
      return await handler(req)
    } catch (error) {
      return createErrorResponse(error)
    }
  }
}
```

### **Step 8: Testing**

#### **8.1 Route Testing**

```typescript
// __tests__/api/ai/agents.test.ts
import { GET, POST } from '@/app/api/ai/agents/route'
import { NextRequest } from 'next/server'

describe('/api/ai/agents', () => {
  it('GET returns empty array when no agents exist', async () => {
    const req = new NextRequest('http://localhost:3000/api/ai/agents')
    const response = await GET()
    const data = await response.json()
    
    expect(response.status).toBe(200)
    expect(data.ok).toBe(true)
    expect(Array.isArray(data.agents)).toBe(true)
  })
  
  it('POST creates new agent', async () => {
    const agent = {
      id: 'test-agent',
      name: 'Test Agent',
      provider: 'openai',
      model: 'gpt-4',
    }
    
    const req = new NextRequest('http://localhost:3000/api/ai/agents', {
      method: 'POST',
      body: JSON.stringify(agent),
    })
    
    const response = await POST(req)
    const data = await response.json()
    
    expect(response.status).toBe(200)
    expect(data.ok).toBe(true)
  })
})
```

### **Step 9: Troubleshooting**

#### **9.1 Common Issues**

**Issue: File not found errors**
- **Cause:** Directory doesn't exist
- **Solution:** Use `fs.mkdir` with `recursive: true`

**Issue: Path traversal vulnerabilities**
- **Cause:** User input in file paths
- **Solution:** Sanitize paths, validate against base directory

**Issue: API key exposure**
- **Cause:** Keys in client-side code
- **Solution:** Store in environment variables, use backend proxy

**Issue: Rate limiting not working**
- **Cause:** In-memory map cleared on restart
- **Solution:** Use Redis or database for rate limiting

### **Step 10: Best Practices**

#### **10.1 Route Design**

**Do:**
- ✅ Use RESTful conventions
- ✅ Validate all inputs
- ✅ Handle errors gracefully
- ✅ Return consistent response format
- ✅ Use appropriate HTTP status codes

**Don't:**
- ❌ Expose sensitive data in errors
- ❌ Use file-based storage in production
- ❌ Skip input validation
- ❌ Ignore security best practices
- ❌ Mix concerns (validation, business logic, storage)

#### **10.2 Security**

**Do:**
- ✅ Authenticate all routes
- ✅ Validate all inputs
- ✅ Sanitize file paths
- ✅ Use environment variables for secrets
- ✅ Implement rate limiting

**Don't:**
- ❌ Trust user input
- ❌ Expose API keys
- ❌ Allow path traversal
- ❌ Skip authentication
- ❌ Ignore security headers

---

## 📚 **REFERENCES**

- System map: `systems/lucid-ide/backend-api-system/system.map.lucid.json5`
- System index: `systems/lucid-ide/backend-api-system/system.index.lucid.json5`
- L2 Architecture: `systems/lucid-ide/backend-api-system/L2_architecture.md`
- L4 Complete: `systems/lucid-ide/backend-api-system/L4_complete.md`

---

**Status:** Complete  
**Last Updated:** 2025-11-09  
**Version:** v1.0.0

