# PLIx Compiler for APOE

**Purpose:** Compile PLIx intent (CNL) to APOE ACL execution plans.

**Status:** Phase 0 - Language Bridge Implementation

---

## 🔗 **Language Bridge**

### **Architecture:**

```
PLIx Text (CNL)
    ↓
TypeScript Parser (Node.js subprocess)
    ↓
JSON AST
    ↓
Python Bridge (plix_parser_bridge.py)
    ↓
Python PLIxIntent
    ↓
PLIx→ACL Compiler
    ↓
APOE ACL Plan
```

### **Usage:**

```python
from apoe.plix_compiler import parse_plix

plix_text = """
ask ent:room/meeting
  act:reserve
  requires con:available == True
  ensures con:reserved == True
  plan [
    task check := api.check_room()
  ]
"""

intent = parse_plix(plix_text)
print(intent.entity)  # "room/meeting"
```

---

## 📊 **Components**

### **Implemented:**
- ✅ `cli-json.ts` - TypeScript CLI with JSON output
- ✅ `plix_parser_bridge.py` - Python bridge with caching
- ✅ `tests/test_plix_parser_bridge.py` - Bridge tests

### **Pending:**
- ⏳ `plix_to_acl_compiler.py` - Main compiler (Phase 1)
- ⏳ `purity_checker.py` - Purity validation (Phase 1)
- ⏳ `compensation_generator.py` - Compensation logic (Phase 1)
- ⏳ `retry_policy_generator.py` - Retry policies (Phase 1)

---

## 🧪 **Testing**

```bash
# Test bridge
pytest packages/apoe/plix_compiler/tests/test_plix_parser_bridge.py -v
```

---

**Status:** Language bridge complete, ready for compiler implementation 💙

