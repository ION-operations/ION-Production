from kernel.ion_ai_git_branch_containment import (
    build_ai_branch_name,
    classify_git_edit_posture,
    build_start_receipt,
    build_recovery_receipt,
    as_receipt_fragment,
)


def test_branch_name_is_namespaced_and_slugged():
    name = build_ai_branch_name("Codex CLI", "Browser Extension", "Receipt Tags!!", "20260514T170232Z")
    assert name == "ion/codex-cli/browser-extension/receipt-tags/20260514T170232Z"


def test_protected_branch_is_read_only():
    posture = classify_git_edit_posture(branch="main", dirty=False, isolated_worktree=False, start_receipt_present=False)
    assert posture.verdict == "read_only"
    assert posture.protected_branch is True
    assert "protected_branch" in posture.reasons


def test_dirty_protected_branch_is_blocked():
    posture = classify_git_edit_posture(branch="main", dirty=True, isolated_worktree=False, start_receipt_present=False)
    assert posture.verdict == "blocked"
    assert "dirty_protected_checkout" in posture.reasons


def test_non_protected_without_start_receipt_is_patch_only():
    posture = classify_git_edit_posture(branch="ion/codex/kernel/work/20260514T170232Z", dirty=False, isolated_worktree=True, start_receipt_present=False)
    assert posture.verdict == "patch_only"
    assert "missing_start_receipt" in posture.reasons


def test_start_and_recovery_receipts_are_non_authorizing():
    start = build_start_receipt(
        receipt_id="r-start",
        agent="codex",
        objective="repair browser queue",
        branch_name="ion/codex/browser-extension/repair-browser-queue/20260514T170232Z",
        base_ref="main",
        base_commit="abc123",
        worktree_path="../ion-worktrees/repair-browser-queue",
        branch_node_path="ION/09_integrations/browser_extension",
    )
    assert start["verdict"] == "allow_edit"
    assert start["authority"]["protected_branch_write"] is False

    recovery = build_recovery_receipt(
        receipt_id="r-recovery",
        agent="codex",
        objective="repair browser queue",
        recovery_branch="ion/codex/browser-extension/repair-browser-queue-recovery/20260514T170232Z",
        damaged_branch="ion/codex/browser-extension/repair-browser-queue/20260514T170000Z",
        last_known_good_ref="abc123",
        recovered_from=["failing_test_summary", "diff_summary", "failing_test_summary"],
        excluded=["secrets"],
    )
    assert recovery["receipt_type"] == "recovery"
    assert recovery["recovery_source"]["recovered_from"] == ["diff_summary", "failing_test_summary"]
    fragment = as_receipt_fragment(classify_git_edit_posture(branch=recovery["branch"]["name"], isolated_worktree=True, start_receipt_present=True))
    assert fragment["verdict"] == "allow_edit"
