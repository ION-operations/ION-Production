# Git Cleanup Potential Index - 2026-06-05T18:12:17Z

## Scope

This packet follows the operator instruction: no deletion, only Git ignore
containment plus a quarantine-style list of what may be cleaned later.

Current source baseline before this packet: `ebd07fc2`.

Pre-edit status shape:

| Status | Count | Handling |
|---|---:|---|
| `??` | 70200 | Only generated/local residue can be ignored here; source-like families stay visible. |
| `D` | 18578 | Cannot be hidden by `.gitignore`; listed for future explicit deletion review only. |
| `M` | 60 | Requires separate owner/source review. |

## Ignore Rules Added

The `.gitignore` update targets only generated/local residue observed in the
current worktree:

| Rule | Current matching untracked paths | Reason |
|---|---:|---|
| `Cosmos/**/.icip/` | 8 | Local semantic/index cache files. |
| `Cosmos/**/.claude/settings.local.json` | 3 observed in sample set | Local IDE/agent settings. |
| `desktop.ini` | 63 observed in sample set | Windows folder metadata. |
| `ION/05_context/current/project_launcher/app_diagnostics/` | included in 116 ION generated paths | Local diagnostic event/config snapshots. |
| `ION/05_context/current/reports/*.jsonl` | included in 116 ION generated paths | Generated report streams. |
| `ION/05_context/runtime_state/v64_local_mcp_bridge/runtime_sessions/` | included in 116 ION generated paths | Runtime session state. |
| `ION/05_context/current/codex_capsule_chat/raw_cli_runs/` | included in 116 ION generated paths | Raw Codex run transcripts; compact receipts remain the review surface. |
| `ION/05_context/current/codex_carrier/commit_boundary/CODEX_SOURCE_BUNDLE_STAGE_MANIFEST.candidate.json` | included in 116 ION generated paths | Generated full source-bundle stage manifest. |

Generic rules for `node_modules/`, `dist/`, `.next/`, `.vite/`, `tmp/`, and
large Cosmos raw data already existed and were not broadened here.

## Potential Cleanup Families

These are not deleted or staged by this packet.

| Family | Candidate count | Current action |
|---|---:|---|
| Tracked deletion review paths | 18578 | Review only; `.gitignore` does not apply to tracked paths. |
| AIM-OS archive deletion review | 11846 | Review packet exists; no deletion. |
| Same-content old-root deletion candidates | 6530 | Review packet exists; no deletion. |
| Changed-content old-root exceptions | 173 | Settlement required before any destructive action. |
| ION_GPT artifact deletion review | 21 | Review packet exists; no deletion. |
| Small-family deletion review | 8 | Review packet exists; no deletion. |
| Untracked owner-review families | 69084 | Still visible for owner/source classification. |
| Generated/local evidence | 951 | Partially ignored when narrow and generated/local. |
| Runtime residue | 127 | Partially ignored when narrow and generated/local. |

## Existing Review Packet References

- `ION/05_context/current/repo_organization/PCKT_GIT_REMAINING_CLEANUP_ROUTE_MAP_001_20260605T180012Z.candidate.md`
- `ION/05_context/current/repo_organization/PCKT_GIT_ROOT_NORMALIZATION_EXCEPTION_REVIEW_001_20260605T175820Z.candidate.md`
- `ION/05_context/current/repo_organization/PCKT_GIT_ROOT_NORMALIZATION_SAME_CONTENT_DELETE_REVIEW_001_20260605T175912Z.candidate.md`
- `ION/05_context/current/repo_organization/PCKT_GIT_AIMOS_ARCHIVE_DELETION_REVIEW_001_20260605T180059Z.candidate.md`
- `ION/05_context/current/repo_organization/PCKT_GIT_ION_GPT_ARTIFACT_DELETION_REVIEW_001_20260605T180115Z.candidate.md`
- `ION/05_context/current/repo_organization/PCKT_GIT_SMALL_FAMILY_DELETION_REVIEW_001_20260605T180129Z.candidate.md`
- `ION/05_context/current/repo_organization/PCKT_GIT_GENERATED_RUNTIME_HANDLING_REVIEW_001_20260605T180153Z.candidate.md`
- `ION/05_context/current/repo_organization/PCKT_GIT_UNTRACKED_OWNER_REVIEW_001_20260605T180221Z.candidate.md`

## Next Review Questions

1. Which tracked deletion families are approved for real deletion staging, if any?
2. Which untracked Cosmos and ION families are source to keep versus local build
   or generated output to ignore?
3. Whether `Needs_Routed/`, `ION_GPT/`, `ION_VNEXT/`, and `dAimon/` untracked
   material should be promoted, packetized, archived, or ignored by family.
