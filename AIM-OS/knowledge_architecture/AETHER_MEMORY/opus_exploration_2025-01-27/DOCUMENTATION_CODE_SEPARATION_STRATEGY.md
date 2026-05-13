# Documentation Code Separation Strategy
**Date:** 2025-01-27  
**Status:** 📋 Planning Phase

---

## 📊 **SCOPE ANALYSIS**

### **Code Files Found in Documentation/00_Organized:**
- **Total:** 782 code files (.js, .ts, .tsx, .jsx)
- **Distribution:**
  - `01_Core_AI_Systems/Symbolic_Processing/`: 424 files (137 .js, 105 .ts)
  - `12_System_Families/LOG_OS_Family/`: 424 files (137 .js, 105 .ts) - **Likely duplicate**
  - `03_Creative_Platforms/3D_Tools/`: 684 files (474 no-ext, 67 .js, 49 .ts)
  - `12_System_Families/Director_Family/`: 88 files (22 .js, 15 .ts)
  - `07_Game_Platforms/LIFE_Platform/`: 29 files (8 .ts, 6 .js)
  - `11_Algorithms_Methods/Optimization/`: 24 files (6 .js, 6 .ts)
  - `10_Data_Structures/Glyph_Systems/`: 20 files (4 .ts, 3 .h)
  - Others: scattered smaller collections

---

## 🎯 **CLASSIFICATION STRATEGY**

### **Category 1: Example/Reference Code (Keep with Docs)**
- Small example snippets that illustrate concepts
- Code that's part of documentation explanations
- **Action:** Keep in place, add README explaining purpose

### **Category 2: Reference Implementations (Move to examples/)**
- Complete implementations meant as references
- Working code examples
- **Action:** Move to `examples/documentation_references/`

### **Category 3: Archived/Historical Code (Move to archive/)**
- Old versions of systems
- Deprecated implementations
- **Action:** Move to `archive/documentation_code/`

### **Category 4: Active Code (Move to packages/ or appropriate location)**
- Code that should be part of active codebase
- **Action:** Move to appropriate package or create new package

---

## 🔍 **INVESTIGATION NEEDED**

Before moving files, need to determine:
1. Are LOG_OS_Family and Symbolic_Processing the same code? (both show 424 files)
2. Are these active implementations or historical references?
3. Do they belong to existing packages or are they standalone?

---

## ✅ **RECOMMENDED APPROACH**

### **Phase 1: Analysis (Current)**
1. Sample files from each major collection
2. Determine purpose and classification
3. Check for duplicates

### **Phase 2: Safe Moves**
1. Move clearly archived code to `archive/documentation_code/`
2. Move reference implementations to `examples/documentation_references/`
3. Create README files explaining what stayed and why

### **Phase 3: Deep Clean (Future)**
1. Full audit of remaining code
2. Integration with active codebase if appropriate
3. Final organization

---

## ⚠️ **RISKS**

- Moving active code could break references
- Documentation might reference these files
- Need to preserve context and relationships

---

## 💡 **RECOMMENDATION**

**Start conservative:**
1. Create `archive/documentation_code/` for clearly old code
2. Create `examples/documentation_references/` for reference implementations
3. Move only files we're certain about
4. Document decisions in README files
5. Leave ambiguous cases for later review

---

**Status:** Strategy defined, ready for implementation

