from dataclasses import dataclass


@dataclass(frozen=True)
class AgentRole:
    id: str
    description: str


PLANNER = AgentRole("planner", "Converts operator intent into task graphs")
NAVIGATOR = AgentRole("navigator", "Chooses the best local execution path")
VISION_REPAIR = AgentRole("vision_repair", "Repairs broken locators and visual anchors")
ARTIFACT_CURATOR = AgentRole("artifact_curator", "Decides what new artifacts should be persisted")
CODE_ENGINEER = AgentRole("code_engineer", "Uses coding agents to extend adapters and tests")
AUDITOR = AgentRole("auditor", "Checks success, safety, and reproducibility")

