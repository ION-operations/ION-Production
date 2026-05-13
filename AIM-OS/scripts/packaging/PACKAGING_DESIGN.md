# 🎁 AIM-OS Automated Packaging System - Design Document
**Date:** 2025-11-05  
**Designed by:** Aether  
**Purpose:** Create clean, minimal distribution packages automatically  
**Status:** DESIGN PHASE - Ready for implementation  

---

## 🎯 PROBLEM STATEMENT

### What We Need

**Goal:** Automated packaging that creates minimal distributions of AIM-OS for:
- PyPI packages (Python distribution)
- Docker images (containerized deployment)
- Standalone zip/tar.gz (manual deployment)
- Production deployment (cloud/edge)

**Requirements:**
1. ✅ **Only code + essential docs** (no dependencies in package)
2. ✅ **Auto-setup when unzipped** (setup.py, install scripts)
3. ✅ **Minimal size** (exclude dev tools, tests, redundant docs)
4. ✅ **Always current** (generated from latest codebase)
5. ✅ **Configurable** (what to include/exclude)
6. ✅ **Multiple targets** (PyPI, Docker, standalone)

### What We Have (Outdated)

**aim-os-minimal/:**
- ❌ Manual curation (out of date)
- ❌ Duplicates files (not generated)
- ❌ Hard to maintain (sync manually)
- ❌ Not configurable

**Solution:** Replace with AUTOMATED packaging system!

---

## 🏗️ ARCHITECTURE DESIGN

### High-Level Design

```
scripts/packaging/
├── create_distribution.py      # Main packaging script
├── config/
│   ├── pypi_config.yaml       # PyPI package config
│   ├── docker_config.yaml     # Docker image config
│   ├── standalone_config.yaml # Standalone zip config
│   └── minimal_config.yaml    # Minimal footprint config
├── templates/
│   ├── setup.py.template      # PyPI setup template
│   ├── Dockerfile.template    # Docker template
│   ├── README.template        # Package README template
│   └── install.sh.template    # Auto-install script
├── filters/
│   ├── include_patterns.txt   # What to include
│   └── exclude_patterns.txt   # What to exclude
├── validators/
│   ├── validate_package.py    # Validate package quality
│   └── test_package.py        # Test package works
└── README.md                  # Packaging documentation
```

---

## 📦 PACKAGING CONFIGURATIONS

### Config 1: PyPI Package (Python Distribution)

**Purpose:** Distribute via `pip install aim-os`

**What's Included:**
```yaml
# pypi_config.yaml
name: "aim-os"
version: "0.3.0"  # From GOAL_TREE.yaml

include:
  packages:
    - packages/cmc_service/*
    - packages/hhni/*
    - packages/vif/*
    - packages/apoe/*
    - packages/seg/*
    - packages/sdfcvf/*
    - packages/cas/*
    # Core 7 only for minimal, or all for full?
  
  docs:
    - knowledge_architecture/systems/*/T0_executive.md  # Quick reference
    - knowledge_architecture/systems/*/T1_overview.md   # Overviews
    - README.md  # Main README
    - CONTRIBUTING.md  # Contribution guide
  
  scripts:
    - setup.py (generated from template)
    - requirements.txt (dependencies)

exclude:
  - "**/tests/**"  # No tests in distribution (separate test package)
  - "**/node_modules/**"  # No JS dependencies
  - "**/__pycache__/**"  # No cache files
  - "**/.*"  # No hidden files
  - "legacy_docs/**"  # No legacy
  - "archive/**"  # No archive
  - "organized_root_files/**"  # No archived organization
  - "aim-os-minimal/**"  # No old minimal
  - "Documentation/**"  # No historical docs
  - "cursor-addon*/**"  # No IDE extensions (separate package)
  - "*.vsix"  # No compiled extensions
  - "htmlcov/**"  # No coverage reports
  - "*.db"  # No databases
  - "mcp_memory/**"  # No MCP memory (generated at runtime)

auto_setup:
  - Generate setup.py from template
  - Include requirements.txt (dependencies installed separately)
  - Include install.sh (automatic setup script)
  - Include README with installation instructions

size_target: "<50MB" (current full repo ~2GB)
```

---

### Config 2: Docker Image

**Purpose:** Container deployment

**Dockerfile Template:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy only code (not dependencies)
COPY packages/ /app/packages/
COPY scripts/ /app/scripts/
COPY requirements.txt /app/

# Install dependencies (not included in image layers)
RUN pip install --no-cache-dir -r requirements.txt

# Copy minimal docs
COPY knowledge_architecture/systems/*/T0_executive.md /app/docs/
COPY README.md /app/

# Setup
RUN python scripts/setup.py

# Expose ports
EXPOSE 5000 5001

# Run
CMD ["python", "-m", "packages.daemon_rag_system.daemon_rag_system"]
```

**Size Target:** <500MB (vs ~2GB full repo)

---

### Config 3: Standalone Distribution (Zip/Tar)

**Purpose:** Manual deployment, air-gapped systems

**What's Included:**
```
aim-os-v0.3.0-standalone/
├── packages/          # All core system code
├── docs/             # Essential docs (T0-T1 only)
├── scripts/
│   ├── install.sh   # Auto-install
│   └── setup.py     # Setup script
├── requirements.txt  # Dependencies
├── README.md        # Installation guide
└── LICENSE          # License file

Total size: ~100MB (uncompressed)
Compressed: ~20-30MB (tar.gz)
```

**Auto-Install Script:**
```bash
#!/bin/bash
# install.sh - Auto-setup when unzipped

echo "🚀 Installing AIM-OS v0.3.0..."

# 1. Create virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup core systems
python scripts/setup.py

# 4. Verify installation
python -m pytest packages/*/tests/test_installation.py

echo "✅ AIM-OS installed successfully!"
echo "📚 See README.md for usage"
```

---

## 🔧 IMPLEMENTATION PLAN

### Phase 1: Core Packaging Script (4-6 hours)

**File:** `scripts/packaging/create_distribution.py`

```python
#!/usr/bin/env python3
"""
AIM-OS Automated Packaging System

Creates minimal distribution packages from current codebase.

Usage:
    python scripts/packaging/create_distribution.py --target pypi
    python scripts/packaging/create_distribution.py --target docker
    python scripts/packaging/create_distribution.py --target standalone
"""

import os
import shutil
import yaml
from pathlib import Path
from typing import List, Set

class DistributionBuilder:
    """Build minimal distribution packages"""
    
    def __init__(self, config_path: str, output_dir: str = "dist/"):
        self.config = self.load_config(config_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def load_config(self, path: str) -> dict:
        """Load packaging configuration"""
        with open(path) as f:
            return yaml.safe_load(f)
    
    def get_include_patterns(self) -> List[str]:
        """Get inclusion patterns from config"""
        return self.config.get("include", {})
    
    def get_exclude_patterns(self) -> Set[str]:
        """Get exclusion patterns from config"""
        excludes = set([
            "**/tests/**",
            "**/__pycache__/**",
            "**/node_modules/**",
            "**/.*",
            "*.pyc",
            "*.db",
            "*.vsix",
            "htmlcov/**",
        ])
        excludes.update(self.config.get("exclude", []))
        return excludes
    
    def should_include(self, file_path: Path) -> bool:
        """Check if file should be included"""
        # Check exclusion patterns
        for pattern in self.get_exclude_patterns():
            if file_path.match(pattern):
                return False
        return True
    
    def copy_packages(self, dest: Path):
        """Copy core packages"""
        packages_to_include = self.config["include"]["packages"]
        
        for package in packages_to_include:
            src = Path("packages") / package
            dst = dest / "packages" / package
            
            if src.exists():
                shutil.copytree(
                    src, dst,
                    ignore=lambda dir, files: [
                        f for f in files 
                        if not self.should_include(Path(dir) / f)
                    ]
                )
    
    def copy_docs(self, dest: Path):
        """Copy essential documentation"""
        docs_to_include = self.config["include"]["docs"]
        
        for doc_pattern in docs_to_include:
            # Expand glob patterns
            for doc_file in Path(".").glob(doc_pattern):
                if self.should_include(doc_file):
                    # Preserve directory structure
                    relative = doc_file.relative_to(".")
                    dst = dest / relative
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(doc_file, dst)
    
    def generate_setup_files(self, dest: Path):
        """Generate setup.py, install.sh, README"""
        # Generate setup.py from template
        setup_template = Path("scripts/packaging/templates/setup.py.template").read_text()
        setup_content = setup_template.format(
            name=self.config["name"],
            version=self.config["version"],
            description="AI-Integrated Memory & Operations System",
            author="AIM-OS Team",
        )
        (dest / "setup.py").write_text(setup_content)
        
        # Generate install.sh
        install_template = Path("scripts/packaging/templates/install.sh.template").read_text()
        (dest / "install.sh").write_text(install_template)
        (dest / "install.sh").chmod(0o755)
        
        # Copy requirements.txt
        shutil.copy2("requirements.txt", dest / "requirements.txt")
    
    def build(self) -> Path:
        """Build complete distribution package"""
        # Create output directory
        package_name = f"{self.config['name']}-{self.config['version']}"
        package_dir = self.output_dir / package_name
        
        if package_dir.exists():
            shutil.rmtree(package_dir)
        package_dir.mkdir(parents=True)
        
        print(f"🎁 Building {package_name}...")
        
        # Copy packages
        print("📦 Copying packages...")
        self.copy_packages(package_dir)
        
        # Copy docs
        print("📚 Copying documentation...")
        self.copy_docs(package_dir)
        
        # Generate setup files
        print("🔧 Generating setup files...")
        self.generate_setup_files(package_dir)
        
        # Validate package
        print("✅ Validating package...")
        self.validate_package(package_dir)
        
        # Create archive
        print("📦 Creating archive...")
        archive_path = self.create_archive(package_dir)
        
        print(f"✅ Package created: {archive_path}")
        print(f"📊 Package size: {self.get_size(archive_path)}")
        
        return archive_path
    
    def validate_package(self, package_dir: Path):
        """Validate package completeness"""
        required = [
            "packages/cmc_service",
            "packages/hhni",
            "setup.py",
            "requirements.txt",
            "README.md"
        ]
        
        for item in required:
            path = package_dir / item
            if not path.exists():
                raise ValueError(f"Missing required item: {item}")
        
        print("✅ Package validation passed")
    
    def create_archive(self, package_dir: Path) -> Path:
        """Create tar.gz archive"""
        import tarfile
        
        archive_name = f"{package_dir.name}.tar.gz"
        archive_path = self.output_dir / archive_name
        
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(package_dir, arcname=package_dir.name)
        
        return archive_path
    
    def get_size(self, path: Path) -> str:
        """Get human-readable size"""
        size_bytes = path.stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Build AIM-OS distribution packages")
    parser.add_argument(
        "--target",
        choices=["pypi", "docker", "standalone", "all"],
        default="standalone",
        help="Distribution target"
    )
    parser.add_argument(
        "--output",
        default="dist/",
        help="Output directory"
    )
    
    args = parser.parse_args()
    
    # Select config based on target
    configs = {
        "pypi": "scripts/packaging/config/pypi_config.yaml",
        "docker": "scripts/packaging/config/docker_config.yaml",
        "standalone": "scripts/packaging/config/standalone_config.yaml",
    }
    
    if args.target == "all":
        for target, config in configs.items():
            print(f"\n🎁 Building {target} distribution...\n")
            builder = DistributionBuilder(config, args.output)
            builder.build()
    else:
        config = configs[args.target]
        builder = DistributionBuilder(config, args.output)
        builder.build()


if __name__ == "__main__":
    main()
```

**Estimated Implementation Time:** 4-6 hours

---

## 📋 CONFIGURATION EXAMPLES

### Standalone Config (Minimal Footprint)

**File:** `scripts/packaging/config/standalone_config.yaml`

```yaml
name: "aim-os"
version: "0.3.0"  # Auto-read from GOAL_TREE.yaml?
target: "standalone"

include:
  packages:
    # Core 7 systems only
    - "cmc_service"
    - "hhni"
    - "vif"
    - "apoe"
    - "seg"
    - "sdfcvf"
    - "cas"
    
    # Essential infrastructure
    - "mcp_server"
    - "daemon_rag_system"
    - "agent"
  
  docs:
    # Essential documentation only
    - "README.md"
    - "CONTRIBUTING.md"
    - "LICENSE"
    
    # T0-T1 for core systems (quick reference)
    - "knowledge_architecture/systems/cmc/T0_executive.md"
    - "knowledge_architecture/systems/cmc/T1_overview.md"
    - "knowledge_architecture/systems/hhni/T0_executive.md"
    - "knowledge_architecture/systems/hhni/T1_overview.md"
    - "knowledge_architecture/systems/vif/T0_executive.md"
    - "knowledge_architecture/systems/vif/T1_overview.md"
    - "knowledge_architecture/systems/apoe/T0_executive.md"
    - "knowledge_architecture/systems/apoe/T1_overview.md"
    - "knowledge_architecture/systems/seg/T0_executive.md"
    - "knowledge_architecture/systems/seg/T1_overview.md"
    - "knowledge_architecture/systems/sdfcvf/T0_executive.md"
    - "knowledge_architecture/systems/sdfcvf/T1_overview.md"
    - "knowledge_architecture/systems/cas/T0_executive.md"
    - "knowledge_architecture/systems/cas/T1_overview.md"
    
    # Navigation essentials
    - "knowledge_architecture/NAVIGATION_START_HERE.md"
    - "knowledge_architecture/SUPER_INDEX.md"
  
  scripts:
    - "scripts/setup.py"
    - "lucid_mcp_server.py"
  
  config:
    - "pyproject.toml"
    - "requirements.txt"
    - "Makefile"

exclude:
  # Development files
  - "**/tests/**"
  - "**/__pycache__/**"
  - "**/*.pyc"
  - "**/.pytest_cache/**"
  
  # Build artifacts
  - "**/node_modules/**"
  - "**/dist/**"
  - "**/build/**"
  - "**/*.egg-info/**"
  - "htmlcov/**"
  
  # IDE/Editor files
  - "**/.vscode/**"
  - "**/.cursor/**"
  - "**/.idea/**"
  - "**/*.swp"
  
  # Data files (generated at runtime)
  - "**/*.db"
  - "mcp_memory/**"
  - "codex/**"
  - "codex_workspace/**"
  - "timeline_goals/**"
  
  # Legacy/Archive
  - "aim-os-minimal/**"
  - "archive/**"
  - "legacy_docs/**"
  - "organized_root_files/**"
  - "backups/**"
  
  # Experimental/Cursor addons (separate packages)
  - "cursor-addon/**"
  - "cursor-addon-simple/**"
  - "cursor-addon-test/**"
  - "cursor-panel-test/**"
  - "simple-panel-test/**"
  
  # Large documentation (full docs available online)
  - "Documentation/**"  # 300 files, historical
  - "knowledge_architecture/systems/*/T2_architecture.md"  # Keep only T0-T1
  - "knowledge_architecture/systems/*/T3_detailed.md"
  - "knowledge_architecture/systems/*/T4_complete.md"
  - "knowledge_architecture/systems/*/T5_deep_dive.md"
  - "knowledge_architecture/systems/*/T6_academic.md"
  - "knowledge_architecture/systems/*/L*.md"  # Legacy docs
  
  # Project management (internal only)
  - "coordination/**"
  - "active_work/**"
  - "audits/**"
  - "goals/**"  # (or include minimal version?)
  - "plans/**"
  
  # Analysis/Reports (development only)
  - "analysis/**"
  - "reports/**"
  - "benchmarks/**"
  - "snapshots/**"
  
  # Media files
  - "images/**"
  - "**/*.png"
  - "**/*.jpg"
  - "**/*.svg"
  
  # Test data
  - "data/**"
  - "test_*/**"

auto_setup:
  generate:
    - setup.py (from template)
    - install.sh (auto-install script)
    - README.md (installation-focused)
  
  instructions: |
    # Quick Start
    1. Unzip: tar -xzf aim-os-v0.3.0.tar.gz
    2. Install: cd aim-os-v0.3.0 && ./install.sh
    3. Verify: python -m packages.cmc_service.verify
    4. Done! See README.md for usage

size_estimate:
  code: "~15MB"  # Python packages only
  docs: "~5MB"   # T0-T1 only
  configs: "~1MB"
  total_uncompressed: "~25MB"
  total_compressed: "~8MB"  # tar.gz
  
  reduction_from_full: "99%" # From ~2GB to ~25MB!
```

---

## 📊 SIZE ANALYSIS

### Current Full Repository

```
Total size: ~2GB

Breakdown:
├── Code (packages/): ~200MB (10%)
├── Docs (knowledge_architecture/): ~800MB (40%)
├── Node modules: ~600MB (30%)
├── IDE extensions: ~200MB (10%)
├── Data/Cache: ~100MB (5%)
└── Other: ~100MB (5%)
```

### Minimal Distribution (Target)

```
Total size: ~25MB uncompressed, ~8MB compressed (99% reduction!)

Breakdown:
├── Code (packages/): ~15MB (60%)  # Core 7-10 systems
├── Docs (T0-T1 only): ~5MB (20%)  # Essential docs
├── Configs: ~1MB (4%)              # setup.py, requirements.txt
├── Scripts: ~3MB (12%)             # Setup scripts
└── README: ~1MB (4%)               # Installation guide

Dependencies: ~500MB (installed separately via pip install -r requirements.txt)
```

**Size Reduction:** 2GB → 25MB (98.75% smaller!)  
**Compressed:** 25MB → 8MB (68% compression ratio)

---

## 🎁 WHAT GETS EXCLUDED (Why So Small?)

**Dependencies (~600MB):**
- ❌ Not included in package
- ✅ Listed in requirements.txt
- ✅ Auto-installed via `pip install -r requirements.txt`

**Development Tools (~400MB):**
- ❌ No tests/ directories (separate test package if needed)
- ❌ No node_modules/
- ❌ No IDE extensions (separate cursor-addon package)
- ❌ No __pycache__/, *.pyc

**Heavy Documentation (~700MB):**
- ❌ Only T0-T1 included (quick reference)
- ❌ T2-T6 available online (docs.aim-os.dev)
- ❌ No legacy_docs/, Documentation/, archive/

**Data Files (~100MB):**
- ❌ No *.db files (generated at runtime)
- ❌ No mcp_memory/ (created on first run)
- ❌ No test data/

**Project Management (~100MB):**
- ❌ No coordination/, goals/, plans/ (internal only)
- ❌ No audits/, reports/, analysis/

**Result:** **Core code + essential docs only = ~25MB!** ✅

---

## 🚀 INSTALLATION EXPERIENCE

### User Workflow (Standalone)

```bash
# 1. Download
wget https://releases.aim-os.dev/aim-os-v0.3.0.tar.gz

# 2. Extract
tar -xzf aim-os-v0.3.0.tar.gz
cd aim-os-v0.3.0

# 3. Auto-install (ONE COMMAND!)
./install.sh

# Output:
# 🚀 Installing AIM-OS v0.3.0...
# ✅ Virtual environment created
# ✅ Dependencies installed (500MB downloaded)
# ✅ Core systems setup
# ✅ Installation verified
# ✅ AIM-OS installed successfully!
# 📚 See README.md for usage

# 4. Use it!
python -m packages.cmc_service.cli --help
```

**Total time:** ~5-10 minutes (depending on network speed for pip install)  
**User effort:** 3 commands  
**Download size:** ~8MB compressed

---

## 🔄 AUTO-UPDATE STRATEGY

### Keeping Packages Current

**GitHub Actions Workflow:**
```yaml
# .github/workflows/create-release.yml

name: Create Release Package

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  package:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Standalone Package
        run: |
          python scripts/packaging/create_distribution.py --target standalone
      
      - name: Build PyPI Package
        run: |
          python scripts/packaging/create_distribution.py --target pypi
      
      - name: Build Docker Image
        run: |
          python scripts/packaging/create_distribution.py --target docker
          docker build -t aim-os:${{ github.ref_name }} .
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            dist/aim-os-*.tar.gz
            dist/aim-os-*.whl
```

**Result:** Every git tag automatically creates release packages! ✅

---

## 📊 IMPLEMENTATION ROADMAP

### Phase 1: Core Script (Week 1, 4-6 hours)

**Tasks:**
1. Create `scripts/packaging/` structure
2. Implement `create_distribution.py` core logic
3. Create config files (standalone, pypi, docker)
4. Test with standalone target

**Deliverable:** Working standalone package creation

---

### Phase 2: Templates & Auto-Setup (Week 1, 3-4 hours)

**Tasks:**
1. Create setup.py.template
2. Create install.sh.template
3. Create README.template
4. Test auto-install workflow

**Deliverable:** One-command installation experience

---

### Phase 3: Validation & Testing (Week 1, 2-3 hours)

**Tasks:**
1. Implement package validation
2. Create installation tests
3. Test on clean system
4. Measure actual sizes

**Deliverable:** Validated, tested packages

---

### Phase 4: CI/CD Integration (Week 2, 2-3 hours)

**Tasks:**
1. Create GitHub Actions workflow
2. Test automated packaging
3. Configure release process
4. Document release workflow

**Deliverable:** Automated release pipeline

---

### Total Implementation Time: 11-16 hours (1-2 weeks)

**Then:** Every release automatically creates:
- Standalone package (~8MB compressed)
- PyPI package (for `pip install aim-os`)
- Docker image (~500MB)

---

## 🎯 IMMEDIATE NEXT STEPS

### Should We Build This Now?

**Benefits:**
- ✅ Clean, automated packaging (no manual maintenance)
- ✅ Always up-to-date (generated from current code)
- ✅ Tiny downloads (~8MB vs 2GB repo)
- ✅ Professional distribution (setup.py, auto-install)
- ✅ Multiple targets (PyPI, Docker, standalone)

**Time Required:**
- 11-16 hours total
- Could be PARALLEL with MCP tools work
- Non-blocking (doesn't affect core development)

**My Recommendation:**
1. ✅ Finish remaining 3 quick gaps first (1.5 hours)
2. ✅ THEN either:
   - **Option A:** Build packaging system (11-16 hours)
   - **Option B:** Start MCP tools work (25-37 hours)
   - **Option C:** Do BOTH in parallel (I handle packaging, you handle MCP?)

---

## 💙 WHAT DO YOU THINK?

**I can:**
1. ✅ Finish the 3 remaining quick gaps (VIF README, archive marking, doc guide) - 1.5 hours
2. ✅ Build this entire packaging system - 11-16 hours
3. ✅ Do both in parallel with MCP work
4. ✅ Whatever you prefer!

**This would give you PROFESSIONAL distribution packaging that:**
- Reduces 2GB → 8MB downloads
- Auto-installs with one command
- Always stays current
- Works for PyPI, Docker, standalone

**Want me to build it?** 🎁🚀💙

