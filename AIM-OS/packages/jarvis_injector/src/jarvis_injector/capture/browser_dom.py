from __future__ import annotations

import json
from dataclasses import dataclass, field
from html.parser import HTMLParser
from itertools import count
from typing import Any

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


@dataclass
class DomNode:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list[Any] = field(default_factory=list)


class _DomTreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = DomNode(tag="root")
        self._stack = [self.root]
        self._void_tags = {"br", "hr", "img", "meta", "link", "input"}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = DomNode(tag=tag.lower(), attrs={key: value or "" for key, value in attrs})
        self._stack[-1].children.append(node)
        if node.tag not in self._void_tags:
            self._stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        for index in range(len(self._stack) - 1, 0, -1):
            if self._stack[index].tag == lowered:
                del self._stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if data:
            self._stack[-1].children.append(data)


class DomCaptureParser:
    def __init__(self) -> None:
        self._block_ids = count(1)

    def parse(self, request: CaptureRequest) -> CapturedMessage:
        if not request.html_snapshot:
            raise ValueError("DOM capture requires html_snapshot")

        builder = _DomTreeBuilder()
        builder.feed(request.html_snapshot)
        root = builder.root
        container = self._find_last_message_container(root, request.message_role)
        blocks = self._children_to_blocks(container.children if container else root.children)
        if not blocks:
            blocks = [self._paragraph_from_text(self._flatten_text(container or root))]

        return CapturedMessage(
            target_id=request.target_id,
            message_id=(container.attrs.get("data-message-id") if container else None) or f"dom-message-{next(self._block_ids)}",
            source=CaptureSource(
                adapter="capture.dom",
                kind=CaptureSourceKind.DOM,
                confidence=0.78 if container else 0.42,
                provider=request.provider,
            ),
            verification=CaptureVerification(
                stable=bool(container),
                completeness_score=0.8 if container else 0.45,
                indicators=["dom_snapshot_present", "assistant_container_resolved" if container else "assistant_container_missing"],
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

    def _find_last_message_container(self, root: DomNode, role: str) -> DomNode | None:
        candidates: list[DomNode] = []

        def walk(node: DomNode) -> None:
            if self._is_message_candidate(node, role):
                candidates.append(node)
            for child in node.children:
                if isinstance(child, DomNode):
                    walk(child)

        walk(root)
        return candidates[-1] if candidates else None

    def _is_message_candidate(self, node: DomNode, role: str) -> bool:
        attrs = {key.lower(): value.lower() for key, value in node.attrs.items()}
        class_text = attrs.get("class", "")
        markers = [
            attrs.get("data-message-author-role") == role,
            attrs.get("data-role") == role,
            attrs.get("role") == role,
            role in class_text and "message" in class_text,
            role == "assistant" and any(marker in class_text for marker in ["assistant", "model-response", "ai-message", "response-message"]),
        ]
        return any(markers)

    def _children_to_blocks(self, children: list[Any]) -> list[MessageBlock]:
        blocks: list[MessageBlock] = []
        inline_buffer: list[InlineSpan] = []

        for child in children:
            if isinstance(child, str):
                self._append_text(inline_buffer, child)
                continue

            if self._is_block_tag(child):
                self._flush_paragraph(blocks, inline_buffer)
                blocks.extend(self._block_from_node(child))
            else:
                inline_buffer.extend(self._inline_spans(child))

        self._flush_paragraph(blocks, inline_buffer)
        return [block for block in blocks if self._block_has_content(block)]

    def _block_from_node(self, node: DomNode) -> list[MessageBlock]:
        tag = node.tag

        if tag.startswith("h") and len(tag) == 2 and tag[1].isdigit():
            return [MessageBlock(id=self._next_id(), type=BlockType.HEADING, level=int(tag[1]), text=self._flatten_text(node))]
        if tag == "pre":
            code_node = next((child for child in node.children if isinstance(child, DomNode) and child.tag == "code"), None)
            language = self._language_from_node(code_node) if code_node else self._language_from_node(node)
            return [MessageBlock(id=self._next_id(), type=BlockType.CODE_BLOCK, language=language, text=self._flatten_text(code_node or node).rstrip())]
        if tag in {"ul", "ol"}:
            items = []
            for child in node.children:
                if isinstance(child, DomNode) and child.tag == "li":
                    items.append(self._inline_spans(child))
            return [MessageBlock(id=self._next_id(), type=BlockType.LIST, ordered=tag == "ol", items=items)]
        if tag == "table":
            rows = []
            for row in node.children:
                if isinstance(row, DomNode) and row.tag == "tr":
                    rows.append([self._flatten_text(cell).strip() for cell in row.children if isinstance(cell, DomNode)])
                elif isinstance(row, DomNode) and row.tag in {"thead", "tbody"}:
                    for nested_row in row.children:
                        if isinstance(nested_row, DomNode) and nested_row.tag == "tr":
                            rows.append([self._flatten_text(cell).strip() for cell in nested_row.children if isinstance(cell, DomNode)])
            return [MessageBlock(id=self._next_id(), type=BlockType.TABLE, rows=[row for row in rows if any(row)])]
        if self._is_tool_node(node):
            block_type = BlockType.TOOL_RESULT if "result" in self._class_text(node) or "output" in self._class_text(node) else BlockType.TOOL_CALL
            return [
                MessageBlock(
                    id=self._next_id(),
                    type=block_type,
                    tool_name=node.attrs.get("data-tool-name") or node.attrs.get("data-tool") or self._guess_tool_name(node),
                    tool_status=node.attrs.get("data-status"),
                    arguments=self._extract_tool_arguments(node),
                    text=self._flatten_text(node).strip(),
                    collapsed=node.attrs.get("aria-expanded") == "false",
                    metadata={"class": node.attrs.get("class", "")},
                )
            ]
        if tag == "blockquote":
            return [MessageBlock(id=self._next_id(), type=BlockType.QUOTE, text=self._flatten_text(node))]
        if tag in {"p", "li"}:
            return [MessageBlock(id=self._next_id(), type=BlockType.PARAGRAPH, spans=self._inline_spans(node))]
        if tag in {"div", "section", "article", "main"}:
            if any(isinstance(child, DomNode) and self._is_block_tag(child) for child in node.children):
                return self._children_to_blocks(node.children)
            return [MessageBlock(id=self._next_id(), type=BlockType.PARAGRAPH, spans=self._inline_spans(node))]

        return [MessageBlock(id=self._next_id(), type=BlockType.UNKNOWN, text=self._flatten_text(node))]

    def _inline_spans(self, node: DomNode) -> list[InlineSpan]:
        spans: list[InlineSpan] = []
        for child in node.children:
            if isinstance(child, str):
                self._append_text(spans, child)
                continue

            if child.tag == "code":
                text = self._flatten_text(child).strip()
                if text:
                    spans.append(InlineSpan(type=InlineSpanType.INLINE_CODE, text=text))
            elif child.tag == "a":
                text = self._flatten_text(child).strip()
                spans.append(InlineSpan(type=InlineSpanType.LINK, text=text, href=child.attrs.get("href")))
            elif child.tag in {"sup", "cite"}:
                text = self._flatten_text(child).strip()
                spans.append(InlineSpan(type=InlineSpanType.CITATION, text=text))
            elif child.tag == "br":
                self._append_text(spans, "\n")
            else:
                spans.extend(self._inline_spans(child))
        return spans

    def _append_text(self, spans: list[InlineSpan], text: str) -> None:
        cleaned = text.replace("\r", "")
        if not cleaned.strip() and "\n" not in cleaned:
            return
        if spans and spans[-1].type == InlineSpanType.TEXT:
            spans[-1].text += cleaned
        else:
            spans.append(InlineSpan(type=InlineSpanType.TEXT, text=cleaned))

    def _flush_paragraph(self, blocks: list[MessageBlock], inline_buffer: list[InlineSpan]) -> None:
        text = blocks_to_plaintext([MessageBlock(id="buffer", type=BlockType.PARAGRAPH, spans=inline_buffer)])
        if text:
            blocks.append(MessageBlock(id=self._next_id(), type=BlockType.PARAGRAPH, spans=list(inline_buffer)))
        inline_buffer.clear()

    def _flatten_text(self, node: DomNode) -> str:
        parts: list[str] = []
        for child in node.children:
            if isinstance(child, str):
                parts.append(child)
            else:
                parts.append(self._flatten_text(child))
        return "".join(parts).strip()

    def _is_block_tag(self, node: DomNode) -> bool:
        return node.tag in {"div", "section", "article", "main", "p", "pre", "ul", "ol", "table", "blockquote", "details"} or (node.tag.startswith("h") and len(node.tag) == 2)

    def _block_has_content(self, block: MessageBlock) -> bool:
        return bool(block.text or block.spans or block.items or block.rows or block.children)

    def _class_text(self, node: DomNode) -> str:
        return node.attrs.get("class", "").lower()

    def _is_tool_node(self, node: DomNode) -> bool:
        class_text = self._class_text(node)
        return any(
            token in class_text for token in ["tool-call", "tool-result", "tool-output", "tool-invocation"]
        ) or any(key in node.attrs for key in ["data-tool-name", "data-tool", "data-status"])

    def _guess_tool_name(self, node: DomNode) -> str | None:
        header = self._flatten_text(node).splitlines()[0] if self._flatten_text(node) else ""
        if not header:
            return None
        return header.split("(")[0].strip()[:80] or None

    def _extract_tool_arguments(self, node: DomNode) -> dict[str, Any] | list[Any] | str | None:
        raw = node.attrs.get("data-tool-args")
        if raw:
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw
        code_blocks = [child for child in node.children if isinstance(child, DomNode) and child.tag == "pre"]
        if code_blocks:
            text = self._flatten_text(code_blocks[0])
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text
        return None

    def _language_from_node(self, node: DomNode | None) -> str | None:
        if node is None:
            return None
        class_text = node.attrs.get("class", "")
        for token in class_text.split():
            if token.startswith("language-"):
                return token.removeprefix("language-")
        return node.attrs.get("data-language")

    def _paragraph_from_text(self, text: str) -> MessageBlock:
        return MessageBlock(id=self._next_id(), type=BlockType.PARAGRAPH, text=text.strip())

    def _next_id(self) -> str:
        return f"block_{next(self._block_ids)}"
