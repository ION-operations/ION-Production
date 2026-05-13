# Chapter 48: CNL Compiler Implementation

**Part:** V - Implementation  
**Chapter:** 48  
**Target Word Count:** 2,500-3,000 words  
**Status:** ✅ **COMPLETE** (Unified Textbook v1.0)

---

## Section 48.1: Parser Design

The CNL parser transforms human-readable CNL text into PLIx AST (Abstract Syntax Tree), enabling automatic contract generation from natural language intent expression.

**Parser Architecture**

CNL parser architecture:

```typescript
class CNLParser {
  // Lexical analysis: CNL text → tokens
  tokenize(cnl: string): Token[];
  
  // Syntax analysis: tokens → AST
  parse(tokens: Token[]): AST;
  
  // Semantic analysis: AST → validated AST
  validate(ast: AST): ValidationResult;
  
  // Contract generation: AST → PLIx contract
  generateContract(ast: AST): PLIxContract;
}
```

Parser stages:
1. **Lexical Analysis:** Tokenize CNL into keywords, identifiers, values
2. **Syntax Analysis:** Parse tokens into abstract syntax tree
3. **Semantic Analysis:** Validate AST and resolve references
4. **Contract Generation:** Generate formal contract from AST

**Lexer Implementation**

Lexer tokenizes CNL:

```typescript
interface Token {
  type: 'INTENT_KEYWORD' | 'TASK_KEYWORD' | 'ENTITY_KEYWORD' | 'TAG' | 'IDENTIFIER' | 'STRING' | 'NUMBER' | 'COLON' | 'EQUALS' | 'COMMA' | 'NEWLINE';
  value: string;
  line: number;
  column: number;
}

function tokenize(cnl: string): Token[] {
  const tokens: Token[] = [];
  const lines = cnl.split('\n');
  
  for (let lineNum = 0; lineNum < lines.length; lineNum++) {
    const line = lines[lineNum];
    let column = 0;
    
    // Skip empty lines
    if (line.trim() === '') continue;
    
    // Entity keyword (tag-based)
    if (line.startsWith('Entity:')) {
      tokens.push({ type: 'ENTITY_KEYWORD', value: 'Entity', line: lineNum, column });
      column += 7;
      tokens.push({ type: 'COLON', value: ':', line: lineNum, column });
      column += 1;
      const entityTag = line.substring(8).trim();
      // Validate tag format: plix://namespace/path
      if (entityTag.startsWith('plix://')) {
        tokens.push({ type: 'TAG', value: entityTag, line: lineNum, column });
      } else {
        // Invalid tag format - will be caught in validation
        tokens.push({ type: 'STRING', value: entityTag, line: lineNum, column });
      }
      continue;
    }
    
    // Intent keyword
    if (line.startsWith('Intent:')) {
      tokens.push({ type: 'INTENT_KEYWORD', value: 'Intent', line: lineNum, column });
      column += 7;
      tokens.push({ type: 'COLON', value: ':', line: lineNum, column });
      column += 1;
      const intentText = line.substring(8).trim();
      tokens.push({ type: 'STRING', value: intentText, line: lineNum, column });
      continue;
    }
    
    // Task keyword
    const taskMatch = line.match(/^Task\s+(\w+):/);
    if (taskMatch) {
      tokens.push({ type: 'TASK_KEYWORD', value: 'Task', line: lineNum, column });
      column += 4;
      tokens.push({ type: 'IDENTIFIER', value: taskMatch[1], line: lineNum, column: column + 1 });
      column += taskMatch[1].length + 1;
      tokens.push({ type: 'COLON', value: ':', line: lineNum, column });
      continue;
    }
    
    // Action line
    if (line.trim().startsWith('Action:')) {
      tokens.push({ type: 'IDENTIFIER', value: 'Action', line: lineNum, column: line.indexOf('Action') });
      const actionValue = line.substring(line.indexOf(':') + 1).trim();
      tokens.push({ type: 'IDENTIFIER', value: actionValue, line: lineNum, column: line.indexOf(':') + 2 });
    }
    
    // Params line
    if (line.trim().startsWith('Params:')) {
      tokens.push({ type: 'IDENTIFIER', value: 'Params', line: lineNum, column: line.indexOf('Params') });
      // Parse param list: key=value, key2=value2
      const paramsText = line.substring(line.indexOf(':') + 1).trim();
      parseParams(paramsText, tokens, lineNum);
    }
    
    // ... more tokenization rules
  }
  
  return tokens;
}
```

Lexer converts CNL text into tokens, enabling syntax analysis.

**Parser Implementation**

Parser builds AST from tokens:

```typescript
interface AST {
  intent: string | null;
  entity?: string;  // Entity tag (plix://...)
  tasks: TaskAST[];
  constraints: string[];
  evidence: {
    required: string[];
    produce: string[];
  };
}

interface TaskAST {
  id: string;
  action: string;
  entityTag?: string;  // Entity tag for this task
  capabilityTag?: string;  // Capability tag for this task
  params: Record<string, any>;
  depends_on: string[];
  retry?: RetryAST;
  compensate?: string;
}

function parse(tokens: Token[]): AST {
  const ast: AST = {
    intent: null,
    tasks: [],
    constraints: [],
    evidence: { required: [], produce: [] }
  };
  
  let i = 0;
  
  // Parse entity tag (optional)
  if (i < tokens.length && tokens[i].type === 'ENTITY_KEYWORD') {
    i++; // Skip 'Entity'
    i++; // Skip ':'
    if (tokens[i].type === 'TAG') {
      ast.entity = tokens[i].value;  // Store entity tag
    }
    i++;
  }
  
  // Parse intent
  while (i < tokens.length && tokens[i].type === 'INTENT_KEYWORD') {
    i++; // Skip 'Intent'
    i++; // Skip ':'
    ast.intent = tokens[i].value;
    i++;
  }
  
  // Parse tasks
  while (i < tokens.length) {
    if (tokens[i].type === 'TASK_KEYWORD') {
      const task = parseTask(tokens, i);
      ast.tasks.push(task.ast);
      i = task.nextIndex;
    } else if (tokens[i].value === 'Constraints') {
      i = parseConstraints(tokens, i, ast);
    } else if (tokens[i].value === 'Evidence') {
      i = parseEvidence(tokens, i, ast);
    } else {
      i++;
    }
  }
  
  return ast;
}

function parseTask(tokens: Token[], startIndex: number): { ast: TaskAST; nextIndex: number } {
  let i = startIndex;
  const task: TaskAST = {
    id: '',
    action: '',
    params: {},
    depends_on: []
  };
  
  // Parse task ID
  if (tokens[i].type === 'TASK_KEYWORD') {
    i++;
    task.id = tokens[i].value; // Task identifier
    i += 2; // Skip identifier and ':'
  }
  
  // Parse task body
  while (i < tokens.length && tokens[i].type !== 'TASK_KEYWORD' && tokens[i].value !== 'Constraints' && tokens[i].value !== 'Evidence') {
    if (tokens[i].value === 'Action') {
      i += 2; // Skip 'Action' and ':'
      task.action = tokens[i].value;
      i++;
    } else if (tokens[i].value === 'Entity') {
      i += 2; // Skip 'Entity' and ':'
      if (tokens[i].type === 'TAG') {
        task.entityTag = tokens[i].value;  // Store entity tag
      }
      i++;
    } else if (tokens[i].value === 'Capability') {
      i += 2; // Skip 'Capability' and ':'
      if (tokens[i].type === 'TAG') {
        task.capabilityTag = tokens[i].value;  // Store capability tag
      }
      i++;
    } else if (tokens[i].value === 'Params') {
      i += 2; // Skip 'Params' and ':'
      task.params = parseParamList(tokens, i);
      i = findNextLine(tokens, i);
    } else if (tokens[i].value === 'Depends') {
      i += 2; // Skip 'Depends' and ':'
      task.depends_on = parseIdentifierList(tokens, i);
      i = findNextLine(tokens, i);
    } else if (tokens[i].value === 'Compensate') {
      i += 2; // Skip 'Compensate' and ':'
      task.compensate = tokens[i].value;
      i++;
    } else if (tokens[i].value === 'Retry') {
      i += 2; // Skip 'Retry' and ':'
      task.retry = parseRetry(tokens, i);
      i = findNextLine(tokens, i);
    } else {
      i++;
    }
  }
  
  return { ast: task, nextIndex: i };
}
```

Parser builds AST from tokens, representing CNL structure.

**Semantic Validation**

Semantic validation ensures AST correctness:

```typescript
interface ValidationResult {
  valid: boolean;
  errors: string[];
}

function validate(ast: AST): ValidationResult {
  const errors: string[] = [];
  
  // Validate intent exists
  if (!ast.intent || ast.intent.trim() === '') {
    errors.push('Intent is required');
  }
  
  // Validate entity tag format if present
  if (ast.entity && !ast.entity.startsWith('plix://')) {
    errors.push(`Invalid entity tag format: ${ast.entity}. Must start with 'plix://'`);
  }
  
  // Validate task entity tags
  for (const task of ast.tasks) {
    if (task.entityTag && !task.entityTag.startsWith('plix://')) {
      errors.push(`Invalid entity tag format in task ${task.id}: ${task.entityTag}. Must start with 'plix://'`);
    }
    if (task.capabilityTag && !task.capabilityTag.startsWith('plix://')) {
      errors.push(`Invalid capability tag format in task ${task.id}: ${task.capabilityTag}. Must start with 'plix://'`);
    }
  }
  
  // Validate tasks exist
  if (ast.tasks.length === 0) {
    errors.push('At least one task is required');
  }
  
  // Validate task IDs are unique
  const taskIds = new Set<string>();
  for (const task of ast.tasks) {
    if (taskIds.has(task.id)) {
      errors.push(`Duplicate task ID: ${task.id}`);
    }
    taskIds.add(task.id);
  }
  
  // Validate dependencies
  for (const task of ast.tasks) {
    for (const dep of task.depends_on) {
      if (!ast.tasks.find(t => t.id === dep)) {
        errors.push(`Task ${task.id} depends on unknown task: ${dep}`);
      }
    }
  }
  
  // Validate compensation references
  for (const task of ast.tasks) {
    if (task.compensate) {
      if (!ast.tasks.find(t => t.id === task.compensate)) {
        errors.push(`Task ${task.id} compensates with unknown task: ${task.compensate}`);
      }
    }
  }
  
  // Validate circular dependencies
  const circularDeps = detectCircularDependencies(ast.tasks);
  if (circularDeps.length > 0) {
    errors.push(`Circular dependencies detected: ${circularDeps.join(', ')}`);
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}
```

Semantic validation ensures contracts are well-formed before generation.

**Parser Benefits**

Parser design provides:

- **Automatic Translation:** CNL → Contract translation
- **Syntax Validation:** CNL syntax validation
- **Semantic Validation:** Contract correctness validation
- **Error Reporting:** Helpful error messages

These benefits enable reliable CNL processing, ensuring contracts are correctly generated from human-readable CNL.

---

## Section 48.2: AST to Contract Generation

AST to contract generation transforms validated AST into formal PLIx contracts, preserving intent semantics while enabling verification.

**Contract Generation**

Contract generation from AST:

```typescript
function generateContract(ast: AST): PLIxContract {
  // Generate contract from AST with tag resolution
  const contract = new PLIxContract({
    intent: ast.intent!,
    entity: ast.entity,  // Include entity tag
    contract: {
      pre: extractPreconditions(ast),
      post: extractPostconditions(ast)
    },
    tasks: ast.tasks.map(task => generateTask(task)),
    constraints: ast.constraints,
    evidence: ast.evidence
  });
  
  return contract;
}

function generateTask(taskAST: TaskAST): Task {
  return {
    id: taskAST.id,
    action: taskAST.action,
    entityTag: taskAST.entityTag,  // Include entity tag
    capabilityTag: taskAST.capabilityTag,  // Include capability tag
    params: taskAST.params,
    depends_on: taskAST.depends_on,
    retry: taskAST.retry ? {
      max_attempts: taskAST.retry.max,
      backoff: taskAST.retry.backoff,
      backoff_ms: taskAST.retry.ms
    } : undefined,
    compensate: taskAST.compensate
  };
}
```

Contract generation transforms AST into formal contracts, preserving semantics.

**Precondition Extraction**

Precondition extraction:

```typescript
function extractPreconditions(ast: AST): string[] {
  const preconditions: string[] = [];
  
  // Extract from task dependencies
  for (const task of ast.tasks) {
    for (const dep of task.depends_on) {
      const depTask = ast.tasks.find(t => t.id === dep);
      if (depTask) {
        // Add dependency precondition
        preconditions.push(`${depTask.id}_completed == true`);
      }
    }
  }
  
  // Extract from constraints
  for (const constraint of ast.constraints) {
    if (constraint.includes('required') || constraint.includes('must')) {
      preconditions.push(constraint);
    }
  }
  
  return preconditions;
}
```

Precondition extraction identifies what must be true before intent achievement.

**Postcondition Extraction**

Postcondition extraction:

```typescript
function extractPostconditions(ast: AST): string[] {
  const postconditions: string[] = [];
  
  // Extract from intent
  if (ast.intent?.includes('book')) {
    postconditions.push('room_reserved == true');
  }
  if (ast.intent?.includes('reserve')) {
    postconditions.push('reservation_created == true');
  }
  
  // Extract from evidence produce
  for (const evidence of ast.evidence.produce) {
    postconditions.push(`${evidence}_produced == true`);
  }
  
  return postconditions;
}
```

Postcondition extraction identifies what must be true after intent achievement.

**Contract Generation Benefits**

Contract generation provides:

- **Semantic Preservation:** Maintains intent semantics through generation
- **Formal Contracts:** Generates verifiable contracts
- **Precondition/Postcondition:** Extracts pre/post conditions automatically
- **Task Mapping:** Maps AST tasks to contract tasks

These benefits enable automatic contract generation from CNL, bridging human intent and formal contracts.

---

## Section 48.3: Error Handling

Error handling provides helpful error messages, enabling contract debugging and correction.

**Error Types**

Parser error types:

```typescript
class ParseError extends Error {
  constructor(
    public message: string,
    public line: number,
    public column: number,
    public context: string,
    public errorType: 'syntax' | 'semantic' | 'validation'
  ) {
    super(message);
  }
}

class SyntaxError extends ParseError {
  constructor(message: string, line: number, column: number, context: string) {
    super(message, line, column, context, 'syntax');
  }
}

class SemanticError extends ParseError {
  constructor(message: string, line: number, column: number, context: string) {
    super(message, line, column, context, 'semantic');
  }
}

class ValidationError extends ParseError {
  constructor(message: string, line: number, column: number, context: string) {
    super(message, line, column, context, 'validation');
  }
}
```

Error types enable specific error handling and reporting.

**Error Reporting**

Error reporting provides actionable feedback:

```typescript
function reportErrors(errors: ParseError[], cnl: string): void {
  console.error('CNL Parse Errors:');
  
  for (const error of errors) {
    console.error(`\n${error.errorType.toUpperCase()} Error at line ${error.line}, column ${error.column}:`);
    console.error(`  ${error.message}`);
    
    // Show context
    const lines = cnl.split('\n');
    if (error.line < lines.length) {
      console.error(`  Context: ${lines[error.line]}`);
      console.error(`  ${' '.repeat(error.column)}^`);
    }
  }
}

function parseWithErrorHandling(cnl: string): PLIxContract | null {
  try {
    const tokens = tokenize(cnl);
    const ast = parse(tokens);
    const validation = validate(ast);
    
    if (!validation.valid) {
      const errors = validation.errors.map(err => 
        new ValidationError(err, 0, 0, cnl)
      );
      reportErrors(errors, cnl);
      return null;
    }
    
    return generateContract(ast);
  } catch (error) {
    if (error instanceof ParseError) {
      reportErrors([error], cnl);
    } else {
      console.error(`Unexpected error: ${error}`);
    }
    return null;
  }
}
```

Error reporting provides actionable feedback, enabling contract debugging.

**Error Recovery**

Error recovery attempts to fix common errors:

```typescript
function recoverFromErrors(cnl: string, errors: ParseError[]): string {
  let recovered = cnl;
  
  for (const error of errors) {
    if (error.errorType === 'syntax') {
      // Attempt syntax recovery
      if (error.message.includes('missing colon')) {
        // Add missing colon
        const lines = recovered.split('\n');
        if (error.line < lines.length) {
          lines[error.line] = lines[error.line] + ':';
          recovered = lines.join('\n');
        }
      }
    }
  }
  
  return recovered;
}
```

Error recovery attempts to fix common errors automatically, improving parser usability.

**Error Handling Benefits**

Error handling provides:

- **Actionable Feedback:** Helpful error messages with context
- **Error Types:** Specific error types for different failure modes
- **Error Recovery:** Automatic recovery from common errors
- **Debugging Support:** Context and location information

These benefits enable effective contract debugging and correction.

---

## Section 48.4: Testing Strategies

Testing strategies ensure parser correctness, reliability, and robustness.

**Unit Tests**

Unit tests for parser components:

```typescript
describe('CNLParser', () => {
  describe('tokenize', () => {
    it('tokenizes intent keyword', () => {
      const tokens = tokenize('Intent: Book a room');
      expect(tokens[0].type).toBe('INTENT_KEYWORD');
      expect(tokens[0].value).toBe('Intent');
    });
    
    it('tokenizes task keyword', () => {
      const tokens = tokenize('Task reserve_room:');
      expect(tokens[0].type).toBe('TASK_KEYWORD');
      expect(tokens[1].type).toBe('IDENTIFIER');
      expect(tokens[1].value).toBe('reserve_room');
    });
    
    it('tokenizes entity tag', () => {
      const tokens = tokenize('Entity: plix://room/meeting_room');
      expect(tokens[0].type).toBe('ENTITY_KEYWORD');
      expect(tokens[2].type).toBe('TAG');
      expect(tokens[2].value).toBe('plix://room/meeting_room');
    });
  });
  
  describe('parse', () => {
    it('parses minimal contract', () => {
      const cnl = `Intent: Book a room
Task reserve:
  Action: api.reserve_room`;
      
      const contract = parser.parse(cnl);
      expect(contract.intent).toBe('Book a room');
      expect(contract.tasks).toHaveLength(1);
      expect(contract.tasks[0].id).toBe('reserve');
    });
    
    it('parses contract with entity tag', () => {
      const cnl = `Entity: plix://room/meeting_room
Intent: Book a room
Task reserve:
  Action: api.reserve_room
  Entity: plix://room/meeting_room`;
      
      const contract = parser.parse(cnl);
      expect(contract.entity).toBe('plix://room/meeting_room');
      expect(contract.tasks[0].entityTag).toBe('plix://room/meeting_room');
    });
  });
  
  describe('validate', () => {
    it('validates dependencies', () => {
      const cnl = `Intent: Book a room
Task reserve:
  Action: api.reserve_room
  Depends: unknown_task`;
      
      const validation = parser.validate(parser.parse(parser.tokenize(cnl)));
      expect(validation.valid).toBe(false);
      expect(validation.errors).toContain('depends on unknown task');
    });
    
    it('validates entity tag format', () => {
      const cnl = `Entity: invalid_tag
Intent: Book a room`;
      
      const validation = parser.validate(parser.parse(parser.tokenize(cnl)));
      expect(validation.valid).toBe(false);
      expect(validation.errors.some(e => e.includes('Invalid entity tag format'))).toBe(true);
    });
  });
});
```

Unit tests ensure parser components work correctly in isolation.

**Integration Tests**

Integration tests for complete parsing:

```typescript
describe('CNLParser Integration', () => {
  it('parses complete contract', () => {
    const cnl = `
Entity: plix://room/meeting_room
Intent: Book a meeting room on 2025-12-01 for 2h.

Task check_availability:
  Action: api.check_room_availability
  Entity: plix://room/meeting_room
  Params: date=2025-12-01, duration=2h
  Retry: max=3, backoff=exponential, backoff_ms=1000

Task reserve_room:
  Action: api.reserve_room
  Entity: plix://room/meeting_room
  Params: room_id=\${check_availability.room_id}, duration=2h
  Depends: check_availability
  Compensate: cancel_reservation

Constraints:
  duration <= 4h
  calendar_conflicts == none

Evidence Required:
  calendar.open_slots

Evidence Produce:
  reservation.record
`;
    
    const contract = parser.parse(cnl);
    expect(contract.entity).toBe('plix://room/meeting_room');
    expect(contract.intent).toBe('Book a meeting room on 2025-12-01 for 2h.');
    expect(contract.tasks).toHaveLength(2);
    expect(contract.tasks[0].entityTag).toBe('plix://room/meeting_room');
    expect(contract.tasks[1].entityTag).toBe('plix://room/meeting_room');
    expect(contract.constraints).toHaveLength(2);
    expect(contract.evidence.required).toContain('calendar.open_slots');
    expect(contract.evidence.produce).toContain('reservation.record');
  });
});
```

Integration tests ensure complete parsing works end-to-end.

**Error Handling Tests**

Error handling tests:

```typescript
describe('Error Handling', () => {
  it('handles missing intent', () => {
    const cnl = `Task reserve:
  Action: api.reserve_room`;
    
    expect(() => parser.parse(cnl)).toThrow('Intent is required');
  });
  
  it('handles circular dependencies', () => {
    const cnl = `Intent: Book a room
Task a:
  Action: api.a
  Depends: b
Task b:
  Action: api.b
  Depends: a`;
    
    const validation = parser.validate(parser.parse(parser.tokenize(cnl)));
    expect(validation.valid).toBe(false);
    expect(validation.errors.some(e => e.includes('circular'))).toBe(true);
  });
});
```

Error handling tests ensure parser handles errors gracefully.

**Testing Benefits**

Testing strategies provide:

- **Correctness:** Ensures parser works correctly
- **Reliability:** Ensures parser handles edge cases
- **Robustness:** Ensures parser recovers from errors
- **Maintainability:** Tests document expected behavior

These benefits enable reliable CNL processing, ensuring contracts are correctly generated.

---

## Chapter 48 Summary

CNL compiler implementation transforms human-readable CNL into formal PLIx contracts through parser design, AST to contract generation, error handling, and testing strategies. Parser design provides lexical analysis **with tag tokenization**, syntax analysis **with tag parsing**, semantic validation **with tag format validation**, and contract generation **with tag-based entity references**. AST to contract generation preserves intent semantics **with tag-based entity references** while enabling verification. Error handling provides actionable feedback for debugging **including tag validation errors**. Testing strategies ensure correctness, reliability, and robustness **including tag parsing and validation**.

**Tags enable canonical identity** throughout CNL compilation: entity tags (`plix://room/meeting_room`) are parsed from CNL, validated for format correctness, stored in AST, and included in generated contracts. Tags enable unambiguous entity references that survive technology changes, enabling intent-aware contract generation with canonical identity.

**Next:** Chapter 49 explores runtime implementation—durable execution, saga patterns, and recovery, showing how tags enable runtime execution.

---

**Word Count:** ~2,700 words  
**Status:** ✅ **COMPLETE** (Unified Textbook v1.0)  
**Cross-References:**
- Chapter 5: Tag System (tag format and components)
- Chapter 6: Three Surface Forms (CNL as Human-PLIX surface form)
- Chapter 15: Tag Registry (tag resolution process)

