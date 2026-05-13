# Critical Gap 1: Language Boundary Design

**Date:** 2025-01-27  
**Status:** ⏳ **DESIGNING**  
**Priority:** 🔴 **CRITICAL** - Blocks Phase 1  
**Estimated Time:** 2-3 hours

---

## 🎯 **PROBLEM STATEMENT**

**Challenge:** PLIx parser is TypeScript (Node.js), APOE is Python. How do they communicate?

**Current Planning:** "Call TypeScript parser via subprocess" (mentioned but not designed)

**Why Critical:** Can't implement compiler without knowing how to get PLIx AST from parser.

---

## 🔍 **DESIGN OPTIONS**

### **Option 1: Subprocess + JSON (RECOMMENDED)**

**Architecture:**
```python
# Python side (APOE)
import subprocess
import json

def parse_plix(text: str) -> PLIxIntent:
    """Parse PLIx text using TypeScript parser"""
    
    # Call Node.js parser
    result = subprocess.run(
        ["node", "packages/plix/dist/cli.js", "parse", "--json", "-"],
        input=text.encode('utf-8'),
        capture_output=True,
        check=True,
        timeout=30
    )
    
    # Parse JSON output
    ast_json = json.loads(result.stdout)
    
    # Convert to Python structures
    return convert_ast_to_python(ast_json)
```

**TypeScript side (PLIx):**
```typescript
// packages/plix/src/cli.ts

if (args.includes('--json')) {
  const parser = new PLIXParser();
  const stdin = await readStdin();
  const result = parser.parse(stdin);
  
  if (result.errors.length > 0) {
    console.error(JSON.stringify({
      success: false,
      errors: result.errors
    }));
    process.exit(1);
  }
  
  console.log(JSON.stringify({
    success: true,
    intent: result.intent
  }));
}
```

**Pros:**
- ✅ Simple to implement
- ✅ Language-agnostic (just JSON)
- ✅ No additional dependencies
- ✅ Works locally and in containers

**Cons:**
- ⚠️ Subprocess overhead (~50ms per parse)
- ⚠️ Requires Node.js installed
- ⚠️ Error handling across process boundary

**Performance:**
- Parse time: ~100ms (50ms subprocess + 50ms parsing)
- Acceptable for interactive use
- Can be cached by intent hash

**Error Handling:**
```python
try:
    result = subprocess.run(...)
except subprocess.CalledProcessError as e:
    # Parser returned non-zero (parse errors)
    error_json = json.loads(e.stderr)
    raise PLIxParseError(error_json['errors'])
except subprocess.TimeoutExpired:
    raise PLIxParseError("Parser timeout after 30s")
except FileNotFoundError:
    raise PLIxParseError("Node.js not found - please install Node.js")
```

---

### **Option 2: HTTP API Server**

**Architecture:**
```python
# Start PLIx parser as HTTP service
# POST http://localhost:8080/parse with PLIx text
# Returns JSON AST

import requests

def parse_plix(text: str) -> PLIxIntent:
    response = requests.post(
        "http://localhost:8080/parse",
        json={"text": text},
        timeout=5
    )
    return convert_ast_to_python(response.json())
```

**Pros:**
- ✅ Lower latency (no subprocess spawn)
- ✅ Connection pooling
- ✅ Can be deployed separately

**Cons:**
- ⚠️ Requires service management
- ⚠️ More complex deployment
- ⚠️ Network dependency

**Not Recommended for v0.1** - Adds complexity

---

### **Option 3: Py_mini_racer (Embedded V8)**

**Architecture:**
```python
from py_mini_racer import MiniRacer

# Embed PLIx parser JavaScript in Python
ctx = MiniRacer()
ctx.eval(plix_parser_js_bundle)
ast = ctx.call('parse', plix_text)
```

**Pros:**
- ✅ No subprocess overhead
- ✅ No Node.js required
- ✅ Faster (embedded)

**Cons:**
- ⚠️ Complex setup (bundle PLIx parser)
- ⚠️ Harder to debug
- ⚠️ Version management tricky

**Not Recommended for v0.1** - Too complex

---

## ✅ **RECOMMENDED SOLUTION: Option 1 (Subprocess + JSON)**

### **Implementation Plan:**

**Step 1: Create PLIx CLI JSON Mode**
```bash
# packages/plix/src/cli.ts enhancement
# Add --json flag for machine-readable output
```

**Step 2: Create Python Bridge Module**
```python
# packages/apoe/plix_compiler/plix_parser_bridge.py
# Implements parse_plix() using subprocess
```

**Step 3: Add Error Handling**
```python
# Handle: parse errors, timeouts, Node.js missing
# Provide clear error messages with setup instructions
```

**Step 4: Add Caching**
```python
# Cache parsed intents by hash (avoid re-parsing)
# TTL: 1 hour
```

**Step 5: Test Bridge**
```python
# Test successful parse
# Test parse errors propagation
# Test timeout handling
# Test Node.js missing scenario
```

---

## 📊 **BRIDGE SPECIFICATION**

### **Input/Output Contract:**

**Input (stdin):**
```
PLIx intent text (CNL)
```

**Output (stdout) - Success:**
```json
{
  "success": true,
  "intent": {
    "speechAct": "ask",
    "entity": "room/meeting",
    "action": "reserve",
    "contract": {
      "preconditions": [...],
      "postconditions": [...]
    },
    "plan": {
      "steps": [...]
    }
  }
}
```

**Output (stderr) - Failure:**
```json
{
  "success": false,
  "errors": [
    {
      "line": 5,
      "column": 10,
      "message": "Unexpected token",
      "code": "PARSE_ERROR"
    }
  ]
}
```

### **Performance Specification:**

- **Latency:** < 200ms for typical intent (10-20 lines)
- **Throughput:** Can be cached (same intent parsed once)
- **Reliability:** 99.9% success rate (assuming valid input)

### **Error Scenarios:**

| Error | Cause | Handling |
|-------|-------|----------|
| Parse Error | Invalid PLIx syntax | Return structured errors |
| Timeout | Complex intent | Increase timeout or simplify |
| Node.js Missing | Environment issue | Clear setup instructions |
| JSON Decode Error | Parser bug | Log and raise exception |

---

## 🧪 **VALIDATION**

### **Test Plan:**

```python
def test_bridge_successful_parse():
    """Test successful parse"""
    text = "ask ent:test act:test requires con:x > 0 plan []"
    intent = parse_plix(text)
    assert intent.entity == "test"

def test_bridge_parse_error():
    """Test parse error handling"""
    text = "invalid plix syntax {{"
    with pytest.raises(PLIxParseError) as exc:
        parse_plix(text)
    assert "parse error" in str(exc).lower()

def test_bridge_timeout():
    """Test timeout handling"""
    # Create intent that takes >30s to parse
    # (Would need to mock for testing)

def test_bridge_node_missing():
    """Test Node.js not installed"""
    # Mock subprocess.run to raise FileNotFoundError
```

---

## ✅ **GAP 1 RESOLUTION**

**Status:** DESIGNED ✅

**Solution:** Subprocess + JSON bridge with caching and error handling

**Implementation Required:**
1. Enhance PLIx CLI with --json flag (~1 hour)
2. Create Python bridge module (~1 hour)
3. Add tests (~30 minutes)

**Total Time:** ~2.5 hours

**Confidence:** 0.90 (high confidence this will work)

**Blocks Removed:** Phase 1 can now proceed

---

**Next: Gap 2 (APOE Models) and Gap 3 (VIF Schema)** 💙

