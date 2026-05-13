#!/usr/bin/env python3
"""
Lane B Mapper Adapter Contract v0.1 (isolated proof).

Transforms a live-mapper-like snapshot shape into the current
Shadow BCI emitter input shape.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import shadow_bci_v1_emitter as emitter

ALLOWED_CONFIDENCE = {"High", "Degraded", "Fallback"}


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _normalize_confidence(value: Any) -> str:
    if isinstance(value, str) and value in ALLOWED_CONFIDENCE:
        return value
    return "Fallback"


def _normalize_path(path_like: Any) -> str:
    return str(path_like).replace("\\", "/")


def validate_adapter_input_shape(adapter_input: Dict[str, Any]) -> None:
    """Validate that adapted payload is compatible with emitter contract."""
    emitter.ensure_required_fixture_fields(adapter_input)
    if not isinstance(adapter_input.get("imports"), list):
        raise ValueError("adapter_input.imports must be a list")
    if not isinstance(adapter_input.get("contracts"), list):
        raise ValueError("adapter_input.contracts must be a list")


def adapt_live_mapper_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert live-mapper-like snapshot into emitter fixture input shape.

    Expected snapshot shape:
    {
      "target_path": "...",
      "target_source": "...",
      "extracted_file": {
        "path": "...",
        "imports": [...],
        "contracts": [{"kind","name","signature"}],
        "confidence": "High|Degraded|Fallback"
      },
      "resolved_local_files": ["..."],
      "observed_at": "optional"
    }
    """
    extracted = snapshot.get("extracted_file")
    if not isinstance(extracted, dict):
        raise ValueError("snapshot.extracted_file must be an object")

    path = extracted.get("path") or snapshot.get("target_path")
    if not path:
        raise ValueError("missing extracted_file.path / target_path")

    source_text = snapshot.get("target_source")
    if not isinstance(source_text, str) or not source_text:
        raise ValueError("snapshot.target_source must be a non-empty string")

    imports = extracted.get("imports", [])
    contracts = extracted.get("contracts", [])

    if not isinstance(imports, list):
        raise ValueError("extracted_file.imports must be a list")
    if not isinstance(contracts, list):
        raise ValueError("extracted_file.contracts must be a list")

    normalized_contracts: List[Dict[str, Any]] = []
    for contract in contracts:
        if not isinstance(contract, dict):
            raise ValueError("each contract must be an object")
        normalized_contracts.append(
            {
                "kind": contract.get("kind"),
                "name": contract.get("name"),
                "signature": contract.get("signature"),
            }
        )

    resolved_local_files = snapshot.get("resolved_local_files", [])
    if not isinstance(resolved_local_files, list):
        raise ValueError("resolved_local_files must be a list")

    adapted = {
        "source_path": _normalize_path(path),
        "source_text": source_text,
        "imports": imports,
        "contracts": normalized_contracts,
        "parse_confidence": _normalize_confidence(extracted.get("confidence")),
        "resolved_dependencies": [_normalize_path(p) for p in resolved_local_files],
    }
    if "observed_at" in snapshot:
        adapted["observed_at"] = snapshot["observed_at"]

    # Reuse emitter fixture contract check to guarantee compatibility.
    validate_adapter_input_shape(adapted)
    return adapted


def emit_probe(adapter_input: Dict[str, Any], schema_path: Path) -> Dict[str, Any]:
    """
    Isolated proof helper: run emission and schema validation from adapted input.
    Returns summary if successful; raises ValueError on failure.
    """
    records = emitter.emit_records_from_fixture(adapter_input)
    is_valid, errors = emitter.validate_records(records, schema_path)
    if not is_valid:
        raise ValueError("\n".join(errors))
    return emitter.summarize_records(records)


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Lane B mapper adapter proof v0.1")
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=root / "fixtures" / "live_mapper_snapshot_v0_1.json",
        help="Input live-mapper-like snapshot JSON",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=root / "shadow_bci_v1_schema.json",
        help="Shadow BCI schema path used for probe validation",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=root / "out" / "adapter_emitter_input_v0_1.json",
        help="Output file for adapted emitter input",
    )
    parser.add_argument(
        "--probe",
        action="store_true",
        help="Run emitter probe (emit + schema validate) on adapted input",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        snapshot = read_json(args.snapshot)
        adapted = adapt_live_mapper_snapshot(snapshot)
    except Exception as exc:
        print(f"[adapter_v0_1] ERROR adapting snapshot: {exc}", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        json.dump(adapted, handle, indent=2)

    print("[adapter_v0_1] Adapted input written.")
    print(str(args.out))

    if args.probe:
        try:
            summary = emit_probe(adapted, args.schema)
            print("[adapter_v0_1] Probe succeeded.")
            print(json.dumps(summary, indent=2))
        except Exception as exc:
            print(f"[adapter_v0_1] ERROR probe failed: {exc}", file=sys.stderr)
            return 3

    return 0


if __name__ == "__main__":
    sys.exit(main())
