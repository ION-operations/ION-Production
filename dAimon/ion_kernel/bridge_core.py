"""Core classifier for ION Continuity Bridge.

Classification is deliberately conservative: all imports begin as witness
material, and most objects require settlement before future inheritance.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import csv
import json
import re

from ion_kernel.schemas import ContinuityObject, stable_hash


def _authority_for_source(source_file: str, declared_type: str, text: str) -> tuple[str, int]:
    name = source_file.lower()
    lower = text.lower()
    if "operator" in name or "user" in declared_type:
        return "direct_operator_statement", 85
    if "source" in name or "http" in lower:
        return "source_manifest_or_external_reference", 72
    if "task" in name:
        return "task_backlog", 62
    if "assistant" in name or "export" in name:
        return "assistant_synthesis", 45
    return "unclassified_witness", 35


def _infer_role(declared_type: str, text: str) -> str:
    lower = text.lower()
    if "decision" in lower or declared_type == "decision":
        return "CANDIDATE_DECISION"
    if "risk" in lower or "blocked" in lower:
        return "RISK_OR_BLOCKER"
    if "todo" in lower or "task" in lower or declared_type == "task":
        return "NEXT_WORK_CANDIDATE"
    if "http" in lower or "source" in declared_type:
        return "SOURCE_REFERENCE"
    if "receipt" in lower:
        return "RECEIPT_REFERENCE"
    return "CANDIDATE_CLAIM"


def _proof_status(role: str, authority_score: int, text: str) -> str:
    lower = text.lower()
    if "http" in lower or "receipt" in lower or "sha256" in lower:
        return "HAS_EVIDENCE_POINTER"
    if authority_score >= 80:
        return "OPERATOR_STATEMENT_NEEDS_SETTLEMENT"
    if role in {"SOURCE_REFERENCE", "RECEIPT_REFERENCE"}:
        return "REFERENCE_NEEDS_VERIFICATION"
    return "PROOF_DEBT_MISSING_EVIDENCE"


def _risk_flags(role: str, authority_score: int, proof_status: str) -> List[str]:
    flags = []
    if authority_score < 55:
        flags.append("low_authority_import")
    if "MISSING" in proof_status or "NEEDS" in proof_status:
        flags.append("needs_proof_or_settlement")
    if role == "RISK_OR_BLOCKER":
        flags.append("risk_or_blocker")
    return flags


def classify_item(session_id: str, source_file: str, source_format: str, declared_type: str, text: str, index: int) -> ContinuityObject:
    authority_class, authority_score = _authority_for_source(source_file, declared_type, text)
    role = _infer_role(declared_type, text)
    proof_status = _proof_status(role, authority_score, text)
    risk_flags = _risk_flags(role, authority_score, proof_status)
    object_id = f"co_{stable_hash({'s': session_id, 'f': source_file, 'i': index, 't': text}, 10)}"
    can_inherit = authority_score >= 80 and "HAS_EVIDENCE" in proof_status
    return ContinuityObject(
        object_id=object_id,
        session_id=session_id,
        source_file=source_file,
        source_format=source_format,
        text=text.strip(),
        declared_type=declared_type,
        inferred_role=role,
        authority_class=authority_class,
        authority_score=authority_score,
        acceptance_status="candidate_needs_settlement",
        acceptance_role="WITNESS_OR_CANDIDATE",
        inheritance_status="NOT_INHERITABLE_AS_STATE_WITHOUT_SETTLEMENT" if not can_inherit else "POTENTIALLY_INHERITABLE_AFTER_RECEIPT",
        requires_settlement=True,
        proof_status=proof_status,
        risk_flags=risk_flags,
        text_hash=stable_hash({"text": text, "source": source_file})
    )


def _load_json(path: Path) -> List[Dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows: List[Dict[str, str]] = []
    if isinstance(data, dict) and "items" in data:
        for item in data["items"]:
            rows.append({
                "declared_type": str(item.get("type", "json_item")),
                "text": str(item.get("text", "")),
                "source_format": "json_items"
            })
    elif isinstance(data, list):
        for item in data:
            rows.append({
                "declared_type": str(item.get("type", "json_item")) if isinstance(item, dict) else "json_value",
                "text": str(item.get("text", item)) if isinstance(item, dict) else str(item),
                "source_format": "json_list"
            })
    else:
        rows.append({"declared_type": "json_document", "text": json.dumps(data, sort_keys=True), "source_format": "json_document"})
    return rows


def _load_csv(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row.get("text") or row.get("task") or row.get("claim") or row.get("source") or json.dumps(row, sort_keys=True)
            declared_type = row.get("type") or row.get("kind") or "csv_row"
            rows.append({"declared_type": declared_type, "text": text, "source_format": "csv_row"})
    return rows


def _load_markdown(path: Path) -> List[Dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    chunks = [c.strip() for c in re.split(r"\n\s*[-#]{2,}.*\n", text) if c.strip()]
    if not chunks:
        chunks = [text.strip()]
    return [{"declared_type": "markdown_note", "text": c[:2000], "source_format": "markdown_chunk"} for c in chunks]


def import_bundle(input_dir: Path, session_id: str) -> List[ContinuityObject]:
    objects: List[ContinuityObject] = []
    supported = {".json", ".md", ".csv"}
    files = sorted([p for p in input_dir.rglob("*") if p.is_file() and p.suffix.lower() in supported])
    for path in files:
        if path.suffix.lower() == ".json":
            rows = _load_json(path)
        elif path.suffix.lower() == ".csv":
            rows = _load_csv(path)
        else:
            rows = _load_markdown(path)
        for idx, row in enumerate(rows):
            text = row["text"].strip()
            if text:
                objects.append(classify_item(
                    session_id=session_id,
                    source_file=str(path.relative_to(input_dir)),
                    source_format=row["source_format"],
                    declared_type=row["declared_type"],
                    text=text,
                    index=len(objects) + idx,
                ))
    return objects
