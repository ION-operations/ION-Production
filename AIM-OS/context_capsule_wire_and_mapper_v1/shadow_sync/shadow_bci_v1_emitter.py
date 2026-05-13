#!/usr/bin/env python3
"""
Lane B - Shadow BCI Emitter Prototype v0.

Standalone, additive prototype that:
1) Ingests an extracted-file style fixture.
2) Emits bci_atom and bci_boundary_view records.
3) Validates records against Shadow BCI v1 schema.
4) Optionally writes JSON + JSONL output for replay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker

ALLOWED_PARSE_CONFIDENCE = {"High", "Degraded", "Fallback"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_sha256(payload: Dict[str, Any]) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_parse_confidence(value: Any) -> str:
    if isinstance(value, str) and value in ALLOWED_PARSE_CONFIDENCE:
        return value
    return "Fallback"


def ensure_required_fixture_fields(fixture: Dict[str, Any]) -> None:
    required = ["source_path", "source_text", "imports", "contracts"]
    missing = [key for key in required if key not in fixture]
    if missing:
        raise ValueError(f"Fixture missing required fields: {missing}")


def build_atom_record(
    *,
    source_ref: str,
    observed_at: str,
    parse_confidence: str,
    payload: Dict[str, Any],
    relations: List[Dict[str, str]] | None = None,
) -> Dict[str, Any]:
    record: Dict[str, Any] = {
        "record_type": "bci_atom",
        "record_id": str(uuid4()),
        "source_plane": "mapper",
        "source_ref": source_ref,
        "observed_at": observed_at,
        "recorded_at": utc_now_iso(),
        "valid_from": observed_at,
        "valid_to": None,
        "payload_hash": canonical_sha256(payload),
        "payload": payload,
        "provenance": {
            "producer": "shadow_bci_v1_emitter.py",
            "producer_version": "0.1.0",
            "parse_confidence": parse_confidence,
            "tool_call_id": None,
            "snapshot_id": None,
            "correlation_id": None,
        },
    }
    if relations:
        record["relations"] = relations
    return record


def build_boundary_view_record(
    *,
    source_path: str,
    observed_at: str,
    parse_confidence: str,
    view_level: str,
    payload: Dict[str, Any],
    relations: List[Dict[str, str]],
) -> Dict[str, Any]:
    return {
        "record_type": "bci_boundary_view",
        "record_id": str(uuid4()),
        "source_plane": "contextual_sync",
        "source_ref": source_path,
        "observed_at": observed_at,
        "recorded_at": utc_now_iso(),
        "valid_from": observed_at,
        "valid_to": None,
        "view_level": view_level,
        "payload_hash": canonical_sha256(payload),
        "payload": payload,
        "relations": relations,
        "provenance": {
            "producer": "shadow_bci_v1_emitter.py",
            "producer_version": "0.1.0",
            "parse_confidence": parse_confidence,
            "tool_call_id": None,
            "snapshot_id": None,
            "correlation_id": None,
        },
    }


def emit_records_from_fixture(fixture: Dict[str, Any]) -> List[Dict[str, Any]]:
    ensure_required_fixture_fields(fixture)

    source_path = fixture["source_path"]
    source_text = fixture["source_text"]
    imports = fixture.get("imports", [])
    contracts = fixture.get("contracts", [])
    resolved_dependencies = fixture.get("resolved_dependencies", [])
    parse_confidence = normalize_parse_confidence(fixture.get("parse_confidence"))
    observed_at = fixture.get("observed_at") or utc_now_iso()

    records: List[Dict[str, Any]] = []

    # File-level atom.
    file_payload = {
        "fact_type": "file_snapshot",
        "source_path": source_path,
        "parse_confidence": parse_confidence,
        "import_count": len(imports),
        "contract_count": len(contracts),
        "resolved_dependency_count": len(resolved_dependencies),
        "source_text_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
    }
    file_atom = build_atom_record(
        source_ref=source_path,
        observed_at=observed_at,
        parse_confidence=parse_confidence,
        payload=file_payload,
    )
    records.append(file_atom)
    file_atom_id = file_atom["record_id"]

    # Import atoms.
    for idx, import_decl in enumerate(imports):
        import_payload = {
            "fact_type": "import_decl",
            "source_path": source_path,
            "import_decl": import_decl,
            "ordinal": idx,
        }
        records.append(
            build_atom_record(
                source_ref=f"{source_path}::import::{idx}",
                observed_at=observed_at,
                parse_confidence=parse_confidence,
                payload=import_payload,
                relations=[{"to_record_id": file_atom_id, "relation_type": "derived_from"}],
            )
        )

    # Contract atoms.
    for contract in contracts:
        name = contract.get("name", "unknown")
        contract_payload = {
            "fact_type": "contract_decl",
            "source_path": source_path,
            "contract_kind": contract.get("kind"),
            "contract_name": name,
            "contract_signature": contract.get("signature"),
        }
        records.append(
            build_atom_record(
                source_ref=f"{source_path}::{name}",
                observed_at=observed_at,
                parse_confidence=parse_confidence,
                payload=contract_payload,
                relations=[{"to_record_id": file_atom_id, "relation_type": "derived_from"}],
            )
        )

    contract_names = [c.get("name", "unknown") for c in contracts]

    # L0 boundary view: concise operator/model-facing summary.
    l0_payload = {
        "view_type": "summary_boundary",
        "source_path": source_path,
        "unit_kind": "rust_file",
        "summary": (
            f"{source_path} exposes {len(contracts)} public contracts and "
            f"{len(imports)} imports with parse_confidence={parse_confidence}."
        ),
        "contract_names": contract_names,
        "resolved_dependencies": resolved_dependencies,
    }
    l0_view = build_boundary_view_record(
        source_path=source_path,
        observed_at=observed_at,
        parse_confidence=parse_confidence,
        view_level="L0",
        payload=l0_payload,
        relations=[{"to_record_id": file_atom_id, "relation_type": "derived_from"}],
    )
    records.append(l0_view)

    # L5 boundary view: source-adjacent representation.
    l5_payload = {
        "view_type": "source_adjacent_boundary",
        "source_path": source_path,
        "source_text": source_text,
        "imports": imports,
        "contracts": contracts,
        "parse_confidence": parse_confidence,
    }
    l5_view = build_boundary_view_record(
        source_path=source_path,
        observed_at=observed_at,
        parse_confidence=parse_confidence,
        view_level="L5",
        payload=l5_payload,
        relations=[{"to_record_id": file_atom_id, "relation_type": "derived_from"}],
    )
    records.append(l5_view)

    return records


def validate_records(
    records: List[Dict[str, Any]], schema_path: Path
) -> Tuple[bool, List[str]]:
    schema = read_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: List[str] = []

    for idx, record in enumerate(records):
        for err in validator.iter_errors(record):
            path = ".".join([str(part) for part in err.path]) if err.path else "<root>"
            errors.append(f"record[{idx}] path={path}: {err.message}")

    return len(errors) == 0, errors


def write_records(records: List[Dict[str, Any]], out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "shadow_bci_records.json"
    jsonl_path = out_dir / "shadow_bci_records.jsonl"

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2)

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {
        "json": str(json_path),
        "jsonl": str(jsonl_path),
    }


def summarize_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    record_types = [r.get("record_type") for r in records]
    view_levels = [r.get("view_level") for r in records if r.get("record_type") == "bci_boundary_view"]
    return {
        "record_count": len(records),
        "record_types": sorted(set([r for r in record_types if r])),
        "view_levels": sorted(set([v for v in view_levels if v])),
        "atom_count": sum(1 for r in records if r.get("record_type") == "bci_atom"),
        "boundary_view_count": sum(1 for r in records if r.get("record_type") == "bci_boundary_view"),
    }


def run_prototype(
    *,
    fixture_path: Path,
    schema_path: Path,
    out_dir: Path,
    write_output: bool,
) -> Dict[str, Any]:
    fixture = read_json(fixture_path)
    records = emit_records_from_fixture(fixture)
    is_valid, validation_errors = validate_records(records, schema_path)

    if not is_valid:
        raise ValueError("Schema validation failed:\n" + "\n".join(validation_errors))

    output_paths: Dict[str, str] = {}
    if write_output:
        output_paths = write_records(records, out_dir)

    return {
        "fixture_path": str(fixture_path),
        "schema_path": str(schema_path),
        "summary": summarize_records(records),
        "output_paths": output_paths,
        "records": records,
    }


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Emit Shadow BCI v1 prototype records.")
    parser.add_argument(
        "--fixture",
        type=Path,
        default=root / "fixtures" / "extracted_file_fixture_v0.json",
        help="Path to extracted-file style fixture JSON.",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=root / "shadow_bci_v1_schema.json",
        help="Path to Shadow BCI v1 JSON schema.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "out",
        help="Output directory for JSON and JSONL replay artifacts.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Run emission+validation without writing output files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = run_prototype(
            fixture_path=args.fixture,
            schema_path=args.schema,
            out_dir=args.out_dir,
            write_output=not args.no_write,
        )
    except Exception as exc:
        print(f"[shadow_sync] ERROR: {exc}", file=sys.stderr)
        return 1

    print("[shadow_sync] Emission and schema validation succeeded.")
    print(json.dumps(result["summary"], indent=2))
    if result["output_paths"]:
        print(json.dumps(result["output_paths"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
