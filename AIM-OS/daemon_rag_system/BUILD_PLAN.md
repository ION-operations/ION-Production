# 🏗️ Daemon/RAG System - Build Plan

**Version:** 1.0.0  
**Last Updated:** 2025-10-31  
**Status:** Comprehensive Build Guide  
**System:** Daemon/RAG Intelligent MCP Tool Management

---

## 📋 **OVERVIEW**

This build plan provides step-by-step instructions for building, testing, and deploying the Daemon/RAG System, including all dependencies, prerequisites, and integration requirements.

---

## ✅ **PREREQUISITES**

### **System Requirements**

#### **Operating System**
- ✅ **Windows 10/11** (Primary development platform)
- ✅ **macOS 10.15+** (Supported)
- ✅ **Linux** (Ubuntu 20.04+, Debian 11+) (Supported)

#### **Python Environment**
- **Python Version:** 3.9+ (Required)
- **Python Path:** Must be in system PATH
- **Pip Version:** 21.0+ (Latest recommended)

**Verify:**
```bash
python --version  # Should show 3.9+
pip --version     # Should show 21.0+
```

#### **Development Tools**
- **Git:** For version control
- **VS Code / Cursor IDE:** For development (optional but recommended)
- **Terminal:** PowerShell (Windows) or Bash (macOS/Linux)

### **AIM-OS Dependencies**

The Daemon/RAG system integrates with AIM-OS core systems. Ensure these are available:

- ✅ **CMC (Context Memory Core):** `packages/cmc_service/`
- ✅ **HHNI (Hierarchical Hypergraph Neural Index):** `packages/hhni/`
- ✅ **VIF (Verifiable Intelligence Framework):** `packages/vif/` (optional)
- ✅ **MCP Tools:** `lucid_mcp_server.py` with 51+ tools

**Note:** AIM-OS systems should be in the same repository or accessible via PYTHONPATH.

---

## 📦 **DEPENDENCIES**

### **Core Dependencies** (Required)

From `daemon_rag_system/requirements.txt`:

```txt
# Core dependencies
numpy>=1.21.0              # Numerical operations
psutil>=5.8.0              # System resource monitoring
pydantic>=1.8.0            # Data validation
dataclasses-json>=0.5.7    # JSON serialization

# HTTP API dependencies
fastapi>=0.104.0           # Web framework
uvicorn[standard]>=0.24.0  # ASGI server
python-multipart>=0.0.6    # File upload support
```

### **Optional Dependencies** (Enhanced Features)

```txt
# Machine learning (for advanced RAG)
scikit-learn>=1.0.0        # ML algorithms
torch>=1.9.0               # Deep learning
transformers>=4.0.0        # NLP models
```

### **Development Dependencies**

```txt
# Testing
pytest>=6.0.0              # Test framework
pytest-cov>=2.12.0         # Coverage reporting

# Code Quality
black>=21.0.0              # Code formatting
flake8>=3.9.0              # Linting
mypy>=0.910                # Type checking
```

---

## 🔧 **BUILD STEPS**

### **Step 1: Clone/Checkout Repository**

```bash
# If cloning fresh
git clone <repository-url>
cd AIM-OS

# If already cloned, ensure latest
git pull origin main
```

### **Step 2: Create Virtual Environment** (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Verify activation:**
```bash
which python  # Should show venv path
```

### **Step 3: Install Dependencies**

```bash
# Navigate to daemon_rag_system directory
cd daemon_rag_system

# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pytest pytest-cov black flake8 mypy
```

**Verify installation:**
```bash
pip list | grep -E "(numpy|psutil|pydantic|fastapi|uvicorn)"
```

### **Step 4: Set PYTHONPATH**

**Critical:** Daemon/RAG system needs access to AIM-OS packages.

**Windows (PowerShell):**
```powershell
$env:PYTHONPATH = "C:\Users\<username>\OneDrive\Desktop\AIM-OS"
```

**Windows (CMD):**
```cmd
set PYTHONPATH=C:\Users\<username>\OneDrive\Desktop\AIM-OS
```

**macOS/Linux:**
```bash
export PYTHONPATH=$(pwd)
```

**Permanent Setup (Optional):**
- Add to `.bashrc` / `.zshrc` / `profile.ps1`
- Or use `.env` file with `python-dotenv`

### **Step 5: Verify AIM-OS Integration**

```bash
# Test imports
python -c "from packages.cmc_service import MemoryStore; print('CMC OK')"
python -c "from packages.hhni import HierarchicalIndex; print('HHNI OK')"
python -c "from daemon_rag_system import DaemonRAGSystem; print('Daemon OK')"
```

**Expected:** All imports succeed without errors.

---

## 🧪 **TESTING**

### **Run Unit Tests**

```bash
cd daemon_rag_system

# Run all tests
pytest test_daemon_rag_system.py -v

# Run specific test class
pytest test_daemon_rag_system.py::TestToolRegistry -v

# Run with coverage
pytest test_daemon_rag_system.py --cov=. --cov-report=html
```

### **Run Performance Benchmarks**

```bash
# Run performance tests
pytest test_daemon_rag_system.py --benchmark

# Or use built-in benchmark
python test_daemon_rag_system.py --benchmark
```

### **Test Individual Components**

```bash
# Test Tool Registry
python -c "from tool_registry.tool_registry import ToolRegistry; r = ToolRegistry(); print(f'Tools: {len(r.get_all_tools())}')"

# Test Context Analyzer
python -c "from context_analysis_engine.context_analyzer import ContextAnalysisEngine; print('Context Analyzer OK')"

# Test Tool Selector
python -c "from tool_selection_engine.tool_selector import ToolSelectionEngine; print('Tool Selector OK')"
```

### **Integration Tests**

```bash
# Test full daemon system
python -c "
from daemon_rag_system import DaemonRAGSystem, DaemonConfig
config = DaemonConfig(max_tools=40)
daemon = DaemonRAGSystem(config)
success = daemon.start()
print(f'Daemon started: {success}')
daemon.stop()
"
```

---

## 🚀 **BUILD ARTIFACTS**

### **Python Package Structure**

```
daemon_rag_system/
├── __init__.py
├── daemon_rag_system.py          # Main daemon class
├── http_api_server.py            # HTTP API server
├── requirements.txt               # Dependencies
├── README.md                      # Documentation
├── TROUBLESHOOTING.md            # Troubleshooting guide
├── tool_registry/                # Tool registry subsystem
├── context_analysis_engine/      # Context analysis subsystem
├── tool_selection_engine/         # Tool selection subsystem
├── rag_system/                   # RAG subsystem
├── server_manager/               # Server management subsystem
├── performance_monitor/          # Performance monitoring subsystem
├── learning_system/              # Learning subsystem
├── resource_manager/             # Resource management subsystem
└── ah_protocol/                  # A-H Protocol integration (optional)
```

### **Build Outputs**

After successful build:
- ✅ All Python modules compiled (`.pyc` files in `__pycache__/`)
- ✅ Dependencies installed in virtual environment
- ✅ Tests passing
- ✅ No import errors

---

## 📦 **PACKAGING**

### **Create Distribution Package** (Optional)

```bash
# Create setup.py (if packaging for distribution)
cat > setup.py << EOF
from setuptools import setup, find_packages

setup(
    name="daemon-rag-system",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "psutil>=5.8.0",
        "pydantic>=1.8.0",
        "dataclasses-json>=0.5.7",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "python-multipart>=0.0.6",
    ],
)
EOF

# Build package
python setup.py sdist bdist_wheel
```

### **Docker Build** (Optional)

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY daemon_rag_system/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy daemon system
COPY daemon_rag_system/ .

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Expose HTTP API port
EXPOSE 5000

# Run HTTP API server
CMD ["python", "http_api_server.py"]
```

**Build Docker image:**
```bash
docker build -t daemon-rag-system:latest .
```

---

## 🔍 **VERIFICATION**

### **Build Verification Checklist**

- [ ] Python 3.9+ installed and accessible
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip list` shows all packages)
- [ ] PYTHONPATH set correctly
- [ ] AIM-OS packages importable
- [ ] Daemon system imports without errors
- [ ] All unit tests pass (`pytest` shows 100% pass rate)
- [ ] Performance benchmarks meet targets (<400ms response time)
- [ ] HTTP API server starts without errors
- [ ] No linting errors (`flake8` clean)
- [ ] Type checking passes (`mypy` clean)

### **Quick Verification Script**

```bash
#!/bin/bash
# verify_build.sh

echo "=== Daemon/RAG Build Verification ==="

# Check Python version
python --version | grep -q "Python 3.9" && echo "✅ Python version OK" || echo "❌ Python version check failed"

# Check dependencies
python -c "import numpy, psutil, pydantic, fastapi, uvicorn" && echo "✅ Dependencies OK" || echo "❌ Dependencies missing"

# Check imports
python -c "from daemon_rag_system import DaemonRAGSystem" && echo "✅ Daemon imports OK" || echo "❌ Daemon import failed"

# Check AIM-OS integration
python -c "from packages.cmc_service import MemoryStore" && echo "✅ CMC integration OK" || echo "❌ CMC integration failed"

# Run tests
pytest test_daemon_rag_system.py -v --tb=short && echo "✅ Tests pass" || echo "❌ Tests failed"

echo "=== Verification Complete ==="
```

---

## 🐛 **TROUBLESHOOTING BUILD ISSUES**

### **Common Issues**

#### **1. Import Errors**
**Symptom:** `ModuleNotFoundError: No module named 'packages'`

**Solution:**
```bash
# Set PYTHONPATH to project root
export PYTHONPATH=$(pwd)  # Linux/macOS
set PYTHONPATH=%CD%       # Windows CMD
$env:PYTHONPATH = $PWD    # Windows PowerShell
```

#### **2. Dependency Conflicts**
**Symptom:** Package version conflicts

**Solution:**
```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### **3. Missing System Libraries**
**Symptom:** `psutil` fails to install or import

**Solution:**
```bash
# Windows: Usually works out of box
# Linux: May need system packages
sudo apt-get install python3-dev  # Ubuntu/Debian
sudo yum install python3-devel    # CentOS/RHEL
```

#### **4. FastAPI/Uvicorn Issues**
**Symptom:** HTTP server won't start

**Solution:**
```bash
# Ensure all dependencies installed
pip install fastapi uvicorn[standard] python-multipart

# Check port availability
netstat -an | grep 5000  # Linux/macOS
netstat -an | findstr 5000  # Windows
```

---

## 📊 **BUILD METRICS**

### **Expected Build Times**

- **Dependency Installation:** 2-5 minutes
- **Full Test Suite:** 30-60 seconds
- **Performance Benchmarks:** 1-2 minutes
- **Total Build Time:** 5-10 minutes

### **Build Size**

- **Source Code:** ~50-100 KB
- **Dependencies:** ~500 MB (with virtual environment)
- **Compiled:** ~10-20 MB (`.pyc` files)

---

## 🎯 **NEXT STEPS**

After successful build:

1. ✅ **Review Integration Plan** - `INTEGRATION_PLAN.md`
2. ✅ **Configure Cursor IDE** - MCP server setup
3. ✅ **Start HTTP API Server** - For Cursor UI integration
4. ✅ **Run Verification Tests** - Ensure everything works
5. ✅ **Check Documentation** - `README.md`, `TROUBLESHOOTING.md`

---

**Build Status:** ✅ Ready for Production  
**Last Verified:** 2025-10-31  
**Build Confidence:** 0.95 (High)

