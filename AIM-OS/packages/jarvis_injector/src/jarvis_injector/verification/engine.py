from __future__ import annotations

from jarvis_injector.core.models import DispatchContext, VerificationResult, VerificationSignal
from jarvis_injector.windows.window_controller import Win32WindowController


class VerificationEngine:
    def __init__(self, window_controller: Win32WindowController) -> None:
        self._window_controller = window_controller

    def verify(self, ctx: DispatchContext) -> VerificationResult:
        signals: list[VerificationSignal] = []

        if ctx.window is None:
            return VerificationResult(
                passed=False,
                signals=[VerificationSignal(name="window_missing", passed=False, detail="No resolved window in context")],
            )

        if not ctx.target.verification_policy:
            signals.append(
                VerificationSignal(
                    name="verification_policy_missing",
                    passed=False,
                    detail="Target has no verification policy configured",
                )
            )

        for rule in ctx.target.verification_policy:
            if rule == "window_visible":
                signals.append(VerificationSignal(name=rule, passed=bool(ctx.window.is_visible), detail="Window visibility check"))
            elif rule == "window_active":
                signals.append(
                    VerificationSignal(
                        name=rule,
                        passed=self._window_controller.is_foreground(ctx.window.hwnd),
                        detail="Foreground activation check",
                    )
                )
            else:
                signals.append(VerificationSignal(name=rule, passed=False, detail="Rule not implemented in Phase A"))

        return VerificationResult(
            passed=bool(signals) and all(signal.passed for signal in signals),
            signals=signals,
        )

