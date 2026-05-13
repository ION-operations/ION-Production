from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from time import monotonic, sleep
from urllib.error import URLError

from jarvis_injector.capture.browser_dom import DomCaptureParser
from jarvis_injector.capture.models import CaptureRequest, CaptureSourceKind, CapturedMessage
from jarvis_injector.core.models import TargetProfile


@dataclass
class CdpPageSnapshot:
    html: str
    url: str
    title: str
    stable: bool


@dataclass
class CdpPageCandidate:
    url: str
    title: str
    score: int
    avoided: bool


class LiveCdpCaptureClient:
    def __init__(self) -> None:
        self._parser = DomCaptureParser()

    def is_supported(self, target: TargetProfile) -> bool:
        return target.cdp is not None

    def capture(self, request: CaptureRequest, target: TargetProfile) -> CapturedMessage:
        if target.cdp is None:
            raise ValueError(f"Target '{target.id}' has no CDP profile")

        page_snapshot = self._capture_page_snapshot(target, request.live_timeout_ms)
        parsed = self._parser.parse(
            request.model_copy(
                update={
                    "html_snapshot": page_snapshot.html,
                    "source_preference": [CaptureSourceKind.DOM],
                }
            )
        )
        parsed.source.adapter = "capture.live_cdp"
        parsed.source.kind = CaptureSourceKind.LIVE
        parsed.source.confidence = 0.91 if page_snapshot.stable else 0.67
        parsed.verification.stable = page_snapshot.stable
        parsed.verification.completeness_score = max(parsed.verification.completeness_score, 0.78 if page_snapshot.stable else 0.55)
        parsed.verification.indicators.extend(["cdp_attached", "dom_snapshot_acquired"])
        parsed.metadata["pageUrl"] = page_snapshot.url
        parsed.metadata["pageTitle"] = page_snapshot.title
        return parsed

    def _capture_page_snapshot(self, target: TargetProfile, timeout_ms: int) -> CdpPageSnapshot:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:  # pragma: no cover
            raise ValueError("Playwright is required for live CDP capture") from exc

        host = target.cdp.host
        port = target.cdp.remote_debugging_port
        endpoint = f"http://{host}:{port}"
        self._ensure_endpoint_responding(endpoint)
        preferred_page = self._wait_for_preferred_page(endpoint, target, timeout_ms)

        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(endpoint)
            try:
                page = self._select_page(browser, target, preferred_page)
                if page is None:
                    raise ValueError(f"No matching CDP page found for target '{target.id}'")

                stable = False
                html = page.content()
                last_length = len(html)
                deadline = monotonic() + max(timeout_ms, 1000) / 1000
                while monotonic() < deadline:
                    sleep(0.2)
                    candidate = page.content()
                    if len(candidate) == last_length:
                        html = candidate
                        stable = True
                        break
                    html = candidate
                    last_length = len(candidate)

                return CdpPageSnapshot(
                    html=html,
                    url=page.url,
                    title=page.title(),
                    stable=stable,
                )
            finally:
                browser.close()

    def _wait_for_preferred_page(self, endpoint: str, target: TargetProfile, timeout_ms: int) -> CdpPageCandidate | None:
        deadline = monotonic() + max(timeout_ms, 1000) / 1000
        best_candidate: CdpPageCandidate | None = None

        while monotonic() < deadline:
            candidates = self._list_page_candidates(endpoint, target)
            if candidates:
                candidates.sort(key=lambda item: (item.score, not item.avoided), reverse=True)
                candidate = candidates[0]
                best_candidate = candidate
                if candidate.score >= 60 and not candidate.avoided:
                    return candidate
            sleep(0.2)

        return best_candidate

    def _list_page_candidates(self, endpoint: str, target: TargetProfile) -> list[CdpPageCandidate]:
        try:
            with urllib.request.urlopen(f"{endpoint}/json/list", timeout=2) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except URLError as exc:
            raise ValueError(f"Unable to enumerate CDP pages at {endpoint}") from exc

        candidates: list[CdpPageCandidate] = []
        for entry in payload:
            if entry.get("type") != "page":
                continue
            title = str(entry.get("title", ""))
            url = str(entry.get("url", ""))
            score, avoided = self._score_candidate(title, url, target)
            candidates.append(CdpPageCandidate(url=url, title=title, score=score, avoided=avoided))
        return candidates

    def _select_page(self, browser, target: TargetProfile, preferred: CdpPageCandidate | None):
        candidates = []
        for context in browser.contexts:
            for page in context.pages:
                title = page.title()
                url = page.url
                score, avoided = self._score_candidate(title, url, target)
                if preferred is not None and preferred.url == url and preferred.title == title:
                    score += 100
                candidates.append((score, avoided, page))

        if not candidates:
            return None

        candidates.sort(key=lambda item: (item[0], not item[1]), reverse=True)
        return candidates[0][2]

    def _score_candidate(self, title: str, url: str, target: TargetProfile) -> tuple[int, bool]:
        import re

        lowered_title = title.lower()
        lowered_url = url.lower()
        score = 0
        avoided = False

        title_patterns = target.cdp.title_patterns if target.cdp else []
        avoid_url_patterns = target.cdp.avoid_url_patterns if target.cdp else []
        url_patterns = target.cdp.url_patterns if target.cdp else []

        if target.title_regex:
            try:
                if re.search(target.title_regex, title, flags=re.IGNORECASE):
                    score += 35
            except re.error:
                pass

        if title_patterns and any(pattern.lower() in lowered_title for pattern in title_patterns):
            score += 30

        if url_patterns and any(pattern.lower() in lowered_url for pattern in url_patterns):
            score += 60

        if lowered_url.startswith(("chrome://", "edge://", "devtools://", "about:blank")):
            score -= 80
            avoided = True

        if avoid_url_patterns and any(pattern.lower() in lowered_url for pattern in avoid_url_patterns):
            score -= 90
            avoided = True

        if lowered_url.startswith("file:///") and (title_patterns or target.title_regex):
            score += 20

        return score, avoided

    @staticmethod
    def _ensure_endpoint_responding(endpoint: str) -> None:
        try:
            with urllib.request.urlopen(f"{endpoint}/json/version", timeout=2) as response:
                payload = json.loads(response.read().decode("utf-8"))
                if "Browser" not in payload:
                    raise ValueError("CDP endpoint did not return browser metadata")
        except Exception as exc:
            raise ValueError(f"Unable to reach CDP endpoint at {endpoint}") from exc
