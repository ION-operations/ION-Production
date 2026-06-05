export type IonAuthorityClass =
  | 'ACTIVE_RUNTIME_AUTHORITY'
  | 'ACCEPTED_TASK_RETURN'
  | 'PENDING_TASK_RETURN'
  | 'REJECTED_TASK_RETURN'
  | 'HUMAN_GATE_REQUIRED'
  | 'LEGACY_CONTEXT_WITNESS'
  | 'DONOR_REFERENCE'
  | 'FORBIDDEN_CAPABILITY'
  | string;

export type IonTimelineEvent = {
  time: string;
  source: string;
  event_type: string;
  status: string;
  path?: string;
  detail?: string;
};

export type IonLaneTimelineEvent = {
  id: string;
  message_id?: string;
  utterance_id?: string;
  atom_id?: string;
  timestamp: string;
  organ: string;
  requested_lane?: string;
  effective_lane?: string;
  lane_change_reason?: string;
  claim_class?: string;
  authority_verdict?: string;
  receipt_id?: string;
  repair_id?: string;
  source_path?: string;
  status: string;
  latency_ms?: number;
};

export type IonReceiptHydrationRecord = {
  receipt_id: string;
  repair_id?: string;
  utterance_id?: string;
  atom_id?: string;
  resolved_bubble_id?: string;
  resolution_method: string;
  confidence: string;
  claim_class?: string;
  authority_verdict?: string;
  latest_effective: boolean;
  supersedes?: string[];
  superseded_by?: string;
  source_receipt_path?: string;
  db_row_id?: string;
  warning?: string;
};

export type IonRuntimeDebugOverlay = {
  schema_id?: string;
  generated_at?: string;
  window_seconds?: number;
  sse?: Record<string, unknown>;
  render?: Record<string, unknown>;
  hydration?: Record<string, unknown>;
  kernel?: Record<string, unknown>;
  watcher?: Record<string, unknown>;
  status?: string;
};

export type IonSafeFullProjectPackage = {
  schema_id?: string;
  accepted?: boolean;
  zip_path?: string;
  zip_sha256?: string;
  production_authority?: boolean;
  zip_root_audit?: {
    verdict?: string;
    archive_root_mode?: string;
    wrapped_root_prefix?: string | null;
    missing_at_archive_root?: string[];
  };
  preservation_report?: {
    files_before?: number;
    files_after?: number;
    added_files?: number;
    modified_files?: number;
    removed_files?: number;
    protected_removed_files?: number;
    unexpected_removed_files?: number;
    packaging_verdict?: string;
  };
};

export type IonV72McpDonorReconciliation = {
  schema_id?: string;
  version_line?: string;
  reconciliation_verdict?: string;
  donor_scope?: string;
  restored_donor_surface_count?: number;
  missing_donor_surface_count?: number;
  forbidden_runtime_file_count?: number;
  cursor_bridge_preserved?: boolean;
  donor_runtime_receipts_restored?: boolean;
  live_execution_authority?: boolean;
  production_authority?: boolean;
};

export type IonFrontDoorProofTrace = {
  schema_id?: string;
  trace_id?: string;
  generated_at?: string;
  projection_mode?: string;
  session_id?: string;
  proof_complete?: boolean;
  verdict?: string;
  operator_message?: string;
  controlled_system_output?: string;
  boundary_proof?: Record<string, unknown>;
  steward_verdict?: Record<string, unknown>;
  receipts?: Record<string, unknown>;
  stage_sequence?: Array<{
    sequence?: number;
    stage?: string;
    organ?: string;
    status?: string;
    artifact_id?: string;
    witness_path?: string;
    receipt_id?: string;
    detail?: string;
  }>;
  witness_paths?: string[];
  missing_witness_paths?: string[];
  production_authority?: boolean;
  live_execution_authority?: boolean;
};

export type IonSpawnRow = {
  index: string | number;
  role: string;
  spawn: boolean;
  status: string;
  context_package_path?: string;
  context_load_receipt_path?: string;
  authority_class?: IonAuthorityClass;
  return_recorded?: boolean;
};

export type IonTaskReturn = {
  role: string;
  index: string | number;
  decision: string;
  path?: string;
  authority_class?: IonAuthorityClass;
};

export type IonQueueState = {
  operator_messages: Record<string, unknown>[];
  human_gates: Record<string, unknown>[];
  steward_integration: Record<string, unknown>[];
};

export type IonLocalServiceStatus = {
  schema_id: 'ion.local_service_status.v1';
  generated_at: string;
  verdict: string;
  status: string;
  probe_http: boolean;
  service_count: number;
  ready_count: number;
  not_running_count: number;
  degraded_count: number;
  missing_template_count: number;
  services: Array<{
    service_id: string;
    unit_name: string;
    role: string;
    local_url?: string | null;
    health_url?: string | null;
    public_url?: string | null;
    tunnel_name?: string | null;
    status: string;
    findings: string[];
    production_authority: boolean;
    live_execution_authority: boolean;
  }>;
  install_authority: boolean;
  production_authority: boolean;
  live_execution_authority: boolean;
};

export type IonHelixionJocRebuildProjection = {
  schema_id?: string;
  status?: string;
  decision?: string;
  master_plan_path?: string;
  registry_path?: string;
  current_plan_path?: string;
  master_plan_present?: boolean;
  registry_present?: boolean;
  current_plan_present?: boolean;
  ready_for_phase_1?: boolean;
  phase_0_gate?: Record<string, unknown>;
  product_roles?: Record<string, string>;
  required_surfaces?: string[];
  canonical_zones?: string[];
  canonical_object_types?: string[];
  allowed_v1_capabilities?: string[];
  forbidden_v1_capabilities?: string[];
  next_build_sequence?: string[];
  source_authorities?: string[];
  orchestration_context_package?: Record<string, unknown>;
  local_shell?: Record<string, unknown>;
  react_bundle?: Record<string, unknown>;
  development_urls?: string[];
  latest_capsule_entry_id?: string;
  latest_history_receipt?: string;
  latest_codex_solo_checkpoint_id?: string;
  authority_posture?: Record<string, unknown>;
  production_authority?: boolean;
  live_execution_authority?: boolean;
  unrestricted_browser_control?: boolean;
};

export type IonVNextAuthorityFlags = {
  production_authority?: boolean;
  live_execution_authority?: boolean;
  accepted_state_claim?: boolean;
  secrets_authority?: boolean;
  supabase_mutated?: boolean;
};

export type IonVNextPacket = {
  sequence_id: string;
  token: string;
  title?: string;
  status: string;
  packet_id?: string;
  verdict?: string;
  created_at?: string;
  packet_path?: string | null;
  result_path?: string | null;
  artifact_root?: string | null;
  release_artifact_count?: number;
  closed_gates?: string[];
  remaining_gates?: string[];
  reviewed_gates?: string[];
  non_claims?: string[];
  authority_flags?: IonVNextAuthorityFlags;
  next_route?: string;
  next_route_condition?: string;
};

export type IonVNextLane = {
  lane_id: string;
  label: string;
  status: string;
  posture?: string;
  evidence_path?: string;
};

export type IonVNextGate = {
  gate_id: string;
  status: string;
  latest_packet?: string;
};

export type IonVNextDriftGuard = {
  guard_id: string;
  status: string;
  detail?: string;
  items?: string[];
};

export type IonVNextMissionFamily = {
  family_id: string;
  label: string;
  description?: string;
  packet_count?: number;
  epoch_count?: number;
  protocol_count?: number;
  context_package_count?: number;
  evidence_paths?: string[];
  status?: string;
};

export type IonVNextLongHorizonEpoch = {
  epoch_id?: string;
  date_start?: string;
  date_end?: string;
  row_start?: string;
  row_end?: string;
  row_count?: number;
  status_counts?: Record<string, number>;
  family_id?: string;
  evidence_refs?: string[];
  summaries?: Array<{
    id?: string;
    date?: string;
    status?: string;
    summary?: string;
  }>;
};

export type IonVNextLongHorizon = {
  schema_id?: string;
  generated_at?: string;
  source_path?: string;
  capsule_entry_count?: number;
  epoch_count?: number;
  production_authority?: boolean;
  live_execution_authority?: boolean;
  family_counts?: Array<{
    family_id: string;
    label?: string;
    epoch_count?: number;
  }>;
  latest_epochs?: IonVNextLongHorizonEpoch[];
  epochs?: IonVNextLongHorizonEpoch[];
};

export type IonVNextProtocolRow = {
  path: string;
  name?: string;
  title?: string;
  kind?: string;
  family_id?: string;
  authority?: string;
  status?: string;
  type?: string;
  bytes?: number;
};

export type IonVNextProtocolInventory = {
  schema_id?: string;
  generated_at?: string;
  source_roots?: string[];
  protocol_count?: number;
  groups?: Array<{
    family_id: string;
    label?: string;
    protocol_count?: number;
    authority_count?: number;
    sample_paths?: string[];
  }>;
  rows?: IonVNextProtocolRow[];
};

export type IonVNextContextPackageProjection = {
  schema_id?: string;
  generated_at?: string;
  source_path?: string;
  package_count?: number;
  missing_ref_count?: number;
  packages?: Array<{
    package_id?: string;
    context_type?: string;
    load_policy?: string;
    family_id?: string;
    path_refs?: string[];
    missing_refs?: string[];
    window?: Record<string, unknown>;
  }>;
};

export type IonVNextDocumentationSurfaces = {
  schema_id?: string;
  generated_at?: string;
  surface_count?: number;
  file_count?: number;
  surfaces?: Array<{
    surface_id: string;
    label?: string;
    root?: string;
    exists?: boolean;
    file_count?: number;
    sample_paths?: string[];
  }>;
};

export type IonVNextMissionControl = {
  schema_id?: 'ion.vnext_mission_control_projection.v1' | string;
  generated_at?: string;
  status?: string;
  mission?: string;
  canon_status?: string;
  read_only?: boolean;
  source_paths?: Record<string, string>;
  source_present?: Record<string, boolean>;
  operating_model?: Record<string, string>;
  current_packet?: IonVNextPacket;
  latest_result?: {
    path?: string | null;
    verdict?: string;
    created_at?: string;
  };
  latest_receipt?: {
    id?: string;
    date?: string;
    summary?: string;
    status?: string;
    evidence?: string;
  };
  lanes?: IonVNextLane[];
  packets?: IonVNextPacket[];
  gates?: IonVNextGate[];
  mission_families?: IonVNextMissionFamily[];
  long_horizon?: IonVNextLongHorizon;
  protocol_index?: IonVNextProtocolInventory;
  context_packages?: IonVNextContextPackageProjection;
  documentation_surfaces?: IonVNextDocumentationSurfaces;
  gate_summary?: {
    open?: number;
    closed?: number;
    reviewed?: number;
  };
  drift_guards?: IonVNextDriftGuard[];
  next_safe_route?: {
    route?: string;
    condition?: string;
    automatic?: boolean;
  };
  authority?: IonVNextAuthorityFlags & {
    read_only_projection?: boolean;
    accepted_state_authority?: boolean;
    supabase_mutation_authority?: boolean;
  };
};

export type IonProjectCockpitRecordStatus = 'open' | 'blocked' | 'in_progress' | 'watch' | 'resolved' | 'closed' | 'complete' | string;

export type IonProjectCockpitProject = {
  project_id: string;
  label?: string;
  status?: string;
  summary?: string;
  kind?: string;
  path?: string;
  exists?: boolean;
  current_packet?: string | null;
  source?: string;
  route_hint?: string;
  route_href?: string;
  preview_href?: string;
  launcher_url?: string;
  app_catalog_url?: string;
  package_root_count?: number;
  launchable_count?: number;
  family_count?: number;
  evidence_refs?: string[];
};

export type IonProjectCockpitMission = {
  mission_id: string;
  project_id?: string;
  label?: string;
  summary?: string;
  status?: string;
  mission_type?: string;
  packet_count?: number;
  epoch_count?: number;
  protocol_count?: number;
  context_package_count?: number;
  evidence_refs?: string[];
  source?: string;
};

export type IonProjectCockpitBlocker = {
  blocker_id: string;
  project_id?: string;
  mission_ids?: string[];
  title?: string;
  detail?: string;
  severity?: string;
  status?: IonProjectCockpitRecordStatus;
  source?: string;
  derived?: boolean;
  latest_packet?: string;
  blocks?: string[];
  unlock_condition?: string;
  required_next_action?: string;
  owner_route?: string;
  evidence_refs?: string[];
  created_at?: string;
  updated_at?: string;
  resolution?: string;
  resolution_evidence?: string[];
};

export type IonProjectCockpitQuestion = {
  question_id: string;
  project_id?: string;
  mission_ids?: string[];
  question_text?: string;
  needed_from?: string;
  priority?: string;
  status?: IonProjectCockpitRecordStatus;
  context?: string;
  blocking?: string[];
  evidence_refs?: string[];
  created_at?: string;
  updated_at?: string;
  resolution?: string;
  resolution_evidence?: string[];
  source?: string;
};

export type IonProjectCockpitTimelineEvent = {
  event_id: string;
  project_id?: string;
  event_type?: string;
  status?: string;
  occurred_at?: string;
  title?: string;
  detail?: string;
  evidence_refs?: string[];
  source?: string;
  actor?: string;
};

export type IonProjectLaunchMetadata = {
  launchable?: boolean;
  framework?: string;
  mode?: string;
  action_path?: string;
  stop_path?: string;
  status_path?: string;
  diagnostics_path?: string;
  requires_local_machine?: boolean;
  install_repair_on_launch?: boolean;
  managed_window_stops_server?: boolean;
  host?: string;
  status?: string;
  project_id?: string;
  version_id?: string;
  label?: string;
  project_path?: string;
};

export type IonProjectLauncherRecord = {
  launch_id?: string;
  project_id?: string;
  version_id?: string;
  label?: string;
  path?: string;
  framework?: string;
  command?: string[];
  url?: string;
  open_href?: string;
  port?: number;
  state?: string;
  message?: string;
  running?: boolean;
  detached?: boolean;
  process_attached?: boolean;
  actual_process_control?: boolean;
  process_pid?: number | null;
  process_pgid?: number | null;
  process_sid?: number | null;
  process_start_time_ticks?: string;
  os_boot_id?: string;
  runner_instance_id?: string;
  process_identity?: Record<string, unknown>;
  runtime_truth?: Record<string, unknown>;
  process_control_level?: string;
  ownership_confidence?: string;
  loopback_reachable?: boolean;
  recovered_at?: string;
  last_known_state?: string;
  stop_available?: boolean;
  created_at?: string;
  updated_at?: string;
  exit_code?: number | null;
  log_path?: string;
  log_tail?: string;
  managed_window_stops_server?: boolean;
  stop_path?: string;
  status_path?: string;
  diagnostics_path?: string;
  diagnostics_event_path?: string;
  instrumented_open_href?: string;
};

export type IonProjectLauncherStatus = {
  schema_id?: 'ion.project_launcher_status.v1' | string;
  ok?: boolean;
  generated_at?: string;
  confirmation?: string;
  host?: string;
  running_count?: number;
  detached_count?: number;
  launch_count?: number;
  launches?: IonProjectLauncherRecord[];
  durable_state?: Record<string, unknown>;
  authority?: Record<string, boolean>;
};

export type IonProjectPreviewProvider = {
  schema_id?: 'ion.project_preview_provider.v0_1' | string;
  provider_id?: string;
  label?: string;
  state?: string;
  runner_location?: string;
  capabilities?: string[];
  summary?: string;
  authority?: Record<string, boolean>;
};

export type IonProjectPreviewSession = {
  schema_id?: 'ion.project_preview_session.v0_1' | string;
  preview_id?: string;
  project_id?: string;
  version_id?: string;
  family_id?: string;
  label?: string;
  provider_id?: string;
  runner_id?: string;
  runner_location?: string;
  source_kind?: string;
  source_root_ref?: string;
  public_url?: string;
  same_origin_embed_url?: string;
  local_url_ref?: string;
  control_url?: string;
  status_url?: string;
  diagnostics_url?: string;
  screenshot_url?: string;
  hmr_proxy?: string;
  auth_mode?: string;
  viewer_scope?: string;
  lifecycle_state?: string;
  runtime_state_class?: string;
  state_basis?: string;
  association_state?: string;
  detached?: boolean;
  process_attached?: boolean;
  actual_process_control?: boolean;
  stop_available?: boolean;
  last_known_state?: string;
  recovered_at?: string;
  launcher_finding?: string;
  ownership_confidence?: string;
  process_control_level?: string;
  loopback_reachable?: boolean;
  stale?: boolean;
  stale_reasons?: string[];
  created_at?: string;
  updated_at?: string;
  expires_at?: string;
  stop_token_ref?: string;
  receipt_refs?: string[];
  public_preview_allowed?: boolean;
  finding?: string;
  capabilities?: Record<string, boolean>;
  authority?: Record<string, boolean>;
};

export type IonProjectPreviewSessionsModel = {
  schema_id?: 'ion.project_preview_sessions.v0_1' | string;
  ok?: boolean;
  verdict?: string;
  status?: string;
  generated_at?: string;
  summary?: {
    provider_count?: number;
    session_count?: number;
    running_count?: number;
    detached_count?: number;
    orphaned_count?: number;
    stale_count?: number;
    public_preview_count?: number;
    portfolio_session_count?: number;
    source_counts?: Record<string, number>;
    runtime_state_counts?: Record<string, number>;
  };
  providers?: IonProjectPreviewProvider[];
  sessions?: IonProjectPreviewSession[];
  comparisons?: Array<Record<string, unknown>>;
  capability_classes?: Record<string, string>;
  routes?: Record<string, string>;
  source_models?: Record<string, string>;
  authority?: Record<string, boolean>;
  non_claims?: string[];
  findings?: string[];
};

export type IonProjectDocReference = {
  type?: string;
  label?: string;
  target?: string;
  detail?: string;
  project_id?: string;
  family_id?: string;
  family_label?: string;
};

export type IonProjectDocRow = {
  title?: string;
  kind?: string;
  rel_path?: string;
  path?: string;
  extension?: string;
  bytes?: number;
  primary?: boolean;
  reference?: boolean;
  excerpt?: string;
  source_root?: string;
  project_id?: string;
  project_label?: string;
  family_id?: string;
  family_label?: string;
};

export type IonProjectDocs = {
  schema_id?: string;
  status?: string;
  doc_count?: number;
  reference_count?: number;
  documented_version_count?: number;
  current_version_id?: string;
  primary_doc?: IonProjectDocRow;
  primary_docs?: IonProjectDocRow[];
  docs?: IonProjectDocRow[];
  references?: IonProjectDocReference[];
  target_docs?: Array<{ label?: string; path?: string; status?: string; family_id?: string; family_label?: string }>;
  top_docs?: IonProjectDocRow[];
  recommended_sections?: string[];
  documented_family_count?: number;
  coverage?: {
    has_readme?: boolean;
    has_architecture?: boolean;
    has_runbook?: boolean;
    has_reference?: boolean;
    has_references?: boolean;
  };
  source_curation?: Record<string, string>;
};

export type IonProjectOperatingSystem = {
  schema_id?: string;
  family_id?: string;
  domain_id?: string;
  label?: string;
  posture?: string;
  readiness_score?: number;
  average_readiness_score?: number;
  family_count?: number;
  ready_count?: number;
  watch_count?: number;
  blocked_count?: number;
  summary?: {
    version_count?: number;
    branch_count?: number;
    diff_count?: number;
    launchable_count?: number;
    doc_count?: number;
    reference_count?: number;
    risk_count?: number;
  };
  lifecycle?: Array<{ stage_id?: string; label?: string; status?: string; objective?: string }>;
  maintenance_lanes?: Array<{ lane_id?: string; label?: string; status?: string; objective?: string; next_action?: string }>;
  quality_gates?: Array<{ gate_id?: string; label?: string; status?: string; evidence?: string }>;
  risk_register?: Array<{ risk_id?: string; severity?: string; title?: string; mitigation?: string; family_id?: string; family_label?: string }>;
  human_workflows?: Array<{ workflow_id?: string; label?: string; cadence?: string; trigger?: string; output?: string }>;
  next_actions?: Array<{ action_id?: string; label?: string; lane?: string; priority?: string; detail?: string }>;
  operating_principles?: string[];
  top_risks?: Array<{ risk_id?: string; severity?: string; title?: string; mitigation?: string; family_id?: string; family_label?: string }>;
  board_columns?: Array<{
    column_id?: string;
    label?: string;
    count?: number;
    families?: Array<{ family_id?: string; label?: string; score?: number; risk_count?: number; count?: number }>;
  }>;
  maintenance_rhythm?: Array<{ cadence?: string; label?: string; focus?: string }>;
  authority?: Record<string, boolean>;
};

export type IonProjectPortfolioProject = {
  project_id: string;
  source_id?: string;
  source_label?: string;
  family_id?: string;
  group_id?: string;
  domain_id?: string;
  domain_label?: string;
  family_label?: string;
  label?: string;
  name?: string;
  package_version?: string;
  version_token?: string;
  date_token?: string;
  milestone_token?: string;
  branch_id?: string;
  branch_label?: string;
  path?: string;
  source_root?: string;
  rel_path?: string;
  markers?: string[];
  stack?: string;
  launchable?: boolean;
  launch?: IonProjectLaunchMetadata;
  docs?: IonProjectDocs;
  scripts?: Record<string, string>;
  load?: {
    mode?: string;
    label?: string;
    path?: string;
    organized_current_source?: string;
    organized_version_manifest?: string;
    launchable?: boolean;
  };
  has_git?: boolean;
  status?: string;
};

export type IonProjectPortfolioVersion = {
  version_id?: string;
  project_id?: string;
  label?: string;
  display_label?: string;
  sequence_label?: string;
  version_token?: string;
  date_token?: string;
  milestone_token?: string;
  branch_id?: string;
  branch_label?: string;
  path?: string;
  stack?: string;
  launchable?: boolean;
  launch?: IonProjectLaunchMetadata;
  docs?: IonProjectDocs;
  is_current?: boolean;
  load?: {
    mode?: string;
    label?: string;
    path?: string;
    organized_current_source?: string;
    organized_version_manifest?: string;
    launchable?: boolean;
  };
};

export type IonProjectPortfolioBranch = {
  branch_id?: string;
  label?: string;
  version_count?: number;
  launchable_count?: number;
  latest_version?: IonProjectPortfolioVersion;
};

export type IonProjectPortfolioDiff = {
  diff_id?: string;
  from_project_id?: string;
  to_project_id?: string;
  from_path?: string;
  to_path?: string;
  from_version?: string;
  to_version?: string;
  from_label?: string;
  to_label?: string;
  from_branch?: string;
  to_branch?: string;
  status?: string;
  copy_policy?: string;
  manifest_path?: string;
  file_diff?: {
    status?: string;
    added_count?: number;
    removed_count?: number;
    changed_count?: number;
    added_sample?: string[];
    removed_sample?: string[];
    changed_sample?: string[];
    previous_file_count?: number;
    current_file_count?: number;
    truncated?: boolean;
  };
};

export type IonProjectPortfolioFamily = {
  family_id: string;
  group_id?: string;
  domain_id?: string;
  domain_label?: string;
  label?: string;
  source_ids?: string[];
  workspace_dir_count?: number;
  project_count?: number;
  version_count?: number;
  branch_count?: number;
  diff_count?: number;
  launchable_count?: number;
  doc_count?: number;
  reference_count?: number;
  current_project_id?: string;
  current_path?: string;
  current?: IonProjectPortfolioProject;
  versions?: IonProjectPortfolioVersion[];
  branches?: IonProjectPortfolioBranch[];
  diffs?: IonProjectPortfolioDiff[];
  docs?: IonProjectDocs;
  operating_system?: IonProjectOperatingSystem;
  organized_path?: string;
  lineage_status?: string;
  materialization_plan?: string;
};

export type IonProjectPortfolioGroup = {
  group_id: string;
  label?: string;
  family_count?: number;
  project_count?: number;
  launchable_count?: number;
  versioned_family_count?: number;
};

export type IonProjectPortfolioDomain = {
  domain_id: string;
  group_id?: string;
  label?: string;
  summary?: string;
  folder?: string;
  sort_order?: number;
  family_count?: number;
  project_count?: number;
  version_count?: number;
  branch_count?: number;
  diff_count?: number;
  launchable_count?: number;
  doc_count?: number;
  reference_count?: number;
  documented_family_count?: number;
  docs?: IonProjectDocs;
  operating_system?: IonProjectOperatingSystem;
  versioned_family_count?: number;
  families?: Array<{
    family_id?: string;
    label?: string;
    version_count?: number;
    branch_count?: number;
    diff_count?: number;
    project_count?: number;
    launchable_count?: number;
    doc_count?: number;
    reference_count?: number;
    ops_posture?: string;
    ops_score?: number;
    current_path?: string;
  }>;
};

export type IonProjectPortfolioDuplicateCluster = {
  cluster_id: string;
  family_id?: string;
  label?: string;
  count?: number;
  paths?: string[];
  recommendation?: string;
};

export type IonProjectPortfolioMaterializationReceipt = {
  path?: string;
  relpath?: string;
  created_at?: string;
  target?: string;
  copy_count?: number;
  family_count?: number;
  project_root_count?: number;
  production_authority?: boolean;
  live_execution_authority?: boolean;
  accepted_state_authority?: boolean;
  secrets_authority?: boolean;
};

export type IonProjectPortfolio = {
  schema_id?: 'ion.project_portfolio.v1' | string;
  generated_at?: string;
  status?: string;
  load_mode?: string;
  source_roots?: Record<string, string>;
  source_present?: Record<string, boolean>;
  organizer?: {
    manifest_path?: string;
    manifest_relpath?: string;
    materialized_root?: string;
    materialized_present?: boolean;
    materialize_path?: string;
    materialize_confirmation?: string;
    latest_materialization_receipt?: IonProjectPortfolioMaterializationReceipt;
    source_copy_policy?: string;
    layout?: string;
    excluded_dirs?: string[];
    max_file_bytes?: number;
    accepted_state_authority?: boolean;
    production_authority?: boolean;
    live_execution_authority?: boolean;
    secrets_authority?: boolean;
  };
  summary?: {
    source_root_count?: number;
    workspace_dir_count?: number;
    project_root_count?: number;
    family_count?: number;
    group_count?: number;
    canonical_domain_count?: number;
    launchable_count?: number;
    documentation_surface_count?: number;
    reference_count?: number;
    documented_family_count?: number;
    project_os_ready_count?: number;
    project_os_watch_count?: number;
    project_os_blocked_count?: number;
    legacy_copy_cluster_count?: number;
    duplicate_cluster_count?: number;
    versioned_family_count?: number;
    materialized_present?: boolean;
  };
  canonical_domains?: IonProjectPortfolioDomain[];
  groups?: IonProjectPortfolioGroup[];
  families?: IonProjectPortfolioFamily[];
  projects?: IonProjectPortfolioProject[];
  duplicate_clusters?: IonProjectPortfolioDuplicateCluster[];
  recommendations?: Array<{ title?: string; detail?: string; family_id?: string; status?: string }>;
};

export type IonProjectSpecialistProjection = {
  status?: string;
  index_path?: string;
  index_relpath?: string;
  generated_at?: string;
  domain_specialist_capsule_count?: number;
  project_specialist_capsule_count?: number;
  domain_agent_packet_count?: number;
  project_agent_packet_count?: number;
  total_agent_packet_count?: number;
  mirrored_domain_context_count?: number;
  mirrored_project_context_count?: number;
  agent_invocation_status?: string;
};

export type IonProjectCanonDossierProjection = {
  status?: string;
  index_path?: string;
  index_relpath?: string;
  generated_at?: string;
  domain_dossier_count?: number;
  project_dossier_count?: number;
  mirrored_project_dossier_count?: number;
};

export type IonProjectCockpit = {
  schema_id?: 'ion.project_cockpit_projection.v1' | string;
  generated_at?: string;
  status?: string;
  selected_project_id?: string;
  source_paths?: Record<string, string>;
  source_present?: Record<string, boolean>;
  projects?: IonProjectCockpitProject[];
  missions?: IonProjectCockpitMission[];
  blockers?: IonProjectCockpitBlocker[];
  questions?: IonProjectCockpitQuestion[];
  timeline_events?: IonProjectCockpitTimelineEvent[];
  latest_receipts?: Array<Record<string, unknown>>;
  portfolio?: IonProjectPortfolio;
  portfolio_load_mode?: string;
  organization_state?: {
    status?: string;
    load_mode?: string;
    candidate_only?: boolean;
    materialized_present?: boolean;
    materialized_root?: string;
    manifest_path?: string;
    latest_receipt?: Record<string, unknown>;
    source_copy_policy?: string;
    layout?: string;
    copy_count?: number;
    family_count?: number;
    project_root_count?: number;
    duplicate_cluster_count?: number;
    legacy_copy_cluster_count?: number;
    versioned_family_count?: number;
    diff_manifest_count?: number;
    canon_dossiers?: IonProjectCanonDossierProjection;
    project_specialists?: IonProjectSpecialistProjection;
    accepted_state_authority?: boolean;
    production_authority?: boolean;
    live_execution_authority?: boolean;
    secrets_authority?: boolean;
  };
  launcher?: IonProjectLauncherStatus;
  preview_sessions?: IonProjectPreviewSessionsModel;
  summary?: {
    project_count?: number;
    mission_count?: number;
    blocker_count?: number;
    open_blocker_count?: number;
    derived_blocker_count?: number;
    managed_blocker_count?: number;
    question_count?: number;
    open_question_count?: number;
    blocking_question_count?: number;
    timeline_event_count?: number;
    portfolio_project_root_count?: number;
    portfolio_family_count?: number;
    portfolio_duplicate_cluster_count?: number;
    portfolio_versioned_family_count?: number;
    portfolio_diff_manifest_count?: number;
    portfolio_copy_count?: number;
    portfolio_load_mode?: string;
    preview_provider_count?: number;
    preview_session_count?: number;
    preview_running_session_count?: number;
  };
  authority?: {
    candidate_state_write_authority?: boolean;
    accepted_state_authority?: boolean;
    production_authority?: boolean;
    live_execution_authority?: boolean;
    secrets_authority?: boolean;
    supabase_mutation_authority?: boolean;
    codex_queue_dispatch_authority?: boolean;
  };
  write_confirmation?: string;
  local_launch_confirmation?: string;
  non_claims?: string[];
};

export type IonServiceConsoleModel = {
  schema_id?: 'ion.cockpit_service_console.v1' | string;
  ok?: boolean;
  verdict?: string;
  headline?: string;
  required_issue_count?: number;
  warning_count?: number;
  generated_at?: string;
  shell_root?: string;
  operator_message?: string;
  production_authority?: boolean;
  live_execution_authority?: boolean;
  services?: Array<{
    id?: string;
    unit?: string;
    label?: string;
    role?: string;
    critical?: boolean;
    fix_label?: string;
    active?: boolean;
    status?: string;
    finding?: string;
    severity?: string;
    restart_confirmation?: string;
  }>;
};

export type IonSystemDiagnosticsProcess = {
  pid: number;
  ppid?: number;
  state?: string;
  elapsed_seconds?: number;
  cpu_percent?: number;
  memory_percent?: number;
  rss_kb?: number;
  command?: string;
  name?: string;
  cwd?: string | null;
  workspace?: string;
  protected?: boolean;
  dev_server?: boolean;
  dev_server_reason?: string | null;
  framework?: string | null;
  package_name?: string | null;
  package_path?: string | null;
};

export type IonSystemDiagnosticsPort = {
  protocol?: string;
  local_address?: string;
  port: number;
  pid?: number | null;
  process_name?: string | null;
  command?: string | null;
  cwd?: string | null;
  workspace?: string;
  dev_server?: boolean;
  dev_server_reason?: string | null;
  framework?: string | null;
  package_name?: string | null;
  package_path?: string | null;
  protected?: boolean;
  cleanup_candidate?: boolean;
};

export type IonSystemDiagnosticsHttpProbe = {
  serves_http?: boolean;
  url?: string;
  http_status?: number | null;
  finding?: string;
  title?: string | null;
};

export type IonSystemDiagnosticsAction = {
  action_type: string;
  target_pid?: number | null;
  target_port?: number | null;
  confirmation?: string;
  confirmed?: boolean;
};

export type IonSystemDiagnosticsActionEligibility = {
  action_type?: string;
  allowed?: boolean;
  stoppable?: boolean;
  reasons?: string[];
  requires_confirmation?: boolean;
  required_confirmation?: string | null;
  policy_projection?: string;
};

export type IonSystemDiagnosticsCleanupCandidate = {
  id: string;
  pid: number;
  port?: number;
  process_name?: string | null;
  workspace?: string;
  cwd?: string | null;
  elapsed_seconds?: number;
  cpu_percent?: number;
  stale?: boolean;
  action_eligibility?: IonSystemDiagnosticsActionEligibility;
  action: IonSystemDiagnosticsAction;
};

export type IonSystemDiagnosticsDevServer = {
  id: string;
  port: number;
  pid?: number | null;
  process_name?: string | null;
  workspace?: string;
  cwd?: string | null;
  command?: string | null;
  elapsed_seconds?: number;
  cpu_percent?: number;
  rss_kb?: number;
  protected?: boolean;
  dev_server?: boolean;
  cleanup_candidate?: boolean;
  stale?: boolean;
  framework?: string | null;
  package_name?: string | null;
  package_path?: string | null;
  reason?: string | null;
  confidence?: string;
  http_probe?: IonSystemDiagnosticsHttpProbe;
  action_eligibility?: IonSystemDiagnosticsActionEligibility;
  action?: IonSystemDiagnosticsAction;
};

export type IonSystemDiagnosticsIssue = {
  id: string;
  severity: string;
  title: string;
  detail?: string;
  evidence?: string[];
  action?: IonSystemDiagnosticsAction | null;
};

export type IonSystemDiagnosticsRiskFinding = {
  id?: string;
  severity?: string;
  category?: string;
  title?: string;
  detail?: string;
  evidence?: string[];
};

export type IonSystemDiagnosticsRoute = {
  id?: string;
  method?: string;
  path?: string;
  surface?: string;
  route_class?: string;
  capability?: string;
  sensitivity?: string;
  auth_required?: boolean;
  same_origin_required?: boolean;
  confirmation_required?: boolean;
  required_confirmation?: string;
  policy_projection?: string;
  mutation?: boolean;
};

export type IonSystemDiagnosticsService = {
  id?: string;
  unit?: string;
  label?: string;
  role?: string;
  critical?: boolean;
  active?: boolean;
  status?: string;
  finding?: string;
  severity?: string;
  restart_confirmation?: string;
};

export type IonSystemDiagnostics = {
  schema_id?: 'ion.system_diagnostics.v1' | string;
  generated_at?: string;
  status?: string;
  summary?: {
    cpu_percent?: number;
    load_avg?: number[];
    memory_total_mb?: number;
    memory_used_mb?: number;
    memory_percent?: number;
    swap_total_mb?: number;
    swap_used_mb?: number;
    swap_percent?: number;
    disk_percent?: number;
    uptime_seconds?: number;
    process_count?: number;
    listener_count?: number;
    active_dev_server_count?: number;
    protected_dev_server_count?: number;
    http_verified_dev_server_count?: number;
    cleanup_candidate_count?: number;
    stale_port_count?: number;
    issue_count?: number;
    risk_finding_count?: number;
    security_finding_count?: number;
    service_issue_count?: number;
  };
  top_processes?: IonSystemDiagnosticsProcess[];
  ports?: IonSystemDiagnosticsPort[];
  dev_servers?: IonSystemDiagnosticsDevServer[];
  cleanup_candidates?: IonSystemDiagnosticsCleanupCandidate[];
  issues?: IonSystemDiagnosticsIssue[];
  risk_summary?: {
    verdict?: string;
    issue_count?: number;
    severity_counts?: Record<string, number>;
    actionable_cleanup_count?: number;
    protected_dev_server_count?: number;
    stale_dev_server_count?: number;
    security_finding_count?: number;
    critical_service_issue_count?: number;
    authority?: Record<string, boolean>;
  };
  risk_findings?: IonSystemDiagnosticsRiskFinding[];
  service_health?: {
    ok?: boolean;
    verdict?: string;
    headline?: string;
    required_issue_count?: number;
    warning_count?: number;
    service_count?: number;
    services?: IonSystemDiagnosticsService[];
    authority?: Record<string, boolean>;
  };
  route_matrix?: IonSystemDiagnosticsRoute[];
  security_summary?: {
    auth_configured?: boolean;
    session_cookie?: string;
    session_secret_configured?: boolean;
    dedicated_session_secret_configured?: boolean;
    session_secret_source?: string;
    public_token_configured?: boolean;
    invite_token_count?: number;
    google_oauth_configured?: boolean;
    google_client_id_configured?: boolean;
    google_allowlist_configured?: boolean;
    mutation_route_count?: number;
    same_origin_mutation_required?: boolean;
    unauthenticated_local_control_route_count?: number;
    cookie_policy?: Record<string, unknown>;
    token_values_emitted?: boolean;
    secret_values_emitted?: boolean;
    findings?: IonSystemDiagnosticsRiskFinding[];
    authority?: Record<string, boolean>;
  };
  policy_projection?: Record<string, unknown>;
  redaction_summary?: {
    command_redaction_enabled?: boolean;
    secret_value_redaction_enabled?: boolean;
    redacted_process_command_count?: number;
    token_values_emitted?: boolean;
    secret_values_emitted?: boolean;
  };
  data_quality?: {
    process_source?: string;
    port_source?: string;
    http_probe_timeout_seconds?: number;
    active_dev_servers_are_probe_verified?: number;
    dev_server_count_includes_protected?: boolean;
    cleanup_candidates_exclude_protected?: boolean;
    command_redaction_enabled?: boolean;
    redacted_process_command_count?: number;
    route_matrix_source?: string;
    service_health_source?: string;
  };
  action_contract?: {
    stop_confirmation?: string;
    preview_endpoint?: string;
    execute_endpoint?: string;
  };
  authority?: {
    local_operator_action_authority?: boolean;
    accepted_state_authority?: boolean;
    production_authority?: boolean;
    live_execution_authority?: boolean;
    protected_processes_blocked?: boolean;
  };
};

export type IonBranchGatewayInvocation = {
  ok?: boolean;
  finding?: string;
  branch_id?: string;
  branch_title?: string;
  route_id?: string;
  route_title?: string;
  route_schema_version?: string;
  delegated_result?: Record<string, unknown>;
  mutates_active_state?: boolean;
  production_authority?: boolean;
  live_execution_authority?: boolean;
};

export type IonBranchGatewayServiceControl = {
  service_id?: string;
  service_status?: Record<string, unknown>;
  service_reload_plan?: Record<string, unknown>;
  allowed_service_id?: boolean;
  restart_route_id?: string;
  reload_and_retest_route_id?: string;
  requires_confirmation?: boolean;
  required_confirmation?: string;
  requires_idempotency_key?: boolean;
  shows_plan_before_action?: boolean;
  receipt_handoff_dir?: string;
  cockpit_executes_mutation?: boolean;
  mutates_active_state?: boolean;
};

export type IonBranchGatewayConsumers = {
  schema_id?: 'ion.branch_gateway_cockpit_consumers.v0_1' | string;
  generated_at?: string;
  worker_shift?: {
    branch?: IonBranchGatewayInvocation;
    status_summary?: IonBranchGatewayInvocation;
    active_workers?: IonBranchGatewayInvocation;
    coordination_state?: IonBranchGatewayInvocation;
    mutates_active_state?: boolean;
  };
  runtime_services?: {
    branch?: IonBranchGatewayInvocation;
    service_status?: IonBranchGatewayInvocation;
    service_reload_plans?: Record<string, IonBranchGatewayInvocation>;
    retest_service?: IonBranchGatewayInvocation;
    default_retest_service_id?: string;
    service_controls?: IonBranchGatewayServiceControl[];
    mutation_gate?: {
      allowed_service_id_required?: boolean;
      confirmation_required?: string;
      idempotency_key_required?: boolean;
      plan_preview_required?: boolean;
      post_action_receipt_handoff_required?: boolean;
      receipt_handoff_dir?: string;
      cockpit_executes_mutation?: boolean;
    };
    mutates_active_state?: boolean;
  };
  accepted_state_claim?: boolean;
  production_authority?: boolean;
  live_execution_authority?: boolean;
};

export type IonChatgptBrowserMcpSummary = {
  schema_id?: 'ion.chatgpt_browser_mcp_cockpit_summary.v1' | string;
  connector_contract_verdict?: string;
  http_preview_verdict?: string;
  transport_state?: string;
  active_connector_url?: string;
  carrier_id?: string;
  project_facing_callsign?: string;
  callsign_authority?: string;
  callsign_decision_receipt?: string;
  tool_count?: number;
  first_parity_tools_present?: string[];
  visibility_tools_present?: string[];
  agent_invocation_tools_present?: string[];
  carrier_message_count?: number;
  codex_work_request_count?: number;
  latest_carrier_messages?: Array<Record<string, unknown>>;
  latest_task_returns?: Array<Record<string, unknown>>;
  latest_task_return_machine_receipts?: Array<Record<string, unknown>>;
  latest_task_return_automation_diagnoses?: Array<Record<string, unknown>>;
  latest_agent_invocations?: Array<Record<string, unknown>>;
  latest_artifact_receipts?: Array<Record<string, unknown>>;
  latest_decisions?: Array<Record<string, unknown>>;
  codex_queue_runner?: Record<string, unknown>;
  agent_invocation_broker?: Record<string, unknown>;
  artifact_upload_status_counts?: Record<string, number>;
  adapter_gap_not_core_failure?: boolean;
  production_authority?: boolean;
  live_execution_authority?: boolean;
};

export type IonCodexCapsuleChatSummary = {
  schema_id?: 'ion.codex_capsule_chat_cockpit_summary.v1' | string;
  model_path?: string;
  model_present?: boolean;
  verdict?: string;
  generated_at?: string;
  product?: Record<string, unknown>;
  product_mode?: Record<string, unknown>;
  authority?: Record<string, unknown>;
  conversation_summary?: Record<string, unknown>;
  conversation_turn_groups?: Array<Record<string, unknown>>;
  ion_comms_turn_groups?: Array<Record<string, unknown>>;
  pipeline_runs?: Array<Record<string, unknown>>;
  ion_comms?: Record<string, unknown>;
  shared_digest?: Record<string, unknown>;
  lanes?: Record<string, unknown>;
  chat_branches?: Array<Record<string, unknown>>;
  fresh_agent_capsule_chats?: Array<Record<string, unknown>>;
  chat_context?: Record<string, unknown>;
  ide_context_bridge?: Record<string, unknown>;
  turn_trace_count?: number;
  turn_traces?: Record<string, unknown>;
  queued_request_count?: number;
  runner_active?: boolean;
  response_run_count?: number;
  latest_response_status?: string;
  latest_response_runs?: Array<Record<string, unknown>>;
  latest_work_requests?: Array<Record<string, unknown>>;
  latest_task_returns?: Array<Record<string, unknown>>;
  latest_task_return_machine_receipts?: Array<Record<string, unknown>>;
  latest_task_return_automation_diagnoses?: Array<Record<string, unknown>>;
  return_hydration?: Record<string, unknown>;
  memory?: {
    pin_count?: number;
    archive_attachments?: Array<Record<string, unknown>>;
    archive_attachment_count?: number;
    codex_memory_path?: string;
  };
  codex_queue_path?: string;
  capsule?: {
    ok?: boolean;
    path?: string;
    entry_count?: number;
    context_line_limit?: number;
    recent_rows?: Array<Record<string, unknown>>;
  };
  mini?: {
    ok?: boolean;
    role?: string;
    line_count?: number;
    max_lines?: number;
    text_excerpt?: string;
  };
  hot_context?: Record<string, unknown>;
  memory_visualization?: Record<string, unknown>;
  chat_engine?: Record<string, unknown>;
  model_moves?: Record<string, unknown>;
  assistant_work_routes?: Record<string, unknown>;
  raw_codex_cli?: Record<string, unknown>;
  codex_app_server?: Record<string, unknown>;
  service_console?: Record<string, unknown>;
  telemetry_inventory?: Record<string, unknown>;
  skills?: Record<string, unknown>;
  response_carrier?: Record<string, unknown>;
  execution_bridge?: Record<string, unknown>;
  production_authority?: boolean;
  live_execution_authority?: boolean;
  secrets_authority?: boolean;
};

export type IonCodexCliWorkbench = {
  schema_id?: 'ion.codex_cli_workbench_model.v1' | string;
  generated_at?: string;
  verdict?: string;
  ok?: boolean;
  workbench_ready?: boolean;
  shell_root?: string;
  content_root?: string;
  north_star?: string;
  summary?: Record<string, unknown>;
  visibility_contract?: Record<string, unknown>;
  chat?: Record<string, unknown>;
  context?: {
    witness_policy?: string;
    active_context?: Record<string, unknown>;
    surfaces?: Array<Record<string, unknown>>;
    long_horizon?: Record<string, unknown>;
    context_packages?: Record<string, unknown>;
    timeline?: IonCodexContextTimeline;
  };
  settings?: Record<string, unknown>;
  hooks?: Record<string, unknown>;
  skills?: Record<string, unknown>;
  tools?: Record<string, unknown>;
  agents_and_roles?: Record<string, unknown>;
  project_context?: Record<string, unknown>;
  carrier_os?: Record<string, unknown>;
  findings?: string[];
  surface_errors?: Array<Record<string, unknown>>;
  hidden_reasoning_exposed?: boolean;
  secrets_authority?: boolean;
  production_authority?: boolean;
  live_execution_authority?: boolean;
};

export type IonCodexIdeWorkbench = {
  schema_id?: 'ion.codex_ide_workbench_model.v0_1' | string;
  generated_at?: string;
  status?: string;
  root?: string;
  surface?: 'ide' | string;
  workspace_session?: {
    schema_id?: 'ion.codex_ide_workspace_session.v0_1' | string;
    session_id?: string;
    root?: string;
    active_chat_context_binding_id?: string;
    active_bridge_id?: string;
    active_branch_ids?: string[];
    selected_path?: string;
    open_tabs?: Array<Record<string, unknown>>;
    authority?: Record<string, boolean>;
  };
  context_registry?: {
    schema_id?: 'ion.codex_ide_context_registry.v0_1' | string;
    status?: string;
    active_binding_id?: string;
    active_binding?: Record<string, unknown> | null;
    binding_count?: number;
    bindings?: Array<Record<string, unknown>>;
    binding_ids_unique?: boolean;
    duplicate_binding_ids?: string[];
    bridge_status?: string;
    bridge_count?: number;
    latest_bridge?: Record<string, unknown> | null;
    latest_bridge_artifact_present?: boolean;
    context_system_count?: number;
    context_systems?: Array<Record<string, unknown>>;
    warnings?: Array<Record<string, unknown>>;
    warning_count?: number;
    context_policy?: Record<string, unknown>;
    authority?: Record<string, boolean>;
  };
  editor?: Record<string, unknown>;
  worktree?: Record<string, unknown>;
  capability_registry?: Record<string, unknown>;
  authority?: Record<string, boolean>;
  production_authority?: boolean;
  live_execution_authority?: boolean;
  accepted_state_authority?: boolean;
  secrets_authority?: boolean;
};

export type IonCodexContextTimeline = {
  schema_id?: 'ion.codex_context_timeline.v1' | string;
  generated_at?: string;
  verdict?: string;
  ok?: boolean;
  shell_root?: string;
  context_root?: string;
  history_root?: string;
  north_star?: string;
  summary?: Record<string, unknown>;
  surfaces?: Array<Record<string, unknown>>;
  lanes?: Array<Record<string, unknown>>;
  timeline?: Array<Record<string, unknown>>;
  boundaries?: Array<Record<string, unknown>>;
  topology?: Record<string, unknown>;
  visibility_contract?: Record<string, unknown>;
  findings?: string[];
  hidden_reasoning_exposed?: boolean;
  secrets_authority?: boolean;
  production_authority?: boolean;
  live_execution_authority?: boolean;
};

export type IonCodexConversationArchiveSession = {
  schema_id?: 'ion.codex_conversation_archive_session.v1' | string;
  session_id: string;
  thread_name?: string;
  display_title?: string;
  project_key?: string;
  project_label?: string;
  updated_at?: string | null;
  created_at?: string | null;
  session_path?: string;
  cwd?: string | null;
  model?: string | null;
  bytes?: number;
  line_count_sampled?: number;
  line_scan_limited?: boolean;
  event_counts?: Record<string, number>;
  role_counts?: Record<string, number>;
  tool_counts?: Record<string, number>;
  mission_labels?: Array<{ label?: string; source?: string; confidence?: string }>;
  agent_labels?: Array<{ label?: string; source?: string; confidence?: string }>;
  tool_summary?: Array<{ name?: string; count?: number }>;
  activity_score?: number;
  session_flags?: Record<string, boolean>;
  first_user_snippet?: string;
  latest_user_snippet?: string;
  latest_assistant_snippet?: string;
  history_prompt_count?: number;
  history_latest_ts?: string | null;
  raw_transcript_exported?: boolean;
  is_current_session?: boolean;
};

export type IonCodexConversationArchive = {
  schema_id?: 'ion.codex_conversation_archive.v1' | string;
  verdict?: string;
  generated_at?: string;
  codex_home?: string;
  sources?: Record<string, string>;
  source_counts?: {
    history_rows_sampled?: number;
    session_index_rows?: number;
    session_files_total?: number;
    session_files_returned?: number;
  };
  sessions?: IonCodexConversationArchiveSession[];
  current_session_id?: string;
  current_prompt_ts?: string | number | null;
  current_prompt_snippet?: string;
  selected_session_excerpt?: {
    session_id?: string;
    is_current_session?: boolean;
    found?: boolean;
    raw_transcript_exported?: boolean;
    hidden_reasoning_exposed?: boolean;
    safe_transcript_exported?: boolean;
    display_mode?: string;
    window_mode?: string;
    policy?: string;
    session_path?: string | null;
    line_scan_limit?: number | null;
    line_scan_limited?: boolean;
    excerpt_limit?: number;
    item_count?: number;
    displayed_item_count?: number;
    total_displayable_items?: number;
    omitted_older_items?: number;
    omitted_newer_items?: number;
    has_older_items?: boolean;
    has_newer_items?: boolean;
    oldest_item_index?: number | null;
    newest_item_index?: number | null;
    window_start_index?: number | null;
    window_end_index?: number | null;
    window_count?: number;
    line_count?: number;
    items?: Array<{
      index?: number;
      timestamp?: string;
      role?: string;
      snippet?: string;
      text?: string;
      source_type?: string;
      message_kind?: string;
      visual_lane?: string;
      detail_label?: string;
      path_refs?: string[];
      context_refs?: string[];
      compaction_markers?: string[];
      diff_stats?: {
        files?: string[];
        file_count?: number;
        added_lines?: number;
        removed_lines?: number;
      };
      synthetic?: boolean;
      truncated?: boolean;
    }>;
  } | null;
  query?: string;
  session_limit?: number;
  raw_content_exported?: boolean;
  raw_transcript_exported?: boolean;
  hidden_reasoning_exposed?: boolean;
  secrets_authority?: boolean;
  production_authority?: boolean;
  live_execution_authority?: boolean;
  policy?: string;
};

export type IonCodexGitRollback = {
  schema_id?: 'ion.codex_git_rollback.v1' | string;
  generated_at?: string;
  verdict?: string;
  ok?: boolean;
  selected_session_id?: string | null;
  current_git?: Record<string, unknown>;
  current_worktree?: {
    schema_id?: 'ion.codex_current_worktree_edits.v1' | string;
    available?: boolean;
    generated_at?: string;
    branch?: string | null;
    head?: string | null;
    dirty?: boolean;
    scope_prefix?: string;
    status_entries?: Array<Record<string, unknown>>;
    status_sample?: Array<Record<string, unknown>>;
    file_edits?: Array<Record<string, unknown>>;
    staged_file_count?: number;
    unstaged_file_count?: number;
    untracked_file_count?: number;
    secret_risk_path_count?: number;
    secret_risk_paths?: string[];
    diff_truncated?: boolean;
    diff_stats?: {
      files?: string[];
      file_count?: number;
      added_lines?: number;
      removed_lines?: number;
    };
  };
  tree_discipline?: Record<string, unknown>;
  summary?: {
    checkpoint_count?: number;
    visible_checkpoint_count?: number;
    rollback_receipt_count?: number;
    rollback_ready_count?: number;
    archive_diff_evidence_count?: number;
    current_file_count?: number;
    current_added_lines?: number;
    current_removed_lines?: number;
    current_untracked_file_count?: number;
  };
  checkpoints?: Array<Record<string, unknown>>;
  archive_diff_evidence?: Array<Record<string, unknown>>;
  rollback_receipts?: Array<Record<string, unknown>>;
  policy?: string;
  production_authority?: boolean;
  live_execution_authority?: boolean;
  secrets_authority?: boolean;
};

export type IonAgentControlPlane = {
  schema_id?: 'ion.agent_control_plane.v1' | string;
  generated_at?: string;
  verdict?: string;
  ok?: boolean;
  shell_root?: string;
  source_model?: Record<string, string>;
  summary?: {
    agent_count?: number;
    invocable_agent_count?: number;
    domain_count?: number;
    active_process_running?: boolean;
    queued_agent_codex_work_request_count?: number;
    missing_legacy_context_ref_count?: number;
    codex_mount_count?: number;
    materialized_codex_mount_count?: number;
    roster_capsule_agent_count?: number;
    roster_domain_built_count?: number;
    available_agent_comms_count?: number;
    active_domain_count?: number;
    domain_weaver_usable_domain_count?: number;
    candidate_domain_count?: number;
    candidate_covered_domain_count?: number;
    covered_domain_count?: number;
    domain_weaver_gap_count?: number;
    domain_weaver_edge_count?: number;
    dispatcher_actionable_run_count?: number;
    dispatcher_active_worker_count?: number;
    dispatcher_pending_directive_count?: number;
  };
  chain?: {
    steps?: Array<Record<string, unknown>>;
    active_process_running?: boolean;
    active_run?: Record<string, unknown> | null;
    return_path?: string;
    single_carrier_sequential?: boolean;
  };
  roster?: Record<string, unknown>;
  agents?: Array<Record<string, unknown>>;
  domains?: Array<Record<string, unknown>>;
  domain_weaver?: Record<string, unknown>;
  dispatcher?: Record<string, unknown>;
  starter_capsule?: Record<string, unknown>;
  codex_mounts?: {
    schema_id?: 'ion.codex_agent_mounts.v0_1' | string;
    mount_count?: number;
    materialized_count?: number;
    prompt_visibility_proven_count?: number;
    mount_root?: string;
    mounts?: Array<Record<string, unknown>>;
    policy?: string;
  };
  runs?: {
    active_process_running?: boolean;
    active_run?: Record<string, unknown> | null;
    live_worker_telemetry?: Record<string, unknown>;
    latest_state?: Record<string, unknown>;
    recent_invocations?: Array<Record<string, unknown>>;
    agent_invocation_count?: number;
    queued_agent_codex_work_request_count?: number;
    next_agent_codex_work_request_path?: string | null;
  };
  communications?: {
    schema_id?: 'ion.agent_control_plane.communications.v1' | string;
    invocations?: Array<Record<string, unknown>>;
    relays?: Array<Record<string, unknown>>;
    pending_relays?: Array<Record<string, unknown>>;
    receipts?: Array<Record<string, unknown>>;
    timeline?: Array<Record<string, unknown>>;
    team_comms?: Record<string, unknown>;
    team_comms_chain_audit?: Record<string, unknown>;
    team_comms_chain_proof?: Record<string, unknown>;
    team_comms_chain_gate?: Record<string, unknown>;
    summary?: Record<string, unknown>;
    policy?: string;
    production_authority?: boolean;
    live_execution_authority?: boolean;
  };
  diagnostics?: Record<string, unknown>;
  settings?: Record<string, unknown>;
  authority?: Record<string, boolean>;
  production_authority?: boolean;
  live_execution_authority?: boolean;
  accepted_state_authority?: boolean;
  secrets_authority?: boolean;
};

export type IonExtensionMicroShellSummary = {
  schema_id?: 'ion.extension_micro_shell_cockpit_summary.v1' | string;
  status?: string;
  extension_root?: string;
  manifest?: Record<string, unknown>;
  agent_lane_contract?: Record<string, unknown>;
  portable_companion?: Record<string, unknown>;
  page_perception?: {
    domain_registry_path?: string;
    task_return_path?: string;
    domain_registry_present?: boolean;
    task_return_present?: boolean;
    domain_count?: number;
    domains?: Array<Record<string, unknown>>;
    task_return_headings?: string[];
  };
  browser_gpt_dom?: {
    schema_id?: 'ion.browser_gpt_dom_profile_summary.v1' | string;
    status?: string;
    verdict?: string;
    profile_count?: number;
    latest_profile_id?: string;
    latest_profile_path?: string;
    latest_health_path?: string;
    latest_receipt_path?: string;
    origin?: string;
    target_url?: string;
    surfaces?: Array<Record<string, unknown>>;
    runtime_commands?: string[];
    safety_boundaries?: string[];
    prior_live_dom_evidence?: Record<string, unknown>;
    probe_intake?: Record<string, unknown>;
    chatgpt_dom_twin?: Record<string, unknown>;
    failed_required_surfaces?: string[];
    recommended_action?: string;
    authority?: Record<string, unknown>;
  };
  computer_assistant_capability_map?: Record<string, unknown>;
  queue_pack_authoring?: Record<string, unknown>;
  current_v1_authority?: Record<string, unknown>;
  safety_law?: string[];
  required_boundaries?: string[];
  implementation_gates?: string[];
  non_claim_boundaries?: string[];
  production_authority?: boolean;
  live_execution_authority?: boolean;
  unrestricted_browser_control?: boolean;
  silent_browser_send_authority?: boolean;
};

export type IonDocsProjectsPackagesSummary = {
  schema_id?: 'ion.docs_projects_packages_cockpit_summary.v1' | string;
  status?: string;
  context_packages?: {
    path?: string;
    generated_at?: string;
    package_count?: number;
    selected_by_default?: string[];
    package_types?: Record<string, number>;
    packages?: Array<Record<string, unknown>>;
    production_authority?: boolean;
    live_execution_authority?: boolean;
  };
  project_favorites?: Array<Record<string, unknown>>;
  artifact_packages?: {
    root?: string;
    zip_count_visible?: number;
    latest_zips?: Array<Record<string, unknown>>;
    auto_zip_drop_authority?: boolean;
    drop_zone_execution_authority?: boolean;
  };
  safe_full_project_package?: Record<string, unknown>;
  custom_gpt_context?: Record<string, unknown>;
  operator_model?: Record<string, unknown>;
  production_authority?: boolean;
  live_execution_authority?: boolean;
  unrestricted_filesystem_mutation?: boolean;
};

export type IonContextPackageGraphBranch = {
  path?: string;
  package_type?: string;
  parent_ref?: string;
  maturity_level?: string;
  read_first?: string[];
  candidate_capsule_path?: string;
  candidate_capsule_sha256_after_wave_002?: string;
  readme_projection_candidate?: string;
  promotion_readiness?: string;
  classification?: string;
  candidate_valid?: boolean;
  accepted_capsule_exists?: boolean;
  accepted_capsule_path?: string;
  gaps?: string[];
  blockers?: string[];
  recommended_next?: string[];
  authority?: {
    accepted_state_authority?: boolean;
    production_authority?: boolean;
    live_execution_authority?: boolean;
  };
  surface_counts?: Record<string, number>;
  surface_hints_preview?: Record<string, unknown[]>;
};

export type IonContextPackageGraphProjection = {
  schema_id?: 'ion.cockpit_context_package_graph_projection.v1' | string;
  status?: string;
  generated_at?: string;
  packet_id?: string;
  source_wave_id?: string;
  source_paths?: Record<string, string>;
  source_present?: Record<string, boolean>;
  branch_count?: number;
  candidate_review_ready_count?: number;
  blocked_count?: number;
  allowed_operations?: string[];
  forbidden_operations?: string[];
  required_ui_fields?: string[];
  candidate_state_only?: boolean;
  accepted_state_claim?: boolean;
  authority?: {
    accepted_state_authority?: boolean;
    production_authority?: boolean;
    live_execution_authority?: boolean;
    secrets_authority?: boolean;
  };
  branches?: IonContextPackageGraphBranch[];
};

export type JocCommsChannel = {
  channel_id: string;
  label: string;
  source_surface?: string;
  channel_kind?: string;
  authority_scope?: string;
  purpose?: string;
  unread_or_pending_count?: number;
  thread_count?: number;
  latest_event_at?: string;
  required_tool_or_route?: string;
  write_policy?: string;
  production_authority?: boolean;
  live_execution_authority?: boolean;
  write_authority?: boolean;
};

export type JocCommsThread = {
  thread_id: string;
  channel_id: string;
  title?: string;
  subject?: string;
  thread_kind?: string;
  source_refs?: string[];
  context_refs?: string[];
  receipt_refs?: string[];
  status?: string;
  next_allowed_actions?: string[];
  authority_boundary?: string;
  message_count?: number;
  latest_summary?: string;
  updated_at?: string;
  created_at?: string;
  production_authority?: boolean;
  live_execution_authority?: boolean;
};

export type JocCommsMessage = {
  message_id: string;
  thread_id: string;
  channel_id: string;
  sender_id?: string;
  sender_kind?: string;
  recipient?: string[] | string;
  body?: string;
  message_type?: string;
  message_kind?: string;
  subject?: string;
  from_role?: string;
  source_path?: string;
  source_refs?: string[];
  context_refs?: string[];
  receipt_refs?: string[];
  status?: string;
  acked_by?: string[];
  created_at?: string;
  production_authority?: boolean;
  live_execution_authority?: boolean;
  secrets_authority?: boolean;
  work_panel?: Record<string, unknown>;
};

export type JocCommsParticipant = {
  participant_id: string;
  display_name?: string;
  participant_kind?: string;
  carrier_id?: string;
  domain_id?: string;
  context_package_path?: string;
  mount_receipt_path?: string;
  status?: string;
  available_for_comms?: boolean;
  authority_scope?: string;
  production_authority?: boolean;
  live_execution_authority?: boolean;
};

export type JocCommsPin = {
  pin_id: string;
  thread_id?: string;
  label?: string;
  ref_path?: string;
  ref_sha256?: string;
  truth_class?: string;
  authority_scope?: string;
  stale_policy?: string;
  production_authority?: boolean;
  live_execution_authority?: boolean;
};

export type JocCommsAction = {
  action_id: string;
  label?: string;
  action_kind?: string;
  route_or_tool?: string;
  confirmation_required?: boolean;
  approval_required?: boolean;
  production_authority?: boolean;
  live_execution_authority?: boolean;
  allowed_when?: string;
  forbidden_when?: string;
  state?: string;
};

export type JocCommsProjection = {
  schema_id?: string;
  status?: string;
  generated_at?: string;
  authority?: {
    production_authority?: boolean;
    live_execution_authority?: boolean;
    write_authority?: boolean;
    write_authority_policy?: string;
    accepted_state_claim?: boolean;
    secrets_authority?: boolean;
  };
  source_paths?: Record<string, string>;
  source_present?: Record<string, boolean>;
  channels?: JocCommsChannel[];
  threads?: JocCommsThread[];
  messages?: JocCommsMessage[];
  participants?: JocCommsParticipant[];
  pins?: JocCommsPin[];
  receipts?: Array<Record<string, unknown>>;
  actions?: JocCommsAction[];
  blockers?: Array<Record<string, unknown>>;
  read_only_projection?: boolean;
  production_authority?: boolean;
  live_execution_authority?: boolean;
  non_claims?: string[];
};

export type IonCockpitViewModel = {
  schema_id: 'ion.cockpit_view_model.v1';
  generated_at: string;
  runtime: {
    status: string;
    shell_root: string;
    mode: string;
    version: string;
    blocked: boolean;
    audit_findings: unknown[];
  };
  top_bar: {
    objective: string;
    carrier_status: string;
    hook_status: string;
    gate_count: number;
    spawn_count: number;
    plan_spawn_count?: number;
    deferred_spawn_count?: number;
    spawn_rows_total: number;
    execution_bundle_materialized?: boolean | null;
    return_counts: Record<string, number>;
    steward_queue_count: number;
    operator_queue_pending: number;
    local_service_status?: string;
    local_service_count?: number;
    local_service_missing_template_count?: number;
    system_cpu_percent?: number;
    system_memory_percent?: number;
    system_swap_percent?: number;
    system_listener_count?: number;
    system_cleanup_candidate_count?: number;
    system_stale_port_count?: number;
    system_issue_count?: number;
    worker_shift_active_worker_count?: number;
    runtime_services_branch_service_count?: number;
    helixion_rebuild_status?: string;
    helixion_rebuild_ready_for_phase_1?: boolean;
    vnext_status?: string;
    vnext_current_packet?: string;
    vnext_open_gate_count?: number;
    vnext_packet_count?: number;
    project_cockpit_status?: string;
    project_count?: number;
    project_mission_count?: number;
    project_open_blocker_count?: number;
    project_open_question_count?: number;
    browser_carrier_message_count?: number;
    codex_work_request_count?: number;
    action_gateway_tool_count?: number;
    action_gateway_transport_state?: string;
    codex_capsule_chat_verdict?: string;
    codex_capsule_chat_turn_count?: number;
    codex_capsule_chat_response_run_count?: number;
    codex_cli_workbench_verdict?: string;
    codex_cli_workbench_tool_count?: number;
    codex_cli_workbench_hook_group_count?: number;
    codex_conversation_session_count?: number;
    extension_version?: string;
    extension_panel_count?: number;
    page_perception_domain_count?: number;
    browser_gpt_dom_status?: string;
    context_package_count?: number;
    branch_context_package_count?: number;
    branch_context_package_ready_count?: number;
    context_package_graph_status?: string;
    artifact_package_count?: number;
    agent_control_plane_agent_count?: number;
    agent_control_plane_domain_count?: number;
    agent_control_plane_active?: boolean;
  };
  queues: IonQueueState;
  agents: {
    spawn_rows: IonSpawnRow[];
    context_packages: Record<string, unknown>[];
    returns: IonTaskReturn[];
  };
  timeline: IonTimelineEvent[];
  front_door_proof_trace?: IonFrontDoorProofTrace;
  lane_timeline?: {
    schema_id?: string;
    event_count?: number;
    events?: IonLaneTimelineEvent[];
    messages?: Record<string, unknown>[];
  };
  receipt_hydration?: {
    schema_id?: string;
    receipt_count?: number;
    unresolved_count?: number;
    hydration_conflict_count?: number;
    records?: IonReceiptHydrationRecord[];
  };
  runtime_debug_overlay?: IonRuntimeDebugOverlay;
  safe_full_project_package?: IonSafeFullProjectPackage;
  v72_mcp_donor_reconciliation?: IonV72McpDonorReconciliation;
  local_services?: IonLocalServiceStatus;
  service_console?: IonServiceConsoleModel;
  system_diagnostics?: IonSystemDiagnostics;
  branch_gateway_consumers?: IonBranchGatewayConsumers;
  helixion_joc_rebuild?: IonHelixionJocRebuildProjection;
  vnext_mission_control?: IonVNextMissionControl;
  project_cockpit?: IonProjectCockpit;
  chatgpt_browser_mcp?: IonChatgptBrowserMcpSummary;
  codex_capsule_chat?: IonCodexCapsuleChatSummary;
  codex_cli_workbench?: IonCodexCliWorkbench;
  codex_ide_workbench?: IonCodexIdeWorkbench;
  codex_conversation_archive?: IonCodexConversationArchive;
  codex_git_rollback?: IonCodexGitRollback;
  joc_comms?: JocCommsProjection;
  agent_control_plane?: IonAgentControlPlane;
  automation_control_plane?: Record<string, unknown>;
  extension_micro_shell?: IonExtensionMicroShellSummary;
  docs_projects_packages?: IonDocsProjectsPackagesSummary;
  context_package_graph?: IonContextPackageGraphProjection;
  receipts: Record<string, unknown>[];
  authority_classes: IonAuthorityClass[];
  source_paths: Record<string, string>;
};
