# Aether Chat Integration Examples

**For:** Nova (ICIP) and Alex (Backend)  
**Created by:** Sage - Frontend Integration Specialist  
**Date:** 2025-01-27

---

## 🔌 **Integration Examples**

### **Example 1: Full ICIP Integration (Nova)**

```typescript
import { AetherChat } from './components/aether-chat'
import { useICIP } from '../hooks/useICIP' // Nova's hook

function AetherChatWithICIP() {
  const {
    generating,
    transforming,
    error,
    lastResult,
    generateFunction,
    generateClass,
    generateTest,
    executeCode
  } = useICIP({
    autoValidate: true,
    storeInCMC: true,
    trackConfidence: true,
    trackInTimeline: true
  })

  const handleCodeGeneration = async (
    type: 'function' | 'class' | 'test' | 'documentation' | 'completion' | 'refactoring',
    prompt: string,
    language?: string,
    context?: string
  ) => {
    let result
    switch (type) {
      case 'function':
        result = await generateFunction(prompt, language, context)
        break
      case 'class':
        result = await generateClass(prompt, language, context)
        break
      case 'test':
        result = await generateTest(prompt, language, context)
        break
      // ... other types
    }
    return result
  }

  const handleCodeExecution = async (code: string, language: string) => {
    return await executeCode(code, language)
  }

  return (
    <AetherChat
      onCodeGenerate={handleCodeGeneration}
      onCodeExecute={handleCodeExecution}
    />
  )
}
```

### **Example 2: Backend Error Handling (Alex)**

```typescript
import { ErrorDisplay, type ErrorType } from './components/shared'
import { mcpService } from '../services/MCPService' // Alex's service

async function storeMemoryWithErrorHandling(content: string) {
  let retryCount = 0
  const maxRetries = 3

  while (retryCount < maxRetries) {
    try {
      const result = await mcpService.executeTool('mcp_lucid-mcp_store_memory', {
        content,
        tags: { test: 1.0 }
      })
      return result
    } catch (error) {
      retryCount++
      
      // Determine error type
      let errorType: ErrorType = 'system'
      if (error instanceof NetworkError) {
        errorType = 'network'
      } else if (error instanceof TimeoutError) {
        errorType = 'timeout'
      } else if (error instanceof ValidationError) {
        errorType = 'validation'
      } else if (error.status >= 400 && error.status < 500) {
        errorType = 'api'
      }

      // Show error with retry
      if (retryCount < maxRetries) {
        // User can retry via ErrorDisplay component
        return { error, errorType, retryCount }
      } else {
        // Max retries reached
        return { error, errorType, retryCount, maxRetries }
      }
    }
  }
}

// Usage in component
{error && (
  <ErrorDisplay
    error={error}
    errorType={errorType}
    onRetry={() => storeMemoryWithErrorHandling(content)}
    retryCount={retryCount}
    maxRetries={maxRetries}
  />
)}
```

### **Example 3: VIF Quality Gate Integration (Alex)**

```typescript
import { QualityGateDisplay, ConfidenceDisplay } from './components/aether-chat'
import { useVIF } from '../hooks/useAIMOS'

function CodeGenerationWithQualityGate() {
  const { trackConfidence, getWitnesses } = useVIF()

  const handleCodeGeneration = async (prompt: string) => {
    // Generate code (Nova's ICIP)
    const codeResult = await generateCode(prompt)
    
    // Track confidence
    const { witness_id, witness } = await trackConfidence(
      `Code generation: ${prompt}`,
      codeResult.confidence,
      [],
      `Generated code with ${codeResult.confidence} confidence`,
      'important' // task criticality
    )

    // Display quality gate
    return {
      code: codeResult,
      witness,
      witnessId: witness_id
    }
  }

  return (
    <div>
      {witness && (
        <QualityGateDisplay
          witness={witness}
          confidence={witness.confidence_score}
          confidenceBand={witness.confidence_band}
          kappaGatePassed={witness.kappa_gate_passed}
          taskCriticality={witness.task_criticality}
        />
      )}
    </div>
  )
}
```

### **Example 4: Complete Integration (All Systems)**

```typescript
import { AetherChat } from './components/aether-chat'
import { useICIP } from '../hooks/useICIP' // Nova
import { useVIF, useCMC, useTCS } from '../hooks/useAIMOS' // Alex
import { mcpService } from '../services/MCPService' // Alex

function CompleteAetherChat() {
  // Nova's ICIP
  const { generateFunction, generating } = useICIP()
  
  // Alex's Backend
  const { trackConfidence } = useVIF()
  const { storeAtom } = useCMC()
  const { addEntry } = useTCS()

  const handleCodeGeneration = async (
    type: 'function' | 'class' | 'test',
    prompt: string,
    language?: string
  ) => {
    try {
      // Generate code (Nova)
      const codeResult = await generateFunction(prompt, language)
      
      // Track confidence (Alex)
      const { witness_id, witness } = await trackConfidence(
        `Code generation: ${type}`,
        codeResult.confidence,
        [],
        `Generated ${type} in ${language}`
      )

      // Store in CMC (Alex)
      await storeAtom(codeResult.generated_code, 'code', {
        type,
        language,
        witness_id
      })

      // Add timeline entry (Alex)
      await addEntry({
        prompt_id: `code_gen_${Date.now()}`,
        context_index: { type, language, prompt },
        summary: `Generated ${type} code`,
        confidence_metrics: { confidence: codeResult.confidence }
      })

      return {
        ...codeResult,
        witness,
        witnessId: witness_id
      }
    } catch (error) {
      // Error handling with ErrorDisplay
      throw error
    }
  }

  return (
    <AetherChat
      onCodeGenerate={handleCodeGeneration}
    />
  )
}
```

---

## 🧪 **Testing Integration**

### **Test Code Generation Flow**

```typescript
// Test CodeGenerationInput
<CodeGenerationInput
  onGenerate={async (type, prompt, language) => {
    console.log('Generating:', type, prompt, language)
    // Mock or real ICIP call
  }}
  generating={false}
/>

// Test CodeBlockRenderer
<CodeBlockRenderer
  result={{
    generated_code: 'function test() { return "hello" }',
    explanation: 'Test function',
    confidence: 0.85,
    language: 'typescript'
  }}
  onExecute={() => console.log('Execute clicked')}
/>
```

### **Test Quality Gate Flow**

```typescript
// Test QualityGateDisplay
<QualityGateDisplay
  confidence={0.92}
  confidenceBand="A"
  kappaGatePassed={true}
  kappaThreshold={0.85}
  taskCriticality="important"
/>

// Test ConfidenceDisplay
<ConfidenceDisplay
  confidence={0.92}
  confidenceBand="A"
  previousConfidence={0.88}
  showTrend={true}
/>
```

---

## 📋 **Integration Checklist**

### **Nova's Checklist:**
- [ ] Implement `useICIP()` hook matching interface in CodeGenerationInput
- [ ] Implement code execution service matching CodeExecutionUI interface
- [ ] Test code generation with all types (function, class, test, etc.)
- [ ] Test code execution with different languages
- [ ] Verify CMC storage integration
- [ ] Verify VIF confidence tracking integration
- [ ] Verify TCS timeline integration

### **Alex's Checklist:**
- [ ] Replace mock data in all AIM-OS hooks with real API calls
- [ ] Test error handling with real network errors
- [ ] Test error handling with real timeout errors
- [ ] Test error handling with real API errors
- [ ] Verify VIF witness creation and retrieval
- [ ] Verify quality gate calculations
- [ ] Test confidence tracking end-to-end
- [ ] Verify CMC storage and retrieval
- [ ] Verify TCS timeline entries

---

**Status:** Ready for Integration  
**Last Updated:** 2025-01-27

