# Building Minimal AIM-OS Distribution

**Purpose:** Create a clean, minimal copy of AIM-OS containing only:
- Source code we wrote
- Documentation we wrote  
- Essential configuration files
- Required data files

**Excludes:**
- `node_modules/` (dependencies)
- `__pycache__/` (Python cache)
- `dist/` (build artifacts)
- Backup files (`.backup`)
- Test artifacts
- Temporary files
- Large binary files

---

## 🚀 **Quick Start**

### **Generate Minimal Build:**

```bash
# From project root
python scripts/create_minimal_build.py
```

**Output:** `aim-os-minimal/` directory containing clean build

### **Generate System Map:**

```bash
# Generate complete file/folder map
python scripts/generate_system_map.py
```

**Output:** 
- `SYSTEM_MAP.json` (JSON format)
- `SYSTEM_MAP.txt` (Human-readable format)

---

## 📋 **What's Included**

### **Essential Files:**
- `README.md` - Main documentation
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Python project config
- `package.json` - Node.js dependencies (if exists)
- `.gitignore` - Git ignore rules
- `lucid_mcp_server.py` - MCP server
- Launch scripts (`LAUNCH_ELECTRON.bat`, etc.)

### **Essential Directories:**
- `packages/` - All our Python/TypeScript packages
- `knowledge_architecture/` - All documentation
- `goals/` - Goal tracking files
- `scripts/` - Utility scripts
- `cursor-addon/` - Cursor extension code
- `daemon_rag_system/` - Daemon/RAG system

### **Documentation:**
- All `.md` files in `knowledge_architecture/`
- All `.md` files in root and subdirectories
- Documentation standards and guides

### **Source Code:**
- All `.py` files (except `__pycache__/`)
- All `.ts` and `.tsx` files (except `node_modules/`)
- All `.js` files we wrote (not dependencies)
- Configuration files (`.json`, `.yaml`, `.toml`)

---

## 🚫 **What's Excluded**

### **Dependencies:**
- `node_modules/` - Node.js dependencies (can be reinstalled)
- `venv/`, `.venv/`, `env/` - Python virtual environments
- `__pycache__/` - Python bytecode cache

### **Build Artifacts:**
- `dist/`, `build/` - Compiled/built files
- `.next/`, `out/` - Next.js build outputs
- `*.pyc`, `*.pyo` - Python compiled files
- `*.map` - Source maps

### **IDE/Editor:**
- `.vscode/`, `.idea/`, `.cursor/` - IDE settings
- `*.swp`, `*.swo` - Editor temp files

### **Temporary/Backup:**
- `*.backup` - Backup files
- `backups/`, `backup/` - Backup directories
- `*.log` - Log files
- `tmp/`, `temp/` - Temporary directories

### **Test Artifacts:**
- `.pytest_cache/` - Pytest cache
- `htmlcov/`, `coverage/` - Test coverage reports
- `coverage.xml` - Coverage data

### **Large/Binary:**
- `codex/`, `codex_workspace/` - Large test data
- `snapshots/` - Snapshot files
- `archive/` - Archived files
- Large database files (`.db-shm`, `.db-wal`)

---

## 📊 **Build Manifest**

After running the minimal build script, check `aim-os-minimal/MANIFEST.json`:

```json
{
  "total_files": 1234,
  "total_size_bytes": 52428800,
  "total_size_mb": 50.0,
  "excluded_files": 5678,
  "files": [
    ["path/to/file.py", 1024],
    ...
  ]
}
```

---

## 🔍 **System Map**

The system map provides a complete inventory of all files and folders:

**JSON Format (`SYSTEM_MAP.json`):**
- Complete file/folder structure
- File sizes and metadata
- Directory organization
- Summary statistics

**Text Format (`SYSTEM_MAP.txt`):**
- Human-readable directory tree
- File counts per directory
- Size information
- Excluded directories list

---

## 🛠️ **Usage Examples**

### **Create Minimal Build for Distribution:**

```bash
# Generate minimal build
python scripts/create_minimal_build.py

# Check manifest
cat aim-os-minimal/MANIFEST.json

# Package for distribution (optional)
cd aim-os-minimal
tar -czf ../aim-os-minimal.tar.gz .
```

### **Generate System Map for Documentation:**

```bash
# Generate map
python scripts/generate_system_map.py

# View summary
cat SYSTEM_MAP.txt | head -50

# Count files by type
python -c "import json; data=json.load(open('SYSTEM_MAP.json')); print(f\"Files: {data['summary']['total_files']}\")"
```

---

## 📝 **Customization**

To customize what's included/excluded, edit:
- `scripts/create_minimal_build.py` - Modify `EXCLUDE_PATTERNS`, `ESSENTIAL_FILES`, etc.
- `scripts/generate_system_map.py` - Modify `SKIP_DIRECTORIES`

---

## ✅ **Verification**

After creating minimal build:

1. **Check size:** Should be significantly smaller than full project
2. **Verify structure:** All essential directories present
3. **Test build:** Can rebuild from minimal (install dependencies)
4. **Check manifest:** All expected files included

---

**Last Updated:** 2025-11-02  
**Status:** ✅ Ready for use

