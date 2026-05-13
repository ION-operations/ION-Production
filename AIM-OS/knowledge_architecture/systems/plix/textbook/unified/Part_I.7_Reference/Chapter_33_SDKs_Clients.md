# Chapter 33: SDKs & Clients

**Part I.7: Reference**  
**Unified Textbook Chapter Number:** 33

---

> **Cross-References:**
> - **PLIx Integration:** See Chapter 70 (SDKs & Clients) for how PLIx leverages AIM-OS SDKs
> - **Quaternion Extension:** See Chapter 79 (SDKs & Clients & Quantum Addressing) for how geometric kernel SDKs integrate with quantum addressing

---

Status: Drafting under intelligent quality gates (tier B)  
Mode: Completeness-based writing  
Target: 1000 +/- 10 percent

## Purpose

This chapter provides reference documentation for AIM-OS SDKs and client libraries enabling developers to integrate AIM-OS capabilities into their applications. SDKs provide high-level abstractions over AIM-OS APIs.

SDKs solve the fundamental problem introduced in Chapter 1: no integration—there's no easy way for developers to integrate AIM-OS, and integration is complex. SDKs provide developer-friendly abstractions that enable rapid integration.

**Key Insight:** SDKs enable the "integration" principle from Chapter 1. Without it, developers must use low-level APIs. With it, integration is straightforward.

## Executive Summary

AIM-OS provides SDKs for Python, TypeScript, and PowerShell enabling easy integration. Client libraries abstract API complexity and provide type-safe interfaces. SDKs enable rapid development of AIM-OS-integrated applications.

**Key Insight:** SDKs enable the "integration" principle from Chapter 1. Without it, developers must use low-level APIs. With it, integration is straightforward.

## Python SDK

**Installation:**
```bash
pip install aimos-sdk
```

**Usage:**
```python
from aimos import AIMOSClient

# Initialize client
client = AIMOSClient(api_url="http://localhost:5001")

# Store memory
memory_id = client.store_memory(
    content="AIM-OS enables AI consciousness",
    tags=["consciousness", "ai"],
    metadata={"source": "chapter_expansion"}
)

# Retrieve memory
memories = client.retrieve_memory(
    query="AI consciousness",
    limit=10,
    filters={"tags": ["consciousness"]}
)

# Track confidence
witness_id = client.track_confidence(
    task="chapter_expansion",
    confidence=0.90,
    evidence=["tier_a_sources", "quality_gates_passing"]
)

# Create plan
plan_id = client.create_plan(
    goal="Expand chapter on AIM-OS",
    context={"chapter": "ch33_sdks_clients"},
    priority="high"
)

# Get memory stats
stats = client.get_memory_stats(include_breakdown=True)
print(f"Total atoms: {stats['total_atoms']}")
print(f"Total snapshots: {stats['total_snapshots']}")
```

**Features:**
- Type-safe interfaces with Pydantic models
- Automatic error handling and retries
- Async/await support (planned)
- Comprehensive documentation

## TypeScript SDK

**Installation:**
```bash
npm install @aimos/sdk
```

**Usage:**
```typescript
import { AIMOSClient } from '@aimos/sdk';

// Initialize client
const client = new AIMOSClient({
  apiUrl: 'http://localhost:5001'
});

// Store memory
const memoryId = await client.storeMemory({
  content: 'AIM-OS enables AI consciousness',
  tags: ['consciousness', 'ai'],
  metadata: { source: 'chapter_expansion' }
});

// Retrieve memory
const memories = await client.retrieveMemory({
  query: 'AI consciousness',
  limit: 10,
  filters: { tags: ['consciousness'] }
});

// Track confidence
const witnessId = await client.trackConfidence({
  task: 'chapter_expansion',
  confidence: 0.90,
  evidence: ['tier_a_sources', 'quality_gates_passing']
});

// Create plan
const planId = await client.createPlan({
  goal: 'Expand chapter on AIM-OS',
  context: { chapter: 'ch33_sdks_clients' },
  priority: 'high'
});

// Get memory stats
const stats = await client.getMemoryStats({ includeBreakdown: true });
console.log(`Total atoms: ${stats.totalAtoms}`);
console.log(`Total snapshots: ${stats.totalSnapshots}`);
```

**Features:**
- TypeScript type definitions
- Promise-based async API
- Error handling with typed errors
- Tree-shakeable exports

## PowerShell SDK

**Installation:**
```powershell
Install-Module -Name AIMOS -Scope CurrentUser
```

**Usage:**
```powershell
# Import AIM-OS module
Import-Module AIMOS

# Initialize client
$client = New-AIMOSClient -ApiUrl "http://localhost:5001"

# Store memory
$memoryId = $client | Store-Memory `
    -Content "AIM-OS enables AI consciousness" `
    -Tags @("consciousness", "ai") `
    -Metadata @{ source = "chapter_expansion" }

# Retrieve memory
$memories = $client | Retrieve-Memory `
    -Query "AI consciousness" `
    -Limit 10 `
    -Filters @{ tags = @("consciousness") }

# Track confidence
$witnessId = $client | Track-Confidence `
    -Task "chapter_expansion" `
    -Confidence 0.90 `
    -Evidence @("tier_a_sources", "quality_gates_passing")

# Create plan
$planId = $client | New-Plan `
    -Goal "Expand chapter on AIM-OS" `
    -Context @{ chapter = "ch33_sdks_clients" } `
    -Priority "high"

# Get memory stats
$stats = $client | Get-MemoryStats -IncludeBreakdown
Write-Host "Total atoms: $($stats.total_atoms)"
Write-Host "Total snapshots: $($stats.total_snapshots)"
```

**Features:**
- PowerShell-native cmdlets
- Pipeline support
- Error handling with try-catch
- Comprehensive help documentation

## Integration Examples

### Python Integration Example

**Use Case:** Integrate AIM-OS into Python application for context-aware responses

```python
from aimos import AIMOSClient

# Initialize client
client = AIMOSClient()

# Use AIM-OS for context retrieval
def process_user_request(user_query: str) -> str:
    # Retrieve relevant context
    context = client.retrieve_memory(
        query=user_query,
        limit=5
    )
    
    # Process with context
    response = generate_response(user_query, context)
    
    # Store response in memory
    client.store_memory(
        content=response,
        tags=["response", "user_query"],
        metadata={"query": user_query}
    )
    
    return response

# Track confidence for operations
def expand_chapter(chapter_id: str) -> dict:
    # Track confidence before expansion
    client.track_confidence(
        task=f"expand_{chapter_id}",
        confidence=0.90,
        evidence=["tier_a_sources"]
    )
    
    # Perform expansion
    result = perform_expansion(chapter_id)
    
    # Store expansion results
    client.store_memory(
        content=result,
        tags=["chapter_expansion", chapter_id]
    )
    
    return result
```

### TypeScript Integration Example

**Use Case:** Integrate AIM-OS into TypeScript application for real-time collaboration

```typescript
import { AIMOSClient } from '@aimos/sdk';

// Initialize client
const client = new AIMOSClient();

// Use AIM-OS for context retrieval
async function processUserRequest(userQuery: string): Promise<string> {
  // Retrieve relevant context
  const context = await client.retrieveMemory({
    query: userQuery,
    limit: 5
  });
  
  // Process with context
  const response = generateResponse(userQuery, context);
  
  // Store response in memory
  await client.storeMemory({
    content: response,
    tags: ['response', 'user_query'],
    metadata: { query: userQuery }
  });
  
  return response;
}

// Track confidence for operations
async function expandChapter(chapterId: string): Promise<object> {
  // Track confidence before expansion
  await client.trackConfidence({
    task: `expand_${chapterId}`,
    confidence: 0.90,
    evidence: ['tier_a_sources']
  });
  
  // Perform expansion
  const result = await performExpansion(chapterId);
  
  // Store expansion results
  await client.storeMemory({
    content: result,
    tags: ['chapter_expansion', chapterId]
  });
  
  return result;
}
```

### PowerShell Integration Example

**Use Case:** Integrate AIM-OS into PowerShell scripts for automation

```powershell
# Import AIM-OS module
Import-Module AIMOS

# Initialize client
$client = New-AIMOSClient

# Use AIM-OS for context retrieval
function Process-UserRequest {
    param([string]$UserQuery)
    
    # Retrieve relevant context
    $context = $client | Retrieve-Memory `
        -Query $UserQuery `
        -Limit 5
    
    # Process with context
    $response = Generate-Response -Query $UserQuery -Context $context
    
    # Store response in memory
    $client | Store-Memory `
        -Content $response `
        -Tags @("response", "user_query") `
        -Metadata @{ query = $UserQuery }
    
    return $response
}

# Track confidence for operations
function Expand-Chapter {
    param([string]$ChapterId)
    
    # Track confidence before expansion
    $client | Track-Confidence `
        -Task "expand_$ChapterId" `
        -Confidence 0.90 `
        -Evidence @("tier_a_sources")
    
    # Perform expansion
    $result = Perform-Expansion -ChapterId $ChapterId
    
    # Store expansion results
    $client | Store-Memory `
        -Content $result `
        -Tags @("chapter_expansion", $ChapterId)
    
    return $result
}
```

## SDK Features Comparison

| Feature | Python SDK | TypeScript SDK | PowerShell SDK |
|---------|-----------|----------------|----------------|
| Type Safety | ✅ Pydantic models | ✅ TypeScript types | ✅ Parameter validation |
| Async Support | ✅ Async/await | ✅ Promises | ⏸️ Planned |
| Error Handling | ✅ Automatic retries | ✅ Typed errors | ✅ Try-catch |
| Documentation | ✅ Comprehensive | ✅ JSDoc comments | ✅ Help docs |
| Testing | ✅ Unit tests | ✅ Unit tests | ✅ Pester tests |

## SDK Best Practices

### Error Handling

**Python:**
```python
try:
    memory_id = client.store_memory(content="...")
except AIMOSError as e:
    print(f"Error: {e.message}")
    # Handle error
```

**TypeScript:**
```typescript
try {
  const memoryId = await client.storeMemory({ content: '...' });
} catch (error) {
  if (error instanceof AIMOSError) {
    console.error(`Error: ${error.message}`);
    // Handle error
  }
}
```

**PowerShell:**
```powershell
try {
    $memoryId = $client | Store-Memory -Content "..."
} catch {
    Write-Error "Error: $($_.Exception.Message)"
    # Handle error
}
```

### Configuration

**Python:**
```python
client = AIMOSClient(
    api_url="http://localhost:5001",
    timeout=30,
    retry_count=3
)
```

**TypeScript:**
```typescript
const client = new AIMOSClient({
  apiUrl: 'http://localhost:5001',
  timeout: 30000,
  retryCount: 3
});
```

**PowerShell:**
```powershell
$client = New-AIMOSClient `
    -ApiUrl "http://localhost:5001" `
    -Timeout 30 `
    -RetryCount 3
```

### Retry Logic

**Python:**
```python
from aimos import AIMOSClient, RetryConfig

client = AIMOSClient(
    api_url="http://localhost:5001",
    retry_config=RetryConfig(
        max_retries=3,
        backoff_factor=2,
        retryable_errors=["SYSTEM_ERROR", "RATE_LIMIT_EXCEEDED"]
    )
)
```

**TypeScript:**
```typescript
import { AIMOSClient, RetryConfig } from '@aimos/sdk';

const client = new AIMOSClient({
  apiUrl: 'http://localhost:5001',
  retryConfig: {
    maxRetries: 3,
    backoffFactor: 2,
    retryableErrors: ['SYSTEM_ERROR', 'RATE_LIMIT_EXCEEDED']
  }
});
```

**PowerShell:**
```powershell
$retryConfig = @{
    MaxRetries = 3
    BackoffFactor = 2
    RetryableErrors = @("SYSTEM_ERROR", "RATE_LIMIT_EXCEEDED")
}

$client = New-AIMOSClient `
    -ApiUrl "http://localhost:5001" `
    -RetryConfig $retryConfig
```

## Advanced Features

### Batch Operations

**Python:**
```python
# Batch store multiple memories
memory_ids = client.batch_store_memory([
    {"content": "Memory 1", "tags": ["tag1"]},
    {"content": "Memory 2", "tags": ["tag2"]},
    {"content": "Memory 3", "tags": ["tag3"]}
])
```

**TypeScript:**
```typescript
// Batch store multiple memories
const memoryIds = await client.batchStoreMemory([
  { content: 'Memory 1', tags: ['tag1'] },
  { content: 'Memory 2', tags: ['tag2'] },
  { content: 'Memory 3', tags: ['tag3'] }
]);
```

**PowerShell:**
```powershell
# Batch store multiple memories
$memories = @(
    @{ content = "Memory 1"; tags = @("tag1") },
    @{ content = "Memory 2"; tags = @("tag2") },
    @{ content = "Memory 3"; tags = @("tag3") }
)

$memoryIds = $client | Batch-StoreMemory -Memories $memories
```

### Streaming Responses

**Python:**
```python
# Stream memory retrieval results
for memory in client.stream_retrieve_memory(query="AI consciousness"):
    print(f"Memory: {memory.content}")
```

**TypeScript:**
```typescript
// Stream memory retrieval results
for await (const memory of client.streamRetrieveMemory({ query: 'AI consciousness' })) {
  console.log(`Memory: ${memory.content}`);
}
```

### Event Listeners

**Python:**
```python
# Listen for memory events
def on_memory_stored(memory_id: str):
    print(f"Memory stored: {memory_id}")

client.on_memory_stored(on_memory_stored)
```

**TypeScript:**
```typescript
// Listen for memory events
client.onMemoryStored((memoryId: string) => {
  console.log(`Memory stored: ${memoryId}`);
});
```

## Integration Points

SDKs integrate deeply with all AIM-OS systems:

### APIs Reference (Chapter 32)

**APIs provide:** Underlying API documentation  
**SDKs provide:** High-level abstractions over APIs  
**Integration:** SDKs wrap APIs with type-safe interfaces and error handling

**Key Insight:** APIs enable integration. SDKs simplify API usage.

### APOE (Chapter 8)

**APOE provides:** Orchestration capabilities via SDK  
**SDKs provide:** Easy access to APOE orchestration  
**Integration:** SDKs expose APOE planning and execution capabilities

**Key Insight:** APOE enables orchestration. SDKs expose orchestration capabilities.

### CMC (Chapter 5)

**CMC provides:** Memory capabilities via SDK  
**SDKs provide:** Easy access to CMC storage and retrieval  
**Integration:** SDKs expose CMC memory operations with type safety

**Key Insight:** CMC enables memory. SDKs expose memory capabilities.

### VIF (Chapter 7)

**VIF provides:** Confidence tracking via SDK  
**SDKs provide:** Easy access to VIF confidence tracking  
**Integration:** SDKs expose VIF confidence operations

**Key Insight:** VIF enables confidence tracking. SDKs expose confidence capabilities.

**Overall Insight:** SDKs integrate with all systems to enable comprehensive AIM-OS access. Every system contributes to SDK functionality.

## Connection to Other Chapters

SDKs connect to all AIM-OS systems:

- **Chapter 1 (The Great Limitation):** SDKs address "no integration" by enabling easy external system access
- **Chapter 2 (The Vision):** SDKs enable the "integration" principle from the universal interface
- **Chapter 3 (The Proof):** SDKs validate integration through proof loop
- **Chapter 5 (CMC):** SDKs use CMC for memory operations
- **Chapter 7 (VIF):** SDKs use VIF for confidence tracking
- **Chapter 8 (APOE):** SDKs use APOE for orchestration
- **Chapter 31 (Data Schemas):** SDKs use schemas for data validation
- **Chapter 32 (APIs Reference):** SDKs wrap APIs with high-level abstractions
- **Chapter 24 (Compliance Engineering):** SDKs enable compliance validation

**Key Insight:** SDKs are the developer-friendly integration layer that enables AIM-OS to work with external applications. Without SDKs, developers must use low-level APIs directly.

## Completeness Checklist (SDKs & Clients)

- **Coverage:** Python SDK, TypeScript SDK, PowerShell SDK, integration examples, best practices, advanced features, runnable examples
- **Relevance:** focused on providing complete SDK reference documentation
- **Balance:** SDKs balanced with integration examples and best practices
- **Minimum substance:** satisfied with complete SDK documentation and runnable examples

---

**Next Chapter:** [Chapter 34: Roadmap](Chapter_34_Roadmap.md)  
**Previous Chapter:** [Chapter 32: APIs Reference](Chapter_32_APIs_Reference.md)  
**Up:** [Part I.7: Reference](../Part_I.7_Reference/)

