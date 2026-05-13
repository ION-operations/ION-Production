from __future__ import annotations

from itertools import count
import re

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
    UiTreeNode,
)
from jarvis_injector.capture.normalize import blocks_to_markdown, blocks_to_plaintext


class UiaCaptureParser:
    _ACCESSIBILITY_NOISE = {
        "The editor is not accessible at this time. To enable screen reader optimized mode, use Shift+Alt+F1",
    }
    _PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff]+")

    def __init__(self) -> None:
        self._ids = count(1)

    def parse(self, request: CaptureRequest) -> CapturedMessage:
        if not request.uia_tree:
            raise ValueError("UIA capture requires uia_tree")

        roots = request.uia_tree if isinstance(request.uia_tree, list) else [request.uia_tree]
        container = self._find_last_message_container(roots, request.message_role)
        blocks = self._node_to_blocks(container) if container else []
        if not blocks:
            blocks = [MessageBlock(id=self._next_id(), type=BlockType.PARAGRAPH, text=self._aggregate_text(container or roots[0]))]

        return CapturedMessage(
            target_id=request.target_id,
            message_id=(container.automation_id if container else None) or f"uia-message-{next(self._ids)}",
            source=CaptureSource(
                adapter="capture.uia",
                kind=CaptureSourceKind.UIA,
                confidence=0.68 if container else 0.35,
                provider=request.provider,
            ),
            verification=CaptureVerification(
                stable=bool(container),
                completeness_score=0.72 if container else 0.4,
                indicators=["uia_tree_present", "assistant_container_resolved" if container else "assistant_container_missing"],
            ),
            blocks=blocks,
            plaintext=blocks_to_plaintext(blocks),
            markdown=blocks_to_markdown(blocks),
            metadata={
                **request.metadata,
                "containerResolved": bool(container),
                "provider": request.provider,
            },
        )

    def _find_last_message_container(self, roots: list[UiTreeNode], role: str) -> UiTreeNode | None:
        candidates: list[UiTreeNode] = []

        def walk(node: UiTreeNode) -> None:
            if self._is_message_candidate(node, role):
                candidates.append(node)
            for child in node.children:
                walk(child)

        for root in roots:
            walk(root)
        return candidates[-1] if candidates else None

    def _is_message_candidate(self, node: UiTreeNode, role: str) -> bool:
        if node.metadata.get("role") == role:
            return True
        haystack = " ".join(
            part.lower()
            for part in [node.name or "", node.automation_id or "", node.class_name or "", node.control_type or ""]
            if part
        )
        return role in haystack and any(marker in haystack for marker in ["message", "response", "assistant", "model"])

    def _node_to_blocks(self, node: UiTreeNode) -> list[MessageBlock]:
        control_type = (node.control_type or "").lower()

        if self._is_tool_node(node):
            return [
                MessageBlock(
                    id=self._next_id(),
                    type=BlockType.TOOL_CALL if "result" not in self._node_text(node).lower() else BlockType.TOOL_RESULT,
                    tool_name=node.metadata.get("tool_name") or node.name,
                    tool_status=node.metadata.get("status"),
                    arguments=node.metadata.get("arguments"),
                    text=self._aggregate_text(node).strip(),
                )
            ]

        if self._is_code_node(node):
            return [
                MessageBlock(
                    id=self._next_id(),
                    type=BlockType.CODE_BLOCK,
                    language=node.metadata.get("language"),
                    text=self._aggregate_text(node),
                )
            ]

        if control_type == "heading":
            return [MessageBlock(id=self._next_id(), type=BlockType.HEADING, text=self._aggregate_text(node), level=2)]

        if control_type == "blockquote":
            return [MessageBlock(id=self._next_id(), type=BlockType.QUOTE, text=self._aggregate_text(node))]

        if control_type == "list":
            items = []
            for child in node.children:
                item_text = self._aggregate_text(child).strip()
                if item_text:
                    items.append([InlineSpan(type=InlineSpanType.TEXT, text=item_text)])
            if items:
                return [MessageBlock(id=self._next_id(), type=BlockType.LIST, items=items, ordered=False)]

        if control_type in {"table", "datagrid"}:
            rows = []
            for row in node.children:
                rows.append([self._aggregate_text(cell).strip() for cell in row.children] or [self._aggregate_text(row).strip()])
            return [MessageBlock(id=self._next_id(), type=BlockType.TABLE, rows=[row for row in rows if any(row)])]

        if node.children and self._children_are_inline(node.children):
            text = self._aggregate_text(node).strip()
            if text:
                return [
                    MessageBlock(
                        id=self._next_id(),
                        type=BlockType.PARAGRAPH,
                        spans=[InlineSpan(type=InlineSpanType.TEXT, text=text)],
                    )
                ]

        if node.children:
            blocks: list[MessageBlock] = []
            for child in node.children:
                blocks.extend(self._node_to_blocks(child))
            if blocks:
                return blocks

        text = self._node_text(node)
        if text:
            return [
                MessageBlock(
                    id=self._next_id(),
                    type=BlockType.PARAGRAPH,
                    spans=[InlineSpan(type=InlineSpanType.TEXT, text=text)],
                )
            ]
        return []

    def _node_text(self, node: UiTreeNode) -> str:
        return (node.value or node.name or "").strip()

    def _aggregate_text(self, node: UiTreeNode) -> str:
        own_text = self._node_text(node)
        child_texts = [self._aggregate_text(child) for child in node.children]
        child_texts = [text for text in child_texts if text]

        if not child_texts:
            return own_text

        separator = " " if self._children_are_inline(node.children) else "\n"
        combined_children = self._normalize_text(separator.join(child_texts), separator)

        if not own_text:
            return combined_children

        normalized_own = self._normalize_text(own_text, " ")
        normalized_children = self._normalize_text(combined_children, " ")

        if normalized_own and normalized_children:
            if normalized_own in normalized_children:
                return combined_children
            if normalized_children in normalized_own:
                return own_text.strip()

        return self._normalize_text(f"{own_text}{separator}{combined_children}", separator)

    def _is_code_node(self, node: UiTreeNode) -> bool:
        haystack = " ".join([node.class_name or "", node.automation_id or "", node.name or ""]).lower()
        return "code" in haystack or node.metadata.get("kind") == "code_block"

    def _is_tool_node(self, node: UiTreeNode) -> bool:
        haystack = " ".join([node.class_name or "", node.automation_id or "", node.name or ""]).lower()
        return "tool" in haystack or node.metadata.get("kind") in {"tool_call", "tool_result"}

    def _children_are_inline(self, children: list[UiTreeNode]) -> bool:
        inline_controls = {"text", "link", "emphasis", "code"}
        for child in children:
            control_type = (child.control_type or "").lower()
            if control_type and control_type not in inline_controls:
                return False
            if child.children and not self._children_are_inline(child.children):
                return False
        return True

    def _normalize_text(self, text: str, separator: str) -> str:
        text = self._PRIVATE_USE_RE.sub("", text)
        if separator == " ":
            text = re.sub(r"\s+", " ", text)
            text = re.sub(r"\s+([,.;:!?])", r"\1", text)
            text = re.sub(r"([(\[])\s+", r"\1", text)
        else:
            lines: list[str] = []
            for raw_line in text.splitlines():
                line = re.sub(r"\s+", " ", raw_line).strip()
                if not line or line in self._ACCESSIBILITY_NOISE:
                    continue
                if lines and lines[-1] == line:
                    continue
                lines.append(line)
            text = "\n".join(lines)
        return text.strip()

    def _next_id(self) -> str:
        return f"block_{next(self._ids)}"
