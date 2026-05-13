# 🔧 EPIC STANDARDS - TROUBLESHOOTING

**Common problems and solutions for EPIC Standards work.**

---

## 🔴 Problem: Can't find EPIC files

### Solution: Navigate to correct directory
```powershell
cd "C:\Users\bombe\OneDrive\Desktop\AIM-OS"
ls coordination/epic_standards_overhaul/comms/
```

### Key files:
- `LEADERSHIP_DIRECTIVE.md` - Mission and goals
- `AGENT_PROTOCOLS.md` - How agents work
- `MESSAGE_BOARD.md` - Current status and assignments

---

## 🔴 Problem: File not found

### Solution 1: Check exact path
```powershell
cat coordination/epic_standards_overhaul/comms/LEADERSHIP_DIRECTIVE.md
```

### Solution 2: Check if file exists
```powershell
ls coordination/epic_standards_overhaul/comms/
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

## 🔴 Problem: Don't understand the directive

### Solution: Re-read key sections
1. **Mission:** What is the EPIC Standards rollout trying to achieve?
2. **Timeline:** When are things due?
3. **Priorities:** What should be done first?

If still confused, ask user for clarification.

---

## 🔴 Problem: Don't know my assignment

### Solution 1: Check message board
```powershell
cat coordination/epic_standards_overhaul/comms/MESSAGE_BOARD.md
```

### Solution 2: Ask user
If no assignment on message board, ask user what you should work on.

---

## 🔴 Problem: Don't know how to coordinate

### Solution: Re-read agent protocols
```powershell
cat coordination/epic_standards_overhaul/comms/AGENT_PROTOCOLS.md
```

Key protocols:
1. Assign unique name
2. Announce on message board
3. Create plan before work
4. Regular updates

---

## 🔴 Problem: Conflicting with other agents

### Solution 1: Check message board for other agents
See who else is working on what.

### Solution 2: Coordinate via message board
Post your intent before starting work.

### Solution 3: Ask user to resolve
If conflict can't be resolved, ask user.

---

## 🆘 Still Stuck?

**Ask user for help. Provide:**
1. What you're trying to do
2. What's confusing you
3. What you've read so far

---

*EPIC Standards Troubleshooting v1.0*  
*Common problems and solutions*  
*Created: 2025-01-27*

