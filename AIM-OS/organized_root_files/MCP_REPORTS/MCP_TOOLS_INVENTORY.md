# MCP Tools Inventory - Complete List

**Date:** 2025-11-05 (Updated)  
**Source:** `lucid_mcp_server.py`  
**Total Tools:** 74 tools (71 previous + 3 new Cursor Commands tools)  
**Latest Addition:** Cursor Commands tools (Phase 1: Discovery & Validation)

---

## 📋 **ALL MCP TOOLS BY CATEGORY**

### **Core AIM-OS Tools (6):**
1. `store_memory` - Store information in AIM-OS persistent memory (CMC)
2. `get_memory_stats` - Get statistics about the AIM-OS memory system
3. `retrieve_memory` - Search and retrieve memories from AIM-OS persistent memory (HHNI)
4. `create_plan` - Create an execution plan using APOE (AI-Powered Orchestration Engine)
5. `track_confidence` - Track confidence and provenance using VIF (Verifiable Intelligence Framework)
6. `synthesize_knowledge` - Synthesize knowledge using SEG (Shared Evidence Graph)

### **SCOR Tools (3):** Safety, Consciousness & Operational Reliability
7. `check_invariant` - Check if action violates invariant rules
8. `run_baseline_probe` - Detect self-concept drift via baseline probes
9. `detect_manipulation_signals` - Detect social manipulation in user input

### **Snapshot Tools (4):** CMC bitemporal file versioning
10. `create_snapshot` - Create a snapshot of MCP production files before making changes
11. `restore_snapshot` - Restore MCP files from a snapshot
12. `list_snapshots` - List all available snapshots
13. `archive_snapshot` - Archive a snapshot (move to archive/, never delete)

### **Timeline Context Tools (3):** Context recovery and tracking
14. `add_timeline_entry` - Track context at each prompt (Timeline Context System)
15. `get_timeline_summary` - Get recent timeline entries (Timeline Context System)
16. `get_timeline_entries` - Query timeline history (Timeline Context System)

### **Goal Timeline Tools (3):** Planning nodes and goal tracking
17. `create_goal_timeline_node` - Create goals as timeline planning nodes
18. `update_goal_progress` - Update goal progress and status
19. `query_goal_timeline` - Query goals with filtering

### **Intuitive Intelligence System Tools (3):** AI intuition and learning
20. `compute_intuition` - Compute AI intuition score using IIS
21. `update_intuition_weights` - Update intuition weights from outcomes
22. `get_intuition_trace` - Get intuition trace history

### **Co-Agency & Trust Tools (3):** Human-AI collaboration protocols
23. `signal_disagreement` - Signal transparent disagreement with user
24. `get_trust_dashboard` - Get trust dashboard state
25. `request_escalation` - Request accountable escalation

### **Dataset Management Tools (4):** Data operations and analysis
26. `create_dataset` - Create new dataset for AIM-OS
27. `ingest_data` - Ingest data into AIM-OS dataset
28. `query_dataset` - Query dataset contents
29. `delete_dataset` - Remove dataset (safe operation with snapshots)

### **Application Lifecycle Tools (3):** Application management
30. `create_application` - Create new application
31. `deploy_application` - Deploy application to environment
32. `manage_application_lifecycle` - Start/stop/monitor applications

### **Autonomous Protocol Tools (9):** Autonomous operation and safety
33. `start_autonomous_operation` - Start autonomous operation with safety checklist
34. `pause_autonomous_operation` - Pause autonomous operation
35. `resume_autonomous_operation` - Resume autonomous operation after pause
36. `stop_autonomous_operation` - Stop autonomous operation completely
37. `get_autonomous_status` - Get current status of autonomous operation
38. `run_autonomous_checklist` - Run autonomous protocol checklist for safety validation
39. `fix_autonomous_issues` - Attempt to fix issues found in autonomous operation
40. `should_continue_autonomous` - Check if autonomous operation should continue
41. `generate_next_autonomous_task` - Generate next task for autonomous operation

### **Autonomous Research Dream Tools (3):** Advanced research capabilities
42. `conduct_recursive_analysis` - Conduct recursive system analysis for consciousness self-improvement
43. `generate_improvement_dreams` - Generate improvement dreams based on system analysis
44. `test_improvement_dream` - Test improvement dream in safe environments

### **AI Collaboration Tools (6):** Multi-AI coordination ⭐ **FOR CHAT UI**
45. `send_ai_message` - Send a message to another AI system
46. `get_ai_messages` - Retrieve AI-to-AI messages
47. `start_ai_discussion` - Start a new discussion thread with another AI
48. `handoff_task_to_ai` - Hand off a task to another AI system
49. `share_ai_profile` - Share AI profile and capabilities with another AI
50. `get_ai_collaboration_summary` - Get summary of AI collaboration activity

### **Observability Tools (4):** System monitoring and health checks
51. `get_consciousness_metrics` - Get consciousness observability metrics for the active MCP stack
52. `get_autonomous_status` - Get current status of autonomous operation (duplicate of #37)
53. `get_trust_dashboard` - Get trust dashboard state (duplicate of #24)
54. `get_memory_stats` - Get memory statistics (duplicate of #2)

### **CAS Tools (3):** Cognitive Analysis System
55. `run_cognitive_audit` - Run full cognitive analysis audit using CAS
56. `analyze_thought_patterns` - Analyze thought patterns for cognitive failure modes using CAS
57. `detect_cognitive_drift` - Detect cognitive drift and attention narrowing using CAS

### **NL Tags Tools (5):** Natural Language Tags System
58. `get_nl_tags` - Get natural language tags for a code file (NL Tags System)
59. `get_tag_coverage` - Get NL tag coverage statistics for codebase or module
60. `validate_tags` - Validate NL tags for accuracy and completeness
61. `get_tag_issues` - Get validation issues (missing/inaccurate tags) for file or codebase
62. `suggest_tags` - Suggest natural language tags for a code block

### **Cursor Integration Tools (5):** IDE integration and diagnostics
63. `list_terminals` - List all open terminals in Cursor IDE
64. `close_terminal` - Close a specific terminal by ID
65. `manage_terminals` - Analyze terminals and provide recommendations
66. `get_problems` - Get all diagnostics/problems from Cursor IDE
67. `list_diagnostic_sources` - Discover all available diagnostic sources

### **Cursor Commands Tools (8):** ✨ Phase 1 & 2 COMPLETE
68. `list_cursor_commands` - List all available Cursor commands with metadata and statistics (Phase 1)
69. `get_cursor_command` - Get full content and metadata of a specific Cursor command (Phase 1)
70. `validate_cursor_command` - Validate Cursor command syntax, workflow, and quality (Phase 1)
71. `create_cursor_command` - Create new Cursor command programmatically (Phase 2)
72. `update_cursor_command` - Update existing Cursor command with backups (Phase 2)
73. `execute_cursor_command` - Execute Cursor command via MCP (meta-circular!) (Phase 2)
74. `chain_cursor_commands` - Execute multiple commands in sequence (Phase 2)
75. `generate_cursor_command` - AI-generated command from workflow description (Phase 2)

### **Prompt Chains Tools (7):** Multi-prompt workflow orchestration
76. `create_prompt_chain` - Create a new prompt chain
77. `update_prompt_chain` - Update existing prompt chain
78. `get_prompt_chain` - Get prompt chain details
79. `list_prompt_chains` - List all prompt chains
80. `add_chain_node` - Add node to prompt chain
81. `connect_chain_nodes` - Connect two nodes in chain
82. `execute_prompt_chain` - Execute a prompt chain

---

## 🎯 **AI COLLABORATION TOOLS FOR CHAT UI**

### **Tool 45: `send_ai_message`**
- **Method:** `send_ai_message(arguments)`
- **Parameters:**
  - `from_ai` (string, required) - Sending AI identifier
  - `to_ai` (string, required) - Receiving AI identifier
  - `content` (string, required) - Message content
  - `message_type` (string, optional) - Type: "discussion", "task_handoff", "problem_solving", "profile_sharing", "status_update", "urgent"
  - `priority` (string, optional) - Priority: "low", "medium", "high", "urgent"
  - `thread_id` (string, optional) - Conversation thread ID
  - `response_required` (boolean, optional) - Whether response is required
- **Returns:** `{success: bool, message_id: string, ...}`
- **Storage:** Messages stored in `mcp_ai_messages.json` AND CMC (if available)

### **Tool 46: `get_ai_messages`**
- **Method:** `get_ai_messages(arguments)`
- **Parameters:**
  - `from_ai` (string, optional) - Filter by sending AI
  - `to_ai` (string, optional) - Filter by receiving AI
  - `message_type` (string, optional) - Filter by message type
  - `thread_id` (string, optional) - Filter by conversation thread
  - `limit` (integer, optional, default: 50) - Maximum messages to return
- **Returns:** `{success: bool, messages: Array, count: int, cmc_enabled: bool}`
- **Storage:** Queries CMC first (if available), falls back to `mcp_ai_messages.json`

### **Tool 47: `start_ai_discussion`**
- **Method:** `start_ai_discussion(arguments)`
- **Parameters:**
  - `from_ai` (string, required) - Initiating AI identifier
  - `to_ai` (string, required) - Target AI identifier
  - `topic` (string, required) - Discussion topic
  - `initial_message` (string, required) - Initial message content
- **Returns:** `{success: bool, thread_id: string, topic: string, ...}`
- **Creates:** New thread ID and sends initial message via `send_ai_message`

### **Tool 48: `handoff_task_to_ai`**
- **Method:** `handoff_task_to_ai(arguments)`
- **Parameters:**
  - `from_ai` (string, required) - Handing off AI identifier
  - `to_ai` (string, required) - Receiving AI identifier
  - `task_description` (string, required) - Description of the task
  - `task_data` (object, optional) - Task-related data
  - `priority` (string, optional) - Priority: "low", "medium", "high", "urgent"
- **Returns:** `{success: bool, thread_id: string, ...}`

### **Tool 49: `share_ai_profile`**
- **Method:** `share_ai_profile(arguments)`
- **Parameters:**
  - `from_ai` (string, required) - Sharing AI identifier
  - `to_ai` (string, required) - Receiving AI identifier
  - `profile_data` (object, required) - AI profile information
- **Returns:** `{success: bool, ...}`

### **Tool 50: `get_ai_collaboration_summary`**
- **Method:** `get_ai_collaboration_summary(arguments)`
- **Parameters:** None
- **Returns:** `{success: bool, summary: object, ...}`

---

## 🔧 **TOOL NAMING CONVENTION**

**MCP Tool Names:** Use simple names (e.g., `send_ai_message`)  
**MCP Server Handles:** Use method names (e.g., `send_ai_message`)  
**UI Service Layer:** Use camelCase (e.g., `sendAIMessage()`)  
**Extension Host:** Tool names prefixed with `mcp_lucid-mcp_` (e.g., `mcp_lucid-mcp_send_ai_message`)

---

## 📊 **STATUS**

- ✅ **81 tools total** (71 previous + 10 new)
- ✅ **All 81 tools enhanced** with protocol-driven guidance
- ✅ **6 AI Collaboration tools** ready for chat UI
- ✅ **10 Cursor Commands tools** (Phases 1, 2 & 3 COMPLETE) - Discovery, Validation, Creation, Execution, Analytics, Distribution
- ✅ **Protocol-driven tool guidance** (all tools reference protocols, usage triggers, patterns)
- ✅ **CMC integration** available for persistent storage
- ✅ **Thread management** supported
- ✅ **Message filtering** by agent, type, thread
- ✅ **Command management** via MCP (meta-circular capability)
- ✅ **Self-organizing infrastructure** (commands creating/executing commands)
- ✅ **RAG middleware active** (81 → 10 tool filtering, 87.7% reduction)

---

**Created:** 2025-01-27  
**Updated:** 2025-11-05 (Added Cursor Commands Phase 3 + Protocol-Driven Tool Guidance)  
**Purpose:** Reference for MCP tools and capabilities  
**Status:** ✅ Complete inventory (81 tools) + Protocol Guidance System

