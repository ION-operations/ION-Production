# 🔧 LUCID IMAGE - TROUBLESHOOTING

**Common problems and solutions for Lucid Image app.**

---

## 🔴 Problem: `npm run dev` fails

### Solution 1: Kill conflicting Node processes
```powershell
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
npm run dev
```

### Solution 2: Clear Vite cache
```powershell
Remove-Item -Path "node_modules/.vite" -Recurse -ErrorAction SilentlyContinue
npm run dev
```

### Solution 3: Reinstall dependencies
```powershell
Remove-Item -Path "node_modules" -Recurse -ErrorAction SilentlyContinue
npm install
npm run dev
```

### Solution 4: Check you're in right directory
```powershell
pwd
# Should show: C:\Users\bombe\OneDrive\Desktop\AIM-OS\Documentation\appexamples\lucidimage\project
```

If not:
```powershell
cd "C:\Users\bombe\OneDrive\Desktop\AIM-OS\Documentation\appexamples\lucidimage\project"
npm run dev
```

---

## 🔴 Problem: TypeScript errors

### Solution: Run typecheck to see specific errors
```powershell
npm run typecheck
```

### Common TypeScript errors:

**Missing import:**
```
Cannot find module '@/...'
```
→ Check import path is correct

**Type error:**
```
Type 'X' is not assignable to type 'Y'
```
→ Check variable types match

**Syntax error:**
```
')' expected
```
→ Check for missing parentheses, brackets, or braces

---

## 🔴 Problem: Browser doesn't open automatically

### Solution: Open manually
Navigate to http://localhost:5173 in your browser.

Check console output for actual port (might be 5174, 5175 if 5173 in use).

---

## 🔴 Problem: Port 5173 already in use

### Solution 1: Vite auto-uses next port
Check console output for actual port (5174, 5175, etc.)

### Solution 2: Kill process using port
```powershell
netstat -ano | findstr :5173
# Note the PID (last column)
taskkill /PID <PID> /F
npm run dev
```

---

## 🔴 Problem: App crashes when clicking/hovering something

### Solution 1: Check console for errors
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for red error messages
4. Fix the component causing the error

### Solution 2: Check for syntax errors
```powershell
npm run typecheck
```

### Solution 3: Check recent changes
If you just made changes, undo them and try again.

---

## 🔴 Problem: Page shows blank/error

### Solution 1: Check console for errors
Browser console (F12 → Console) will show what's wrong.

### Solution 2: Check the page component
Your page component is at `src/pages/versions/{page}/`

Common issues:
- Missing return statement
- Missing closing tags
- Undefined variables
- Missing imports

---

## 🔴 Problem: Changes not appearing

### Solution 1: Hard refresh
Press Ctrl+Shift+R in browser.

### Solution 2: Clear browser cache
DevTools (F12) → Application → Clear site data

### Solution 3: Restart dev server
```powershell
# Ctrl+C to stop current server
npm run dev
```

---

## 🔴 Problem: Module not found errors

### Solution: Install missing module
```powershell
npm install <module-name>
```

Or reinstall all:
```powershell
npm install
```

---

## 🔴 Problem: "Cannot find module" in import

### Solution 1: Check the path
```typescript
// Wrong (might not exist)
import { Thing } from './Thing'

// Right (check actual file location)
import { Thing } from '../components/Thing'
```

### Solution 2: Check the @ alias
```typescript
// @ maps to src/
import { Thing } from '@/components/Thing'
// Same as:
import { Thing } from 'src/components/Thing'
```

---

## 🆘 Still Stuck?

**Ask user for help. Provide:**
1. Exact error message (copy-paste)
2. What you tried
3. What happened

**Do NOT:**
- Claim "fixed" without testing
- Make random changes hoping they work
- Give up without trying solutions above

---

*Lucid Image Troubleshooting v1.0*  
*Common problems and solutions*  
*Created: 2025-01-27*

