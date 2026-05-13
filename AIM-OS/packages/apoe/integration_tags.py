"""Integration Tag Helpers for APOE."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class IntegrationSystem:
    name: str
    priority: Optional[str] = None


@dataclass
class IntegrationTagContext:
    system: Optional[IntegrationSystem] = None
    integration_type: Optional[str] = None
    connection: Optional[str] = None
    modality: Optional[str] = None
    action: Optional[str] = None
    mode: Optional[str] = None
    agent: Optional[str] = None
    extras: List[str] = field(default_factory=list)


def build_integration_tags(context: IntegrationTagContext) -> List[str]:
    """Convert context into standardized tag list."""
    tags: List[str] = []

    if context.system:
        priority = context.system.priority or "p0"
        tags.append(f"system:{context.system.name}:{priority}")

    if context.integration_type:
        tags.append(f"integration_type:{context.integration_type}")

    if context.connection:
        tags.append(f"connection:{context.connection}")

    if context.modality:
        tags.append(f"modality:{context.modality}")

    if context.action:
        tags.append(f"action:{context.action}")

    if context.mode:
        tags.append(f"mode:{context.mode}")

    if context.agent:
        tags.append(f"agent:{context.agent}")

    if context.extras:
        tags.extend([extra for extra in context.extras if extra])

    if "chat_ide" not in tags:
        tags.append("chat_ide")

    # Deduplicate
    return list(dict.fromkeys(tags))


def integration_tags_to_dict(tags: List[str]) -> Dict[str, float]:
    """Weight tags for CMC storage."""
    weights: Dict[str, float] = {}

    for tag in tags:
        weight = 0.9
        if tag.startswith("system:"):
            weight = 1.0
        elif tag.startswith("integration_type:"):
            weight = 1.0
        elif tag.startswith("modality:"):
            weight = 1.0
        elif tag.startswith("connection:"):
            weight = 0.9
        elif tag == "chat_ide":
            weight = 1.0
        elif tag.startswith(("action:", "mode:", "agent:")):
            weight = 0.85
        else:
            weight = 0.8

        weights[tag] = weight

    return weights


def merge_integration_context(
    base: Optional[IntegrationTagContext],
    override: Optional[IntegrationTagContext]
) -> IntegrationTagContext:
    """Merge base context with overrides."""
    merged = IntegrationTagContext()

    merged.system = _merge_system(base.system if base else None, override.system if override else None)
    merged.integration_type = override.integration_type or (base.integration_type if base else None)
    merged.connection = override.connection or (base.connection if base else None)
    merged.modality = override.modality or (base.modality if base else None)
    merged.action = override.action or (base.action if base else None)
    merged.mode = override.mode or (base.mode if base else None)
    merged.agent = override.agent or (base.agent if base else None)

    extras: List[str] = []
    if base and base.extras:
        extras.extend(base.extras)
    if override and override.extras:
        extras.extend(override.extras)
    merged.extras = list(dict.fromkeys([extra for extra in extras if extra]))

    return merged


def _merge_system(
    base: Optional[IntegrationSystem],
    override: Optional[IntegrationSystem]
) -> Optional[IntegrationSystem]:
    if not base and not override:
        return None

    name = override.name if override and override.name else (base.name if base else None)
    priority = override.priority if override and override.priority else (base.priority if base else None)

    if not name:
        return None

    return IntegrationSystem(name=name, priority=priority)
