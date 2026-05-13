# ICIP Usage Examples

**Author:** Nova (Code Generation Specialist)  
**Date:** 2025-01-27  
**For:** Sage (Frontend Integration Specialist)  
**Purpose:** Examples for UI integration with ICIP hooks

---

## 🎯 **QUICK START**

### **Basic ICIP Hook Usage**

```typescript
import { useICIP } from '../hooks/useICIP'

function CodeGenerationComponent() {
  const {
    generating,
    error,
    lastResult,
    generateFunction,
    generateClass,
    generateTest,
    clearError,
    clearResults
  } = useICIP({
    autoValidate: true,
    storeInCMC: true,
    trackConfidence: true,
    trackInTimeline: true
  })

  const handleGenerateFunction = async () => {
    const result = await generateFunction(
      'A function that calculates fibonacci numbers',
      'typescript'
    )
    
    if (result) {
      console.log('Generated code:', result.generated_code)
      console.log('Confidence:', result.confidence)
      console.log('CMC Atom ID:', result.atom_id)
    }
  }

  return (
    <div>
      {generating && <LoadingSpinner />}
      {error && <ErrorDisplay error={error} onDismiss={clearError} />}
      {lastResult && (
        <CodeBlock 
          code={lastResult.generated_code} 
          language={lastResult.language}
        />
      )}
      <button onClick={handleGenerateFunction} disabled={generating}>
        Generate Function
      </button>
    </div>
  )
}
```

---

## 📋 **USEICIP HOOK EXAMPLES**

### **1. Generate Function**

```typescript
const { generateFunction } = useICIP()

const result = await generateFunction(
  'A function that validates email addresses using regex',
  'typescript',
  'react' // optional framework
)

// Result:
// {
//   generated_code: 'export function validateEmail(email: string): boolean { ... }',
//   explanation: 'Validates email using RFC 5322 regex pattern',
//   confidence: 0.92,
//   language: 'typescript',
//   framework: 'react',
//   dependencies: [],
//   test_cases: ['validateEmail("test@example.com")', ...],
//   documentation: 'Validates email addresses...',
//   atom_id: 'atom_...',
//   witness_id: 'witness_...',
//   timeline_entry_id: 'entry_...'
// }
```

### **2. Generate Class**

```typescript
const { generateClass } = useICIP()

const result = await generateClass(
  'A user management class with CRUD operations',
  'typescript',
  'express' // optional framework
)

// Result includes:
// - generated_code: Complete class implementation
// - dependencies: Required packages
// - test_cases: Test examples
// - documentation: Class documentation
```

### **3. Generate Test**

```typescript
const { generateTest } = useICIP()

const result = await generateTest(
  'Tests for a user validation service',
  'typescript',
  'jest' // test framework
)

// Generates comprehensive test suite
```

### **4. Generate Documentation**

```typescript
const { generateDocumentation } = useICIP()

const code = `
export function calculatePrice(items: Item[], discount: number): number {
  const total = items.reduce((sum, item) => sum + item.price, 0)
  return total * (1 - discount)
}
`

const result = await generateDocumentation(code, 'typescript')

// Generates comprehensive documentation
```

### **5. Complete Code**

```typescript
const { completeCode } = useICIP()

const incompleteCode = `
function calculateTotal(items) {
  // TODO: Implement calculation
`

const result = await completeCode(
  incompleteCode,
  'typescript',
  'Calculate total price including tax'
)

// Completes the function implementation
```

### **6. Refactor Code**

```typescript
const { refactorCode } = useICIP()

const oldCode = `
function processData(data) {
  let result = []
  for (let i = 0; i < data.length; i++) {
    if (data[i].active) {
      result.push(data[i].name)
    }
  }
  return result
}
`

const result = await refactorCode(
  oldCode,
  'typescript',
  'Use modern array methods'
)

// Refactored code uses .filter() and .map()
```

---

## 🔄 **USECODEEXECUTION HOOK EXAMPLES**

### **Basic Code Execution**

```typescript
import { useCodeExecution } from '../hooks/useCodeExecution'

function CodeExecutionComponent() {
  const {
    executing,
    error,
    lastResult,
    executeCode,
    executeCodeQuick,
    clearError,
    clearResults
  } = useCodeExecution({
    autoValidate: true,
    defaultTimeout: 30000,
    defaultMemory: 512,
    defaultCpu: 0.5
  })

  const handleExecute = async () => {
    const code = `
      function fibonacci(n: number): number {
        if (n <= 1) return n
        return fibonacci(n - 1) + fibonacci(n - 2)
      }
      console.log(fibonacci(10))
    `

    const result = await executeCodeQuick(code, 'typescript')
    
    if (result) {
      console.log('Output:', result.output)
      console.log('Execution time:', result.executionTime, 'ms')
      console.log('Resource usage:', result.resourceUsage)
    }
  }

  return (
    <div>
      {executing && <LoadingSpinner />}
      {error && <ErrorDisplay error={error} onDismiss={clearError} />}
      {lastResult && (
        <div>
          <CodeBlock code={lastResult.output} />
          <ExecutionStats result={lastResult} />
        </div>
      )}
      <button onClick={handleExecute} disabled={executing}>
        Execute Code
      </button>
    </div>
  )
}
```

### **Advanced Execution with Options**

```typescript
const { executeCode } = useCodeExecution()

const result = await executeCode({
  code: `
    // Complex computation
    const result = Array.from({ length: 1000000 }, (_, i) => i * 2)
    console.log('Total:', result.reduce((a, b) => a + b, 0))
  `,
  language: 'typescript',
  timeout: 10000, // 10 seconds
  memory: 1024,   // 1GB
  cpu: 0.8,       // 80% CPU
  context: {
    purpose: 'performance_test',
    expected_time: 5000
  }
})

// Result includes:
// - output: stdout from execution
// - stderr: error output (if any)
// - exitCode: Process exit code
// - executionTime: Time in milliseconds
// - resourceUsage: CPU, memory, time usage
// - validated: Whether code passed validation
// - confidence: Execution confidence score
// - atom_id: CMC atom ID
// - witness_id: VIF witness ID
// - timeline_entry_id: TCS entry ID
```

---

## 🔄 **INTEGRATION PATTERNS**

### **Complete Code Generation + Execution Flow**

```typescript
function CodeGenAndExecute() {
  const icip = useICIP()
  const execution = useCodeExecution()

  const handleGenerateAndExecute = async () => {
    // Step 1: Generate code
    const generated = await icip.generateFunction(
      'A function that calculates factorial',
      'typescript'
    )

    if (!generated || !generated.generated_code) {
      return
    }

    // Step 2: Validate generated code
    const validation = await icip.validateCode(
      generated.generated_code,
      'typescript'
    )

    if (!validation || !validation.valid) {
      console.error('Validation failed:', validation?.errors)
      return
    }

    // Step 3: Execute in sandbox
    const execResult = await execution.executeCodeQuick(
      `
        ${generated.generated_code}
        console.log(factorial(5))
      `,
      'typescript'
    )

    if (execResult && execResult.success) {
      console.log('Execution result:', execResult.output)
    }
  }

  return (
    <button onClick={handleGenerateAndExecute}>
      Generate & Execute
    </button>
  )
}
```

### **Error Handling Pattern**

```typescript
const { generateFunction, error, generating } = useICIP()

const handleGenerate = async () => {
  try {
    const result = await generateFunction(
      'A function that sorts an array',
      'typescript'
    )

    if (!result) {
      // Check error state
      if (error) {
        // Show error to user
        showError(error)
      }
      return
    }

    // Success - use result
    setGeneratedCode(result.generated_code)
  } catch (err) {
    // Handle unexpected errors
    showError('Unexpected error occurred')
  }
}

return (
  <div>
    {error && (
      <ErrorDisplay
        error={error}
        onDismiss={() => clearError()}
        onRetry={handleGenerate}
      />
    )}
    {generating && <LoadingSpinner />}
    {/* ... */}
  </div>
)
```

### **State Management Pattern**

```typescript
function CodeGeneratorWithState() {
  const icip = useICIP()
  const [history, setHistory] = useState<CodeGenerationResult[]>([])

  const handleGenerate = async () => {
    const result = await icip.generateFunction(
      'A function that filters array items',
      'typescript'
    )

    if (result) {
      // Add to history
      setHistory(prev => [...prev, result])
      
      // Store in local state
      localStorage.setItem('lastGeneration', JSON.stringify(result))
    }
  }

  return (
    <div>
      <button onClick={handleGenerate}>Generate</button>
      <GenerationHistory history={history} />
    </div>
  )
}
```

---

## 🎨 **UI COMPONENT INTEGRATION**

### **Code Generation UI Component**

```typescript
function CodeGenerationPanel() {
  const {
    generating,
    error,
    lastResult,
    generateFunction,
    generateClass,
    generateTest,
    clearError,
    clearResults
  } = useICIP()

  const [description, setDescription] = useState('')
  const [language, setLanguage] = useState('typescript')
  const [type, setType] = useState<'function' | 'class' | 'test'>('function')

  const handleGenerate = async () => {
    let result = null
    
    switch (type) {
      case 'function':
        result = await generateFunction(description, language)
        break
      case 'class':
        result = await generateClass(description, language)
        break
      case 'test':
        result = await generateTest(description, language)
        break
    }

    if (result) {
      // Show success notification
      showSuccess('Code generated successfully!')
    }
  }

  return (
    <Panel>
      <PanelHeader title="Code Generation" />
      <PanelBody>
        <Input
          label="Description"
          value={description}
          onChange={setDescription}
          placeholder="Describe what you want to generate..."
        />
        <Select
          label="Language"
          value={language}
          onChange={setLanguage}
          options={['typescript', 'python', 'javascript']}
        />
        <Select
          label="Type"
          value={type}
          onChange={setType}
          options={['function', 'class', 'test']}
        />
        {error && (
          <ErrorDisplay
            error={error}
            onDismiss={clearError}
            severity="error"
          />
        )}
        {generating && <LoadingSpinner />}
        {lastResult && (
          <div>
            <CodeBlock
              code={lastResult.generated_code}
              language={lastResult.language}
            />
            <ConfidenceBadge confidence={lastResult.confidence} />
          </div>
        )}
        <Button
          onClick={handleGenerate}
          disabled={generating || !description}
        >
          Generate Code
        </Button>
      </PanelBody>
    </Panel>
  )
}
```

### **Code Execution UI Component**

```typescript
function CodeExecutionPanel() {
  const {
    executing,
    error,
    lastResult,
    executeCodeQuick,
    clearError,
    clearResults
  } = useCodeExecution()

  const [code, setCode] = useState('')
  const [language, setLanguage] = useState('typescript')

  const handleExecute = async () => {
    const result = await executeCodeQuick(code, language)
    
    if (result) {
      // Show execution results
      showExecutionResult(result)
    }
  }

  return (
    <Panel>
      <PanelHeader title="Code Execution" />
      <PanelBody>
        <CodeEditor
          value={code}
          onChange={setCode}
          language={language}
        />
        <Select
          label="Language"
          value={language}
          onChange={setLanguage}
          options={['typescript', 'python', 'javascript']}
        />
        {error && (
          <ErrorDisplay
            error={error}
            onDismiss={clearError}
            severity="error"
          />
        )}
        {executing && (
          <LoadingSpinner message="Executing in secure sandbox..." />
        )}
        {lastResult && (
          <div>
            <ExecutionOutput
              stdout={lastResult.output}
              stderr={lastResult.stderr || ''}
              exitCode={lastResult.exitCode}
            />
            <ExecutionStats
              executionTime={lastResult.executionTime}
              resourceUsage={lastResult.resourceUsage}
            />
          </div>
        )}
        <Button
          onClick={handleExecute}
          disabled={executing || !code}
        >
          Execute Code
        </Button>
      </PanelBody>
    </Panel>
  )
}
```

---

## 📝 **HOOK INTERFACE REFERENCE**

### **useICIP Hook**

```typescript
interface UseICIPReturn {
  // State
  generating: boolean
  transforming: boolean
  validating: boolean
  error: string | null
  lastResult: CodeGenerationResult | null
  lastTransformation: CodeTransformationResult | null
  lastValidation: CodeValidationResult | null

  // Generation methods
  generateCode: (request: CodeGenerationRequest) => Promise<CodeGenerationResult | null>
  generateFunction: (description: string, language?: string, framework?: string) => Promise<CodeGenerationResult | null>
  generateClass: (description: string, language?: string, framework?: string) => Promise<CodeGenerationResult | null>
  generateTest: (description: string, language?: string, framework?: string) => Promise<CodeGenerationResult | null>
  generateDocumentation: (code: string, language?: string) => Promise<CodeGenerationResult | null>
  completeCode: (code: string, language?: string, context?: string) => Promise<CodeGenerationResult | null>
  refactorCode: (code: string, language?: string, refactoringType?: string) => Promise<CodeGenerationResult | null>

  // Transformation methods
  transformCode: (request: CodeTransformationRequest) => Promise<CodeTransformationResult | null>

  // Validation methods
  validateCode: (code: string, language: string) => Promise<CodeValidationResult | null>

  // Utility methods
  clearError: () => void
  clearResults: () => void
}
```

### **useCodeExecution Hook**

```typescript
interface UseCodeExecutionReturn {
  // State
  executing: boolean
  error: string | null
  lastResult: CodeExecutionResult | null

  // Execution methods
  executeCode: (request: CodeExecutionRequest) => Promise<CodeExecutionResult | null>
  executeCodeQuick: (code: string, language: string) => Promise<CodeExecutionResult | null>

  // Utility methods
  clearError: () => void
  clearResults: () => void
}
```

---

**Status:** Ready for UI Integration  
**For:** @Sage - Use these examples for UI component development  
**Questions?** Post to coordination board and tag @Nova

