# 🚀 NL Tags Quick Start Guide

**Version:** 0.3.0  
**Goal:** Get started with NL tags in 5 minutes

---

## ⚡ **5-MINUTE QUICK START**

### **Step 1: Extract Your First Tag**

```python
from packages.nl_tags import NLTagParser

parser = NLTagParser()
tags = parser.parse_file("your_file.py")

for tag in tags:
    print(f"Tag: {tag.tag_text}")
    print(f"  Location: {tag.file_path}:{tag.line_start}")
    print(f"  Language: {tag.language}")
```

### **Step 2: Add a Tag to Your Code**

```python
# NL: Validate user authentication token
def validate_token(token: str) -> bool:
    if not token:
        return False
    # ... validation logic
    return True
```

### **Step 3: Use Registry for Management**

```python
from packages.nl_tags import NLTagRegistry

registry = NLTagRegistry()
tags = registry.register_tags_from_file("your_file.py")

# Get coverage stats
stats = registry.get_coverage_stats()
print(f"Total tags: {stats.total_tags}")
print(f"Coverage: {stats.coverage_percentage:.1f}%")
```

---

## 📝 **TAG FORMATS**

### **Simple Format (Easiest)**
```python
# NL: What this code does
def my_function():
    ...
```

### **Structured Format (More Powerful)**
```python
# NL_TAG: AUTH-001 | Authenticate user credentials | authenticate(user, password) | [VIF-001, TEST-AUTH-001]
def authenticate(user: str, password: str) -> bool:
    ...
```

**Benefits of Structured Format:**
- **Canonical ID:** Unique identifier that links across systems
- **SYNTAX_REF:** Enables structural validation (exact match with code)
- **Dependencies:** Tracks relationships to other tags/tests/docs

---

## ✅ **VALIDATION**

### **Automatic Validation**

Tags are automatically validated when registered:

```python
registry = NLTagRegistry()
tags = registry.register_tags_from_file("your_file.py")

# Tags now have validation results
for tag in tags:
    print(f"Tag: {tag.tag_text}")
    print(f"  Accuracy: {tag.accuracy_score}")
    print(f"  Structural Match: {tag.structural_match_score}")
    print(f"  Status: {tag.validation_status}")
```

### **Manual Validation**

```python
from packages.nl_tags import CombinedNLTagValidator

validator = CombinedNLTagValidator()
result = validator.validate_tag(tag, code_content)

print(f"Combined Score: {result.combined_score}")
print(f"Passes Threshold: {result.passes_threshold}")
print(f"Suggestions: {result.suggestions}")
```

---

## 🔗 **INTEGRATION WITH CMC**

### **Store Tags in CMC**

```python
from packages.nl_tags import NLTagRegistry
from packages.cmc_service.memory_store import MemoryStore

cmc_store = MemoryStore("./data")
registry = NLTagRegistry(cmc_store=cmc_store)

# Tags automatically stored when registered
tags = registry.register_tags_from_file("your_file.py")
```

### **Retrieve Tags from CMC**

```python
# Tags are automatically loaded from CMC on initialization
registry = NLTagRegistry(cmc_store=cmc_store)
tags = registry.get_tags_for_file("your_file.py")
```

---

## 📊 **COVERAGE STATISTICS**

### **Get Coverage Stats**

```python
registry = NLTagRegistry()

# Overall coverage
stats = registry.get_coverage_stats()
print(f"Total Files: {stats.total_files}")
print(f"Tagged Files: {stats.tagged_files}")
print(f"Total Tags: {stats.total_tags}")
print(f"Coverage: {stats.coverage_percentage:.1f}%")
print(f"Average Accuracy: {stats.average_accuracy:.2f}")

# Module-specific coverage
module_stats = registry.get_coverage_stats(module="packages/vif")
print(f"VIF Coverage: {module_stats.coverage_percentage:.1f}%")
```

---

## 🎯 **BEST PRACTICES**

### **1. Use Descriptive Tags**
```python
# ❌ Bad: Too vague
# NL: Does stuff

# ✅ Good: Clear intent
# NL: Validates user authentication token before processing request
```

### **2. Use Structured Format for Important Code**
```python
# ✅ Best: Structured format enables validation and tracking
# NL_TAG: AUTH-001 | Authenticate user credentials | authenticate(user, password) | [VIF-001, TEST-AUTH-001]
```

### **3. Keep Tags Near Code**
```python
# ✅ Good: Tag right before the code
# NL: Calculate total with tax
total = calculate_total(items) * (1 + tax_rate)

# ❌ Bad: Tag far from code
# NL: Calculate total with tax
# ... 50 lines later ...
total = calculate_total(items) * (1 + tax_rate)
```

### **4. Use Canonical IDs Consistently**
```python
# ✅ Good: Consistent ID format
# NL_TAG: AUTH-001 | ...
# NL_TAG: AUTH-002 | ...
# NL_TAG: AUTH-003 | ...

# ❌ Bad: Inconsistent IDs
# NL_TAG: auth-1 | ...
# NL_TAG: AUTH-2 | ...
# NL_TAG: authentication-3 | ...
```

---

## 🚨 **COMMON ISSUES**

### **Tags Not Extracted**
- **Check language:** Ensure file extension is supported (`.py`, `.ts`, `.js`, `.java`)
- **Check format:** Tag must match patterns (`# NL:`, `// NL:`, `# NL_TAG:`)
- **Check encoding:** File must be UTF-8

### **Validation Fails**
- **Check HHNI:** Semantic validation requires HHNI to be available
- **Check SYNTAX_REF:** Must match actual code signature exactly
- **Check code block:** Tag must have associated code block

### **CMC Storage Issues**
- **Check CMC store:** Must be initialized before use
- **Check permissions:** CMC store must have write permissions
- **Check logs:** Review CMC logs for errors

---

## 📚 **NEXT STEPS**

1. **Read Full README:** `packages/nl_tags/README.md`
2. **Learn Standard:** `knowledge_architecture/PERFECT_NL_TAG_STANDARD.md`
3. **See Examples:** `packages/nl_tags/demo.py`
4. **Check Integration:** `packages/nl_tags/API_INTEGRATION.md`

---

## 💡 **TIPS**

- **Start Simple:** Use `# NL: description` format first
- **Add Structure Later:** Migrate to structured format when ready
- **Validate Regularly:** Run validation to ensure tag accuracy
- **Track Coverage:** Monitor coverage statistics over time

---

**Ready to tag your code!** 🏷️💙

