from enum import StrEnum


class AdapterKind(StrEnum):
    CDP = "cdp"
    UIA = "uia"
    KEYBOARD = "keyboard"
    VISUAL = "visual"


class DispatchState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    REPAIRED = "repaired"
    FAILED = "failed"
    TIMEOUT = "timeout"


class PolicyMode(StrEnum):
    MANUAL_ASSIST = "manual_assist"
    SEMI_AUTONOMOUS = "semi_autonomous"
    AUTONOMOUS_WITH_APPROVALS = "autonomous_with_approvals"
    TRUSTED_TARGETS = "trusted_targets"


class Initiator(StrEnum):
    CLI = "cli"
    HOTKEY = "hotkey"
    JOC = "joc"
    TRAY = "tray"


class ArtifactKind(StrEnum):
    DOM_LOCATOR = "dom_locator"
    UIA_LOCATOR = "uia_locator"
    TEMPLATE = "template"
    MOTION = "motion"
    WORKFLOW = "workflow"
    FINGERPRINT = "fingerprint"

