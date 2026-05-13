from jarvis_injector.core.models import DispatchContext


PHASE_TIMEOUTS_MS = {
    "find_window": 2000,
    "restore_activate": 2000,
    "locate_input": 3000,
    "submit_verify": 5000,
    "repair_pass": 8000,
}


class DispatchStateMachine:
    phase_order = [
        "resolve_target",
        "find_window",
        "restore_if_minimized",
        "activate_window",
        "wait_for_ready",
        "choose_adapter",
        "locate_input",
        "set_text",
        "submit",
        "verify",
    ]

    def phases(self) -> list[str]:
        return list(self.phase_order)

    def run(self, ctx: DispatchContext) -> DispatchContext:
        return ctx

