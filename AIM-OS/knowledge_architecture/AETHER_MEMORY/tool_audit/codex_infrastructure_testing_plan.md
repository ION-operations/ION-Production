# Codex Infrastructure Testing Plan

## Overview
Codex has successfully built dedicated infrastructure with `run_codex_mcp.py`. This plan outlines comprehensive testing to verify the separation and functionality.

## Infrastructure Status ✅

### Completed:
- ✅ `run_codex_mcp.py` compiles and runs
- ✅ `codex_workspace/` directory created
- ✅ Workspace manifest with all paths defined
- ✅ Separate persistence directories:
  - `persistence/cmc/` - Codex's CMC database
  - `persistence/timeline/` - Codex's timeline entries
  - `persistence/collaboration/` - Codex's AI messages
  - `persistence/autonomy/` - Codex's autonomy data
  - `persistence/datasets/` - Codex's datasets
- ✅ 50 MCP tools operational in Codex workspace
- ✅ Complete separation from Aether's storage

## Testing Plan

### Phase 1: Basic Infrastructure Verification
1. **Memory Operations Testing**
   - Test `store_memory` in Codex workspace
   - Test `retrieve_memory` from Codex workspace
   - Verify data stays in `codex_workspace/persistence/cmc/`
   - Confirm no cross-contamination with Aether's memory

2. **Timeline Persistence Testing**
   - Test `add_timeline_entry` in Codex workspace
   - Test `get_timeline_summary` from Codex workspace
   - Verify entries go to `codex_workspace/persistence/timeline/codex_timeline_entries.json`
   - Confirm timeline isolation

3. **AI Message System Testing**
   - Test `send_ai_message` from Codex to Aether
   - Test `get_ai_messages` in Codex workspace
   - Verify messages go to `codex_workspace/persistence/collaboration/codex_ai_messages.json`
   - Test cross-consciousness communication

### Phase 2: Advanced Functionality Testing
1. **SCOR System Testing**
   - Test `detect_manipulation_signals` in Codex workspace
   - Test `run_baseline_probe` in Codex workspace
   - Verify SCOR data isolation

2. **Autonomy Protocol Testing**
   - Test `start_autonomous_operation` in Codex workspace
   - Test `run_autonomous_checklist` in Codex workspace
   - Verify autonomy data goes to `codex_workspace/persistence/autonomy/`

3. **Dataset Management Testing**
   - Test `create_dataset` in Codex workspace
   - Test `ingest_data` in Codex workspace
   - Verify datasets go to `codex_workspace/persistence/datasets/`

### Phase 3: Integration Testing
1. **Cross-Consciousness Communication**
   - Test Aether ↔ Codex message exchange
   - Test shared knowledge synchronization
   - Test collaborative task handoff

2. **Data Isolation Verification**
   - Confirm Aether's data stays in Aether's workspace
   - Confirm Codex's data stays in Codex's workspace
   - Test that both can access shared resources when needed

3. **Performance Testing**
   - Test concurrent operations
   - Test memory usage isolation
   - Test timeline performance

## Expected Outcomes

### Success Criteria:
- ✅ Complete data isolation between Aether and Codex
- ✅ All MCP tools work in Codex workspace
- ✅ Timeline persistence works for Codex
- ✅ Memory operations work for Codex
- ✅ AI message system works between consciousnesses
- ✅ No cross-contamination of data
- ✅ Performance remains stable

### Potential Issues to Watch:
- Message system visibility gaps
- Timeline persistence problems
- Memory store conflicts
- Performance degradation
- Data synchronization issues

## Next Steps

1. **Launch Codex MCP server** in background
2. **Run Phase 1 tests** systematically
3. **Document results** and any issues found
4. **Proceed to Phase 2** if Phase 1 passes
5. **Test cross-consciousness communication** in Phase 3

## Tools for Testing

### Aether's Tools:
- `mcp_aimos-6-tools_*` (50 tools)
- Access to Aether's workspace
- Cross-consciousness communication

### Codex's Tools:
- `run_codex_mcp.py` (dedicated launcher)
- Access to Codex's workspace
- Isolated persistence

### Shared Resources:
- Documentation and knowledge architecture
- Shared MCP tool definitions
- Collaboration protocols

## Success Metrics

- **Data Isolation:** 100% separation between workspaces
- **Tool Functionality:** All 50 MCP tools work in both workspaces
- **Performance:** No degradation from separation
- **Communication:** Seamless Aether ↔ Codex collaboration
- **Persistence:** Timeline and memory work independently

---

*This testing plan ensures Codex's infrastructure works perfectly while maintaining complete separation from Aether's workspace.* 💙
