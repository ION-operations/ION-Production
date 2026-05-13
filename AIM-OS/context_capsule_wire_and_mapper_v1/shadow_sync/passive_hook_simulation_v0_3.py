#!/usr/bin/env python3
"""
Lane B isolated simulation for a passive shadow emission hook.

This script does not integrate with live runtime seams. It simulates:
- feature flag off-by-default behavior
- observational-only shadow emission
- fail-open behavior on shadow failures
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import mapper_adapter_v0_1 as adapter
import shadow_bci_v1_emitter as emitter


LOGGER = logging.getLogger("shadow_sync.passive_hook_simulation")
ROOT = Path(__file__).resolve().parent
DEFAULT_SNAPSHOT = ROOT / "fixtures" / "live_mapper_snapshot_v0_1.json"
DEFAULT_SCHEMA = ROOT / "shadow_bci_v1_schema.json"


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def simulate_live_response(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    extracted = snapshot.get("extracted_file", {})
    contracts = extracted.get("contracts", [])
    imports = extracted.get("imports", [])
    return {
        "status": "ok",
        "target_path": snapshot.get("target_path"),
        "summary": {
            "import_count": len(imports),
            "contract_count": len(contracts),
            "resolved_dependency_count": len(snapshot.get("resolved_local_files", [])),
        },
    }


def run_passive_hook(
    snapshot: Dict[str, Any],
    *,
    shadow_enabled: bool,
    schema_path: Path,
    inject_shadow_failure: bool = False,
) -> Dict[str, Any]:
    """
    Simulate passive shadow emission alongside live response generation.

    Returns an envelope with separate `live_response` and `shadow_observation`
    to make observational-only behavior explicit in this isolated simulation.
    """
    live_response = simulate_live_response(snapshot)

    if not shadow_enabled:
        return {
            "live_response": live_response,
            "shadow_observation": {
                "attempted": False,
                "success": False,
                "record_count": 0,
                "error": None,
            },
        }

    try:
        adapted = adapter.adapt_live_mapper_snapshot(snapshot)
        if inject_shadow_failure:
            raise RuntimeError("Injected shadow failure for fail-open simulation")
        records = emitter.emit_records_from_fixture(adapted)
        ok, errors = emitter.validate_records(records, schema_path)
        if not ok:
            raise ValueError(f"Schema validation failed: {'; '.join(errors)}")
        return {
            "live_response": live_response,
            "shadow_observation": {
                "attempted": True,
                "success": True,
                "record_count": len(records),
                "error": None,
            },
        }
    except Exception as exc:  # fail-open by design in this simulation
        LOGGER.warning("Shadow emission failed; continuing live path: %s", exc)
        return {
            "live_response": live_response,
            "shadow_observation": {
                "attempted": True,
                "success": False,
                "record_count": 0,
                "error": str(exc),
            },
        }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Isolated passive hook simulation (Lane B, no live seam integration)."
    )
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=DEFAULT_SNAPSHOT,
        help="Path to mocked live mapper snapshot fixture JSON.",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help="Path to BCI schema for validation.",
    )
    parser.add_argument(
        "--enable-shadow",
        action="store_true",
        help="Enable passive shadow emission attempt.",
    )
    parser.add_argument(
        "--inject-failure",
        action="store_true",
        help="Inject a shadow failure to verify fail-open behavior.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    return parser


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    parser = build_arg_parser()
    args = parser.parse_args()

    snapshot = read_json(args.snapshot)
    result = run_passive_hook(
        snapshot,
        shadow_enabled=args.enable_shadow,
        schema_path=args.schema,
        inject_shadow_failure=args.inject_failure,
    )
    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
