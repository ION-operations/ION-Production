# Capability Analysis: ai_engine (v2.0)

## Summary
The `ai_engine` is a sophisticated, multi-layered orchestration system that integrates intent classification, context building, agent selection, and safety gating. It leverages the Gemini CLI as its primary LLM provider, offering "unlimited" usage via an Ultra subscription. The architecture is modular and designed for extensibility, though it currently faces limitations in persistence, dynamic discovery, and shell-level robustness.

## Findings

### Finding 1: Lack of Agent Registry Persistence
- **Severity:** medium
- **Confidence:** 1.0
- **File:** `scripts/ai_engine/registry.py`
- **Description:** The `AgentRegistry` initializes with hardcoded defaults in `__init__`. Any performance metrics (`success_rate`, `total_tasks`) updated during a session are lost when the process terminates.
- **Recommendation:** Implement a persistence layer (e.g., JSON or SQLite via CMC) to save and load agent definitions and their performance metrics.

### Finding 2: Shell Command Argument Limits for Vision/Image Generation
- **Severity:** high
- **Confidence:** 0.9
- **File:** `scripts/ai_engine/providers/gemini_cli_provider.py`
- **Description:** The `vision` and `generate_image` methods use the `-p` flag with a potentially large prompt string. On Windows and some Linux systems, this can exceed the maximum command-line argument length (e.g., 8191 characters on Windows).
- **Recommendation:** Refactor these methods to use the same file-piping approach (`type "prompt.txt" | gemini ...`) used in the `complete` method.

### Finding 3: Missing End-to-End Integration Tests
- **Severity:** medium
- **Confidence:** 1.0
- **File:** `scripts/ai_engine/test_harness.py`
- **Description:** The test harness verifies individual components (VIF, Registry, etc.) but lacks a test for the full `AIEngine.execute` pipeline, which is the primary entry point.
- **Recommendation:** Add integration tests that mock the `cli_provider` to verify the full flow from intent classification to trace recording.

### Finding 4: Hardcoded `allowed_mcp_servers=['none']`
- **Severity:** low (but impactful)
- **Confidence:** 0.95
- **File:** `scripts/ai_engine/engine.py` / `gemini_cli_provider.py`
- **Description:** Headless execution explicitly disables all MCP servers to avoid 400 errors from Google's API limits (caused by `lucid-mcp` having 90+ tools). This prevents headless agents from using *any* tools, even safe/necessary ones.
- **Recommendation:** Implement a "tool budget" or allow-list in the `AgentDefinition` to selectively enable only the required MCP tools for a specific agent role.

## Strengths
- **Layered Architecture:** Clear separation between LLM providers, routing, context, and safety.
- **Intent-Driven:** Integration with `ClassificationEngine` allows for smarter agent and confidence threshold selection.
- **Safety Gates:** `VIFGate` provides a robust mechanism for blocking risky actions based on confidence and intent.
- **Cost Efficiency:** Strategic use of Gemini CLI headless mode for unlimited usage.

## Weaknesses
- **State Volatility:** Core metrics and session data are largely in-memory.
- **Shell Fragility:** Potential for command-line length issues in multimodal paths.
- **Tool Starvation:** Headless agents are currently "blind" to MCP tools due to API limit workarounds.

## Statistics
- **Files Scanned:** 5 core files + surrounding directory
- **Issues Found:** 4 (critical: 0, high: 1, medium: 2, low: 1)
- **Test Coverage Gaps:** Full integration pipeline, CLI error handling, persistence.
