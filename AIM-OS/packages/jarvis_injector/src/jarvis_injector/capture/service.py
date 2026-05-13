from __future__ import annotations

from jarvis_injector.capture.live_cdp import LiveCdpCaptureClient
from jarvis_injector.capture.live_uia import LiveUiaCaptureClient
from jarvis_injector.capture.browser_dom import DomCaptureParser
from jarvis_injector.capture.models import (
    BlockType,
    CaptureRequest,
    CaptureSource,
    CaptureSourceKind,
    CaptureVerification,
    CapturedMessage,
    InlineSpan,
    InlineSpanType,
    MessageBlock,
)
from jarvis_injector.capture.normalize import blocks_to_markdown, blocks_to_plaintext
from jarvis_injector.capture.uia_tree import UiaCaptureParser
from jarvis_injector.registry.target_registry import TargetRegistry
from jarvis_injector.windows.window_controller import Win32WindowController


class CaptureService:
    def __init__(
        self,
        target_registry: TargetRegistry | None = None,
        window_controller: Win32WindowController | None = None,
    ) -> None:
        self._target_registry = target_registry
        self._window_controller = window_controller
        self._dom_parser = DomCaptureParser()
        self._uia_parser = UiaCaptureParser()
        self._live_cdp = LiveCdpCaptureClient()
        self._live_uia = LiveUiaCaptureClient(window_controller) if window_controller else None

    def capture_last_message(self, request: CaptureRequest) -> CapturedMessage:
        for source_kind in request.source_preference:
            if source_kind == CaptureSourceKind.LIVE:
                live_result = self._capture_live(request)
                if live_result is not None:
                    return live_result
            if source_kind == CaptureSourceKind.DOM and request.html_snapshot:
                return self._dom_parser.parse(request)
            if source_kind == CaptureSourceKind.UIA and request.uia_tree:
                return self._uia_parser.parse(request)
            if source_kind == CaptureSourceKind.PLAINTEXT and request.plain_text:
                return self._capture_plaintext(request)

        live_errors = request.metadata.get("liveCaptureErrors", [])
        detail = []
        if live_errors:
            detail.append(f"live attempts failed: {', '.join(str(error) for error in live_errors)}")
        detail.append("provide html_snapshot, uia_tree, or plain_text when live capture is unavailable")
        raise ValueError("; ".join(detail))

    def _capture_live(self, request: CaptureRequest) -> CapturedMessage | None:
        if self._target_registry is None:
            return None
        target = self._target_registry.get(request.target_id)
        if target is None:
            raise ValueError(f"Unknown target '{request.target_id}'")

        live_errors: list[str] = []
        if self._live_cdp.is_supported(target):
            try:
                return self._live_cdp.capture(request, target)
            except Exception as exc:
                live_errors.append(f"cdp:{exc}")

        if self._live_uia is not None:
            try:
                return self._live_uia.capture(request, target)
            except Exception as exc:
                live_errors.append(f"uia:{exc}")

        if live_errors:
            request.metadata["liveCaptureErrors"] = live_errors
        return None

    def _capture_plaintext(self, request: CaptureRequest) -> CapturedMessage:
        blocks = [
            MessageBlock(
                id="block_1",
                type=BlockType.PARAGRAPH,
                spans=[InlineSpan(type=InlineSpanType.TEXT, text=request.plain_text or "")],
            )
        ]
        return CapturedMessage(
            target_id=request.target_id,
            message_id="plaintext-message-1",
            source=CaptureSource(
                adapter="capture.plaintext",
                kind=CaptureSourceKind.PLAINTEXT,
                confidence=0.2,
                provider=request.provider,
            ),
            verification=CaptureVerification(
                stable=False,
                completeness_score=0.2,
                indicators=["plaintext_fallback"],
            ),
            blocks=blocks,
            plaintext=blocks_to_plaintext(blocks),
            markdown=blocks_to_markdown(blocks),
            metadata={**request.metadata, "fallback": True},
        )
