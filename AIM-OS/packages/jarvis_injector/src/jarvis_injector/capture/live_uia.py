from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from jarvis_injector.capture.models import CaptureRequest, CaptureSourceKind, CapturedMessage, UiTreeNode
from jarvis_injector.capture.uia_tree import UiaCaptureParser
from jarvis_injector.core.models import Rect, ResolvedWindow, SearchRegion, TargetProfile, UiaCaptureProfile
from jarvis_injector.windows.window_controller import Win32WindowController


@dataclass
class UiaSnapshot:
    root: UiTreeNode
    stable: bool
    panel_id: str | None = None
    message_role: str | None = None


class LiveUiaCaptureClient:
    def __init__(self, window_controller: Win32WindowController) -> None:
        self._window_controller = window_controller
        self._parser = UiaCaptureParser()

    def capture(self, request: CaptureRequest, target: TargetProfile) -> CapturedMessage:
        window = self._window_controller.find_window(target)
        if window is None:
            raise ValueError(f"Target window not found for '{target.id}'")

        snapshot = self._capture_uia_tree(window, target)
        parsed = self._parser.parse(
            request.model_copy(
                update={
                    "uia_tree": snapshot.root,
                    "source_preference": [CaptureSourceKind.UIA],
                }
            )
        )
        parsed.source.adapter = "capture.live_uia"
        parsed.source.kind = CaptureSourceKind.LIVE
        parsed.source.confidence = 0.88 if snapshot.message_role == "assistant" else 0.72
        parsed.verification.stable = snapshot.stable
        parsed.verification.completeness_score = max(parsed.verification.completeness_score, 0.82 if snapshot.message_role == "assistant" else 0.58)
        parsed.verification.indicators.extend(["uia_window_resolved", "uia_tree_acquired"])
        parsed.metadata["windowTitle"] = window.title
        parsed.metadata["windowClass"] = window.class_name
        parsed.metadata["windowProcess"] = window.process_name
        if snapshot.panel_id:
            parsed.metadata["selectedPanelId"] = snapshot.panel_id
        if snapshot.message_role:
            parsed.metadata["messageRole"] = snapshot.message_role
        return parsed

    def _capture_uia_tree(self, window: ResolvedWindow, target: TargetProfile) -> UiaSnapshot:
        try:
            from comtypes.client import CreateObject, GetModule
        except ImportError as exc:  # pragma: no cover
            raise ValueError("comtypes is required for live UIA capture") from exc

        try:
            GetModule("UIAutomationCore.dll")
            from comtypes.gen.UIAutomationClient import CUIAutomation
        except Exception as exc:  # pragma: no cover
            raise ValueError("Unable to load UIAutomation COM bindings") from exc

        automation = CreateObject(CUIAutomation)
        try:
            root_element = automation.ElementFromHandle(window.hwnd)
        except Exception as exc:
            raise ValueError(f"Unable to resolve UIA root for hwnd={window.hwnd}") from exc

        profile = target.uia or UiaCaptureProfile()
        visibility_rects = self._resolve_visibility_rects(window, target, profile)

        panel_element = self._find_best_panel(root_element, automation, profile, visibility_rects)
        capture_element = panel_element or root_element
        built_root = None

        message_element, message_role = self._find_best_message(capture_element, automation, profile, visibility_rects)
        if message_element is not None:
            clustered_elements = self._collect_message_cluster(
                capture_element,
                message_element,
                automation,
                profile,
                visibility_rects,
            )
            if len(clustered_elements) > 1:
                built_root = self._build_cluster_root(clustered_elements, automation, profile.max_depth, message_role)
            else:
                capture_element = message_element

        root = built_root or self._build_tree(capture_element, automation, depth=0, max_depth=profile.max_depth)
        if message_role:
            root.metadata["role"] = message_role

        panel_id = None
        if panel_element is not None:
            panel_id = self._safe_get(panel_element, "CurrentAutomationId") or self._safe_get(panel_element, "CurrentClassName")

        return UiaSnapshot(
            root=root,
            stable=True,
            panel_id=panel_id,
            message_role=message_role,
        )

    def _build_tree(self, element, automation, depth: int, max_depth: int) -> UiTreeNode:
        if depth > max_depth:
            return UiTreeNode()

        bounds = self._bounds_from_element(element)
        node = UiTreeNode(
            name=self._safe_get(element, "CurrentName"),
            value=self._safe_get(element, "CurrentValue"),
            control_type=self._safe_get(element, "CurrentLocalizedControlType"),
            automation_id=self._safe_get(element, "CurrentAutomationId"),
            class_name=self._safe_get(element, "CurrentClassName"),
            is_enabled=self._safe_get(element, "CurrentIsEnabled"),
            metadata={
                "bounds": bounds.model_dump() if bounds is not None else None,
                "is_offscreen": self._safe_get(element, "CurrentIsOffscreen"),
            },
        )

        for child in self._children_of(element, automation):
            node.children.append(self._build_tree(child, automation, depth + 1, max_depth))
        return node

    def _find_best_panel(self, root_element, automation, profile: UiaCaptureProfile, visibility_rects: list[Rect]):
        best_element = None
        best_key = None
        stack = [(root_element, 0)]
        search_depth_limit = max(profile.max_depth + 16, 24)

        while stack:
            element, depth = stack.pop()
            if depth > search_depth_limit:
                continue

            score = self._score_panel_candidate(element, automation, profile, visibility_rects, depth)
            if score > 0:
                key = (score, -depth)
                if best_key is None or key > best_key:
                    best_key = key
                    best_element = element

            for child in reversed(self._children_of(element, automation)):
                stack.append((child, depth + 1))

        return best_element

    def _find_best_message(self, panel_element, automation, profile: UiaCaptureProfile, visibility_rects: list[Rect]):
        best_element = None
        best_key = None
        best_role = None
        input_bounds = self._find_input_bounds(panel_element, automation, profile, visibility_rects)
        stack = [(panel_element, 0)]

        while stack:
            element, depth = stack.pop()
            if depth > profile.max_depth:
                continue

            score, role, bottom = self._score_message_candidate(
                element,
                automation,
                profile,
                visibility_rects,
                input_bounds,
            )
            if score > 0:
                key = (score, bottom)
                if best_key is None or key > best_key:
                    best_key = key
                    best_element = element
                    best_role = role

            for child in reversed(self._children_of(element, automation)):
                stack.append((child, depth + 1))

        return best_element, best_role

    def _score_panel_candidate(
        self,
        element,
        automation,
        profile: UiaCaptureProfile,
        visibility_rects: list[Rect],
        depth: int,
    ) -> int:
        automation_id = (self._safe_get(element, "CurrentAutomationId") or "").lower()
        class_name = (self._safe_get(element, "CurrentClassName") or "").lower()
        score = 0
        matched_hint = False

        if profile.panel_automation_id_patterns and self._contains_any(automation_id, profile.panel_automation_id_patterns):
            score += 140
            matched_hint = True
        if profile.panel_class_hints and self._contains_any(class_name, profile.panel_class_hints):
            score += 90
            matched_hint = True

        if (profile.panel_automation_id_patterns or profile.panel_class_hints) and not matched_hint:
            return 0

        bounds = self._bounds_from_element(element)
        if bounds is not None and any(self._intersects(bounds, rect) for rect in visibility_rects):
            score += 15

        score += min(depth * 3, 24)
        score += min(self._descendant_signal_score(element, automation, max_descendants=24), 30)
        return score

    def _score_message_candidate(
        self,
        element,
        automation,
        profile: UiaCaptureProfile,
        visibility_rects: list[Rect],
        input_bounds: Rect | None = None,
    ) -> tuple[int, str | None, int]:
        bounds = self._bounds_from_element(element)
        if bounds is None:
            return 0, None, -1

        automation_id = self._safe_get(element, "CurrentAutomationId") or ""
        class_name = self._safe_get(element, "CurrentClassName") or ""
        score = 0
        role = None
        direct_message_match = self._is_direct_message_candidate(element, profile)

        if profile.message_automation_id_prefixes and self._starts_with_any(automation_id, profile.message_automation_id_prefixes):
            score += 90

        if profile.message_class_hints and self._contains_any(class_name, profile.message_class_hints):
            score += 80

        if self._subtree_contains_hint(element, automation, profile.human_message_hints, max_descendants=80):
            return 0, "user", bounds.y + bounds.height

        if profile.assistant_message_hints and self._subtree_contains_hint(element, automation, profile.assistant_message_hints, max_descendants=50):
            score += 35
            role = "assistant"

        subtree_has_input = self._subtree_contains_hint(
            element,
            automation,
            profile.input_automation_id_patterns + profile.input_class_hints,
            max_descendants=50,
        )
        if subtree_has_input and not direct_message_match:
            return 0, None, bounds.y + bounds.height
        if subtree_has_input and direct_message_match:
            score -= 18

        if input_bounds is not None:
            overlap = self._intersection(bounds, input_bounds)
            if overlap is not None:
                overlap_ratio = (overlap.width * overlap.height) / (bounds.width * bounds.height)
                if overlap_ratio >= 0.12:
                    return 0, None, bounds.y + bounds.height
                score -= int(overlap_ratio * 40)

        visible_ratio = self._visible_ratio(bounds, visibility_rects)
        if profile.ignore_offscreen and visible_ratio < profile.min_visible_ratio:
            return 0, None, bounds.y + bounds.height

        text_score = self._element_text_score(element, automation, max_descendants=80)
        if text_score < 20:
            return 0, None, bounds.y + bounds.height

        score += min(text_score // 10, 45)
        score += int(visible_ratio * 30)
        score += int(self._normalized_visible_bottom(bounds, visibility_rects) * (42 if direct_message_match else 18))

        max_region_height = max((rect.height for rect in visibility_rects), default=bounds.height)
        if not direct_message_match and bounds.height > max_region_height * 0.55:
            score -= 60
        if not direct_message_match and bounds.height > max_region_height * 0.35:
            score -= 20

        if role is None:
            role = "assistant"

        return score, role, bounds.y + bounds.height

    def _collect_message_cluster(
        self,
        panel_element,
        selected_element,
        automation,
        profile: UiaCaptureProfile,
        visibility_rects: list[Rect],
    ) -> list:
        if not profile.message_automation_id_prefixes:
            return [selected_element]

        selected_bounds = self._bounds_from_element(selected_element)
        if selected_bounds is None:
            return [selected_element]

        input_bounds = self._find_input_bounds(panel_element, automation, profile, visibility_rects)
        human_boundary = self._find_last_human_boundary(panel_element, automation, profile, visibility_rects)
        candidates = []
        stack = [(panel_element, 0)]

        while stack:
            element, depth = stack.pop()
            if depth > profile.max_depth:
                continue

            if self._is_direct_message_candidate(element, profile):
                bounds = self._bounds_from_element(element)
                if bounds is not None:
                    score, role, _ = self._score_message_candidate(
                        element,
                        automation,
                        profile,
                        visibility_rects,
                        input_bounds,
                    )
                    if score > 0 and role != "user":
                        top = bounds.y
                        bottom = self._visible_bottom(bounds, visibility_rects)
                        if human_boundary is None or top >= human_boundary - 4:
                            candidates.append(
                                {
                                    "element": element,
                                    "top": top,
                                    "bottom": bottom,
                                    "bounds": bounds,
                                }
                            )

            for child in reversed(self._children_of(element, automation)):
                stack.append((child, depth + 1))

        if not candidates:
            return [selected_element]

        candidates.sort(key=lambda candidate: (candidate["top"], candidate["bottom"]))
        selected_index = next(
            (
                index
                for index, candidate in enumerate(candidates)
                if self._elements_match(candidate["element"], selected_element, candidate["bounds"], selected_bounds)
            ),
            -1,
        )
        if selected_index < 0:
            return [selected_element]

        start_index = selected_index
        while start_index > 0:
            current = candidates[start_index]
            previous = candidates[start_index - 1]
            if current["top"] - previous["bottom"] > 48:
                break
            start_index -= 1

        cluster = [candidate["element"] for candidate in candidates[start_index : selected_index + 1]]
        return cluster[-10:] or [selected_element]

    def _build_cluster_root(self, elements: list, automation, max_depth: int, role: str | None) -> UiTreeNode:
        bounds = [self._bounds_from_element(element) for element in elements]
        merged_bounds = self._union_bounds([bound for bound in bounds if bound is not None])
        return UiTreeNode(
            control_type="group",
            class_name="capture-message-cluster",
            metadata={
                "role": role or "assistant",
                "cluster": True,
                "cluster_size": len(elements),
                "bounds": merged_bounds.model_dump() if merged_bounds is not None else None,
            },
            children=[self._build_tree(element, automation, depth=0, max_depth=max_depth) for element in elements],
        )

    def _find_last_human_boundary(
        self,
        panel_element,
        automation,
        profile: UiaCaptureProfile,
        visibility_rects: list[Rect],
    ) -> int | None:
        best_bottom = None
        stack = [(panel_element, 0)]

        while stack:
            element, depth = stack.pop()
            if depth > profile.max_depth:
                continue

            bounds = self._bounds_from_element(element)
            if bounds is not None and self._visible_ratio(bounds, visibility_rects) >= profile.min_visible_ratio:
                if self._subtree_contains_hint(element, automation, profile.human_message_hints, max_descendants=80):
                    bottom = self._visible_bottom(bounds, visibility_rects)
                    if best_bottom is None or bottom > best_bottom:
                        best_bottom = bottom

            for child in reversed(self._children_of(element, automation)):
                stack.append((child, depth + 1))

        return best_bottom

    def _resolve_visibility_rects(self, window: ResolvedWindow, target: TargetProfile, profile: UiaCaptureProfile) -> list[Rect]:
        if not profile.region_names:
            return [window.bounds]

        rects: list[Rect] = []
        for region_name in profile.region_names:
            region = target.regions.get(region_name)
            if region is not None:
                rects.append(self._resolve_region(window.bounds, region))
        return rects or [window.bounds]

    def _resolve_region(self, window_rect: Rect, region: SearchRegion) -> Rect:
        anchor = region.anchor.lower()
        x = window_rect.x + region.x
        y = window_rect.y + region.y
        if anchor in {"bottomright", "bottom_right"}:
            x = window_rect.x + window_rect.width + region.x
            y = window_rect.y + window_rect.height + region.y
        elif anchor in {"topright", "top_right"}:
            x = window_rect.x + window_rect.width + region.x
            y = window_rect.y + region.y
        elif anchor in {"bottomleft", "bottom_left"}:
            x = window_rect.x + region.x
            y = window_rect.y + window_rect.height + region.y
        return Rect(x=x, y=y, width=region.w, height=region.h)

    def _children_of(self, element, automation) -> list:
        children = []
        try:
            walker = automation.RawViewWalker
            child = walker.GetFirstChildElement(element)
            count = 0
            while child and count < 250:
                children.append(child)
                child = walker.GetNextSiblingElement(child)
                count += 1
        except Exception:
            return []
        return children

    def _descendant_signal_score(self, element, automation, max_descendants: int) -> int:
        score = 0
        stack = [element]
        seen = 0
        while stack and seen < max_descendants:
            current = stack.pop()
            seen += 1
            haystack = self._element_haystack(current)
            if haystack:
                score += 1
            for child in self._children_of(current, automation)[:6]:
                stack.append(child)
        return score

    def _element_text_score(self, element, automation, max_descendants: int) -> int:
        total = 0
        stack = [element]
        seen = 0
        while stack and seen < max_descendants:
            current = stack.pop()
            seen += 1
            total += len(self._safe_get(current, "CurrentName") or "")
            total += len(self._safe_get(current, "CurrentValue") or "")
            for child in self._children_of(current, automation)[:8]:
                stack.append(child)
        return total

    def _subtree_contains_hint(self, element, automation, hints: list[str], max_descendants: int) -> bool:
        if not hints:
            return False

        lowered_hints = [hint.lower() for hint in hints]
        stack = [element]
        seen = 0
        while stack and seen < max_descendants:
            current = stack.pop()
            seen += 1
            haystack = self._element_haystack(current)
            if any(hint in haystack for hint in lowered_hints):
                return True
            for child in self._children_of(current, automation)[:8]:
                stack.append(child)
        return False

    def _find_input_bounds(
        self,
        panel_element,
        automation,
        profile: UiaCaptureProfile,
        visibility_rects: list[Rect],
    ) -> Rect | None:
        if not profile.input_automation_id_patterns and not profile.input_class_hints:
            return None

        best_bounds = None
        best_key = None
        stack = [(panel_element, 0)]
        while stack:
            current, depth = stack.pop()
            if depth > profile.max_depth:
                continue

            score, bounds = self._score_input_candidate(current, profile, visibility_rects)
            if score > 0 and bounds is not None:
                key = (score, self._visible_bottom(bounds, visibility_rects))
                if best_key is None or key > best_key:
                    best_key = key
                    best_bounds = bounds

            for child in reversed(self._children_of(current, automation)):
                stack.append((child, depth + 1))
        return best_bounds

    def _score_input_candidate(self, element, profile: UiaCaptureProfile, visibility_rects: list[Rect]) -> tuple[int, Rect | None]:
        bounds = self._bounds_from_element(element)
        if bounds is None:
            return 0, None

        automation_id = (self._safe_get(element, "CurrentAutomationId") or "").lower()
        class_name = (self._safe_get(element, "CurrentClassName") or "").lower()
        control_type = (self._safe_get(element, "CurrentLocalizedControlType") or "").lower()

        direct_match = self._contains_any(automation_id, profile.input_automation_id_patterns) or self._contains_any(
            class_name,
            profile.input_class_hints,
        )
        if not direct_match:
            return 0, None

        visible_ratio = self._visible_ratio(bounds, visibility_rects)
        if profile.ignore_offscreen and visible_ratio < profile.min_visible_ratio:
            return 0, None

        score = 60
        if control_type in {"edit", "document"}:
            score += 35
        if "input" in class_name:
            score += 20
        if "readonly" in class_name or "readonly" in automation_id:
            score -= 80
        score += int(visible_ratio * 25)
        score += int(self._normalized_visible_bottom(bounds, visibility_rects) * 30)
        return max(score, 0), bounds

    def _is_direct_message_candidate(self, element, profile: UiaCaptureProfile) -> bool:
        automation_id = self._safe_get(element, "CurrentAutomationId") or ""
        class_name = self._safe_get(element, "CurrentClassName") or ""
        return self._starts_with_any(automation_id, profile.message_automation_id_prefixes) or self._contains_any(
            class_name,
            profile.message_class_hints,
        )

    @staticmethod
    def _contains_any(value: str, patterns: list[str]) -> bool:
        lowered = value.lower()
        return any(pattern.lower() in lowered for pattern in patterns)

    @staticmethod
    def _starts_with_any(value: str, patterns: list[str]) -> bool:
        lowered = value.lower()
        return any(lowered.startswith(pattern.lower()) for pattern in patterns)

    def _element_haystack(self, element) -> str:
        parts = [
            self._safe_get(element, "CurrentName") or "",
            self._safe_get(element, "CurrentAutomationId") or "",
            self._safe_get(element, "CurrentClassName") or "",
            self._safe_get(element, "CurrentLocalizedControlType") or "",
        ]
        return " ".join(str(part).lower() for part in parts if part)

    def _visible_ratio(self, bounds: Rect, visibility_rects: list[Rect]) -> float:
        if bounds.width <= 0 or bounds.height <= 0:
            return 0.0

        area = bounds.width * bounds.height
        best_ratio = 0.0
        for rect in visibility_rects:
            intersection = self._intersection(bounds, rect)
            if intersection is None:
                continue
            best_ratio = max(best_ratio, (intersection.width * intersection.height) / area)
        return best_ratio

    def _visible_bottom(self, bounds: Rect, visibility_rects: list[Rect]) -> int:
        best_bottom = None
        for rect in visibility_rects:
            intersection = self._intersection(bounds, rect)
            if intersection is None:
                continue
            bottom = intersection.y + intersection.height
            if best_bottom is None or bottom > best_bottom:
                best_bottom = bottom
        return best_bottom if best_bottom is not None else bounds.y + bounds.height

    def _normalized_visible_bottom(self, bounds: Rect, visibility_rects: list[Rect]) -> float:
        if not visibility_rects:
            return 0.0

        region_top = min(rect.y for rect in visibility_rects)
        region_bottom = max(rect.y + rect.height for rect in visibility_rects)
        if region_bottom <= region_top:
            return 0.0

        visible_bottom = self._visible_bottom(bounds, visibility_rects)
        ratio = (visible_bottom - region_top) / (region_bottom - region_top)
        return max(0.0, min(1.0, ratio))

    def _elements_match(self, left, right, left_bounds: Rect | None, right_bounds: Rect | None) -> bool:
        if left is right:
            return True

        left_id = self._safe_get(left, "CurrentAutomationId") or ""
        right_id = self._safe_get(right, "CurrentAutomationId") or ""
        if left_id and left_id == right_id and left_bounds == right_bounds:
            return True

        return left_bounds == right_bounds and self._safe_get(left, "CurrentClassName") == self._safe_get(right, "CurrentClassName")

    @staticmethod
    def _union_bounds(bounds: list[Rect]) -> Rect | None:
        if not bounds:
            return None

        left = min(bound.x for bound in bounds)
        top = min(bound.y for bound in bounds)
        right = max(bound.x + bound.width for bound in bounds)
        bottom = max(bound.y + bound.height for bound in bounds)
        return Rect(x=left, y=top, width=right - left, height=bottom - top)

    @staticmethod
    def _bounds_from_element(element) -> Rect | None:
        try:
            rect = element.CurrentBoundingRectangle
        except Exception:
            return None

        values = [rect.left, rect.top, rect.right, rect.bottom]
        if not all(isfinite(float(value)) for value in values):
            return None

        width = int(rect.right - rect.left)
        height = int(rect.bottom - rect.top)
        if width <= 0 or height <= 0:
            return None

        return Rect(
            x=int(rect.left),
            y=int(rect.top),
            width=width,
            height=height,
        )

    @staticmethod
    def _intersects(left: Rect, right: Rect) -> bool:
        return not (
            left.x + left.width <= right.x
            or left.x >= right.x + right.width
            or left.y + left.height <= right.y
            or left.y >= right.y + right.height
        )

    @staticmethod
    def _intersection(left: Rect, right: Rect) -> Rect | None:
        x1 = max(left.x, right.x)
        y1 = max(left.y, right.y)
        x2 = min(left.x + left.width, right.x + right.width)
        y2 = min(left.y + left.height, right.y + right.height)
        if x2 <= x1 or y2 <= y1:
            return None
        return Rect(x=x1, y=y1, width=x2 - x1, height=y2 - y1)

    @staticmethod
    def _safe_get(element, attribute: str):
        try:
            value = getattr(element, attribute)
            if callable(value):
                value = value()
            if isinstance(value, str):
                return value.strip()
            return value
        except Exception:
            return None
