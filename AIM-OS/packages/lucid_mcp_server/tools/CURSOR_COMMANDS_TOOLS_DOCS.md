# Cursor Commands MCP Tools - Documentation

**Package:** `packages/lucid_mcp_server/tools/cursor_commands.py`  
**Category:** Cursor Commands (3 tools)  
**Phase:** Phase 1 - Discovery & Validation  
**Status:** ✅ Implemented (needs server restart)  
**Date:** 2025-11-05  
**Author:** Aether  

---

## Overview

MCP tools for programmatic management of Cursor commands. Enables command discovery, inspection, and validation through MCP interface.

**Benefits:**
- Programmatic command management
- Automated validation
- Meta-circular capability
- Analytics foundation

---

## Tools

### 1. list_cursor_commands

**Purpose:** Discover all available Cursor commands with filtering and metadata

**Usage:**
```python
result = mcp_lucid-mcp_list_cursor_commands(
    scope="all",  # "project" | "global" | "team" | "all"
    category="documentation",  # "documentation" | "development" | "system" | "memory" | "all"
    include_metadata=True
)
```

**Returns:**
```json
{
  "success": true,
  "commands": [
    {
      "name": "create-t0-t4-docs",
      "path": ".cursor/commands/create-t0-t4-docs.md",
      "scope": "project",
      "category": "documentation",
      "description": "Generate complete T0-T4 documentation stack",
      "lines": 102,
      "word_count": 850
    }
  ],
  "total": 15,
  "by_category": {
    "documentation": 5,
    "development": 5,
    "system": 3,
    "memory": 2
  },
  "timestamp": "2025-11-05T19:35:00Z"
}
```

**Use Cases:**
- Command discovery for AI
- Autocomplete integration
- Command analytics
- Documentation generation

---

### 2. get_cursor_command

**Purpose:** Get full command content and metadata for inspection

**Usage:**
```python
result = mcp_lucid-mcp_get_cursor_command(
    command_name="run-tests",
    include_usage_stats=False  # True to include analytics (future)
)
```

**Returns:**
```json
{
  "success": true,
  "name": "run-tests",
  "path": ".cursor/commands/run-tests.md",
  "content": "# Run Tests with Comprehensive Reporting\n\n...",
  "metadata": {
    "created": "2025-11-05T18:45:00Z",
    "updated": "2025-11-05T18:45:00Z",
    "lines": 89,
    "word_count": 720,
    "category": "development"
  },
  "workflow_steps": [
    "Determine Test Scope",
    "Run Tests",
    "Analyze Results",
    "Report Issues"
  ],
  "mcp_tools_used": [
    "track_confidence",
    "add_timeline_entry"
  ],
  "scripts_referenced": [
    "scripts/vif_auto_tagger.py"
  ],
  "timestamp": "2025-11-05T19:35:00Z"
}
```

**Use Cases:**
- Command debugging
- Workflow inspection
- Dependency analysis
- Integration planning

---

### 3. validate_cursor_command

**Purpose:** Validate command syntax, workflow, and quality

**Usage:**
```python
result = mcp_lucid-mcp_validate_cursor_command(
    command_name="fix-nl-tags",
    checks=["syntax", "workflow", "scripts", "mcp_tools", "examples"]  # Optional, defaults to all
)
```

**Returns:**
```json
{
  "success": true,
  "command": "fix-nl-tags",
  "valid": true,
  "checks": {
    "syntax": {
      "valid": true,
      "markdown_errors": []
    },
    "workflow": {
      "valid": true,
      "steps_complete": true,
      "step_count": 6,
      "missing_steps": []
    },
    "scripts": {
      "valid": true,
      "missing_scripts": [],
      "scripts_found": ["scripts/vif_auto_tagger.py"],
      "total_scripts": 1
    },
    "mcp_tools": {
      "valid": true,
      "tools_exist": true,
      "tools_referenced": ["track_confidence"],
      "unknown_tools": []
    },
    "examples": {
      "valid": true,
      "examples_present": true,
      "example_count": 2
    }
  },
  "quality_score": 1.0,
  "timestamp": "2025-11-05T19:35:00Z"
}
```

**Use Cases:**
- Pre-commit validation
- Quality gates
- Automated testing
- Command health checks

---

## Implementation Details

### CursorCommandsTools Class

**Location:** `packages/lucid_mcp_server/tools/cursor_commands.py`

**Key Methods:**

```python
class CursorCommandsTools:
    """MCP tools for Cursor command management."""
    
    def __init__(self, workspace_root: Optional[str] = None):
        """Initialize with auto-detected workspace root."""
        
    def list_cursor_commands(self, scope="all", category=None, include_metadata=True):
        """List commands with filtering."""
        
    def get_cursor_command(self, command_name: str, include_usage_stats=False):
        """Get full command details."""
        
    def validate_cursor_command(self, command_name: str, checks=None):
        """Validate command quality."""
```

**Helper Methods:**
- `_scan_commands_directory` - Scan for command files
- `_parse_command_metadata` - Extract metadata
- `_extract_workflow_steps` - Parse workflow
- `_extract_mcp_tools` - Find MCP tools used
- `_extract_scripts` - Find scripts referenced
- `_validate_syntax` - Markdown validation
- `_validate_workflow` - Workflow completeness
- `_validate_scripts` - Script existence
- `_validate_mcp_tools` - Tool validation
- `_validate_examples` - Example presence
- `_calculate_quality_score` - Overall quality

---

## Integration Architecture

```
┌──────────────────────────────────────┐
│      MCP Tools (74 total)            │
│                                      │
│  ┌────────────────────────────────┐ │
│  │ Cursor Commands Tools (3)      │ │
│  │                                │ │
│  │  - list_cursor_commands        │ │
│  │  - get_cursor_command          │ │
│  │  - validate_cursor_command     │ │
│  └────────┬───────────────────────┘ │
│           │                          │
└───────────┼──────────────────────────┘
            ↓
    ┌───────────────┐
    │ .cursor/      │
    │  commands/    │
    │               │
    │  - 15 command │
    │    files      │
    └───────┬───────┘
            │
            ↓ (commands execute)
    ┌───────────────┐
    │ MCP Tools     │
    │ (store_memory,│
    │  track_conf., │
    │  etc.)        │
    └───────────────┘
    
Meta-circular loop:
Commands ↔ MCP Tools
```

---

## Testing Plan

### After Server Restart

**Test 1: list_cursor_commands**
```python
# Test basic listing
result = mcp_lucid-mcp_list_cursor_commands()
assert result["success"] == True
assert result["total"] == 15
assert "commands" in result

# Test category filtering
docs = mcp_lucid-mcp_list_cursor_commands(category="documentation")
assert len(docs["commands"]) == 5
```

**Test 2: get_cursor_command**
```python
# Test command retrieval
result = mcp_lucid-mcp_get_cursor_command("create-t0-t4-docs")
assert result["success"] == True
assert result["name"] == "create-t0-t4-docs"
assert "workflow_steps" in result
assert len(result["mcp_tools_used"]) > 0
```

**Test 3: validate_cursor_command**
```python
# Test validation
result = mcp_lucid-mcp_validate_cursor_command("run-tests")
assert result["success"] == True
assert result["valid"] == True
assert result["quality_score"] >= 0.90
```

---

## Future Enhancements (Phase 2-3)

**Phase 2: Creation & Execution**
- `create_cursor_command` - Create commands programmatically
- `execute_cursor_command` - Execute commands via MCP
- `chain_cursor_commands` - Multi-command workflows

**Phase 3: Analytics & Optimization**
- `analyze_cursor_commands` - Usage analytics
- `generate_cursor_command` - AI-assisted creation
- `sync_cursor_commands` - Distribution

**Phase 4: Advanced**
- Command templates
- Self-optimization
- Marketplace integration

---

**Status:** ✅ **Documented and Ready for Testing**  
**Next:** Server restart → Testing → Validation  
**Confidence:** 0.90

