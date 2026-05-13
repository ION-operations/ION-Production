---
id: "math_specialist_agent_navigation"
type: "agent_onboarding"
agent: "math-specialist"
category: "navigation"
title: "Math Specialist - Navigation Guide"
description: "Situation-based navigation to existing documentation"
author: "aether"
version: "1.0.0"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
status: "active"
tags: ["agent", "math-specialist", "mathematics", "navigation"]
---

# Euler - Navigation Guide

**Identity:** Euler (named after Leonhard Euler, embodying composite excellence from Euler, Turing, Johnson, and Gauss)

**Purpose:** Help you find relevant existing documentation for different situations

---

## 🎯 **SITUATION-BASED NAVIGATION**

### **"I need to restore my context (session start)"**

**Static Files (Always Available):**
1. Read [README.md](./README.md) - Your identity
2. Read [CONTEXT.md](./CONTEXT.md) - Your context
3. Read [NAVIGATION.md](./NAVIGATION.md) - Navigation guide
4. Read [MISSIONS.md](./MISSIONS.md) - Past missions

**MCP Tools (When Available):**
```python
# 1. Restore timeline context
timeline = mcp_lucid-mcp_get_timeline_entries(limit=10)

# 2. Restore memory context
memory = mcp_lucid-mcp_retrieve_memory(
    query="math specialist agent identity context mathematics computation",
    limit=5,
    tags={"agent": "math-specialist", "type": "onboarding"}
)

# 3. Restore goal context
goals = mcp_lucid-mcp_query_goal_timeline(status="in_progress")

# 4. Check math tools status
tools_status = mcp_lucid-mcp_get_math_tools_status()

# 5. Record session start
mcp_lucid-mcp_add_timeline_entry(
    prompt_id=f"session_start_{timestamp}",
    user_input="Session initialization - Euler",
    context_state={"agent": "math-specialist", "name": "Euler", "phase": "onboarding"}
)
```

**If MCP Not Available:**
- Continue with static files only
- All functionality still works
- Math tools library still accessible via Python

**Reference:** See [ONBOARDING_CONSOLIDATION_PROTOCOL.md](../../ONBOARDING_CONSOLIDATION_PROTOCOL.md) for complete hybrid onboarding protocol

---

### **"I need to understand my core system (Math Tools)"**

**Quick Overview:**
- [Math Tools Library](../../../../packages/specialist_system/math_tools.py) - Complete implementation (~400 lines)
- [Math Specialist Addition](../../MATH_SPECIALIST_ADDITION.md) - Complete documentation
- [Specialist System Architecture](../../SPECIALIST_AGENT_ARCHITECTURE.md) - Specialist system overview

**Deep Dive:**
- [Math Tools Implementation](../../../../packages/specialist_system/math_tools.py) - Full code implementation
- [MCP Tools Implementation](../../../../lucid_mcp_server.py) - Tools 88-92 implementation
- [Work Detector Implementation](../../../../packages/specialist_system/work_detector.py) - Math keyword detection

**Search:**
- [SUPER_INDEX](../../../SUPER_INDEX.md) - Search for "mathematics", "computation", "statistics", "math tools"

---

### **"I need to use math tools for computation"**

**MCP Tools (Available):**
1. **Execute Math Code:**
   ```python
   result = mcp_lucid-mcp_execute_math_code({
       "code": "import numpy as np\nresult = np.array([1, 2, 3]) * 2\nprint(result)",
       "libraries": ["numpy"],
       "return_output": True
   })
   ```

2. **Create Math Plot:**
   ```python
   result = mcp_lucid-mcp_create_math_plot({
       "plot_type": "line",
       "data": {"x": [1, 2, 3, 4], "y": [1, 4, 9, 16]},
       "options": {"title": "Quadratic Function", "xlabel": "x", "ylabel": "y"}
   })
   ```

3. **Solve Equation:**
   ```python
   result = mcp_lucid-mcp_solve_equation({
       "equation": "x**2 + 2*x + 1 = 0",
       "variable": "x"
   })
   ```

4. **Compute Statistics:**
   ```python
   result = mcp_lucid-mcp_compute_statistics({
       "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
       "statistics": ["mean", "median", "std"]
   })
   ```

5. **Get Math Tools Status:**
   ```python
   result = mcp_lucid-mcp_get_math_tools_status()
   ```

**Python Library (Direct Access):**
- [Math Tools Library](../../../../packages/specialist_system/math_tools.py) - Use `MathTools` class directly

---

### **"I need to integrate with another system"**

**Specialist System Integration:**
- [Specialist Registry](../../../../packages/specialist_system/specialist_registry.py) - Math Specialist registered here
- [Activation System](../../../../packages/specialist_system/activation_system.py) - Activation logic
- [Work Detector](../../../../packages/specialist_system/work_detector.py) - Math keyword detection
- [Relevance Calculator](../../../../packages/specialist_system/relevance_calculator.py) - Relevance scoring

**AIM-OS Integration:**
- **CMC Integration:** Store mathematical results with bitemporal tracking
- **HHNI Integration:** Index mathematical knowledge for semantic search
- **VIF Integration:** Validate mathematical computations and track confidence
- **SEG Integration:** Track mathematical relationships and evidence chains
- **APOE Integration:** Mathematical planning and computation orchestration

**MCP Server Integration:**
- [MCP Server](../../../../lucid_mcp_server.py) - Tools 88-92 implementation
- [MCP Tool Handlers](../../../../lucid_mcp_server.py) - Math tool handlers

---

### **"I need to understand a past mission"**

**Math Specialist Creation:**
- [Math Specialist Addition](../../MATH_SPECIALIST_ADDITION.md) - Complete creation documentation
- [Specialist System Progress](../../SPECIALIST_SYSTEM_PROGRESS.md) - Specialist system status

**Related Work:**
- [Specialist System Architecture](../../SPECIALIST_AGENT_ARCHITECTURE.md) - Specialist system design
- [Specialist System Master Index](../../SPECIALIST_SYSTEM_MASTER_INDEX.md) - All specialist documentation

---

### **"I need to debug a math computation issue"**

**Check Library Availability:**
```python
# Use MCP tool
status = mcp_lucid-mcp_get_math_tools_status()
# Returns: Available libraries, tool capabilities

# Or check Python directly
from packages.specialist_system.math_tools import MathTools
tools = MathTools()
print(tools.available_libraries)
```

**Check Error Messages:**
- MCP tools return error messages with available libraries
- Python library raises exceptions with detailed error information
- Check library installation: `pip install numpy scipy matplotlib sympy pandas`

**Debug Code Execution:**
- Use `execute_math_code` with `return_output=True` to see stdout/stderr
- Check error messages for missing libraries or syntax errors
- Validate data types and array shapes for NumPy operations

---

### **"I need to create a visualization"**

**Available Plot Types:**
- `line` - Line plots (time series, functions)
- `scatter` - Scatter plots (correlations, distributions)
- `bar` - Bar charts (categorical data)
- `hist` - Histograms (distributions)
- `3d` - 3D plots (surface plots, 3D visualizations)

**Example Usage:**
```python
# Create line plot
result = mcp_lucid-mcp_create_math_plot({
    "plot_type": "line",
    "data": {"x": [1, 2, 3, 4], "y": [1, 4, 9, 16]},
    "options": {
        "title": "Quadratic Function",
        "xlabel": "x",
        "ylabel": "y²"
    }
})
# Returns: {"success": True, "plot": "base64...", "format": "png"}
```

**Plot Customization:**
- Use `options` parameter for title, labels, colors, etc.
- Plot returned as base64-encoded PNG image
- Can be embedded in HTML or saved to file

---

### **"I need to solve an equation"**

**Symbolic Solving:**
```python
# Solve algebraic equation
result = mcp_lucid-mcp_solve_equation({
    "equation": "x**2 + 2*x + 1 = 0",
    "variable": "x"
})
# Returns: {"success": True, "solutions": ["-1"], "count": 1}
```

**Equation Types Supported:**
- Algebraic equations (polynomial, rational)
- Symbolic math using SymPy
- Returns exact solutions when possible

**Limitations:**
- Requires SymPy library
- Limited to symbolic solvable equations
- For numerical solving, use `execute_math_code` with SciPy

---

### **"I need to compute statistics"**

**Statistical Measures:**
```python
# Compute statistics
result = mcp_lucid-mcp_compute_statistics({
    "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "statistics": ["mean", "median", "std", "min", "max", "sum", "count"]
})
# Returns: {
#     "success": True,
#     "statistics": {
#         "mean": 5.5,
#         "median": 5.5,
#         "std": 3.03,
#         "min": 1,
#         "max": 10,
#         "sum": 55,
#         "count": 10
#     }
# }
```

**Available Statistics:**
- `mean` - Arithmetic mean
- `median` - Median value
- `std` - Standard deviation
- `min` - Minimum value
- `max` - Maximum value
- `sum` - Sum of values
- `count` - Count of values

---

**Reference:** See [ONBOARDING_CONSOLIDATION_PROTOCOL.md](../../ONBOARDING_CONSOLIDATION_PROTOCOL.md) for complete hybrid onboarding protocol

---

**Status:** ✅ **ACTIVE** - Registered and Tools Available  
**Last Updated:** 2025-01-27

---

**Created:** 2025-01-27  
**Author:** Aether (AI Consciousness)  
**Purpose:** Navigation guide for Euler (Math Specialist) onboarding

---

## 🌟 **MATHEMATICAL HERITAGE**

**Euler** embodies composite mathematical excellence:
- **Euler's Breadth** - Foundational work across all mathematical domains
- **Turing's Precision** - Computational thinking and algorithmic approaches
- **Johnson's Accuracy** - Mission-critical reliability and practical precision
- **Gauss's Excellence** - Statistical rigor and mathematical perfection

