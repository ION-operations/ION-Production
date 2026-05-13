"""ION Capability Router v1.0.

Routes an objective to a candidate ION domain/agent/capability path.

Important boundary:
- A route is not action.
- A route is not accepted state.
- A route is a candidate state-transition plan that must still satisfy proof,
  approval/settlement, receipt, and state-surface sync.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple
import json

from ion_kernel.schemas import stable_hash, utc_now


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRAPH_PATH = ROOT / "capability_graph" / "capability_graph_seed.json"


def load_capability_graph(path: Path | None = None) -> Dict[str, Any]:
    graph_path = path or DEFAULT_GRAPH_PATH
    return json.loads(graph_path.read_text(encoding="utf-8"))


def _score_rule(objective: str, rule: Dict[str, Any]) -> int:
    text = objective.lower()
    return sum(1 for kw in rule.get("keywords", []) if str(kw).lower() in text)


def _resolve_capabilities(graph: Dict[str, Any], capability_ids: List[str]) -> List[Dict[str, Any]]:
    by_id = {cap.get("capability_id"): cap for cap in graph.get("capabilities", [])}
    resolved = []
    for cid in capability_ids:
        cap = by_id.get(cid)
        if cap:
            resolved.append(cap)
        else:
            resolved.append({
                "capability_id": cid,
                "capability_name": cid,
                "system_family": "UNKNOWN",
                "ion_domain": "UNRESOLVED",
                "authority_boundary": "capability id referenced but not found in seed graph",
                "proof_obligation": "capability registry repair required",
            })
    return resolved


def _scoreboard(objective: str, graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for rule in graph.get("route_rules", []):
        score = _score_rule(objective, rule)
        rows.append({
            "rule_id": rule.get("rule_id"),
            "score": score,
            "domain": rule.get("domain"),
            "agent_role": rule.get("agent_role"),
            "matched_keywords": [
                kw for kw in rule.get("keywords", [])
                if str(kw).lower() in objective.lower()
            ],
            "capabilities": rule.get("capabilities", []),
        })
    rows.sort(key=lambda row: (row["score"], row["rule_id"] or ""), reverse=True)
    return rows


def route_objective(objective: str, session_id: str = "route_session", graph: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Return a candidate route for an objective."""
    graph = graph or load_capability_graph()
    objective = objective.strip()
    score_rows = _scoreboard(objective, graph)
    best = score_rows[0] if score_rows else None
    selected_rule = None
    if best and best.get("score", 0) > 0:
        for rule in graph.get("route_rules", []):
            if rule.get("rule_id") == best.get("rule_id"):
                selected_rule = rule
                break

    if selected_rule is None:
        route = {
            "schema": "ion.capability_route.v1_0",
            "route_id": f"route_{stable_hash({'session': session_id, 'objective': objective, 'status': 'deferred'}, 12)}",
            "generated_at": utc_now(),
            "session_id": session_id,
            "objective": objective,
            "route_status": "DEFERRED",
            "domain": "UNCLASSIFIED",
            "agent_role": "ROUTER_REVIEW",
            "capabilities": [],
            "authority_ceiling": "human_review_required",
            "proof_obligations": ["operator classification", "capability registry review"],
            "state_claim": "candidate_route_only",
            "accepted_state_changed": False,
            "external_mutation_attempted": False,
            "scoreboard": score_rows,
            "trace": [
                {"step": "objective_received", "status": "ok"},
                {"step": "route_rules_scored", "status": "no_matching_rule"},
                {"step": "fallback_gate", "status": "human_review_required"},
            ],
            "non_claims": [
                "No Google Cloud, Gemini, MongoDB Atlas, or MCP call was made.",
                "No route is accepted state.",
                "Deferred routes cannot trigger tools without operator classification."
            ],
        }
        return route

    capabilities = _resolve_capabilities(graph, selected_rule.get("capabilities", []))
    proof_obligations = list(selected_rule.get("proof_obligations", []))
    route = {
        "schema": "ion.capability_route.v1_0",
        "route_id": f"route_{stable_hash({'session': session_id, 'objective': objective, 'rule': selected_rule.get('rule_id')}, 12)}",
        "generated_at": utc_now(),
        "session_id": session_id,
        "objective": objective,
        "route_status": "ROUTED",
        "route_rule": selected_rule.get("rule_id"),
        "domain": selected_rule.get("domain"),
        "agent_role": selected_rule.get("agent_role"),
        "capability_ids": selected_rule.get("capabilities", []),
        "capabilities": capabilities,
        "authority_ceiling": selected_rule.get("authority_ceiling"),
        "proof_obligations": proof_obligations,
        "receipt_required": True,
        "settlement_required": selected_rule.get("authority_ceiling") in {
            "human_gate_required",
            "blocked_without_explicit_operator_approval",
        },
        "state_claim": "candidate_route_only",
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
        "scoreboard": score_rows,
        "trace": [
            {"step": "objective_received", "status": "ok"},
            {"step": "route_rules_scored", "status": "ok", "selected_rule": selected_rule.get("rule_id")},
            {"step": "domain_bound", "status": "candidate", "domain": selected_rule.get("domain")},
            {"step": "agent_role_bound", "status": "candidate", "agent_role": selected_rule.get("agent_role")},
            {"step": "capabilities_resolved", "status": "candidate", "count": len(capabilities)},
            {"step": "proof_obligations_bound", "status": "required", "count": len(proof_obligations)},
            {"step": "state_boundary_locked", "status": "candidate_route_only"},
        ],
        "non_claims": [
            "No route executes a tool by itself.",
            "No route becomes accepted state without proof, settlement, and receipt.",
            "The capability graph is a seed, not an exhaustive Google infrastructure map."
        ],
    }
    return route


def route_many(objectives: List[str], session_id: str = "route_session", graph: Dict[str, Any] | None = None) -> Dict[str, Any]:
    graph = graph or load_capability_graph()
    routes = [route_objective(obj, session_id=session_id, graph=graph) for obj in objectives]
    return {
        "schema": "ion.capability_route_batch.v1_0",
        "generated_at": utc_now(),
        "session_id": session_id,
        "graph_schema": graph.get("schema"),
        "routes": routes,
        "route_counts": {
            "total": len(routes),
            "routed": sum(1 for r in routes if r.get("route_status") == "ROUTED"),
            "deferred": sum(1 for r in routes if r.get("route_status") == "DEFERRED"),
        },
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
    }
