# Reliable Launch Protocol - DAC IDE V2

## 🚨 CRITICAL: This protocol MUST be followed every time

**Problem:** Launch failures due to:
1. Multiple Node processes running (port conflicts)
2. Inconsistent directory navigation (relative paths failing)
3. No verification of server startup
4. Background execution hiding errors

## ✅ RELIABLE LAUNCH PATTERN (ALWAYS USE THIS)

### Step 1: Kill Existing Processes
```powershell
# Kill any Node processes on ports 3002-3004
$ports = @(3002, 3003, 3004)
foreach ($port in $ports) {
    $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conn) {
        $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
        if ($proc -and $proc.ProcessName -eq "node") {
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
    }
}
```

### Step 2: Navigate Using Absolute Path
```powershell
# ALWAYS use absolute path, NEVER relative
Set-Location "C:\Users\bombe\OneDrive\Desktop\AIM-OS\ide_orchestration\prototypes\dac"
```

### Step 3: Verify Prerequisites
```powershell
# Check Node.js
node --version

# Check node_modules exists
Test-Path "node_modules"

# Check launch script exists
Test-Path "launch.ps1"
```

### Step 4: Launch Server
```powershell
# Run in background but capture output
npm run dev
```

### Step 5: Verify Server Started
```powershell
# Wait 5 seconds, then verify
Start-Sleep -Seconds 5
$conn = Get-NetTCPConnection -LocalPort 3002 -ErrorAction SilentlyContinue
if ($conn -and $conn.State -eq "Listen") {
    Write-Host "✅ Server running on port 3002"
} else {
    Write-Host "❌ Server NOT running - check errors"
}
```

## 🔧 ALTERNATIVE: Use Launch Script Directly

If the above pattern fails, use the launch script directly:

```powershell
# Navigate to directory
Set-Location "C:\Users\bombe\OneDrive\Desktop\AIM-OS\ide_orchestration\prototypes\dac"

# Run launch script
powershell -ExecutionPolicy Bypass -File launch.ps1
```

## 🚫 NEVER DO THESE THINGS

1. ❌ **NEVER use relative paths with `cd`** - Always use absolute paths
2. ❌ **NEVER launch without killing existing processes** - Always check ports first
3. ❌ **NEVER skip verification** - Always verify server started
4. ❌ **NEVER assume success** - Always check the result
5. ❌ **NEVER use `&&` in PowerShell** - Use `;` or separate commands
6. ❌ **NEVER nest `cd` commands** - Use absolute paths instead

## 📋 CHECKLIST (MANDATORY)

Before claiming launch success:
- [ ] Killed existing Node processes on ports 3002-3004
- [ ] Navigated using absolute path
- [ ] Verified Node.js is available
- [ ] Verified node_modules exists
- [ ] Started server (npm run dev)
- [ ] Waited 5 seconds
- [ ] Verified server is listening on port 3002
- [ ] Confirmed browser opened or provided URL

## 🎯 SUCCESS CRITERIA

Launch is successful ONLY when:
1. ✅ No existing processes on ports 3002-3004
2. ✅ Server process started
3. ✅ Server listening on port 3002 (or 3003/3004 if 3002 busy)
4. ✅ Browser opened automatically OR URL provided to user
5. ✅ User confirms it's working

## 🔍 DEBUGGING

If launch fails:
1. Check for existing processes: `Get-NetTCPConnection -LocalPort 3002,3003,3004`
2. Check Node.js: `node --version`
3. Check dependencies: `Test-Path "node_modules"`
4. Check Vite config: `Get-Content vite.config.ts`
5. Check package.json scripts: `Get-Content package.json | Select-String "dev"`

## 📝 NOTES

- **Port 3002** is the default (configured in vite.config.ts)
- **Vite auto-opens browser** (configured in vite.config.ts)
- **Background execution** is fine, but MUST verify after 5 seconds
- **Absolute paths** prevent directory navigation failures
- **Process cleanup** prevents port conflicts

---

**Created:** 2025-01-27  
**Purpose:** Prevent launch failures through consistent, reliable pattern  
**Status:** MANDATORY PROTOCOL - Never deviate from this pattern

