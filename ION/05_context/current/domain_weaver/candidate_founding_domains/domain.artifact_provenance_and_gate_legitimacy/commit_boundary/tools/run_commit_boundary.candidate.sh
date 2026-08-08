#!/usr/bin/env bash
# Repeatable commit-boundary lane (candidate-only). Run from ION shell root (pyproject.toml + ION/REPO_AUTHORITY.md).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../../../../../../../" && pwd)"
if [[ ! -f "$ROOT/pyproject.toml" || ! -f "$ROOT/ION/REPO_AUTHORITY.md" ]]; then
  echo "ROOT_NOT_CONFIRMED: $ROOT" >&2
  exit 2
fi

MANIFEST="${1:-ION/05_context/current/domain_weaver/candidate_founding_domains/domain.artifact_provenance_and_gate_legitimacy/commit_boundary/COMMIT_BOUNDARY_MANIFEST_20260808.candidate.yaml}"
SCAN_DIR="$ROOT/ION/05_context/current/domain_weaver/candidate_founding_domains/domain.artifact_provenance_and_gate_legitimacy/commit_boundary/secret_scan_runs"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
PATHSPEC_FILE="$SCAN_DIR/pathspec_${STAMP}.txt"
SUMMARY="$SCAN_DIR/gate_git_snapshot_secret_scan_${STAMP}/secret_scan_summary.json"

python3 - "$ROOT" "$MANIFEST" "$PATHSPEC_FILE" <<'PY'
import sys, yaml
from pathlib import Path
root, manifest_rel, out = sys.argv[1:4]
data = yaml.safe_load((Path(root) / manifest_rel).read_text(encoding="utf-8"))
paths = [e["path"] for e in data.get("include_paths", [])]
Path(out).write_text("\n".join(paths) + "\n", encoding="utf-8")
print(len(paths), "paths in manifest")
PY

mkdir -p "$(dirname "$SUMMARY")"
BLOCKED=0
while IFS= read -r p; do
  case "$p" in
    *ION_VAULT_LOCAL*|*.env|*credentials*) BLOCKED=1; echo "BLOCK path rule: $p" >&2 ;;
  esac
  if [[ -f "$ROOT/$p" ]]; then
    if rg -q -i '(AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36}|-----BEGIN (RSA |OPENSSH )?PRIVATE KEY-----)' "$ROOT/$p" 2>/dev/null; then
      BLOCKED=1
      echo "BLOCK rg credential pattern: $p" >&2
    fi
  fi
done < "$PATHSPEC_FILE"

if [[ "$BLOCKED" -ne 0 ]]; then
  printf '%s\n' "{\"gate_id\":\"gate.git_snapshot.secret_scan\",\"verdict\":\"BLOCKED_SECRET_RISK\",\"scan_name\":\"gate_git_snapshot_secret_scan_${STAMP}\"}" > "$SUMMARY"
  exit 1
fi

printf '%s\n' "{\"gate_id\":\"gate.git_snapshot.secret_scan\",\"verdict\":\"PASS\",\"scan_name\":\"gate_git_snapshot_secret_scan_${STAMP}\",\"pathspec_file\":\"${PATHSPEC_FILE#"$ROOT/"}"}" > "$SUMMARY"

while IFS= read -r p; do
  git -C "$ROOT" add -- "$p"
done < "$PATHSPEC_FILE"

DELETIONS="$(git -C "$ROOT" diff --cached --diff-filter=D --name-only | wc -l)"
if [[ "$DELETIONS" -gt 0 ]]; then
  echo "gate.commit_boundary.deletion_zero FAIL: $DELETIONS deletions staged" >&2
  git -C "$ROOT" reset HEAD
  exit 1
fi

PACKET_ID="$(python3 -c "import yaml;from pathlib import Path;d=yaml.safe_load(Path('$ROOT/$MANIFEST').read_text());print(d['packet_id'])")"
MANIFEST_SHA="$(sha256sum "$ROOT/$MANIFEST" | awk '{print $1}')"
git -C "$ROOT" commit -m "candidate(commit-boundary): ${PACKET_ID}

Manifest: $(basename "$MANIFEST") sha256=${MANIFEST_SHA}
Gate: gate.git_snapshot.secret_scan PASS
Authority: candidate-only; no push."

echo "Committed. Write COMMIT_BOUNDARY_RECEIPT with: git -C $ROOT rev-parse HEAD"
