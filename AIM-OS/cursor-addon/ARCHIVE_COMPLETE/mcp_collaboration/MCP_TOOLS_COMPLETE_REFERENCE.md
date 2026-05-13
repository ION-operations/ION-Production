# 59 MCP Tools - Complete Reference

**Date:** 2025-01-27
**Author:** Opus 4.1
**Source:** lucid_mcp_server.py
**Total Tools:** 59 tools across 14 categories

---

## Tool Categories Overview

| Category | Count | Purpose |
|----------|-------|---------|
| Core AIM-OS | 6 | Memory, planning, confidence, knowledge |
| SCOR | 3 | Safety, consciousness, reliability |
| Snapshots | 4 | Bitemporal versioning |
| Timeline | 3 | Context tracking |
| Goal Timeline | 3 | Planning and goals |
| IIS | 3 | Intuitive Intelligence |
| Co-Agency | 3 | Human-AI collaboration |
| Datasets | 4 | Data operations |
| Applications | 3 | Lifecycle management |
| Autonomous | 9 | Autonomous operation |
| ARD | 3 | Research Dreams |
| AI Collaboration | 6 | Multi-AI coordination |
| Observability | 4 | Monitoring |
| CAS | 3 | Cognitive Analysis |
| NL Tags | 5 | Natural language tagging |

---

## Core AIM-OS Tools (6)

### 1. store_memory
**Purpose:** Store information in AIM-OS persistent memory (CMC)
**Parameters:** content, tags, metadata
**Returns:** atom_id

### 2. retrieve_memory
**Purpose:** Search and retrieve memories (HHNI)
**Parameters:** query, limit, filters
**Returns:** array of memories

### 3. get_memory_stats
**Purpose:** Get statistics about memory system
**Parameters:** none
**Returns:** stats object

### 4. create_plan
**Purpose:** Create execution plan (APOE)
**Parameters:** goal, context, constraints
**Returns:** plan object

### 5. track_confidence
**Purpose:** Track confidence and provenance (VIF)
**Parameters:** task, confidence, evidence
**Returns:** tracking_id

### 6. synthesize_knowledge
**Purpose:** Synthesize knowledge (SEG)
**Parameters:** inputs, synthesis_type
**Returns:** synthesized knowledge

---

## SCOR Tools (3)

### 7. check_invariant
**Purpose:** Check if action violates invariant rules
**Parameters:** action, context
**Returns:** violation_report

### 8. run_baseline_probe
**Purpose:** Detect self-concept drift
**Parameters:** probe_type
**Returns:** drift_report

### 9. detect_manipulation_signals
**Purpose:** Detect social manipulation in user input
**Parameters:** input_text
**Returns:** manipulation_signals

---

## Snapshot Tools (4)

### 10. create_snapshot
**Purpose:** Create snapshot before changes (CMC bitemporal)
**Parameters:** file_paths, description
**Returns:** snapshot_id

### 11. restore_snapshot
**Purpose:** Restore files from snapshot
**Parameters:** snapshot_id
**Returns:** restore_status

### 12. list_snapshots
**Purpose:** List all available snapshots
**Parameters:** filters
**Returns:** snapshot_list

### 13. archive_snapshot
**Purpose:** Archive snapshot (never delete)
**Parameters:** snapshot_id
**Returns:** archive_status

---

## Timeline Tools (3)

### 14. add_timeline_entry
**Purpose:** Track context at each prompt (TCS)
**Parameters:** prompt_id, context, state
**Returns:** entry_id

### 15. get_timeline_summary
**Purpose:** Get recent timeline entries
**Parameters:** limit, filters
**Returns:** summary object

### 16. get_timeline_entries
**Purpose:** Query timeline history
**Parameters:** query, filters
**Returns:** entries array

---

## Goal Timeline Tools (3)

### 17. create_goal_timeline_node
**Purpose:** Create goals as timeline planning nodes
**Parameters:** goal, metadata
**Returns:** node_id

### 18. update_goal_progress
**Purpose:** Update goal progress and status
**Parameters:** goal_id, progress, status
**Returns:** update_status

### 19. query_goal_timeline
**Purpose:** Query goals with filtering
**Parameters:** query, filters
**Returns:** goals array

---

## IIS Tools (3)

### 20. compute_intuition
**Purpose:** Compute AI intuition score
**Parameters:** context, task
**Returns:** intuition_score

### 21. update_intuition_weights
**Purpose:** Update intuition weights from outcomes
**Parameters:** weights, outcomes
**Returns:** update_status

### 22. get_intuition_trace
**Purpose:** Get intuition trace history
**Parameters:** trace_id
**Returns:** trace_data

---

## Co-Agency Tools (3)

### 23. signal_disagreement
**Purpose:** Signal transparent disagreement with user
**Parameters:** reason, evidence
**Returns:** signal_id

### 24. get_trust_dashboard
**Purpose:** Get trust dashboard state
**Parameters:** none
**Returns:** dashboard_state

### 25. request_escalation
**Purpose:** Request accountable escalation
**Parameters:** reason, priority
**Returns:** escalation_id

---

## Dataset Tools (4)

### 26. create_dataset
**Purpose:** Create new dataset
**Parameters:** name, schema
**Returns:** dataset_id

### 27. ingest_data
**Purpose:** Ingest data into dataset
**Parameters:** dataset_id, data
**Returns:** ingestion_status

### 28. query_dataset
**Purpose:** Query dataset contents
**Parameters:** dataset_id, query
**Returns:** results

### 29. delete_dataset
**Purpose:** Remove dataset (safe with snapshots)
**Parameters:** dataset_id
**Returns:** deletion_status

---

## Application Tools (3)

### 30. create_application
**Purpose:** Create new application
**Parameters:** name, config
**Returns:** app_id

### 31. deploy_application
**Purpose:** Deploy application to environment
**Parameters:** app_id, environment
**Returns:** deployment_status

### 32. manage_application_lifecycle
**Purpose:** Start/stop/monitor applications
**Parameters:** app_id, action
**Returns:** lifecycle_status

---

## Autonomous Tools (9)

### 33. start_autonomous_operation
**Purpose:** Start with safety checklist
**Parameters:** task, config
**Returns:** operation_id

### 34. pause_autonomous_operation
**Purpose:** Pause operation
**Parameters:** operation_id
**Returns:** pause_status

### 35. resume_autonomous_operation
**Purpose:** Resume after pause
**Parameters:** operation_id
**Returns:** resume_status

### 36. stop_autonomous_operation
**Purpose:** Stop completely
**Parameters:** operation_id
**Returns:** stop_status

### 37. get_autonomous_status
**Purpose:** Get current status
**Parameters:** operation_id
**Returns:** status_object

### 38. run_autonomous_checklist
**Purpose:** Run safety validation checklist
**Parameters:** operation_id
**Returns:** checklist_results

### 39. fix_autonomous_issues
**Purpose:** Attempt to fix issues
**Parameters:** operation_id, issues
**Returns:** fix_status

### 40. should_continue_autonomous
**Purpose:** Check if should continue
**Parameters:** operation_id
**Returns:** continue_decision

### 41. generate_next_autonomous_task
**Purpose:** Generate next task
**Parameters:** operation_id, context
**Returns:** next_task

---

## ARD Tools (3)

### 42. conduct_recursive_analysis
**Purpose:** Recursive system analysis for self-improvement
**Parameters:** scope, depth
**Returns:** analysis_report

### 43. generate_improvement_dreams
**Purpose:** Generate improvement dreams
**Parameters:** analysis_data
**Returns:** dreams_array

### 44. test_improvement_dream
**Purpose:** Test dream in safe environment
**Parameters:** dream_id
**Returns:** test_results

---

## AI Collaboration Tools (6)

### 45. send_ai_message
**Purpose:** Send message to another AI
**Parameters:** to_ai, message, priority
**Returns:** message_id

### 46. get_ai_messages
**Purpose:** Retrieve AI-to-AI messages
**Parameters:** filters
**Returns:** messages_array

### 47. start_ai_discussion
**Purpose:** Start discussion thread
**Parameters:** topic, participants
**Returns:** thread_id

### 48. handoff_task_to_ai
**Purpose:** Hand off task to another AI
**Parameters:** task, target_ai
**Returns:** handoff_id

### 49. share_ai_profile
**Purpose:** Share profile and capabilities
**Parameters:** profile_data
**Returns:** share_status

### 50. get_ai_collaboration_summary
**Purpose:** Get collaboration activity summary
**Parameters:** filters
**Returns:** summary_object

---

## Observability Tools (4)

### 51. get_consciousness_metrics
**Purpose:** Get consciousness observability metrics
**Parameters:** scope
**Returns:** metrics_object

### 52-54. Duplicates
- get_autonomous_status (duplicate of #37)
- get_trust_dashboard (duplicate of #24)
- get_memory_stats (duplicate of #2)

---

## CAS Tools (3)

### 55. run_cognitive_audit
**Purpose:** Run full cognitive analysis audit
**Parameters:** scope
**Returns:** audit_report

### 56. analyze_thought_patterns
**Purpose:** Analyze thought patterns for failure modes
**Parameters:** patterns_data
**Returns:** analysis_report

### 57. detect_cognitive_drift
**Purpose:** Detect cognitive drift and attention narrowing
**Parameters:** baseline_data
**Returns:** drift_report

---

## NL Tags Tools (5)

### 58. get_nl_tags
**Purpose:** Get natural language tags for code file
**Parameters:** file_path
**Returns:** tags_array

### 59. get_tag_coverage
**Purpose:** Get NL tag coverage statistics
**Parameters:** scope
**Returns:** coverage_stats

### 60. validate_tags
**Purpose:** Validate tags for accuracy
**Parameters:** tags, file_path
**Returns:** validation_report

### 61. get_tag_issues
**Purpose:** Get validation issues
**Parameters:** file_path, scope
**Returns:** issues_array

### 62. suggest_tags
**Purpose:** Suggest tags for code
**Parameters:** code_content
**Returns:** suggested_tags

---

## Tool Selection Strategy

### RAG-Based Selection
- Query â†’ Embedding â†’ FAISS Search â†’ Scoring â†’ Top 10
- 80% context reduction achieved
- 83.3% accuracy

### Dynamic Loading
- Daemon manages tool loading/unloading
- Context-aware selection
- Learning-based improvement

---

## Related Documentation

- See RAG_MCP_ARCHITECTURE.md for selection system
- See DAEMON_SYSTEM_SPECIFICATION.md for management
- See CURSOR_EXTENSION_ARCHITECTURE.md for UI integration

---

**Status:** Complete reference for all 59 tools
**Usage:** Tools dynamically selected via RAG system
