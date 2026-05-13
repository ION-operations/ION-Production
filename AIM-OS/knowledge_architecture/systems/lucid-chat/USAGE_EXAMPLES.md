# Lucid Chat - Usage Examples

**Version:** 0.9.2  
**Last Updated:** 2025-01-27  
**Status:** Production Ready

---

## 📚 **TABLE OF CONTENTS**

1. [Quick Start](#quick-start)
2. [Basic Examples](#basic-examples)
3. [Advanced Examples](#advanced-examples)
4. [Real-World Scenarios](#real-world-scenarios)
5. [Integration Examples](#integration-examples)
6. [Best Practices](#best-practices)
7. [Common Patterns](#common-patterns)
8. [Troubleshooting](#troubleshooting)

---

## 1. Quick Start

### 1.1 Installation

```typescript
// Install dependencies
npm install

// Set up environment variables
export API_KEY=your-api-key-here
export ANTHROPIC_API_KEY=your-anthropic-key
export GEMINI_API_KEY=your-gemini-key
```

### 1.2 Basic Chat

```typescript
import { LLMService } from './llm/LLMService'

const service = new LLMService()
const response = await service.chatCompletion({
  provider: 'anthropic',
  messages: [
    { role: 'user', content: 'Hello, world!' }
  ]
})

if (response.success) {
  console.log(response.data.text)
} else {
  console.error(response.error)
}
```

### 1.3 Advanced Chat

```typescript
import { AdvancedLLMService } from './llm/AdvancedLLMService'

const service = new AdvancedLLMService()
const response = await service.advancedChatCompletion({
  messages: [
    { role: 'user', content: 'Research quantum computing' }
  ],
  thinkingMode: {
    mode: 'analytical'
  },
  deepSearch: {
    providers: ['deepsearch', 'perplexity'],
    depth: 'comprehensive'
  }
})

console.log(response.data.text)
console.log(response.data.searchResults)
```

---

## 2. Basic Examples

### 2.1 Simple Question-Answer

```typescript
import { LLMService } from './llm/LLMService'

const service = new LLMService()

async function askQuestion(question: string) {
  const response = await service.chatCompletion({
    provider: 'anthropic',
    messages: [
      { role: 'user', content: question }
    ],
    temperature: 0.7,
    maxTokens: 500
  })
  
  if (response.success) {
    return response.data.text
  } else {
    throw new Error(response.error?.message || 'Unknown error')
  }
}

// Usage
const answer = await askQuestion('What is quantum computing?')
console.log(answer)
```

### 2.2 Multi-Turn Conversation

```typescript
import { LLMService } from './llm/LLMService'
import { ChatHistoryService } from './memory/ChatHistoryService'

const llmService = new LLMService()
const historyService = new ChatHistoryService()

// Start session
const session = await historyService.startSession('user123')

// Conversation loop
async function chat(message: string) {
  // Add user message
  await historyService.addMessage({
    role: 'user',
    content: message,
    timestamp: new Date()
  })
  
  // Get conversation history
  const messages = session.messages.map(m => ({
    role: m.role,
    content: m.content
  }))
  
  // Get LLM response
  const response = await llmService.chatCompletion({
    provider: 'anthropic',
    messages
  })
  
  if (response.success) {
    // Add assistant message
    await historyService.addMessage({
      role: 'assistant',
      content: response.data.text,
      timestamp: new Date()
    })
    
    return response.data.text
  } else {
    throw new Error(response.error?.message || 'Unknown error')
  }
}

// Usage
await chat('Hello!')
await chat('Tell me about quantum computing')
await chat('What are the applications?')
```

### 2.3 System Prompts

```typescript
import { LLMService } from './llm/LLMService'

const service = new LLMService()

const response = await service.chatCompletion({
  provider: 'anthropic',
  system: 'You are an expert software engineer specializing in TypeScript and React.',
  messages: [
    { role: 'user', content: 'How do I optimize React performance?' }
  ]
})

console.log(response.data.text)
```

### 2.4 Different Providers

```typescript
import { LLMService } from './llm/LLMService'

const service = new LLMService()

// Anthropic Claude
const claude = await service.chatCompletion({
  provider: 'anthropic',
  model: 'claude-3-5-sonnet-20241022',
  messages: [{ role: 'user', content: 'Hello!' }]
})

// Google Gemini
const gemini = await service.chatCompletion({
  provider: 'gemini',
  model: 'gemini-2.0-flash-exp',
  messages: [{ role: 'user', content: 'Hello!' }]
})

// Cerebras
const cerebras = await service.chatCompletion({
  provider: 'cerebras',
  model: 'llama-3.1-70b',
  messages: [{ role: 'user', content: 'Hello!' }]
})
```

---

## 3. Advanced Examples

### 3.1 Thinking Modes

```typescript
import { AdvancedLLMService } from './llm/AdvancedLLMService'

const service = new AdvancedLLMService()

// Creative Mode
const creative = await service.advancedChatCompletion({
  messages: [
    { role: 'user', content: 'Write a creative story about AI' }
  ],
  thinkingMode: {
    mode: 'creative',
    config: {
      temperature: 0.9,
      useBranchReasoning: false
    }
  }
})

// Analytical Mode
const analytical = await service.advancedChatCompletion({
  messages: [
    { role: 'user', content: 'Analyze this code for performance issues' }
  ],
  thinkingMode: {
    mode: 'analytical',
    config: {
      temperature: 0.3,
      useBranchReasoning: true,
      numBranches: 3
    }
  }
})

// Reasoning Mode
const reasoning = await service.advancedChatCompletion({
  messages: [
    { role: 'user', content: 'Prove this theorem' }
  ],
  thinkingMode: {
    mode: 'reasoning',
    config: {
      temperature: 0.2,
      useBranchReasoning: true,
      reasoningType: 'deductive'
    }
  }
})
```

### 3.2 Deep Search Integration

```typescript
import { AdvancedLLMService } from './llm/AdvancedLLMService'

const service = new AdvancedLLMService()

const response = await service.advancedChatCompletion({
  messages: [
    { role: 'user', content: 'Research the latest developments in quantum computing' }
  ],
  deepSearch: {
    providers: ['deepsearch', 'perplexity', 'tavily', 'icip'],
    depth: 'comprehensive',
    enableCrawling: true,
    crawlDepth: 2,
    trustThreshold: 0.7,
    synthesizeResults: true,
    detectContradictions: true,
    requireCitations: true
  }
})

console.log('Response:', response.data.text)
console.log('Search Results:', response.data.searchResults)
console.log('Synthesis:', response.data.segSynthesis)
```

### 3.3 APOE Orchestration

```typescript
import { AdvancedLLMService } from './llm/AdvancedLLMService'

const service = new AdvancedLLMService()

const response = await service.advancedChatCompletion({
  messages: [
    { role: 'user', content: 'Plan and build a REST API for user management' }
  ],
  apoe: {
    useAPOE: true,
    roles: [
      { role: 'planner', temperature: 0.7 },
      { role: 'retriever', temperature: 0.3 },
      { role: 'reasoner', temperature: 0.2 },
      { role: 'builder', temperature: 0.5 },
      { role: 'verifier', temperature: 0.1 }
    ],
    workflow: {
      parallel: false,
      budget: {
        tokens: 10000,
        time: 60000,
        cost: 1.0
      }
    }
  }
})

console.log('Response:', response.data.text)
console.log('APOE Trace:', response.data.apoeTrace)
```

### 3.4 Branch Reasoning

```typescript
import { BranchReasoningService } from './reasoning/BranchReasoningService'

const service = new BranchReasoningService()

const response = await service.reasonWithBranches(
  'How to optimize database queries for a high-traffic web application?',
  {
    numBranches: 3,
    reasoningType: 'deductive',
    pruneThreshold: 0.7,
    storeToCMC: true
  }
)

console.log('Best Solution:', response.data.bestBranch)
console.log('All Branches:', response.data.branches)
```

### 3.5 Autonomous Research

```typescript
import { ARDService } from './research/ARDService'

const service = new ARDService()

const response = await service.conductResearch({
  topic: { topic: 'quantum computing applications in cryptography' },
  depth: 'deep',
  recursiveDepth: 2,
  generateImprovements: true,
  synthesize: true
})

console.log('Findings:', response.data.findings)
console.log('Improvements:', response.data.improvements)
console.log('Synthesis:', response.data.synthesis)
```

---

## 4. Real-World Scenarios

### 4.1 Research Assistant

```typescript
import { AdvancedLLMService } from './llm/AdvancedLLMService'
import { ARDService } from './research/ARDService'
import { ChatHistoryService } from './memory/ChatHistoryService'

class ResearchAssistant {
  private llmService: AdvancedLLMService
  private ardService: ARDService
  private historyService: ChatHistoryService
  
  constructor() {
    this.llmService = new AdvancedLLMService()
    this.ardService = new ARDService()
    this.historyService = new ChatHistoryService()
  }
  
  async researchTopic(topic: string) {
    // Start session
    const session = await this.historyService.startSession()
    
    // Conduct autonomous research
    const research = await this.ardService.conductResearch({
      topic: { topic },
      depth: 'deep',
      recursiveDepth: 2,
      generateImprovements: true,
      synthesize: true
    })
    
    // Generate comprehensive report
    const report = await this.llmService.advancedChatCompletion({
      messages: [
        { role: 'system', content: 'You are a research assistant. Generate a comprehensive report based on research findings.' },
        { role: 'user', content: `Research Topic: ${topic}\n\nFindings: ${JSON.stringify(research.data.findings, null, 2)}\n\nGenerate a comprehensive report.` }
      ],
      thinkingMode: { mode: 'analytical' },
      deepSearch: { providers: ['deepsearch'], depth: 'comprehensive' }
    })
    
    return {
      topic,
      findings: research.data.findings,
      improvements: research.data.improvements,
      report: report.data.text,
      synthesis: research.data.synthesis
    }
  }
}

// Usage
const assistant = new ResearchAssistant()
const result = await assistant.researchTopic('quantum computing applications')
console.log(result.report)
```

### 4.2 Code Review Assistant

```typescript
import { AdvancedLLMService } from './llm/AdvancedLLMService'
import { ICIPSearchService } from './search/ICIPSearchService'

class CodeReviewAssistant {
  private llmService: AdvancedLLMService
  private codeSearch: ICIPSearchService
  
  constructor() {
    this.llmService = new AdvancedLLMService()
    this.codeSearch = new ICIPSearchService()
  }
  
  async reviewCode(code: string, language: string = 'typescript') {
    // Search for similar code patterns
    const similarCode = await this.codeSearch.search('authentication function', {
      language,
      tier: 'semantic',
      maxResults: 5
    })
    
    // Generate review
    const review = await this.llmService.advancedChatCompletion({
      messages: [
        { role: 'system', content: 'You are an expert code reviewer. Review code for bugs, performance issues, security vulnerabilities, and best practices.' },
        { role: 'user', content: `Review this ${language} code:\n\n\`\`\`${language}\n${code}\n\`\`\`\n\nSimilar patterns found:\n${JSON.stringify(similarCode.data.results, null, 2)}` }
      ],
      thinkingMode: { mode: 'analytical' },
      apoe: {
        useAPOE: true,
        roles: [
          { role: 'critic' },
          { role: 'verifier' }
        ]
      }
    })
    
    return review.data.text
  }
}

// Usage
const reviewer = new CodeReviewAssistant()
const review = await reviewer.reviewCode(`
function authenticate(user: string, password: string) {
  if (user === 'admin' && password === 'password') {
    return true
  }
  return false
}
`)
console.log(review)
```

### 4.3 Documentation Generator

```typescript
import { AdvancedLLMService } from './llm/AdvancedLLMService'
import { ICIPSearchService } from './search/ICIPSearchService'

class DocumentationGenerator {
  private llmService: AdvancedLLMService
  private codeSearch: ICIPSearchService
  
  constructor() {
    this.llmService = new AdvancedLLMService()
    this.codeSearch = new ICIPSearchService()
  }
  
  async generateDocs(functionName: string, code: string) {
    // Search for usage examples
    const examples = await this.codeSearch.search(`usage of ${functionName}`, {
      tier: 'semantic',
      maxResults: 3
    })
    
    // Generate documentation
    const docs = await this.llmService.advancedChatCompletion({
      messages: [
        { role: 'system', content: 'You are a technical writer. Generate comprehensive documentation including description, parameters, return value, examples, and best practices.' },
        { role: 'user', content: `Generate documentation for this function:\n\n\`\`\`typescript\n${code}\n\`\`\`\n\nUsage examples:\n${JSON.stringify(examples.data.results, null, 2)}` }
      ],
      thinkingMode: { mode: 'balanced' },
      outputProtocol: {
        format: 'markdown',
        style: 'technical',
        tone: 'professional'
      }
    })
    
    return docs.data.text
  }
}

// Usage
const generator = new DocumentationGenerator()
const docs = await generator.generateDocs('authenticate', `
function authenticate(user: string, password: string): boolean {
  // Implementation
}
`)
console.log(docs)
```

### 4.4 Testing Assistant

```typescript
import { AdvancedLLMService } from './llm/AdvancedLLMService'
import { MultiAgentOrchestrator, AgentRegistry, TestingAgent } from './agents'

class TestingAssistant {
  private llmService: AdvancedLLMService
  private orchestrator: MultiAgentOrchestrator
  private registry: AgentRegistry
  
  constructor() {
    this.llmService = new AdvancedLLMService()
    this.registry = new AgentRegistry()
    this.orchestrator = new MultiAgentOrchestrator(this.registry)
    
    // Register testing agent
    const testingAgent = new TestingAgent('testing-1')
    this.registry.register(testingAgent)
  }
  
  async generateTests(code: string, framework: string = 'vitest') {
    // Use testing agent
    const result = await this.orchestrator.executeParallel([
      {
        id: 'test-1',
        description: `Generate ${framework} tests for this code`,
        type: 'testing',
        input: { code, framework }
      }
    ])
    
    return result[0].output.tests
  }
}

// Usage
const assistant = new TestingAssistant()
const tests = await assistant.generateTests(`
function add(a: number, b: number): number {
  return a + b
}
`, 'vitest')
console.log(tests)
```

### 4.5 Knowledge Base Query

```typescript
import { AdvancedLLMService } from './llm/AdvancedLLMService'
import { ChatHistoryService } from './memory/ChatHistoryService'
import { ContextManager } from './memory/ContextManager'

class KnowledgeBaseQuery {
  private llmService: AdvancedLLMService
  private historyService: ChatHistoryService
  private contextManager: ContextManager
  
  constructor() {
    this.llmService = new AdvancedLLMService()
    this.historyService = new ChatHistoryService()
    this.contextManager = new ContextManager()
  }
  
  async query(question: string, userId: string) {
    // Load user profile
    const profile = await this.historyService.loadProfile(userId)
    
    // Search chat history
    const relevantMessages = await this.historyService.searchMessages(question)
    
    // Get context
    const context = await this.contextManager.getContext(
      relevantMessages,
      {
        strategy: 'relevant',
        maxTokens: 4000
      }
    )
    
    // Generate answer with context
    const answer = await this.llmService.advancedChatCompletion({
      messages: [
        ...context.map(m => ({ role: m.role, content: m.content })),
        { role: 'user', content: question }
      ],
      thinkingMode: { mode: 'analytical' },
      deepSearch: {
        providers: ['deepsearch', 'icip'],
        depth: 'advanced'
      }
    })
    
    return answer.data.text
  }
}

// Usage
const kb = new KnowledgeBaseQuery()
const answer = await kb.query('What is quantum computing?', 'user123')
console.log(answer)
```

---

## 5. Integration Examples

### 5.1 AIM-OS Integration

```typescript
import { AdvancedLLMService } from './llm/AdvancedLLMService'
import { AIMOSIntegrationService } from './base/AIMOSIntegrationService'

const llmService = new AdvancedLLMService()
const aimosIntegration = new AIMOSIntegrationService()

// Chat with AIM-OS integration
const response = await llmService.advancedChatCompletion({
  messages: [
    { role: 'user', content: 'Research quantum computing' }
  ],
  deepSearch: {
    providers: ['deepsearch', 'perplexity'],
    depth: 'comprehensive'
  }
})

// Response automatically stored in CMC via AIMOSIntegrationService
// Check response.aimos for integration details
console.log('Atom ID:', response.aimos?.atomId)
console.log('Confidence:', response.aimos?.confidence)
console.log('Stored:', response.aimos?.stored)
```

### 5.2 CMC Storage

```typescript
import { BaseAPIService } from './base/BaseAPIService'

class MyService extends BaseAPIService {
  async storeData(data: any) {
    // Store to CMC
    const atomId = await this.storeToCMC(
      data,
      'my_data_type',
      ['tag1', 'tag2']
    )
    
    return atomId
  }
  
  async retrieveData(query: string) {
    // Retrieve from HHNI
    const results = await this.retrieveFromHHNI(query, 10)
    
    return results
  }
}
```

### 5.3 Error Handling with Recovery

```typescript
import { LLMService } from './llm/LLMService'
import { ErrorRecovery, RetryManager, CircuitBreaker } from './recovery'

const llmService = new LLMService()
const recovery = new ErrorRecovery({
  retry: RetryManager,
  circuitBreaker: new CircuitBreaker({
    failureThreshold: 5,
    recoveryTimeout: 60000
  }),
  fallback: async () => ({
    success: false,
    error: { code: 'FALLBACK', message: 'Service unavailable' }
  })
})

async function robustChat(message: string) {
  return await recovery.execute(async () => {
    return await llmService.chatCompletion({
      provider: 'anthropic',
      messages: [{ role: 'user', content: message }]
    })
  })
}

// Usage
const response = await robustChat('Hello!')
```

### 5.4 Caching Strategy

```typescript
import { LLMService } from './llm/LLMService'
import { CacheManager } from './cache/CacheManager'

const llmService = new LLMService()
const cache = new CacheManager({
  maxSize: 1000,
  defaultTTL: 3600000 // 1 hour
})

async function cachedChat(message: string) {
  // Check cache
  const cacheKey = `chat:${message}`
  const cached = cache.get<string>(cacheKey)
  
  if (cached) {
    return cached
  }
  
  // Call LLM
  const response = await llmService.chatCompletion({
    provider: 'anthropic',
    messages: [{ role: 'user', content: message }]
  })
  
  if (response.success) {
    // Cache result
    cache.set(cacheKey, response.data.text, 3600000) // 1 hour
    return response.data.text
  } else {
    throw new Error(response.error?.message || 'Unknown error')
  }
}
```

### 5.5 Rate Limiting

```typescript
import { LLMService } from './llm/LLMService'
import { RateLimiter } from './cache/RateLimiter'

const llmService = new LLMService()
const limiter = new RateLimiter()

async function rateLimitedChat(message: string, userId: string) {
  // Check rate limit
  const status = limiter.checkLimit(userId, {
    limit: 100,
    window: 60000, // 1 minute
    burst: 20
  })
  
  if (!status.allowed) {
    throw new Error(`Rate limit exceeded. Try again in ${status.resetAfter}ms`)
  }
  
  // Consume tokens
  limiter.consume(userId, 1, {
    limit: 100,
    window: 60000
  })
  
  // Call LLM
  return await llmService.chatCompletion({
    provider: 'anthropic',
    messages: [{ role: 'user', content: message }]
  })
}
```

### 5.6 Budget Management

```typescript
import { AdvancedLLMService } from './llm/AdvancedLLMService'
import { BudgetTracker } from './orchestration/BudgetTracker'

const llmService = new AdvancedLLMService()
const budgetTracker = new BudgetTracker()

// Start budget
budgetTracker.start({
  tokens: 10000,
  time: 60000, // 1 minute
  cost: 1.0 // $1.00
})

async function budgetedChat(message: string) {
  // Check budget
  const status = budgetTracker.check()
  if (!status.withinBudget) {
    throw new Error('Budget exceeded')
  }
  
  // Call LLM
  const response = await llmService.advancedChatCompletion({
    messages: [{ role: 'user', content: message }]
  })
  
  // Track usage
  if (response.metadata) {
    budgetTracker.track(
      response.metadata.tokensUsed || 0,
      response.metadata.latencyMs || 0,
      response.metadata.cost || 0
    )
  }
  
  return response
}
```

---

## 6. Best Practices

### 6.1 Input Validation

```typescript
import { InputValidator } from './validation/InputValidator'
import { SecurityValidator } from './validation/SecurityValidator'

async function safeChat(userInput: string) {
  // Validate input
  const validated = InputValidator.validateString(userInput, 'query', {
    minLength: 1,
    maxLength: 1000,
    required: true,
    trim: true
  })
  
  // Security validation
  if (SecurityValidator.detectXSS(validated)) {
    throw new Error('XSS detected')
  }
  
  if (SecurityValidator.detectInjection(validated)) {
    throw new Error('Injection detected')
  }
  
  // Sanitize
  const sanitized = SecurityValidator.sanitizeString(validated)
  
  // Use sanitized input
  // ...
}
```

### 6.2 Error Handling

```typescript
import { LLMService } from './llm/LLMService'

const service = new LLMService()

async function robustChat(message: string) {
  try {
    const response = await service.chatCompletion({
      provider: 'anthropic',
      messages: [{ role: 'user', content: message }]
    })
    
    if (!response.success) {
      // Handle API error
      console.error('API Error:', response.error)
      
      // Check error code
      switch (response.error?.code) {
        case 'RATE_LIMIT_EXCEEDED':
          // Retry after delay
          await new Promise(resolve => setTimeout(resolve, 5000))
          return await robustChat(message)
        case 'BUDGET_EXCEEDED':
          throw new Error('Budget exceeded')
        case 'VALIDATION_ERROR':
          throw new Error('Invalid input')
        default:
          throw new Error(response.error?.message || 'Unknown error')
      }
    }
    
    return response.data
  } catch (error) {
    // Handle unexpected errors
    console.error('Unexpected error:', error)
    throw error
  }
}
```

### 6.3 Context Management

```typescript
import { ContextManager } from './memory/ContextManager'
import { ChatHistoryService } from './memory/ChatHistoryService'

const contextManager = new ContextManager()
const historyService = new ChatHistoryService()

async function contextualChat(message: string, userId: string) {
  // Get chat history
  const session = await historyService.getSession(userId)
  const messages = session.messages
  
  // Get relevant context
  const context = await contextManager.getContext(messages, {
    strategy: 'relevant', // or 'recent', 'sliding_window', 'summary'
    maxTokens: 4000
  })
  
  // Use context in LLM call
  // ...
}
```

### 6.4 Quality Assurance

```typescript
import { QualityGates } from './orchestration/QualityGates'

const gates = new QualityGates()

async function qualityCheckedResponse(result: RoleResult) {
  // Evaluate quality gates
  const passed = await gates.evaluate(result, {
    confidence: 0.70,
    kappa: 0.75,
    quality: 0.80,
    consistency: 0.85,
    budget: true,
    vif: true
  })
  
  if (!passed) {
    throw new Error('Quality gates failed')
  }
  
  return result
}
```

---

## 7. Common Patterns

### 7.1 Service Composition

```typescript
import { AdvancedLLMService } from './llm/AdvancedLLMService'
import { DeepSearchService } from './search/DeepSearchService'
import { BranchReasoningService } from './reasoning/BranchReasoningService'

class CompositeService {
  private llmService: AdvancedLLMService
  private searchService: DeepSearchService
  private reasoningService: BranchReasoningService
  
  constructor() {
    this.llmService = new AdvancedLLMService()
    this.searchService = new DeepSearchService()
    this.reasoningService = new BranchReasoningService()
  }
  
  async comprehensiveAnalysis(question: string) {
    // 1. Search
    const searchResults = await this.searchService.search(question, {
      depth: 'comprehensive'
    })
    
    // 2. Reason
    const reasoning = await this.reasoningService.reasonWithBranches(question, {
      numBranches: 3
    })
    
    // 3. Synthesize
    const synthesis = await this.llmService.advancedChatCompletion({
      messages: [
        { role: 'user', content: `Question: ${question}\n\nSearch Results: ${JSON.stringify(searchResults.data.results)}\n\nReasoning: ${JSON.stringify(reasoning.data.bestBranch)}` }
      ],
      thinkingMode: { mode: 'analytical' }
    })
    
    return {
      searchResults: searchResults.data,
      reasoning: reasoning.data,
      synthesis: synthesis.data.text
    }
  }
}
```

### 7.2 Parallel Execution

```typescript
import { SearchOrchestrator } from './search/SearchOrchestrator'

const orchestrator = new SearchOrchestrator()

async function parallelSearch(query: string) {
  // Execute searches in parallel
  const results = await orchestrator.orchestrateSearch(
    query,
    ['deepsearch', 'perplexity', 'tavily', 'icip'],
    {
      parallel: true,
      synthesize: true,
      deduplicate: true
    }
  )
  
  return results.data.aggregated
}
```

### 7.3 Sequential Workflow

```typescript
import { WorkflowExecutor } from './orchestration/WorkflowExecutor'

const executor = new WorkflowExecutor()

async function sequentialWorkflow() {
  const plan = {
    id: 'workflow-1',
    steps: [
      { id: 'step-1', role: 'planner', task: 'Plan the solution' },
      { id: 'step-2', role: 'retriever', task: 'Retrieve relevant information', dependsOn: ['step-1'] },
      { id: 'step-3', role: 'reasoner', task: 'Reason about the solution', dependsOn: ['step-2'] },
      { id: 'step-4', role: 'builder', task: 'Build the solution', dependsOn: ['step-3'] }
    ]
  }
  
  const result = await executor.execute(plan, {
    budget: {
      tokens: 10000,
      time: 60000,
      cost: 1.0
    },
    qualityGates: {
      confidence: 0.70,
      kappa: 0.75
    }
  })
  
  return result
}
```

---

## 8. Troubleshooting

### 8.1 Common Errors

**Rate Limit Exceeded:**
```typescript
// Error: Rate limit exceeded
// Solution: Implement rate limiting check before requests
const status = limiter.checkLimit(userId, { limit: 100, window: 60000 })
if (!status.allowed) {
  // Wait or return error
}
```

**Budget Exceeded:**
```typescript
// Error: Budget exceeded
// Solution: Check budget before requests
const status = budgetTracker.check()
if (!status.withinBudget) {
  // Reduce request size or return error
}
```

**Quality Gate Failed:**
```typescript
// Error: Quality gate failed
// Solution: Adjust quality thresholds or improve input
const passed = await gates.evaluate(result, {
  confidence: 0.70, // Lower threshold if needed
  kappa: 0.75
})
```

**Authentication Failed:**
```typescript
// Error: Authentication failed
// Solution: Check API key
const result = Authentication.authenticate(apiKey, {
  requireAuth: true,
  apiKey: process.env.API_KEY
})
```

### 8.2 Performance Optimization

**Use Caching:**
```typescript
const cache = new CacheManager()
const cached = cache.get<string>(key)
if (cached) return cached
// ... expensive operation
cache.set(key, result, ttl)
```

**Use Parallel Execution:**
```typescript
// Instead of sequential
const result1 = await operation1()
const result2 = await operation2()

// Use parallel
const [result1, result2] = await Promise.all([
  operation1(),
  operation2()
])
```

**Optimize Context:**
```typescript
// Use relevant strategy for better context
const context = await contextManager.getContext(messages, {
  strategy: 'relevant', // Better than 'recent'
  maxTokens: 4000
})
```

---

**Status:** ✅ **COMPLETE**  
**Version:** 0.9.2  
**Last Updated:** 2025-01-27  
**Word Count:** ~1,500 words


