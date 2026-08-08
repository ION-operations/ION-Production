#!/usr/bin/env python3
"""CF-12 directive scope/expiry admission findings tests (candidate)."""
from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path


def _load_module():
    script = Path(__file__).resolve().parents[1] / (
        "runtime/ion_cf12_directive_scope_expiry_admission_findings.candidate.py"
    )
    spec = importlib.util.spec_from_file_location("cf12_findings", script)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_scoped_fixture_has_no_findings() -> None:
    mod = _load_module()
    fixture = Path(__file__).resolve().parents[1] / "fixtures/directive_scoped_fixture.candidate.json"
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    assert mod.assess_directive_payload(payload) == []


def test_unscoped_fixture_emits_both_findings() -> None:
    mod = _load_module()
    fixture = Path(__file__).resolve().parents[1] / "fixtures/directive_unscoped_fixture.candidate.json"
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    codes = mod.assess_directive_payload(payload)
    assert "cf12_directive_scope_missing" in codes
    assert "cf12_directive_expiry_or_satisfaction_missing" in codes


def test_record_writes_summary_and_ledger() -> None:
    mod = _load_module()
    fixture = Path(__file__).resolve().parents[1] / "fixtures/directive_unscoped_fixture.candidate.json"
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        shell = Path(tmp)
        (shell / "ION/05_context/current/domain_weaver/candidate_founding_domains/domain.operator_sovereignty_and_directive_admission").mkdir(
            parents=True
        )
        out = mod.record_admission_assessment(
            shell,
            source_kind="test_fixture",
            source_ref="directive_unscoped_fixture",
            directive_payload=payload,
            write=True,
        )
        assert out["ledger_rows_appended"] == 2
        summary_path = shell / mod.SUMMARY_REL
        ledger_path = shell / mod.LEDGER_REL
        assert summary_path.is_file()
        assert ledger_path.is_file()
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        assert summary["fundamental_id"] == "CF-12"
        assert summary["absence_present"] is False


if __name__ == "__main__":
    test_scoped_fixture_has_no_findings()
    test_unscoped_fixture_emits_both_findings()
    test_record_writes_summary_and_ledger()
    print("CF-12 admission findings tests OK")
