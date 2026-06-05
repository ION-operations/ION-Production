# Clean Export Manifest Template

Status: template
Authority: candidate export manifest shape only; no accepted-state, production, live execution, deploy, push, or secrets authority.

```json
{
  "schema_id": "ion.clean_export_manifest.v0_1",
  "export_id": "ION_CLEAN_EXPORT_YYYYMMDDTHHMMSSZ",
  "created_at": "YYYY-MM-DDTHH:MM:SS+00:00",
  "source_root": "/path/to/active/root",
  "output_dir": "/path/outside/source/root/ION_EXPORTS_LOCAL",
  "dry_run": true,
  "archive_path": null,
  "archive_sha256": null,
  "file_count": 0,
  "total_bytes": 0,
  "required_review_files": {
    "ION/05_context/current/reports/SINGLE_CARRIER_OPERATING_SPINE_SETTLEMENT_REPORT.md": true,
    "ION/05_context/current/reports/SINGLE_CARRIER_OPERATING_SPINE_SETTLEMENT_LEDGER.json": true,
    "ION/05_context/current/reports/WAVE_001_002_RECONCILIATION_REPORT.md": true,
    "ION/05_context/current/reports/WAVE_001_002_RECONCILIATION_LEDGER.json": true,
    "ION/05_context/current/reports/WAVE_003_PLAN_ONLY.md": true
  },
  "included_files": [
    {
      "path": "ION/04_packages/kernel/example.py",
      "bytes": 0,
      "sha256": "hex",
      "source_posture": "kernel_source"
    }
  ],
  "excluded_summary": {
    "counts_by_reason": {},
    "sample_paths_by_reason": {},
    "raw_needs_routed_included": false,
    "vault_content_read": false
  },
  "warnings": [],
  "secret_scan": {
    "status": "SECURITY_READY",
    "accepted": true,
    "secret_values_emitted": false
  },
  "status_verdict_at_export_time": {
    "verdict": "ION_STATUS_SINGLE_CARRIER_READY",
    "production_authority": false,
    "live_execution_authority": false
  },
  "accepted_state_claim": false,
  "production_authority": false,
  "live_execution_authority": false,
  "deploy_authority": false,
  "push_authority": false,
  "secrets_authority": false
}
```

The sidecar manifest carries the final archive SHA-256. The in-archive prehash manifest is evidence for selection and scan state before the archive hash exists.
