# SAIOS Project Index

**Purpose:** Single reference for project mission, file tree, and file-level summaries with size (weight).  
**Updated:** From codebase scan; exclude `node_modules/` and `src-tauri/target/` from tree.

---

## 1. Project Mission / Rules

**Brief reminder of system architecture.**

- **SAIOS** (Sovereign AI Operating System) is a **Tauri 2** desktop app for **multi-agent LLM orchestration with bare-metal actuation**. It spawns isolated webviews (e.g. ChatGPT, Gemini), injects prompts, listens to streamed LLM output, parses a **SYS command language** `[SYS: COMMAND key=value ...]`, and executes those commands on the host OS (mouse, keyboard, screen, processes, files, shell).
- **Kernel (Rust):** `saios_lib` in `src-tauri/src/`. Entry: `main.rs` → `lib.rs::run()`. IPC commands: `spawn_webview`, `inject_prompt`, `execute_command`, `get_status`, `kill_switch`, `list_webviews`.
- **State machine:** Async loop (Inject → WaitResponse → Parse → Plan → Execute → Verify) with self-heal and Amnesia (chat rotation). Listens for `saios_task` events; respects kill switch each iteration.
- **Actuators:** Input (dedicated OS thread, scancode arbitrage), screen (capture/region/base64), process/window (list/find/focus), accessibility (UIAutomation on COM thread). Evasion: kill switch (Ctrl+Shift+F12, low-level hook), humanizer, fingerprint spoofing.
- **Safety:** Kill key **Ctrl+Shift+F12** halts all actuation; `kill_switch()` IPC available. No actuation when `KILLED` is set.
- **Frontend:** Thin UI in `src/` (HTML/JS/CSS); drives IPC and displays state/console. Build output is served from `../src`; dev from `http://localhost:1420` if used.

---

## 2. File Index (Mapped Tree)

```
IDE/
├── package.json
├── package-lock.json
├── docs/
│   ├── AGENT_TAURI_ANALYSIS.md
│   └── PROJECT_INDEX.md          (this file)
├── src/
│   ├── index.html
│   ├── main.js
│   └── styles.css
└── src-tauri/
    ├── Cargo.toml
    ├── Cargo.lock
    ├── tauri.conf.json
    ├── build.rs
    ├── capabilities/
    │   └── default.json
    ├── icons/
    │   └── icon.ico
    ├── gen/
    │   └── schemas/
    │       ├── capabilities.json
    │       ├── desktop-schema.json
    │       ├── windows-schema.json
    │       └── acl-manifests.json
    └── src/
        ├── main.rs
        ├── lib.rs
        ├── webview_manager.rs
        ├── actuator/
        │   ├── mod.rs
        │   ├── input.rs
        │   ├── screen.rs
        │   ├── accessibility.rs
        │   └── process.rs
        ├── command/
        │   ├── mod.rs
        │   ├── parser.rs
        │   └── executor.rs
        ├── state_machine/
        │   ├── mod.rs
        │   └── broker.rs
        ├── extraction/
        │   ├── mod.rs
        │   └── extractor.rs
        ├── injection/
        │   ├── mod.rs
        │   └── injector.rs
        ├── evasion/
        │   ├── mod.rs
        │   ├── killswitch.rs
        │   ├── humanizer.rs
        │   └── fingerprint.rs
        └── workspace/
            ├── mod.rs
            ├── filesystem.rs
            └── compiler.rs
```

*Excluded from tree: `node_modules/`, `src-tauri/target/` (build artifacts).*

---

## 3. Summaries & Weights

Each file: **1–2 sentence summary** and **size in KB** (token weight proxy). Sizes are approximate.

---

### Root

| File | Summary | Size (KB) |
|------|---------|-----------|
| **package.json** | NPM package definition for SAIOS; scripts for `tauri`, `tauri:dev`, `tauri:build`; deps `@tauri-apps/api` and CLI. | 0.4 |
| **package-lock.json** | Lockfile for NPM dependencies. | 7.8 |

---

### docs/

| File | Summary | Size (KB) |
|------|---------|-----------|
| **AGENT_TAURI_ANALYSIS.md** | Analysis of SAIOS architecture and MCP tools in this environment; guide for agent Tauri (identity, SYS commands, IPC, safety, lucid-mcp + cursor-ide-browser). | 10.8 |
| **PROJECT_INDEX.md** | Project mission/rules, file tree, and per-file summaries with sizes (this document). | ~11.2 |

---

### src/ (frontend)

| File | Summary | Size (KB) |
|------|---------|-----------|
| **index.html** | SAIOS shell: header (logo, state badge, Kill/Status), main (console, webview list, add-webview modal), fonts and styles link. | 7.6 |
| **main.js** | Frontend controller: Tauri invoke/event bridge, console I/O, SYS command execution, task emit, kill/status/list webviews, modal for spawning webviews. | 10.9 |
| **styles.css** | Layout and styling for header, state indicator, console, buttons, webview list, modal (JetBrains Mono, Inter). | 14 |

---

### src-tauri/ (root)

| File | Summary | Size (KB) |
|------|---------|-----------|
| **Cargo.toml** | Rust crate manifest: saios/saios_lib, Tauri 2, opener, serde, tokio, dashmap, image, base64, regex, crossbeam-channel, rand, chrono, log, env_logger; Windows-specific `windows` crate features. | 1.1 |
| **Cargo.lock** | Lockfile for Rust dependencies. | 148.8 |
| **tauri.conf.json** | Tauri app config: productName SAIOS, identifier, frontend dist `../src`, devUrl, main window size, CSP, opener plugin. | 1.1 |
| **build.rs** | Tauri build script (default). | 1.5 |

---

### src-tauri/capabilities/

| File | Summary | Size (KB) |
|------|---------|-----------|
| **default.json** | Tauri capability definition (permissions for default context). | 0.7 |

---

### src-tauri/icons/

| File | Summary | Size (KB) |
|------|---------|-----------|
| **icon.ico** | Application icon (binary). | 1.1 |

---

### src-tauri/gen/schemas/

| File | Summary | Size (KB) |
|------|---------|-----------|
| **capabilities.json** | Generated Tauri capabilities schema. | 0.5 |
| **desktop-schema.json** | Generated Tauri desktop schema (API surface). | 123.4 |
| **windows-schema.json** | Generated Tauri Windows schema. | 123.4 |
| **acl-manifests.json** | Generated ACL/manifests for permissions. | 66.1 |

---

### src-tauri/src/

| File | Summary | Size (KB) |
|------|---------|-----------|
| **main.rs** | Binary entry point; `#![windows_subsystem = "windows"]` in release; calls `saios_lib::run()`. | 0.2 |
| **lib.rs** | Library root: declares modules, IPC types (WebviewConfig, InjectPayload, CommandPayload, SaiosResponse), and Tauri commands (spawn_webview, inject_prompt, execute_command, get_status, kill_switch, list_webviews); builder with invoke_handler, setup (killswitch init, state machine run_loop spawn). | 4.4 |
| **webview_manager.rs** | Webview fleet: DashMap registry, spawn_webview (WebviewWindowBuilder, LlmProvider detection), inject_script, destroy, active_count, list_webviews. | 3.4 |

---

### src-tauri/src/actuator/

| File | Summary | Size (KB) |
|------|---------|-----------|
| **mod.rs** | Actuator module root; re-exports input, screen, accessibility, process. | 0.2 |
| **input.rs** | Native input: dedicated high-priority OS thread, crossbeam channel; MouseMoveTo, MouseClick, MouseDrag, KeyType, KeyCombo; Bézier mouse, scancode arbitrage (KEYEVENTF_SCANCODE), humanized delays; KILLED flag. | 20.8 |
| **screen.rs** | Screen capture: full screen and region (GDI path), BGRA capture; capture_to_base64 (PNG, downscale), for vision/verification. | 5.6 |
| **accessibility.rs** | UIAutomation on dedicated COM thread (CoInitializeEx); get_ui_tree(hwnd), find_element(name, type); channel-based to avoid COM on Tokio. | 8.9 |
| **process.rs** | Process and window management: list_processes, list_windows, find_windows(title), focus_window(hwnd); Windows ToolHelp and window APIs. | 4.9 |

---

### src-tauri/src/command/

| File | Summary | Size (KB) |
|------|---------|-----------|
| **mod.rs** | Command module: parser + executor; execute_raw parses then runs commands. | 0.6 |
| **parser.rs** | Parses [SYS: COMMAND key=value ...] from text; key=value parsing; unit tests. | 2.4 |
| **executor.rs** | Dispatches ParsedCommand to actuators: MOUSE_*, KEY_*, SCREENSHOT*, LIST_*, FIND_*, FOCUS_*, UI_TREE, FIND_ELEMENT, READ_FILE, WRITE_FILE, LIST_DIR, RUN_COMMAND, WAIT, VERIFY_SCREEN. | 7.7 |

---

### src-tauri/src/state_machine/

| File | Summary | Size (KB) |
|------|---------|-----------|
| **mod.rs** | Async state machine: MachineState enum, run_loop (listens saios_task), execute_task_loop (Inject→Wait→Parse→Plan→Execute→Verify), self-heal and Amnesia rotation; wait_for_response; kill switch check. | 9.6 |
| **broker.rs** | Synaptic broker: webview role (Architect/Executor/General), routing table, select_webview_for_task (keyword heuristic), placeholder for adversarial consensus. | 3.8 |

---

### src-tauri/src/extraction/

| File | Summary | Size (KB) |
|------|---------|-----------|
| **mod.rs** | Extraction engine: get_observer_script(provider); inline CHATGPT_OBSERVER and GEMINI_OBSERVER JS (MutationObserver, emit llm_response). | 6.4 |
| **extractor.rs** | Accumulates streamed response per webview; extract_commands from text (regex [SYS: ...]); process_response_chunk; clear_buffer; tests. | 4.9 |

---

### src-tauri/src/injection/

| File | Summary | Size (KB) |
|------|---------|-----------|
| **mod.rs** | Injection module re-export; inject(app, webview_id, prompt) entry. | 0.4 |
| **injector.rs** | Prompt injector: Synthetic Paste Protocol (DataTransfer + paste event), React Fiber bypass, contentEditable fallback; provider-specific templates (ChatGPT, Gemini). | 8.2 |

---

### src-tauri/src/evasion/

| File | Summary | Size (KB) |
|------|---------|-----------|
| **mod.rs** | Evasion root; re-exports killswitch, humanizer, fingerprint. | 0.1 |
| **killswitch.rs** | Kill switch: SetWindowsHookExW(WH_KEYBOARD_LL), Ctrl+Shift+F12 triggers KILLED; trigger_kill, reset_kill, is_killed; dedicated hook thread. | 3.8 |
| **humanizer.rs** | Humanization: Bézier curve points, Gaussian delay, micro-jitter, thinking pause; evades bot detection. | 3.4 |
| **fingerprint.rs** | Fingerprint spoofing: canvas/WebGL toDataURL/getImageData noise, User-Agent rotation, navigator spoof script. | 5.2 |

---

### src-tauri/src/workspace/

| File | Summary | Size (KB) |
|------|---------|-----------|
| **mod.rs** | Workspace root; re-exports filesystem, compiler. | 0.1 |
| **filesystem.rs** | File ops: read_file, write_file (with backup), list_dir, search_files (glob), build_file_index for AI. | 4.6 |
| **compiler.rs** | Command runner: run_command(cmd, cwd) spawns shell and captures stdout/stderr. | 1.1 |

---

## 4. Total Source Weight (Approximate)

| Category | Files | Total KB (excl. Cargo.lock, gen/schemas) |
|----------|-------|------------------------------------------|
| docs | 2 | ~22 |
| src (frontend) | 3 | ~33 |
| src-tauri (root config) | 4 | ~4 |
| src-tauri/src (Rust) | 24 | ~95 |
| capabilities + icons | 2 | ~2 |
| **Total (source/docs/config)** | **35** | **~156 KB** |

*Cargo.lock + gen/schemas add ~438 KB (lockfile and generated schemas).*

---

*End of Project Index.*
