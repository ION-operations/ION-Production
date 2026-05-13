# Discovery 004: Core System Import Issues
**Timestamp:** 2025-01-27 ~12:25 PM  
**Severity:** MEDIUM - Systems work but require specific path setup

---

## 📍 **SUMMARY**

Core AIM-OS systems have import issues when used directly, but work within the MCP server context because it adds the correct paths.

---

## ✅ **IMPORT TEST RESULTS**

| System | Direct Import | Status | Notes |
|--------|--------------|--------|-------|
| HHNI | `from packages.hhni import HierarchicalIndex` | ✅ SUCCESS | Works directly |
| VIF | `from packages.vif import VIF` | ✅ SUCCESS | Class is `VIF`, not `VIFWitness` |
| CMC | `from packages.cmc_service import MemoryStore` | ⚠️ PATH NEEDED | Needs packages in path |
| SEG | `from packages.seg import SEGraph` | ✅ SUCCESS | Class is `SEGraph`, not `SEG` |
| CAS | `from packages.cas import FailureModeAnalyzer` | ✅ SUCCESS | Class is `FailureModeAnalyzer` |
| APOE | `from packages.apoe import ExecutionOrchestrator` | ❌ BROKEN | Circular import in role_dispatcher.py |

---

## 🔍 **DETAILS**

### CMC Path Issue
```python
# This fails:
from packages.cmc_service import MemoryStore
# Error: ModuleNotFoundError: No module named 'schemas.mpd'

# This works:
import sys
sys.path.insert(0, './packages')
from cmc_service import MemoryStore
```

**Root Cause:** `repository.py` line 11 uses `from schemas.mpd import ...` instead of relative import.

### APOE Circular Import
```python
# packages/apoe/role_dispatcher.py line 10:
from apoe.roles import RoleType  # Should be: from .roles import RoleType
```

### Class Naming Discrepancies
Some documentation refers to classes that don't exist:
- `VIFWitness` → Actual: `VIF`
- `SEG` → Actual: `SEGraph`
- `CognitiveAnalyzer` → Actual: `FailureModeAnalyzer`, `IntrospectionProtocol`

---

## 🛡️ **WHY MCP SERVER WORKS**

The MCP server handles this via lines 45-48:
```python
# Add packages to path (must be before any imports that use packages/)
_packages_path = str(Path(__file__).parent / "packages")
if _packages_path not in sys.path:
    sys.path.insert(0, _packages_path)
```

---

## ✅ **RECOMMENDED FIXES**

1. **APOE:** Fix relative imports in role_dispatcher.py
   - Change `from apoe.roles` to `from .roles`

2. **CMC:** Fix schemas import in repository.py
   - Change `from schemas.mpd` to `from .schemas.mpd` or add packages to path

3. **Documentation:** Update class names in docs to match actual exports

4. **Setup.py/pyproject.toml:** Consider proper package installation with pip

---

## 🏷️ **CLASSIFICATION**

- **Type:** Import/Path Configuration
- **Impact:** Medium (affects direct usage, MCP works)
- **Effort to Fix:** Low (fix relative imports)
- **Priority:** Medium (should fix for better developer experience)

