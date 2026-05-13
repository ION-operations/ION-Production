# OneDrive Migration Plan — Critical Priority
> **Goal:** Move AIM-OS off OneDrive to local SSD, eliminate sync overhead permanently

## Problem
- Desktop is trapped inside OneDrive sync folder
- Every git object write, file save, and process spawns a sync check
- Git commits take 5-10 minutes instead of seconds
- Process zombies accumulate because OneDrive locks files
- ~50GB of duplicate node_modules across project builds

## Migration Steps

### Phase 1: Create Clean Local Directory
```powershell
# Create AIM-OS home on local SSD (NOT in OneDrive)
mkdir C:\AIM-OS
# Or on another drive if available:
# mkdir D:\AIM-OS
```

### Phase 2: Copy Project (NOT move — keep OneDrive as backup)
```powershell
# Use robocopy for reliable copy with exclusions
robocopy "C:\Users\bombe\OneDrive\Desktop\AIM-OS" "C:\AIM-OS" /E /XD node_modules .venv __pycache__ target .git /XF *.pdb *.rlib
```

### Phase 3: Re-initialize Git
```powershell
cd C:\AIM-OS
git init
git remote add origin https://github.com/sev-32/AIM-OS.git
git add -A
git commit -m "Clean start: AIM-OS local SSD migration"
git push -u origin main --force
```

### Phase 4: Reinstall Dependencies (only where needed)
```powershell
# Echo Forge Loop
cd C:\AIM-OS\echo-forge-loop
npm install

# Any other projects that need node_modules
# Only install when you actually need to run them
```

### Phase 5: Update Antigravity Workspace
- Open `C:\AIM-OS` as workspace in Antigravity
- Update any absolute paths in configs
- Verify MCP server still connects

### Phase 6: Clean Up OneDrive
```powershell
# AFTER verifying everything works locally:
# Option A: Unlink OneDrive from Desktop
# Settings > OneDrive > Manage backup > Stop backing up Desktop

# Option B: Delete old copy (careful!)
# Remove-Item "C:\Users\bombe\OneDrive\Desktop\AIM-OS" -Recurse -Force
```

### Phase 7: Node Modules Cleanup
```powershell
# Find all node_modules directories and their sizes
Get-ChildItem -Path C:\ -Filter node_modules -Directory -Recurse -ErrorAction SilentlyContinue |
  ForEach-Object { 
    $size = (Get-ChildItem $_.FullName -Recurse | Measure-Object -Property Length -Sum).Sum / 1GB
    [PSCustomObject]@{Path=$_.FullName; SizeGB=[math]::Round($size,2)}
  } | Sort-Object SizeGB -Descending
```

## Critical Notes
- **Ghost machine connection:** Update Ollama provider if IP changes
- **Echo Forge submodule:** Already pushed to GitHub, just re-clone
- **MCP memory:** Store session context BEFORE moving
- **Cursor addon:** May need path updates in package.json
