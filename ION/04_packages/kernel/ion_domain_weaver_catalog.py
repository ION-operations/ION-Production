"""Leaf static catalog constants for Domain Weaver.

This module is intentionally stdlib-only and must not import the Domain Weaver
monolith or stateful owner modules.
"""
from __future__ import annotations

SCHEMA_ID = "ion.domain_weaver.projection.v1"
PROMOTION_REVIEW_SCHEMA_ID = "ion.domain_weaver.promotion_review.v1"
PROMOTION_GATE_SCHEMA_ID = "ion.domain_weaver.promotion_gate.v1"
DOGFOOD_CONTEXT_CAPSULE_SCHEMA_ID = "ion.domain_weaver.dogfood_context_capsule.v1"
DOGFOOD_NEXT_PACKET_SCHEMA_ID = "ion.domain_weaver.dogfood_next_packet_candidate.v1"
STEWARD_READY_REVIEW_SCHEMA_ID = "ion.domain_weaver.steward_ready_review.v1"
PHASE_CLOSURE_REVIEW_SCHEMA_ID = "ion.domain_weaver.phase_closure_review.v0_1"
FOUNDING_DOMAIN_ASSEMBLY_SCHEMA_ID = "ion.domain_weaver.founding_domain_assembly.v0_1_candidate"
OPERATOR_ACTION_SCHEMA_ID = "ion.domain_weaver.operator_action_result.v0_1"
OPERATOR_ACTION_RECORD_SCHEMA_ID = "ion.domain_weaver.operator_action_record.v0_1"
