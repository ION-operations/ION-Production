#!/usr/bin/env python3
"""Hand receipt-cleared dAimon context to Gemini and capture output as candidate.

This script performs a live Gemini API call only when a key is present. It never
prints or writes the key. Gemini output remains candidate witness material and
is not added to inheritable state.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from env_loader import load_local_env
from ion_kernel.bridge_core import classify_item
from ion_kernel.mongodb_adapter import MongoAdapterConfig, MongoAtlasAdapter
from ion_kernel.receipt_chain import issue_receipt_candidate
from ion_kernel.settlement_queue import build_settlement_queue


API_BASE = "https://generativelanguage.googleapis.com/v1beta"
PREFERRED_MODELS = [
    "models/gemini-2.5-flash",
    "models/gemini-2.0-flash",
    "models/gemini-2.0-flash-001",
    "models/gemini-1.5-flash-latest",
]


def _write_json(output_dir: Path, filename: str, payload: Mapping[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / filename).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _api_key() -> str | None:
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def _request_json(url: str, *, payload: Mapping[str, Any] | None = None, timeout: int = 45) -> tuple[int, dict[str, Any]]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"content-type": "application/json"} if payload is not None else {}
    method = "POST" if payload is not None else "GET"
    request = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            return int(response.status), data
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"raw_error": raw[:1200]}
        data["error_type"] = "HTTPError"
        data["status_code"] = int(exc.code)
        return int(exc.code), data
    except URLError as exc:
        return 0, {"error_type": "URLError", "error_message": str(exc.reason)}
    except TimeoutError as exc:
        return 0, {"error_type": "TimeoutError", "error_message": str(exc)}


def list_gemini_models(api_key: str, timeout: int = 45) -> tuple[int, dict[str, Any]]:
    url = f"{API_BASE}/models?key={quote(api_key)}"
    return _request_json(url, timeout=timeout)


def _supports_generate_content(model: Mapping[str, Any]) -> bool:
    methods = model.get("supportedGenerationMethods", [])
    return "generateContent" in methods


def select_gemini_model(api_key: str, preferred_model: str, timeout: int = 45) -> tuple[str, dict[str, Any]]:
    status, inventory = list_gemini_models(api_key, timeout=timeout)
    models = inventory.get("models", []) if status == 200 else []
    by_name = {model.get("name"): model for model in models if isinstance(model, Mapping)}
    preferred = preferred_model if preferred_model.startswith("models/") else f"models/{preferred_model}"
    candidates = [preferred, *PREFERRED_MODELS]
    for name in candidates:
        model = by_name.get(name)
        if model and _supports_generate_content(model):
            return name, {
                "models_list_status": status,
                "model_count": len(models),
                "selected_model": name,
                "selection_reason": "preferred_or_known_generate_content_model",
            }
    if preferred:
        return preferred, {
            "models_list_status": status,
            "model_count": len(models),
            "selected_model": preferred,
            "selection_reason": "fallback_to_requested_model_without_inventory_match",
            "inventory_error": inventory.get("error"),
        }
    return PREFERRED_MODELS[0], {
        "models_list_status": status,
        "model_count": len(models),
        "selected_model": PREFERRED_MODELS[0],
        "selection_reason": "fallback_default",
    }


def extract_gemini_text(response: Mapping[str, Any]) -> str:
    texts: list[str] = []
    for candidate in response.get("candidates", []) or []:
        content = candidate.get("content", {}) if isinstance(candidate, Mapping) else {}
        for part in content.get("parts", []) or []:
            if isinstance(part, Mapping) and isinstance(part.get("text"), str):
                texts.append(part["text"])
    return "\n".join(texts).strip()


def build_context_payload(
    session_id: str,
    inherited_objects: Sequence[Mapping[str, Any]],
    receipt_ids: Sequence[str],
    receipt_proof_hash: str | None,
) -> dict[str, Any]:
    context_objects = []
    for obj in inherited_objects:
        context_objects.append({
            "object_id": obj.get("object_id"),
            "source_file": obj.get("source_file"),
            "inferred_role": obj.get("inferred_role"),
            "authority_class": obj.get("authority_class"),
            "authority_score": obj.get("authority_score"),
            "acceptance_status": obj.get("acceptance_status"),
            "inheritance_status": obj.get("inheritance_status"),
            "proof_status": obj.get("proof_status"),
            "text_hash": obj.get("text_hash"),
            "text_excerpt": str(obj.get("text", ""))[:900],
        })
    return {
        "schema": "daimon.gemini_handoff_context.v0_1",
        "session_id": session_id,
        "receipt_ids": list(receipt_ids),
        "receipt_proof_hash": receipt_proof_hash,
        "inheritance_rule": "Only objects listed here are receipt-cleared context. Gemini output must return as candidate.",
        "objects": context_objects,
        "non_claims": [
            "Gemini output is not accepted state.",
            "Rejected, deferred, witness-only, and proof-debt objects are excluded from this context payload.",
        ],
    }


def build_prompt(context_payload: Mapping[str, Any], question: str) -> str:
    context_json = json.dumps(context_payload, indent=2, sort_keys=True)
    return (
        "You are a Gemini carrier receiving dAimon receipt-cleared context.\n"
        "Use only the provided context objects as trusted inherited state.\n"
        "Your response is candidate output and must not claim acceptance.\n"
        "Cite object_id values and receipt_ids when relying on context.\n"
        "Return under 350 words with sections named TRUSTED_CONTEXT_USED, CANDIDATE_OUTPUT, and NON_CLAIMS.\n\n"
        f"Operator question:\n{question}\n\n"
        f"dAimon context payload:\n{context_json}\n"
    )


def call_gemini(api_key: str, model: str, prompt: str, timeout: int = 60) -> tuple[int, dict[str, Any]]:
    generation_config: dict[str, Any] = {"temperature": 0.2, "maxOutputTokens": 1200}
    if "gemini-2.5-flash" in model:
        generation_config["thinkingConfig"] = {"thinkingBudget": 0}
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": generation_config,
    }
    url = f"{API_BASE}/{model}:generateContent?key={quote(api_key)}"
    return _request_json(url, payload=payload, timeout=timeout)


def run_gemini_handoff(
    *,
    session_id: str,
    inherited_objects: Sequence[Mapping[str, Any]],
    receipt_ids: Sequence[str],
    receipt_proof_hash: str | None,
    question: str,
    output_dir: Path,
    preferred_model: str = "gemini-2.5-flash",
    timeout: int = 60,
) -> dict[str, Any]:
    api_key = _api_key()
    if not api_key:
        summary = {
            "schema": "daimon.gemini_handoff_summary.v0_1",
            "ok": False,
            "blocked": True,
            "reason": "GEMINI_API_KEY or GOOGLE_API_KEY is required",
            "accepted_state_changed": False,
            "external_mutation_attempted": False,
        }
        _write_json(output_dir, "gemini_handoff_summary.json", summary)
        return summary
    if not inherited_objects:
        summary = {
            "schema": "daimon.gemini_handoff_summary.v0_1",
            "ok": False,
            "blocked": True,
            "reason": "no inherited objects were supplied to Gemini handoff",
            "accepted_state_changed": False,
            "external_mutation_attempted": False,
        }
        _write_json(output_dir, "gemini_handoff_summary.json", summary)
        return summary

    model, model_selection = select_gemini_model(api_key, preferred_model, timeout=timeout)
    context_payload = build_context_payload(session_id, inherited_objects, receipt_ids, receipt_proof_hash)
    prompt = build_prompt(context_payload, question)
    request_artifact = {
        "schema": "daimon.gemini_handoff_request.v0_1",
        "provider": "generativelanguage.googleapis.com",
        "model": model,
        "endpoint": f"{API_BASE}/{model}:generateContent?key=REDACTED",
        "question": question,
        "context_object_count": len(inherited_objects),
        "receipt_ids": list(receipt_ids),
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
    }
    _write_json(output_dir, "gemini_handoff_context_bundle.json", context_payload)
    _write_json(output_dir, "gemini_handoff_request.json", request_artifact)

    status, response = call_gemini(api_key, model, prompt, timeout=timeout)
    output_text = extract_gemini_text(response)
    candidate_objects = []
    candidate_queue = []
    candidate_receipt = None
    if output_text:
        candidate = classify_item(
            session_id=session_id,
            source_file="gemini_handoff_response.json",
            source_format="gemini_generate_content",
            declared_type="assistant_synthesis",
            text=output_text,
            index=0,
        )
        candidate_objects = [candidate.to_dict()]
        candidate_queue = [item.to_dict() for item in build_settlement_queue([candidate])]
        candidate_receipt = issue_receipt_candidate(
            session_id,
            [candidate],
            issued_by="gemini_handoff_demo",
            receipt_label="gemini_candidate_001",
            receipt_type="GEMINI_CANDIDATE_RETURN",
            non_claims=[
                "Gemini output was captured as candidate witness material.",
                "Gemini output is not accepted state and is not inheritable without later settlement.",
                "The live API call proves carrier handoff only, not complete Agent Builder deployment.",
            ],
        ).to_dict()

    response_artifact = {
        "schema": "daimon.gemini_handoff_response.v0_1",
        "provider": "generativelanguage.googleapis.com",
        "status_code": status,
        "model": model,
        "raw_response": response,
        "output_text": output_text,
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
    }
    candidate_artifact = {
        "schema": "daimon.gemini_candidate_output.v0_1",
        "session_id": session_id,
        "gemini_output_captured_as_candidate": bool(candidate_objects),
        "candidate_objects": candidate_objects,
        "settlement_queue": candidate_queue,
        "candidate_receipt": candidate_receipt,
        "inheritance_status": candidate_objects[0]["inheritance_status"] if candidate_objects else None,
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
        "non_claim": "Gemini output is candidate witness material until a later settlement accepts or rejects it.",
    }
    ok = status == 200 and bool(output_text) and bool(candidate_objects)
    summary = {
        "schema": "daimon.gemini_handoff_summary.v0_1",
        "ok": ok,
        "provider": "generativelanguage.googleapis.com",
        "model": model,
        "model_selection": model_selection,
        "status_code": status,
        "context_object_count": len(inherited_objects),
        "receipt_ids": list(receipt_ids),
        "gemini_output_captured_as_candidate": bool(candidate_objects),
        "candidate_object_count": len(candidate_objects),
        "candidate_receipt_id": candidate_receipt["receipt_id"] if candidate_receipt else None,
        "candidate_inheritance_status": candidate_artifact["inheritance_status"],
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
        "external_service_called": True,
        "non_claim": "This proves a Gemini carrier handoff, not automatic trust in Gemini output.",
    }
    _write_json(output_dir, "gemini_handoff_response.json", response_artifact)
    _write_json(output_dir, "gemini_candidate_output.json", candidate_artifact)
    _write_json(output_dir, "gemini_handoff_summary.json", summary)
    return {
        **summary,
        "candidate_objects": candidate_objects,
        "candidate_queue": candidate_queue,
        "candidate_receipt": candidate_receipt,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-id", default="sample_session_20260509")
    parser.add_argument("--model", default="gemini-2.5-flash")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument(
        "--question",
        default="Summarize what the next dAimon session may inherit, and name what remains excluded.",
    )
    args = parser.parse_args()

    load_local_env(ROOT / ".env")
    cfg = MongoAdapterConfig.from_env()
    adapter = MongoAtlasAdapter(cfg)
    inherited = adapter.find_inheritable_objects(args.session_id, limit=25)
    receipts = adapter.find_receipts_for_session(args.session_id, limit=5)
    receipt_ids = [receipt["receipt_id"] for receipt in receipts]
    receipt_proof_hash = receipts[0].get("proof_hash") if receipts else None
    summary = run_gemini_handoff(
        session_id=args.session_id,
        inherited_objects=inherited,
        receipt_ids=receipt_ids,
        receipt_proof_hash=receipt_proof_hash,
        question=args.question,
        output_dir=ROOT / "sample_outputs",
        preferred_model=args.model,
        timeout=args.timeout,
    )
    printable = {k: v for k, v in summary.items() if k not in {"candidate_objects", "candidate_queue", "candidate_receipt"}}
    print(json.dumps(printable, indent=2))
    return 0 if summary.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
