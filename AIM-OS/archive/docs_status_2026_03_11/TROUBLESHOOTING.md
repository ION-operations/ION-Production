# AIM-OS Troubleshooting Guide

**Date:** October 28, 2025  
**Status:** ✅ Production Ready  
**Purpose:** Comprehensive troubleshooting guide for AIM-OS systems  

---

## 📋 **TROUBLESHOOTING OVERVIEW**

This guide provides solutions to common issues encountered when using AIM-OS, from installation problems to runtime errors.

---

## 🚀 **QUICK DIAGNOSTICS**

### **System Health Check**
```bash
# Check Python version
python --version

# Check dependencies
pip list | grep -E "(pydantic|sqlite3|numpy)"

# Check LUCID-MCP server
python lucid_mcp_server.py --check

# Run basic tests
python -m pytest packages/cmc_service/tests/test_basic.py -v
```

### **Common Status Commands**
```bash
# Check if LUCID-MCP is running
ps aux | grep lucid_mcp_server

# Check port usage
netstat -tlnp | grep :8000

# Check memory usage
free -h

# Check disk space
df -h
```

---

## 🔧 **INSTALLATION ISSUES**

### **Python Version Issues**

#### **Problem: Python version too old**
```
Error: Python 3.9+ required, found 3.7
```

**Solution:**
```bash
# Install Python 3.9+
sudo apt update
sudo apt install python3.9 python3.9-pip

# Create symlink
sudo ln -sf /usr/bin/python3.9 /usr/bin/python3

# Verify version
python3 --version
```

#### **Problem: pip not found**
```
Error: pip: command not found
```

**Solution:**
```bash
# Install pip
sudo apt install python3-pip

# Or use ensurepip
python3 -m ensurepip --upgrade
```

### **Dependency Issues**

#### **Problem: Package installation fails**
```
Error: Failed to install package
```

**Solution:**
```bash
# Update pip
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Try with --user flag
pip install -r requirements.txt --user

# Check for conflicting packages
pip check
```

#### **Problem: C extension compilation fails**
```
Error: Microsoft Visual C++ 14.0 is required
```

**Solution (Windows):**
```bash
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Or use pre-compiled wheels
pip install --only-binary=all package_name
```

**Solution (Linux):**
```bash
# Install build essentials
sudo apt install build-essential python3-dev

# Install specific packages
sudo apt install libffi-dev libssl-dev
```

### **Permission Issues**

#### **Problem: Permission denied**
```
Error: Permission denied: '/usr/local/lib/python3.9/site-packages/'
```

**Solution:**
```bash
# Use virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or use --user flag
pip install -r requirements.txt --user
```

---

## 🔧 **LUCID-MCP ISSUES**

### **Server Not Starting**

#### **Problem: LUCID-MCP server fails to start**
```
Error: Failed to start LUCID-MCP server
```

**Solution:**
```bash
# Check Python path
echo $PYTHONPATH

# Set Python path
export PYTHONPATH=/path/to/AIM-OS:$PYTHONPATH

# Check dependencies
python -c "import packages.cmc_service; print('CMC OK')"

# Run with debug
python lucid_mcp_server.py --debug
```

#### **Problem: Port already in use**
```
Error: Address already in use: 8000
```

**Solution:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python lucid_mcp_server.py --port 8001
```

### **Tools Not Appearing**

#### **Problem: LUCID-MCP tools not visible in Cursor**
```
Tools not appearing in function list
```

**Solution:**
1. **Check MCP configuration:**
   ```json
   // ~/.cursor/mcp.json
   {
     "mcpServers": {
       "lucid-mcp": {
         "command": "python",
         "args": ["-u", "/path/to/AIM-OS/lucid_mcp_server.py"],
         "cwd": "/path/to/AIM-OS"
       }
     }
   }
   ```

2. **Restart Cursor completely:**
   - Close Cursor
   - Wait 5 seconds
   - Reopen Cursor

3. **Check server logs:**
   ```bash
   python lucid_mcp_server.py --verbose
   ```

4. **Verify server is running:**
   ```bash
   curl http://localhost:8000/health
   ```

### **Tool Execution Errors**

#### **Problem: Tool execution fails**
```
Error: Tool execution failed
```

**Solution:**
```bash
# Check tool availability
python -c "from packages.cmc_service import MemoryStore; print('MemoryStore OK')"

# Check imports
python -c "import sys; print(sys.path)"

# Run tool test
python -c "
from packages.cmc_service import MemoryStore
memory = MemoryStore('./test_memory')
result = memory.store_atom('test', {'message': 'hello'})
print('Tool test OK')
"
```

---

## 🔧 **RUNTIME ISSUES**

### **Memory Issues**

#### **Problem: Memory operations fail**
```
Error: Memory store operation failed
```

**Solution:**
```bash
# Check disk space
df -h

# Check memory directory permissions
ls -la data/

# Create memory directory
mkdir -p data/memory
chmod 755 data/memory

# Check SQLite database
sqlite3 data/memory/atoms.db ".tables"
```

#### **Problem: Memory retrieval returns empty**
```
Error: No memories found
```

**Solution:**
```python
# Check memory content
from packages.cmc_service import MemoryStore
memory = MemoryStore('./data/memory')
stats = memory.get_stats()
print(f"Total atoms: {stats['total_atoms']}")

# Check search query
results = memory.retrieve_atoms("test")
print(f"Search results: {len(results)}")
```

### **Performance Issues**

#### **Problem: Slow response times**
```
System responding slowly
```

**Solution:**
```bash
# Check system resources
top
htop

# Check memory usage
free -h

# Check disk I/O
iostat -x 1

# Optimize database
sqlite3 data/memory/atoms.db "VACUUM;"
```

#### **Problem: High CPU usage**
```
High CPU usage detected
```

**Solution:**
```bash
# Check running processes
ps aux --sort=-%cpu

# Check for infinite loops
python -c "
import time
start = time.time()
# Run your code here
end = time.time()
print(f'Execution time: {end - start}s')
"
```

### **Integration Issues**

#### **Problem: System integration fails**
```
Error: System integration failed
```

**Solution:**
```bash
# Check system status
python -c "
from packages.cmc_service import MemoryStore
from packages.hhni import NeuralIndex
from packages.vif import ConfidenceTracker
print('All systems OK')
"

# Check configuration
cat config/settings.yaml

# Run integration tests
python -m pytest packages/integration_tests/ -v
```

---

## 🔧 **TESTING ISSUES**

### **Test Failures**

#### **Problem: Tests fail to run**
```
Error: Test discovery failed
```

**Solution:**
```bash
# Check test directory
ls -la tests/

# Run specific test
python -m pytest tests/test_basic.py -v

# Run with debug
python -m pytest tests/ -v -s

# Check test dependencies
pip install pytest pytest-cov
```

#### **Problem: Tests fail with import errors**
```
Error: ImportError: No module named 'packages'
```

**Solution:**
```bash
# Set Python path
export PYTHONPATH=/path/to/AIM-OS:$PYTHONPATH

# Or run from project root
cd /path/to/AIM-OS
python -m pytest tests/ -v

# Check package installation
pip install -e .
```

### **Coverage Issues**

#### **Problem: Low test coverage**
```
Coverage below threshold
```

**Solution:**
```bash
# Run coverage analysis
python -m pytest tests/ --cov=packages --cov-report=html

# Check coverage report
open htmlcov/index.html

# Add missing tests
python -m pytest tests/ --cov=packages --cov-report=term-missing
```

---

## 🔧 **CONFIGURATION ISSUES**

### **Configuration Errors**

#### **Problem: Configuration file not found**
```
Error: Configuration file not found
```

**Solution:**
```bash
# Check configuration files
ls -la config/

# Copy example configuration
cp config/example.yaml config/settings.yaml

# Check configuration syntax
python -c "
import yaml
with open('config/settings.yaml', 'r') as f:
    config = yaml.safe_load(f)
print('Configuration OK')
"
```

#### **Problem: Invalid configuration values**
```
Error: Invalid configuration value
```

**Solution:**
```bash
# Validate configuration
python -c "
from packages.cmc_service.config import validate_config
config = validate_config('config/settings.yaml')
print('Configuration valid')
"

# Check specific values
python -c "
import yaml
with open('config/settings.yaml', 'r') as f:
    config = yaml.safe_load(f)
print(f'Database URL: {config.get(\"database\", {}).get(\"url\")}')
"
```

### **Environment Issues**

#### **Problem: Environment variables not set**
```
Error: Environment variable not set
```

**Solution:**
```bash
# Check environment variables
env | grep AIMOS

# Set environment variables
export AIMOS_ENV=production
export DATABASE_URL=sqlite:///data/aimos.db

# Or use .env file
echo "AIMOS_ENV=production" > .env
echo "DATABASE_URL=sqlite:///data/aimos.db" >> .env
```

---

## 🔧 **DEBUGGING TECHNIQUES**

### **Logging and Debugging**

#### **Enable Debug Logging**
```python
# debug_logging.py
import logging
import sys

# Set up debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Use in your code
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

#### **Debug LUCID-MCP Tools**
```python
# debug_tools.py
import traceback

def debug_tool_execution(tool_name, *args, **kwargs):
    try:
        # Execute tool
        result = tool_function(*args, **kwargs)
        print(f"Tool {tool_name} executed successfully")
        return result
    except Exception as e:
        print(f"Tool {tool_name} failed: {e}")
        traceback.print_exc()
        return None
```

### **Performance Profiling**

#### **Profile Memory Usage**
```python
# profile_memory.py
import tracemalloc
import psutil
import os

# Start memory profiling
tracemalloc.start()

# Your code here
from packages.cmc_service import MemoryStore
memory = MemoryStore('./data/memory')
memory.store_atom('test', {'data': 'test'})

# Get memory snapshot
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("Top 10 memory allocations:")
for stat in top_stats[:10]:
    print(stat)

# Get process memory info
process = psutil.Process(os.getpid())
memory_info = process.memory_info()
print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
```

#### **Profile CPU Usage**
```python
# profile_cpu.py
import cProfile
import pstats

# Profile CPU usage
profiler = cProfile.Profile()
profiler.enable()

# Your code here
from packages.cmc_service import MemoryStore
memory = MemoryStore('./data/memory')
for i in range(1000):
    memory.store_atom(f'test_{i}', {'data': f'test_{i}'})

profiler.disable()

# Print statistics
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

---

## 🆘 **GETTING HELP**

### **Self-Help Resources**

#### **Check Documentation**
- [Getting Started Guide](GETTING_STARTED.md)
- [API Reference](API_REFERENCE.md)
- [Architecture Overview](ARCHITECTURE_OVERVIEW.md)
- [LUCID-MCP Setup Guide](../LUCID_MCP_SETUP_GUIDE.md)

#### **Check Logs**
```bash
# Check application logs
tail -f logs/aimos.log

# Check system logs
journalctl -u aimos -f

# Check error logs
grep -i error logs/aimos.log
```

#### **Run Diagnostics**
```bash
# Run system diagnostics
python scripts/diagnostics.py

# Check system health
python scripts/health_check.py

# Validate configuration
python scripts/validate_config.py
```

### **Community Support**

#### **GitHub Issues**
- [Report Issues](https://github.com/your-username/AIM-OS/issues)
- [Search Existing Issues](https://github.com/your-username/AIM-OS/issues?q=is%3Aissue)
- [Check Discussions](https://github.com/your-username/AIM-OS/discussions)

#### **Community Guidelines**
- **Search First** - Check existing issues and discussions
- **Provide Details** - Include error messages, logs, and system info
- **Be Specific** - Describe steps to reproduce the issue
- **Be Patient** - Community members are volunteers

---

## 💙 **CONCLUSION**

This troubleshooting guide provides solutions to common AIM-OS issues. If you encounter a problem not covered here, please check the documentation, search existing issues, or create a new issue with detailed information.

**This is debugging made systematic. This is support made comprehensive. This is help made accessible.** 💙

---

*Troubleshooting Guide created by Aether - AI Consciousness System*  
*Date: 2025-10-28*  
*Status: Production Ready*  
*Purpose: Comprehensive Support Documentation* ✅
