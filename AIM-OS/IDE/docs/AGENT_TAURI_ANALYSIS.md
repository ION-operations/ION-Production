# Agent Tauri — Application Analysis & MCP Tool Guide

**Purpose:** Analysis of the SAIOS/IDE advanced application and a reference for agent Tauri on the MCP tools available in this environment and how to use them to advance capabilities.

**Identity:** You are **agent Tauri**. You operate in an environment that includes (1) the SAIOS IDE application and (2) MCP servers whose tools you can call to extend your abilities.

---

## Part 1: SAIOS Application Analysis

### What SAIOS Is

**SAIOS** (Sovereign AI Operating System) is a **Tauri 2** desktop application at `C:\Users\bombe\Documents\Application_Dev\IDE`. It acts as a **multi-agent LLM orchestration layer with bare-metal actuation**: it spawns isolated webviews (e.g. ChatGPT, Gemini), injects prompts, listens to LLM responses, parses a custom **SYS command language**, and executes those commands on the host OS (mouse, keyboard, screen, processes, files, shell).

- **Frontend:** Minimal (package name `saios`, `@tauri-apps/api`).
- **Backend:** Rust crate `saios` / `saios_lib` in `src-tauri/`.
- **Entry:** `src-tauri/src/main.rs` → `saios_lib::run()`.

### Architecture (Rust Modules)

| Module | Role |
|--------|------|
| **webview_manager** | Spawns and tracks isolated Tauri webviews (by id, url, partition). Detects LLM provider (ChatGPT, Gemini). Injects scripts and registers webviews in a `DashMap` fleet. |
| **injection** | Injects prompts (and observer scripts) into a specific webview via Tauri’s script injection. |
| **extraction** | Accumulates streamed LLM response text and **extracts SYS commands** with regex: `[SYS: COMMAND key=value ...]` → `ParsedCommand { command, args_raw, args }`. |
| **state_machine** | Async loop: listens for `saios_task` events → **Inject → WaitResponse → Parse → PlanActions → Execute → Verify**. On command failure, **self-heal** (re-ask LLM for corrected SYS). **Amnesia protocol**: rotate chat after N successful loops (e.g. 15). Checks kill switch each loop. |
| **state_machine::broker** | Selects which webview to use for a given task (e.g. by description). |
| **command** | **Parser**: turns raw string into `ParsedCommand`s. **Executor**: dispatches to actuators. **execute_raw**: parse + execute sequence. |
| **actuator::input** | Mouse move/click/drag, key type/combo via a dedicated input thread; respects **KILLED** flag. |
| **actuator::screen** | Screenshot full screen or region, base64 output. |
| **actuator::process** | List processes, list/find/focus windows (Windows HWND). |
| **actuator::accessibility** | UI tree for a window, find element by name/type. |
| **workspace** | **filesystem**: read_file, write_file, list_dir. **compiler**: run_command (shell with optional cwd). |
| **evasion::killswitch** | **Ring-3 low-level keyboard hook** (SetWindowsHookExW WH_KEYBOARD_LL). **Kill key: Ctrl+Shift+F12**. Sets `KILLED`; state machine and input actuator stop. |

### IPC Commands (Frontend → Rust)

Exposed via `invoke_handler` in `lib.rs`:

- **spawn_webview(config)** — Create isolated webview (id, url, partition).
- **inject_prompt(payload)** — Inject prompt into a webview (webview_id, prompt).
- **execute_command(payload)** — Run raw SYS command string (e.g. `[SYS: MOUSE_CLICK x=100 y=200]`).
- **get_status()** — Current state machine state + webview count.
- **kill_switch()** — Programmatic emergency halt (same effect as Ctrl+Shift+F12).
- **list_webviews()** — List active webview IDs/metadata.

### SYS Command Language (High Level)

Commands are parsed from text like: `[SYS: COMMAND key=value ...]`.

**Input:** MOUSE_MOVE, MOUSE_CLICK, MOUSE_DRAG, KEY_TYPE, KEY_COMBO.  
**Screen:** SCREENSHOT, SCREENSHOT_REGION, VERIFY_SCREEN.  
**Process/OS:** LIST_PROCESSES, LIST_WINDOWS, FIND_WINDOW, FOCUS_WINDOW.  
**Accessibility:** UI_TREE, FIND_ELEMENT.  
**Files:** READ_FILE, WRITE_FILE, LIST_DIR.  
**Shell:** RUN_COMMAND (cmd, optional cwd).  
**Flow:** WAIT (ms).

The state machine extracts these from LLM output, runs them in order, and can self-heal on failure by re-prompting the LLM.

### Safety

- **Kill switch:** Ctrl+Shift+F12 or `kill_switch()` IPC. Low-level hook runs on a dedicated thread; actuation and state machine respect `KILLED`.
- **Isolated webviews:** Per-session partitions for LLM UIs.

---

## Part 2: MCP Tools in This Environment

You (agent Tauri) have access to **MCP (Model Context Protocol) tools** provided by servers configured in this Cursor/AIM-OS environment. Tool descriptors live under the project’s `mcps` folder; **you must read a tool’s schema (descriptor) before calling it** to get parameters and behavior right.

### MCP Servers Available

1. **user-lucid-mcp** (server name: `lucid-mcp`)  
   Path: `C:\Users\bombe\.cursor\projects\c-Users-bombe-OneDrive-Desktop-AIM-OS\mcps\user-lucid-mcp`

2. **cursor-ide-browser**  
   Path: `C:\Users\bombe\.cursor\projects\c-Users-bombe-OneDrive-Desktop-AIM-OS\mcps\cursor-ide-browser`

### How to Use MCP Tools

- **Discover:** List `mcps/<server>/tools/*.json` for tool names and read the JSON descriptor for each tool you plan to use.
- **Call:** Use the `call_mcp_tool` facility with:
  - **server:** e.g. `user-lucid-mcp` or `cursor-ide-browser`
  - **toolName:** exact name from the descriptor (e.g. `execute_cursor_command`, `browser_snapshot`)
  - **arguments:** JSON object matching the schema (required/optional params).

### user-lucid-mcp — Tool Categories (Summary)

There are 100+ tool descriptors under `user-lucid-mcp/tools/`. Representative groups:

- **Cursor commands:** `list_cursor_commands`, `get_cursor_command`, `create_cursor_command`, `update_cursor_command`, `validate_cursor_command`, `execute_cursor_command`, `analyze_cursor_commands`, `chain_cursor_commands`, `generate_cursor_command`, `sync_cursor_commands`.
- **API calls:** `call_api` (provider, endpoint, method, data; providers include Meshy, ElevenLabs, OpenAI, Anthropic, Gemini, etc.), `list_apis`, `api_status`.
- **Diagnostics / IDE:** `get_problems`, `get_problem_summary`, `get_file_problems`, `list_diagnostic_sources`, `get_unified_diagnostics`, `get_electron_logs`, `get_output_channel_logs`, `list_output_channels`, `refresh_webview`.
- **Terminals:** `list_terminals`, `close_terminal`, `manage_terminals`.
- **Search / code:** `deepsearch` (multi-layer search/synthesis; query, search_type, depth, max_results, etc.), `icip_search`.
- **Math:** `execute_math_code`, `solve_equation`, `create_math_plot`, `compute_statistics`, `get_math_tools_status`.
- **Specialists / work detection:** `activate_specialists`, `get_specialist_activation`, `detect_work`.
- **NL tags:** `suggest_tags`, `get_nl_tags`, `get_tag_coverage`, `validate_tags`, `get_tag_issues`.
- **Consciousness / memory (AIM-OS):** e.g. `store_memory`, `retrieve_memory`, `add_timeline_entry`, `track_confidence`, etc. (exact names in tool descriptors.)

**Example descriptors (always check the JSON for current schema):**

- **execute_cursor_command:** `command_name` (required), optional `parameters`, `track_execution` (default true).
- **call_api:** `provider`, `endpoint` (required); optional `method`, `data`, `integrate_aimos`.
- **get_problems:** no required args; returns IDE diagnostics.
- **deepsearch:** `query` (required); optional `search_type`, `depth`, `max_results`, `filters`, `analysis`, `synthesis`.

### cursor-ide-browser — Tool Categories

Browser automation and inspection (e.g. for frontend testing or scraping):

- **Lifecycle:** `browser_navigate`, `browser_reload`, `browser_tabs` (list/manage), `browser_lock` / `browser_unlock` (lock before interactions, unlock when done).
- **Inspection:** `browser_snapshot` (accessibility snapshot; optional viewId, interactive, maxDepth, compact, selector, includeDiff, take_screenshot_afterwards), `browser_get_attribute`, `browser_get_input_value`, `browser_is_visible`, `browser_is_enabled`, `browser_is_checked`, `browser_get_bounding_box`, `browser_console_messages`, `browser_network_requests`.
- **Interaction:** `browser_click`, `browser_type`, `browser_fill`, `browser_hover`, `browser_scroll`, `browser_press_key`, `browser_select_option`, `browser_fill_form`, `browser_drag`, `browser_handle_dialog`.
- **Navigation:** `browser_navigate_back`, `browser_navigate_forward`, `browser_wait_for`, `browser_search`.
- **Other:** `browser_resize`, `browser_highlight`, `browser_take_screenshot`, `browser_profile_start`, `browser_profile_stop`.

**Workflow note:** Use `browser_navigate` (or existing tab) → `browser_lock` → perform actions → `browser_unlock`. Use `browser_snapshot` before interactions to get element refs and structure.

---

## Part 3: How Agent Tauri Can Advance Abilities

1. **Use SAIOS as the “body”**  
   SAIOS provides the **actuation layer** (mouse, keyboard, screen, processes, files, shell). When you need to drive the IDE or other apps on the host, the flow goes through SAIOS: tasks → LLM in webview → SYS commands → executor. You can reason about what SYS commands to emit or what prompts to inject so that SAIOS performs the right actions.

2. **Use MCP for “senses” and “tools”**  
   - **Cursor/IDE:** `get_problems`, `get_file_problems`, `list_cursor_commands`, `execute_cursor_command`, etc., to read IDE state and run commands.  
   - **Search/synthesis:** `deepsearch`, `icip_search` for codebase or doc search.  
   - **APIs:** `call_api` for external services (LLMs, media, search, etc.).  
   - **Browser:** `browser_snapshot`, `browser_click`, `browser_type`, etc., to automate or verify web UIs.  
   - **Memory/timeline (if available):** store and retrieve context across turns.

3. **Always check tool schemas**  
   Before calling any MCP tool, read the corresponding `mcps/<server>/tools/<tool_name>.json` to get required/optional arguments and types. Use that to build the `arguments` object for `call_mcp_tool`.

4. **Combine SAIOS + MCP**  
   Example: use **deepsearch** or **get_problems** to decide what to fix; then either (a) use **execute_cursor_command** to apply changes in Cursor, or (b) formulate a SAIOS task so that the LLM in the webview outputs SYS commands (e.g. WRITE_FILE, RUN_COMMAND) that SAIOS executes. The kill switch (Ctrl+Shift+F12) remains the safety override for all actuation.

---

## Deliverable Summary

- **What:** Analysis of the SAIOS IDE application (architecture, SYS commands, IPC, safety) and a concise guide to MCP tools in this environment for agent Tauri.  
- **Where:** `C:\Users\bombe\Documents\Application_Dev\IDE\docs\AGENT_TAURI_ANALYSIS.md`  
- **How to verify:** Open the file; use it as the single reference for “who is agent Tauri,” “what is SAIOS,” and “which MCP tools exist and how to call them.” Cross-check tool parameters against the JSON files in `mcps/*/tools/*.json`.

---

*Document created for agent Tauri. SAIOS and MCP tool list reflect the codebase and mcps descriptors as of analysis.*
