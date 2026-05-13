# 🔧 AIM-OS CORE - TROUBLESHOOTING

**Common problems and solutions for AIM-OS Core work.**

---

## 🔴 Problem: Can't find files

### Solution: Navigate to correct directory
```powershell
cd "C:\Users\bombe\OneDrive\Desktop\AIM-OS"
ls knowledge_architecture/
```

### Key locations:
- `knowledge_architecture/SUPER_INDEX.md` - Master index
- `goals/GOAL_TREE.yaml` - Goals and objectives
- `knowledge_architecture/systems/` - System documentation
- `knowledge_architecture/AETHER_MEMORY/` - Aether's memory

---

## 🔴 Problem: File not found

### Solution 1: Check exact path
```powershell
cat knowledge_architecture/SUPER_INDEX.md
```

### Solution 2: Check if file exists
```powershell
ls knowledge_architecture/
```

### Solution 3: Check you're in right directory
```powershell
pwd
# Should show: C:\Users\bombe\OneDrive\Desktop\AIM-OS
```

If not:
```powershell
cd "C:\Users\bombe\OneDrive\Desktop\AIM-OS"
```

---

## 🔴 Problem: Don't understand the system

### Solution: Read L0-L4 docs in order
1. **L0** - Executive summary (100 words)
2. **L1** - Overview (500 words)
3. **L2** - Architecture (2,000 words)
4. **L3** - Implementation (10,000 words)
5. **L4** - Complete reference (15,000+ words)

Location: `knowledge_architecture/systems/{system_name}/`

---

## 🔴 Problem: Don't know which system to work on

### Solution 1: Check your agent profile
```powershell
cat knowledge_architecture/AGENT_ONBOARDING/agents/{your_name}/README.md
```

### Solution 2: Check GOAL_TREE.yaml for priorities
```powershell
cat goals/GOAL_TREE.yaml
```

### Solution 3: Ask user
If still unclear, ask user what system you should work on.

---

## 🔴 Problem: Don't understand L0-L4 standards

### Solution: Read the documentation standard
```powershell
cat knowledge_architecture/PERFECT_L0_L6_DOCUMENTATION_STANDARD.md
```

Key points:
- L0 = 100 words (executive summary)
- L1 = 500 words (overview)
- L2 = 2,000 words (architecture)
- L3 = 10,000 words (implementation)
- L4 = 15,000+ words (complete reference)

---

## 🔴 Problem: Don't know the north star

### Solution: It's in GOAL_TREE.yaml
**North Star:** Ship AIM-OS v0.3 by 2025-11-30

All work must trace back to this goal.

---

## 🔴 Problem: Confidence below threshold

### Solution: Follow confidence protocol
| Confidence | Action |
|------------|--------|
| 0.90-1.00 | Execute immediately |
| 0.80-0.89 | Execute with standard validation |
| 0.70-0.79 | Execute with extra validation |
| 0.60-0.69 | Research or build minimal test first |
| < 0.60 | Document question, pivot to different task |

**NEVER work below 0.70 confidence.**

---

## 🔴 Problem: Need more context

### Solution 1: Read your agent's CONTEXT.md
```powershell
cat knowledge_architecture/AGENT_ONBOARDING/agents/{your_name}/CONTEXT.md
```

### Solution 2: Read AETHER_MEMORY
```powershell
ls knowledge_architecture/AETHER_MEMORY/
```

### Solution 3: Use MCP tools (if available)
- `retrieve_memory` - Get relevant insights
- `get_timeline_entries` - Get recent context
- `query_goal_timeline` - Get active goals

---

## 🆘 Still Stuck?

**Ask user for help. Provide:**
1. What you're trying to do
2. What's confusing you
3. What you've read so far

---

*AIM-OS Core Troubleshooting v1.0*  
*Common problems and solutions*  
*Created: 2025-01-27*

