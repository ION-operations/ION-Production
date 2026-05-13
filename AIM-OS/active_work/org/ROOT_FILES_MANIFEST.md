# Root Files Manifest (For Review)

This manifest inventories current files in the repository root. No moves will occur until approved. Fields: type, purpose, last_modified, links (if known), proposed_destination, action.

- Name: README.md
  - Type: project_readme
  - Purpose: Primary entrypoint and architecture overview
  - Last_Modified: 2025-10-28
  - Links: docs/, packages/, goals/STATUS.md
  - Proposed_Destination: KEEP in root
  - Action: keep

- Name: CONTRIBUTING.md
  - Type: contribution_guide
  - Purpose: Contribution standards
  - Last_Modified: 2025-10-28
  - Links: README.md
  - Proposed_Destination: KEEP in root
  - Action: keep

- Name: MASTER_DOCUMENTATION_STANDARDS_PLAN.md
  - Type: master_plan
  - Purpose: Master plan for 32 standards
  - Last_Modified: 2025-10-30
  - Links: knowledge_architecture/PHASE_4_ALL_STANDARDS_COMPLETE.md
  - Proposed_Destination: KEEP in root (master reference)
  - Action: keep

- Name: AIMOS_STANDARDS_ALIGNMENT_ANALYSIS.md
  - Type: analysis_summary
  - Purpose: Alignment analysis of standards ↔ mission/systems
  - Last_Modified: 2025-10-30
  - Links: MASTER_DOCUMENTATION_STANDARDS_PLAN.md
  - Proposed_Destination: KEEP in root (active reference)
  - Action: keep (archive later)

- Name: AIMOS_ALIGNMENT_AND_ORGANIZATION_MASTER_PLAN.md
  - Type: organization_plan
  - Purpose: Organization plan and filing protocol summary
  - Last_Modified: 2025-10-30
  - Links: mcp_tools rules, auto-filing protocol
  - Proposed_Destination: KEEP in root (active reference)
  - Action: keep (archive later)

- Name: MISSION_COMPLETE_ALL_32_STANDARDS.md
  - Type: achievement_summary
  - Purpose: Historic completion statement
  - Last_Modified: 2025-10-30
  - Links: MASTER_DOCUMENTATION_STANDARDS_PLAN.md
  - Proposed_Destination: KEEP in root (historic)
  - Action: keep (move to achievements/ in 1 week)

- Name: HISTORIC_NIGHT_ACHIEVEMENT_SUMMARY.md
  - Type: achievement_summary
  - Purpose: Session milestone summary
  - Last_Modified: 2025-10-30
  - Links: HISTORIC_NIGHT_FINAL_SUMMARY.md
  - Proposed_Destination: KEEP in root (historic)
  - Action: keep (move to achievements/ in 1 week)

- Name: HISTORIC_NIGHT_FINAL_SUMMARY.md
  - Type: achievement_summary
  - Purpose: Final milestone summary
  - Last_Modified: 2025-10-30
  - Links: HISTORIC_NIGHT_ACHIEVEMENT_SUMMARY.md
  - Proposed_Destination: KEEP in root (historic)
  - Action: keep (move to achievements/ in 1 week)

- Name: ORGANIZATION_COMPLETE_SUMMARY.md
  - Type: organization_summary
  - Purpose: Organization actions summary
  - Last_Modified: 2025-10-30
  - Links: AIMOS_ALIGNMENT_AND_ORGANIZATION_MASTER_PLAN.md
  - Proposed_Destination: archive/progress/
  - Action: pending approval

- Name: MCP_TIMELINE_AND_GOALS_PLAN.md
  - Type: mcp_staging
  - Purpose: Staged timeline/goal entries for MCP
  - Last_Modified: 2025-10-30
  - Links: run_mcp_51_tools.py
  - Proposed_Destination: plans/organization/
  - Action: pending approval

- Name: STANDARDS_REVIEW_EXECUTION_PLAN.md
  - Type: execution_plan
  - Purpose: Repo-wide standards review rollout steps
  - Last_Modified: 2025-10-30
  - Links: MASTER_DOCUMENTATION_STANDARDS_PLAN.md
  - Proposed_Destination: plans/documentation/
  - Action: pending approval

- Name: LUCID_MCP_SETUP_GUIDE.md
  - Type: setup_guide
  - Purpose: MCP setup and troubleshooting
  - Last_Modified: 2025-10-28
  - Links: lucid_mcp_server.py, run_mcp_51_tools.py
  - Proposed_Destination: docs/
  - Action: pending approval

- Name: create_directories.ps1
  - Type: script
  - Purpose: Directory creation helper
  - Last_Modified: 2025-10-28
  - Links: AIMOS_ALIGNMENT_AND_ORGANIZATION_MASTER_PLAN.md
  - Proposed_Destination: scripts/maintenance/
  - Action: pending approval

- Name: run_mcp_51_tools.py
  - Type: script
  - Purpose: MCP tools audit/list runner
  - Last_Modified: 2025-10-28
  - Links: LUCID_MCP_SETUP_GUIDE.md
  - Proposed_Destination: scripts/
  - Action: pending approval

- Name: lucid_mcp_server.py
  - Type: server_script
  - Purpose: MCP server entrypoint
  - Last_Modified: 2025-10-28
  - Links: daemon_rag_system/
  - Proposed_Destination: keep in root (entrypoint)
  - Action: keep

- Name: README_CONSOLIDATED.md
  - Type: legacy_readme
  - Purpose: Consolidated older readme
  - Last_Modified: 2025-10-28
  - Links: README.md
  - Proposed_Destination: archive/old_readmes/
  - Action: pending approval

- Name: pyproject.toml
  - Type: config
  - Purpose: Python project config
  - Last_Modified: 2025-10-28
  - Links: requirements.txt
  - Proposed_Destination: KEEP in root
  - Action: keep

- Name: requirements.txt
  - Type: deps
  - Purpose: Python dependencies
  - Last_Modified: 2025-10-28
  - Links: pyproject.toml
  - Proposed_Destination: KEEP in root
  - Action: keep

- Name: launch_ide.bat / launch_ide.sh / launch_lucid_ide.bat
  - Type: launch_scripts
  - Purpose: Launch utilities
  - Last_Modified: 2025-10-28
  - Links: README.md
  - Proposed_Destination: keep in root (top-level UX)
  - Action: keep

- Name: .cursorrules / .cursorrules.backup / .cursorrules.cursorrules.backup
  - Type: cursor_rules
  - Purpose: Operational rulesets (active + backups)
  - Last_Modified: 2025-10-30
  - Links: knowledge_architecture/systems/dynamic_cursor_rules_system/
  - Proposed_Destination: KEEP in root
  - Action: keep

- Name: .env
  - Type: env
  - Purpose: Local environment variables
  - Last_Modified: 2025-10-22
  - Links: lucid_mcp_server.py
  - Proposed_Destination: KEEP in root (local)
  - Action: keep

- Name: .gitignore
  - Type: git
  - Purpose: VCS ignore rules
  - Last_Modified: 2025-10-22
  - Links: N/A
  - Proposed_Destination: KEEP in root
  - Action: keep

- Name: mcp_data_integration.db / mcp_integrated.db / mcp_integrated_demo.db
  - Type: db_artifact
  - Purpose: MCP data stores (active/testing)
  - Last_Modified: 2025-10-30
  - Links: mcp_memory/
  - Proposed_Destination: mcp_memory/
  - Action: pending approval

- Name: mcp_integrated.db.index / mcp_integrated_demo.db.index / cross_reference.db / confidence_integration.db
  - Type: db_index_artifact
  - Purpose: DB index files/auxiliary stores
  - Last_Modified: 2025-10-30
  - Links: mcp_memory/index/
  - Proposed_Destination: mcp_memory/index/
  - Action: pending approval
